from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ResourceChange(BaseModel):
    action: str  # CREATE, UPDATE, DELETE, NOOP
    symbol: str  # +, ~, -, =
    resource_type: str
    name: str
    diff: Optional[str] = None
    cost_monthly_usd: float = 0.0
    is_destructive: bool = False

class RiskFinding(BaseModel):
    category: str  # SPOF, SECURITY, FINOPS, PERFORMANCE, OPERATIONS, SUSTAINABILITY
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    message: str
    affected_resource: Optional[str] = None
    recommendation: Optional[str] = None
    is_blocking: bool = False

class DeploymentPlanRequest(BaseModel):
    project_name: str
    target_region: str
    environment_tier: str = "production"
    tenant_id: Optional[str] = None
    terraform_files: Optional[Dict[str, str]] = None
    architecture_version_id: Optional[str] = None

class DeploymentPlanResponse(BaseModel):
    plan_id: str
    project_name: str
    target_region: str
    environment_tier: str
    plan_hash: str
    changes: List[ResourceChange]
    risk_assessment: Dict[str, Any]
    cost_summary: Optional[Dict[str, Any]] = Field(default_factory=dict)
    complexity_assessment: Optional[Dict[str, Any]] = Field(default_factory=dict)
    can_proceed: bool
