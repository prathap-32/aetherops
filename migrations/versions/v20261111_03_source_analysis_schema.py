"""Create Module 3's isolated source-analysis persistence schema."""
from __future__ import annotations
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("migration-source-analysis")
REVISION = "20261111_03"
NAME = "source_analysis_schema"
DESCRIPTION = "Create Module 3 source-analysis persistence tables."


async def upgrade(session: AsyncSession, dialect: str, target: str = "source_analysis") -> None:
    if target != "source_analysis":
        return
    from services.source_code_analyzer.app.models import Base
    if dialect == "postgresql":
        await session.execute(text('CREATE SCHEMA IF NOT EXISTS "source_analysis"'))
        await session.execute(text('SET search_path TO "source_analysis", public'))
    connection = await session.connection()
    await connection.run_sync(Base.metadata.create_all)
    if dialect == "postgresql":
        await session.execute(text("""
            CREATE OR REPLACE FUNCTION source_analysis.reject_analysis_snapshot_mutation()
            RETURNS trigger
            LANGUAGE plpgsql
            AS $function$
            BEGIN
                RAISE EXCEPTION 'Analysis snapshots are immutable; create a new snapshot instead.';
            END;
            $function$
        """))
        await session.execute(text('DROP TRIGGER IF EXISTS trg_sa_analysis_snapshots_immutable ON source_analysis.sa_analysis_snapshots'))
        await session.execute(text("""
            CREATE TRIGGER trg_sa_analysis_snapshots_immutable
            BEFORE UPDATE OR DELETE ON source_analysis.sa_analysis_snapshots
            FOR EACH ROW EXECUTE FUNCTION source_analysis.reject_analysis_snapshot_mutation()
        """))
    await session.commit()
    logger.info("Applied %s to %s", REVISION, target)


async def downgrade(session: AsyncSession, dialect: str, target: str = "source_analysis") -> None:
    if target != "source_analysis":
        return
    from services.source_code_analyzer.app.models import Base
    if dialect == "postgresql":
        await session.execute(text('DROP TRIGGER IF EXISTS trg_sa_analysis_snapshots_immutable ON source_analysis.sa_analysis_snapshots'))
        await session.execute(text('DROP FUNCTION IF EXISTS source_analysis.reject_analysis_snapshot_mutation()'))
        await session.execute(text('SET search_path TO "source_analysis", public'))
    connection = await session.connection()
    await connection.run_sync(Base.metadata.drop_all)
    await session.commit()
    logger.info("Reverted %s from %s", REVISION, target)
