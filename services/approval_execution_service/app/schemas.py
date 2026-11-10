from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DeploymentApproveRequest(BaseModel):
    plan_id: str
    plan_hash: Optional[str] = None
    plan_digest: Optional[str] = None
    approver: Optional[str] = None
    comments: Optional[str] = None
    override_blocked: bool = False

class DeploymentApproveResponse(BaseModel):
    status: str
    plan_id: str
    approval_id: str
    approved_by: str
    approved_at: float
    message: str

class DeploymentExecuteRequest(BaseModel):
    plan_id: str
    plan_hash: Optional[str] = None
    plan_digest: Optional[str] = None
    mode: Optional[str] = "TEST_SANDBOX"  # REAL or TEST_SANDBOX
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: Optional[str] = None
