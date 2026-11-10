# services/architecture_generator/app/database.py
import os
import sys
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import event, text

logger = logging.getLogger("architecture-database")

IS_TESTING = "pytest" in sys.modules or any("pytest" in arg for arg in sys.argv)

POSTGRES_USER     = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgrespassword")
POSTGRES_HOST     = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT     = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB       = os.getenv("POSTGRES_DB", "aether_catalog")
RAW_DATABASE_URL  = os.getenv("DATABASE_URL", "")
ECHO_SQL          = os.getenv("ECHO_SQL", "False").lower() in ("true", "1", "yes")

Base = declarative_base()

def get_sqlite_url() -> str:
    return "sqlite+aiosqlite:///test_architecture.db" if IS_TESTING else "sqlite+aiosqlite:///architecture.db"

def get_postgres_url() -> str:
    if RAW_DATABASE_URL.startswith(("postgresql", "postgres")):
        return (RAW_DATABASE_URL
                .replace("postgresql://", "postgresql+asyncpg://")
                .replace("postgres://", "postgresql+asyncpg://"))
    return (f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
            f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

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
                          "server_settings": {"search_path": '"architecture", public'}},
        )
    return _pg_engine

def get_pg_sessionmaker():
    global _pg_sm
    if _pg_sm is None:
        _pg_sm = async_sessionmaker(bind=get_pg_engine(), class_=AsyncSession,
                                    expire_on_commit=False, autocommit=False, autoflush=False)
    return _pg_sm

async def get_session():
    use_postgres = bool(os.getenv("DATABASE_URL") or os.getenv("POSTGRES_HOST"))
    if use_postgres and not IS_TESTING:
        try:
            sm = get_pg_sessionmaker()
            async with sm() as session:
                yield session
                return
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed ({e}), falling back to SQLite: {get_sqlite_url()}")
    
    sm = get_sqlite_sessionmaker()
    async with sm() as session:
        yield session

async def init_db():
    engine = get_sqlite_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        if os.getenv("DATABASE_URL") or os.getenv("POSTGRES_HOST"):
            pg_engine = get_pg_engine()
            async with pg_engine.begin() as conn:
                await conn.execute(text("CREATE SCHEMA IF NOT EXISTS architecture;"))
                await conn.run_sync(Base.metadata.create_all)
            logger.info("PostgreSQL architecture database initialized successfully.")
    except Exception as e:
        logger.warning(f"PostgreSQL initialization notice: {e}")
