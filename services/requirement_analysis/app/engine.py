# services/requirement_analysis/app/engine.py
import math
from typing import List, Tuple, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EC2Catalog, RDSCatalog, GenericServiceCatalog
from app.cache import cache_manager
from app.catalog import STORAGE_PRICING, NETWORK_PRICING
from app.ai_advisor import generate_ai_architecture_advice
from app.schemas import (
    RequirementInput,
    RequirementProfileOutput,
    ArchitectureComponents,
    ComputeRecommendation,
    DatabaseRecommendation,
    RecommendationInput,
    RecommendationOutput,
    NetworkingRecommendation,
    StorageRecommendation,
    SecurityRecommendation,
    OperationsRecommendation,
    MonitoringRecommendation
)

# Dynamic class adaptors to support dot-notation matching static models
class DynamicEC2Spec:
    def __init__(self, data: dict):
        self.instance_type = data["instance_type"]
        self.vcpus = data["vcpus"]
        self.ram_gb = data["ram_gb"]
        self.price_per_hour = data["price_per_hour"]
        self.network_performance = data["network_performance"]
        self.category = data["category"]

class DynamicRDSSpec:
    def __init__(self, data: dict):
        self.instance_type = data["instance_type"]
        self.vcpus = data["vcpus"]
        self.ram_gb = data["ram_gb"]
        self.price_per_hour = data["price_per_hour"]
        self.category = data["category"]

async def get_cheapest_ec2_matching_db(
    session: AsyncSession,
    min_vcpus: int,
    min_ram_gb: float,
    category_preference: Optional[str] = None
) -> Optional[DynamicEC2Spec]:
    """
    Finds the cheapest EC2 instance satisfying constraints using Cache-Aside (Redis -> DB -> Fallback).
    """
    cache_key = f"catalog:ec2:vcpu_{min_vcpus}:ram_{min_ram_gb}:cat_{category_preference or 'any'}"
    cached_data = await cache_manager.get_json(cache_key)
    if cached_data is not None:
        return DynamicEC2Spec(cached_data)

    # Query DB
    query = select(EC2Catalog).where(
        EC2Catalog.vcpus >= min_vcpus,
        EC2Catalog.ram_gb >= min_ram_gb
    )
    result = await session.execute(query)
    candidates = result.scalars().all()

    if not candidates:
        # Fallback to static catalog if DB is empty/unseeded
        from app.catalog import get_cheapest_ec2_matching
        fallback = get_cheapest_ec2_matching(min_vcpus, min_ram_gb, category_preference)
        if fallback:
            return DynamicEC2Spec(fallback.model_dump())
        return None

    best_candidate = None
    if category_preference:
        pref_candidates = [c for c in candidates if c.category == category_preference]
        if pref_candidates:
            best_candidate = min(pref_candidates, key=lambda x: x.price_per_hour)
        else:
            # Try static catalog fallback for preferred category
            from app.catalog import get_cheapest_ec2_matching
            fallback = get_cheapest_ec2_matching(min_vcpus, min_ram_gb, category_preference)
            if fallback:
                res_dict = fallback.model_dump()
                await cache_manager.set_json(cache_key, res_dict, expire_seconds=3600)
                return DynamicEC2Spec(res_dict)

    if best_candidate is None:
        best_candidate = min(candidates, key=lambda x: x.price_per_hour)

    res_dict = best_candidate.to_dict()
    # Cache result
    await cache_manager.set_json(cache_key, res_dict, expire_seconds=3600)
    return DynamicEC2Spec(res_dict)

async def get_cheapest_rds_matching_db(
    session: AsyncSession,
    min_vcpus: int,
    min_ram_gb: float,
    category_preference: Optional[str] = None
) -> Optional[DynamicRDSSpec]:
    """
    Finds the cheapest RDS instance satisfying constraints using Cache-Aside (Redis -> DB -> Fallback).
    """
    cache_key = f"catalog:rds:vcpu_{min_vcpus}:ram_{min_ram_gb}:cat_{category_preference or 'any'}"
    cached_data = await cache_manager.get_json(cache_key)
    if cached_data is not None:
        return DynamicRDSSpec(cached_data)

    # Query DB
    query = select(RDSCatalog).where(
        RDSCatalog.vcpus >= min_vcpus,
        RDSCatalog.ram_gb >= min_ram_gb
    )
    result = await session.execute(query)
    candidates = result.scalars().all()

    if not candidates:
        # Fallback to static catalog if DB is empty/unseeded
        from app.catalog import get_cheapest_rds_matching
        fallback = get_cheapest_rds_matching(min_vcpus, min_ram_gb, category_preference)
        if fallback:
            return DynamicRDSSpec(fallback.model_dump())
        return None

    best_candidate = None
    if category_preference:
        pref_candidates = [c for c in candidates if c.category == category_preference]
        if pref_candidates:
            best_candidate = min(pref_candidates, key=lambda x: x.price_per_hour)
        else:
            # Try static catalog fallback for preferred category
            from app.catalog import get_cheapest_rds_matching
            fallback = get_cheapest_rds_matching(min_vcpus, min_ram_gb, category_preference)
            if fallback:
                res_dict = fallback.model_dump()
                await cache_manager.set_json(cache_key, res_dict, expire_seconds=3600)
                return DynamicRDSSpec(res_dict)

    if best_candidate is None:
        best_candidate = min(candidates, key=lambda x: x.price_per_hour)

    res_dict = best_candidate.to_dict()
    # Cache result
    await cache_manager.set_json(cache_key, res_dict, expire_seconds=3600)
    return DynamicRDSSpec(res_dict)

