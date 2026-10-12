# services/project_and_environment_management/app/schemas.py
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, field_validator

# ── Valid choices ─────────────────────────────────────────────────────────────

PROJECT_TYPES = {
    "web_application",
    "api_service",
    "data_pipeline",
    "ml_workload",
    "static_site",
    "microservices",
}

ENV_TYPES = {"development", "staging", "production"}

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
    name:         str
    description:  Optional[str] = None
    project_type: str

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
    name:        str
    env_type:    str
    aws_region:  str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Environment name cannot be empty.")
        return v

    @field_validator("env_type")
    @classmethod
    def valid_env_type(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in ENV_TYPES:
            raise ValueError(f"env_type must be one of: {sorted(ENV_TYPES)}")
        return v

    @field_validator("aws_region")
    @classmethod
    def valid_region(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in AWS_REGIONS:
            raise ValueError(f"aws_region '{v}' is not a supported AWS region.")
        return v


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


# ── Output Schemas ────────────────────────────────────────────────────────────

class EnvironmentOut(BaseModel):
    id:          str
    project_id:  str
    name:        str
    env_type:    str
    aws_region:  str
    description: Optional[str]
    status:      str
    created_at:  str
    updated_at:  str

    model_config = {"from_attributes": True}


class ProjectOut(BaseModel):
    id:                str
    name:              str
    description:       Optional[str]
    project_type:      str
    owner:             str
    status:            str
    environment_count: int
    environments:      List[EnvironmentOut] = []
    created_at:        str
    updated_at:        str

    model_config = {"from_attributes": True}


class ProjectListOut(BaseModel):
    projects: List[ProjectOut]
    total:    int
