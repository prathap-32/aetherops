# services/source_and_cloud_connection/app/schemas.py
from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator, model_validator

VALID_CONNECTION_STATUSES = {"PENDING", "CONNECTED", "FAILED", "DISCONNECTED"}
VALID_CLOUD_AUTH_TYPES = {"ACCESS_KEYS", "IAM_ROLE_ARN", "IAM_ARN", "IAM_USER_ARN"}


# ═══════════════════════════════════════════════════════════════════════════════
# GIT CONNECTION SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class GitConnectionCreate(BaseModel):
    project_id:     str
    environment_id: str
    repo_url:       str
    branch:         str = "main"
    auth_type:      Optional[str] = "PAT"   # OAUTH | PAT | MANUAL
    github_user:    Optional[str] = None
    pat_token:      Optional[str] = None    # raw PAT — hashed and discarded, never stored as-is
    pat_label:      Optional[str] = None    # human-readable label for the token

    @field_validator("repo_url")
    @classmethod
    def valid_repo_url(cls, v: str) -> str:
        v = v.strip().rstrip("/")
        if not (v.startswith("https://github.com/") or v.startswith("https://gitlab.com/")
                or v.startswith("https://bitbucket.org/")):
            raise ValueError("repo_url must start with https://github.com/, https://gitlab.com/, or https://bitbucket.org/")
        return v

    @field_validator("branch")
    @classmethod
    def valid_branch(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("branch cannot be empty.")
        return v

    @field_validator("project_id", "environment_id")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("ID cannot be empty.")
        return v.strip()


class GitConnectionUpdate(BaseModel):
    branch:      Optional[str] = None
    auth_type:   Optional[str] = None
    github_user: Optional[str] = None
    pat_token:   Optional[str] = None
    pat_label:   Optional[str] = None


class ConnectionStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in VALID_CONNECTION_STATUSES:
            raise ValueError(f"status must be one of: {sorted(VALID_CONNECTION_STATUSES)}")
        return v


class GitConnectionOut(BaseModel):
    id:                 str
    project_id:         str
    environment_id:     str
    tenant_id:          Optional[str] = None
    created_by_user_id: Optional[str] = None
    owner:              str
    repo_url:           str
    repo_name:          str
    branch:             str
    auth_type:          Optional[str] = "PAT"
    github_user:        Optional[str] = None
    pat_label:          Optional[str] = None
    default_branch:     Optional[str] = None
    last_commit_sha:    Optional[str] = None
    last_commit_msg:    Optional[str] = None
    last_commit_author: Optional[str] = None
    last_commit_at:     Optional[str] = None
    is_private:         bool = False
    stars:              Optional[str] = None
    language:           Optional[str] = None
    status:             str
    created_at:         str
    updated_at:         str

    model_config = {"from_attributes": True}


class SourceSnapshotOut(BaseModel):
    id:             str
    connection_id:  str
    project_id:     str
    environment_id: str
    commit_sha:     str
    branch:         str
    file_tree:      List[Dict[str, Any]] = []
    detected_files: Dict[str, Any] = {}
    language_hints: Dict[str, Any] = {}
    total_files:    Optional[str] = None
    total_size_kb:  Optional[str] = None
    created_at:     str

    model_config = {"from_attributes": True}


class ConnectionListOut(BaseModel):
    connections: List[GitConnectionOut]
    total:       int


# ═══════════════════════════════════════════════════════════════════════════════
# GITHUB INTEGRATION SCHEMAS (OAUTH & PAT)
# ═══════════════════════════════════════════════════════════════════════════════

class GitHubVerifyPatRequest(BaseModel):
    pat_token: Optional[str] = None
    token: Optional[str] = None

    @property
    def effective_token(self) -> str:
        return (self.pat_token or self.token or "").strip()


class GitHubVerifyPatResponse(BaseModel):
    valid:     bool
    username:  str
    name:      Optional[str] = None
    avatar_url: Optional[str] = None
    scopes:    Optional[str] = None


class GitHubOAuthConfigRequest(BaseModel):
    client_id:     str
    client_secret: str
    redirect_uri:  Optional[str] = None


class GitHubOAuthConfigResponse(BaseModel):
    is_configured:     bool
    client_id:         Optional[str] = None
    redirect_uri:      Optional[str] = None
    callback_url_hint: str


class GitHubRepoItem(BaseModel):
    name:           str
    full_name:      str
    html_url:       str
    default_branch: str = "main"
    is_private:     bool = False
    language:       Optional[str] = None
    description:    Optional[str] = None


class GitHubRepoListOut(BaseModel):
    repos:    List[GitHubRepoItem]
    total:    int
    username: Optional[str] = None


class GitHubBranchListOut(BaseModel):
    branches: List[str]


# ═══════════════════════════════════════════════════════════════════════════════
# AWS CLOUD CONNECTION SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class AwsValidateRequest(BaseModel):
    auth_type:          str = "ACCESS_KEYS"  # ACCESS_KEYS | IAM_ROLE_ARN
    aws_region:         str = "us-east-1"
    access_key_id:      Optional[str] = None
    secret_access_key:  Optional[str] = None
    aws_access_key_id:  Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    session_token:      Optional[str] = None
    role_arn:           Optional[str] = None
    external_id:        Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def resolve_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("access_key_id") and data.get("aws_access_key_id"):
                data["access_key_id"] = data["aws_access_key_id"]
            if not data.get("secret_access_key") and data.get("aws_secret_access_key"):
                data["secret_access_key"] = data["aws_secret_access_key"]
            if not data.get("aws_region") and data.get("region"):
                data["aws_region"] = data["region"]
        return data

    @field_validator("auth_type")
    @classmethod
    def valid_auth_type(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in VALID_CLOUD_AUTH_TYPES:
            raise ValueError(f"auth_type must be one of: {sorted(VALID_CLOUD_AUTH_TYPES)}")
        if v in ("IAM_ARN", "IAM_USER_ARN"):
            return "IAM_ROLE_ARN"
        return v

    @field_validator("aws_region")
    @classmethod
    def valid_aws_region(cls, v: str) -> str:
        return v.strip().lower() if v else "us-east-1"


class AwsValidateResponse(BaseModel):
    valid:          bool
    provider:       str = "AWS"
    auth_type:      str
    account_id:     str
    arn:            str
    user_id:        Optional[str] = None
    role_name:      Optional[str] = None
    user_name:      Optional[str] = None
    resource_type:  Optional[str] = None
    region:         str
    masked_key:     Optional[str] = None
    simulated:      bool = False
    note:           Optional[str] = None


class CloudConnectionCreate(BaseModel):
    project_id:         str
    environment_id:     str
    provider:           str = "AWS"
    auth_type:          str = "ACCESS_KEYS"  # ACCESS_KEYS | IAM_ROLE_ARN
    aws_region:         str = "us-east-1"
    access_key_id:      Optional[str] = None
    secret_access_key:  Optional[str] = None
    aws_access_key_id:  Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    session_token:      Optional[str] = None
    role_arn:           Optional[str] = None
    external_id:        Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def resolve_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("access_key_id") and data.get("aws_access_key_id"):
                data["access_key_id"] = data["aws_access_key_id"]
            if not data.get("secret_access_key") and data.get("aws_secret_access_key"):
                data["secret_access_key"] = data["aws_secret_access_key"]
            if not data.get("aws_region") and data.get("region"):
                data["aws_region"] = data["region"]
        return data

    @field_validator("auth_type")
    @classmethod
    def valid_auth_type(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in VALID_CLOUD_AUTH_TYPES:
            raise ValueError(f"auth_type must be one of: {sorted(VALID_CLOUD_AUTH_TYPES)}")
        if v in ("IAM_ARN", "IAM_USER_ARN"):
            return "IAM_ROLE_ARN"
        return v

    @field_validator("project_id", "environment_id")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("ID cannot be empty.")
        return v.strip()


class CloudConnectionUpdate(BaseModel):
    aws_region:         Optional[str] = None
    access_key_id:      Optional[str] = None
    secret_access_key:  Optional[str] = None
    session_token:      Optional[str] = None
    role_arn:           Optional[str] = None
    external_id:        Optional[str] = None
    status:             Optional[str] = None


class CloudConnectionOut(BaseModel):
    id:                 str
    project_id:         str
    environment_id:     str
    tenant_id:          Optional[str] = None
    created_by_user_id: Optional[str] = None
    owner:              str
    provider:           str
    auth_type:          str
    aws_region:         str
    access_key_masked:  Optional[str] = None
    role_arn:           Optional[str] = None
    external_id:        Optional[str] = None
    account_id:         Optional[str] = None
    caller_arn:         Optional[str] = None
    caller_user_id:     Optional[str] = None
    status:             str
    last_validated_at:  Optional[str] = None
    created_at:         str
    updated_at:         str

    model_config = {"from_attributes": True}


class CloudConnectionListOut(BaseModel):
    connections: List[CloudConnectionOut]
    total:       int


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED FINALIZE SCHEMAS (SOURCE + CLOUD TOGETHER)
# ═══════════════════════════════════════════════════════════════════════════════

class UnifiedFinalizeRequest(BaseModel):
    project_id:         str
    environment_id:     str

    # Source (GitHub)
    repo_url:           str
    branch:             str = "main"
    git_auth_type:      str = "PAT"   # OAUTH | PAT | MANUAL
    github_user:        Optional[str] = None
    pat_token:          Optional[str] = None
    access_token:       Optional[str] = None
    pat_label:          Optional[str] = None

    # Cloud (AWS)
    cloud_provider:     str = "AWS"
    cloud_auth_type:    str = "ACCESS_KEYS"  # ACCESS_KEYS | IAM_ROLE_ARN
    aws_region:         str = "us-east-1"
    access_key_id:      Optional[str] = None
    secret_access_key:  Optional[str] = None
    aws_access_key_id:  Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    session_token:      Optional[str] = None
    role_arn:           Optional[str] = None
    external_id:        Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def resolve_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("access_key_id") and data.get("aws_access_key_id"):
                data["access_key_id"] = data["aws_access_key_id"]
            if not data.get("secret_access_key") and data.get("aws_secret_access_key"):
                data["secret_access_key"] = data["aws_secret_access_key"]
            if not data.get("pat_token") and data.get("access_token"):
                data["pat_token"] = data["access_token"]
        return data

    @field_validator("cloud_auth_type")
    @classmethod
    def valid_cloud_auth_type(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in VALID_CLOUD_AUTH_TYPES:
            raise ValueError(f"cloud_auth_type must be one of: {sorted(VALID_CLOUD_AUTH_TYPES)}")
        if v in ("IAM_ARN", "IAM_USER_ARN"):
            return "IAM_ROLE_ARN"
        return v

    @field_validator("project_id", "environment_id", "repo_url")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty.")
        return v.strip()


class UnifiedFinalizeOut(BaseModel):
    git_connection:   GitConnectionOut
    cloud_connection: Optional[CloudConnectionOut] = None
    snapshot:         Optional[SourceSnapshotOut] = None
    status:           str
    message:          str
