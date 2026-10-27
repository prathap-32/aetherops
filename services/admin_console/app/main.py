# services/admin_console/app/main.py
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
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
    logger.info("Starting up AetherOps Admin Console Control Plane on port 8012...")
    await cache_manager.connect()
    
    try:
        await init_admin_security()
    except Exception as e:
        logger.error(f"Failed to initialize admin security: {e}", exc_info=True)

    # Pre-seed us-east-1 default catalog so catalog is always loaded immediately on startup
    try:
        from app.database import init_db_for_region, get_sessionmaker_for_region
        from app.seed import seed_catalog
        await init_db_for_region("us-east-1")
        sf = get_sessionmaker_for_region("us-east-1")
        async with sf() as session:
            await seed_catalog(session, region="us-east-1", force=False)
            logger.info("Default catalog for us-east-1 verified and seeded.")
    except Exception as e:
        logger.warning(f"Default catalog seeding: {e}")

    asyncio.create_task(background_catalog_warm())
    yield

    logger.info("Shutting down AetherOps Admin Console...")
    await cache_manager.disconnect()
    print_shutdown_banner()


app = FastAPI(
    title="AetherOps AI - Admin Console Control Plane",
    description="Central AWS Management Console, Catalog Manager, and Microservices Telemetry Control Plane (Port 8012)",
    version="1.0.0",
    lifespan=lifespan
)

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000,http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(admin_router)


@app.get("/")
async def root(request: Request):
    from app.auth import SESSION_COOKIE_NAME, decode_access_token
    cookie_token = request.cookies.get(SESSION_COOKIE_NAME)
    if cookie_token and decode_access_token(cookie_token):
        return RedirectResponse(url="/admin")
    return RedirectResponse(url="/admin/login?redirect=/admin", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "admin-console-service",
        "port": 8012,
        "timestamp": time.time()
    }

