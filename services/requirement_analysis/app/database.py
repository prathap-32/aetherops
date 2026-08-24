# services/requirement_analysis/app/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

# Default to local SQLite fallback if DATABASE_URL is not set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./catalog.db")

# Echo SQL queries in development/debug modes
ECHO_SQL = os.getenv("ECHO_SQL", "False").lower() in ("true", "1", "yes")

# Configure the async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=ECHO_SQL,
    future=True,
    # SQLite requires some special pool configurations
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

async def get_db_session() -> AsyncSession:
    """
    Dependency helper to yield an async database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
