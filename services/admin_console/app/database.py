# services/requirement_analysis/app/database.py
import os
import sys
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import event, text
from fastapi import Request

logger = logging.getLogger("requirement-analysis-database")

# Detect test execution environment
IS_TESTING = "pytest" in sys.modules or any("pytest" in arg for arg in sys.argv)

# PostgreSQL Environment Defaults (Docker Container)
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgrespassword")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "aether_catalog")

RAW_DATABASE_URL = os.getenv("DATABASE_URL", "")

ECHO_SQL = os.getenv("ECHO_SQL", "False").lower() in ("true", "1", "yes")

Base = declarative_base()

# All 39 Supported AWS Regions
SUPPORTED_REGIONS = [
    # North America
    "us-east-1", "us-east-2", "us-west-1", "us-west-2", "ca-central-1", "ca-west-1", "mx-central-1", "us-gov-east-1", "us-gov-west-1",
    # South America
    "sa-east-1",
    # Europe
    "eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1", "eu-central-2", "eu-north-1", "eu-south-1", "eu-south-2",
    # Asia Pacific
    "ap-south-1", "ap-south-2", "ap-southeast-1", "ap-southeast-2", "ap-southeast-3", "ap-southeast-4", "ap-southeast-5", "ap-southeast-6", "ap-southeast-7", "ap-east-1", "ap-east-2", "ap-northeast-1", "ap-northeast-2", "ap-northeast-3",
    # Middle East
    "me-south-1", "me-central-1", "il-central-1", "me-central-2",
    # Africa
    "af-south-1",
    # China
    "cn-north-1", "cn-northwest-1"
]

def get_sqlite_url(region: str) -> str:
    region_raw = region.lower().strip()
    if IS_TESTING:
        return f"sqlite+aiosqlite:///test_catalog_{region_raw}.db"
    return f"sqlite+aiosqlite:///catalog_{region_raw}.db"

def get_postgres_url(region: str) -> str:
    if RAW_DATABASE_URL.startswith("postgresql") or RAW_DATABASE_URL.startswith("postgres"):
        return RAW_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://").replace("postgres://", "postgresql+asyncpg://")
    return f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Engine & Session Registries
_sqlite_engines = {}
_sqlite_sessions = {}
_postgres_engines = {}
_postgres_sessions = {}

def get_sqlite_engine(region: str):
    region = region.lower().strip()
    if region not in _sqlite_engines:
        url = get_sqlite_url(region)
        eng = create_async_engine(
            url,
            echo=ECHO_SQL,
            future=True,
            connect_args={"check_same_thread": False}
        )
        @event.listens_for(eng.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode = WAL;")
            cursor.execute("PRAGMA synchronous = NORMAL;")
            cursor.execute("PRAGMA cache_size = -64000;")
            cursor.execute("PRAGMA busy_timeout = 5000;")
            cursor.close()
        _sqlite_engines[region] = eng
    return _sqlite_engines[region]

def get_sqlite_sessionmaker(region: str):
    region = region.lower().strip()
    if region not in _sqlite_sessions:
        eng = get_sqlite_engine(region)
        _sqlite_sessions[region] = async_sessionmaker(
            bind=eng,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    return _sqlite_sessions[region]

def get_postgres_engine(region: str):
    region_raw = region.lower().strip()
    region_pg = region_raw.replace("-", "_")
    if region_raw not in _postgres_engines:
        url = get_postgres_url(region_raw)
        _postgres_engines[region_raw] = create_async_engine(
            url,
            echo=ECHO_SQL,
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            connect_args={
                "command_timeout": 10,
                "server_settings": {"search_path": f'"region_{region_pg}", public'}
            }
        )
    return _postgres_engines[region_raw]

def get_postgres_sessionmaker(region: str):
    region = region.lower().strip()
    if region not in _postgres_sessions:
        eng = get_postgres_engine(region)
        _postgres_sessions[region] = async_sessionmaker(
            bind=eng,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    return _postgres_sessions[region]

# Backward Compatibility Aliases
def get_region_db_url(region: str) -> str:
    return get_sqlite_url(region)

def get_engine_for_region(region: str):
    return get_sqlite_engine(region)

def get_sessionmaker_for_region(region: str):
    return get_sqlite_sessionmaker(region)

async def init_db_for_region(region: str):
    """
    Initializes database tables for the given region in local SQLite and PostgreSQL (if reachable).
    """
    import app.models  # Register all ORM models onto Base.metadata
    region_raw = region.lower().strip()
    region_pg = region_raw.replace("-", "_")
    
    # 1. Initialize local SQLite
    sqlite_eng = get_sqlite_engine(region_raw)
    async with sqlite_eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Try initializing PostgreSQL container DB if not testing
    if not IS_TESTING:
        try:
            pg_eng = get_postgres_engine(region_raw)
            async with pg_eng.begin() as conn:
                await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "region_{region_pg}"'))
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            logger.warning(f"PostgreSQL initialization deferred for region '{region_raw}': {e}")

async def get_db_session(request: Request = None) -> AsyncSession:
    """
    Resilient Database Session Dependency:
    1. Primary Path: Uses local SQLite (0ms local file read).
    2. Failover Path: If SQLite file is missing/error, fails over to PostgreSQL Docker Container.
    """
    region = "us-east-1"
    if request is not None:
        region = request.query_params.get("region", "us-east-1")
    
    region = region.lower().strip()
    await init_db_for_region(region)

    sqlite_sf = get_sqlite_sessionmaker(region)
    sqlite_available = False
    
    try:
        session = sqlite_sf()
        await session.execute(text("SELECT 1"))
        sqlite_available = True
    except Exception as sqlite_err:
        logger.warning(f"Local SQLite database unavailable for region '{region}': {sqlite_err}. Failing over to PostgreSQL Docker container...")
        sqlite_available = False

    if sqlite_available:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    else:
        pg_sf = get_postgres_sessionmaker(region)
        async with pg_sf() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

# Default engine and sessionmaker for general imports
engine = get_sqlite_engine("us-east-1")
AsyncSessionLocal = get_sqlite_sessionmaker("us-east-1")

# Module 1 Dedicated Requirements Database (SQLite + Redis Architecture)
_requirements_engine = None
_requirements_sessionmaker = None

def get_requirements_db_url() -> str:
    if IS_TESTING:
        return "sqlite+aiosqlite:///test_requirements.db"
    return "sqlite+aiosqlite:///requirements.db"

def get_requirements_engine():
    global _requirements_engine
    if _requirements_engine is None:
        url = get_requirements_db_url()
        _requirements_engine = create_async_engine(
            url,
            echo=ECHO_SQL,
            future=True,
            connect_args={"check_same_thread": False}
        )
        @event.listens_for(_requirements_engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode = WAL;")
            cursor.execute("PRAGMA synchronous = NORMAL;")
            cursor.execute("PRAGMA cache_size = -64000;")
            cursor.execute("PRAGMA busy_timeout = 5000;")
            cursor.close()
    return _requirements_engine

def get_requirements_sessionmaker():
    global _requirements_sessionmaker
    if _requirements_sessionmaker is None:
        eng = get_requirements_engine()
        _requirements_sessionmaker = async_sessionmaker(
            bind=eng,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    return _requirements_sessionmaker

async def init_requirements_db():
    eng = get_requirements_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_requirements_db() -> AsyncSession:
    await init_requirements_db()
    sf = get_requirements_sessionmaker()
    async with sf() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

