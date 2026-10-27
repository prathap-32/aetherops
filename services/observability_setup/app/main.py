# services/observability_setup/app/main.py
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from app.schemas import ObservabilitySetupRequest, ObservabilitySetupResponse
from app.observability_engine import generate_observability_suite

logger = logging.getLogger("observability-setup-service")

app = FastAPI(
    title="AetherOps AI - Observability & Telemetry Setup Service",
    description="Module 7: CloudWatch Alarms, OpenTelemetry & Grafana Manifest Synthesizer",
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
        "service": "AetherOps AI - Observability & Telemetry Service (Module 7)",
        "version": "1.0.0",
        "port": 8010,
        "endpoints": {
            "health": "/health",
            "generate-observability": "/api/v1/generate-observability",
            "docs": "/docs"
        }
    }

@app.get("/health", status_code=status.HTTP_200_OK)
@app.get("/api/v1/monitoring/health", status_code=status.HTTP_200_OK)
@app.get("/api/v1/observability/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "observability-setup-service",
        "port": 8010,
        "timestamp": time.time()
    }

@app.post("/api/v1/generate-observability", response_model=ObservabilitySetupResponse, status_code=status.HTTP_200_OK)
@app.post("/api/v1/monitoring/generate-observability", response_model=ObservabilitySetupResponse, status_code=status.HTTP_200_OK)
@app.post("/api/v1/observability/generate-observability", response_model=ObservabilitySetupResponse, status_code=status.HTTP_200_OK)
async def generate_telemetry_stack(request: ObservabilitySetupRequest):
    logger.info(f"Synthesizing observability stack for project='{request.project_name}'")
    try:
        res = generate_observability_suite(request)
        return res
    except Exception as e:
        logger.error(f"Observability generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Observability setup failure: {str(e)}"
        )
