# services/source_and_cloud_connection/app/main.py
import os, logging, time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from rich.logging import RichHandler

from app.database import init_source_db
from app.auth import init_admin_security, SESSION_COOKIE_NAME, decode_access_token, MASTER_ADMIN_KEY
from app.cache import cache_manager
from app.seed import seed_initial_data
from app.router import router
from app.dashboard_page import get_dashboard_html
from app.connection_page import get_connection_detail_html
from app.terminal_ui import print_banner, run_startup_diagnostics, print_shutdown_banner

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
_fh = logging.FileHandler(os.path.join(BASE_DIR, "logs", "source_connection.log"))
_fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
_ch = RichHandler(level=logging.INFO, show_time=True, show_path=False, markup=True, rich_tracebacks=True)
root = logging.getLogger()
root.setLevel(logging.INFO)
root.handlers = []
root.addHandler(_fh)
root.addHandler(_ch)
for _n in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
    _l = logging.getLogger(_n); _l.handlers = [_ch]; _l.propagate = False

logger = logging.getLogger("source-connection-service")


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print_banner()
    await run_startup_diagnostics()
    logger.info("Starting Source & Cloud Connection Service…")
    await cache_manager.connect()
    try:
        await init_source_db()
        await init_admin_security()
        await seed_initial_data()
    except Exception as exc:
        logger.error(f"Startup error: {exc}", exc_info=True)
    logger.info("Module 2 ready → http://localhost:8002/app/source")
    yield
    logger.info("Shutting down Source Connection Service…")
    await cache_manager.disconnect()
    print_shutdown_banner()


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AetherOps AI — Module 2: Source & Cloud Connection",
    description="Connect GitHub repositories to project environments and capture source snapshots.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

app.include_router(router)


# ── Deny Direct Browser Access to Microservice Port 8002 ─────────────────────
@app.api_route("/app", methods=["GET", "POST", "HEAD"])
@app.api_route("/app/source", methods=["GET", "POST", "HEAD"])
@app.api_route("/app/source/{rest:path}", methods=["GET", "POST", "HEAD"])
@app.api_route("/login", methods=["GET", "POST", "HEAD"])
async def deny_browser_dashboard_access():
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "status": "DENIED",
            "code": 403,
            "detail": "Direct browser access to microservice port 8002 is denied. The AetherOps Dashboard is exclusively hosted on Port 8000.",
            "service": "source-cloud-connection",
            "port": 8002,
            "dashboard_url": "http://localhost:8000",
        },
    )


# ── Health / Root ─────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "source-and-cloud-connection", "port": 8002, "timestamp": time.time()}


@app.get("/")
async def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "status": "DENIED",
                "code": 403,
                "detail": "Direct browser access to microservice port 8002 is denied. The AetherOps Dashboard is exclusively hosted on Port 8000.",
                "service": "source-cloud-connection",
                "port": 8002,
                "dashboard_url": "http://localhost:8000",
            },
        )
    return {
        "service": "AetherOps AI — Module 2: Source & Cloud Connection",
        "version": "1.0.0",
        "port": 8002,
        "type": "BACKEND_MICROSERVICE",
        "endpoints": {
            "health": "/health",
            "connections_api": "/api/v1/connections",
            "finalize_api": "/api/v1/connections/finalize",
            "validate": "/api/v1/connections/{id}/validate",
            "snapshot": "/api/v1/connections/{id}/snapshot",
            "github_repos": "/api/v1/github/repos",
            "aws_validate": "/api/v1/cloud/aws/validate",
            "cloud_connections": "/api/v1/cloud/connections",
            "docs": "/docs",
        },
    }


# ── Exception handlers ────────────────────────────────────────────────────────
@app.exception_handler(ValidationError)
async def _val_err(request: Request, exc: ValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def _global_err(request: Request, exc: Exception):
    logger.error(f"Unhandled: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"message": "Internal server error.", "error": str(exc)})

