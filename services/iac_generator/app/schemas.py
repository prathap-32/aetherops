# services/iac_generator/app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class IaCGenerationRequest(BaseModel):
    project_name: str = Field(default="aether-workload", description="Target project identifier")
    aws_region: str = Field(default="us-east-1", description="AWS target deployment region")
    iac_tool: str = Field(default="terraform", description="Target IaC tool: terraform, opentofu")
    compute_instance_type: str = Field(default="t3.medium", description="EC2 instance type")
    compute_count: int = Field(default=2, ge=1)
    database_instance_type: str = Field(default="db.t3.medium", description="RDS instance type")
    database_storage_gb: int = Field(default=50, ge=10)
    database_multi_az: bool = Field(default=True)
    enable_alb: bool = Field(default=True)
    enable_waf: bool = Field(default=True)
    enable_kms: bool = Field(default=True)
    tags: Dict[str, str] = Field(default_factory=lambda: {"ManagedBy": "AetherOps", "Environment": "Production"})

class GeneratedFile(BaseModel):
    filename: str
    content: str
    language: str

class IaCGenerationResponse(BaseModel):
    status: str
    iac_tool: str
    project_name: str
    files: List[GeneratedFile]
    summary: Dict[str, Any]
