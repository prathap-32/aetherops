# services/project_and_environment_management/app/auth.py
import os
import datetime
import secrets
import logging
from typing import Optional, Dict, Any

import bcrypt
import jwt
from fastapi import Request, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database import (
    IS_TESTING, get_postgres_url, get_sqlite_engine, ECHO_SQL,
)
from app.security_models import AdminUser, AdminAuditLog

logger = logging.getLogger("project-manager-auth")

JWT_SECRET_KEY       = os.getenv(
    "JWT_SECRET_KEY",
    "aetherops-super-secure-production-cryptographic-jwt-token-signing-key-2026-cloudops-master"
)
JWT_ALGORITHM        = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "8"))
SESSION_COOKIE_NAME  = "aether_session"
ENVIRONMENT          = os.getenv("AETHER_ENV", os.getenv("ENVIRONMENT", "development")).lower()
MASTER_ADMIN_KEY     = os.getenv("ADMIN_API_KEY", "aetherops-secret-admin-key")
if ENVIRONMENT == "production" and MASTER_ADMIN_KEY == "aetherops-secret-admin-key":
    logger.critical("SECURITY ALERT: Insecure default ADMIN_API_KEY in production! Disabling master key fallback.")
    MASTER_ADMIN_KEY = None

DEFAULT_ADMIN_USER   = os.getenv("ADMIN_DEFAULT_USER", "admin")
DEFAULT_ADMIN_PASS   = os.getenv("ADMIN_DEFAULT_PASS", "AetherOps@2026!")
DEFAULT_ADMIN_EMAIL  = os.getenv("ADMIN_DEFAULT_EMAIL", "admin@aetherops.cloud")

_admin_sqlite_engine      = None
_admin_sqlite_sessionmaker = None
_admin_pg_engine          = None
_admin_pg_sessionmaker    = None
_security_initialized     = False


