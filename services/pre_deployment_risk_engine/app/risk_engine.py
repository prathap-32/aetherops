import hashlib
import time
import uuid
from typing import Dict, Any, List, Optional
from app.schemas import ResourceChange, RiskFinding, DeploymentPlanRequest, DeploymentPlanResponse

_PLANS: Dict[str, Dict[str, Any]] = {}

def evaluate_plan_risk(
    project_name: str,
    environment_tier: str,
    target_region: str,
    resource_changes: List[ResourceChange]
) -> Dict[str, Any]:
    env = (environment_tier or "development").lower()
    is_prod = "prod" in env
    findings: List[Dict[str, Any]] = []

    res_types = [rc.resource_type for rc in resource_changes]

    # 1. Cost & FinOps Analysis
    total_cost = 0.0
    cost_breakdown = {"compute": 0.0, "database": 0.0, "networking": 0.0, "storage": 0.0, "security": 0.0}

    for rc in resource_changes:
        rtype = rc.resource_type
        cnum = rc.cost_monthly_usd
        if cnum > 0.0:
            total_cost += cnum
            if "instance" in rtype or "ecs" in rtype:
                cost_breakdown["compute"] += cnum
            elif "db" in rtype or "rds" in rtype:
                cost_breakdown["database"] += cnum
            elif "lb" in rtype or "nat" in rtype:
                cost_breakdown["networking"] += cnum
            elif "s3" in rtype:
                cost_breakdown["storage"] += cnum
            else:
                cost_breakdown["security"] += cnum
        else:
            est = 0.0
            if rtype == "aws_instance":
                est = 24.50 if is_prod else 12.24
                cost_breakdown["compute"] += est
            elif rtype in ("aws_db_instance", "aws_rds_cluster"):
                est = 88.00 if is_prod else 17.50
                cost_breakdown["database"] += est
            elif rtype == "aws_lb":
                est = 16.50
                cost_breakdown["networking"] += est
            elif rtype == "aws_nat_gateway":
                est = 32.40
                cost_breakdown["networking"] += est
            elif rtype == "aws_s3_bucket":
                est = 4.50
                cost_breakdown["storage"] += est
            elif rtype == "aws_kms_key":
                est = 1.00
                cost_breakdown["security"] += est
            total_cost += est

    # 2. Security Analysis
    has_kms = any(rt in ("aws_kms_key", "aws_kms_alias") for rt in res_types)
    has_waf = any(rt in ("aws_wafv2_web_acl", "aws_shield_protection") for rt in res_types)

    if is_prod and not has_kms:
        findings.append({
            "id": "RISK-SEC-01",
            "category": "SECURITY",
            "severity": "CRITICAL",
            "title": "Missing Customer Managed KMS Key in Production",
            "explanation": "Zero-trust compliance mandates customer-managed KMS envelope encryption for data stores in production environments.",
            "affected_resource": f"{project_name}-kms-primary (absent)",
            "recommendation": "Provision an aws_kms_key resource with annual key rotation enabled and attach it to EBS/RDS/S3.",
            "is_blocking": True
        })

    # 3. SPOF Analysis
    has_single_db = any(rt == "aws_db_instance" for rt in res_types)
    if is_prod and has_single_db and not any(rt == "aws_rds_cluster" for rt in res_types):
        findings.append({
            "id": "RISK-SPOF-01",
            "category": "SPOF",
            "severity": "CRITICAL",
            "title": "Single AZ Relational Database in Production",
            "explanation": "Single-AZ database deployments cannot survive AWS data center disruptions.",
            "affected_resource": f"{project_name}-db-primary",
            "recommendation": "Enable Multi-AZ failover replication or migrate to Amazon Aurora.",
            "is_blocking": True
        })

    # 4. Destructive Change Detection
    destructive_changes = [rc for rc in resource_changes if rc.is_destructive or rc.action == "DELETE"]
    if destructive_changes:
        findings.append({
            "id": "RISK-DESTR-01",
            "category": "OPERATIONS",
            "severity": "HIGH",
            "title": f"Destructive Mutation Detected: {len(destructive_changes)} resource(s)",
            "explanation": "The plan contains mutations that will tear down existing infrastructure.",
            "affected_resource": ", ".join(rc.name for rc in destructive_changes),
            "recommendation": "Review plan diff carefully before approving execution.",
            "is_blocking": False
        })

    blocking_findings = [f for f in findings if f.get("is_blocking")]
    warning_findings = [f for f in findings if not f.get("is_blocking")]

    status = "BLOCKED" if blocking_findings else ("WARNING" if warning_findings else "PASS")

    scores = {
        "security": max(40, 100 - (sum(1 for f in findings if f["category"] == "SECURITY") * 25)),
        "spof": max(40, 100 - (sum(1 for f in findings if f["category"] == "SPOF") * 25)),
        "finops": 92,
        "performance": 95,
        "operations": 90,
        "sustainability": 95,
    }

    cost_summary = {
        "monthly_cost_usd": round(total_cost, 2),
        "currency": "USD",
        "breakdown": {k: round(v, 2) for k, v in cost_breakdown.items()},
        "unavailable_pricing_resources": []
    }

    complexity_assessment = {
        "total_resources": len(resource_changes),
        "mutation_types": {
            "create": sum(1 for rc in resource_changes if rc.action == "CREATE"),
            "update": sum(1 for rc in resource_changes if rc.action == "UPDATE"),
            "delete": sum(1 for rc in resource_changes if rc.action == "DELETE"),
        },
        "destructive_mutations": len(destructive_changes),
        "estimated_execution_seconds": max(30, len(resource_changes) * 12)
    }

    return {
        "status": status,
        "can_proceed": len(blocking_findings) == 0,
        "findings": findings,
        "blocking_count": len(blocking_findings),
        "warning_count": len(warning_findings),
        "pillar_scores": scores,
        "cost_summary": cost_summary,
        "complexity_assessment": complexity_assessment,
    }

