from __future__ import annotations

import builtins

import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

from app.models import Base


@pytest.mark.anyio
async def test_source_analysis_metadata_creates_expected_tables():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    expected = {
        "sa_repositories",
        "sa_repository_revisions",
        "sa_analysis_runs",
        "sa_analysis_snapshots",
        "sa_applications",
        "sa_analysis_findings",
        "sa_evidence_records",
        "sa_dependencies",
        "sa_sbom_documents",
        "sa_application_profiles",
    }
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
            actual = await connection.run_sync(
                lambda sync_connection: set(inspect(sync_connection).get_table_names())
            )
        assert expected.issubset(actual)
    finally:
        await engine.dispose()


def test_repository_revision_and_finding_evidence_have_real_foreign_keys():
    revision = Base.metadata.tables["sa_repository_revisions"]
    evidence = Base.metadata.tables["sa_evidence_records"]

    assert any(fk.target_fullname == "sa_repositories.id" for fk in revision.foreign_keys)
    assert any(fk.target_fullname == "sa_analysis_findings.id" for fk in evidence.foreign_keys)