def calculate_compute_needs(
    rps: float,
    peak_multiplier: float,
    workload_type: str
) -> Tuple[int, float]:
    """
    Calculates the minimum vCPU and RAM requirements based on workload type and peak RPS.
    Returns: (required_vcpus, required_ram_gb)
    """
    rps_per_vcpu = {
        "web": 100.0,
        "api": 150.0,
        "database": 50.0,
        "cache": 500.0,
        "batch": 10.0,
        "hybrid": 80.0
    }.get(workload_type, 100.0)

    ram_per_vcpu = {
        "web": 2.0,
        "api": 2.0,
        "database": 4.0,
        "cache": 4.0,
        "batch": 4.0,
        "hybrid": 3.0
    }.get(workload_type, 2.0)

    peak_rps = rps * peak_multiplier
    required_vcpus = max(1, math.ceil(peak_rps / rps_per_vcpu))
    required_ram_gb = float(required_vcpus * ram_per_vcpu)

    return required_vcpus, required_ram_gb

async def analyze_requirements(inputs: RequirementInput, session: AsyncSession) -> RequirementProfileOutput:
    """
    Refactored engine: maps beginner layman parameters to strict AWS configurations.
    """
    educational_notes: List[str] = []
    remediation_steps: List[str] = []

    # 1. Translate Traffic Scale to RPS & Peak Multipliers
    if inputs.traffic_scale == "hobby_dev":
        rps = 1.0
        peak_multiplier = 1.0
        educational_notes.append("Traffic Scale: Configured for low-volume hobby/testing workload (1 RPS average).")
    elif inputs.traffic_scale == "growth":
        rps = 30.0
        peak_multiplier = 1.5
        educational_notes.append("Traffic Scale: Configured for mid-tier growth workload (30 RPS, peaking up to 45 RPS).")
    else: # production
        rps = 200.0
        peak_multiplier = 2.0
        educational_notes.append("Traffic Scale: Configured for high-volume production scale (200 RPS, peaking up to 400 RPS).")

    # 2. Translate Reliability Level to SLA & High Availability Modes
    if inputs.reliability == "dev_testing":
        sla = 95.0
        ha_mode = "none"
        tier = "Developer"
        educational_notes.append("Reliability: Budget-oriented single instance setup selected (no automated failover).")
    elif inputs.reliability == "production_safe":
        sla = 99.9
        ha_mode = "multi-az"
        tier = "Production-Standard"
        educational_notes.append("Reliability: Production-safe multi-AZ layout enabled (recovers automatically if one AZ goes offline).")
    else: # mission_critical
        sla = 99.99
        ha_mode = "multi-region"
        tier = "Enterprise-HA"
        educational_notes.append("Reliability: Mission-critical multi-region setup enabled (resilient to entire region outages).")

    # 3. Translate Security Needs to Compliance Frameworks
    compliance_list: List[str] = []
    if inputs.security_need == "healthcare":
        compliance_list = ["HIPAA", "SOC2"]
        educational_notes.append("Security: Healthcare profile activated. Applying HIPAA & SOC2 compliance policies.")
    elif inputs.security_need == "payment_processing":
        compliance_list = ["PCI-DSS", "GDPR"]
        educational_notes.append("Security: Payment Processing profile activated. Applying PCI-DSS & GDPR safety guards.")
    else:
        educational_notes.append("Security: Standard web security rules applied.")

    # 4. Process Specialized Streams
    ec2_category_preference = "general"
    if inputs.stream == "ai_ml":
        ec2_category_preference = "gpu"
        educational_notes.append("Stream: AI/ML workload detected. Selecting GPU-accelerated computing nodes (e.g., AWS EC2 g4dn series).")
    elif inputs.stream == "iot":
        educational_notes.append("Stream: IoT workload detected. Adding ingestion buffer advisory (AWS IoT Core + Amazon Kinesis).")
    elif inputs.stream == "devops_tooling":
        educational_notes.append("Stream: DevOps tooling deployment runner setup. Optimized for heavy building cached storage.")
    elif inputs.stream == "dev_sandbox":
        remediation_steps.append("Configure AWS Instance Scheduler to shut down sandbox servers outside work hours to save ~65% cost.")

    # 5. Compute sizing requirements
    has_compute = inputs.technology.backend != "none"
    if has_compute:
        req_vcpus, req_ram = calculate_compute_needs(rps, peak_multiplier, "api")
        
        if tier == "Enterprise-HA":
            min_instances = 4
            max_instances = 12
            target_cpu = 60
            ebs_gb = 100
            if ec2_category_preference != "gpu":
                ec2_category_preference = "compute"
        elif tier == "Production-Standard":
            min_instances = 2
            max_instances = 6
            target_cpu = 70
            ebs_gb = 50
        else: # Developer
            min_instances = 1
            max_instances = 2
            target_cpu = 80
            ebs_gb = 20
            if ec2_category_preference != "gpu":
                ec2_category_preference = "burstable"

        # Sizing calculations per node
        vcpu_per_instance = max(1, math.ceil(req_vcpus / min_instances))
        ram_per_instance = max(1.0, req_ram / min_instances)

        # Query catalog DB
        selected_ec2 = await get_cheapest_ec2_matching_db(session, vcpu_per_instance, ram_per_instance, ec2_category_preference)
        if not selected_ec2:
            selected_ec2 = await get_cheapest_ec2_matching_db(session, vcpu_per_instance, ram_per_instance)
        if not selected_ec2:
            selected_ec2 = DynamicEC2Spec({
                "instance_type": "t3.micro", "vcpus": 2, "ram_gb": 1.0, 
                "price_per_hour": 0.0104, "network_performance": "Up to 5 Gbps", "category": "burstable"
            })
    else:
        selected_ec2 = DynamicEC2Spec({
            "instance_type": "none", "vcpus": 0, "ram_gb": 0.0, 
            "price_per_hour": 0.0, "network_performance": "none", "category": "none"
        })
        min_instances = 0
        max_instances = 0
        target_cpu = 0
        ebs_gb = 0

    # 6. Database sizing requirements
    has_db = inputs.technology.database != "none"
    if has_db:
        db_multi_az = ha_mode in ["multi-az", "multi-region"]
        db_replica_count = 1 if ha_mode == "multi-region" else 0

        if tier == "Enterprise-HA":
            db_category = "memory"
            db_min_vcpu = 4
            db_min_ram = 16.0
        elif tier == "Production-Standard":
            db_category = "standard"
            db_min_vcpu = 2
            db_min_ram = 8.0
        else:
            db_category = "burstable"
            db_min_vcpu = 2
            db_min_ram = 2.0

        selected_rds = await get_cheapest_rds_matching_db(session, db_min_vcpu, db_min_ram, db_category)
        if not selected_rds:
            selected_rds = await get_cheapest_rds_matching_db(session, db_min_vcpu, db_min_ram)
        if not selected_rds:
            selected_rds = DynamicRDSSpec({
                "instance_type": "db.t4g.micro", "vcpus": 2, "ram_gb": 1.0,
                "price_per_hour": 0.016, "category": "burstable"
            })
        db_storage_gb = max(20, math.ceil(inputs.data_storage_gb * 1.5))
    else:
        selected_rds = DynamicRDSSpec({
            "instance_type": "none", "vcpus": 0, "ram_gb": 0.0,
            "price_per_hour": 0.0, "category": "none"
        })
        db_multi_az = False
        db_replica_count = 0
        db_storage_gb = 0

    # 7. Calculate costs
    ec2_cost = selected_ec2.price_per_hour * 730.0 * min_instances if has_compute else 0.0

    if has_db:
        rds_instance_multiplier = 2.0 if db_multi_az else 1.0
        rds_instance_cost = selected_rds.price_per_hour * 730.0 * rds_instance_multiplier * (1 + db_replica_count)
        rds_storage_cost = db_storage_gb * STORAGE_PRICING["rds_gp3_gb_per_month"] * rds_instance_multiplier
        rds_backup_cost = 7 * 0.01 * db_storage_gb  # assume 7 retention days
        total_rds_cost = rds_instance_cost + rds_storage_cost + rds_backup_cost
    else:
        total_rds_cost = 0.0

    # Networking:
    has_alb = min_instances > 1 or tier in ["Production-Standard", "Enterprise-HA"]
    alb_cost = NETWORK_PRICING["alb_per_hour"] * 730.0 if has_alb else 0.0

    if tier == "Enterprise-HA":
        nat_gw_count = 2
    elif tier == "Production-Standard":
        nat_gw_count = 1
    else:
        nat_gw_count = 0
    nat_gw_cost = nat_gw_count * NETWORK_PRICING["nat_gateway_per_hour"] * 730.0

    # Static site hosting option
    is_static_only = inputs.technology.frontend != "none" and inputs.technology.backend == "none"
    has_cloudfront = is_static_only or inputs.technology.frontend == "react_vue_angular" or tier == "Enterprise-HA"
    cf_cost = max(5.0, rps * 0.05) if has_cloudfront else 0.0

    data_transfer_gb = rps * 0.00002 * 3600 * 730 
    data_transfer_cost = data_transfer_gb * NETWORK_PRICING["data_transfer_out_per_gb"]
    total_net_cost = alb_cost + nat_gw_cost + cf_cost + data_transfer_cost

    # Storage (S3 & EBS)
    ebs_cost = ebs_gb * min_instances * STORAGE_PRICING["ebs_gp3_gb_per_month"] if has_compute else 0.0
    has_s3 = len(compliance_list) > 0 or is_static_only or inputs.technology.frontend != "none"
    s3_gb = max(50, math.ceil(inputs.data_storage_gb * 2.0)) if has_s3 else 0
    s3_cost = s3_gb * STORAGE_PRICING["s3_standard_gb_per_month"] if has_s3 else 0.0
    total_storage_cost = ebs_cost + s3_cost

    # Security details
    encryption_enabled = len(compliance_list) > 0 or tier in ["Production-Standard", "Enterprise-HA"]
    iam_audit_required = len(compliance_list) > 0 or tier == "Enterprise-HA"
    waf_enabled = inputs.security_need in ["healthcare", "payment_processing"] or tier == "Enterprise-HA"
    kms_key_rotation = len(compliance_list) > 0

    total_cost = ec2_cost + total_rds_cost + total_net_cost + total_storage_cost

    # 8. Budget Optimization Loop
    if inputs.monthly_budget and total_cost > inputs.monthly_budget:
        # Scale compute down to cheaper burstable classes
        if has_compute and selected_ec2.instance_type not in ["t3.micro", "t3.small"]:
            cheaper_ec2 = await get_cheapest_ec2_matching_db(session, max(1, vcpu_per_instance - 1), max(1.0, ram_per_instance / 2), "burstable")
            if cheaper_ec2 and cheaper_ec2.price_per_hour < selected_ec2.price_per_hour:
                selected_ec2 = cheaper_ec2
                ec2_cost = selected_ec2.price_per_hour * 730.0 * min_instances
                educational_notes.append("Optimized: Downgraded compute instance type to burstable class to fit budget.")

        # Scale database down to cheaper burstable classes
        if has_db and selected_rds.instance_type not in ["db.t4g.micro", "db.t4g.small"]:
            cheaper_rds = await get_cheapest_rds_matching_db(session, max(1, db_min_vcpu - 1), max(1.0, db_min_ram / 2), "burstable")
            if cheaper_rds and cheaper_rds.price_per_hour < selected_rds.price_per_hour:
                selected_rds = cheaper_rds
                rds_cost = selected_rds.price_per_hour * 730.0 * rds_instance_multiplier * (1 + db_replica_count)
                total_rds_cost = rds_cost + rds_storage_cost + rds_backup_cost
                educational_notes.append("Optimized: Downgraded database instance type to burstable class to fit budget.")

        # Scale down NAT Gateways
        if nat_gw_count > 1:
            nat_gw_count = 1
            nat_gw_cost = nat_gw_count * NETWORK_PRICING["nat_gateway_per_hour"] * 730.0
            total_net_cost = alb_cost + nat_gw_cost + cf_cost + data_transfer_cost
            educational_notes.append("Optimized: Reduced NAT Gateway count to 1 to cut egress gateway charges.")

        total_cost = ec2_cost + total_rds_cost + total_net_cost + total_storage_cost

    cost_exceeds_budget = False
    if inputs.monthly_budget and total_cost > inputs.monthly_budget:
        cost_exceeds_budget = True
        remediation_steps.append("Increase your monthly budget limit or scale down your expectations on reliability / scale.")
        remediation_steps.append("Host frontend and backend as serverless assets (AWS Lambda) which minimizes baseline VM expenses.")

    if not encryption_enabled:
        remediation_steps.append("Enable database and volume encryption to guard system data and prepare for security reviews.")
    if not waf_enabled and tier != "Developer":
        remediation_steps.append("Deploy AWS WAF to secure your Application Load Balancer from cross-site scripts and SQL injection.")
    if ha_mode == "none":
        remediation_steps.append("Scale your compute nodes to 2 instances across separate AZs to protect the app from local hardware crashes.")

    # 9. Formulate Operations recommendations
    ops_files = []
    if inputs.operations.container_orchestration == "kubernetes":
        ops_files += ["deployment.yaml", "service.yaml", "ingress.yaml"]
    elif inputs.operations.container_orchestration == "docker_compose":
        ops_files += ["docker-compose.yml", "Dockerfile"]
    elif inputs.operations.container_orchestration == "ecs_fargate":
        ops_files += ["task-definition.json", "ecs-service.tf"]
    elif inputs.operations.container_orchestration == "eks":
        ops_files += ["deployment.yaml", "service.yaml", "eks-cluster.tf"]

    if inputs.operations.infrastructure_as_code == "terraform":
        ops_files += ["main.tf", "variables.tf", "outputs.tf"]
        
    if inputs.operations.configuration_management == "ansible":
        ops_files += ["playbook.yml", "hosts.ini"]

    if inputs.operations.ci_cd_pipeline == "github_actions":
        ops_files += [".github/workflows/deploy.yml"]
    elif inputs.operations.ci_cd_pipeline == "jenkins":
        ops_files += ["Jenkinsfile"]

    ops_rec = OperationsRecommendation(
        orchestration_tool=inputs.operations.container_orchestration,
        iac_tool=inputs.operations.infrastructure_as_code,
        config_tool=inputs.operations.configuration_management,
        ci_cd_tool=inputs.operations.ci_cd_pipeline,
        files_to_generate=ops_files
    )

    # 10. Formulate Monitoring recommendations
    mon_tools = []
    if inputs.monitoring.level == "basic":
        mon_tools += ["Amazon CloudWatch Metrics", "CloudWatch Alarms"]
    elif inputs.monitoring.level == "advanced":
        mon_tools += ["Prometheus Server", "Grafana Dashboard", "CloudWatch Logs Agent", "AWS X-Ray Daemon"]

    if inputs.monitoring.alerting_channel == "slack_webhook":
        mon_tools += ["AWS Chatbot integration", "Slack Webhook Channel"]
    elif inputs.monitoring.alerting_channel == "email":
        mon_tools += ["Amazon SNS Topic", "Email Subscription"]

    mon_rec = MonitoringRecommendation(
        level=inputs.monitoring.level,
        alerting_channel=inputs.monitoring.alerting_channel,
        tools_to_deploy=mon_tools
    )

    components = ArchitectureComponents(
        compute=ComputeRecommendation(
            instance_type=selected_ec2.instance_type,
            vcpus=selected_ec2.vcpus,
            ram_gb=selected_ec2.ram_gb,
            min_instances=min_instances,
            max_instances=max_instances,
            target_cpu_utilization=target_cpu,
            has_autoscaling=max_instances > min_instances,
            monthly_cost=round(ec2_cost, 2)
        ),
        database=DatabaseRecommendation(
            instance_type=selected_rds.instance_type,
            vcpus=selected_rds.vcpus,
            ram_gb=selected_rds.ram_gb,
            storage_gb=db_storage_gb,
            storage_type="gp3" if has_db else "none",
            multi_az=db_multi_az,
            replica_count=db_replica_count,
            backup_retention_days=7 if has_db else 0,
            monthly_cost=round(total_rds_cost, 2)
        ),
        networking=NetworkingRecommendation(
            has_alb=has_alb,
            nat_gateway_count=nat_gw_count,
            has_cloudfront=has_cloudfront,
            monthly_cost=round(total_net_cost, 2)
        ),
        storage=StorageRecommendation(
            s3_gb=s3_gb,
            s3_class="STANDARD" if s3_gb > 0 else "NONE",
            ebs_gb_per_instance=ebs_gb,
            monthly_cost=round(total_storage_cost, 2)
        ),
        security=SecurityRecommendation(
            encryption_enabled=encryption_enabled,
            iam_audit_required=iam_audit_required,
            waf_enabled=waf_enabled,
            kms_key_rotation=kms_key_rotation
        ),
        operations=ops_rec,
        monitoring=mon_rec
    )

    return RequirementProfileOutput(
        architecture_tier=tier,
        high_availability_mode=ha_mode,
        compliance_applied=compliance_list,
        monthly_budget_limit=inputs.monthly_budget,
        total_estimated_cost=round(total_cost, 2),
        cost_exceeds_budget=cost_exceeds_budget,
        components=components,
        educational_notes=educational_notes,
        remediation_steps=remediation_steps
    )

