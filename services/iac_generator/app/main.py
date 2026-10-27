# services/iac_generator/app/main.py
import logging
import os
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

from app.schemas import IaCGenerationRequest, IaCGenerationResponse
from app.iac_engine import generate_terraform_hcl

logger = logging.getLogger("iac-generator-service")

app = FastAPI(
    title="AetherOps AI - IaC Code Generator Service",
    description="Module 3: Terraform & OpenTofu HCL Infrastructure Synthesizer",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ARCH_SERVICE_URL = os.getenv("ARCH_SERVICE_URL", "http://127.0.0.1:8005")

def verify_architecture_approval(version_id: Optional[str]) -> Dict[str, Any]:
    """
    Mandatory Section 5 & 8 Approval Gate:
    Verifies that the architecture topology has been reviewed and explicitly approved
    by the platform engineer before allowing Terraform code synthesis.
    """
    if not version_id or not str(version_id).strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Approval Gate Violation: 'architecture_version_id' is required. "
                   "Architecture must be reviewed and approved before Terraform synthesis can proceed."
        )

    vid = str(version_id).strip()


    # Query Architecture Studio Service (Port 8005)
    try:
        with httpx.Client(timeout=4.0) as client:
            resp = client.get(f"{ARCH_SERVICE_URL}/api/v1/architecture/versions/{vid}/status")
            if resp.status_code == 200:
                data = resp.json()
                if not data.get("is_approved"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Approval Gate Violation: Architecture version '{vid}' is not approved "
                               f"(status: '{data.get('status', 'UNAPPROVED')}'). You must approve the architecture "
                               f"in Architecture Review before generating Terraform."
                    )
                return data
            elif resp.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Approval Gate Violation: Architecture version '{vid}' was not found in Architecture Studio."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Approval Gate Verification Failed: Architecture service returned unexpected status {resp.status_code}."
                )
    except httpx.RequestError as exc:
        logger.warning(f"Architecture service unreachable at {ARCH_SERVICE_URL}: {exc}")
        # Reject by default if verification cannot be confirmed
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Approval Gate Verification Failed: Could not contact Architecture Service to verify version '{vid}': {exc}"
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Approval Gate Verification Failed: Unexpected state during architecture approval check."
    )


@app.get("/")
async def root():
    return {
        "service": "AetherOps AI - IaC Code Generator Service (Module 3)",
        "version": "2.0.0",
        "port": 8006,
        "endpoints": {
            "health": "/health",
            "generate-iac": "/api/v1/generate-iac",
            "iac-generate": "/api/v1/iac/generate",
            "docs": "/docs"
        }
    }

@app.get("/health", status_code=status.HTTP_200_OK)
@app.get("/api/v1/iac/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "iac-generator-service",
        "port": 8006,
        "timestamp": time.time()
    }

@app.post("/api/v1/generate-iac", response_model=IaCGenerationResponse, status_code=status.HTTP_200_OK)
@app.post("/api/v1/iac/generate", response_model=IaCGenerationResponse, status_code=status.HTTP_200_OK)
@app.post("/api/v1/iac/generate-iac", response_model=IaCGenerationResponse, status_code=status.HTTP_200_OK)
async def generate_iac(request: IaCGenerationRequest):
    logger.info(f"Checking architecture approval for version='{request.architecture_version_id}'")
    # Enforce mandatory architecture approval gate
    verify_architecture_approval(request.architecture_version_id)

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

