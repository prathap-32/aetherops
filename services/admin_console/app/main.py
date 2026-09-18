# services/admin_console/app/main.py
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from contextlib import asynccontextmanager
import time
import logging
import asyncio
import os

from app.database import init_db_for_region, SUPPORTED_REGIONS, get_sessionmaker_for_region
from app.cache import cache_manager, get_region_catalog
from app.auth import init_admin_security
from app.admin_router import admin_router
from app.terminal_ui import print_banner, run_startup_diagnostics, render_catalog_dashboard, print_shutdown_banner
from rich.logging import RichHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)
log_file_path = os.path.join(logs_dir, "admin_console.log")

log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
file_handler = logging.FileHandler(log_file_path)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

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
root_logger.handlers = [file_handler, console_handler]

for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
    l = logging.getLogger(logger_name)
    l.handlers = [console_handler]
    l.propagate = False

logger = logging.getLogger("admin-console-service")


async def background_catalog_warm():
    logger.info("Admin Console: Warming regional pricing catalog in background...")
    sem = asyncio.Semaphore(5)
    
    async def warm_one(region):
        async with sem:
            try:
                await init_db_for_region(region)
                sf = get_sessionmaker_for_region(region)
                async with sf() as session:
                    await get_region_catalog(region, session)
            except Exception as e:
                logger.debug(f"Catalog warm for {region}: {e}")

    await asyncio.gather(*(warm_one(r) for r in SUPPORTED_REGIONS[:10]))


@asynccontextmanager
async def lifespan(app: FastAPI):
    print_banner()
    logger.info("Starting up AetherOps Admin Console Control Plane on port 2470...")
    await cache_manager.connect()
    
    try:
        await init_admin_security()
    except Exception as e:
        logger.error(f"Failed to initialize admin security: {e}", exc_info=True)

    asyncio.create_task(background_catalog_warm())
    yield

    logger.info("Shutting down AetherOps Admin Console...")
    await cache_manager.disconnect()
    print_shutdown_banner()


app = FastAPI(
    title="AetherOps AI - Admin Console & Fleet Gateway",
    description="Central AWS Management Console, Catalog Manager, and Microservices Telemetry Control Plane (Port 2470)",
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


@app.get("/")
async def root():
    return RedirectResponse(url="/admin")


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "admin-console-service",
        "port": 2470,
        "timestamp": time.time()
    }