async def recommend_infrastructure(inputs: RecommendationInput, session: AsyncSession) -> RecommendationOutput:
    # 1. Translate traffic_scale to instance requirements
    if inputs.traffic_scale == "low":
        min_vcpus, min_ram = 1, 2.0
        ec2_category = "burstable"
        node_count = 1
        db_instances = 1  # Single-AZ
        estimated_data_transfer = 10.0
        ebs_size = 20
    elif inputs.traffic_scale == "medium":
        min_vcpus, min_ram = 2, 8.0
        ec2_category = "general"
        node_count = 2
        db_instances = 2  # Multi-AZ (2x)
        estimated_data_transfer = 100.0
        ebs_size = 50
    else:  # high
        min_vcpus, min_ram = 4, 16.0
        ec2_category = "gpu" if inputs.tech_stack == "ai_ml" else "compute"
        node_count = 3
        db_instances = 3  # Multi-AZ + 1 replica (3x)
        estimated_data_transfer = 500.0
        ebs_size = 100

    # 2. Fetch cheapest matching EC2 instance from DB
    ec2_query = select(EC2Catalog).where(
        EC2Catalog.vcpus >= min_vcpus,
        EC2Catalog.ram_gb >= min_ram
    )
    result = await session.execute(ec2_query)
    candidates = result.scalars().all()
    
    # Filter by category preference if possible
    pref_candidates = [c for c in candidates if c.category == ec2_category]
    if pref_candidates:
        selected_ec2 = min(pref_candidates, key=lambda x: x.price_per_hour)
    elif candidates:
        selected_ec2 = min(candidates, key=lambda x: x.price_per_hour)
    else:
        # Static fallback if DB is completely unseeded
        selected_ec2 = type('EC2', (object,), {
            "instance_type": "t3.medium", "vcpus": 2, "ram_gb": 4.0, 
            "price_per_hour": 0.0416, "network_performance": "Up to 5 Gbps", "category": "burstable"
        })()

    # 3. Fetch cheapest RDS instance from DB (if stack needs database)
    needs_db = inputs.tech_stack in ["web_api", "iot"]
    selected_rds = None
    if needs_db:
        # DB category mapping
        db_category = "burstable" if inputs.traffic_scale == "low" else ("standard" if inputs.traffic_scale == "medium" else "memory")
        db_min_vcpu = 2 if inputs.traffic_scale in ["low", "medium"] else 4
        db_min_ram = 2.0 if inputs.traffic_scale == "low" else (8.0 if inputs.traffic_scale == "medium" else 16.0)

        rds_query = select(RDSCatalog).where(
            RDSCatalog.vcpus >= db_min_vcpu,
            RDSCatalog.ram_gb >= db_min_ram
        )
        result = await session.execute(rds_query)
        candidates = result.scalars().all()
        pref_rds = [c for c in candidates if c.category == db_category]
        if pref_rds:
            selected_rds = min(pref_rds, key=lambda x: x.price_per_hour)
        elif candidates:
            selected_rds = min(candidates, key=lambda x: x.price_per_hour)
        else:
            selected_rds = type('RDS', (object,), {
                "instance_type": "db.t4g.micro", "vcpus": 2, "ram_gb": 1.0,
                "price_per_hour": 0.016, "category": "burstable"
            })()

    # 4. Fetch generic service rates from DB
    generic_query = select(GenericServiceCatalog)
    result = await session.execute(generic_query)
    generic_rates = {item.service: item.price_per_hour for item in result.scalars().all()}

    # Pricing helpers with static defaults matching standard reference
    s3_standard_rate = generic_rates.get("s3_standard_per_gb", 0.023)
    ebs_gp3_rate = generic_rates.get("ebs_gp3_per_gb", 0.08)
    nat_gw_rate = generic_rates.get("nat_gateway_per_hour", 0.045)
    data_transfer_rate = generic_rates.get("data_transfer_out_per_gb", 0.09)
    waf_acl_rate = generic_rates.get("waf_web_acl_monthly", 5.0)
    waf_rule_rate = generic_rates.get("waf_rule_monthly", 1.0)
    cw_alarm_rate = generic_rates.get("cloudwatch_alarm_monthly", 0.1)
    kms_key_rate = generic_rates.get("kms_key_monthly", 1.0)

    # 5. Perform cost calculations
    # Compute: hourly rate * 730 hours * nodes count
    compute_monthly = selected_ec2.price_per_hour * 730 * node_count
    
    # DB: (hourly rate * 730 * instances count) + (storage * ebs gp3 rate * instances count)
    db_monthly = 0.0
    if needs_db and selected_rds:
        db_instance_cost = selected_rds.price_per_hour * 730 * db_instances
        db_storage_cost = inputs.storage_size_gb * ebs_gp3_rate * db_instances
        db_monthly = db_instance_cost + db_storage_cost

    # Storage: EBS per node + S3 storage
    ebs_monthly = ebs_size * ebs_gp3_rate * node_count
    s3_monthly = inputs.storage_size_gb * s3_standard_rate
    storage_monthly = ebs_monthly + s3_monthly

    # Network: NAT Gateway + Data Transfer Out
    nat_gateways_count = 0
    if inputs.traffic_scale == "medium":
        nat_gateways_count = 1
    elif inputs.traffic_scale == "high":
        nat_gateways_count = 2
    nat_gw_monthly = nat_gateways_count * nat_gw_rate * 730
    transfer_monthly = estimated_data_transfer * data_transfer_rate
    network_monthly = nat_gw_monthly + transfer_monthly

    # Security/Monitoring: WAF + KMS + CloudWatch Alarms
    waf_monthly = 0.0
    if inputs.security_level == "enhanced":
        waf_monthly = waf_acl_rate
    elif inputs.security_level == "strict":
        waf_monthly = waf_acl_rate + 5 * waf_rule_rate
        
    kms_monthly = kms_key_rate if inputs.security_level == "strict" else 0.0
    cw_alarms_count = 0 if inputs.traffic_scale == "low" else 3
    cw_monthly = cw_alarms_count * cw_alarm_rate
    security_monitoring_monthly = waf_monthly + kms_monthly + cw_monthly

    total_monthly_cost = compute_monthly + db_monthly + storage_monthly + network_monthly + security_monitoring_monthly

    # 6. Budget validation and optimization loop
    budget_status = "UNLIMITED"
    if inputs.monthly_max_budget is not None:
        budget_status = "WITHIN_BUDGET"
        if total_monthly_cost > inputs.monthly_max_budget:
            # Optimization 1: Downgrade EC2 to burstable class if not already
            if selected_ec2.category != "burstable":
                # Find burstable candidates
                burstable_candidates = [c for c in candidates if c.category == "burstable"]
                if burstable_candidates:
                    selected_ec2 = min(burstable_candidates, key=lambda x: x.price_per_hour)
                    compute_monthly = selected_ec2.price_per_hour * 730 * node_count
                    total_monthly_cost = compute_monthly + db_monthly + storage_monthly + network_monthly + security_monitoring_monthly

            # Optimization 2: Downgrade RDS database if budget still exceeded
            if total_monthly_cost > inputs.monthly_max_budget and needs_db and selected_rds:
                if selected_rds.category != "burstable":
                    rds_burstable_candidates = [c for c in candidates if hasattr(c, 'category') and c.category == "burstable"]
                    if rds_burstable_candidates:
                        selected_rds = min(rds_burstable_candidates, key=lambda x: x.price_per_hour)
                        db_instance_cost = selected_rds.price_per_hour * 730 * db_instances
                        db_storage_cost = inputs.storage_size_gb * ebs_gp3_rate * db_instances
                        db_monthly = db_instance_cost + db_storage_cost
                        total_monthly_cost = compute_monthly + db_monthly + storage_monthly + network_monthly + security_monitoring_monthly

            # Optimization 3: Reduce NAT Gateways
            if total_monthly_cost > inputs.monthly_max_budget and nat_gateways_count > 1:
                nat_gateways_count = 1
                nat_gw_monthly = nat_gateways_count * nat_gw_rate * 730
                network_monthly = nat_gw_monthly + transfer_monthly
                total_monthly_cost = compute_monthly + db_monthly + storage_monthly + network_monthly + security_monitoring_monthly

            # Check final status
            if total_monthly_cost > inputs.monthly_max_budget:
                budget_status = "EXCEEDED"

    cost_breakdown = {
        "compute": round(compute_monthly, 2),
        "database": round(db_monthly, 2),
        "storage": round(storage_monthly, 2),
        "networking": round(network_monthly, 2),
        "security_monitoring": round(security_monitoring_monthly, 2)
    }

    recommended_resources = {
        "compute": {
            "instance_type": selected_ec2.instance_type,
            "vcpus": selected_ec2.vcpus,
            "ram_gb": selected_ec2.ram_gb,
            "nodes_count": node_count,
            "network_performance": getattr(selected_ec2, "network_performance", "Up to 5 Gbps")
        },
        "database": {
            "instance_type": selected_rds.instance_type if selected_rds else "none",
            "vcpus": selected_rds.vcpus if selected_rds else 0,
            "ram_gb": selected_rds.ram_gb if selected_rds else 0,
            "instances_count": db_instances if needs_db else 0,
            "storage_gb": inputs.storage_size_gb if needs_db else 0
        } if needs_db else None,
        "storage": {
            "ebs_gb_per_node": ebs_size,
            "s3_gb": inputs.storage_size_gb
        },
        "networking": {
            "nat_gateways_count": nat_gateways_count,
            "estimated_data_transfer_gb": estimated_data_transfer
        },
        "security_monitoring": {
            "waf_enabled": inputs.security_level in ["enhanced", "strict"],
            "kms_enabled": inputs.security_level == "strict",
            "cloudwatch_alarms_count": cw_alarms_count
        }
    }

    return RecommendationOutput(
        region=inputs.region,
        tech_stack=inputs.tech_stack,
        traffic_scale=inputs.traffic_scale,
        budget_status=budget_status,
        monthly_budget_limit=inputs.monthly_max_budget,
        total_monthly_cost=round(total_monthly_cost, 2),
        cost_breakdown=cost_breakdown,
        recommended_resources=recommended_resources
    )


