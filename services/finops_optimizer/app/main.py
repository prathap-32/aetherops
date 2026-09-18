# services/finops_optimizer/app/main.py
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from app.schemas import FinOpsOptimizationRequest, FinOpsOptimizationResponse
from app.finops_engine import calculate_finops_optimizations

logger = logging.getLogger("finops-optimizer-service")

app = FastAPI(
    title="AetherOps AI - FinOps Cost Optimizer Service",
    description="Module 4: AWS Cost Arbitrage, Commitment Modeling & TCO Engine",
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
        "service": "AetherOps AI - FinOps Cost Optimizer Service (Module 4)",
        "version": "1.0.0",
        "port": 8004,
        "endpoints": {
            "health": "/health",
            "optimize": "/api/v1/optimize",
            "docs": "/docs"
        }
    }

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "finops-optimizer-service",
        "port": 8004,
        "timestamp": time.time()
    }

@app.post("/api/v1/optimize", response_model=FinOpsOptimizationResponse, status_code=status.HTTP_200_OK)
async def optimize_workload_costs(request: FinOpsOptimizationRequest):
    logger.info(f"Computing FinOps model for project='{request.project_name}'")
    try:
        res = calculate_finops_optimizations(request)
        return res
    except Exception as e:
        logger.error(f"FinOps optimization calculation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FinOps optimizer error: {str(e)}"
        )
