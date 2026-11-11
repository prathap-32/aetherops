"""Persistence models owned exclusively by the Module 3 source-analysis service.

Module 2 remains the authority for Git credentials and connection lifecycle.
This schema stores only repository references and analysis-derived records.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def new_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Repository(Base):
    __tablename__ = "sa_repositories"
    __table_args__ = (
        UniqueConstraint("provider", "external_repo_id", name="uq_sa_repository_provider_external"),
        Index("ix_sa_repositories_project_environment", "project_id", "environment_id"),
        Index("ix_sa_repositories_tenant", "tenant_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False)
    environment_id: Mapped[str] = mapped_column(String(36), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    connection_id: Mapped[str] = mapped_column(String(36), nullable=False)
    provider: Mapped[str] = mapped_column(String(24), nullable=False, default="github")
    external_repo_id: Mapped[str] = mapped_column(String(128), nullable=False)
    owner: Mapped[str] = mapped_column(String(200), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    default_branch: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class RepositoryRevision(Base):
    __tablename__ = "sa_repository_revisions"
    __table_args__ = (
        UniqueConstraint("repository_id", "commit_sha", name="uq_sa_revision_repository_commit"),
        Index("ix_sa_revisions_repository_branch", "repository_id", "branch"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    repository_id: Mapped[str] = mapped_column(ForeignKey("sa_repositories.id", ondelete="CASCADE"), nullable=False)
    branch: Mapped[str] = mapped_column(String(255), nullable=False)
    commit_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    committed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class AnalysisRun(Base):
    __tablename__ = "sa_analysis_runs"
    __table_args__ = (
        Index("ix_sa_runs_repository_status", "repository_id", "status"),
        Index("ix_sa_runs_started_at", "started_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    repository_id: Mapped[str] = mapped_column(ForeignKey("sa_repositories.id", ondelete="CASCADE"), nullable=False)
    revision_id: Mapped[str] = mapped_column(ForeignKey("sa_repository_revisions.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="QUEUED")
    analyzer_version: Mapped[str] = mapped_column(String(64), nullable=False, default="0.1.0")
    analysis_mode: Mapped[str] = mapped_column(String(24), nullable=False, default="FULL")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_code: Mapped[str | None] = mapped_column(String(80))
    coverage: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class AnalysisSnapshot(Base):
    __tablename__ = "sa_analysis_snapshots"
    __table_args__ = (
        UniqueConstraint("revision_id", "snapshot_hash", name="uq_sa_snapshot_revision_hash"),
        Index("ix_sa_snapshots_repository_created", "repository_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    repository_id: Mapped[str] = mapped_column(ForeignKey("sa_repositories.id", ondelete="CASCADE"), nullable=False)
    revision_id: Mapped[str] = mapped_column(ForeignKey("sa_repository_revisions.id", ondelete="RESTRICT"), nullable=False)
    run_id: Mapped[str] = mapped_column(ForeignKey("sa_analysis_runs.id", ondelete="RESTRICT"), nullable=False)
    analyzer_version: Mapped[str] = mapped_column(String(64), nullable=False)
    snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    profile_version: Mapped[str] = mapped_column(String(32), nullable=False, default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Application(Base):
    __tablename__ = "sa_applications"
    __table_args__ = (
        UniqueConstraint("repository_id", "revision_id", "root_path", name="uq_sa_application_revision_root"),
        Index("ix_sa_applications_repository", "repository_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    repository_id: Mapped[str] = mapped_column(ForeignKey("sa_repositories.id", ondelete="CASCADE"), nullable=False)
    revision_id: Mapped[str] = mapped_column(ForeignKey("sa_repository_revisions.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    root_path: Mapped[str] = mapped_column(String(1024), nullable=False, default=".")
    application_type: Mapped[str] = mapped_column(String(40), nullable=False, default="UNKNOWN")
    discovery_status: Mapped[str] = mapped_column(String(24), nullable=False, default="INFERRED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class AnalysisFinding(Base):
    __tablename__ = "sa_analysis_findings"
    __table_args__ = (
        Index("ix_sa_findings_run_category", "run_id", "category"),
        Index("ix_sa_findings_application", "application_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    run_id: Mapped[str] = mapped_column(ForeignKey("sa_analysis_runs.id", ondelete="CASCADE"), nullable=False)
    application_id: Mapped[str | None] = mapped_column(ForeignKey("sa_applications.id", ondelete="SET NULL"))
    category: Mapped[str] = mapped_column(String(48), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    verification_status: Mapped[str] = mapped_column(String(24), nullable=False, default="INFERRED")
    confidence: Mapped[str] = mapped_column(String(16), nullable=False, default="MEDIUM")
    detector: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class EvidenceRecord(Base):
    __tablename__ = "sa_evidence_records"
    __table_args__ = (Index("ix_sa_evidence_finding", "finding_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    finding_id: Mapped[str] = mapped_column(ForeignKey("sa_analysis_findings.id", ondelete="CASCADE"), nullable=False)
    source_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    line_start: Mapped[int | None] = mapped_column(Integer)
    line_end: Mapped[int | None] = mapped_column(Integer)
    content_hash: Mapped[str | None] = mapped_column(String(64))
    excerpt_redacted: Mapped[str | None] = mapped_column(Text)
    evidence_type: Mapped[str] = mapped_column(String(32), nullable=False, default="STATIC")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Dependency(Base):
    __tablename__ = "sa_dependencies"
    __table_args__ = (
        Index("ix_sa_dependencies_application_ecosystem", "application_id", "ecosystem"),
        Index("ix_sa_dependencies_purl", "purl"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    application_id: Mapped[str] = mapped_column(ForeignKey("sa_applications.id", ondelete="CASCADE"), nullable=False)
    ecosystem: Mapped[str] = mapped_column(String(40), nullable=False)
    package_name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str | None] = mapped_column(String(128))
    purl: Mapped[str | None] = mapped_column(String(1024))
    is_direct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    source_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    manifest_hash: Mapped[str | None] = mapped_column(String(64))


class SbomDocument(Base):
    __tablename__ = "sa_sbom_documents"
    __table_args__ = (
        UniqueConstraint("run_id", "application_id", "format", name="uq_sa_sbom_run_application_format"),
        Index("ix_sa_sbom_checksum", "checksum"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    run_id: Mapped[str] = mapped_column(ForeignKey("sa_analysis_runs.id", ondelete="CASCADE"), nullable=False)
    application_id: Mapped[str] = mapped_column(ForeignKey("sa_applications.id", ondelete="CASCADE"), nullable=False)
    format: Mapped[str] = mapped_column(String(16), nullable=False)
    format_version: Mapped[str] = mapped_column(String(32), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    document: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class ApplicationProfile(Base):
    __tablename__ = "sa_application_profiles"
    __table_args__ = (
        UniqueConstraint("application_id", "profile_version", name="uq_sa_profile_application_version"),
        Index("ix_sa_profiles_run", "run_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    application_id: Mapped[str] = mapped_column(ForeignKey("sa_applications.id", ondelete="CASCADE"), nullable=False)
    run_id: Mapped[str] = mapped_column(ForeignKey("sa_analysis_runs.id", ondelete="RESTRICT"), nullable=False)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("sa_analysis_snapshots.id", ondelete="RESTRICT"), nullable=False)
    profile_version: Mapped[str] = mapped_column(String(32), nullable=False)
    profile: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
