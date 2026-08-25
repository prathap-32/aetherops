# services/requirement_analysis/app/database.py
import os
import sys
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import event
from fastapi import Request

logger = logging.getLogger("requirement-analysis-database")

# Detect if running under pytest to isolate test database state
IS_TESTING = "pytest" in sys.modules or any("pytest" in arg for arg in sys.argv)

if IS_TESTING:
    DATABASE_URL = "sqlite+aiosqlite:///test_catalog.db"
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///catalog.db")

ECHO_SQL = os.getenv("ECHO_SQL", "False").lower() in ("true", "1", "yes")

# Configure the default async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=ECHO_SQL,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Apply SQLite performance PRAGMAs on connection
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.execute("PRAGMA cache_size = -64000;")
    cursor.execute("PRAGMA busy_timeout = 5000;")
    cursor.close()

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

# Supported AWS Regions for production
# All 39 regions from the user's master list
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

# Cache of engines and sessionmakers by region
_region_engines = {}
_region_sessions = {}

def get_region_db_url(region: str) -> str:
    region = region.lower().strip()
    if IS_TESTING:
        return f"sqlite+aiosqlite:///test_catalog_{region}.db"
    else:
        return f"sqlite+aiosqlite:///catalog_{region}.db"

def get_engine_for_region(region: str):
    region = region.lower().strip()
    if region not in _region_engines:
        url = get_region_db_url(region)
        eng = create_async_engine(
            url,
            echo=ECHO_SQL,
            future=True,
            connect_args={"check_same_thread": False} if "sqlite" in url else {}
        )
        # Apply SQLite performance PRAGMAs on connection
        @event.listens_for(eng.sync_engine, "connect")
        def set_region_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode = WAL;")
            cursor.execute("PRAGMA synchronous = NORMAL;")
            cursor.execute("PRAGMA cache_size = -64000;")
            cursor.execute("PRAGMA busy_timeout = 5000;")
            cursor.close()
        _region_engines[region] = eng
    return _region_engines[region]

def get_sessionmaker_for_region(region: str):
    region = region.lower().strip()
    if region not in _region_sessions:
        eng = get_engine_for_region(region)
        _region_sessions[region] = async_sessionmaker(
            bind=eng,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    return _region_sessions[region]

async def init_db_for_region(region: str):
    """
    Ensures that database tables are initialized for the specified region.
    """
    region = region.lower().strip()
    eng = get_engine_for_region(region)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db_session(request: Request = None) -> AsyncSession:
    """
    Dependency helper to yield an async database session mapped to the requested region.
    """
    region = "us-east-1"
    if request is not None:
        # Check query parameters
        region = request.query_params.get("region", "us-east-1")
    
    region = region.lower().strip()
    # Auto-initialize schemas if not done
    await init_db_for_region(region)
    
    session_factory = get_sessionmaker_for_region(region)
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
