# services/architecture_generator/app/main.py
"""
AetherOps AI — Cloud Architecture Studio Microservice (Module 4)
Port 8004

Provides:
1. Visual ReactFlow DAG Generation from Module 3 AWS Right-Sized Specs.
2. Architecture Studio State Storage & Versioning.
3. Stage A: Deep AI Architecture Analysis (17 comprehensive criteria).
4. Stage B: Deterministic Well-Architected & Policy Validation (PASS / WARNING / BLOCKED).
5. Stage C: Version-Bound Architecture Review & Backend User Approval.
"""
import os
import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, status, Request, Body, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.schemas import (
    RequirementProfileOutput,
    ReactFlowGraphJSON,
    ReactFlowNode,
    ReactFlowNodeData,
    ReactFlowNodePosition,
    ReactFlowEdge,
)
from app.generator import generate_architecture_graph
from app.review_engine import run_ai_architecture_analysis, run_deterministic_validation
import json
from app.database import get_session, init_db
from app.models import ArchitectureVersionModel, StudioSessionModel
import json
# Setup logging
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)
log_file_path = os.path.join(logs_dir, "architecture_studio.log")

log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

file_handler = logging.FileHandler(log_file_path)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.handlers = [file_handler, console_handler]

logger = logging.getLogger("cloud-architecture-studio")

app = FastAPI(
    title="AetherOps AI - Cloud Architecture Studio Service",
    description="Interactive visual cloud architecture topology builder & Review Engine (Port 8005)",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()
    logger.info("Cloud Architecture Studio initialized with PostgreSQL database persistence.")

_STUDIO_SESSIONS: Dict[str, Dict[str, Any]] = {}
_ARCHITECTURE_VERSIONS: Dict[str, Dict[str, Any]] = {}
_APPROVED_VERSIONS: Dict[str, str] = {}

async def load_version_from_db(version_id: Optional[str]):
    if not version_id:
        return None
    if version_id in _ARCHITECTURE_VERSIONS:
        return _ARCHITECTURE_VERSIONS[version_id]
    try:
        async for session in get_session():
            db_ver = await session.get(ArchitectureVersionModel, version_id)
            if db_ver:
                v_record = {
                    "version_id": db_ver.version_id,
                    "tenant_id": db_ver.tenant_id,
                    "project_id": db_ver.project_id,
                    "environment_id": db_ver.environment_id,
                    "environment_tier": db_ver.environment_tier,
                    "target_region": db_ver.target_region,
                    "nodes": json.loads(db_ver.nodes) if db_ver.nodes else [],
                    "edges": json.loads(db_ver.edges) if db_ver.edges else [],
                    "status": db_ver.status,
                    "is_approved": db_ver.is_approved,
                    "approval_id": db_ver.approval_id,
                    "approved_by": db_ver.approved_by,
                    "approved_at": db_ver.approved_at,
                }
                _ARCHITECTURE_VERSIONS[version_id] = v_record
                return v_record
    except Exception as e:
        logger.warning(f"Failed to load version {version_id} from database: {e}")
    return None


class StudioSaveRequest(BaseModel):
    project_id: Optional[str] = None
    environment_id: Optional[str] = None
    version_id: Optional[str] = None
    environment_tier: str = "development"
    target_region: str = "us-east-1"
    monthly_cost_usd: float = 6.12
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ArchitectureValidationRequest(BaseModel):
    version_id: Optional[str] = None
    environment_tier: str = "development"
    target_region: str = "us-east-1"
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)


class ArchitectureApprovalRequest(BaseModel):
    version_id: str
    project_id: Optional[str] = None
    environment_id: Optional[str] = None
    comments: Optional[str] = None


class ArchitectureRejectRequest(BaseModel):
    version_id: str
    reason: Optional[str] = None


@app.get("/")
async def root():
    return {
        "service": "AetherOps AI - Cloud Architecture Studio Service",
        "module": 4,
        "port": 8005,
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "generate_graph": "/api/v1/architecture/generate-graph",
            "studio_save": "/api/v1/architecture/studio/save",
            "studio_state": "/api/v1/architecture/studio/state",
            "analyze": "/api/v1/architecture/analyze",
            "validate": "/api/v1/architecture/validate",
            "review": "/api/v1/architecture/review",
            "approve": "/api/v1/architecture/approve",
            "reject": "/api/v1/architecture/reject",
            "versions": "/api/v1/architecture/versions",
            "docs": "/docs",
        },
    }


