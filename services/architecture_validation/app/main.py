import time
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    ArchitectureValidationRequest,
    ArchitectureValidationResponse,
    ValidationFinding
)
from app.validator import validate_architecture, SUPPORTED_AWS_RESOURCE_TYPES

logger = logging.getLogger("architecture-validation-service")

app = FastAPI(
    title="AetherOps AI - Architecture Validation Service",
    description="Module 7: Architecture structure, compatibility, security policy, and dependency validation (Port 8006)",
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
        "service": "AetherOps AI — Architecture Validation Service (Module 7)",
        "version": "2.0.0",
        "port": 8006,
        "endpoints": {
            "health": "/health",
            "validate": "/api/v1/architecture/validate",
            "review": "/api/v1/architecture/review",
            "rules": "/api/v1/validation/rules",
            "docs": "/docs"
        }
    }

@app.get("/health", status_code=status.HTTP_200_OK)
@app.get("/api/v1/validation/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "architecture-validation-service",
        "port": 8006,
        "timestamp": time.time()
    }

@app.get("/api/v1/validation/rules")
async def get_validation_rules():
    return {
        "supported_resource_types": sorted(list(SUPPORTED_AWS_RESOURCE_TYPES)),
        "rules": [
            {"id": "VAL-INGRESS-01", "name": "Ingress Layer Requirement", "blocking": True},
            {"id": "VAL-COMPUTE-01", "name": "Compute Runtime Requirement", "blocking": True},
            {"id": "VAL-PROD-HA-01", "name": "Production Multi-AZ Resilience", "blocking": False},
            {"id": "VAL-COMPAT", "name": "AWS Resource Type Catalog Compatibility", "blocking": False},
        ]
    }

@app.post("/api/v1/architecture/validate", response_model=ArchitectureValidationResponse)
@app.post("/api/v1/architecture/review", response_model=ArchitectureValidationResponse)
@app.post("/api/v1/validation/run", response_model=ArchitectureValidationResponse)
async def run_validation(req: ArchitectureValidationRequest):
    logger.info(f"Running architecture validation for project={req.project_id}, node_count={len(req.nodes)}")
    try:
        res = validate_architecture(req)
        return res
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Architecture validation failure: {str(e)}"
        )