def generate_service_rationales(inputs: RequirementInput, profile: RequirementProfileOutput) -> dict:
    """
    Synthesizes deep architectural justification ('Why That Service') for each recommended AWS service.
    """
    comp = profile.components
    compute = comp.compute
    db = comp.database
    net = comp.networking
    storage = comp.storage
    sec = comp.security
    ops = comp.operations
    mon = comp.monitoring

    # 1. Compute Rationale
    inst_type = compute.instance_type
    is_arm = "t4g" in inst_type or "c7g" in inst_type or "m7g" in inst_type or "g5g" in inst_type
    arch_note = "ARM64 Graviton architecture selected for 40% superior price-performance ratio over legacy x86." if is_arm else "Standard x86 compute node selected to support broad binary compatibility."
    
    if inputs.traffic_scale == "hobby_dev":
        traffic_exp = f"Burstable instance ({inst_type}) ideal for dev/hobby traffic (1 RPS baseline), leveraging accumulated CPU credits for intermittent bursts without paying for idle capacity."
    elif inputs.traffic_scale == "growth":
        traffic_exp = f"Right-sized for mid-scale growth (30-45 RPS) with {compute.min_instances} instances to guarantee zero-downtime rolling deployments."
    else:
        traffic_exp = f"High-capacity production fleet ({compute.min_instances}-{compute.max_instances} instances) with automated horizontal scaling triggered when CPU utilization crosses {compute.target_cpu_utilization}%."

    compute_why = (
        f"Selected Amazon EC2 {inst_type} ({compute.vcpus} vCPU, {compute.ram_gb} GB RAM). {arch_note} "
        f"{traffic_exp} Redundancy: Min {compute.min_instances} nodes spread across multiple Availability Zones."
    )

    # 2. Database Rationale
    if inputs.technology.database != "none":
        db_engine = "PostgreSQL" if inputs.technology.database == "postgresql" else "MySQL"
        ha_exp = (
            f"Multi-AZ synchronous replication enabled to ensure instant automated failover within 60s without data loss."
            if db.multi_az else
            "Single-AZ deployment selected to minimize monthly spend for non-mission-critical workloads."
        )
        db_why = (
            f"Provisioned Amazon RDS {db_engine} on {db.instance_type} ({db.vcpus} vCPU, {db.ram_gb} GB RAM, {db.storage_gb} GB {db.storage_type}). "
            f"{ha_exp} Automated daily backups retained for {db.backup_retention_days} days to support point-in-time recovery (PITR)."
        )
    else:
        db_why = "No dedicated relational database requested in tech stack. Stateless or external storage assumed."

    # 3. Networking Rationale
    alb_exp = (
        "Application Load Balancer (ALB) terminates public SSL/TLS HTTPS certificates and dynamically balances traffic across healthy EC2 targets."
        if net.has_alb else
        "Direct elastic IP assignment without load balancer to preserve budget."
    )
    nat_exp = (
        f"{net.nat_gateway_count} NAT Gateway(s) deployed to give private subnets secure egress access for patching and third-party APIs while blocking inbound threats."
        if net.nat_gateway_count > 0 else
        "Instances co-located with public interfaces under security group perimeter."
    )
    cf_exp = " Amazon CloudFront CDN added to cache static assets globally at edge locations." if net.has_cloudfront else ""
    net_why = f"Amazon VPC configured with public and private subnet isolation. {alb_exp} {nat_exp}{cf_exp}"

    # 4. Storage Rationale
    s3_exp = f"Amazon S3 ({storage.s3_gb} GB {storage.s3_class}) provides 11 9's durability for backups, media, and unstructured assets." if storage.s3_gb > 0 else ""
    ebs_exp = f"Amazon EBS gp3 ({storage.ebs_gb_per_instance} GB/instance) delivers baseline 3,000 IOPS and 125 MB/s throughput independently of volume size, cutting EBS spend by 20% compared to gp2."
    storage_why = f"{ebs_exp} {s3_exp}".strip()

    # 5. Security Rationale
    waf_exp = "AWS WAF integrated at the ALB perimeter to guard against SQL injection, cross-site scripting (XSS), and bot scrapers." if sec.waf_enabled else "Security Groups enforce network-level port whitelisting."
    kms_exp = "AWS KMS Customer Master Keys (CMK) enforce hardware-backed AES-256 encryption at rest." if sec.encryption_enabled else "Standard AWS-managed encryption applied."
    comp_exp = f" Compliance framework applied: {', '.join(profile.compliance_applied)}." if profile.compliance_applied else ""
    sec_why = f"{kms_exp} {waf_exp}{comp_exp}"

    # 6. DevOps & Monitoring Rationale
    ops_why = (
        f"Orchestration via {ops.orchestration_tool.upper()} with Infrastructure as Code via {ops.iac_tool.title()}. "
        f"Deterministic, auditable deployments managed through {ops.ci_cd_tool.replace('_', ' ').title()}."
    )
    mon_why = (
        f"Amazon CloudWatch ({mon.level.title()} level) tracks CPU, memory saturation, and p95 request latency. "
        f"Alert notifications routed to {mon.alerting_channel.replace('_', ' ').title()}."
    )

    return {
        "compute": {
            "service_name": f"Amazon EC2 ({inst_type})",
            "category": "Compute & Capacity",
            "specs": f"{compute.vcpus} vCPUs • {compute.ram_gb} GB RAM • {compute.min_instances} Instances",
            "monthly_cost": compute.monthly_cost,
            "why": compute_why
        },
        "database": {
            "service_name": f"Amazon RDS ({db.instance_type})",
            "category": "Managed Relational Database",
            "specs": f"{db.vcpus} vCPUs • {db.ram_gb} GB RAM • {db.storage_gb} GB {db.storage_type} • Multi-AZ: {db.multi_az}",
            "monthly_cost": db.monthly_cost,
            "why": db_why
        },
        "networking": {
            "service_name": "Amazon VPC + ALB + NAT Gateway",
            "category": "Network Topology & Ingress",
            "specs": f"ALB: {net.has_alb} • NAT Gateways: {net.nat_gateway_count} • CloudFront: {net.has_cloudfront}",
            "monthly_cost": net.monthly_cost,
            "why": net_why
        },
        "storage": {
            "service_name": "Amazon EBS gp3 + Amazon S3",
            "category": "Persistent Block & Object Storage",
            "specs": f"EBS: {storage.ebs_gb_per_instance} GB/node • S3: {storage.s3_gb} GB ({storage.s3_class})",
            "monthly_cost": storage.monthly_cost,
            "why": storage_why
        },
        "security": {
            "service_name": "AWS IAM + AWS KMS + AWS WAF",
            "category": "Identity, Perimeter & Data Protection",
            "specs": f"WAF: {sec.waf_enabled} • KMS Rotation: {sec.kms_key_rotation} • Compliance: {', '.join(profile.compliance_applied) or 'Standard'}",
            "monthly_cost": 0.0 if not sec.waf_enabled else 25.0,
            "why": sec_why
        },
        "operations_monitoring": {
            "service_name": f"{ops.orchestration_tool.upper()} + Amazon CloudWatch",
            "category": "DevOps, IaC & Observability",
            "specs": f"IaC: {ops.iac_tool} • CI/CD: {ops.ci_cd_tool} • Alerts: {mon.alerting_channel}",
            "monthly_cost": 15.0 if mon.level == "advanced" else 0.0,
            "why": f"{ops_why} {mon_why}"
        }
    }


