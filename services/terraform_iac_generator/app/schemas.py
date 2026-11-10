# services/iac_generator/app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class IaCGenerationRequest(BaseModel):
    project_name: str = Field(default="aether-workload", description="Target project identifier")
    aws_region: str = Field(default="us-east-1", description="AWS target deployment region")
    iac_tool: str = Field(default="terraform", description="Target IaC tool: terraform, opentofu")
    architecture_version_id: Optional[str] = Field(default=None, description="Approved architecture version ID required for IaC generation")
    compute_instance_type: str = Field(default="t3.medium", description="EC2 instance type")
    compute_count: int = Field(default=1, ge=1)
    database_instance_type: str = Field(default="db.t3.medium", description="RDS instance type")
    database_storage_gb: int = Field(default=20, ge=0)
    database_multi_az: bool = Field(default=False)
    enable_alb: bool = Field(default=False)
    enable_waf: bool = Field(default=False)
    enable_kms: bool = Field(default=False)
    tags: Dict[str, str] = Field(default_factory=lambda: {"ManagedBy": "AetherOps", "Environment": "Production"})

class InfrastructureResourceIR(BaseModel):
    resource_id: str
    aws_service: str
    terraform_type: str
    logical_name: str
    region: str
    required_config: Dict[str, Any] = Field(default_factory=dict)
    optional_config: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    network_relationships: Dict[str, Any] = Field(default_factory=dict)
    security_relationships: Dict[str, Any] = Field(default_factory=dict)
    source_architecture_resource_id: str
    approved_values: Dict[str, Any] = Field(default_factory=dict)
    cost_relevant: bool = True
    explicitly_approved: bool = True

class InfrastructureIR(BaseModel):
    project_id: str
    environment_id: str
    architecture_version_id: str
    region: str
    environment_tier: str
    resources: List[InfrastructureResourceIR] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConsistencyVerificationReport(BaseModel):
    status: str = Field(default="PASSED", description="PASSED or FAILED")
    approved_summary: Dict[str, int] = Field(default_factory=dict)
    generated_summary: Dict[str, int] = Field(default_factory=dict)
    unexpected_resources: List[str] = Field(default_factory=list)
    missing_resources: List[str] = Field(default_factory=list)
    configuration_mismatches: List[str] = Field(default_factory=list)
    cost_relevant_changes: List[str] = Field(default_factory=list)
    details: str = Field(default="")

class GeneratedFile(BaseModel):
    filename: str
    content: str
    language: str

class IaCGenerationResponse(BaseModel):
    status: str
    iac_tool: str
    project_name: str
    architecture_version_id: Optional[str] = None
    terraform_version_id: str = Field(default="", description="Unique version identifier for the synthesized Terraform bundle")
    checksum: str = Field(default="", description="SHA256 checksum of synthesized configuration files")
    approved_architecture_link: str = Field(default="", description="URI link to the approved architecture version")
    validation: Dict[str, Any] = Field(default_factory=dict, description="Terraform fmt and validate verification report")
    consistency_report: Optional[Dict[str, Any]] = Field(default=None, description="Architecture-to-IaC consistency verification report")
    intermediate_representation: Optional[Dict[str, Any]] = Field(default=None, description="Structured Infrastructure Intermediate Representation (IR)")
    files: List[GeneratedFile]
    summary: Dict[str, Any]
