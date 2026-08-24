# services/architecture_generator/app/main.py
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import time
import logging

from app.schemas import RequirementProfileOutput, ReactFlowGraphJSON
from app.generator import generate_architecture_graph

import os

# Setup logs directory relative to this service root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)
log_file_path = os.path.join(logs_dir, "architecture_generator.log")

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

logger = logging.getLogger("architecture-generator-service")

app = FastAPI(
    title="AetherOps AI - Cloud Architecture Generator Service",
    description="Deterministic visual layout builder (Module 2)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "service": "AetherOps AI - Cloud Architecture Generator Service (Module 2)",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "generate-graph": "/api/v1/generate-graph",
            "docs": "/docs"
        }
    }

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "architecture-generator-service",
        "timestamp": time.time()
    }

@app.post("/api/v1/generate-graph", response_model=ReactFlowGraphJSON, status_code=status.HTTP_200_OK)
async def generate_graph_from_profile(profile: RequirementProfileOutput):
    logger.info(f"Received graph generation request for tier={profile.architecture_tier}")
    try:
        graph = generate_architecture_graph(profile)
        return graph
    except Exception as e:
        logger.error(f"Generator failed to produce architecture graph: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate architecture graph: {str(e)}"
        )
