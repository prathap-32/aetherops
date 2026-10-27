# services/repo_analyzer_service/app/gemini_sizer.py
"""
Google Gemini Cloud LLM Sizing Engine & Multi-User Cost-Optimized Shield.
Combines environment-aware AWS sizing with SHA-256 caching, concurrency throttling,
and an automated deterministic heuristic fallback so users are never blocked.
"""
from __future__ import annotations

import re
import os
import json
import time
import asyncio
import hashlib
import logging
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger("repo-analyzer-service.gemini")


def load_dotenv_if_exists():
    """Load key-values from .env files if present without external dependencies."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(base_dir, ".env"),
        os.path.join(os.path.dirname(os.path.dirname(base_dir)), ".env"),
    ]
    for env_file in candidates:
        if os.path.exists(env_file):
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k not in os.environ and v:
                                os.environ[k] = v
            except Exception as e:
                logger.warning(f"Failed to read {env_file}: {e}")


load_dotenv_if_exists()


# ─────────────────────────────────────────────────────────────────────────────
# In-Memory SHA-256 Content-Addressable Cache
# ─────────────────────────────────────────────────────────────────────────────
_AI_SIZING_CACHE: Dict[str, Dict[str, Any]] = {}
_IN_FLIGHT_REQUESTS: Dict[str, asyncio.Future] = {}


def _compute_cache_key(
    verified_spec: Dict[str, Any],
    environment_tier: str,
    target_region: str,
    budget_tier: str,
    traffic_scale: str,
) -> str:
    """Creates a deterministic SHA-256 fingerprint of the inputs."""
    payload_str = json.dumps(
        {
            "spec": verified_spec,
            "env": environment_tier.lower(),
            "region": target_region.lower(),
            "budget": budget_tier.lower(),
            "traffic": traffic_scale.lower(),
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# Deterministic Heuristic Sizing Rules Engine (Zero-Downtime Guarantee)
# ─────────────────────────────────────────────────────────────────────────────
def generate_deterministic_aws_sizing(
    verified_spec: Dict[str, Any],
    environment_tier: str = "development",
    target_region: str = "us-east-1",
    budget_tier: str = "STANDARD",
    traffic_scale: str = "MODERATE",
    ha_level: str = "AUTO",
) -> Dict[str, Any]:
    """
    Synthesizes the exact AWS infrastructure based on the verified codebase Key:Value report
    and the selected Project Environment (DEV vs STAGING vs PROD).
    """
    env = environment_tier.lower()
    is_prod = env in ("production", "prod")
    is_staging = env in ("staging", "stage")
    is_dev = not (is_prod or is_staging)

    # Extract primitives from verified spec
    frameworks = [str(f).lower() for f in verified_spec.get("frameworks", []) or verified_spec.get("detected_frameworks", "").split(",")]
    databases = [str(d).lower() for d in verified_spec.get("databases", []) or verified_spec.get("database_dependencies", "").split(",")]
    workload_type = str(verified_spec.get("workload_type", "Web Application Service"))
    has_docker = bool(verified_spec.get("has_dockerfile", False) or "docker" in str(verified_spec.get("container_status", "")).lower())
    ports = verified_spec.get("ports", [8000])
    if not ports and isinstance(verified_spec.get("network_ports"), str):
        ports = [int(p) for p in re_ports if (re_ports := [m for m in re.findall(r"\d+", verified_spec["network_ports"])])]
    primary_port = ports[0] if ports else 8000

    has_ui = any("react" in f or "vue" in f or "next" in f or "svelte" in f or "spa" in workload_type.lower() for f in frameworks)
    has_postgres = any("postgres" in d for d in databases)
    has_mysql = any("mysql" in d for d in databases)
    has_redis = any("redis" in d for d in databases)
    has_mongo = any("mongo" in d for d in databases)

    # 1. Compute Sizing
    if is_prod:
        compute = {
            "service": "AWS ECS Fargate",
            "task_cpu": "1024 (1 vCPU)",
            "task_memory": "2048 (2 GB)",
            "min_capacity": 2,
            "max_capacity": 8,
            "multi_az": True,
            "container_port": primary_port,
            "autoscaling_metric": "TargetTracking CPUUtilization (70%)",
            "rationale": f"PROD TIER HAS HIGHEST PRIORITY: High-availability auto-scaling ECS Fargate task fleet distributed across 3 Availability Zones for zero-downtime {workload_type}.",
            "monthly_cost": 86.40,
        }
    elif is_staging:
        compute = {
            "service": "AWS ECS Fargate",
            "task_cpu": "512 (0.5 vCPU)",
            "task_memory": "1024 (1 GB)",
            "min_capacity": 2,
            "max_capacity": 4,
            "multi_az": True,
            "container_port": primary_port,
            "autoscaling_metric": "TargetTracking CPUUtilization (80%)",
            "rationale": "Dual-AZ ECS Fargate tasks mirroring production topology with moderate capacity for staging verification.",
            "monthly_cost": 34.20,
        }
    else:  # Development Tier: Extreme Frugality & Cost Minimization
        if has_docker:
            compute = {
                "service": "Amazon EC2 (Docker Runtime)",
                "task_cpu": "t4g.micro (2 vCPU, 1 GB RAM)",
                "task_memory": "1024 MB",
                "min_capacity": 1,
                "max_capacity": 1,
                "multi_az": False,
                "container_port": primary_port,
                "autoscaling_metric": "None (Single Micro Instance)",
                "rationale": "DEV TIER PRIORITIZES COST EFFICIENCY: Uses a small t4g.micro EC2 instance with Docker runtime and direct Elastic IP ($6.12/mo). Eliminates expensive $16.50/mo ALB and Fargate overhead. Eligible for AWS Free Tier.",
                "monthly_cost": 6.12,
            }
        else:
            compute = {
                "service": "Amazon EC2 (t4g.nano)",
                "task_cpu": "t4g.nano (2 vCPU, 0.5 GB RAM)",
                "task_memory": "512 MB",
                "min_capacity": 1,
                "max_capacity": 1,
                "multi_az": False,
                "container_port": primary_port,
                "autoscaling_metric": "None (Single Nano Instance)",
                "rationale": "Burstable ARM64 EC2 nano instance sized for minimal developer testing costs ($3.06/mo).",
                "monthly_cost": 3.06,
            }

    # 2. Database Sizing
    database: Dict[str, Any] = {}
    if has_postgres:
        if is_prod:
            database = {
                "service": "Amazon Aurora PostgreSQL Serverless v2",
                "engine_version": "16.1",
                "min_acu": 1.0,
                "max_acu": 8.0,
                "multi_az": True,
                "storage": "Aurora Distributed Storage (Auto-expanding)",
                "backup_retention_days": 30,
                "rationale": "Multi-AZ Aurora Serverless with automated instant failover and sub-second scaling for production transactions.",
                "monthly_cost": 88.00,
            }
        elif is_staging:
            database = {
                "service": "Amazon RDS PostgreSQL",
                "engine_version": "16.1",
                "instance_class": "db.t4g.small",
                "multi_az": False,
                "storage_gb": 40,
                "storage_type": "gp3",
                "backup_retention_days": 7,
                "rationale": "Single-AZ RDS PostgreSQL for staging integration tests with 40GB SSD storage.",
                "monthly_cost": 34.50,
            }
        else:
            database = {
                "service": "Amazon RDS PostgreSQL",
                "engine_version": "16.1",
                "instance_class": "db.t4g.micro",
                "multi_az": False,
                "storage_gb": 20,
                "storage_type": "gp3",
                "backup_retention_days": 1,
                "rationale": "Burstable Single-AZ RDS PostgreSQL micro instance to minimize development costs.",
                "monthly_cost": 17.50,
            }
    elif has_mysql:
        if is_prod:
            database = {
                "service": "Amazon RDS MySQL Multi-AZ",
                "engine_version": "8.0",
                "instance_class": "db.t4g.medium",
                "multi_az": True,
                "storage_gb": 100,
                "storage_type": "gp3",
                "backup_retention_days": 30,
                "rationale": "Multi-AZ RDS MySQL with standby replica in secondary AZ.",
                "monthly_cost": 82.00,
            }
        else:
            database = {
                "service": "Amazon RDS MySQL",
                "engine_version": "8.0",
                "instance_class": "db.t4g.micro",
                "multi_az": False,
                "storage_gb": 20,
                "storage_type": "gp3",
                "backup_retention_days": 1,
                "rationale": "Single-AZ RDS MySQL micro instance for development.",
                "monthly_cost": 16.80,
            }
    elif has_mongo:
        database = {
            "service": "Amazon DocumentDB (MongoDB compatible)",
            "instance_class": "db.t3.medium" if is_prod else "db.t3.medium (dev)",
            "instances": 2 if is_prod else 1,
            "rationale": "Managed document database with MongoDB 5.0 compatibility.",
            "monthly_cost": 110.00 if is_prod else 58.00,
        }
    else:
        database = {
            "service": "None (Stateless Architecture)",
            "rationale": "No embedded database client detected in codebase.",
            "monthly_cost": 0.00,
        }

    # 3. Cache Layer Sizing
    cache: Optional[Dict[str, Any]] = None
    if has_redis:
        if is_prod:
            cache = {
                "service": "Amazon ElastiCache for Redis",
                "node_type": "cache.t4g.small",
                "nodes": 2,
                "multi_az": True,
                "auto_failover": True,
                "rationale": "Multi-AZ Redis cluster with automated failover for session management and low-latency API caching.",
                "monthly_cost": 36.40,
            }
        elif is_staging:
            cache = {
                "service": "Amazon ElastiCache for Redis",
                "node_type": "cache.t4g.micro",
                "nodes": 1,
                "multi_az": False,
                "auto_failover": False,
                "rationale": "Single-node Redis cache for staging preview.",
                "monthly_cost": 13.20,
            }
        else:
            cache = {
                "service": "Amazon ElastiCache for Redis (Optional in DEV)",
                "node_type": "cache.t4g.micro",
                "nodes": 1,
                "multi_az": False,
                "auto_failover": False,
                "rationale": "Single-node micro Redis cache for local cache contract testing.",
                "monthly_cost": 13.20,
            }

    # 4. Frontend Hosting (SPA / Jamstack)
    frontend_hosting: Optional[Dict[str, Any]] = None
    if has_ui:
        frontend_hosting = {
            "service": "Amazon CloudFront + AWS S3",
            "distribution_tier": "PriceClass_All" if is_prod else "PriceClass_100",
            "ssl_certificate": "AWS Certificate Manager (ACM)",
            "edge_caching": True,
            "rationale": "Global CDN edge distribution caching static assets with sub-50ms latency and HTTPS termination.",
            "monthly_cost": 4.50 if is_prod else 1.80,
        }

    # 5. Networking & Ingress
    if is_prod:
        networking = {
            "vpc": "Custom VPC (10.0.0.0/16)",
            "availability_zones": 3,
            "public_subnets": 3,
            "private_subnets": 3,
            "nat_gateways": 2,
            "alb": True,
            "waf_shield": True,
            "route53": True,
            "rationale": "3-AZ enterprise VPC with redundant NAT Gateways, Application Load Balancer, and AWS WAF protection.",
            "monthly_cost": 96.00,
        }
    elif is_staging:
        networking = {
            "vpc": "Custom VPC (10.1.0.0/16)",
            "availability_zones": 2,
            "public_subnets": 2,
            "private_subnets": 2,
            "nat_gateways": 1,
            "alb": True,
            "waf_shield": False,
            "route53": True,
            "rationale": "Dual-AZ VPC with shared NAT Gateway and Application Load Balancer.",
            "monthly_cost": 48.00,
        }
    else:  # Dev: Extreme Frugality & Cost Minimization
        networking = {
            "vpc": "Default / Custom VPC (10.2.0.0/16)",
            "availability_zones": 1,
            "public_subnets": 1,
            "private_subnets": 0,
            "nat_gateways": 0,
            "alb": False,
            "waf_shield": False,
            "route53": False,
            "rationale": "Cost-minimized DEV networking: Direct Elastic IP / Public Subnet with Security Group rules on port. Eliminates the $16.50/mo Application Load Balancer and $32/mo NAT Gateway overhead.",
            "monthly_cost": 0.00,
        }

    # Total Cost Calculation
    cost_items = {
        "compute": compute.get("monthly_cost", 0.0),
        "database": database.get("monthly_cost", 0.0),
        "cache": cache.get("monthly_cost", 0.0) if cache else 0.0,
        "frontend": frontend_hosting.get("monthly_cost", 0.0) if frontend_hosting else 0.0,
        "networking": networking.get("monthly_cost", 0.0),
    }
    total_cost = round(sum(cost_items.values()), 2)
    cost_items["total_estimated_monthly_usd"] = total_cost

    # FinOps Optimizations
    finops = []
    if is_dev:
        finops.append("DEV Strategy: Replaced ECS Fargate ($12.80) + ALB ($16.50) with burstable EC2 Docker ($6.12/mo) and direct Elastic IP to eliminate $23+/mo in overhead.")
        finops.append("AWS Free Tier Eligible: Qualifying AWS accounts receive 750 free hours/month on t4g.micro for the first 12 months ($0.00/mo net cost).")
        finops.append("Use AWS Instance Scheduler to auto-stop development EC2 instance outside working hours (saves ~65% further, down to ~$2.10/mo).")
    elif is_staging:
        finops.append("Apply 1-Year Compute Savings Plan to staging Fargate tasks for up to 28% discount.")
        finops.append("Share non-production ALB across staging microservices to amortize ingress load balancer costs.")
    else:  # Production
        finops.append("Apply 3-Year Compute Savings Plan to production ECS task fleet for up to 50% discount.")
        finops.append("Enable Amazon Aurora Serverless v2 Auto-Pause during designated maintenance hours if non-critical.")
        finops.append("Enable S3 Intelligent-Tiering on asset storage to eliminate manual lifecycle policies.")

    # Module 4 Topology Nodes & Edges (Ready for ReactFlow Studio Canvas)
    nodes = [
        {"id": "node-client", "type": "client", "label": "Internet Users / Developers", "position": {"x": 50, "y": 150}},
    ]
    edges = []

    if frontend_hosting:
        nodes.append({"id": "node-cdn", "type": "cloudfront", "label": "CloudFront CDN (S3 Static SPA)", "position": {"x": 240, "y": 60}})
        edges.append({"id": "e-client-cdn", "source": "node-client", "target": "node-cdn"})

    if networking.get("alb"):
        nodes.append({"id": "node-alb", "type": "alb", "label": "Application Load Balancer", "position": {"x": 240, "y": 240}})
        edges.append({"id": "e-client-alb", "source": "node-client", "target": "node-alb"})
        nodes.append({"id": "node-compute", "type": "fargate" if "fargate" in compute["service"].lower() else "ec2", "label": f"{compute['service']} ({compute['task_cpu']})", "position": {"x": 480, "y": 240}})
        edges.append({"id": "e-alb-compute", "source": "node-alb", "target": "node-compute"})
    else:
        # DEV: Direct connection to EC2 Docker instance with Elastic IP ($0 ALB cost)
        nodes.append({"id": "node-compute", "type": "ec2", "label": f"{compute['service']} ({compute['task_cpu']}) - Elastic IP", "position": {"x": 360, "y": 150}})
        edges.append({"id": "e-client-compute", "source": "node-client", "target": "node-compute"})

    if database.get("service") and "none" not in database["service"].lower():
        nodes.append({"id": "node-db", "type": "rds", "label": database["service"], "position": {"x": 720, "y": 180}})
        edges.append({"id": "e-compute-db", "source": "node-compute", "target": "node-db"})

    if cache:
        nodes.append({"id": "node-cache", "type": "elasticache", "label": cache["service"], "position": {"x": 720, "y": 300}})
        edges.append({"id": "e-compute-cache", "source": "node-compute", "target": "node-cache"})

    recommended_services = [
        {"category": "Compute", "service": compute["service"], "tier": compute["task_cpu"], "cost": compute["monthly_cost"]},
        {"category": "Database", "service": database["service"], "tier": database.get("instance_class", "Managed"), "cost": database["monthly_cost"]},
        {"category": "Networking", "service": "VPC & Direct Elastic IP" if not networking.get("alb") else "VPC & ALB", "tier": "Direct Elastic IP ($0/mo)" if not networking.get("alb") else f"{networking['availability_zones']} AZs ALB", "cost": networking["monthly_cost"]},
    ]
    if cache:
        recommended_services.append({"category": "Cache", "service": cache["service"], "tier": cache["node_type"], "cost": cache["monthly_cost"]})
    if frontend_hosting:
        recommended_services.append({"category": "Frontend CDN", "service": frontend_hosting["service"], "tier": "Global Edge", "cost": frontend_hosting["monthly_cost"]})

    return {
        "status": "SUCCESS",
        "environment_tier": environment_tier,
        "target_region": target_region,
        "ai_provider": "deterministic_rules_engine",
        "cached": False,
        "verified_spec_applied": verified_spec,
        "recommended_services": recommended_services,
        "compute": compute,
        "database": database,
        "cache": cache,
        "frontend_hosting": frontend_hosting,
        "networking": networking,
        "monthly_cost_estimate_usd": cost_items,
        "finops_optimizations": finops,
        "deployment_readiness": {
            "has_container_config": has_docker,
            "exposed_ports_configured": True,
            "target_environment_matched": True,
            "ready_for_architecture_studio": True,
        },
        "module4_payload": {
            "graph": {"nodes": nodes, "edges": edges},
            "environment_tier": environment_tier,
            "target_region": target_region,
            "primary_port": primary_port,
            "total_monthly_usd": total_cost,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# Google Gemini 2.0 Flash Cloud LLM Engine with Cost Shield & Fallback
# ─────────────────────────────────────────────────────────────────────────────
class GeminiSizer:
    """Manages Google Gemini API interactions with multi-user concurrency and rate-limit shields."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.max_concurrent = int(os.getenv("GEMINI_MAX_CONCURRENT", "4"))
        self.timeout = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "15.0"))
        self.semaphore = asyncio.Semaphore(self.max_concurrent)

    async def size_architecture(
        self,
        verified_spec: Dict[str, Any],
        environment_tier: str = "development",
        target_region: str = "us-east-1",
        budget_tier: str = "STANDARD",
        traffic_scale: str = "MODERATE",
        ha_level: str = "AUTO",
    ) -> Dict[str, Any]:
        """
        Synthesizes AWS architecture with Google Gemini Flash.
        1. Checks SHA-256 cache (0 tokens if hit).
        2. Throttles concurrent calls with Semaphore.
        3. Calls Gemini REST API with strictly minified abstract JSON.
        4. Gracefully falls back to deterministic rule engine if API key is absent or on error.
        """
        cache_key = _compute_cache_key(verified_spec, environment_tier, target_region, budget_tier, traffic_scale)

        # 1. Cache hit check
        if cache_key in _AI_SIZING_CACHE:
            logger.info("SHA-256 Cache HIT for architecture specification (%s)", cache_key[:12])
            cached = dict(_AI_SIZING_CACHE[cache_key])
            cached["cached"] = True
            return cached

        # Check if identical request is currently in-flight
        if cache_key in _IN_FLIGHT_REQUESTS:
            logger.info("Coalescing in-flight request for cache key (%s)", cache_key[:12])
            return await _IN_FLIGHT_REQUESTS[cache_key]

        # 2. If no Gemini API key configured, use deterministic rule-based engine directly
        if not self.api_key:
            logger.info("No GEMINI_API_KEY configured. Utilizing deterministic AWS sizing engine directly.")
            result = generate_deterministic_aws_sizing(
                verified_spec=verified_spec,
                environment_tier=environment_tier,
                target_region=target_region,
                budget_tier=budget_tier,
                traffic_scale=traffic_scale,
                ha_level=ha_level,
            )
            result["ai_provider"] = "deterministic_rules_engine (Local)"
            _AI_SIZING_CACHE[cache_key] = result
            return result

        # 3. Call Google Gemini 2.0 Flash via REST with Semaphore
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        _IN_FLIGHT_REQUESTS[cache_key] = future

        try:
            async with self.semaphore:
                result = await self._call_gemini_api(
                    verified_spec=verified_spec,
                    environment_tier=environment_tier,
                    target_region=target_region,
                    budget_tier=budget_tier,
                    traffic_scale=traffic_scale,
                )
            future.set_result(result)
            _AI_SIZING_CACHE[cache_key] = result
            return result
        except Exception as exc:
            logger.warning(
                "Gemini API call encountered error: %s. Executing transparent fallback to deterministic rules engine.",
                exc,
            )
            fallback_res = generate_deterministic_aws_sizing(
                verified_spec=verified_spec,
                environment_tier=environment_tier,
                target_region=target_region,
                budget_tier=budget_tier,
                traffic_scale=traffic_scale,
                ha_level=ha_level,
            )
            fallback_res["ai_provider"] = "deterministic_rules_engine"
            fallback_res["diagnostics"] = {
                "engine": "deterministic_rules_engine",
                "fallback_engaged": True,
                "diagnostic_detail": str(exc)[:200],
            }
            future.set_result(fallback_res)
            _AI_SIZING_CACHE[cache_key] = fallback_res
            return fallback_res
        finally:
            _IN_FLIGHT_REQUESTS.pop(cache_key, None)

    async def _call_gemini_api(
        self,
        verified_spec: Dict[str, Any],
        environment_tier: str,
        target_region: str,
        budget_tier: str,
        traffic_scale: str,
    ) -> Dict[str, Any]:
        """Calls Google Gemini REST endpoint with strict JSON schema."""
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        # Build minified abstract input (Zero proprietary code lines)
        abstract_input = {
            "role": "AetherOps Autonomous AWS Architect",
            "task": "Size optimal AWS production architecture based on verified technical primitives.",
            "target_environment": environment_tier,
            "target_region": target_region,
            "budget_tier": budget_tier,
            "traffic_scale": traffic_scale,
            "specification": {
                "workload_type": verified_spec.get("workload_type"),
                "frameworks": verified_spec.get("frameworks") or verified_spec.get("detected_frameworks"),
                "languages": verified_spec.get("languages") or verified_spec.get("primary_languages"),
                "databases": verified_spec.get("databases") or verified_spec.get("database_dependencies"),
                "ports": verified_spec.get("ports") or verified_spec.get("network_ports"),
                "containerized": bool(verified_spec.get("has_dockerfile", False) or "docker" in str(verified_spec.get("container_status", "")).lower()),
            },
        }

        system_instruction = (
            "You are AetherOps AI Infrastructure Architect. You receive ONLY sanitized abstract tech primitives. "
            "Output strictly valid JSON with right-sized AWS architecture. Do not include markdown fences, comments, or pleasantries.\n"
            "ENVIRONMENT PRIORITY & COST RULES:\n"
            "1. PROD ENVIRONMENT HAS HIGHEST PRIORITY: Reliability, High Availability, and Auto-scaling are paramount. "
            "For containerized workloads, ALWAYS use AWS ECS Fargate auto-scaling tasks across 3 AZs with Multi-AZ ALB, Multi-AZ Aurora/RDS, and WAF.\n"
            "2. STAGING ENVIRONMENT: Focus on testing parity and staging isolation. Use dual-task ECS Fargate with shared ALB.\n"
            "3. DEV ENVIRONMENT: Prioritize EXTREME COST EFFICIENCY and developer frugality. For single Docker containers or simple web workloads, "
            "recommend a small Amazon EC2 instance (t4g.nano or t4g.micro with Docker Engine) with direct Elastic IP. "
            "NEVER recommend an Application Load Balancer ($16.50/mo) in DEV because it is unnecessary overhead for developer testing. "
            "DEV monthly compute + networking cost MUST be under $7/month."
        )

        req_body = {
            "contents": [
                {
                    "parts": [
                        {"text": system_instruction + "\n\nInput JSON:\n" + json.dumps(abstract_input)}
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2,
                "max_output_tokens": 4096,
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(endpoint, json=req_body)

        if resp.status_code != 200:
            raise ValueError(f"Gemini API returned HTTP {resp.status_code}: {resp.text[:200]}")

        res_data = resp.json()
        candidates = res_data.get("candidates", [])
        if not candidates:
            raise ValueError(f"No candidates returned from Gemini API: {resp.text[:200]}")

        parts = candidates[0].get("content", {}).get("parts", [])
        raw_text = ""
        for p in parts:
            if "text" in p and not p.get("thought", False):
                raw_text = p["text"]
                break
        if not raw_text and parts:
            raw_text = parts[-1].get("text", "")

        # Clean any accidental fences or thoughts
        raw_text = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        match = re.search(r'(\{[\s\S]*\})', raw_text)
        if match:
            raw_text = match.group(1)

        parsed_ai = json.loads(raw_text)

        # Merge with local topology generator to produce ReactFlow nodes for Module 4
        base_deterministic = generate_deterministic_aws_sizing(
            verified_spec=verified_spec,
            environment_tier=environment_tier,
            target_region=target_region,
            budget_tier=budget_tier,
            traffic_scale=traffic_scale,
        )

        # Overlay Gemini recommendations where valid
        if isinstance(parsed_ai.get("compute"), dict):
            base_deterministic["compute"].update(parsed_ai["compute"])
        if isinstance(parsed_ai.get("database"), dict) and "service" in parsed_ai["database"]:
            base_deterministic["database"].update(parsed_ai["database"])
        if isinstance(parsed_ai.get("finops_optimizations"), list):
            base_deterministic["finops_optimizations"] = parsed_ai["finops_optimizations"]
        if isinstance(parsed_ai.get("monthly_cost_estimate_usd"), dict):
            base_deterministic["monthly_cost_estimate_usd"].update(parsed_ai["monthly_cost_estimate_usd"])

        base_deterministic["ai_provider"] = self.model
        base_deterministic["cached"] = False
        return base_deterministic


# Global singleton instance
gemini_sizer = GeminiSizer()


def recalculate_custom_aws_sizing(
    environment_tier: str,
    target_region: str,
    compute_service: str,
    instance_type: str,
    min_capacity: int,
    max_capacity: int,
    multi_az: bool,
    alb_enabled: bool,
    waf_enabled: bool,
    database_service: str,
    cache_service: str,
    cdn_enabled: bool,
    verified_spec: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Recalculates monthly AWS cloud costs and validates architectural compatibility
    when a user customizes or edits their recommended services.
    """
    verified_spec = verified_spec or {}
    env_lower = environment_tier.lower()
    is_dev = "dev" in env_lower
    is_prod = "prod" in env_lower

    # 1. Compute Cost & Specs
    compute_cost = 6.12
    cpu_label = "2 vCPU"
    ram_label = "1 GB RAM"

    if "EC2" in compute_service:
        tier_pricing = {
            "t4g.nano": (3.06, "2 vCPU", "0.5 GB RAM"),
            "t4g.micro": (6.12, "2 vCPU", "1 GB RAM"),
            "t4g.small": (12.24, "2 vCPU", "2 GB RAM"),
            "t3.micro": (7.60, "2 vCPU", "1 GB RAM"),
            "t3.small": (15.20, "2 vCPU", "2 GB RAM"),
            "t3.medium": (30.40, "2 vCPU", "4 GB RAM"),
        }
        price_tuple = tier_pricing.get(instance_type, (6.12, "2 vCPU", "1 GB RAM"))
        compute_cost = round(price_tuple[0] * max(1, min_capacity), 2)
        cpu_label = price_tuple[1]
        ram_label = price_tuple[2]
    elif "ECS" in compute_service or "Fargate" in compute_service:
        fargate_pricing = {
            "0.25 vCPU / 0.5 GB": (12.80, "0.25 vCPU", "0.5 GB RAM"),
            "0.5 vCPU / 1 GB": (25.60, "0.5 vCPU", "1 GB RAM"),
            "1 vCPU / 2 GB": (51.20, "1 vCPU", "2 GB RAM"),
            "2 vCPU / 4 GB": (102.40, "2 vCPU", "4 GB RAM"),
        }
        price_tuple = fargate_pricing.get(instance_type, (12.80, "0.25 vCPU", "0.5 GB RAM"))
        compute_cost = round(price_tuple[0] * max(1, min_capacity), 2)
        cpu_label = price_tuple[1]
        ram_label = price_tuple[2]
    elif "Lambda" in compute_service:
        compute_cost = 1.50
        cpu_label = "Serverless vCPU"
        ram_label = "512 MB Memory"

    compute_dict = {
        "service": compute_service,
        "instance_class": instance_type,
        "task_cpu": cpu_label,
        "task_memory": ram_label,
        "min_capacity": min_capacity,
        "max_capacity": max(min_capacity, max_capacity),
        "multi_az": multi_az,
        "monthly_cost": compute_cost,
        "rationale": f"User-selected {compute_service} running {min_capacity} instance(s) of {instance_type}.",
    }

    # 2. Database Cost & Specs
    db_cost = 0.00
    db_dict = {
        "service": database_service,
        "monthly_cost": 0.00,
        "multi_az": multi_az,
        "rationale": "No external managed database requested." if "None" in database_service else f"Managed {database_service}",
    }

    if "db.t4g.micro" in database_service:
        db_cost = 17.20 if multi_az else 8.60
        db_dict["monthly_cost"] = db_cost
        db_dict["instance_class"] = "db.t4g.micro"
    elif "db.t4g.small" in database_service:
        db_cost = 34.40 if multi_az else 17.20
        db_dict["monthly_cost"] = db_cost
        db_dict["instance_class"] = "db.t4g.small"
    elif "Aurora" in database_service:
        db_cost = 48.00
        db_dict["monthly_cost"] = db_cost
        db_dict["instance_class"] = "Serverless v2 (0.5 - 4 ACUs)"

    # 3. Cache
    cache_cost = 0.00
    cache_dict = None
    if "Redis" in cache_service and "None" not in cache_service:
        if "t4g.micro" in cache_service:
            cache_cost = 26.40 if multi_az else 13.20
        else:
            cache_cost = 36.40
        cache_dict = {
            "service": cache_service,
            "monthly_cost": cache_cost,
            "multi_az": multi_az,
            "rationale": f"In-memory Redis cache ({'Multi-AZ' if multi_az else 'Single-AZ'}).",
        }

    # 4. Frontend CDN
    cdn_cost = 1.80 if cdn_enabled else 0.00
    frontend_dict = None
    if cdn_enabled:
        frontend_dict = {
            "service": "Amazon CloudFront + S3",
            "monthly_cost": cdn_cost,
            "rationale": "Static assets CDN edge caching with S3 origin.",
        }

    # 5. Networking
    net_cost = 0.00
    if alb_enabled:
        net_cost = 16.50
        if waf_enabled:
            net_cost += 10.00
        if is_prod:
            net_cost += 32.00  # Redundant NAT gateways
    networking_dict = {
        "vpc": "Custom VPC (10.0.0.0/16)",
        "availability_zones": 3 if (multi_az or is_prod) else 1,
        "alb": alb_enabled,
        "waf_shield": waf_enabled,
        "monthly_cost": net_cost,
        "rationale": "ALB with internet-facing routing" if alb_enabled else "Direct Elastic IP with Security Group rules (Zero ALB overhead)",
    }

    # Total Cost
    cost_items = {
        "compute": compute_cost,
        "database": db_cost,
        "cache": cache_cost,
        "frontend": cdn_cost,
        "networking": net_cost,
    }
    total_cost = round(sum(cost_items.values()), 2)
    cost_items["total_estimated_monthly_usd"] = total_cost

    # Compatibility Notes
    notes = []
    if is_dev and alb_enabled:
        notes.append("FinOps Alert: Adding an Application Load Balancer in DEV increases your monthly bill by $16.50. Direct Elastic IP ($0/mo) is recommended.")
    elif is_dev and not alb_enabled:
        notes.append("Cost Optimized: Running with Direct Elastic IP in DEV saves $16.50/month compared to an ALB.")

    if is_prod and not multi_az:
        notes.append("Reliability Alert: PROD environment should typically enable Multi-AZ to prevent single points of failure.")
    elif is_prod and multi_az:
        notes.append("High Availability: Multi-AZ redundancy verified across 3 Availability Zones.")

    if "EC2" in compute_service:
        notes.append(f"Compute: Single-node Docker Engine on {instance_type}. Free-tier qualifying accounts pay $0.00 for up to 750 hours/month.")
    elif "ECS" in compute_service:
        notes.append("Compute: Managed AWS ECS Fargate serverless container tasks with automated recovery.")

    # Recommended Services List
    recomms = [
        {"category": "Compute", "service": compute_dict["service"], "tier": instance_type, "cost": compute_dict["monthly_cost"]},
        {"category": "Networking", "service": "Application Load Balancer" if alb_enabled else "Direct Elastic IP (No ALB)", "tier": "Public Ingress", "cost": networking_dict["monthly_cost"]},
    ]
    if db_dict["monthly_cost"] > 0:
        recomms.append({"category": "Database", "service": db_dict["service"], "tier": db_dict.get("instance_class", "Managed"), "cost": db_dict["monthly_cost"]})
    if cache_dict:
        recomms.append({"category": "Cache", "service": cache_dict["service"], "tier": "In-Memory", "cost": cache_dict["monthly_cost"]})
    if frontend_dict:
        recomms.append({"category": "CDN", "service": frontend_dict["service"], "tier": "Global Edge", "cost": frontend_dict["monthly_cost"]})

    # Visual Graph DAG for Module 4
    nodes = [
        {"id": "node-client", "type": "client", "label": "Client Ingress", "position": {"x": 100, "y": 200}},
    ]
    edges = []

    if alb_enabled:
        nodes.append({"id": "node-alb", "type": "alb", "label": "Application Load Balancer", "position": {"x": 320, "y": 200}})
        edges.append({"id": "e-client-alb", "source": "node-client", "target": "node-alb"})
        edges.append({"id": "e-alb-compute", "source": "node-alb", "target": "node-compute"})
    else:
        nodes.append({"id": "node-eip", "type": "elastic_ip", "label": "Direct Elastic IP", "position": {"x": 320, "y": 200}})
        edges.append({"id": "e-client-eip", "source": "node-client", "target": "node-eip"})
        edges.append({"id": "e-eip-compute", "source": "node-eip", "target": "node-compute"})

    nodes.append({
        "id": "node-compute",
        "type": "compute",
        "label": f"{compute_dict['service']} ({instance_type})",
        "position": {"x": 540, "y": 200},
    })

    if db_dict["monthly_cost"] > 0:
        nodes.append({"id": "node-db", "type": "rds", "label": db_dict["service"], "position": {"x": 760, "y": 140}})
        edges.append({"id": "e-compute-db", "source": "node-compute", "target": "node-db"})

    if cache_dict:
        nodes.append({"id": "node-cache", "type": "elasticache", "label": cache_dict["service"], "position": {"x": 760, "y": 280}})
        edges.append({"id": "e-compute-cache", "source": "node-compute", "target": "node-cache"})

    if cdn_enabled:
        nodes.append({"id": "node-cdn", "type": "cloudfront", "label": "CloudFront CDN + S3", "position": {"x": 320, "y": 80}})
        edges.append({"id": "e-client-cdn", "source": "node-client", "target": "node-cdn"})

    return {
        "status": "SUCCESS",
        "environment_tier": environment_tier,
        "target_region": target_region,
        "ai_provider": "user_customized_sizing_analyzer",
        "cached": False,
        "verified_spec_applied": verified_spec,
        "recommended_services": recomms,
        "compute": compute_dict,
        "database": db_dict,
        "cache": cache_dict,
        "frontend_hosting": frontend_dict,
        "networking": networking_dict,
        "monthly_cost_estimate_usd": cost_items,
        "finops_optimizations": [
            f"Active selection: {compute_service} ({instance_type}) totaling ${total_cost}/month.",
            "Instance scheduling can reduce compute expenses by ~65% outside active developer hours."
        ],
        "deployment_readiness": {
            "has_container_config": True,
            "exposed_ports_configured": True,
            "target_environment_matched": True,
            "ready_for_architecture_studio": True,
        },
        "compatibility_notes": notes,
        "module4_payload": {
            "graph": {"nodes": nodes, "edges": edges},
            "environment_tier": environment_tier,
            "target_region": target_region,
            "total_monthly_usd": total_cost,
        },
    }

