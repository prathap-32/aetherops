# services/requirement_analysis/app/requirements_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, desc
from typing import List, Optional
import hashlib
import json
import uuid
import os
import logging
import httpx
import time
from pydantic import BaseModel, Field

from app.schemas import RequirementInput, RequirementProfileOutput, NaturalLanguagePromptRequest
from app.models import RequirementProject, EC2Catalog, RDSCatalog
from app.catalog import EC2_CATALOG, RDS_CATALOG
from app.database import get_requirements_db, get_sqlite_sessionmaker
from app.engine import analyze_and_explain_requirements
from app.cache import cache_manager
from app.ai_advisor import ai_parse_requirements_with_llm_fallback
from app.instance_finder import InstanceFinderInput, InstanceFinderOutput, evaluate_decision_matrix



# ---------------------------------------------------------------------------
# Request model for repository-scan endpoint (Task 3)
# ---------------------------------------------------------------------------

class AnalyzeRepoRequest(BaseModel):
    repo_path: Optional[str] = Field(
        default=None,
        description="Absolute or relative path to the repository root directory to scan",
        examples=["/home/user/my-project", "../../my-repo"],
    )
    repo_url: Optional[str] = Field(
        default=None,
        description="Optional Git repository URL",
    )
    traffic_profile: Optional[str] = Field(
        default=None,
        description="Traffic scale profile",
    )
    budget_tier: Optional[str] = Field(
        default=None,
        description="Budget tier",
    )
    project_name: Optional[str] = Field(
        None,
        description="Override the project name (defaults to repo folder name)",
    )
    monthly_budget: Optional[float] = Field(
        None,
        ge=0.0,
        description="Optional monthly cost cap in USD forwarded to the sizing engine",
    )
    traffic_scale: Optional[str] = Field(
        None,
        description="Force traffic scale: hobby_dev / growth / production",
    )
    reliability: Optional[str] = Field(
        None,
        description="Force reliability tier: dev_testing / production_safe / mission_critical",
    )
    target_region: Optional[str] = Field(
        default="us-east-1",
        description="Target AWS region for sizing catalog lookup",
    )
    auto_save: bool = Field(
        default=True,
        description="Whether to persist the analyzed project in requirements.db",
    )


logger = logging.getLogger("requirement-analysis-router")

requirements_router = APIRouter(tags=["Requirements Analysis & Sizing"])

MODULE_2_URL = os.getenv("ARCH_SERVICE_URL", "http://localhost:8005/api/v1/generate-graph")


