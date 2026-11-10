# services/architecture_generator/app/schemas.py
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# Input schemas matching Module 1 output
class ComputeRecommendation(BaseModel):
    instance_type: str
    vcpus: int
    ram_gb: float
    min_instances: int
    max_instances: int
    target_cpu_utilization: int
    has_autoscaling: bool
    monthly_cost: float

class DatabaseRecommendation(BaseModel):
    instance_type: str
    vcpus: int
    ram_gb: float
    storage_gb: int
    storage_type: str
    multi_az: bool
    replica_count: int
    backup_retention_days: int
    monthly_cost: float

class NetworkingRecommendation(BaseModel):
    has_alb: bool
    nat_gateway_count: int
    has_cloudfront: bool
    monthly_cost: float

class StorageRecommendation(BaseModel):
    s3_gb: int
    s3_class: str
    ebs_gb_per_instance: int
    monthly_cost: float

class SecurityRecommendation(BaseModel):
    encryption_enabled: bool
    iam_audit_required: bool
    waf_enabled: bool
    kms_key_rotation: bool

class OperationsRecommendation(BaseModel):
    orchestration_tool: str
    iac_tool: str
    config_tool: str
    ci_cd_tool: str
    files_to_generate: List[str]

class MonitoringRecommendation(BaseModel):
    level: str
    alerting_channel: str
    tools_to_deploy: List[str]

class ArchitectureComponents(BaseModel):
    compute: ComputeRecommendation
    database: DatabaseRecommendation
    networking: NetworkingRecommendation
    storage: StorageRecommendation
    security: SecurityRecommendation
    operations: OperationsRecommendation
    monitoring: MonitoringRecommendation

class RequirementProfileOutput(BaseModel):
    architecture_tier: Literal["Developer", "Production-Standard", "Enterprise-HA"]
    high_availability_mode: Literal["none", "multi-az", "multi-region"]
    compliance_applied: List[str]
    monthly_budget_limit: Optional[float]
    total_estimated_cost: float
    cost_exceeds_budget: bool
    components: ArchitectureComponents
    educational_notes: List[str]
    remediation_steps: List[str]

# React Flow Output schemas
class ReactFlowNodePosition(BaseModel):
    x: float
    y: float

class ReactFlowNodeData(BaseModel):
    label: str
    resource_type: str  # e.g., "vpc", "subnet", "alb", "ec2", "rds", "s3", "internet", "cloudfront"
    details: Optional[dict] = None

class ReactFlowNode(BaseModel):
    id: str
    type: Optional[str] = "customNode"
    data: ReactFlowNodeData
    position: ReactFlowNodePosition
    parentId: Optional[str] = None
    width: Optional[float] = None
    height: Optional[float] = None

class ReactFlowEdge(BaseModel):
    id: str
    source: str
    target: str
    animated: bool = False
    label: Optional[str] = None
    style: Optional[dict] = None

class ReactFlowGraphJSON(BaseModel):
    nodes: List[ReactFlowNode]
    edges: List[ReactFlowEdge]
