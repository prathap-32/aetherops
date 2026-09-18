# services/cloud_deployer/app/main.py
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from app.schemas import (
    DeploymentRequest,
    DeploymentResponse,
    DriftDetectionRequest,
    DriftDetectionResponse
)
from app.deployer_engine import execute_cloud_deployment, audit_infrastructure_drift

logger = logging.getLogger("cloud-deployer-service")

app = FastAPI(
    title="AetherOps AI - Cloud Deployer & Drift Engine",
    description="Module 8: Autonomous Cloud Deployer & Continuous Drift Detection",
    version="1.0.0"
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
        "version": "1.0.0",
        "port": 8008,
        "endpoints": {
            "health": "/health",
            "deploy": "/api/v1/deploy",
            "drift-detection": "/api/v1/drift-detection",
            "docs": "/docs"
        }
    }

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "cloud-deployer-service",
        "port": 8008,
        "timestamp": time.time()
    }

@app.post("/api/v1/deploy", response_model=DeploymentResponse, status_code=status.HTTP_200_OK)
async def deploy_infrastructure(request: DeploymentRequest):
    logger.info(f"Initiating deployment for project='{request.project_name}'")
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