def _hash_input(payload: RequirementInput) -> str:
    serialized = json.dumps(payload.model_dump(), sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@requirements_router.post("/api/v1/requirements/parse-prompt", status_code=status.HTTP_200_OK)
async def parse_prompt_endpoint(payload: NaturalLanguagePromptRequest):
    """
    Parses unstructured plain-English requirements into strongly-typed architecture parameters.
    Returns the parsed parameters with high confidence and $0 API cost (zero hallucination).
    """
    parsed_res = await ai_parse_requirements_with_llm_fallback(payload.prompt)
    return {
        "status": "SUCCESS",
        "engine_used": parsed_res["engine_used"],
        "confidence_score": parsed_res["confidence_score"],
        "parsed_input": parsed_res["parsed_input"].model_dump()
    }


@requirements_router.post("/api/v1/requirements/ai-analyze", status_code=status.HTTP_200_OK)
async def ai_analyze_requirements_endpoint(
    payload: NaturalLanguagePromptRequest,
    db: AsyncSession = Depends(get_requirements_db)
):
    """
    End-to-End AI Architecture Analysis from Natural Language:
    1. Extracts technical parameters from prompt (deterministic / hybrid LLM).
    2. Sizes infrastructure against SQLite regional catalog and Redis L1 cache.
    3. Generates 'Why That Service' technical rationales.
    4. Calculates FinOps cost optimizations (Savings Plans, Multi-AZ vs Single-AZ, Spot).
    5. Evaluates AWS Well-Architected Framework 6-Pillar scorecard.
    6. Optionally persists project in SQLite requirements.db.
    """
    parsed_res = await ai_parse_requirements_with_llm_fallback(payload.prompt)
    req_input: RequirementInput = parsed_res["parsed_input"]

    target_reg = payload.target_region or "us-east-1"
    cache_key = f"req:ai_analysis:{_hash_input(req_input)}:{target_reg}"
    cached_result = await cache_manager.get_json(cache_key)

    if cached_result is not None:
        logger.info(f"Redis L1 cache hit for AI analysis {cache_key}")
        result = cached_result
    else:
        logger.info(f"Executing AI sizing analysis for '{req_input.project_name}' in region '{target_reg}'...")
        cat_sf = get_sqlite_sessionmaker(target_reg)
        async with cat_sf() as cat_session:
            result = await analyze_and_explain_requirements(req_input, cat_session)
        await cache_manager.set_json(cache_key, result, ttl=3600)

    project_id = None
    if payload.auto_save:
        project_id = str(uuid.uuid4())
        project = RequirementProject(
            id=project_id,
            project_name=req_input.project_name,
            description=f"AI-analyzed from prompt: {payload.prompt[:150]}...",
            stream=req_input.stream.value,
            target_region=target_reg,
            traffic_scale=req_input.traffic_scale.value,
            reliability=req_input.reliability.value,
            security_need=req_input.security_need.value,
            data_storage_gb=req_input.data_storage_gb,
            monthly_budget=req_input.monthly_budget,
            tech_stack=json.dumps(req_input.technology.model_dump()),
            operations=json.dumps(req_input.operations.model_dump()),
            monitoring=json.dumps(req_input.monitoring.model_dump()),
            architecture_tier=result["architecture_tier"],
            estimated_monthly_cost=result["total_estimated_cost"],
            cost_breakdown=json.dumps(result["cost_breakdown"]),
            service_rationales=json.dumps(result["service_rationales"]),
            cost_optimizations=json.dumps(result["cost_optimizations"]),
            profile_output=json.dumps(result["profile"]),
            status="ANALYZED"
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        logger.info(f"Persisted AI requirement project {project_id} in requirements.db")

    return {
        "status": "SUCCESS",
        "prompt": payload.prompt,
        "engine_used": parsed_res["engine_used"],
        "confidence_score": parsed_res["confidence_score"],
        "parsed_input": req_input.model_dump(),
        "project_id": project_id,
        "data": result,
        "data_source": {
            "sqlite_catalog_partition": f"catalog_{target_reg}.db",
            "redis_cache": "aether_redis",
            "pricing_guarantee": "100% Grounded in Official AWS Pricing (Zero Hallucination)"
        }
    }


@requirements_router.post("/api/v1/repo/scan-and-size", status_code=status.HTTP_200_OK)
@requirements_router.post("/api/v1/repo/scan", status_code=status.HTTP_200_OK)
@requirements_router.post("/api/v1/requirements/analyze-repo", status_code=status.HTTP_200_OK)
async def analyze_repo_endpoint(
    payload: AnalyzeRepoRequest,
    db: AsyncSession = Depends(get_requirements_db)
):
    """
    Repository-Driven Architecture Analysis — Module 3 Integration.

    Scans a local repository using the repo_analyzer library (zero-network,
    zero-LLM, deterministic), maps the detected tech stack to a RequirementInput,
    runs the full Module 1 sizing engine against the regional SQLite catalog, and returns:

    - ``scan_result``   — raw repository fingerprint (languages, frameworks, DBs, ports, …)
    - ``parsed_input``  — the mapped RequirementInput derived from the scan
    - ``data``          — full Module 1 sizing output (costs, rationales, FinOps, AI advice)
    - ``project_id``    — SQLite requirements.db record ID (when auto_save=True)

    The bridge is deterministic — no LLM calls, no guessing.
    Every mapping decision is traceable to a concrete Finding in the ApplicationProfile.
    """
    from pathlib import Path
    import os

    # 1. Validate repository path
    raw_path = payload.repo_path
    if not raw_path:
        raw_path = os.getenv("WORKSPACE_ROOT", "/home/prathap32/GP/devops-lab/projects/aether-cloud")
    repo_path = Path(raw_path).expanduser().resolve()
    if not repo_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Repository path does not exist: {raw_path}"
        )
    if not repo_path.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Path is not a directory: {raw_path}"
        )

    # 2. Run repo_analyzer bridge (blocking but fast — pure Python file scan)
    try:
        from app.repo_bridge import analyze_repository
        bridge_result = analyze_repository(
            repo_path,
            project_name_override=payload.project_name,
            monthly_budget=payload.monthly_budget,
            traffic_scale_override=payload.traffic_scale,
            reliability_override=payload.reliability,
        )
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"repo_analyzer not installed: {exc}"
        )
    except Exception as exc:
        logger.error("repo_bridge analysis failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Repository scan failed: {str(exc)}"
        )

    req_input = bridge_result.requirement_input
    target_reg = payload.target_region or "us-east-1"

    # 3. Run the full Module 1 sizing engine (with Redis L1 cache)
    cache_key = f"req:repo_analysis:{_hash_input(req_input)}:{target_reg}"
    cached_result = await cache_manager.get_json(cache_key)

    if cached_result is not None:
        logger.info("Redis L1 cache hit for repo analysis %s", cache_key)
        result = cached_result
    else:
        logger.info(
            "Running sizing engine for repo '%s' (region=%s) …",
            bridge_result.repo_name, target_reg
        )
        cat_sf = get_sqlite_sessionmaker(target_reg)
        async with cat_sf() as cat_session:
            result = await analyze_and_explain_requirements(req_input, cat_session)
        await cache_manager.set_json(cache_key, result, ttl=3600)

    # 4. Optionally persist in requirements.db
    project_id = None
    if payload.auto_save:
        project_id = str(uuid.uuid4())
        project = RequirementProject(
            id=project_id,
            project_name=req_input.project_name,
            description=(
                f"Auto-analyzed from repository scan of '{bridge_result.repo_name}'. "
                f"Detected: {', '.join(bridge_result.languages_detected[:5])}. "
                f"Monorepo: {bridge_result.is_monorepo}."
            ),
            stream=req_input.stream.value,
            target_region=target_reg,
            traffic_scale=req_input.traffic_scale.value,
            reliability=req_input.reliability.value,
            security_need=req_input.security_need.value,
            data_storage_gb=req_input.data_storage_gb,
            monthly_budget=req_input.monthly_budget,
            tech_stack=json.dumps(req_input.technology.model_dump()),
            operations=json.dumps(req_input.operations.model_dump()),
            monitoring=json.dumps(req_input.monitoring.model_dump()),
            architecture_tier=result["architecture_tier"],
            estimated_monthly_cost=result["total_estimated_cost"],
            cost_breakdown=json.dumps(result["cost_breakdown"]),
            service_rationales=json.dumps(result["service_rationales"]),
            cost_optimizations=json.dumps(result["cost_optimizations"]),
            profile_output=json.dumps(result["profile"]),
            status="ANALYZED",
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        logger.info("Persisted repo-analyzed project %s in requirements.db", project_id)

    return {
        "status": "SUCCESS",
        "source": "repository_scan",
        "repo_path": str(repo_path),
        "project_id": project_id,
        "scan_result": bridge_result.to_dict(),
        "parsed_input": req_input.model_dump(),
        "data": result,
        "data_source": {
            "sqlite_catalog_partition": f"catalog_{target_reg}.db",
            "redis_cache": "aether_redis",
            "repo_analyzer": "rules-only, zero-network, zero-LLM scan",
            "pricing_guarantee": "100% Grounded in Official AWS Pricing (Zero Hallucination)",
        },
    }


@requirements_router.post("/api/v1/requirements/analyze", status_code=status.HTTP_200_OK)
async def analyze_requirements_endpoint(
    payload: RequirementInput,
    save: bool = Query(False, description="Whether to automatically save this analysis as a project in requirements.db"),
    description: Optional[str] = Query(None, description="Optional description for the project"),
    db: AsyncSession = Depends(get_requirements_db)
):
    """
    Analyzes workload requirements, generating architecture sizing, 'Why That Service' rationales,
    and FinOps cost optimizations. Leverages Redis L1 cache for sub-millisecond retrieval.
    """
    cache_key = f"req:analysis:{_hash_input(payload)}"
    cached_result = await cache_manager.get_json(cache_key)

    if cached_result is not None:
        logger.info(f"Redis L1 cache hit for analysis {cache_key}")
        result = cached_result
    else:
        logger.info(f"Analyzing requirements for project '{payload.project_name}'...")
        cat_sf = get_sqlite_sessionmaker("us-east-1")
        async with cat_sf() as cat_session:
            result = await analyze_and_explain_requirements(payload, cat_session)
        await cache_manager.set_json(cache_key, result, ttl=3600)

    project_id = None
    if save:
        project_id = str(uuid.uuid4())
        project = RequirementProject(
            id=project_id,
            project_name=payload.project_name,
            description=description or f"Workload analysis for {payload.stream.value} stream ({payload.traffic_scale.value} scale).",
            stream=payload.stream.value,
            target_region="us-east-1",
            traffic_scale=payload.traffic_scale.value,
            reliability=payload.reliability.value,
            security_need=payload.security_need.value,
            data_storage_gb=payload.data_storage_gb,
            monthly_budget=payload.monthly_budget,
            tech_stack=json.dumps(payload.technology.model_dump()),
            operations=json.dumps(payload.operations.model_dump()),
            monitoring=json.dumps(payload.monitoring.model_dump()),
            architecture_tier=result["architecture_tier"],
            estimated_monthly_cost=result["total_estimated_cost"],
            cost_breakdown=json.dumps(result["cost_breakdown"]),
            service_rationales=json.dumps(result["service_rationales"]),
            cost_optimizations=json.dumps(result["cost_optimizations"]),
            profile_output=json.dumps(result["profile"]),
            status="ANALYZED"
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        logger.info(f"Persisted requirement project {project_id} in requirements.db")

    return {
        "status": "SUCCESS",
        "project_id": project_id,
        "data": result
    }


@requirements_router.post("/api/v1/requirements", status_code=status.HTTP_201_CREATED)
async def create_requirement_project(
    payload: RequirementInput,
    description: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_requirements_db)
):
    """
    Creates, analyzes, and saves a new architecture requirement project in SQLite requirements.db.
    """
    cat_sf = get_sqlite_sessionmaker("us-east-1")
    async with cat_sf() as cat_session:
        result = await analyze_and_explain_requirements(payload, cat_session)

    project_id = str(uuid.uuid4())
    project = RequirementProject(
        id=project_id,
        project_name=payload.project_name,
        description=description or f"Architecture profile for {payload.project_name}",
        stream=payload.stream.value,
        target_region="us-east-1",
        traffic_scale=payload.traffic_scale.value,
        reliability=payload.reliability.value,
        security_need=payload.security_need.value,
        data_storage_gb=payload.data_storage_gb,
        monthly_budget=payload.monthly_budget,
        tech_stack=json.dumps(payload.technology.model_dump()),
        operations=json.dumps(payload.operations.model_dump()),
        monitoring=json.dumps(payload.monitoring.model_dump()),
        architecture_tier=result["architecture_tier"],
        estimated_monthly_cost=result["total_estimated_cost"],
        cost_breakdown=json.dumps(result["cost_breakdown"]),
        service_rationales=json.dumps(result["service_rationales"]),
        cost_optimizations=json.dumps(result["cost_optimizations"]),
        profile_output=json.dumps(result["profile"]),
        status="ANALYZED"
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    # Invalidate cached list
    await cache_manager.delete("req:recent_list")

    return {
        "status": "CREATED",
        "message": f"Project '{payload.project_name}' saved to requirements.db",
        "project": project.to_dict()
    }


@requirements_router.get("/api/v1/requirements", status_code=status.HTTP_200_OK)
async def list_requirement_projects(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_requirements_db)
):
    """
    Lists all saved requirement projects from SQLite requirements.db.
    """
    query = select(RequirementProject).order_by(desc(RequirementProject.created_at)).limit(limit)
    res = await db.execute(query)
    projects = res.scalars().all()

    items = [p.to_dict() for p in projects]
    return {
        "status": "SUCCESS",
        "count": len(items),
        "projects": items
    }


@requirements_router.get("/api/v1/requirements/{project_id}", status_code=status.HTTP_200_OK)
async def get_requirement_project(
    project_id: str,
    db: AsyncSession = Depends(get_requirements_db)
):
    """
    Retrieves a single requirement project by ID including full specs, rationales, and optimizations.
    """
    query = select(RequirementProject).where(RequirementProject.id == project_id)
    res = await db.execute(query)
    project = res.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement project '{project_id}' not found in requirements.db"
        )

    return {
        "status": "SUCCESS",
        "project": project.to_dict()
    }


