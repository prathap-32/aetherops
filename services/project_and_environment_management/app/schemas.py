# services/project_and_environment_management/app/schemas.py
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, field_validator

# ── Valid choices ─────────────────────────────────────────────────────────────

PROJECT_TYPES = {
    "web_application",
    "api_service",
    "microservices",
    "data_pipeline",
    "serverless_backend",
    "event_driven_pipeline",
    "data_lakehouse",
    "ml_workload",
    "ml_inference_pipeline",
    "iot_ingestion",
    "mobile_backend",
    "containerized_workload",
    "static_site",
    "fintech_ledger",
    "edge_computing",
    "internal_tool",
}

ENV_TYPES = {
    "development",
    "staging",
    "production",
    "testing",
    "qa",
    "disaster_recovery",
    "dr",
    "sandbox",
    "preview",
}

# All 39 supported AWS regions (mirrors requirement_analysis)
AWS_REGIONS = {
    "us-east-1", "us-east-2", "us-west-1", "us-west-2",
    "ca-central-1", "ca-west-1", "mx-central-1",
    "us-gov-east-1", "us-gov-west-1",
    "sa-east-1",
    "eu-west-1", "eu-west-2", "eu-west-3",
    "eu-central-1", "eu-central-2",
    "eu-north-1", "eu-south-1", "eu-south-2",
    "ap-south-1", "ap-south-2",
    "ap-southeast-1", "ap-southeast-2", "ap-southeast-3",
    "ap-southeast-4", "ap-southeast-5", "ap-southeast-6", "ap-southeast-7",
    "ap-east-1", "ap-east-2",
    "ap-northeast-1", "ap-northeast-2", "ap-northeast-3",
    "me-south-1", "me-central-1", "me-central-2", "il-central-1",
    "af-south-1",
    "cn-north-1", "cn-northwest-1",
}

VALID_ENV_STATUSES = {
    "CREATED", "CONFIGURED", "REPOSITORY_CONNECTED", "ANALYZED",
    "ARCHITECTURE_READY", "VALIDATED", "READY_TO_DEPLOY",
    "DEPLOYING", "ACTIVE", "FAILED",
}

VALID_PROJECT_STATUSES = {"CREATED", "ACTIVE", "ARCHIVED"}


