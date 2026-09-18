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
import logging
import httpx
import time

from app.schemas import RequirementInput, RequirementProfileOutput
from app.models import RequirementProject
from app.database import get_requirements_db, get_sqlite_sessionmaker
from app.engine import analyze_and_explain_requirements
from app.cache import cache_manager

logger = logging.getLogger("requirement-analysis-router")

requirements_router = APIRouter(tags=["Requirements Analysis & Sizing"])

MODULE_2_URL = "http://localhost:8002/api/v1/generate-graph"


def _hash_input(payload: RequirementInput) -> str:
    serialized = json.dumps(payload.model_dump(), sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]


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
            detail=f"Could not reach Module 2 (Architecture Generator) at {MODULE_2_URL}. Ensure port 8002 is running."
        )


@requirements_router.get("/app", response_class=HTMLResponse)
async def serve_module_1_ui():
    """
    Renders the dedicated interactive AWS Management Console UI for Module 1.
    """
    from app.module1_page import get_module1_page_html
    return HTMLResponse(content=get_module1_page_html())
