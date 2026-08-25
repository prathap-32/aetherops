# services/requirement_analysis/app/database.py
import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from fastapi import Request

logger = logging.getLogger("requirement-analysis-database")

# Default to local SQLite fallback if DATABASE_URL is not set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./catalog.db")

# Echo SQL queries in development/debug modes
ECHO_SQL = os.getenv("ECHO_SQL", "False").lower() in ("true", "1", "yes")

# Configure the default async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=ECHO_SQL,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

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
SUPPORTED_REGIONS = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1", "ap-south-1"]

# Cache of engines and sessionmakers by region
_region_engines = {}
_region_sessions = {}

def get_region_db_url(region: str) -> str:
    region = region.lower().strip()
    if "sqlite" in DATABASE_URL:
        # e.g., sqlite+aiosqlite:///./catalog.db -> sqlite+aiosqlite:///./catalog_us-west-2.db
        if DATABASE_URL.endswith(".db"):
            prefix = DATABASE_URL[:-3]
            return f"{prefix}_{region}.db"
        return f"{DATABASE_URL}_{region}"
    return DATABASE_URL

def get_engine_for_region(region: str):
    region = region.lower().strip()
    if region not in _region_engines:
        url = get_region_db_url(region)
        _region_engines[region] = create_async_engine(
            url,
            echo=ECHO_SQL,
            future=True,
            connect_args={"check_same_thread": False} if "sqlite" in url else {}
        )
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
