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
import os

from app.schemas import RequirementInput, RequirementProfileOutput, RecommendationInput, RecommendationOutput
from app.engine import analyze_requirements, recommend_infrastructure
from app.database import get_db_session, AsyncSessionLocal, SUPPORTED_REGIONS, get_sessionmaker_for_region, init_db_for_region
from app.cache import cache_manager, get_region_catalog
from app.seed import init_db, seed_catalog, seed_sample_requirements
from app.admin_router import admin_router
from app.requirements_router import requirements_router
from app.sync_helper import sync_catalog_from_aws
from app.terminal_ui import print_banner, run_startup_diagnostics, render_catalog_dashboard, print_shutdown_banner
from rich.logging import RichHandler

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
console_handler = RichHandler(
    level=logging.INFO,
    show_time=True,
    show_level=True,
    show_path=False,
    markup=True,
    rich_tracebacks=True
)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
# Clear existing handlers to prevent duplicates
root_logger.handlers = []
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# Silence or format other logs with RichHandler
for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
    l = logging.getLogger(logger_name)
    l.handlers = [console_handler]
    l.propagate = False

logger = logging.getLogger("requirement-analysis-service")

async def background_db_init_and_sync():
    logger.info("Lifespan startup: Starting background non-blocking seeding and sync for all 39 regions...")
    sem = asyncio.Semaphore(5)
    
    async def seed_and_sync_one(region):
        async with sem:
            try:
                logger.info(f"Background worker: Initializing database and cache for region '{region}'...")
                await init_db_for_region(region)
                session_factory = get_sessionmaker_for_region(region)
                async with session_factory() as session:
                    await seed_catalog(session, region=region)
                    # Auto-warm Redis cache immediately for this region
                    await get_region_catalog(region, session)
                logger.info(f"Background worker: Initialized DB and warmed Redis cache for region '{region}'.")
            except Exception as e:
                logger.error(f"Background worker error for region '{region}': {e}", exc_info=True)

    await asyncio.gather(*(seed_and_sync_one(r) for r in SUPPORTED_REGIONS))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Print Banner
    print_banner()
    
    # 2. Dynamic step-by-step progress spinner
    await run_startup_diagnostics()
    
    # Startup Logic
    logger.info("Starting up Requirement Analysis Service...")
    await cache_manager.connect()
    
    try:
        await init_db()
        from app.auth import init_admin_security
        await init_admin_security()
        await seed_sample_requirements()
    except Exception as e:
        logger.error(f"Failed to initialize default database: {e}", exc_info=True)
        
    # Start background db init and sync tasks asynchronously without blocking startup
    asyncio.create_task(background_db_init_and_sync())
    
    # 3. Print Regional Matrix & Endpoints Panel
    await render_catalog_dashboard()
    
    yield
    
    # Shutdown Logic
    logger.info("Shutting down Requirement Analysis Service...")
    await cache_manager.disconnect()
    
    # 4. Graceful Shutdown Card
    print_shutdown_banner()

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

from fastapi.staticfiles import StaticFiles

app.include_router(admin_router)
app.include_router(requirements_router)

static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


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
            "app_console": "/app",
            "admin_console": "/admin",
            "health": "/health",
            "analyze": "/api/v1/analyze",
            "requirements_api": "/api/v1/requirements",
            "catalog": "/api/v1/catalog/{region}",
            "recommendation": "/api/v1/recommendation",
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

@app.get("/api/v1/catalog/{region}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_regional_catalog(
    region: str,
    db: AsyncSession = Depends(get_db_session)
):
    region_lower = region.lower().strip()
    if region_lower not in SUPPORTED_REGIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported region '{region}'. Must be one of: {', '.join(SUPPORTED_REGIONS)}"
        )
    try:
        catalog = await get_region_catalog(region_lower, db)
        return catalog
    except Exception as e:
        logger.error(f"Failed to fetch catalog for region {region_lower}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load catalog: {str(e)}"
        )

@app.post("/api/v1/recommendation", response_model=RecommendationOutput, status_code=status.HTTP_200_OK)
async def recommend_regional_infra(
    payload: RecommendationInput,
    db: AsyncSession = Depends(get_db_session)
):
    region_lower = payload.region.lower().strip()
    if region_lower not in SUPPORTED_REGIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported region '{payload.region}'. Must be one of: {', '.join(SUPPORTED_REGIONS)}"
        )
    logger.info(f"Received infrastructure recommendation request for region {region_lower}, stack={payload.tech_stack}")
    try:
        session_factory = get_sessionmaker_for_region(region_lower)
        async with session_factory() as session:
            result = await recommend_infrastructure(payload, session)
            return result
    except Exception as e:
        logger.error(f"Recommendation engine failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compile recommendation: {str(e)}"
        )
