"""
Pydantic schemas for Module 3 — Repository Analyzer Service.
"""
from __future__ import annotations

from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field, SecretStr


class ScanRequest(BaseModel):
    repo_path: str = Field(
        ...,
        description="Absolute path to the repository root directory to scan",
        examples=["/home/user/my-project"],
    )
    include_findings: bool = Field(
        default=False,
        description="Include the full list of individual findings in the response (verbose mode)",
    )


class CoverageOut(BaseModel):
    status: str = "MEASURED"
    files_scanned: Optional[int] = None
    files_skipped: Optional[int] = None
    bytes_read_kb: Optional[float] = None
    detectors_run: list[str] = Field(default_factory=list)
    detectors_failed: list[str] = Field(default_factory=list)
    limits_hit: list[str] = Field(default_factory=list)
    languages_without_framework_rules: list[str] = Field(default_factory=list)
    inspected_manifests: list[str] = Field(default_factory=list)


class ComponentOut(BaseModel):
    path: str
    kind: str
    languages: list[str]
    frameworks: list[str]
    package_managers: list[str]
    ports: list[int]
    start_commands: list[str]
    build_commands: list[str]
    databases: list[str]
    has_container_config: bool


class ScanResponse(BaseModel):
    status: str
    repo_name: str
    repo_path: str
    commit_sha: Optional[str]
    is_monorepo: bool
    components: list[ComponentOut]
    languages_detected: list[str]
    frameworks_detected: list[str]
    databases_detected: list[str]
    ports_detected: list[int]
    unknowns: list[str]
    conflicts: list[str]
    errors: list[str]
    coverage: CoverageOut
    findings_count: int
    findings: Optional[list[dict]] = None   # only when include_findings=True


class DispatchRequest(BaseModel):
    repo_path: str = Field(..., description="Absolute path to the repository root directory")
    project_name: Optional[str] = Field(None, description="Override project name")
    monthly_budget: Optional[float] = Field(None, ge=0.0)
    traffic_scale: Optional[str] = Field(None, description="hobby_dev / growth / production")
    reliability: Optional[str] = Field(None, description="dev_testing / production_safe / mission_critical")
    target_region: str = Field(default="us-east-1")
    module1_url: str = Field(
        default="http://localhost:8004",
        description="Base URL of the Module 1 Requirement Analysis Service",
    )
    auto_save: bool = Field(default=True)


class DispatchResponse(BaseModel):
    status: str
    repo_path: str
    project_id: Optional[str]
    module1_url: str
    scan_result: dict
    parsed_input: dict
    sizing_data: dict


# ─────────────────────────────────────────────────────────────────────────────
# Module 3 Universal Analyzer & User Acceptance Schemas
# ─────────────────────────────────────────────────────────────────────────────

class ReadinessRequest(BaseModel):
    repo_path: str = Field(..., description="Repository path, workspace directory, or GitHub repo URL/slug")
    project_id: Optional[str] = None
    environment_id: Optional[str] = None
    branch: Optional[str] = "main"
    github_token: Optional[SecretStr] = None


class ReadinessResponse(BaseModel):
    is_analyzable: bool
    status: str = "READY"  # READY | NOT_ANALYZABLE | PATH_NOT_FOUND
    message: str
    files_count: int = 0
    detected_manifests: list[str] = Field(default_factory=list)
    detected_extensions: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    is_remote: bool = False
    inspection_mode: str = "LOCAL_FILESYSTEM"  # LOCAL_FILESYSTEM | IN_MEMORY_ZERO_CLONE


class KeyValueReportItem(BaseModel):
    key: str
    label: str
    value: Any
    category: str = "runtime"  # architecture | runtime | database | network | container
    confidence: str = "HIGH"   # HIGH | MEDIUM | LOW
    editable: bool = True
    options: Optional[list[str]] = None


class ScanReportRequest(BaseModel):
    repo_path: str = Field(..., description="Repository path, workspace directory, or GitHub repo URL/slug")
    project_id: Optional[str] = None
    environment_id: Optional[str] = None
    branch: Optional[str] = "main"
    github_token: Optional[SecretStr] = None
    environment_tier: str = Field(default="development", description="development | staging | production")
    target_region: str = Field(default="us-east-1")


