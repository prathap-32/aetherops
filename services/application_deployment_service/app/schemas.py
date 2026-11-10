from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DeploymentRequest(BaseModel):
    project_id: Optional[str] = None
    environment_id: Optional[str] = None
    service_name: str
    target_region: str = "us-east-1"
    commit_sha: Optional[str] = None
    image_tag: Optional[str] = "latest"
    container_port: int = 8000
    environment_variables: Dict[str, str] = Field(default_factory=dict)

class DeploymentResponse(BaseModel):
    release_id: str
    status: str
    service_name: str
    target_region: str
    image_digest: str
    endpoint_url: Optional[str] = None
    health_status: str
    deployed_at: float
