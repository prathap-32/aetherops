from typing import Dict, Any, List
from app.schemas import (
    ArchitectureRecommendationRequest,
    RequirementProfileOutput,
    ArchitectureComponents,
    ComputeRecommendation,
    DatabaseRecommendation,
    NetworkingRecommendation,
    StorageRecommendation,
    SecurityRecommendation,
    OperationsRecommendation,
    MonitoringRecommendation
)

def build_recommendation(req: ArchitectureRecommendationRequest) -> Dict[str, Any]:
    tier = (req.environment_tier or "development").lower()
    is_prod = "prod" in tier
    is_staging = "stag" in tier

    if is_prod:
        arch_tier = "Production-Standard"
        ha_mode = "multi-az"
        compute = ComputeRecommendation(
            instance_type="t3.large",
            vcpus=2,
            ram_gb=8.0,
            min_instances=2,
            max_instances=6,
            has_autoscaling=True,
            monthly_cost=121.47
        )
        database = DatabaseRecommendation(
            instance_type="db.t3.medium",
            vcpus=2,
            ram_gb=4.0,
            storage_gb=100,
            multi_az=True,
            backup_retention_days=14,
            monthly_cost=99.28
        )
        networking = NetworkingRecommendation(
            has_alb=True,
            nat_gateway_count=2,
            has_cloudfront=True,
            monthly_cost=70.00
        )
        security = SecurityRecommendation(
            encryption_enabled=True,
            iam_audit_required=True,
            waf_enabled=True,
            kms_key_rotation=True
        )
    elif is_staging:
        arch_tier = "Developer"
        ha_mode = "none"
        compute = ComputeRecommendation(
            instance_type="t3.medium",
            vcpus=2,
            ram_gb=4.0,
            min_instances=1,
            max_instances=2,
            has_autoscaling=True,
            monthly_cost=30.37
        )
        database = DatabaseRecommendation(
            instance_type="db.t3.small",
            vcpus=2,
            ram_gb=2.0,
            storage_gb=30,
            multi_az=False,
            backup_retention_days=7,
            monthly_cost=24.82
        )
        networking = NetworkingRecommendation(
            has_alb=True,
            nat_gateway_count=1,
            has_cloudfront=False,
            monthly_cost=22.50
        )
        security = SecurityRecommendation(
            encryption_enabled=True,
            iam_audit_required=True,
            waf_enabled=False,
            kms_key_rotation=True
        )
    else: # development / sandbox
        arch_tier = "Developer"
        ha_mode = "none"
        compute = ComputeRecommendation(
            instance_type="t3.small",
            vcpus=2,
            ram_gb=2.0,
            min_instances=1,
            max_instances=1,
            has_autoscaling=False,
            monthly_cost=15.18
        )
        database = DatabaseRecommendation(
            instance_type="db.t3.micro",
            vcpus=2,
            ram_gb=1.0,
            storage_gb=20,
            multi_az=False,
            backup_retention_days=1,
            monthly_cost=12.41
        )
        networking = NetworkingRecommendation(
            has_alb=False,
            nat_gateway_count=0,
            has_cloudfront=False,
            monthly_cost=0.00
        )
        security = SecurityRecommendation(
            encryption_enabled=True,
            iam_audit_required=False,
            waf_enabled=False,
            kms_key_rotation=False
        )

    storage = StorageRecommendation()
    operations = OperationsRecommendation()
    monitoring = MonitoringRecommendation()

    components = ArchitectureComponents(
        compute=compute,
        database=database,
        networking=networking,
        storage=storage,
        security=security,
        operations=operations,
        monitoring=monitoring
    )

    total_cost = (
        compute.monthly_cost +
        database.monthly_cost +
        networking.monthly_cost +
        storage.monthly_cost
    )

    profile = RequirementProfileOutput(
        architecture_tier=arch_tier,
        high_availability_mode=ha_mode,
        compliance_applied=["SOC2-Readiness"] if is_prod else [],
        monthly_budget_limit=req.monthly_budget,
        total_estimated_cost=round(total_cost, 2),
        cost_exceeds_budget=bool(req.monthly_budget and total_cost > req.monthly_budget),
        components=components,
        educational_notes=[
            f"Configured for {req.environment_tier.upper()} tier with {compute.instance_type} compute and {database.instance_type} persistence.",
            "Multi-AZ failover and dual NAT gateways recommended for production reliability."
        ],
        remediation_steps=[]
    )

    rationale = (
        f"Recommended AWS topology tailored for {req.workload_type} in {req.target_region}. "
        f"Uses {compute.instance_type} instances scaled between {compute.min_instances} and {compute.max_instances} nodes, "
        f"with {database.instance_type} database in {ha_mode} mode."
    )

    alternatives = [
        {
            "name": "Serverless Container Tier (AWS Fargate)",
            "compute": "ECS Fargate",
            "delta_cost_pct": "+15%",
            "pros": "Zero server management, automatic scaling per task",
            "cons": "Slightly higher compute cost at baseline"
        },
        {
            "name": "Cost-Optimized Graviton (ARM64)",
            "compute": "t4g.medium / db.t4g.medium",
            "delta_cost_pct": "-20%",
            "pros": "20% better price-performance with Graviton2",
            "cons": "Requires multi-arch or ARM64 container builds"
        }
    ]

    return {
        "status": "SUCCESS",
        "project_id": req.project_id,
        "environment_id": req.environment_id,
        "profile": profile,
        "rationale": rationale,
        "alternatives": alternatives
    }
