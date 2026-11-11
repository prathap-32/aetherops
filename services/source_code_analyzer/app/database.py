"""Database configuration for the Module 3-owned source_analysis schema."""
from __future__ import annotations

import os
import sys
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import Base

IS_TESTING = "pytest" in sys.modules or any("pytest" in arg for arg in sys.argv)
ENVIRONMENT = os.getenv("AETHER_ENV", os.getenv("ENVIRONMENT", "development")).lower()


def _database_url() -> str:
    configured = os.getenv("SOURCE_ANALYSIS_DATABASE_URL")
    if configured:
        return configured.replace("postgresql://", "postgresql+asyncpg://", 1).replace(
            "postgres://", "postgresql+asyncpg://", 1
        )
    if IS_TESTING:
        return "sqlite+aiosqlite:///./test_source_analysis.db"
    if ENVIRONMENT == "production":
        raise RuntimeError("SOURCE_ANALYSIS_DATABASE_URL must be configured in production.")
    return "sqlite+aiosqlite:///./source_analysis.db"


DATABASE_URL = _database_url()
_connect_args = {}
if DATABASE_URL.startswith("postgresql"):
    _connect_args = {
        "server_settings": {"search_path": "source_analysis,public"},
        "command_timeout": 15,
    }
elif DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=_connect_args,
)
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_analysis_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def dispose_analysis_db() -> None:
    await engine.dispose()
