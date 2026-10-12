# services/iac_generator/app/main.py
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from app.schemas import IaCGenerationRequest, IaCGenerationResponse
from app.iac_engine import generate_terraform_hcl

logger = logging.getLogger("iac-generator-service")

app = FastAPI(
    title="AetherOps AI - IaC Code Generator Service",
    description="Module 3: Terraform & OpenTofu HCL Infrastructure Synthesizer",
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
        "service": "AetherOps AI - IaC Code Generator Service (Module 3)",
        "version": "1.0.0",
        "port": 8006,
        "endpoints": {
            "health": "/health",
            "generate-iac": "/api/v1/generate-iac",
            "docs": "/docs"
        }
    }

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "iac-generator-service",
        "port": 8006,
        "timestamp": time.time()
    }

@app.post("/api/v1/generate-iac", response_model=IaCGenerationResponse, status_code=status.HTTP_200_OK)
async def generate_iac(request: IaCGenerationRequest):
    logger.info(f"Generating IaC files for project='{request.project_name}', region='{request.aws_region}'")
    try:
        response = generate_terraform_hcl(request)
        return response
    except Exception as e:
        logger.error(f"IaC generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate IaC modules: {str(e)}"
        )
