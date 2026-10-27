"""
Migration 20261027_02_crypto_envelope
Adds AES-256-GCM envelope encryption columns to sc_cloud_connections and sc_git_connections.

Target:
- Source Connection Schema (`source_connection` in PostgreSQL, or local SQLite)
"""
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("migration-02")

REVISION = "20261027_02"
NAME = "crypto_envelope"
DESCRIPTION = "Add AES-256-GCM encryption envelope fields to cloud and git connections"


async def upgrade(session: AsyncSession, dialect: str, target: str = "source_connection"):
    if target != "source_connection" and target != "all":
        return

    logger.info(f"Running migration {REVISION} upgrade on target '{target}' ({dialect})")

    cloud_table = '"source_connection".sc_cloud_connections' if dialect == "postgresql" else "sc_cloud_connections"
    git_table = '"source_connection".sc_git_connections' if dialect == "postgresql" else "sc_git_connections"

    # Add columns to sc_cloud_connections
    cloud_cols = [
        ("encrypted_secret", "TEXT"),
        ("encryption_nonce", "VARCHAR(64)"),
        ("encryption_tag", "VARCHAR(64)"),
        ("encryption_key_id", "VARCHAR(64)"),
    ]
    for col_name, col_type in cloud_cols:
        try:
            await session.execute(text(f"ALTER TABLE {cloud_table} ADD COLUMN {col_name} {col_type};"))
            await session.commit()
            logger.info(f"Added column {col_name} to {cloud_table}")
        except Exception as e:
            await session.rollback()
            logger.debug(f"Column {col_name} already exists or error on {cloud_table}: {e}")

    # Add columns to sc_git_connections
    git_cols = [
        ("encrypted_pat", "TEXT"),
        ("pat_nonce", "VARCHAR(64)"),
        ("pat_tag", "VARCHAR(64)"),
    ]
    for col_name, col_type in git_cols:
        try:
            await session.execute(text(f"ALTER TABLE {git_table} ADD COLUMN {col_name} {col_type};"))
            await session.commit()
            logger.info(f"Added column {col_name} to {git_table}")
        except Exception as e:
            await session.rollback()
            logger.debug(f"Column {col_name} already exists or error on {git_table}: {e}")


async def downgrade(session: AsyncSession, dialect: str, target: str = "source_connection"):
    if target != "source_connection" and target != "all":
        return

    logger.info(f"Running migration {REVISION} downgrade on target '{target}' ({dialect})")
    if dialect == "postgresql":
        cloud_table = '"source_connection".sc_cloud_connections'
        git_table = '"source_connection".sc_git_connections'
        for col_name in ["encrypted_secret", "encryption_nonce", "encryption_tag", "encryption_key_id"]:
            try:
                await session.execute(text(f"ALTER TABLE {cloud_table} DROP COLUMN IF EXISTS {col_name};"))
                await session.commit()
            except Exception:
                await session.rollback()
        for col_name in ["encrypted_pat", "pat_nonce", "pat_tag"]:
            try:
                await session.execute(text(f"ALTER TABLE {git_table} DROP COLUMN IF EXISTS {col_name};"))
                await session.commit()
            except Exception:
                await session.rollback()