@requirements_router.put("/api/v1/requirements/{project_id}", status_code=status.HTTP_200_OK)
async def update_requirement_project(
    project_id: str,
    payload: RequirementInput,
    description: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_requirements_db)
):
    """
    Updates an existing requirement project, re-runs sizing analysis, and persists changes.
    """
    query = select(RequirementProject).where(RequirementProject.id == project_id)
    res = await db.execute(query)
    project = res.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement project '{project_id}' not found"
        )

    cat_sf = get_sqlite_sessionmaker("us-east-1")
    async with cat_sf() as cat_session:
        result = await analyze_and_explain_requirements(payload, cat_session)

    project.project_name = payload.project_name
    if description is not None:
        project.description = description
    project.stream = payload.stream.value
    project.traffic_scale = payload.traffic_scale.value
    project.reliability = payload.reliability.value
    project.security_need = payload.security_need.value
    project.data_storage_gb = payload.data_storage_gb
    project.monthly_budget = payload.monthly_budget
    project.tech_stack = json.dumps(payload.technology.model_dump())
    project.operations = json.dumps(payload.operations.model_dump())
    project.monitoring = json.dumps(payload.monitoring.model_dump())
    project.architecture_tier = result["architecture_tier"]
    project.estimated_monthly_cost = result["total_estimated_cost"]
    project.cost_breakdown = json.dumps(result["cost_breakdown"])
    project.service_rationales = json.dumps(result["service_rationales"])
    project.cost_optimizations = json.dumps(result["cost_optimizations"])
    project.profile_output = json.dumps(result["profile"])
    project.status = "ANALYZED"

    await db.commit()
    await db.refresh(project)
    await cache_manager.delete("req:recent_list")

    return {
        "status": "UPDATED",
        "message": f"Project '{project.project_name}' successfully re-analyzed and updated",
        "project": project.to_dict()
    }


