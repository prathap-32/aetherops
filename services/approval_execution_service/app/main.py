import time
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.schemas import (
    DeploymentApproveRequest,
    DeploymentApproveResponse,
    DeploymentExecuteRequest
)
from app.approval_engine import (
    approve_plan,
    execute_deployment,
    _APPROVALS,
    _DEPLOYMENTS,
    _DEPLOYMENT_LOGS
)

logger = logging.getLogger("approval-execution-service")

app = FastAPI(
    title="AetherOps AI - Approval & Execution Service",
    description="Module 9: Approval Gate (plan hash verification) & Infrastructure Execution Engine (Port 8009)",
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
        "service": "AetherOps AI — Approval & Execution Service (Module 9)",
        "version": "2.0.0",
        "port": 8009,
        "endpoints": {
            "health": "/health",
            "approve": "/api/v1/deployments/approve",
            "execute": "/api/v1/deployments/execute",
            "logs": "/api/v1/deployments/{id}/logs",
            "docs": "/docs"
        }
    }

@app.get("/health", status_code=status.HTTP_200_OK)
@app.get("/api/v1/execution/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "approval-execution-service",
        "port": 8009,
        "timestamp": time.time()
    }

@app.post("/api/v1/deployments/approve", response_model=DeploymentApproveResponse, status_code=status.HTTP_200_OK)
@app.post("/api/v1/approvals/approve", response_model=DeploymentApproveResponse, status_code=status.HTTP_200_OK)
async def approve_endpoint(req: DeploymentApproveRequest, request: Request):
    user_identity = {
        "username": request.headers.get("x-authenticated-user") or req.approver or "admin",
        "tenant_id": request.headers.get("x-tenant-id") or "ten_default"
    }
    logger.info(f"Processing approval for plan='{req.plan_id}' by '{user_identity['username']}'")
    try:
        res = approve_plan(req, user_identity)
        return res
    except ValueError as ve:
        logger.warning(f"Approval rejected: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Approval failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Approval failure: {str(e)}")

@app.get("/api/v1/approvals/{plan_id}", status_code=status.HTTP_200_OK)
async def get_approval(plan_id: str):
    approval = _APPROVALS.get(plan_id)
    if not approval:
        raise HTTPException(status_code=404, detail=f"No approval record found for plan '{plan_id}'.")
    return approval

@app.post("/api/v1/deployments/execute", status_code=status.HTTP_200_OK)
async def execute_endpoint(req: DeploymentExecuteRequest, request: Request):
    user_identity = {
        "username": request.headers.get("x-authenticated-user") or "admin",
        "tenant_id": request.headers.get("x-tenant-id") or "ten_default"
    }
    logger.info(f"Executing deployment for plan='{req.plan_id}'")
    try:
        res = execute_deployment(req, user_identity)
        return res
    except ValueError as ve:
        logger.warning(f"Execution rejected: {ve}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except RuntimeError as re:
        logger.warning(f"Execution lock conflict: {re}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(re))
    except Exception as e:
        logger.error(f"Execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Execution failure: {str(e)}")

@app.get("/api/v1/deployments/{deployment_id}/logs", status_code=status.HTTP_200_OK)
async def get_logs(deployment_id: str):
    logs = _DEPLOYMENT_LOGS.get(deployment_id)
    if logs is None:
        raise HTTPException(status_code=404, detail=f"Deployment '{deployment_id}' logs not found.")
    return {"deployment_id": deployment_id, "logs": logs}

@app.get("/api/v1/deployments/{deployment_id}", status_code=status.HTTP_200_OK)
async def get_deployment(deployment_id: str):
    dep = _DEPLOYMENTS.get(deployment_id)
    if not dep:
        raise HTTPException(status_code=404, detail=f"Deployment '{deployment_id}' not found.")
    return dep
