# services/cicd_pipeline/app/main.py
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from app.schemas import PipelineGenerationRequest, PipelineGenerationResponse
from app.pipeline_engine import generate_cicd_pipeline

logger = logging.getLogger("cicd-pipeline-service")

app = FastAPI(
    title="AetherOps AI - CI/CD Pipeline & GitOps Delivery Service",
    description="Module 6: Multi-Stage GitHub Actions & GitLab CI Pipeline Synthesizer",
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
        "service": "AetherOps AI - CI/CD Pipeline Service (Module 6)",
        "version": "1.0.0",
        "port": 8009,
        "endpoints": {
            "health": "/health",
            "generate-pipeline": "/api/v1/generate-pipeline",
            "docs": "/docs"
        }
    }

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "cicd-pipeline-service",
        "port": 8009,
        "timestamp": time.time()
    }

@app.post("/api/v1/generate-pipeline", response_model=PipelineGenerationResponse, status_code=status.HTTP_200_OK)
async def generate_pipeline(request: PipelineGenerationRequest):
    logger.info(f"Synthesizing CI/CD pipeline for project='{request.project_name}', platform='{request.platform}'")
    try:
        res = generate_cicd_pipeline(request)
        return res
    except Exception as e:
        logger.error(f"Pipeline synthesis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CI/CD generator error: {str(e)}"
        )