def generate_cost_optimizations(inputs: RequirementInput, profile: RequirementProfileOutput) -> list:
    """
    Generates tailored, actionable FinOps cost optimization opportunities based on the requirement profile.
    """
    optimizations = []
    comp = profile.components
    compute_cost = comp.compute.monthly_cost
    rds_cost = comp.database.monthly_cost
    nat_cost = comp.networking.nat_gateway_count * 32.85

    # 1. Savings Plans / Reserved Instances
    if compute_cost > 30.0:
        sp_savings = round(compute_cost * 0.34, 2)
        optimizations.append({
            "title": "Adopt 1-Year Compute Savings Plan",
            "category": "Compute FinOps",
            "estimated_monthly_savings": sp_savings,
            "savings_percentage": "34% Savings",
            "impact": "High",
            "recommendation": f"Commit to consistent compute baseline consumption on a 1-year term to reduce EC2 spend from ${compute_cost:.2f}/mo to ~${(compute_cost - sp_savings):.2f}/mo while keeping flexibility across instance types."
        })

    # 2. ARM Graviton Adoption
    inst = comp.compute.instance_type
    if "t3" in inst or "c5" in inst or "m5" in inst:
        graviton_savings = round(compute_cost * 0.20, 2)
        optimizations.append({
            "title": "Migrate from x86 to AWS Graviton (ARM64)",
            "category": "Architecture Modernization",
            "estimated_monthly_savings": graviton_savings,
            "savings_percentage": "20% Savings",
            "impact": "Medium",
            "recommendation": f"Transition workloads to ARM-based Graviton3 instances (e.g., replace {inst} with t4g/c7g equivalents) to lower hourly compute charges by 20% and improve energy efficiency."
        })

    # 3. Off-Hours Scheduling for Development
    if inputs.reliability == "dev_testing" or inputs.stream == "dev_sandbox":
        off_hours_savings = round((compute_cost + rds_cost) * 0.65, 2)
        optimizations.append({
            "title": "Implement Off-Hours Automated Shutdown",
            "category": "Governance & Scheduling",
            "estimated_monthly_savings": off_hours_savings,
            "savings_percentage": "65% Savings",
            "impact": "High",
            "recommendation": "Configure AWS Instance Scheduler or EventBridge + Lambda to power down dev/test EC2 and RDS instances outside 09:00 - 18:00 on weekdays and all weekend."
        })

    # 4. NAT Gateway Consolidation
    if comp.networking.nat_gateway_count > 1 and inputs.reliability != "mission_critical":
        nat_savings = round((comp.networking.nat_gateway_count - 1) * 32.85, 2)
        optimizations.append({
            "title": "Consolidate Multi-AZ NAT Gateways to Single NAT",
            "category": "Network Optimization",
            "estimated_monthly_savings": nat_savings,
            "savings_percentage": "Egress Reduction",
            "impact": "Medium",
            "recommendation": f"Consolidate {comp.networking.nat_gateway_count} NAT Gateways into 1 shared NAT Gateway for non-mission-critical environments to immediately eliminate redundant baseline gateway hourly fees."
        })

    # 5. S3 Intelligent-Tiering
    if comp.storage.s3_gb >= 50:
        s3_savings = round(comp.storage.s3_gb * 0.023 * 0.50, 2)
        optimizations.append({
            "title": "Enable S3 Intelligent-Tiering Storage Class",
            "category": "Storage Optimization",
            "estimated_monthly_savings": max(2.5, s3_savings),
            "savings_percentage": "Up to 68% Storage Savings",
            "impact": "Low",
            "recommendation": "Activate S3 Intelligent-Tiering to automatically transition rarely accessed objects to lower-cost access tiers without monitoring or retrieval fees."
        })

    # 6. Spot Instances for Worker Queues
    if inputs.stream in ["ai_ml", "devops_tooling"] or inputs.traffic_scale == "production":
        spot_savings = round(compute_cost * 0.60, 2)
        optimizations.append({
            "title": "Leverage EC2 Spot Instances for Background Tasks",
            "category": "Compute Spot Pricing",
            "estimated_monthly_savings": spot_savings,
            "savings_percentage": "Up to 70% Savings",
            "impact": "High",
            "recommendation": "Use EC2 Spot instances for background worker processes, asynchronous message queues, and CI build agents to save up to 70-90% compared to On-Demand rates."
        })

    return optimizations


