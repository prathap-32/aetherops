from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ValidationFinding(BaseModel):
    id: str
    category: str
    severity: str
    title: str
    explanation: str
    evidence: str
    affected_resources: List[str] = Field(default_factory=list)
    recommended_correction: str
    is_blocking: bool = False

class ArchitectureValidationRequest(BaseModel):
    project_id: Optional[str] = None
    environment_id: Optional[str] = None
    environment_tier: str = "development"
    target_region: str = "us-east-1"
    version_id: Optional[str] = None
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)

class ArchitectureValidationResponse(BaseModel):
    status: str  # PASS, WARNING, BLOCKED
    blocking_count: int
    warning_count: int
    findings: List[ValidationFinding] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)
    pillars: Dict[str, Any] = Field(default_factory=dict)
    can_proceed_to_iac: bool
