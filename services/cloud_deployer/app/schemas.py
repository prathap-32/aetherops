# services/cloud_deployer/app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DeploymentRequest(BaseModel):
    project_name: str = Field(default="workload-deployer")
    target_region: str = Field(default="us-east-1")
    dry_run: bool = Field(default=False)
    tfstate_backend: str = Field(default="s3_dynamodb_locked")
    architecture_version_id: Optional[str] = None
    terraform_version_id: Optional[str] = None
    plan_id: Optional[str] = None
    resource_manifest: Dict[str, Any] = Field(default_factory=lambda: {
        "vpc": "10.0.0.0/16",
        "ec2_count": 2,
        "rds_engine": "postgres"
    })

class ResourceDeployStatus(BaseModel):
    resource_id: str
    resource_type: str
    action: str  # CREATE, MODIFY, DESTROY, NO_OP
    status: str  # PROVISIONED, FAILED, PENDING

class DeploymentResponse(BaseModel):
    status: str
    deployment_id: str
    project_name: str
    target_region: str
    resources_applied: List[ResourceDeployStatus]
    execution_time_seconds: float
    state_lock_acquired: bool
    mode: str = Field(default="TEST_SANDBOX")
    sandbox_notice: Optional[str] = None

class DriftDetectionRequest(BaseModel):
    project_name: str
    target_region: str = Field(default="us-east-1")

class DriftItem(BaseModel):
    resource_id: str
    expected_state: Dict[str, Any]
    actual_state: Dict[str, Any]
    drift_type: str  # ATTRIBUTE_MODIFIED, MISSING, UNMANAGED

class DriftDetectionResponse(BaseModel):
    status: str
    project_name: str
    is_in_sync: bool
    total_drift_items: int
    drifts: List[DriftItem]

# --- Pre-Deployment Dry Run, Risk Engine, and Gated Execution Schemas ---

class DeploymentPlanRequest(BaseModel):
    project_name: str = Field(default="aether-workload")
    environment_tier: str = Field(default="development")
    target_region: str = Field(default="us-east-1")
    architecture_version_id: Optional[str] = None
    terraform_version_id: Optional[str] = None
    cloud_connection_id: Optional[str] = None
    aws_account_id: Optional[str] = None
    tenant_id: Optional[str] = None
    terraform_files: Optional[List[Dict[str, Any]]] = None

class ResourceChange(BaseModel):
    resource_id: str
    resource_type: str
    action: str  # CREATE, UPDATE, REPLACE, DESTROY
    symbol: str  # +, ~, !, -
    details: Dict[str, Any] = Field(default_factory=dict)

class RiskFinding(BaseModel):
    id: str
    category: str  # SPOF, SECURITY, FINOPS, COMPLIANCE
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    title: str
    explanation: str
    is_blocking: bool

class DeploymentPlanResponse(BaseModel):
    status: str = "PLANNED"
    plan_id: str
    plan_digest: str
    project_name: str
    environment_tier: str
    target_region: str
    architecture_version_id: Optional[str] = None
    terraform_version_id: Optional[str] = None
    resource_changes: List[ResourceChange]
    summary: Dict[str, int]
    risk_assessment: Dict[str, Any]
    created_at: float
    can_approve: bool

class DeploymentApproveRequest(BaseModel):
    plan_id: str
    plan_digest: str
    comments: Optional[str] = None
    override_blocked: bool = False

class DeploymentApproveResponse(BaseModel):
    status: str = "APPROVED"
    approval_id: str
    plan_id: str
    plan_digest: str
    approved_by: str
    approved_by_uuid: str
    tenant_id: str
    approved_at: float
    message: str

class DeploymentExecuteRequest(BaseModel):
    plan_id: str
    execution_mode: Optional[str] = None  # REAL or TEST_SANDBOX
    dry_run: bool = False
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: Optional[str] = None

class DeployedResource(BaseModel):
    resource_id: str
    resource_type: str
    status: str
    arn: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
