# services/source_and_cloud_connection/app/database.py
import os
import sys
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import event, text

logger = logging.getLogger("source-connection-database")

IS_TESTING = "pytest" in sys.modules or any("pytest" in arg for arg in sys.argv)

POSTGRES_USER     = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgrespassword")
POSTGRES_HOST     = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT     = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB       = os.getenv("POSTGRES_DB", "aether_catalog")
RAW_DATABASE_URL  = os.getenv("DATABASE_URL", "")
ECHO_SQL          = os.getenv("ECHO_SQL", "False").lower() in ("true", "1", "yes")

Base = declarative_base()

# ── URL Helpers ───────────────────────────────────────────────────────────────

def get_sqlite_url() -> str:
    return "sqlite+aiosqlite:///test_source_connections.db" if IS_TESTING else "sqlite+aiosqlite:///source_connections.db"


def get_postgres_url() -> str:
    if RAW_DATABASE_URL.startswith(("postgresql", "postgres")):
        return (RAW_DATABASE_URL
                .replace("postgresql://", "postgresql+asyncpg://")
                .replace("postgres://", "postgresql+asyncpg://"))
    return (f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
            f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")


# ── Engine Singletons ─────────────────────────────────────────────────────────

_sqlite_engine = _sqlite_sm = _pg_engine = _pg_sm = None


def get_sqlite_engine():
    global _sqlite_engine
    if _sqlite_engine is None:
        _sqlite_engine = create_async_engine(
            get_sqlite_url(), echo=ECHO_SQL, future=True,
            connect_args={"check_same_thread": False},
        )
        @event.listens_for(_sqlite_engine.sync_engine, "connect")
        def _pragmas(conn, _):
            cur = conn.cursor()
            for p in ["PRAGMA journal_mode=WAL;", "PRAGMA synchronous=NORMAL;",
                      "PRAGMA cache_size=-64000;", "PRAGMA busy_timeout=5000;"]:
                cur.execute(p)
            cur.close()
    return _sqlite_engine


def get_sqlite_sessionmaker():
    global _sqlite_sm
    if _sqlite_sm is None:
        _sqlite_sm = async_sessionmaker(bind=get_sqlite_engine(), class_=AsyncSession,
                                        expire_on_commit=False, autocommit=False, autoflush=False)
    return _sqlite_sm


def get_pg_engine():
    global _pg_engine
    if _pg_engine is None:
        _pg_engine = create_async_engine(
            get_postgres_url(), echo=ECHO_SQL, future=True,
            pool_size=5, max_overflow=10, pool_pre_ping=True,
            connect_args={"command_timeout": 10,
                          "server_settings": {"search_path": '"source_connection", public'}},
        )
    return _pg_engine


def get_pg_sessionmaker():
    global _pg_sm
    if _pg_sm is None:
        _pg_sm = async_sessionmaker(bind=get_pg_engine(), class_=AsyncSession,
                                    expire_on_commit=False, autocommit=False, autoflush=False)
    return _pg_sm


# ── DB Init ───────────────────────────────────────────────────────────────────

async def init_source_db():
    import app.models  # noqa: registers ORM models
    eng = get_sqlite_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        for col_name, col_def in [
            ("auth_type", "VARCHAR(30) DEFAULT 'PAT'"),
            ("github_user", "VARCHAR(100)"),
            ("tenant_id", "VARCHAR(36)"),
            ("created_by_user_id", "VARCHAR(36)"),
        ]:
            try:
                await conn.execute(text(f"ALTER TABLE sc_git_connections ADD COLUMN {col_name} {col_def}"))
            except Exception:
                pass

        for col_name, col_def in [
            ("tenant_id", "VARCHAR(36)"),
            ("created_by_user_id", "VARCHAR(36)"),
        ]:
            try:
                await conn.execute(text(f"ALTER TABLE sc_cloud_connections ADD COLUMN {col_name} {col_def}"))
            except Exception:
                pass
    if not IS_TESTING:
        try:
            pg = get_pg_engine()
            async with pg.begin() as conn:
                await conn.execute(text('CREATE SCHEMA IF NOT EXISTS "source_connection"'))
                await conn.run_sync(Base.metadata.create_all)
        except Exception as exc:
            logger.warning(f"PostgreSQL init deferred: {exc}")


# ── Session Dependency ────────────────────────────────────────────────────────

async def get_db() -> AsyncSession:
    """
    Yields an async session.
    Primary: PostgreSQL Docker container (`aether_postgres`).
    Fallback / Test: Local SQLite with WAL mode.
    """
    await init_source_db()

    if IS_TESTING:
        async with get_sqlite_sessionmaker()() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
        return

    pg_ok = False
    pg_session = None
    try:
        pg_sf = get_pg_sessionmaker()
        pg_session = pg_sf()
        await pg_session.execute(text("SELECT tenant_id FROM sc_git_connections LIMIT 1"))
        pg_ok = True
    except Exception as exc:
        logger.warning(f"PostgreSQL container unavailable or pre-migration ({exc}), failing over to SQLite.")
        if pg_session:
            await pg_session.close()

    if pg_ok and pg_session:
        try:
            yield pg_session
            await pg_session.commit()
        except Exception:
            await pg_session.rollback()
            raise
        finally:
            await pg_session.close()
    else:
        async with get_sqlite_sessionmaker()() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


engine            = get_sqlite_engine()
AsyncSessionLocal = get_sqlite_sessionmaker()
