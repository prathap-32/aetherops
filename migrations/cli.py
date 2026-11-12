"""
Command-line interface to run and inspect AetherOps database migrations.
Supports both PostgreSQL and SQLite, with disposable test database verification.
"""
import argparse
import asyncio
import sys
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from migrations.runner import ensure_migration_table, get_applied_versions, record_migration, remove_migration
import migrations.versions.v20261012_01_user_uuid_and_tenants as m_01
import migrations.versions.v20261027_02_crypto_envelope as m_02
import migrations.versions.v20261111_03_source_analysis_schema as m_03

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("aether-migrations")

MIGRATIONS_BY_TARGET = {
    "project_management": [m_01],
    "source_connections": [m_01, m_02],
    "source_analysis": [m_03],
}


async def run_migrations(db_url: str, target_schema: str = "all", direction: str = "upgrade"):
    """
    Apply or rollback migrations against a specified database URL.
    """
    dialect = "postgresql" if "postgres" in db_url else "sqlite"
    engine = create_async_engine(db_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    targets = list(MIGRATIONS_BY_TARGET) if target_schema == "all" else [target_schema]

    async with session_factory() as session:
        for target in targets:
            logger.info(f"--- Processing Target: {target} ({dialect}) ---")
            await ensure_migration_table(session, dialect, schema=target)
            applied = await get_applied_versions(session, dialect, schema=target)
            logger.info(f"Currently applied versions in '{target}': {applied}")

            target_migrations = MIGRATIONS_BY_TARGET[target]
            if direction == "upgrade":
                for m in target_migrations:
                    if m.REVISION not in applied:
                        logger.info(f"Applying migration {m.REVISION}: {m.NAME}...")
                        await m.upgrade(session, dialect, target=target)
                        await record_migration(session, m.REVISION, m.NAME, m.DESCRIPTION, dialect, schema=target)
                        logger.info(f"Migration {m.REVISION} successfully applied to {target}.")
                    else:
                        logger.info(f"Migration {m.REVISION} already applied to {target}. Skipping.")
            elif direction == "downgrade":
                for m in reversed(target_migrations):
                    if m.REVISION in applied:
                        logger.info(f"Reverting migration {m.REVISION}: {m.NAME}...")
                        await m.downgrade(session, dialect, target=target)
                        await remove_migration(session, m.REVISION, dialect, schema=target)
                        logger.info(f"Migration {m.REVISION} successfully rolled back from {target}.")

    await engine.dispose()
    logger.info("All migration operations finished.")


def main():
    parser = argparse.ArgumentParser(description="AetherOps Database Migration CLI")
    parser.add_argument("--db-url", required=True, help="Database connection URL")
    parser.add_argument("--target", default="all", choices=["all", "project_management", "source_connections", "source_analysis"], help="Target schema/module")
    parser.add_argument("--action", default="upgrade", choices=["upgrade", "downgrade"], help="Migration action")
    args = parser.parse_args()

    asyncio.run(run_migrations(args.db_url, target_schema=args.target, direction=args.action))


if __name__ == "__main__":
    main()
