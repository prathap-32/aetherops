# services/security_scanner/app/main.py
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from app.schemas import SecurityScanRequest, SecurityScanResponse
from app.scanner_engine import evaluate_security_posture

logger = logging.getLogger("security-scanner-service")

app = FastAPI(
    title="AetherOps AI - Security Scanner & Compliance Service",
    description="Module 5: CIS AWS Foundations Benchmark & Zero-Trust Governance Engine",
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
        "service": "AetherOps AI - Security Scanner Service (Module 5)",
        "version": "1.0.0",
        "port": 8005,
        "endpoints": {
            "health": "/health",
            "scan": "/api/v1/scan",
            "docs": "/docs"
        }
    }

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "security-scanner-service",
        "port": 8005,
        "timestamp": time.time()
    }

@app.post("/api/v1/scan", response_model=SecurityScanResponse, status_code=status.HTTP_200_OK)
async def scan_infrastructure_security(request: SecurityScanRequest):
    logger.info(f"Scanning security posture for project='{request.project_name}'")
    try:
        res = evaluate_security_posture(request)
        return res
    except Exception as e:
        logger.error(f"Security scan failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Security scanner failure: {str(e)}"
        )
