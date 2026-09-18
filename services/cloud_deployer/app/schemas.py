# services/cloud_deployer/app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DeploymentRequest(BaseModel):
    project_name: str = Field(default="workload-deployer")
    target_region: str = Field(default="us-east-1")
    dry_run: bool = Field(default=False)
    tfstate_backend: str = Field(default="s3_dynamodb_locked")
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