# ── Input Schemas ─────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    name:                         str
    description:                  Optional[str] = None
    project_type:                 str
    account_id:                   Optional[str] = None
    auto_provision_environments: Optional[bool] = False
    environments_preset:         Optional[str] = None
    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Project name cannot be empty.")
        if len(v) > 100:
            raise ValueError("Project name must be ≤ 100 characters.")
        return v

    @field_validator("project_type")
    @classmethod
    def valid_project_type(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in PROJECT_TYPES:
            raise ValueError(f"project_type must be one of: {sorted(PROJECT_TYPES)}")
        return v


class ProjectUpdate(BaseModel):
    name:        Optional[str] = None
    description: Optional[str] = None
    status:      Optional[str] = None

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.upper() not in VALID_PROJECT_STATUSES:
            raise ValueError(f"status must be one of: {sorted(VALID_PROJECT_STATUSES)}")
        return v.upper() if v else v


class EnvironmentCreate(BaseModel):
    project_id:     Optional[str] = None
    target_project: Optional[str] = None
    name:           str
    account_id:     Optional[str] = None
    env_type:       Optional[str] = None
    type:           Optional[str] = None
    aws_region:     Optional[str] = None
    region:         Optional[str] = None
    description:    Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Environment name cannot be empty.")
        return v

    @field_validator("env_type", mode="before")
    @classmethod
    def valid_env_type(cls, v: Optional[str], info) -> str:
        val = v
        if not val and hasattr(info, "data"):
            val = info.data.get("type")
        if not val:
            val = "development"
        s = str(val).strip().lower()
        mapping = {
            "dev": "development",
            "stage": "staging",
            "staging": "staging",
            "prod": "production",
            "production": "production",
            "test": "testing",
            "testing": "testing",
            "qa": "qa",
            "dr": "disaster_recovery",
            "disaster_recovery": "disaster_recovery",
            "sandbox": "sandbox",
            "preview": "preview",
        }
        normalized = mapping.get(s, s)
        if normalized not in ENV_TYPES:
            raise ValueError(f"env_type must be one of: {sorted(ENV_TYPES)}")
        return normalized

    @field_validator("aws_region", mode="before")
    @classmethod
    def valid_region(cls, v: Optional[str], info) -> str:
        val = v
        if not val and hasattr(info, "data"):
            val = info.data.get("region")
        if not val:
            val = "us-east-1"
        s = str(val).strip().lower()
        if s not in AWS_REGIONS:
            raise ValueError(f"aws_region '{s}' is not a supported AWS region (total 39 regions supported).")
        return s


class EnvironmentUpdate(BaseModel):
    name:        Optional[str] = None
    description: Optional[str] = None


class EnvironmentStatusUpdate(BaseModel):
    """Used by downstream modules to advance the lifecycle state."""
    status: str

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in VALID_ENV_STATUSES:
            raise ValueError(f"status must be one of: {sorted(VALID_ENV_STATUSES)}")
        return v


class EnvironmentCloneRequest(BaseModel):
    new_name:    str
    aws_region:  Optional[str] = None
    env_type:    Optional[str] = None
    description: Optional[str] = None

    @field_validator("new_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("new_name cannot be empty.")
        return v

    @field_validator("aws_region")
    @classmethod
    def valid_aws_region(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip().lower()
            if v not in AWS_REGIONS:
                raise ValueError(f"aws_region '{v}' is not a supported AWS region.")
        return v


class BatchEnvironmentCreate(BaseModel):
    environments: List[EnvironmentCreate]


class ProjectSummaryOut(BaseModel):
    project_id:                str
    name:                      str
    owner:                     str
    tenant_id:                 Optional[str] = None
    account_id:                Optional[str] = None
    project_type:              str
    status:                    str
    environment_count:         int
    active_environments_count: int
    status_breakdown:          dict
    type_breakdown:            dict
    regions:                   List[str]
    health_score:              float
    deployment_ready:          bool
    lifecycle_phase:           str
    created_at:                Optional[str] = None
    updated_at:                Optional[str] = None

    model_config = {"from_attributes": True}


class EnvironmentHealthCheckItem(BaseModel):
    check:  str
    passed: bool
    detail: str


class EnvironmentHealthOut(BaseModel):
    env_id:           str
    project_id:       str
    name:             str
    account_id:       Optional[str] = None
    status:           str
    env_type:         str
    aws_region:       str
    region_supported: bool
    health_status:    str
    lifecycle_phase:  str
    checks:           List[EnvironmentHealthCheckItem]
    checked_at:       str
    model_config = {"from_attributes": True}

# ── Tenant & Membership Schemas ───────────────────────────────────────────────

class TenantCreate(BaseModel):
    name: str
    slug: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Tenant name cannot be empty.")
        if len(v) > 100:
            raise ValueError("Tenant name must be <= 100 characters.")
        return v


class TenantUpdate(BaseModel):
    name:   Optional[str] = None
    status: Optional[str] = None


class TenantMemberAdd(BaseModel):
    user_id:  Optional[str] = None
    username: Optional[str] = None
    role:     str = "MEMBER"

    @field_validator("role")
    @classmethod
    def valid_role(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in {"OWNER", "ADMIN", "MEMBER", "VIEWER"}:
            raise ValueError("Role must be one of: OWNER, ADMIN, MEMBER, VIEWER")
        return v


class TenantMemberRoleUpdate(BaseModel):
    role: str

    @field_validator("role")
    @classmethod
    def valid_role(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in {"OWNER", "ADMIN", "MEMBER", "VIEWER"}:
            raise ValueError("Role must be one of: OWNER, ADMIN, MEMBER, VIEWER")
        return v


class TenantMemberOut(BaseModel):
    id:         str
    tenant_id:  str
    user_id:    str
    username:   Optional[str] = None
    role:       str
    status:     str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}


class TenantOut(BaseModel):
    id:          str
    name:        str
    slug:        str
    tenant_type: str
    status:      str
    role:        Optional[str] = None
    created_at:  Optional[str] = None
    updated_at:  Optional[str] = None

    model_config = {"from_attributes": True}


class TenantListOut(BaseModel):
    tenants: List[TenantOut]
    total:   int


# ── Output Schemas ────────────────────────────────────────────────────────────

class EnvironmentOut(BaseModel):
    id:                 str
    project_id:         str
    tenant_id:          Optional[str] = None
    created_by_user_id: Optional[str] = None
    account_id:         Optional[str] = None
    name:               str
    env_type:           str
    aws_region:         str
    description:        Optional[str] = None
    status:             str
    created_at:         str
    updated_at:         str

    model_config = {"from_attributes": True}


class ProjectOut(BaseModel):
    id:                 str
    name:               str
    description:        Optional[str] = None
    project_type:       str
    owner:              str
    tenant_id:          Optional[str] = None
    created_by_user_id: Optional[str] = None
    account_id:         Optional[str] = None
    status:             str
    environment_count:  int
    environments:       List[EnvironmentOut] = []
    created_at:         str
    updated_at:         str

    model_config = {"from_attributes": True}


class ProjectListOut(BaseModel):
    projects: List[ProjectOut]
    total:    int

