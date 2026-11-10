import time
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    DeploymentPlanRequest,
    DeploymentPlanResponse,
    ResourceChange,
    RiskFinding
)
from app.risk_engine import create_deployment_plan, evaluate_plan_risk, _PLANS

logger = logging.getLogger("pre-deployment-risk-engine")

app = FastAPI(
    title="AetherOps AI - Pre-Deployment Dry Run & Risk Engine",
    description="Module 6: Pre-Deployment plan evaluation, 6-pillar risk assessment, cost headroom, and destructive change detection (Port 8007)",
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
        "service": "AetherOps AI — Pre-Deployment Dry Run & Risk Engine (Module 6)",
        "version": "2.0.0",
        "port": 8007,
        "endpoints": {
            "health": "/health",
            "plan": "/api/v1/deployments/plan",
            "get_plan": "/api/v1/deployments/plan/{plan_id}",
            "dry_run": "/api/v1/dry-run/analyze",
            "docs": "/docs"
        }
    }

@app.get("/health", status_code=status.HTTP_200_OK)
@app.get("/api/v1/risk/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "pre-deployment-risk-engine",
        "port": 8007,
        "timestamp": time.time()
    }

@app.post("/api/v1/deployments/plan", response_model=DeploymentPlanResponse, status_code=status.HTTP_200_OK)
@app.post("/api/v1/dry-run/analyze", response_model=DeploymentPlanResponse, status_code=status.HTTP_200_OK)
async def plan_deployment(req: DeploymentPlanRequest, request: Request):
    if not req.tenant_id:
        req.tenant_id = request.headers.get("x-tenant-id") or "ten_default"
    logger.info(f"Generating pre-deployment risk analysis for project='{req.project_name}', region='{req.target_region}'")
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
@app.get("/api/v1/dry-run/{plan_id}", status_code=status.HTTP_200_OK)
async def get_plan(plan_id: str):
    plan = _PLANS.get(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail=f"Plan '{plan_id}' not found.")
    return plan
