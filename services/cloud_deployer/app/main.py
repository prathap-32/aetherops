# services/cloud_deployer/app/main.py
import asyncio
import logging
import os
import time
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, status, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from app.schemas import (
    DeploymentRequest,
    DeploymentResponse,
    DriftDetectionRequest,
    DriftDetectionResponse,
    DeploymentPlanRequest,
    DeploymentPlanResponse,
    DeploymentApproveRequest,
    DeploymentApproveResponse,
    DeploymentExecuteRequest,
)
from app.deployer_engine import (
    execute_cloud_deployment,
    audit_infrastructure_drift,
    create_deployment_plan,
    approve_deployment_plan,
    run_deployment_execution,
    _PLANS,
    _DEPLOYMENTS,
    _DEPLOYMENT_LOGS,
    _DEPLOYED_RESOURCES,
    _ACTIVE_LOCKS
)

logger = logging.getLogger("cloud-deployer-service")

app = FastAPI(
    title="AetherOps AI - Cloud Deployer & Continuous Drift Engine",
    description="Module 8: Pre-Deployment Planning, Risk Assessment, Gated Approvals, and Execution (Port 8011)",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "AetherOps AI - Cloud Deployer Service (Module 8)",
        "version": "2.0.0",
        "port": 8011,
        "endpoints": {
            "health": "/health",
            "plan": "/api/v1/deployments/plan",
            "approve": "/api/v1/deployments/approve",
            "execute": "/api/v1/deployments/execute",
            "stream": "/api/v1/deployments/{id}/stream",
            "logs": "/api/v1/deployments/{id}/logs",
            "resources": "/api/v1/deployments/{id}/resources",
            "deploy": "/api/v1/deploy",
            "drift": "/api/v1/drift-detection",
            "docs": "/docs"
        }
    }