class ScanReportResponse(BaseModel):
    status: str = "SUCCESS"
    repo_path: str
    repo_name: str
    environment_tier: str
    target_region: str
    workload_type: str
    key_value_report: list[KeyValueReportItem]
    summary_dict: dict[str, Any]
    languages: list[str]
    frameworks: list[str]
    databases: list[str]
    ports: list[int]
    has_dockerfile: bool
    is_monorepo: bool
    requires_user_acceptance: bool = True
    is_remote: bool = False
    inspection_mode: str = "LOCAL_FILESYSTEM"  # LOCAL_FILESYSTEM | IN_MEMORY_ZERO_CLONE
    repo_metadata: Optional[dict[str, Any]] = None
    commit_sha: Optional[str] = None
    languages_breakdown: Optional[list[dict[str, Any]]] = None
    inspected_manifests: Optional[list[str]] = None
    manifest_count: Optional[int] = None
    manifest_limit: Optional[int] = None
    truncated_manifests: bool = False
    max_manifest_bytes: Optional[int] = None
    skipped_large_manifests: list[str] = Field(default_factory=list)
    profile_completeness: str = "PARTIAL"
    analysis_scope: Optional[str] = None
    accuracy_score: Optional[int] = None
    accuracy_method: Optional[str] = "NOT_CALIBRATED"
    persistence_status: str = "SKIPPED_CONTEXT_REQUIRED"
    analysis_run_id: Optional[str] = None
    repository_id: Optional[str] = None
    revision_id: Optional[str] = None
    revision_identifier: Optional[str] = None
    revision_kind: Optional[str] = None
    snapshot_id: Optional[str] = None
    snapshot_hash: Optional[str] = None
    application_ids: list[str] = Field(default_factory=list)
    findings_persisted: int = 0
    dependencies_detected: list[dict[str, Any]] = Field(default_factory=list)
    dependency_count: int = 0
    dependencies_persisted: int = 0
    sbom_formats: list[str] = Field(default_factory=list)
    sbom_checksums: dict[str, str] = Field(default_factory=dict)

class AcceptAndSizeRequest(BaseModel):
    repo_path: Optional[str] = Field(default="", description="Repository identifier or path")
    project_id: Optional[str] = None
    environment_id: Optional[str] = None
    environment_tier: str = Field(default="development", description="development | staging | production")
    target_region: str = Field(default="us-east-1")
    budget_tier: str = Field(default="STANDARD", description="LOW | STANDARD | ENTERPRISE")
    traffic_scale: str = Field(default="MODERATE", description="LOW | MODERATE | HIGH")
    ha_level: str = Field(default="AUTO", description="AUTO | SINGLE_AZ | MULTI_AZ")
    verified_spec: dict[str, Any] = Field(
        ...,
        description="The Key:Value specification verified and accepted by the user",
    )


class AwsSizingOutput(BaseModel):
    status: str = "SUCCESS"
    environment_tier: str
    target_region: str
    ai_provider: str = "gemini-2.5-flash"
    cached: bool = False
    verified_spec_applied: dict[str, Any]
    recommended_services: list[dict[str, Any]]
    compute: dict[str, Any]
    database: dict[str, Any]
    cache: Optional[dict[str, Any]] = None
    frontend_hosting: Optional[dict[str, Any]] = None
    networking: dict[str, Any]
    monthly_cost_estimate_usd: dict[str, Any]
    finops_optimizations: list[str]
    deployment_readiness: dict[str, Any]
    module4_payload: dict[str, Any]
    compatibility_notes: Optional[list[str]] = Field(default_factory=list)


class RecalculateSizingRequest(BaseModel):
    environment_tier: str = Field(default="development", description="development | staging | production")
    target_region: str = Field(default="us-east-1")
    compute_service: str = Field(default="Amazon EC2 (Docker Runtime)")
    instance_type: str = Field(default="t4g.micro")
    min_capacity: int = Field(default=1, ge=1, le=10)
    max_capacity: int = Field(default=1, ge=1, le=20)
    multi_az: bool = Field(default=False)
    alb_enabled: bool = Field(default=False)
    waf_enabled: bool = Field(default=False)
    database_service: str = Field(default="None")
    cache_service: str = Field(default="None")
    cdn_enabled: bool = Field(default=False)
    verified_spec: Optional[dict[str, Any]] = Field(default_factory=dict)