@requirements_router.delete("/api/v1/requirements/{project_id}", status_code=status.HTTP_200_OK)
async def delete_requirement_project(
    project_id: str,
    db: AsyncSession = Depends(get_requirements_db)
):
    """
    Deletes a requirement project from SQLite requirements.db.
    """
    query = select(RequirementProject).where(RequirementProject.id == project_id)
    res = await db.execute(query)
    project = res.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement project '{project_id}' not found"
        )

    await db.delete(project)
    await db.commit()
    await cache_manager.delete("req:recent_list")

    return {
        "status": "DELETED",
        "message": f"Project '{project_id}' deleted successfully"
    }


@requirements_router.post("/api/v1/requirements/{project_id}/dispatch", status_code=status.HTTP_200_OK)
async def dispatch_to_module_2(
    project_id: str,
    db: AsyncSession = Depends(get_requirements_db)
):
    """
    Downstream microservice integration: Dispatches the analyzed requirement profile
    to Module 2 (Architecture Generator on port 8002) to construct the visual ReactFlow diagram.
    """
    query = select(RequirementProject).where(RequirementProject.id == project_id)
    res = await db.execute(query)
    project = res.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Requirement project '{project_id}' not found"
        )

    profile_dict = json.loads(project.profile_output) if project.profile_output else None
    if not profile_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project has no compiled profile output. Please re-analyze first."
        )

    # Call Module 2 over HTTP REST
    logger.info(f"Dispatching project '{project.project_name}' to Module 2 ({MODULE_2_URL})...")
    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(MODULE_2_URL, json=profile_dict)

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Module 2 returned error {response.status_code}: {response.text}"
                )

            graph_data = response.json()
            elapsed_ms = int((time.time() - start_time) * 1000)

            # Record dispatch state in SQLite
            project.dispatched_to_m2 = True
            project.status = "DISPATCHED_TO_M2"
            project.m2_graph_summary = json.dumps({
                "nodes_count": len(graph_data.get("nodes", [])),
                "edges_count": len(graph_data.get("edges", [])),
                "dispatch_duration_ms": elapsed_ms,
                "dispatched_at": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            await db.commit()
            await db.refresh(project)

            logger.info(f"Module 2 returned graph with {len(graph_data.get('nodes', []))} nodes in {elapsed_ms}ms.")

            return {
                "status": "DISPATCHED_SUCCESSFULLY",
                "target_module": "Module 2 (Architecture Generator :8002)",
                "dispatch_duration_ms": elapsed_ms,
                "graph_nodes": len(graph_data.get("nodes", [])),
                "graph_edges": len(graph_data.get("edges", [])),
                "graph": graph_data,
                "project": project.to_dict()
            }

    except httpx.RequestError as e:
        logger.error(f"Failed to communicate with Module 2: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not reach Module 2 (Architecture Generator) at {MODULE_2_URL}. Ensure port 8005 is running."
        )


@requirements_router.post("/api/v1/instance-finder/evaluate", response_model=InstanceFinderOutput, status_code=status.HTTP_200_OK)
async def evaluate_instance_type_finder(payload: InstanceFinderInput):
    """
    Evaluates candidate instances using Core Math Decision Matrix (TOPSIS)
    and Probabilistic SLA Headroom Modeling (Gaussian Error Function erf).
    """
    target_reg = payload.region or "us-east-1"
    candidates = []

    # 1. Attempt to query regional SQLite catalog
    try:
        cat_sf = get_sqlite_sessionmaker(target_reg)
        async with cat_sf() as session:
            if payload.service_type.lower() == "rds":
                stmt = select(RDSCatalog).where(
                    RDSCatalog.vcpus >= payload.min_vcpus,
                    RDSCatalog.ram_gb >= payload.min_ram_gb
                )
                if payload.max_vcpus:
                    stmt = stmt.where(RDSCatalog.vcpus <= payload.max_vcpus)
                if payload.max_ram_gb:
                    stmt = stmt.where(RDSCatalog.ram_gb <= payload.max_ram_gb)
                res = await session.execute(stmt)
                db_items = res.scalars().all()
                candidates = [it.to_dict() for it in db_items]
            else:
                stmt = select(EC2Catalog).where(
                    EC2Catalog.vcpus >= payload.min_vcpus,
                    EC2Catalog.ram_gb >= payload.min_ram_gb
                )
                if payload.max_vcpus:
                    stmt = stmt.where(EC2Catalog.vcpus <= payload.max_vcpus)
                if payload.max_ram_gb:
                    stmt = stmt.where(EC2Catalog.ram_gb <= payload.max_ram_gb)
                res = await session.execute(stmt)
                db_items = res.scalars().all()
                candidates = [it.to_dict() for it in db_items]
    except Exception as e:
        logger.warning(f"Could not load instances from SQLite catalog for {target_reg}: {e}")
        candidates = []

    # 2. In-memory baseline fallback if SQLite is empty or unseeded
    if not candidates:
        if payload.service_type.lower() == "rds":
            for spec in RDS_CATALOG:
                if spec.vcpus >= payload.min_vcpus and spec.ram_gb >= payload.min_ram_gb:
                    if payload.max_vcpus and spec.vcpus > payload.max_vcpus:
                        continue
                    if payload.max_ram_gb and spec.ram_gb > payload.max_ram_gb:
                        continue
                    candidates.append({
                        "instance_type": spec.instance_type,
                        "vcpus": spec.vcpus,
                        "ram_gb": spec.ram_gb,
                        "price_per_hour": spec.price_per_hour,
                        "category": spec.category,
                        "network_performance": "Up to 10 Gbps"
                    })
        else:
            for spec in EC2_CATALOG:
                if spec.vcpus >= payload.min_vcpus and spec.ram_gb >= payload.min_ram_gb:
                    if payload.max_vcpus and spec.vcpus > payload.max_vcpus:
                        continue
                    if payload.max_ram_gb and spec.ram_gb > payload.max_ram_gb:
                        continue
                    candidates.append({
                        "instance_type": spec.instance_type,
                        "vcpus": spec.vcpus,
                        "ram_gb": spec.ram_gb,
                        "price_per_hour": spec.price_per_hour,
                        "category": spec.category,
                        "network_performance": spec.network_performance
                    })

    # 3. Evaluate Decision Matrix
    return evaluate_decision_matrix(candidates, payload)


@requirements_router.get("/app", response_class=HTMLResponse)
async def serve_module_1_ui():
    """
    Renders the dedicated interactive AWS Management Console UI for Module 1.
    """
    from app.module1_page import get_module1_page_html
    return HTMLResponse(content=get_module1_page_html())

