from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AuditEventCreate(BaseModel):
    event_type: str  # e.g., PROJECT_CREATED, ARCHITECTURE_APPROVED, DEPLOYMENT_EXECUTED
    module_key: str  # e.g., MOD-01, MOD-05, MOD-09
    tenant_id: Optional[str] = "ten_default"
    project_id: Optional[str] = None
    environment_id: Optional[str] = None
    actor: str = "system"
    entity_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)

class AuditEvent(BaseModel):
    event_id: str
    event_type: str
    module_key: str
    tenant_id: str
    project_id: Optional[str] = None
    environment_id: Optional[str] = None
    actor: str
    entity_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    occurred_at: float
