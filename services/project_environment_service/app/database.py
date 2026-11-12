# services/project_and_environment_management/app/database.py
import os
import sys
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import event, text

logger = logging.getLogger("project-manager-database")

IS_TESTING = "pytest" in sys.modules or any("pytest" in arg for arg in sys.argv)

POSTGRES_USER     = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgrespassword")
POSTGRES_HOST     = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT     = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB       = os.getenv("POSTGRES_DB", "aetherops_platform")
RAW_DATABASE_URL  = os.getenv("DATABASE_URL", "")
ECHO_SQL          = os.getenv("ECHO_SQL", "False").lower() in ("true", "1", "yes")
ENVIRONMENT       = os.getenv("AETHER_ENV", os.getenv("ENVIRONMENT", "development")).lower()

Base = declarative_base()

# ── URL Helpers ───────────────────────────────────────────────────────────────

def get_sqlite_url() -> str:
    if IS_TESTING:
        return "sqlite+aiosqlite:///test_projects.db"
    return "sqlite+aiosqlite:///projects.db"


def get_postgres_url() -> str:
    if RAW_DATABASE_URL.startswith("postgresql") or RAW_DATABASE_URL.startswith("postgres"):
        return (RAW_DATABASE_URL
                .replace("postgresql://", "postgresql+asyncpg://")
                .replace("postgres://", "postgresql+asyncpg://"))
    return (
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )


# ── Engine Singletons ─────────────────────────────────────────────────────────

_sqlite_engine      = None
_sqlite_sessionmaker = None
_pg_engine          = None
_pg_sessionmaker    = None


def get_sqlite_engine():
    global _sqlite_engine
    if _sqlite_engine is None:
        _sqlite_engine = create_async_engine(
            get_sqlite_url(),
            echo=ECHO_SQL,
            future=True,
            connect_args={"check_same_thread": False},
        )

        @event.listens_for(_sqlite_engine.sync_engine, "connect")
        def _set_pragmas(dbapi_conn, _record):
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA journal_mode = WAL;")
            cur.execute("PRAGMA synchronous  = NORMAL;")
            cur.execute("PRAGMA cache_size   = -64000;")
            cur.execute("PRAGMA busy_timeout = 5000;")
            cur.close()

    return _sqlite_engine


def get_sqlite_sessionmaker():
    global _sqlite_sessionmaker
    if _sqlite_sessionmaker is None:
        _sqlite_sessionmaker = async_sessionmaker(
            bind=get_sqlite_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _sqlite_sessionmaker


def get_pg_engine():
    global _pg_engine
    if _pg_engine is None:
        _pg_engine = create_async_engine(
            get_postgres_url(),
            echo=ECHO_SQL,
            future=True,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            connect_args={
                "command_timeout": 10,
                "server_settings": {"search_path": '"project_management", public'},
            },
        )
    return _pg_engine


def get_pg_sessionmaker():
    global _pg_sessionmaker
    if _pg_sessionmaker is None:
        _pg_sessionmaker = async_sessionmaker(
            bind=get_pg_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _pg_sessionmaker


# ── DB Init ───────────────────────────────────────────────────────────────────

async def init_projects_db():
    """Create all tables in SQLite (development/test) or PostgreSQL (production/runtime)."""
    import app.models  # noqa: F401 — registers ORM models onto Base.metadata

    # 1. SQLite (only for testing or development)
    if IS_TESTING or ENVIRONMENT != "production":
        eng = get_sqlite_engine()
        async with eng.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            for table, col, col_type in [
                ("aether_projects", "tenant_id", "VARCHAR(36)"),
                ("aether_projects", "created_by_user_id", "VARCHAR(36)"),
                ("aether_projects", "account_id", "VARCHAR(36)"),
                ("aether_environments", "tenant_id", "VARCHAR(36)"),
                ("aether_environments", "created_by_user_id", "VARCHAR(36)"),
                ("aether_environments", "account_id", "VARCHAR(36)"),
            ]:
                try:
                    await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                except Exception:
                    pass
        logger.info("projects.db initialised (SQLite WAL).")

    # 2. PostgreSQL (primary durable store)
    if not IS_TESTING:
        try:
            pg = get_pg_engine()
            async with pg.begin() as conn:
                await conn.execute(text('CREATE SCHEMA IF NOT EXISTS "project_manager"'))
                await conn.run_sync(Base.metadata.create_all)
                for table, col, col_type in [
                    ("aether_projects", "tenant_id", "VARCHAR(36)"),
                    ("aether_projects", "created_by_user_id", "VARCHAR(36)"),
                    ("aether_projects", "account_id", "VARCHAR(36)"),
                    ("aether_environments", "tenant_id", "VARCHAR(36)"),
                    ("aether_environments", "created_by_user_id", "VARCHAR(36)"),
                    ("aether_environments", "account_id", "VARCHAR(36)"),
                ]:
                    try:
                        await conn.execute(text(f'ALTER TABLE "project_manager".{table} ADD COLUMN IF NOT EXISTS {col} {col_type}'))
                    except Exception:
                        pass
            logger.info("PostgreSQL schema 'project_manager' initialised.")
        except Exception as exc:
            if ENVIRONMENT == "production":
                raise RuntimeError(f"FATAL: PostgreSQL database initialization failed in production: {exc}")
            logger.warning(f"PostgreSQL init deferred: {exc}")


# ── Session Dependency ────────────────────────────────────────────────────────

async def get_db() -> AsyncSession:
    """
    Yields an async session.
    Primary: PostgreSQL Docker container (`aether_postgres`).
    Fallback / Test: Local SQLite with WAL mode.
    """
    await init_projects_db()

    # In automated test suites, use SQLite for hermetic test execution
    if IS_TESTING:
        sf = get_sqlite_sessionmaker()
        async with sf() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
        return

    # In production/runtime, primary is PostgreSQL container
    pg_ok = False
    pg_session: AsyncSession | None = None
    try:
        pg_sf = get_pg_sessionmaker()
        pg_session = pg_sf()
        await pg_session.execute(text("SELECT tenant_id FROM aether_projects LIMIT 1"))
        pg_ok = True
    except Exception as exc:
        if ENVIRONMENT == "production":
            if pg_session:
                await pg_session.close()
            raise RuntimeError(
                f"FATAL: PostgreSQL database connection failed in production ({exc}). Silent SQLite fallback is strictly prohibited."
            )
        logger.warning(f"PostgreSQL container unavailable or pre-migration ({exc}), failing over to SQLite for development.")
        if pg_session:
            await pg_session.close()
            pg_session = None

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
        sf = get_sqlite_sessionmaker()
        async with sf() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# ── Convenience aliases ───────────────────────────────────────────────────────
engine            = get_sqlite_engine()
AsyncSessionLocal = get_sqlite_sessionmaker()