def _get_admin_sqlite_sessionmaker():
    global _admin_sqlite_engine, _admin_sqlite_sessionmaker
    if _admin_sqlite_sessionmaker is None:
        db_file = "test_pm_admin_security.db" if IS_TESTING else "pm_admin_security.db"
        _admin_sqlite_engine = create_async_engine(
            f"sqlite+aiosqlite:///{db_file}",
            echo=ECHO_SQL,
            future=True,
            connect_args={"check_same_thread": False},
        )
        _admin_sqlite_sessionmaker = async_sessionmaker(
            bind=_admin_sqlite_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _admin_sqlite_sessionmaker


def _get_admin_pg_sessionmaker():
    global _admin_pg_engine, _admin_pg_sessionmaker
    if _admin_pg_sessionmaker is None:
        _admin_pg_engine = create_async_engine(
            get_postgres_url(),
            echo=ECHO_SQL,
            future=True,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            connect_args={
                "command_timeout": 10,
                "server_settings": {"search_path": '"project_manager", public'},
            },
        )
        _admin_pg_sessionmaker = async_sessionmaker(
            bind=_admin_pg_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _admin_pg_sessionmaker


async def ensure_security_initialized():
    global _security_initialized
    if not _security_initialized:
        await init_admin_security()
        _security_initialized = True


async def get_admin_db_session() -> AsyncSession:
    await ensure_security_initialized()
    if IS_TESTING:
        sf = _get_admin_sqlite_sessionmaker()
        async with sf() as session:
            yield session
        return
    try:
        sf = _get_admin_pg_sessionmaker()
        async with sf() as session:
            await session.execute(text("SELECT uuid FROM pm_admin_users LIMIT 1"))
            yield session
            return
    except Exception as exc:
        logger.warning(f"PG admin session unavailable or pre-migration ({exc}), using SQLite.")
        sf = _get_admin_sqlite_sessionmaker()
        async with sf() as session:
            yield session


# ── Crypto Helpers ────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


def create_access_token(
    username: str,
    role: str,
    email: str,
    hours: int = JWT_EXPIRATION_HOURS,
    user_uuid: Optional[str] = None,
) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "sub":   username,
        "uuid":  user_uuid,
        "role":  role,
        "email": email,
        "iat":   now,
        "exp":   now + datetime.timedelta(hours=hours),
        "jti":   secrets.token_hex(16),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


# ── Rate Limiter ──────────────────────────────────────────────────────────────

def check_login_rate_limit(client_ip: str) -> bool:
    try:
        import redis
        r = redis.Redis(host="localhost", port=6379, db=0, socket_timeout=1)
        key = f"pm_auth_fail:{client_ip}"
        fails = r.get(key)
        return not (fails and int(fails) >= 5)
    except Exception:
        return True


def record_failed_login(client_ip: str):
    try:
        import redis
        r = redis.Redis(host="localhost", port=6379, db=0, socket_timeout=1)
        key = f"pm_auth_fail:{client_ip}"
        pipe = r.pipeline()
        pipe.incr(key)
        pipe.expire(key, 900)
        pipe.execute()
    except Exception:
        pass


def clear_failed_login(client_ip: str):
    try:
        import redis
        r = redis.Redis(host="localhost", port=6379, db=0, socket_timeout=1)
        r.delete(f"pm_auth_fail:{client_ip}")
    except Exception:
        pass


# ── DB Init & Seeder ──────────────────────────────────────────────────────────

async def init_admin_security():
    from app.database import Base
    import app.security_models  # noqa: F401

    sf = _get_admin_sqlite_sessionmaker()
    async with _admin_sqlite_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(text("ALTER TABLE pm_admin_users ADD COLUMN uuid VARCHAR(36)"))
        except Exception:
            pass

    if not IS_TESTING:
        try:
            pg_sf = _get_admin_pg_sessionmaker()
            async with _admin_pg_engine.begin() as conn:
                await conn.execute(text('CREATE SCHEMA IF NOT EXISTS "project_manager"'))
                await conn.run_sync(Base.metadata.create_all)
        except Exception as exc:
            logger.warning(f"PG admin security init deferred: {exc}")

    pwd_hash = hash_password(DEFAULT_ADMIN_PASS)
    import uuid as _uuid
    default_admin_uuid = str(_uuid.uuid5(_uuid.NAMESPACE_DNS, f"{DEFAULT_ADMIN_USER}.aetherops.local"))

    async with sf() as session:
        res = await session.execute(select(AdminUser).where(AdminUser.username == DEFAULT_ADMIN_USER))
        existing_admin = res.scalar_one_or_none()
        if not existing_admin:
            session.add(AdminUser(
                uuid=default_admin_uuid,
                username=DEFAULT_ADMIN_USER,
                email=DEFAULT_ADMIN_EMAIL,
                password_hash=pwd_hash,
                role="SUPER_ADMIN",
                is_active=True,
                created_at=datetime.datetime.utcnow(),
            ))
            await session.commit()
            logger.info(f"Seeded default admin '{DEFAULT_ADMIN_USER}' in SQLite.")
        elif not existing_admin.uuid:
            existing_admin.uuid = default_admin_uuid
            await session.commit()

    if not IS_TESTING:
        try:
            async with _get_admin_pg_sessionmaker()() as session:
                res = await session.execute(select(AdminUser).where(AdminUser.username == DEFAULT_ADMIN_USER))
                pg_admin = res.scalar_one_or_none()
                if not pg_admin:
                    session.add(AdminUser(
                        uuid=default_admin_uuid,
                        username=DEFAULT_ADMIN_USER,
                        email=DEFAULT_ADMIN_EMAIL,
                        password_hash=pwd_hash,
                        role="SUPER_ADMIN",
                        is_active=True,
                        created_at=datetime.datetime.utcnow(),
                    ))
                    await session.commit()
                elif not pg_admin.uuid:
                    pg_admin.uuid = default_admin_uuid
                    await session.commit()
        except Exception as exc:
            logger.warning(f"PG admin seed deferred: {exc}")


# ── Auth Middleware ───────────────────────────────────────────────────────────

async def get_current_admin(request: Request) -> Dict[str, Any]:
    """
    Multi-channel authentication:
    1. Authorization: Bearer <JWT> (explicit token)
    2. HttpOnly cookie → JWT (browser session)
    3. X-Admin-Key header (API key fallback)
    """
    # 1. Bearer (explicit token header takes precedence over ambient cookies)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        payload = decode_access_token(auth_header.split(" ", 1)[1].strip())
        if payload:
            return {
                "username":  payload.get("sub"),
                "uuid":      payload.get("uuid"),
                "role":      payload.get("role"),
                "email":     payload.get("email"),
                "auth_type": "bearer",
            }

    # 2. Cookie (ambient browser session)
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        payload = decode_access_token(token)
        if payload:
            return {
                "username":  payload.get("sub"),
                "uuid":      payload.get("uuid"),
                "role":      payload.get("role"),
                "email":     payload.get("email"),
                "auth_type": "cookie",
            }

    # 3. X-Admin-Key
    admin_key = request.headers.get("X-Admin-Key", "")
    if admin_key and MASTER_ADMIN_KEY and secrets.compare_digest(admin_key.strip(), MASTER_ADMIN_KEY):
        return {
            "username":  "root_admin",
            "uuid":      "00000000-0000-0000-0000-000000000001",
            "role":      "SUPER_ADMIN",
            "email":     "root@aetherops.cloud",
            "auth_type": "api_key",
        }

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: valid session required.")


async def register_user(username: str, email: str, password: str, role: str = "USER") -> Dict[str, Any]:
    """Register a new user account in PostgreSQL / SQLite."""
    import uuid as _uuid
    async for session in get_admin_db_session():
        res = await session.execute(
            select(AdminUser).where((AdminUser.username == username) | (AdminUser.email == email))
        )
        existing = res.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already registered.")

        pwd_hash = hash_password(password)
        new_uuid = str(_uuid.uuid4())
        new_user = AdminUser(
            uuid=new_uuid,
            username=username,
            email=email,
            password_hash=pwd_hash,
            role=role,
            is_active=True,
            created_at=datetime.datetime.utcnow(),
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        token = create_access_token(new_user.username, new_user.role, new_user.email, user_uuid=new_user.uuid)
        return {"token": token, "username": new_user.username, "role": new_user.role, "email": new_user.email, "uuid": new_user.uuid}


async def login_admin(username_or_email: str, password: str, request: Request):
    """Validate credentials via username or email, return JWT token + set HttpOnly cookie."""
    client_ip = request.client.host if request.client else "127.0.0.1"

    if not check_login_rate_limit(client_ip):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many failed attempts. Try again in 15 minutes.")

    ident = (username_or_email or "").strip().lower()
    async for session in get_admin_db_session():
        res = await session.execute(
            select(AdminUser).where((AdminUser.username == ident) | (AdminUser.email == ident))
        )
        user = res.scalar_one_or_none()

        if not user or not user.is_active or not verify_password(password, user.password_hash):
            record_failed_login(client_ip)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")

        clear_failed_login(client_ip)
        if not user.uuid:
            import uuid as _uuid
            user.uuid = str(_uuid.uuid5(_uuid.NAMESPACE_DNS, f"{user.username}.aetherops.local"))
            await session.commit()

        token = create_access_token(user.username, user.role, user.email, user_uuid=user.uuid)

        user.last_login_at = datetime.datetime.utcnow()
        await session.commit()

        return {"token": token, "username": user.username, "role": user.role, "email": user.email, "uuid": user.uuid}
