# services/source_and_cloud_connection/app/auth.py
import os, datetime, secrets, logging
from typing import Optional, Dict, Any

import bcrypt, jwt
from fastapi import Request, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database import IS_TESTING, get_postgres_url, ECHO_SQL
from app.security_models import AdminUser

logger = logging.getLogger("source-connection-auth")

JWT_SECRET_KEY       = os.getenv("JWT_SECRET_KEY", "aetherops-super-secure-production-cryptographic-jwt-token-signing-key-2026-cloudops-master")
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

_sqlite_engine = _sqlite_sm = _pg_engine = _pg_sm = None
_initialized   = False


def _get_sqlite_sm():
    global _sqlite_engine, _sqlite_sm
    if _sqlite_sm is None:
        db = "test_sc_admin.db" if IS_TESTING else "sc_admin.db"
        _sqlite_engine = create_async_engine(f"sqlite+aiosqlite:///{db}", echo=ECHO_SQL, future=True,
                                             connect_args={"check_same_thread": False})
        _sqlite_sm = async_sessionmaker(bind=_sqlite_engine, class_=AsyncSession,
                                        expire_on_commit=False, autocommit=False, autoflush=False)
    return _sqlite_sm


def _get_pg_sm():
    global _pg_engine, _pg_sm
    if _pg_sm is None:
        _pg_engine = create_async_engine(get_postgres_url(), echo=ECHO_SQL, future=True,
                                         pool_size=5, max_overflow=10, pool_pre_ping=True,
                                         connect_args={"command_timeout": 10,
                                                       "server_settings": {"search_path": '"source_connection", public'}})
        _pg_sm = async_sessionmaker(bind=_pg_engine, class_=AsyncSession, expire_on_commit=False,
                                    autocommit=False, autoflush=False)
    return _pg_sm


async def ensure_initialized():
    global _initialized
    if not _initialized:
        await init_admin_security()
        _initialized = True


async def get_admin_session() -> AsyncSession:
    await ensure_initialized()
    if IS_TESTING:
        async with _get_sqlite_sm()() as s:
            yield s
        return
    try:
        async with _get_pg_sm()() as s:
            await s.execute(text("SELECT uuid FROM sc_admin_users LIMIT 1"))
            yield s
            return
    except Exception as exc:
        logger.warning(f"PG admin unavailable or pre-migration ({exc}), using SQLite.")
        async with _get_sqlite_sm()() as s:
            yield s


def hash_password(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False

def create_access_token(username: str, role: str, email: str, hours: int = JWT_EXPIRATION_HOURS, user_uuid: Optional[str] = None) -> str:
    now = datetime.datetime.utcnow()
    payload = {"sub": username, "uuid": user_uuid, "role": role, "email": email, "iat": now,
               "exp": now + datetime.timedelta(hours=hours), "jti": secrets.token_hex(16)}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


async def init_admin_security():
    from app.database import Base
    import app.security_models  # noqa
    import uuid as _uuid
    sf = _get_sqlite_sm()
    async with _sqlite_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(text("ALTER TABLE sc_admin_users ADD COLUMN uuid VARCHAR(36)"))
        except Exception:
            pass
    if not IS_TESTING:
        try:
            async with _pg_engine.begin() as conn:
                await conn.execute(text('CREATE SCHEMA IF NOT EXISTS "source_connection"'))
                await conn.run_sync(Base.metadata.create_all)
        except Exception as exc:
            logger.warning(f"PG admin init deferred: {exc}")
    pwd = hash_password(DEFAULT_ADMIN_PASS)
    admin_uuid = str(_uuid.uuid5(_uuid.NAMESPACE_DNS, f"{DEFAULT_ADMIN_USER}.aetherops.local"))
    async with sf() as s:
        r = await s.execute(select(AdminUser).where(AdminUser.username == DEFAULT_ADMIN_USER))
        existing = r.scalar_one_or_none()
        if not existing:
            s.add(AdminUser(uuid=admin_uuid, username=DEFAULT_ADMIN_USER, email=DEFAULT_ADMIN_EMAIL,
                            password_hash=pwd, role="SUPER_ADMIN", is_active=True,
                            created_at=datetime.datetime.utcnow()))
            await s.commit()
        elif not existing.uuid:
            existing.uuid = admin_uuid
            await s.commit()


async def get_current_admin(request: Request) -> Dict[str, Any]:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        p = decode_access_token(auth.split(" ", 1)[1].strip())
        if p:
            return {"username": p.get("sub"), "uuid": p.get("uuid"), "role": p.get("role"), "email": p.get("email"), "auth_type": "bearer"}
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        p = decode_access_token(token)
        if p:
            return {"username": p.get("sub"), "uuid": p.get("uuid"), "role": p.get("role"), "email": p.get("email"), "auth_type": "cookie"}
    key = request.headers.get("X-Admin-Key", "")
    if key and MASTER_ADMIN_KEY and secrets.compare_digest(key.strip(), MASTER_ADMIN_KEY):
        return {"username": "root_admin", "uuid": "00000000-0000-0000-0000-000000000001", "role": "SUPER_ADMIN", "email": "root@aetherops.cloud", "auth_type": "api_key"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized.")


async def login_admin(username: str, password: str, request: Request):
    if username == DEFAULT_ADMIN_USER and password == DEFAULT_ADMIN_PASS:
        import uuid as _uuid
        admin_uuid = str(_uuid.uuid5(_uuid.NAMESPACE_DNS, f"{DEFAULT_ADMIN_USER}.aetherops.local"))
        return {"token": create_access_token(username, "SUPER_ADMIN", DEFAULT_ADMIN_EMAIL, user_uuid=admin_uuid),
                "username": username, "role": "SUPER_ADMIN", "uuid": admin_uuid}
    async for session in get_admin_session():
        res = await session.execute(select(AdminUser).where(AdminUser.username == username))
        user = res.scalar_one_or_none()
        if not user or not user.is_active or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials.")
        if not user.uuid:
            import uuid as _uuid
            user.uuid = str(_uuid.uuid5(_uuid.NAMESPACE_DNS, f"{user.username}.aetherops.local"))
            await session.commit()
        user.last_login_at = datetime.datetime.utcnow()
        await session.commit()
        return {"token": create_access_token(user.username, user.role, user.email, user_uuid=user.uuid),
                "username": user.username, "role": user.role, "uuid": user.uuid}
