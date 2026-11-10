from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class ComputeRecommendation(BaseModel):
    instance_type: str = "t3.medium"
    vcpus: int = 2
    ram_gb: float = 4.0
    min_instances: int = 1
    max_instances: int = 3
    target_cpu_utilization: int = 70
    has_autoscaling: bool = True
    monthly_cost: float = 30.37

class DatabaseRecommendation(BaseModel):
    instance_type: str = "db.t3.medium"
    vcpus: int = 2
    ram_gb: float = 4.0
    storage_gb: int = 50
    storage_type: str = "gp3"
    multi_az: bool = False
    replica_count: int = 0
    backup_retention_days: int = 7
    monthly_cost: float = 49.64

class NetworkingRecommendation(BaseModel):
    has_alb: bool = True
    nat_gateway_count: int = 1
    has_cloudfront: bool = False
    monthly_cost: float = 22.50

class StorageRecommendation(BaseModel):
    s3_gb: int = 20
    s3_class: str = "Standard"
    ebs_gb_per_instance: int = 30
    monthly_cost: float = 3.60

class SecurityRecommendation(BaseModel):
    encryption_enabled: bool = True
    iam_audit_required: bool = True
    waf_enabled: bool = False
    kms_key_rotation: bool = True

class OperationsRecommendation(BaseModel):
    orchestration_tool: str = "Terraform"
    iac_tool: str = "Terraform HCL"
    config_tool: str = "AWS Systems Manager"
    ci_cd_tool: str = "GitHub Actions"
    files_to_generate: List[str] = Field(default_factory=lambda: ["main.tf", "variables.tf", "outputs.tf"])

class MonitoringRecommendation(BaseModel):
    level: str = "Standard"
    alerting_channel: str = "CloudWatch SNS"
    tools_to_deploy: List[str] = Field(default_factory=lambda: ["CloudWatch", "AWS X-Ray"])

class ArchitectureComponents(BaseModel):
    compute: ComputeRecommendation = Field(default_factory=ComputeRecommendation)
    database: DatabaseRecommendation = Field(default_factory=DatabaseRecommendation)
    networking: NetworkingRecommendation = Field(default_factory=NetworkingRecommendation)
    storage: StorageRecommendation = Field(default_factory=StorageRecommendation)
    security: SecurityRecommendation = Field(default_factory=SecurityRecommendation)
    operations: OperationsRecommendation = Field(default_factory=OperationsRecommendation)
    monitoring: MonitoringRecommendation = Field(default_factory=MonitoringRecommendation)

class RequirementProfileOutput(BaseModel):
    architecture_tier: Literal["Developer", "Production-Standard", "Enterprise-HA"] = "Developer"
    high_availability_mode: Literal["none", "multi-az", "multi-region"] = "none"
    compliance_applied: List[str] = Field(default_factory=list)
    monthly_budget_limit: Optional[float] = None
    total_estimated_cost: float = 106.11
    cost_exceeds_budget: bool = False
    components: ArchitectureComponents = Field(default_factory=ArchitectureComponents)
    educational_notes: List[str] = Field(default_factory=list)
    remediation_steps: List[str] = Field(default_factory=list)

class ArchitectureRecommendationRequest(BaseModel):
    project_id: Optional[str] = None
    environment_id: Optional[str] = None
    environment_tier: str = "development"
    target_region: str = "us-east-1"
    workload_type: str = "web_app"
    languages: List[str] = Field(default_factory=lambda: ["python"])
    frameworks: List[str] = Field(default_factory=lambda: ["fastapi"])
    databases: List[str] = Field(default_factory=list)
    ports: List[int] = Field(default_factory=lambda: [8000])
    monthly_budget: Optional[float] = None

class ArchitectureRecommendationResponse(BaseModel):
    status: str = "SUCCESS"
    project_id: Optional[str] = None
    environment_id: Optional[str] = None
    profile: RequirementProfileOutput
    rationale: str
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)
