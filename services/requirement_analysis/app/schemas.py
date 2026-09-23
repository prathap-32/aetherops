# services/requirement_analysis/app/schemas.py
from typing import List, Optional, Literal
from enum import Enum
from pydantic import BaseModel, Field

class CloudStream(str, Enum):
    web_application = "web_application"
    ai_ml = "ai_ml"
    iot = "iot"
    devops_tooling = "devops_tooling"
    dev_sandbox = "dev_sandbox"

class TechnologyStack(BaseModel):
    frontend: Literal["none", "react_vue_angular", "simple_html_css"] = "none"
    backend: Literal["none", "python_fastapi_django", "nodejs_express", "java_spring"] = "none"
    database: Literal["none", "postgresql", "mysql"] = "none"

class OperationsPreference(BaseModel):
    container_orchestration: Literal["none", "docker_compose", "kubernetes", "ecs_fargate", "eks"] = "none"
    infrastructure_as_code: Literal["none", "terraform"] = "none"
    configuration_management: Literal["none", "ansible"] = "none"
    ci_cd_pipeline: Literal["none", "github_actions", "jenkins"] = "none"

class MonitoringPreference(BaseModel):
    level: Literal["none", "basic", "advanced"] = "none"
    alerting_channel: Literal["none", "email", "slack_webhook"] = "none"

class TrafficScale(str, Enum):
    hobby_dev = "hobby_dev"
    growth = "growth"
    production = "production"

class ReliabilityLevel(str, Enum):
    dev_testing = "dev_testing"
    production_safe = "production_safe"
    mission_critical = "mission_critical"

class SecurityNeed(str, Enum):
    standard = "standard"
    healthcare = "healthcare"
    payment_processing = "payment_processing"

class RequirementInput(BaseModel):
    project_name: str = Field(
        default="my-first-cloud-infra",
        description="Alphanumeric name for your project, used to tag resources"
    )
    stream: CloudStream = Field(
        default=CloudStream.web_application,
        description="The primary stream/domain of your cloud architecture"
    )
    technology: TechnologyStack = Field(
        default_factory=TechnologyStack,
        description="Software development stack settings"
    )
    operations: OperationsPreference = Field(
        default_factory=OperationsPreference,
        description="DevOps/operations tools and pipeline settings"
    )
    monitoring: MonitoringPreference = Field(
        default_factory=MonitoringPreference,
        description="Metrics, logging, and alerting preferences"
    )
    traffic_scale: TrafficScale = Field(
        default=TrafficScale.hobby_dev,
        description="Expected traffic volume of the application"
    )
    reliability: ReliabilityLevel = Field(
        default=ReliabilityLevel.dev_testing,
        description="Uptime safety and recovery needs"
    )
    data_storage_gb: float = Field(
        default=5.0,
        description="Persistent database storage volume size in GB",
        ge=0.0
    )
    security_need: SecurityNeed = Field(
        default=SecurityNeed.standard,
        description="Security compliance profile"
    )
    monthly_budget: Optional[float] = Field(
        default=None,
        description="Desired monthly cost limit in USD. If None, budget is unlimited.",
        ge=0.0
    )
    raw_prompt: Optional[str] = Field(
        default=None,
        description="Optional natural-language description of system requirements"
    )

class NaturalLanguagePromptRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=3,
        description="Plain English description of system requirements",
        examples=["Build a healthcare EHR API with FastAPI and PostgreSQL under $200/mo"]
    )
    target_region: Optional[str] = Field(
        default="us-east-1",
        description="Target AWS deployment region"
    )
    auto_save: bool = Field(
        default=False,
        description="Whether to persist analyzed project directly into SQLite requirements.db"
    )

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

class RecommendationInput(BaseModel):
    region: str = Field(..., examples=["us-east-1", "ap-southeast-1"])
    tech_stack: str = Field(..., examples=["web_api", "ai_ml", "iot"])
    traffic_scale: Literal["low", "medium", "high"] = Field(..., examples=["low", "medium", "high"])
    storage_size_gb: float = Field(..., ge=0.0, examples=[50.0])
    security_level: Literal["standard", "enhanced", "strict"] = Field(..., examples=["standard", "enhanced", "strict"])
    monthly_max_budget: Optional[float] = Field(None, ge=0.0, examples=[500.0])

class RecommendationOutput(BaseModel):
    region: str
    tech_stack: str
    traffic_scale: str
    budget_status: Literal["WITHIN_BUDGET", "EXCEEDED", "UNLIMITED"]
    monthly_budget_limit: Optional[float]
    total_monthly_cost: float
    cost_breakdown: dict
    recommended_resources: dict

