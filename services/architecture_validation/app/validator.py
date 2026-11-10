from typing import Dict, Any, List, Optional
from app.schemas import ValidationFinding, ArchitectureValidationRequest, ArchitectureValidationResponse

SUPPORTED_AWS_RESOURCE_TYPES = {
    "internet", "route53", "cloudfront", "alb", "elastic_ip", "api_gateway",
    "vpc", "subnet_public", "subnet_private", "nat_gateway", "internet_gateway",
    "ec2", "ecs", "fargate", "lambda", "eks", "autoscaling_group",
    "rds", "aurora", "dynamodb", "elasticache", "documentdb",
    "s3", "ebs", "efs",
    "kms", "waf", "secrets_manager", "iam_role", "security_group",
    "cloudwatch", "sns", "sqs", "opentelemetry"
}

def validate_architecture(req: ArchitectureValidationRequest) -> ArchitectureValidationResponse:
    env = (req.environment_tier or "development").lower()
    is_prod = "prod" in env
    is_staging = "stag" in env

    findings: List[ValidationFinding] = []
    uncertainties: List[str] = []

    nodes = req.nodes
    edges = req.edges
    node_map = {n.get("id"): n for n in nodes}
    node_types = set()

    for n in nodes:
        rtype = (
            n.get("resource_type")
            or n.get("type")
            or n.get("data", {}).get("resource_type")
            or n.get("serviceType")
            or "unknown"
        ).lower()
        node_types.add(rtype)

    # 1. Ingress Layer Check
    has_ingress = any(t in node_types for t in ["internet", "alb", "elastic_ip", "cloudfront", "api_gateway"])
    if not has_ingress and len(nodes) > 0:
        findings.append(ValidationFinding(
            id="VAL-INGRESS-01",
            category="ARCHITECTURE",
            severity="CRITICAL",
            title="Missing Ingress Layer",
            explanation="No public ingress entrypoint (ALB, CloudFront, API Gateway, or Elastic IP) is configured.",
            evidence=f"{len(nodes)} nodes present; zero ingress resources detected.",
            affected_resources=["topology"],
            recommended_correction="Add an Application Load Balancer or CloudFront distribution for user traffic.",
            is_blocking=True
        ))

    # 2. Compute Runtime Check
    has_compute = any(t in node_types for t in ["ec2", "ecs", "fargate", "lambda", "eks", "autoscaling_group"])
    if not has_compute and len(nodes) > 0:
        findings.append(ValidationFinding(
            id="VAL-COMPUTE-01",
            category="ARCHITECTURE",
            severity="CRITICAL",
            title="Missing Compute Runtime",
            explanation="No server or container execution runtime is configured to execute workload code.",
            evidence=f"{len(nodes)} nodes present; zero compute resources detected.",
            affected_resources=["topology"],
            recommended_correction="Add an Amazon EC2, ECS Fargate, or AWS Lambda compute runtime.",
            is_blocking=True
        ))

    # 3. Production Multi-AZ & Resilience
    if is_prod:
        has_asg = "autoscaling_group" in node_types or any("asg" in str(n.get("id")).lower() for n in nodes)
        has_ha_db = any(t in node_types for t in ["aurora", "dynamodb"]) or any(
            n.get("data", {}).get("multi_az") is True for n in nodes if "rds" in (n.get("resource_type") or "")
        )
        if not has_asg and has_compute:
            findings.append(ValidationFinding(
                id="VAL-PROD-HA-01",
                category="RESILIENCE",
                severity="HIGH",
                title="Production Compute Lacks Auto Scaling Group",
                explanation="Standalone compute in production risks outage during instance failure or traffic surges.",
                evidence="No AutoScalingGroup or multi-instance group detected in production topology.",
                affected_resources=["compute"],
                recommended_correction="Enable Auto Scaling with minimum 2 instances across multiple Availability Zones.",
                is_blocking=False
            ))

    # 4. Unknown Resource Compatibility
    for n in nodes:
        rtype = (
            n.get("resource_type")
            or n.get("type")
            or n.get("data", {}).get("resource_type")
            or "unknown"
        ).lower()
        if rtype not in SUPPORTED_AWS_RESOURCE_TYPES and rtype not in ("customnode", "default", "input", "output"):
            findings.append(ValidationFinding(
                id=f"VAL-COMPAT-{n.get('id', 'unk')}",
                category="COMPATIBILITY",
                severity="MEDIUM",
                title=f"Unrecognized AWS Resource Type: {rtype}",
                explanation=f"Resource '{n.get('id')}' specifies an unvalidated resource type '{rtype}'.",
                evidence=f"Resource ID: {n.get('id')}, type: {rtype}",
                affected_resources=[str(n.get("id"))],
                recommended_correction="Select a valid AWS resource type from the AetherOps catalog.",
                is_blocking=False
            ))

    blocking_count = sum(1 for f in findings if f.is_blocking)
    warning_count = sum(1 for f in findings if not f.is_blocking)

    status = "BLOCKED" if blocking_count > 0 else ("WARNING" if warning_count > 0 else "PASS")
    can_proceed = blocking_count == 0

    pillars = {
        "security": 100 - (sum(1 for f in findings if f.category == "SECURITY") * 20),
        "reliability": 100 - (sum(1 for f in findings if f.category in ("RESILIENCE", "ARCHITECTURE")) * 20),
        "cost_optimization": 95,
        "operational_excellence": 90,
        "performance_efficiency": 90,
        "sustainability": 95,
    }

    return ArchitectureValidationResponse(
        status=status,
        blocking_count=blocking_count,
        warning_count=warning_count,
        findings=findings,
        uncertainties=uncertainties,
        pillars=pillars,
        can_proceed_to_iac=can_proceed
    )