def create_deployment_plan(req: DeploymentPlanRequest) -> DeploymentPlanResponse:
    if not req.project_name or req.project_name.lower() in ("aether-cloud", "default", "none", ""):
        raise ValueError("Project context required: Cannot run pre-deployment analysis without a valid project.")

    plan_id = f"plan_{uuid.uuid4().hex[:12]}"

    # Generate synthetic or parsed changes from request
    changes: List[ResourceChange] = [
        ResourceChange(
            action="CREATE",
            symbol="+",
            resource_type="aws_vpc",
            name=f"{req.project_name}-vpc",
            diff="cidr_block: 10.0.0.0/16",
            cost_monthly_usd=0.0
        ),
        ResourceChange(
            action="CREATE",
            symbol="+",
            resource_type="aws_subnet",
            name=f"{req.project_name}-subnet-public-1",
            diff="cidr_block: 10.0.1.0/24",
            cost_monthly_usd=0.0
        ),
        ResourceChange(
            action="CREATE",
            symbol="+",
            resource_type="aws_instance",
            name=f"{req.project_name}-app-server",
            diff="instance_type: t3.medium",
            cost_monthly_usd=30.37
        ),
        ResourceChange(
            action="CREATE",
            symbol="+",
            resource_type="aws_db_instance",
            name=f"{req.project_name}-postgres-db",
            diff="instance_class: db.t3.medium",
            cost_monthly_usd=49.64
        )
    ]

    # Calculate plan hash
    plan_content = f"{req.project_name}_{req.target_region}_{req.environment_tier}_{len(changes)}"
    plan_hash = hashlib.sha256(plan_content.encode("utf-8")).hexdigest()

    risk_assessment = evaluate_plan_risk(
        project_name=req.project_name,
        environment_tier=req.environment_tier,
        target_region=req.target_region,
        resource_changes=changes
    )

    plan_record = {
        "plan_id": plan_id,
        "project_name": req.project_name,
        "target_region": req.target_region,
        "environment_tier": req.environment_tier,
        "tenant_id": req.tenant_id or "ten_default",
        "plan_hash": plan_hash,
        "changes": [c.model_dump() for c in changes],
        "risk_assessment": risk_assessment,
        "cost_summary": risk_assessment["cost_summary"],
        "complexity_assessment": risk_assessment["complexity_assessment"],
        "can_proceed": risk_assessment["can_proceed"],
        "created_at": time.time()
    }

    _PLANS[plan_id] = plan_record

    return DeploymentPlanResponse(
        plan_id=plan_id,
        project_name=req.project_name,
        target_region=req.target_region,
        environment_tier=req.environment_tier,
        plan_hash=plan_hash,
        changes=changes,
        risk_assessment=risk_assessment,
        cost_summary=risk_assessment["cost_summary"],
        complexity_assessment=risk_assessment["complexity_assessment"],
        can_proceed=risk_assessment["can_proceed"]
    )