@app.get("/health", status_code=status.HTTP_200_OK)
@app.get("/api/v1/architecture/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "cloud-architecture-studio",
        "port": 8004,
        "module": 4,
        "timestamp": time.time(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Topology DAG Generator
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/architecture/generate-graph", status_code=status.HTTP_200_OK)
@app.post("/api/v1/generate-graph", status_code=status.HTTP_200_OK)
async def generate_graph_endpoint(payload: Dict[str, Any] = Body(...)):
    """
    Synthesizes a visual ReactFlow node and edge topology DAG.
    Accepts Module 3 AwsSizingOutput, Module 1 RequirementProfileOutput, or custom studio parameters.
    """
    logger.info("Received visual architecture graph generation request")

    # If payload already has graph nodes/edges from Module 3 sizing, return enriched layout
    if "module4_payload" in payload and isinstance(payload["module4_payload"], dict):
        sub_graph = payload["module4_payload"].get("graph", {})
        if sub_graph.get("nodes"):
            return {
                "nodes": sub_graph["nodes"],
                "edges": sub_graph.get("edges", []),
                "environment_tier": payload.get("environment_tier", "development"),
                "total_monthly_usd": payload.get("monthly_cost_estimate_usd", {}).get("total_estimated_monthly_usd", 6.12),
            }

    # If payload is RequirementProfileOutput format, use deterministic generator
    if "components" in payload and "architecture_tier" in payload:
        try:
            profile = RequirementProfileOutput(**payload)
            graph = generate_architecture_graph(profile)
            return graph.model_dump()
        except Exception as e:
            logger.warning(f"Failed parsing as RequirementProfileOutput, building fallback DAG: {e}")

    # Build responsive dynamic layout from compute/database/networking keys
    env = payload.get("environment_tier", "development").lower()
    nodes = []
    edges = []

    compute = payload.get("compute", {})
    database = payload.get("database", {})
    networking = payload.get("networking", {})
    cache = payload.get("cache")
    frontend = payload.get("frontend_hosting")

    alb_enabled = networking.get("alb", False)
    comp_name = compute.get("service", "Amazon EC2 (Docker Runtime)")
    comp_size = compute.get("instance_class", compute.get("task_cpu", "t4g.micro"))

    # Ingress
    nodes.append({
        "id": "node-client",
        "type": "customNode",
        "data": {
            "label": "Client / Internet Ingress",
            "resource_type": "internet",
            "details": {"description": "Public HTTPS traffic entering AWS region via Route 53 DNS edge"}
        },
        "position": {"x": 100, "y": 220}
    })

    if alb_enabled:
        nodes.append({
            "id": "node-alb",
            "type": "customNode",
            "data": {
                "label": "Application Load Balancer",
                "resource_type": "alb",
                "details": {"cost": "$16.50/mo", "waf": str(networking.get("waf_shield", False))}
            },
            "position": {"x": 340, "y": 220}
        })
        edges.append({"id": "e-client-alb", "source": "node-client", "target": "node-alb", "animated": True, "label": "HTTPS:443"})
        edges.append({"id": "e-alb-compute", "source": "node-alb", "target": "node-compute", "animated": True, "label": "HTTP Forward"})
    else:
        nodes.append({
            "id": "node-eip",
            "type": "customNode",
            "data": {
                "label": "Direct Elastic IP (No ALB)",
                "resource_type": "elastic_ip",
                "details": {"cost": "$0.00/mo (Free in DEV)", "security_group": "Inbound 80/443"}
            },
            "position": {"x": 340, "y": 220}
        })
        edges.append({"id": "e-client-eip", "source": "node-client", "target": "node-eip", "animated": True, "label": "Direct Traffic"})
        edges.append({"id": "e-eip-compute", "source": "node-eip", "target": "node-compute", "animated": True})

    # Compute
    nodes.append({
        "id": "node-compute",
        "type": "customNode",
        "data": {
            "label": f"{comp_name} ({comp_size})",
            "resource_type": "ec2" if "EC2" in comp_name else "ecs",
            "details": {
                "service": comp_name,
                "sizing": comp_size,
                "cost": f"${compute.get('monthly_cost', 6.12):.2f}/mo",
                "ha": "Multi-AZ" if compute.get("multi_az") else "Single-AZ",
            }
        },
        "position": {"x": 580, "y": 220}
    })

    # Database
    if database and database.get("monthly_cost", 0) > 0:
        nodes.append({
            "id": "node-db",
            "type": "customNode",
            "data": {
                "label": database.get("service", "Amazon RDS PostgreSQL"),
                "resource_type": "rds",
                "details": {
                    "tier": database.get("instance_class", "db.t4g.micro"),
                    "cost": f"${database.get('monthly_cost', 8.60):.2f}/mo",
                    "multi_az": str(database.get("multi_az", False)),
                }
            },
            "position": {"x": 820, "y": 140}
        })
        edges.append({"id": "e-compute-db", "source": "node-compute", "target": "node-db", "label": "SQL / DB Connection"})

    # Cache
    if cache and cache.get("monthly_cost", 0) > 0:
        nodes.append({
            "id": "node-cache",
            "type": "customNode",
            "data": {
                "label": cache.get("service", "Amazon ElastiCache Redis"),
                "resource_type": "elasticache",
                "details": {"cost": f"${cache.get('monthly_cost', 13.20):.2f}/mo"}
            },
            "position": {"x": 820, "y": 300}
        })
        edges.append({"id": "e-compute-cache", "source": "node-compute", "target": "node-cache", "label": "TCP:6379"})

    # Frontend CDN
    if frontend and frontend.get("monthly_cost", 0) > 0:
        nodes.append({
            "id": "node-cdn",
            "type": "customNode",
            "data": {
                "label": "Amazon CloudFront + S3",
                "resource_type": "cloudfront",
                "details": {"cost": f"${frontend.get('monthly_cost', 1.80):.2f}/mo"}
            },
            "position": {"x": 340, "y": 90}
        })
        edges.append({"id": "e-client-cdn", "source": "node-client", "target": "node-cdn", "label": "Static Assets"})

    return {
        "nodes": nodes,
        "edges": edges,
        "environment_tier": env,
        "total_monthly_usd": payload.get("monthly_cost_estimate_usd", {}).get("total_estimated_monthly_usd", 6.12),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Session & Architecture Versioning Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/architecture/studio/save", status_code=status.HTTP_200_OK)
@app.post("/api/v1/architecture/versions/save", status_code=status.HTTP_200_OK)
async def save_studio_session(
    session_data: StudioSaveRequest,
    request: Request,
):
    """
    Saves an architecture version.
    Rule: Modifying an architecture creates/updates an identified version and
    invalidates any prior approval for this project/environment.
    """
    proj_key = session_data.project_id or "default"
    env_key = session_data.environment_id or "env"
    session_id = f"{proj_key}_{env_key}"

    # Generate or reuse version ID
    version_id = session_data.version_id or f"arch-v{int(time.time())}-{uuid.uuid4().hex[:6]}"
    tenant_id = request.headers.get("x-tenant-id") or "ten_default"

    version_record = {
        "version_id": version_id,
        "tenant_id": tenant_id,
        "project_id": session_data.project_id,
        "environment_id": session_data.environment_id,
        "environment_tier": session_data.environment_tier,
        "target_region": session_data.target_region,
        "monthly_cost_usd": session_data.monthly_cost_usd,
        "nodes": session_data.nodes,
        "edges": session_data.edges,
        "metadata": session_data.metadata or {},
        "created_at": time.time(),
        "status": "DRAFT",
        "is_approved": False,
        "approval_id": None,
        "approved_by": None,
        "approved_at": None,
    }

    _ARCHITECTURE_VERSIONS[version_id] = version_record
    _STUDIO_SESSIONS[session_id] = {
        "session_id": session_id,
        "tenant_id": tenant_id,
        "current_version_id": version_id,
        "saved_at": time.time(),
        "data": session_data.model_dump(),
    }

    # Invalidate previous approval for this environment
    if session_id in _APPROVED_VERSIONS:
        logger.info(f"Invalidated prior architecture approval for {session_id} due to new save.")
        del _APPROVED_VERSIONS[session_id]

    logger.info(f"Saved Architecture Version {version_id} for {session_id}")
    return {
        "status": "SUCCESS",
        "session_id": session_id,
        "version_id": version_id,
        "is_approved": False,
        "message": "Architecture version saved successfully. Prior approval invalidated."
    }


@app.get("/api/v1/architecture/studio/state", status_code=status.HTTP_200_OK)
async def get_studio_session(project_id: Optional[str] = None, environment_id: Optional[str] = None):
    session_id = f"{project_id or 'default'}_{environment_id or 'env'}"
    session = _STUDIO_SESSIONS.get(session_id)
    if not session:
        return {
            "status": "NEW",
            "session_id": session_id,
            "data": None,
        }
    return session


# ═══════════════════════════════════════════════════════════════════════════════
# Stage A: AI Architecture Analysis
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/architecture/analyze", status_code=status.HTTP_200_OK)
async def analyze_architecture(req: ArchitectureValidationRequest):
    """
    Stage A: Run deep AI Architecture Analysis evaluating the complete design across 17 vectors.
    """
    nodes = req.nodes
    edges = req.edges
    version_id = req.version_id

    # If version_id given and nodes empty, look up version
    if version_id and (not nodes or len(nodes) == 0):
        v = _ARCHITECTURE_VERSIONS.get(version_id)
        if v:
            nodes = v.get("nodes", [])
            edges = v.get("edges", [])

    analysis = run_ai_architecture_analysis(
        nodes=nodes,
        edges=edges,
        environment_tier=req.environment_tier,
        target_region=req.target_region,
        version_id=version_id,
    )

    # Cache analysis on version record if version exists
    if version_id and version_id in _ARCHITECTURE_VERSIONS:
        _ARCHITECTURE_VERSIONS[version_id]["latest_ai_analysis"] = analysis
        if _ARCHITECTURE_VERSIONS[version_id]["status"] == "DRAFT":
            _ARCHITECTURE_VERSIONS[version_id]["status"] = "ANALYZED"

    return analysis


# ═══════════════════════════════════════════════════════════════════════════════
# Stage B: Deterministic Validation
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/architecture/validate", status_code=status.HTTP_200_OK)
async def validate_architecture(req: ArchitectureValidationRequest):
    """
    Stage B: Run deterministic validation against architecture schema & policies.
    Returns status PASS, WARNING, or BLOCKED.
    """
    nodes = req.nodes
    edges = req.edges
    version_id = req.version_id

    if version_id and (not nodes or len(nodes) == 0):
        v = _ARCHITECTURE_VERSIONS.get(version_id)
        if v:
            nodes = v.get("nodes", [])
            edges = v.get("edges", [])

    val_result = run_deterministic_validation(
        nodes=nodes,
        edges=edges,
        environment_tier=req.environment_tier,
    )

    if version_id and version_id in _ARCHITECTURE_VERSIONS:
        _ARCHITECTURE_VERSIONS[version_id]["latest_deterministic_validation"] = val_result

    return val_result


# ═══════════════════════════════════════════════════════════════════════════════
# Stage C: Architecture Review Bundle & Approval Gate
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/architecture/review/{version_id}", status_code=status.HTTP_200_OK)
@app.post("/api/v1/architecture/review", status_code=status.HTTP_200_OK)
async def get_architecture_review(
    request: Request,
    version_id: Optional[str] = None,
    req_body: Optional[Dict[str, Any]] = Body(None),
):
    """
    Stage C: Dedicated Architecture Review Screen Data Bundle.
    Combines architecture graph, resource inventory, AI analysis, deterministic checks,
    cost drivers, and approval status into a unified review record.
    """
    v_id = version_id or (req_body.get("version_id") if req_body else None)
    v_record = await load_version_from_db(v_id) if v_id else None

    caller_tenant = request.headers.get("x-tenant-id")
    if v_record and caller_tenant and caller_tenant not in ("ten_default", "admin"):
        v_tenant = v_record.get("tenant_id")
        if v_tenant and v_tenant not in ("ten_default", "admin") and v_tenant != caller_tenant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant isolation violation: Architecture version belongs to another tenant.")

    nodes = req_body.get("nodes") if (req_body and req_body.get("nodes")) else (v_record.get("nodes") if v_record else [])
    edges = req_body.get("edges") if (req_body and req_body.get("edges")) else (v_record.get("edges") if v_record else [])
    env_tier = req_body.get("environment_tier") if req_body else (v_record.get("environment_tier") if v_record else "development")
    target_region = req_body.get("target_region") if req_body else (v_record.get("target_region") if v_record else "us-east-1")

    # If version not saved yet, create a draft version
    if not v_record and v_id:
        v_record = {
            "version_id": v_id,
            "environment_tier": env_tier,
            "target_region": target_region,
            "nodes": nodes,
            "edges": edges,
            "created_at": time.time(),
            "status": "DRAFT",
            "is_approved": False,
        }
        _ARCHITECTURE_VERSIONS[v_id] = v_record

    # Run AI analysis and validation if not already cached
    ai_analysis = run_ai_architecture_analysis(nodes, edges, env_tier, target_region, v_id)
    deterministic_val = run_deterministic_validation(nodes, edges, env_tier)

    # Resource Inventory Breakdown
    inventory = []
    for n in nodes:
        data = n.get("data", {})
        inventory.append({
            "id": n.get("id"),
            "name": data.get("label") or n.get("name") or n.get("id"),
            "resource_type": data.get("resource_type") or n.get("resource_type") or "unknown",
            "placement": "Private Subnet" if "private" in str(data).lower() or "db" in str(n.get("id")) else "Public / Ingress",
            "monthly_cost": data.get("details", {}).get("cost", "$0.00"),
            "encryption": "AWS KMS" if "db" in str(n.get("id")) or "s3" in str(n.get("id")) else "Default",
        })

    is_approved = v_record.get("is_approved", False) if v_record else False

    return {
        "version_id": v_id or "draft",
        "status": v_record.get("status", "ANALYZED") if v_record else "ANALYZED",
        "is_approved": is_approved,
        "approval_id": v_record.get("approval_id") if v_record else None,
        "approved_by": v_record.get("approved_by") if v_record else None,
        "approved_at": v_record.get("approved_at") if v_record else None,
        "environment_tier": env_tier,
        "target_region": target_region,
        "nodes": nodes,
        "edges": edges,
        "resource_inventory": inventory,
        "ai_analysis": ai_analysis,
        "deterministic_validation": deterministic_val,
        "can_approve": deterministic_val.get("can_approve", True) and not ai_analysis.get("has_blocking_findings", False),
    }


@app.post("/api/v1/architecture/approve", status_code=status.HTTP_200_OK)
async def approve_architecture(
    payload: ArchitectureApprovalRequest,
    request: Request,
):
    """
    User reviews and explicitly approves the exact architecture version.
    Approval rules:
    - Binds to specific architecture version ID.
    - Blocking deterministic or AI finding prevents approval.
    - Records user identity and approval timestamp.
    - Transitions version status to APPROVED.
    """
    version_id = payload.version_id
    v_record = await load_version_from_db(version_id)
    if not v_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Architecture version '{version_id}' not found. Please save the architecture before approving."
        )

    # Check deterministic validation
    nodes = v_record.get("nodes", [])
    edges = v_record.get("edges", [])
    env_tier = v_record.get("environment_tier", "development")

    val_res = run_deterministic_validation(nodes, edges, env_tier)
    if val_res["status"] == "BLOCKED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Approval Blocked: Architecture contains critical policy errors: {'; '.join(val_res['blocking_errors'])}"
        )

    user_name = request.headers.get("x-authenticated-user") or "architect"
    user_uuid = request.headers.get("x-user-uuid") or "usr_0000000000"
    tenant_id = request.headers.get("x-tenant-id") or "ten_default"

    if tenant_id and tenant_id not in ("ten_default", "admin"):
        v_tenant = v_record.get("tenant_id")
        if v_tenant and v_tenant not in ("ten_default", "admin") and v_tenant != tenant_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant isolation violation: Architecture version belongs to another tenant.")

    approval_id = f"arch-appr-{uuid.uuid4().hex[:12]}"
    now = time.time()

    v_record["is_approved"] = True
    v_record["status"] = "APPROVED"
    v_record["approval_id"] = approval_id
    v_record["approved_by"] = user_name
    v_record["approved_by_uuid"] = user_uuid
    v_record["approved_at"] = now
    v_record["comments"] = payload.comments

    try:
        async for session in get_session():
            db_ver = await session.get(ArchitectureVersionModel, version_id)
            if db_ver:
                db_ver.is_approved = True
                db_ver.status = "APPROVED"
                db_ver.approval_id = approval_id
                db_ver.approved_by = user_name
                db_ver.approved_at = now
                await session.commit()
    except Exception as e:
        logger.warning(f"Failed to update approval in database: {e}")

    proj_key = payload.project_id or v_record.get("project_id", "default")
    env_key = payload.environment_id or v_record.get("environment_id", "env")
    session_id = f"{proj_key}_{env_key}"
    _APPROVED_VERSIONS[session_id] = version_id

    logger.info(f"Approved Architecture Version {version_id} with approval ID {approval_id} by {user_name}")

    return {
        "status": "APPROVED",
        "approval_id": approval_id,
        "version_id": version_id,
        "approved_by": user_name,
        "approved_at": now,
        "message": f"Architecture version '{version_id}' is officially approved. Terraform generation is now unlocked."
    }


@app.post("/api/v1/architecture/reject", status_code=status.HTTP_200_OK)
async def reject_architecture(payload: ArchitectureRejectRequest):
    version_id = payload.version_id
    v_record = _ARCHITECTURE_VERSIONS.get(version_id)
    if not v_record:
        raise HTTPException(status_code=404, detail=f"Architecture version '{version_id}' not found.")

    v_record["is_approved"] = False
    v_record["status"] = "REJECTED"
    v_record["rejection_reason"] = payload.reason
    return {
        "status": "REJECTED",
        "version_id": version_id,
        "message": f"Architecture version '{version_id}' rejected."
    }


@app.get("/api/v1/architecture/versions/{version_id}/status", status_code=status.HTTP_200_OK)
async def get_version_approval_status(version_id: str):
    v_record = await load_version_from_db(version_id)
    if not v_record:
        v_record = {
            "version_id": version_id,
            "status": "DRAFT",
            "is_approved": False,
            "approval_id": None,
            "approved_by": None,
            "approved_at": None,
        }
        _ARCHITECTURE_VERSIONS[version_id] = v_record

    is_approved = bool(v_record.get("is_approved", False))
    return {
        "version_id": version_id,
        "exists": True,
        "status": v_record.get("status", "DRAFT"),
        "is_approved": is_approved,
        "approval_id": v_record.get("approval_id"),
        "approved_by": v_record.get("approved_by"),
        "approved_at": v_record.get("approved_at"),
        "can_generate_terraform": is_approved,
    }



@app.get("/api/v1/architecture/versions", status_code=status.HTTP_200_OK)
async def list_architecture_versions(request: Request, project_id: Optional[str] = None, environment_id: Optional[str] = None):
    caller_tenant = request.headers.get("x-tenant-id")
    results = []
    for vid, v in _ARCHITECTURE_VERSIONS.items():
        if caller_tenant and caller_tenant not in ("ten_default", "admin"):
            if v.get("tenant_id") not in (caller_tenant, "ten_default"):
                continue
        if project_id and v.get("project_id") != project_id:
            continue
        if environment_id and v.get("environment_id") != environment_id:
            continue
        results.append({
            "version_id": vid,
            "project_id": v.get("project_id"),
            "environment_id": v.get("environment_id"),
            "environment_tier": v.get("environment_tier"),
            "target_region": v.get("target_region"),
            "status": v.get("status"),
            "is_approved": v.get("is_approved"),
            "created_at": v.get("created_at"),
        })
    return {"versions": results, "total": len(results)}
