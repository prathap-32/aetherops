"""
Bootstrap script to create all 19 canonical schemas in the single AetherOps PostgreSQL database (`aetherops_platform`).
"""
import asyncio
import argparse
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("aether-schema-bootstrap")

CANONICAL_SCHEMAS = [
    "identity",
    "organizations",
    "project_management",
    "source_connections",
    "cloud_connections",
    "source_analysis",
    "architecture",
    "requirements",
    "risk_assessment",
    "architecture_validation",
    "iac_artifacts",
    "infrastructure_execution",
    "deployment",
    "cicd",
    "monitoring",
    "optimization",
    "audit_history",
    "documentation_evidence",
    "ai_platform",
]

async def bootstrap_schemas(db_url: str):
    logger.info(f"Connecting to database to bootstrap 19 canonical schemas...")
    engine = create_async_engine(db_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        for schema in CANONICAL_SCHEMAS:
            logger.info(f"Creating schema if not exists: '{schema}'")
            await session.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}";'))
        await session.commit()

    await engine.dispose()
    logger.info("Successfully bootstrapped all 19 canonical schemas in aetherops_platform.")

def main():
    parser = argparse.ArgumentParser(description="Bootstrap 19 Canonical Schemas for AetherOps")
    parser.add_argument("--db-url", required=True, help="PostgreSQL database URL")
    args = parser.parse_args()

    asyncio.run(bootstrap_schemas(args.db_url))

if __name__ == "__main__":
    main()
