"""
AetherOps Migration Engine
Provides reproducible, reversible, transactional migration execution for both PostgreSQL and SQLite.
Manages schema migration version tracking table: `_aether_schema_migrations`.
"""
import os
import sys
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

logger = logging.getLogger("aether-migration-runner")

SCHEMA_TABLE_NAME = "_aether_schema_migrations"


async def ensure_migration_table(session: AsyncSession, dialect: str, schema: Optional[str] = None):
    """Ensure the schema migration tracking table exists."""
    tbl_name = f'"{schema}"."{SCHEMA_TABLE_NAME}"' if (dialect == "postgresql" and schema) else f'"{SCHEMA_TABLE_NAME}"'
    
    if dialect == "postgresql" and schema:
        await session.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}";'))
    
    ddl = f"""
    CREATE TABLE IF NOT EXISTS {tbl_name} (
        version VARCHAR(64) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        applied_at TIMESTAMP NOT NULL,
        description VARCHAR(500)
    );
    """
    await session.execute(text(ddl))
    await session.commit()


async def get_applied_versions(session: AsyncSession, dialect: str, schema: Optional[str] = None) -> List[str]:
    """Retrieve all applied migration versions."""
    tbl_name = f'"{schema}"."{SCHEMA_TABLE_NAME}"' if (dialect == "postgresql" and schema) else f'"{SCHEMA_TABLE_NAME}"'
    try:
        res = await session.execute(text(f"SELECT version FROM {tbl_name} ORDER BY applied_at ASC;"))
        return [row[0] for row in res.fetchall()]
    except Exception:
        return []


async def record_migration(session: AsyncSession, version: str, name: str, description: str, dialect: str, schema: Optional[str] = None):
    """Record an applied migration."""
    tbl_name = f'"{schema}"."{SCHEMA_TABLE_NAME}"' if (dialect == "postgresql" and schema) else f'"{SCHEMA_TABLE_NAME}"'
    stmt = text(f"""
    INSERT INTO {tbl_name} (version, name, applied_at, description)
    VALUES (:version, :name, :applied_at, :description);
    """)
    await session.execute(stmt, {
        "version": version,
        "name": name,
        "applied_at": datetime.utcnow(),
        "description": description,
    })
    await session.commit()


async def remove_migration(session: AsyncSession, version: str, dialect: str, schema: Optional[str] = None):
    """Remove a migration record on downgrade."""
    tbl_name = f'"{schema}"."{SCHEMA_TABLE_NAME}"' if (dialect == "postgresql" and schema) else f'"{SCHEMA_TABLE_NAME}"'
    stmt = text(f"DELETE FROM {tbl_name} WHERE version = :version;")
    await session.execute(stmt, {"version": version})
    await session.commit()
