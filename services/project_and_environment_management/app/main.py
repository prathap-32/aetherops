# services/project_and_environment_management/app/main.py
import sys
import os

_service_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_root_dir = os.path.dirname(_service_dir)
_shared_dir = os.path.join(_root_dir, "shared")
for p in (_service_dir, _shared_dir, _root_dir):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from aetherops_common.secrets import load_application_secrets
    load_application_secrets()
except Exception:
    pass
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from rich.logging import RichHandler

from app.database import init_projects_db
from app.auth import init_admin_security, SESSION_COOKIE_NAME, decode_access_token, MASTER_ADMIN_KEY
from app.cache import cache_manager
from app.seed import seed_initial_data
from app.router import router
from app.dashboard_page import get_dashboard_html
from app.project_page import get_project_detail_html
from app.terminal_ui import print_banner, run_startup_diagnostics, print_shutdown_banner

# ── Logging ───────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_dir   = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
_fh  = logging.FileHandler(os.path.join(logs_dir, "project_manager.log"))
_fh.setFormatter(_fmt)
_fh.setLevel(logging.INFO)

_ch = RichHandler(level=logging.INFO, show_time=True, show_path=False, markup=True, rich_tracebacks=True)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.handlers = []
root_logger.addHandler(_fh)
root_logger.addHandler(_ch)

for _name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
    _l = logging.getLogger(_name)
    _l.handlers = [_ch]
    _l.propagate = False

logger = logging.getLogger("project-manager-service")


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print_banner()
    await run_startup_diagnostics()

    logger.info("Starting Project & Environment Management Service…")
    await cache_manager.connect()

    try:
        await init_projects_db()
        await init_admin_security()
        await seed_initial_data()
    except Exception as exc:
        logger.error(f"Startup initialisation error: {exc}", exc_info=True)

    logger.info("Module 1 ready → http://localhost:8001/app")
    yield

    # Shutdown
    logger.info("Shutting down Project Manager…")
    await cache_manager.disconnect()
    print_shutdown_banner()


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AetherOps AI — Module 1: Project & Environment Management",
    description="Create and manage projects and deployment environments.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include API router ────────────────────────────────────────────────────────
app.include_router(router)


# ── Deny Direct Browser Access to Microservice Port 8001 ─────────────────────
@app.api_route("/app", methods=["GET", "POST", "HEAD"])
@app.api_route("/login", methods=["GET", "POST", "HEAD"])
@app.api_route("/app/{rest:path}", methods=["GET", "POST", "HEAD"])
async def deny_browser_dashboard_access():
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "status": "DENIED",
            "code": 403,
            "detail": "Direct browser access to microservice port 8001 is denied. The AetherOps Dashboard is exclusively hosted on Port 8000.",
            "service": "project-manager",
            "port": 8001,
            "dashboard_url": "http://localhost:8000",
        },
    )


# ── Health / Root ─────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "project-manager", "port": 8001, "timestamp": time.time()}


@app.get("/")
async def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "status": "DENIED",
                "code": 403,
                "detail": "Direct browser access to microservice port 8001 is denied. The AetherOps Dashboard is exclusively hosted on Port 8000.",
                "service": "project-manager",
                "port": 8001,
                "dashboard_url": "http://localhost:8000",
            },
        )
    return {
        "service": "AetherOps AI — Module 1: Project & Environment Management",
        "version": "1.0.0",
        "port": 8001,
        "type": "BACKEND_MICROSERVICE",
        "endpoints": {
            "health":           "/health",
            "projects_api":     "/api/v1/projects",
            "environments_api": "/api/v1/projects/{id}/environments",
            "docs":             "/docs",
        },
    }


# ── Global exception handlers ─────────────────────────────────────────────────
@app.exception_handler(ValidationError)
async def _validation_err(request: Request, exc: ValidationError):
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "message": "Input validation failed."},
    )


@app.exception_handler(Exception)
async def _global_err(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error.", "error": str(exc)},
    )




