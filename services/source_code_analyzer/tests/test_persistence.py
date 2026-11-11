from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import (
    AnalysisFinding, AnalysisRun, AnalysisSnapshot, Application,
    ApplicationProfile, Base, EvidenceRecord, Repository, RepositoryRevision,
    Dependency, SbomDocument,
)
from app.persistence import persist_analysis_report


@pytest.mark.anyio
async def test_scan_report_is_persisted_as_revision_snapshot_and_profile():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        report = {
            "repo_name": "sample-app",
            "commit_sha": "a" * 40,
            "status": "PARTIAL",
            "profile_completeness": "PARTIAL",
            "analysis_scope": "MANIFESTS_AND_CONFIG",
            "languages": ["Python"],
            "frameworks": ["FastAPI"],
            "databases": ["PostgreSQL"],
            "ports": [8000],
            "is_monorepo": True,
            "application_roots": ["apps/api", "apps/web"],
            "inspected_manifests": ["apps/api/pyproject.toml", "apps/web/package.json"],
            "manifest_count": 1,
            "manifest_limit": 100,
            "truncated_manifests": False,
            "summary_dict": {"workload_type": "Backend REST API"},
            "repo_path": "https://github.com/example/sample-app",
            "dependencies_detected": [
                {"ecosystem": "pypi", "package_name": "fastapi", "version": "0.115.0", "purl": "pkg:pypi/fastapi@0.115.0", "source_path": "apps/api/pyproject.toml", "manifest_hash": "b" * 64, "is_direct": True, "scope": "required"},
                {"ecosystem": "npm", "package_name": "react", "version": "18.2.0", "purl": "pkg:npm/react@18.2.0", "source_path": "apps/web/package.json", "manifest_hash": "c" * 64, "is_direct": True, "scope": "required"}
            ],
        }
        target = {
            "is_remote": True,
            "owner": "example",
            "repo": "sample-app",
            "connection_id": "connection-1",
            "external_repo_id": "repo-123",
        }
        async with sessions() as session:
            result = await persist_analysis_report(
                session,
                report=report,
                target=target,
                project_id="project-1",
                environment_id="environment-1",
                tenant_id="tenant-1",
                branch="main",
            )
            await session.commit()
            assert result["persistence_status"] == "PERSISTED"
            assert result["analysis_run_id"]
            assert result["snapshot_hash"]
            assert result["revision_kind"] == "GIT_COMMIT"
            assert result["revision_identifier"] == "a" * 40
            assert result["findings_persisted"] == 4
            assert result["dependencies_persisted"] == 2
            assert set(result["sbom_formats"]) == {"CYCLONEDX", "SPDX"}
            dependencies = (await session.execute(select(Dependency))).scalars().all()
            assert len(dependencies) == 2
            assert {item.application_id for item in dependencies} == {app.id for app in apps}
            sboms = (await session.execute(select(SbomDocument))).scalars().all()
            assert len(sboms) == 4
            assert {item.format for item in sboms} == {"CYCLONEDX", "SPDX"}

            assert len((await session.execute(select(Repository))).scalars().all()) == 1
            assert len((await session.execute(select(RepositoryRevision))).scalars().all()) == 1
            runs = (await session.execute(select(AnalysisRun))).scalars().all()
            assert len(runs) == 1
            assert runs[0].status == "PARTIAL"
            assert len((await session.execute(select(AnalysisSnapshot))).scalars().all()) == 1
            apps = (await session.execute(select(Application))).scalars().all()
            assert len(apps) == 2
            assert {app.root_path for app in apps} == {"apps/api", "apps/web"}
            assert len((await session.execute(select(ApplicationProfile))).scalars().all()) == 2
            assert len((await session.execute(select(AnalysisFinding))).scalars().all()) == 5
            assert len((await session.execute(select(EvidenceRecord))).scalars().all()) == 1
    finally:
        await engine.dispose()


@pytest.mark.anyio
async def test_scan_report_does_not_persist_without_tenant_scope():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        async with sessions() as session:
            result = await persist_analysis_report(
                session,
                report={"repo_name": "sample-app"},
                target={"is_remote": False, "path": "/tmp/sample-app"},
                project_id="project-1",
                environment_id="environment-1",
                tenant_id=None,
                branch="local",
            )
            assert result == {"persistence_status": "SKIPPED_CONTEXT_REQUIRED"}
            assert len((await session.execute(select(AnalysisRun))).scalars().all()) == 0
    finally:
        await engine.dispose()
