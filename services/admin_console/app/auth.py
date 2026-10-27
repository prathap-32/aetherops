# services/requirement_analysis/app/auth.py
import os
import sys
import time
import logging
import datetime
import secrets
from typing import Optional, Dict, Any

import bcrypt
import jwt
from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database import (
    IS_TESTING,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    get_postgres_url,
    ECHO_SQL,
)
from app.security_models import AdminUser, AdminAuditLog

logger = logging.getLogger("aetherops-admin-auth")

ENVIRONMENT = os.getenv("AETHER_ENV", os.getenv("ENVIRONMENT", "development")).lower()
INSECURE_DEV_JWT_SECRETS = {
    "aetherops-super-secure-production-cryptographic-jwt-token-signing-key-2026-cloudops-master",
    "secret",
    "changeme",
    "admin",
    "default",
    "test",
    "dev",
}
raw_jwt_key = os.getenv("JWT_SECRET_KEY")
if ENVIRONMENT == "production":
    if not raw_jwt_key or raw_jwt_key in INSECURE_DEV_JWT_SECRETS:
        raise RuntimeError("FATAL: JWT_SECRET_KEY must be explicitly configured with a secure non-default secret in production.")
    JWT_SECRET_KEY = raw_jwt_key
else:
    JWT_SECRET_KEY = raw_jwt_key or "aetherops-super-secure-production-cryptographic-jwt-token-signing-key-2026-cloudops-master"

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "8"))
SESSION_COOKIE_NAME = "aether_session"

# Master API Key (for backward compatibility & CI/CD)
MASTER_ADMIN_KEY = os.getenv("ADMIN_API_KEY", "aetherops-secret-admin-key")
if ENVIRONMENT == "production" and (not MASTER_ADMIN_KEY or MASTER_ADMIN_KEY == "aetherops-secret-admin-key"):
    logger.critical("SECURITY ALERT: Insecure default ADMIN_API_KEY in production! Disabling master key fallback.")
    MASTER_ADMIN_KEY = None

# Default Super Admin Seed Credentials
DEFAULT_ADMIN_USER = os.getenv("ADMIN_DEFAULT_USER", "admin")
DEFAULT_ADMIN_PASS = os.getenv("ADMIN_DEFAULT_PASS", "AetherOps@2026!")
DEFAULT_ADMIN_EMAIL = os.getenv("ADMIN_DEFAULT_EMAIL", "admin@aetherops.cloud")

# Engine & Sessionmaker for Admin Security
_admin_pg_engine = None
_admin_pg_sessionmaker = None
_admin_sqlite_engine = None
_admin_sqlite_sessionmaker = None