async def analyze_and_explain_requirements(inputs: RequirementInput, session: AsyncSession) -> dict:
    """
    Executes end-to-end sizing analysis and augments output with 'Why That Service' rationales
    and FinOps cost optimizations.
    """
    profile = await analyze_requirements(inputs, session)
    rationales = generate_service_rationales(inputs, profile)
    optimizations = generate_cost_optimizations(inputs, profile)

    cost_breakdown = {
        "compute": round(profile.components.compute.monthly_cost, 2),
        "database": round(profile.components.database.monthly_cost, 2),
        "networking": round(profile.components.networking.monthly_cost, 2),
        "storage": round(profile.components.storage.monthly_cost, 2),
        "security": 25.0 if profile.components.security.waf_enabled else 0.0,
        "operations_monitoring": 15.0 if profile.components.monitoring.level == "advanced" else 0.0,
        "total": round(profile.total_estimated_cost, 2)
    }

    ai_advice = await generate_ai_architecture_advice(inputs, profile)

    return {
        "profile": profile.model_dump(),
        "service_rationales": rationales,
        "cost_optimizations": optimizations,
        "ai_advice": ai_advice,
        "cost_breakdown": cost_breakdown,
        "architecture_tier": profile.architecture_tier,
        "total_estimated_cost": profile.total_estimated_cost,
        "target_region": "us-east-1"
    }



