import time
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import DeploymentRequest, DeploymentResponse
from app.deployer_engine import deploy_application, list_releases, _RELEASES

logger = logging.getLogger("application-deployment-service")

app = FastAPI(
    title="AetherOps AI - Application Deployment Service",
    description="Module 10: Container image builds, registry integration, runtime configuration, and release tracking (Port 8010)",
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
        "service": "AetherOps AI — Application Deployment Service (Module 10)",
        "version": "2.0.0",
        "port": 8010,
        "endpoints": {
            "health": "/health",
            "deploy": "/api/v1/deploy",
            "releases": "/api/v1/deployments/releases",
            "docs": "/docs"
        }
    }

@app.get("/health", status_code=status.HTTP_200_OK)
@app.get("/api/v1/deploy/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "application-deployment-service",
        "port": 8010,
        "timestamp": time.time()
    }

@app.post("/api/v1/deploy", response_model=DeploymentResponse, status_code=status.HTTP_200_OK)
async def deploy_endpoint(req: DeploymentRequest):
    logger.info(f"Deploying application service='{req.service_name}', region='{req.target_region}'")
    try:
        res = deploy_application(req)
        return res
    except Exception as e:
        logger.error(f"Application deployment failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Application deployment failure: {str(e)}"
        )

@app.get("/api/v1/deployments/releases", status_code=status.HTTP_200_OK)
async def get_releases(project_id: Optional[str] = None):
    return {"releases": list_releases(project_id)}

@app.get("/api/v1/deployments/releases/{release_id}", status_code=status.HTTP_200_OK)
async def get_release(release_id: str):
    rel = _RELEASES.get(release_id)
    if not rel:
        raise HTTPException(status_code=404, detail=f"Release '{release_id}' not found.")
    return rel
