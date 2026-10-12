"""
Pydantic schemas for Module 3 — Repository Analyzer Service.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


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
    files_scanned: int
    files_skipped: int
    bytes_read_kb: float
    detectors_run: list[str]
    detectors_failed: list[str]
    limits_hit: list[str]
    languages_without_framework_rules: list[str]


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
        default="http://localhost:8001",
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