@app.get("/health", status_code=status.HTTP_200_OK)
@app.get("/api/v1/deployments/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "cloud-deployer-service",
        "port": 8011,
        "timestamp": time.time()
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Stage C Pre-Deployment Dry Run & Risk Planning
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/deployments/plan", response_model=DeploymentPlanResponse, status_code=status.HTTP_200_OK)
async def plan_deployment(req: DeploymentPlanRequest, request: Request):
    if not req.tenant_id:
        req.tenant_id = request.headers.get("x-tenant-id") or "ten_default"
    logger.info(f"Generating pre-deployment plan for project='{req.project_name}', region='{req.target_region}', tenant='{req.tenant_id}'")
    try:
        plan_response = create_deployment_plan(req)
        return plan_response
    except Exception as e:
        logger.error(f"Planning failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pre-deployment planning failure: {str(e)}"
        )


@app.get("/api/v1/deployments/plan/{plan_id}", status_code=status.HTTP_200_OK)
async def get_plan(plan_id: str, request: Request):
    plan = _PLANS.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Plan '{plan_id}' not found.")
    caller_tenant = request.headers.get("x-tenant-id")
    if caller_tenant and caller_tenant not in ("ten_default", "admin"):
        plan_tenant = plan.get("tenant_id")
        if plan_tenant and plan_tenant not in ("ten_default", "admin") and plan_tenant != caller_tenant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant Isolation Violation: Plan belongs to another tenant.")
    return plan


# ═══════════════════════════════════════════════════════════════════════════════
# Cryptographically Gated Deployment Approval
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/deployments/approve", response_model=DeploymentApproveResponse, status_code=status.HTTP_200_OK)
async def approve_deployment(req: DeploymentApproveRequest, request: Request):
    user_identity = {
        "user_name": request.headers.get("x-authenticated-user") or "engineer",
        "user_uuid": request.headers.get("x-user-uuid") or request.headers.get("x-user-id") or "usr_0000000000",
        "tenant_id": request.headers.get("x-tenant-id") or "ten_default",
    }
    logger.info(f"Approving deployment plan='{req.plan_id}' by user='{user_identity['user_name']}'")
    try:
        approval_receipt = approve_deployment_plan(
            plan_id=req.plan_id,
            plan_digest=req.plan_digest,
            user_identity=user_identity,
            comments=req.comments,
            override_blocked=req.override_blocked
        )
        return approval_receipt
    except ValueError as ve:
        logger.warning(f"Deployment approval rejected: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Deployment approval failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Execution Gate & State-Locked Runner
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/deployments/execute", status_code=status.HTTP_200_OK)
async def execute_deployment(req: DeploymentExecuteRequest, request: Request):
    user_identity = {
        "user_name": request.headers.get("x-authenticated-user") or "engineer",
        "user_uuid": request.headers.get("x-user-uuid") or request.headers.get("x-user-id") or "usr_0000000000",
        "tenant_id": request.headers.get("x-tenant-id") or "ten_default",
    }
    logger.info(f"Executing deployment for plan='{req.plan_id}'")
    try:
        execution_record = run_deployment_execution(
            plan_id=req.plan_id,
            user_identity=user_identity,
            requested_mode=req.execution_mode,
            aws_access_key_id=req.aws_access_key_id,
            aws_secret_access_key=req.aws_secret_access_key,
            aws_region=req.aws_region
        )
        return execution_record
    except ValueError as ve:
        logger.warning(f"Deployment execution rejected: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except RuntimeError as re:
        logger.warning(f"Deployment state lock conflict: {re}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(re))
    except Exception as e:
        logger.error(f"Deployment execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# Real-Time Log Streaming & Resource Inventory
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/deployments/{deployment_id}/logs", status_code=status.HTTP_200_OK)
async def get_deployment_logs(deployment_id: str, request: Request):
    dep = _DEPLOYMENTS.get(deployment_id)
    caller_tenant = request.headers.get("x-tenant-id")
    if dep and caller_tenant and caller_tenant not in ("ten_default", "admin"):
        dep_tenant = dep.get("tenant_id")
        if dep_tenant and dep_tenant not in ("ten_default", "admin") and dep_tenant != caller_tenant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant Isolation Violation: Deployment belongs to another tenant.")

    logs = _DEPLOYMENT_LOGS.get(deployment_id)
    if logs is None:
        raise HTTPException(status_code=404, detail=f"No logs found for deployment '{deployment_id}'.")
    return {"deployment_id": deployment_id, "logs": logs, "total_lines": len(logs)}


@app.get("/api/v1/deployments/{deployment_id}/stream")
async def stream_deployment_logs(deployment_id: str, request: Request):
    dep = _DEPLOYMENTS.get(deployment_id)
    caller_tenant = request.headers.get("x-tenant-id")
    if dep and caller_tenant and caller_tenant not in ("ten_default", "admin"):
        dep_tenant = dep.get("tenant_id")
        if dep_tenant and dep_tenant not in ("ten_default", "admin") and dep_tenant != caller_tenant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant Isolation Violation: Deployment belongs to another tenant.")

    logs = _DEPLOYMENT_LOGS.get(deployment_id)
    if logs is None:
        raise HTTPException(status_code=404, detail=f"No deployment found for '{deployment_id}'.")

    async def event_generator():
        sent_count = 0
        while sent_count < len(logs):
            line = logs[sent_count]
            yield f"data: {line}\n\n"
            sent_count += 1
            await asyncio.sleep(0.05)
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/v1/deployments/{deployment_id}/resources", status_code=status.HTTP_200_OK)
async def get_deployment_resources(deployment_id: str, request: Request):
    dep = _DEPLOYMENTS.get(deployment_id)
    caller_tenant = request.headers.get("x-tenant-id")
    if dep and caller_tenant and caller_tenant not in ("ten_default", "admin"):
        dep_tenant = dep.get("tenant_id")
        if dep_tenant and dep_tenant not in ("ten_default", "admin") and dep_tenant != caller_tenant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant Isolation Violation: Deployment belongs to another tenant.")

    resources = _DEPLOYED_RESOURCES.get(deployment_id)
    if resources is None:
        raise HTTPException(status_code=404, detail=f"No resources found for deployment '{deployment_id}'.")
    return {"deployment_id": deployment_id, "resources": resources, "count": len(resources)}


@app.post("/api/v1/deployments/{deployment_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_deployment(deployment_id: str, request: Request):
    dep = _DEPLOYMENTS.get(deployment_id)
    if not dep:
        raise HTTPException(status_code=404, detail=f"Deployment '{deployment_id}' not found.")

    caller_tenant = request.headers.get("x-tenant-id")
    if caller_tenant and caller_tenant not in ("ten_default", "admin"):
        dep_tenant = dep.get("tenant_id")
        if dep_tenant and dep_tenant not in ("ten_default", "admin") and dep_tenant != caller_tenant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant Isolation Violation: Deployment belongs to another tenant.")

    proj = dep.get("project_name")
    if proj in _ACTIVE_LOCKS and _ACTIVE_LOCKS[proj] == deployment_id:
        _ACTIVE_LOCKS.pop(proj, None)

    dep["status"] = "CANCELLED"
    if deployment_id in _DEPLOYMENT_LOGS:
        _DEPLOYMENT_LOGS[deployment_id].append("[WARN] Deployment cancelled by operator request. State lock released.")

    return {"status": "CANCELLED", "deployment_id": deployment_id, "message": "Deployment successfully cancelled."}


@app.get("/api/v1/deployments", status_code=status.HTTP_200_OK)
async def list_deployments(request: Request, project_id: Optional[str] = None):
    caller_tenant = request.headers.get("x-tenant-id")
    results = list(_DEPLOYMENTS.values())
    if caller_tenant and caller_tenant not in ("ten_default", "admin"):
        results = [d for d in results if d.get("tenant_id") in (caller_tenant, "ten_default")]
    if project_id:
        results = [d for d in results if d.get("project_name") == project_id]
    return {"deployments": results, "total": len(results)}


# ═══════════════════════════════════════════════════════════════════════════════
# Backwards Compatible Endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/deploy", response_model=DeploymentResponse, status_code=status.HTTP_200_OK)
async def deploy_infrastructure(request: DeploymentRequest):
    logger.info(f"Initiating backwards-compatible deployment for project='{request.project_name}'")
    try:
        res = execute_cloud_deployment(request)
        return res
    except Exception as e:
        logger.error(f"Deployment failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deployment execution failure: {str(e)}"
        )


@app.post("/api/v1/drift-detection", response_model=DriftDetectionResponse, status_code=status.HTTP_200_OK)
async def detect_drift(request: DriftDetectionRequest):
    logger.info(f"Auditing state drift for project='{request.project_name}'")
    try:
        res = audit_infrastructure_drift(request)
        return res
    except Exception as e:
        logger.error(f"Drift detection failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Drift detection failure: {str(e)}"
        )
