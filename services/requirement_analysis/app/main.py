# services/requirement_analysis/app/main.py
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import time
import logging
import asyncio

from app.schemas import RequirementInput, RequirementProfileOutput
from app.engine import analyze_requirements
from app.database import get_db_session, AsyncSessionLocal
from app.cache import cache_manager
from app.seed import init_db, seed_catalog
from app.admin_router import admin_router
from app.sync_helper import sync_catalog_from_aws

import os

# Setup logs directory relative to this service root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)
log_file_path = os.path.join(logs_dir, "requirement_analysis.log")

# Configure logging
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

# File handler
file_handler = logging.FileHandler(log_file_path)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
# Clear existing handlers to prevent duplicates
root_logger.handlers = []
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

logger = logging.getLogger("requirement-analysis-service")

async def rotate_catalog_on_startup():
    logger.info("Lifespan startup: Rotating catalog data from AWS APIs...")
    try:
        async with AsyncSessionLocal() as session:
            await sync_catalog_from_aws(session)
        logger.info("Lifespan startup: Catalog data rotated successfully.")
    except Exception as e:
        logger.error(f"Lifespan startup: Failed to rotate catalog data: {e}", exc_info=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Logic
    logger.info("Starting up Requirement Analysis Service...")
    await cache_manager.connect()
    
    try:
        await init_db()
        async with AsyncSessionLocal() as session:
            await seed_catalog(session)
        # Trigger catalog rotation on spinup asynchronously
        asyncio.create_task(rotate_catalog_on_startup())
    except Exception as e:
        logger.error(f"Failed to initialize and seed database: {e}", exc_info=True)
        
    yield
    
    # Shutdown Logic
    logger.info("Shutting down Requirement Analysis Service...")
    await cache_manager.disconnect()

app = FastAPI(
    title="AetherOps AI - Requirement Analysis Service",
    description="Deterministic cloud architecture profiling engine (Module 1)",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request, exc: ValidationError):
    logger.warning(f"Validation error occurred: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "message": "Input validation failed. Please check your parameters."
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    logger.error(f"Unhandled exception occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "An internal server error occurred while processing your request.",
            "error": str(exc)
        }
    )

@app.get("/")
async def root():
    return {
        "service": "AetherOps AI - Requirement Analysis Service (Module 1)",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "analyze": "/api/v1/analyze",
            "docs": "/docs"
        }
    }

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "requirement-analysis-service",
        "timestamp": time.time()
    }

@app.post("/api/v1/analyze", response_model=RequirementProfileOutput, status_code=status.HTTP_200_OK)
async def analyze_workload_requirements(
    payload: RequirementInput,
    db: AsyncSession = Depends(get_db_session)
):
    logger.info(f"Received requirement profile request: Project={payload.project_name}, Traffic={payload.traffic_scale}, Reliability={payload.reliability}")
    try:
        result = await analyze_requirements(payload, db)
        return result
    except Exception as e:
        logger.error(f"Engine failed to analyze requirements: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compile requirement profile: {str(e)}"
        )