def get_admin_sqlite_sessionmaker():
    global _admin_sqlite_engine, _admin_sqlite_sessionmaker
    if _admin_sqlite_sessionmaker is None:
        db_file = "test_admin_security.db" if IS_TESTING else "admin_security.db"
        _admin_sqlite_engine = create_async_engine(
            f"sqlite+aiosqlite:///{db_file}",
            echo=ECHO_SQL,
            future=True,
            connect_args={"check_same_thread": False}
        )
        _admin_sqlite_sessionmaker = async_sessionmaker(
            bind=_admin_sqlite_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    return _admin_sqlite_sessionmaker


def get_admin_pg_sessionmaker():
    global _admin_pg_engine, _admin_pg_sessionmaker
    if _admin_pg_sessionmaker is None:
        url = get_postgres_url("admin")
        _admin_pg_engine = create_async_engine(
            url,
            echo=ECHO_SQL,
            future=True,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            connect_args={
                "command_timeout": 10,
                "server_settings": {"search_path": '"admin_security", public'}
            }
        )
        _admin_pg_sessionmaker = async_sessionmaker(
            bind=_admin_pg_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    return _admin_pg_sessionmaker


_security_initialized = False


async def ensure_security_initialized():
    global _security_initialized
    if not _security_initialized:
        await init_admin_security()
        _security_initialized = True


async def get_admin_db_session() -> AsyncSession:
    """
    Yields an AsyncSession connected to PostgreSQL 'admin_security' schema,
    failing over to local SQLite if PostgreSQL is unreachable or in tests.
    """
    await ensure_security_initialized()
    if IS_TESTING:
        sf = get_admin_sqlite_sessionmaker()
        async with sf() as session:
            yield session
        return

    # Production / Dev: Try PostgreSQL primary
    try:
        pg_sf = get_admin_pg_sessionmaker()
        async with pg_sf() as session:
            await session.execute(text("SELECT 1"))
            yield session
            return
    except Exception as e:
        logger.warning(f"PostgreSQL admin_security unavailable ({e}), failing over to SQLite.")
        sqlite_sf = get_admin_sqlite_sessionmaker()
        async with sqlite_sf() as session:
            yield session


# Cryptographic Helpers
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(username: str, role: str, email: str, hours: int = JWT_EXPIRATION_HOURS) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "sub": username,
        "role": role,
        "email": email,
        "iat": now,
        "exp": now + datetime.timedelta(hours=hours),
        "jti": secrets.token_hex(16)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


# Redis Rate Limiter & Security Tracking
def check_login_rate_limit(client_ip: str) -> bool:
    """
    Returns True if allowed, False if rate-limited (max 5 failed attempts per 15 min).
    """
    try:
        import redis
        r = redis.Redis(host="localhost", port=6379, db=0, socket_timeout=1)
        key = f"aether_auth_fail:{client_ip}"
        fails = r.get(key)
        if fails and int(fails) >= 5:
            return False
        return True
    except Exception:
        return True


def record_failed_login(client_ip: str):
    try:
        import redis
        r = redis.Redis(host="localhost", port=6379, db=0, socket_timeout=1)
        key = f"aether_auth_fail:{client_ip}"
        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, 900)  # 15 minutes lockout window
        pipe.execute()
    except Exception:
        pass


def clear_failed_login(client_ip: str):
    try:
        import redis
        r = redis.Redis(host="localhost", port=6379, db=0, socket_timeout=1)
        r.delete(f"aether_auth_fail:{client_ip}")
    except Exception:
        pass


# Database Initializer & Super Admin Seeder
async def init_admin_security():
    """
    Ensures schema and tables exist in PostgreSQL (and local SQLite)
    and seeds the initial default Super Admin account if missing.
    """
    from app.database import Base
    import app.security_models

    # 1. Initialize SQLite tables
    sqlite_sf = get_admin_sqlite_sessionmaker()
    async with _admin_sqlite_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Initialize PostgreSQL schema & tables if not testing
    if not IS_TESTING:
        try:
            pg_sf = get_admin_pg_sessionmaker()
            async with _admin_pg_engine.begin() as conn:
                await conn.execute(text('CREATE SCHEMA IF NOT EXISTS "admin_security"'))
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            logger.warning(f"PostgreSQL admin_security setup deferred: {e}")

    # 3. Seed Default Super Admin Account in both DBs
    pwd_hash = hash_password(DEFAULT_ADMIN_PASS)

    # In SQLite:
    async with sqlite_sf() as session:
        res = await session.execute(select(AdminUser).where(AdminUser.username == DEFAULT_ADMIN_USER))
        if not res.scalar_one_or_none():
            user = AdminUser(
                username=DEFAULT_ADMIN_USER,
                email=DEFAULT_ADMIN_EMAIL,
                password_hash=pwd_hash,
                role="SUPER_ADMIN",
                is_active=True,
                created_at=datetime.datetime.utcnow()
            )
            session.add(user)
            await session.commit()
            logger.info(f"Seeded default super admin '{DEFAULT_ADMIN_USER}' in SQLite.")

    # In PostgreSQL (if reachable):
    if not IS_TESTING:
        try:
            async with get_admin_pg_sessionmaker()() as session:
                res = await session.execute(select(AdminUser).where(AdminUser.username == DEFAULT_ADMIN_USER))
                if not res.scalar_one_or_none():
                    user = AdminUser(
                        username=DEFAULT_ADMIN_USER,
                        email=DEFAULT_ADMIN_EMAIL,
                        password_hash=pwd_hash,
                        role="SUPER_ADMIN",
                        is_active=True,
                        created_at=datetime.datetime.utcnow()
                    )
                    session.add(user)
                    await session.commit()
                    logger.info(f"Seeded default super admin '{DEFAULT_ADMIN_USER}' in PostgreSQL.")
        except Exception as e:
            logger.warning(f"PostgreSQL admin seed deferred: {e}")


async def log_admin_audit(
    username: str,
    action: str,
    target: Optional[str] = None,
    status: str = "SUCCESS",
    ip: Optional[str] = None,
    details: Optional[str] = None
):
    try:
        async for session in get_admin_db_session():
            audit = AdminAuditLog(
                username=username,
                action=action,
                target_resource=target,
                status=status,
                ip_address=ip,
                details=details,
                created_at=datetime.datetime.utcnow()
            )
            session.add(audit)
            await session.commit()
            break
    except Exception as e:
        logger.error(f"Audit log failed: {e}")


# Dependency: Verifies session cookie or API key
async def get_current_admin(request: Request) -> Dict[str, Any]:
    """
    Multi-channel Admin Authentication:
    1. HttpOnly Cookie: 'aether_session' (JWT)
    2. Bearer Token: 'Authorization: Bearer <JWT>'
    3. Master Key: 'X-Admin-Key: <key>' (backward compatibility for automation & tests)
    """
    client_ip = request.client.host if request.client else "127.0.0.1"

    # Channel 1: Check HttpOnly Cookie
    cookie_token = request.cookies.get(SESSION_COOKIE_NAME)
    if cookie_token:
        payload = decode_access_token(cookie_token)
        if payload:
            return {
                "username": payload.get("sub", "admin"),
                "role": payload.get("role", "SUPER_ADMIN"),
                "email": payload.get("email", "admin@aetherops.cloud"),
                "auth_type": "cookie"
            }

    # Channel 2: Check Authorization: Bearer <token>
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        payload = decode_access_token(token)
        if payload:
            return {
                "username": payload.get("sub", "admin"),
                "role": payload.get("role", "SUPER_ADMIN"),
                "email": payload.get("email", "admin@aetherops.cloud"),
                "auth_type": "bearer"
            }

    # Channel 3: Check X-Admin-Key (matches configured key)
    admin_key = request.headers.get("X-Admin-Key")
    if admin_key and secrets.compare_digest(admin_key.strip(), MASTER_ADMIN_KEY):
        return {
            "username": "root_admin",
            "role": "SUPER_ADMIN",
            "email": "root@aetherops.cloud",
            "auth_type": "api_key"
        }

    # If unauthenticated:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized: Valid admin session cookie or API key required"
    )
