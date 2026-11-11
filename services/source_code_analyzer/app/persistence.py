"""Transactional persistence for Module 3 analysis results."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AnalysisFinding, AnalysisRun, AnalysisSnapshot, Application,
    ApplicationProfile, EvidenceRecord, Repository, RepositoryRevision,
    Dependency, SbomDocument,
)
from app.dependency_inventory import build_sbom_documents


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


async def persist_analysis_report(
    session: AsyncSession,
    *,
    report: dict[str, Any],
    target: dict[str, Any],
    project_id: str | None,
    environment_id: str | None,
    tenant_id: str | None,
    branch: str,
) -> dict[str, Any]:
    """Persist one scan atomically; never store credentials or raw source."""
    if not all((project_id, environment_id, tenant_id)):
        return {"persistence_status": "SKIPPED_CONTEXT_REQUIRED"}

    owner = str(target.get("owner") or "local")
    name = str(target.get("repo") or report.get("repo_name") or "workspace")
    provider = "github" if target.get("is_remote") else "local"
    external_id = str(
        target.get("external_repo_id")
        or _canonical_hash({"provider": provider, "owner": owner, "name": name, "path": target.get("path")})
    )
    connection_id = str(target.get("connection_id") or "local-workspace")
    repo_result = await session.execute(
        select(Repository).where(
            Repository.tenant_id == tenant_id,
            Repository.project_id == project_id,
            Repository.environment_id == environment_id,
            Repository.provider == provider,
            Repository.external_repo_id == external_id,
        )
    )
    repository = repo_result.scalar_one_or_none()
    if repository is None:
        repository = Repository(
            project_id=project_id, environment_id=environment_id, tenant_id=tenant_id,
            connection_id=connection_id, provider=provider, external_repo_id=external_id,
            owner=owner, name=name, default_branch=branch,
        )
        session.add(repository)
        await session.flush()
    else:
        repository.connection_id = connection_id
        repository.default_branch = branch

    commit_sha = str(report.get("commit_sha") or target.get("commit_sha") or "")
    revision_kind = "GIT_COMMIT" if commit_sha else "PROFILE_FINGERPRINT"
    if not commit_sha:
        commit_sha = _canonical_hash({"branch": branch, "report": report})
    revision_result = await session.execute(
        select(RepositoryRevision).where(
            RepositoryRevision.repository_id == repository.id,
            RepositoryRevision.commit_sha == commit_sha,
        )
    )
    revision = revision_result.scalar_one_or_none()
    if revision is None:
        revision = RepositoryRevision(
            repository_id=repository.id, branch=branch, commit_sha=commit_sha,
        )
        session.add(revision)
        await session.flush()

    run = AnalysisRun(
        repository_id=repository.id, revision_id=revision.id, status="RUNNING",
        analyzer_version="1.0.0", analysis_mode="MANIFESTS_AND_CONFIG",
        coverage=report.get("coverage") or {
            "profile_completeness": report.get("profile_completeness", "PARTIAL"),
            "analysis_scope": report.get("analysis_scope"),
            "inspected_manifests": report.get("inspected_manifests") or [],
            "manifest_count": report.get("manifest_count"),
            "manifest_limit": report.get("manifest_limit"),
            "truncated_manifests": report.get("truncated_manifests", False),
        },
    )
    from app.models import utc_now
    run.started_at = utc_now()
    run.coverage = {**(run.coverage or {}), "revision_kind": revision_kind}
    session.add(run)
    await session.flush()

    snapshot_hash = _canonical_hash({
        "commit_sha": commit_sha,
        "analyzer_version": run.analyzer_version,
        "report": report,
    })
    snapshot_result = await session.execute(
        select(AnalysisSnapshot).where(
            AnalysisSnapshot.revision_id == revision.id,
            AnalysisSnapshot.snapshot_hash == snapshot_hash,
        )
    )
    snapshot = snapshot_result.scalar_one_or_none()
    if snapshot is None:
        snapshot = AnalysisSnapshot(
            repository_id=repository.id, revision_id=revision.id, run_id=run.id,
            analyzer_version=run.analyzer_version, snapshot_hash=snapshot_hash,
            profile_version="1",
        )
        session.add(snapshot)
        await session.flush()

    component_items = report.get("components") or []
    roots = report.get("application_roots") or [
        str(item.get("path") or ".") for item in component_items if isinstance(item, dict)
    ]
    roots = list(dict.fromkeys(str(root or ".").strip("/") or "." for root in roots)) or ["."]
    applications: list[Application] = []
    for root_path in roots:
        app_result = await session.execute(
            select(Application).where(
                Application.repository_id == repository.id,
                Application.revision_id == revision.id,
                Application.root_path == root_path,
            )
        )
        application = app_result.scalar_one_or_none()
        if application is None:
            application = Application(
                repository_id=repository.id, revision_id=revision.id,
                name=name if root_path == "." else root_path.rstrip("/").split("/")[-1],
                root_path=root_path, application_type=str(report.get("workload_type") or "UNKNOWN"),
                discovery_status="OBSERVED_MANIFEST_ROOT" if root_path != "." else "INFERRED",
            )
            session.add(application)
            await session.flush()
        applications.append(application)

    profile_base = {
        "repo_name": report.get("repo_name"),
        "commit_sha": report.get("commit_sha"),
        "status": report.get("status"),
        "profile_completeness": report.get("profile_completeness", "PARTIAL"),
        "analysis_scope": report.get("analysis_scope"),
        "languages": report.get("languages") or [],
        "frameworks": report.get("frameworks") or [],
        "databases": report.get("databases") or [],
        "ports": report.get("ports") or [],
        "is_monorepo": bool(report.get("is_monorepo")),
        "application_roots": roots,
        "components": component_items,
        "summary": report.get("summary_dict") or {},
        "coverage": report.get("coverage") or {},
        "inspected_manifests": report.get("inspected_manifests") or [],
        "dependency_completeness": "DECLARED_DIRECT_DEPENDENCIES_ONLY",
    }
    for application in applications:
        application_profile = {
            **profile_base,
            "application_root": application.root_path,
        }
        session.add(ApplicationProfile(
            application_id=application.id, run_id=run.id, snapshot_id=snapshot.id,
            profile_version=run.id, profile=application_profile,
        ))

    # Persist direct dependencies against the application root containing each manifest.
    dependencies = report.get("dependencies_detected") or []
    unique_dependencies: dict[tuple[str, str, str | None, str], dict[str, Any]] = {}
    for dependency in dependencies:
        if not isinstance(dependency, dict):
            continue
        key = (
            str(dependency.get("ecosystem") or "unknown"),
            str(dependency.get("package_name") or ""),
            dependency.get("version"),
            str(dependency.get("source_path") or ""),
        )
        if key[1] and key[3]:
            unique_dependencies[key] = dependency

    dependencies_by_application: dict[str, list[dict[str, Any]]] = {
        application.id: [] for application in applications
    }
    for dependency in unique_dependencies.values():
        source_path = str(dependency["source_path"]).lstrip("./")
        candidates = [
            application for application in applications
            if application.root_path == "."
            or source_path == application.root_path
            or source_path.startswith(application.root_path.rstrip("/") + "/")
        ]
        if candidates:
            selected = max(candidates, key=lambda item: len(item.root_path))
            dependencies_by_application[selected.id].append(dependency)

    sbom_checksums: dict[str, str] = {}
    for application in applications:
        existing_dependencies = await session.execute(
            select(Dependency).where(Dependency.application_id == application.id)
        )
        for existing in existing_dependencies.scalars().all():
            await session.delete(existing)
        await session.flush()

        app_dependencies = dependencies_by_application[application.id]
        for dependency in app_dependencies:
            session.add(Dependency(
                application_id=application.id,
                ecosystem=str(dependency.get("ecosystem") or "unknown"),
                package_name=str(dependency["package_name"]),
                version=dependency.get("version"),
                purl=dependency.get("purl"),
                is_direct=True,
                source_path=str(dependency["source_path"]),
                manifest_hash=dependency.get("manifest_hash"),
            ))

        sbom_documents = build_sbom_documents(
            application_name=application.name,
            repository_url=str(report.get("repo_path") or f"{provider}:{owner}/{name}"),
            commit_sha=commit_sha if revision_kind == "GIT_COMMIT" else None,
            dependencies=app_dependencies,
        )
        for sbom_format, document in sbom_documents.items():
            checksum = _canonical_hash(document)
            sbom_checksums[f"{application.root_path}:{sbom_format}"] = checksum
            session.add(SbomDocument(
                run_id=run.id,
                application_id=application.id,
                format=sbom_format,
                format_version="1.5" if sbom_format == "CYCLONEDX" else "SPDX-2.3",
                checksum=checksum,
                document=document,
            ))

    findings: list[tuple[str, str, Any]] = []
    for category, values in (
        ("LANGUAGE", report.get("languages") or []),
        ("FRAMEWORK", report.get("frameworks") or []),
        ("DATABASE", report.get("databases") or []),
        ("PORT", report.get("ports") or []),
    ):
        for value in values:
            findings.append((category, str(value), {"detected_value": value}))
    for category, subject, value in findings:
        finding = AnalysisFinding(
            run_id=run.id, application_id=applications[0].id,
            category=category, subject=subject, value=value,
            verification_status="INFERRED", confidence="MEDIUM",
            detector="deterministic_manifest_scanner",
        )
        session.add(finding)
        await session.flush()

    # Manifest evidence is recorded as its own finding so it is not falsely
    # attributed to every language/framework/database result.
    for source_path in report.get("inspected_manifests") or []:
        manifest_finding = AnalysisFinding(
            run_id=run.id, application_id=next((
                app.id for app in sorted(applications, key=lambda item: len(item.root_path), reverse=True)
                if app.root_path == "." or str(source_path).lstrip("./").startswith(app.root_path.rstrip("/") + "/")
            ), applications[0].id),
            category="MANIFEST_INSPECTED", subject=str(source_path),
            value={"path": str(source_path)}, verification_status="OBSERVED",
            confidence="HIGH", detector="manifest_inventory",
        )
        session.add(manifest_finding)
        await session.flush()
        session.add(EvidenceRecord(
            finding_id=manifest_finding.id, source_path=str(source_path),
            evidence_type="MANIFEST",
        ))

    run.status = "PARTIAL" if report.get("profile_completeness", "PARTIAL") == "PARTIAL" else "SUCCEEDED"
    run.completed_at = utc_now()
    await session.flush()
    return {
        "persistence_status": "PERSISTED",
        "analysis_run_id": run.id,
        "repository_id": repository.id,
        "revision_id": revision.id,
        "revision_identifier": revision.commit_sha,
        "revision_kind": revision_kind,
        "snapshot_id": snapshot.id,
        "snapshot_hash": snapshot_hash,
        "application_ids": [item.id for item in applications],
        "findings_persisted": len(findings),
        "dependencies_persisted": len(unique_dependencies),
        "sbom_formats": ["CYCLONEDX", "SPDX"],
        "sbom_checksums": sbom_checksums,
    }
