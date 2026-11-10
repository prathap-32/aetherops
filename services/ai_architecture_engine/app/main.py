import time
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    ArchitectureRecommendationRequest,
    ArchitectureRecommendationResponse,
    RequirementProfileOutput
)
from app.engine import build_recommendation
from app.catalog import EC2_CATALOG, RDS_CATALOG

logger = logging.getLogger("ai-architecture-engine")

app = FastAPI(
    title="AetherOps AI - AI Architecture Engine",
    description="Module 4: AI Architecture recommendation, catalog analysis, and topology specs (Port 8004)",
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
        "service": "AetherOps AI — AI Architecture Engine (Module 4)",
        "version": "2.0.0",
        "port": 8004,
        "endpoints": {
            "health": "/health",
            "recommend": "/api/v1/recommendation",
            "catalog": "/api/v1/catalog",
            "docs": "/docs"
        }
    }

@app.get("/health", status_code=status.HTTP_200_OK)
@app.get("/api/v1/architecture/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-architecture-engine",
        "port": 8004,
        "timestamp": time.time()
    }

@app.get("/api/v1/catalog")
async def get_catalog():
    return {
        "ec2": [e.model_dump() for e in EC2_CATALOG],
        "rds": [r.model_dump() for r in RDS_CATALOG]
    }

@app.post("/api/v1/recommendation", response_model=ArchitectureRecommendationResponse)
@app.post("/api/v1/architecture/recommend", response_model=ArchitectureRecommendationResponse)
@app.post("/api/v1/requirements/analyze", response_model=ArchitectureRecommendationResponse)
async def recommend_architecture(req: ArchitectureRecommendationRequest):
    logger.info(f"Generating architecture recommendation for project={req.project_id}, tier={req.environment_tier}")
    try:
        res = build_recommendation(req)
        return ArchitectureRecommendationResponse(**res)
    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Architecture recommendation failure: {str(e)}"
        )
