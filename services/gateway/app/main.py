# services/gateway/app/main.py
"""
AetherOps AI - Central API Gateway & Unified Dashboard Entrypoint (Port 8000)

Responsibilities:
1. Primary user entry point: Serves the compiled React SPA across all clean routes:
   - /, /projects, /projects/{id}, /environments, /source-connection,
     /source-analysis, /requirements, /architecture, /architecture/designer,
     /risk-analysis, /architecture/validation, /security, /terraform, /execution,
     /deployment, /cicd, /monitoring, /optimization, /audit, /documentation,
     /login, /settings, /admin.
2. Reverse Proxy dispatching API calls to microservices (Ports 8001-8012):
   - /auth/google/*          -> Port 8001 (Project & Session Manager)
   - /auth/github/*          -> Port 8002 (Source & Cloud Connection)
   - /api/v1/auth/*          -> Port 8001 (or GitHub auth to 8002)
   - /api/v1/projects/*      -> Port 8001
   - /api/v1/connections/*   -> Port 8002
   - /api/v1/cloud/*         -> Port 8002
   - /api/v1/github/*        -> Port 8002
   - /api/v1/source/*        -> Port 8002
   - /api/v1/analyzer/*      -> Port 8003 (Source Code Analyzer)
   - /api/v1/repo/*          -> Port 8004 (Requirement Analysis Engine)
   - /api/v1/requirements/*  -> Port 8004
   - /api/v1/analyze/*       -> Port 8004
   - /api/v1/catalog/*       -> Port 8004
   - /api/v1/recommendation  -> Port 8004
   - /api/v1/architecture/*  -> Port 8005 (Architecture Graph Generator)
   - /api/v1/iac/*           -> Port 8006 (IaC / Terraform Generator)
   - /api/v1/terraform/*     -> Port 8006
   - /api/v1/finops/*        -> Port 8007 (FinOps Cost Optimizer)
   - /api/v1/security/*      -> Port 8008 (Security & Compliance Engine)
   - /api/v1/cicd/*          -> Port 8009 (CI/CD Pipeline Generator)
   - /api/v1/monitoring/*    -> Port 8010 (Observability & Monitoring)
   - /api/v1/observability/* -> Port 8010
   - /api/v1/deployments/*   -> Port 8011 (Cloud Deployment & Drift Engine)
   - /api/v1/admin/*         -> Port 8012 (Admin Console)
   - /api/admin/*            -> Port 8012 (Admin Console)
3. Preserves HTTP methods, headers, cookies, query parameters, bodies, and redirects.
4. Provides standard /health endpoint returning port 8000.
"""

import os
import time
import logging
from typing import Optional
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import httpx
from rich.logging import RichHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
FRONTEND_DIST = os.path.join(ROOT_DIR, "frontend", "dist")
FRONTEND_ASSETS = os.path.join(FRONTEND_DIST, "assets")
INDEX_HTML = os.path.join(FRONTEND_DIST, "index.html")

# Setup logging
logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)
log_file_path = os.path.join(logs_dir, "gateway.log")

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
    rich_tracebacks=True,
)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.handlers = [file_handler, console_handler]

for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
    l = logging.getLogger(logger_name)
    l.handlers = [console_handler]
    l.propagate = False

logger = logging.getLogger("aether-gateway")

# Microservices Upstream Routing Map
UPSTREAM_MAP = {
    # Port 8001: Project & Environment Management
    "projects": os.getenv("PM_SERVICE_URL", "http://127.0.0.1:8001"),
    "auth_pm": os.getenv("PM_SERVICE_URL", "http://127.0.0.1:8001"),
    "auth_google": os.getenv("GOOGLE_AUTH_SERVICE_URL", "http://127.0.0.1:8001"),

    # Port 8002: Source & Cloud Connection
    "connections": os.getenv("SC_SERVICE_URL", "http://127.0.0.1:8002"),
    "cloud": os.getenv("SC_SERVICE_URL", "http://127.0.0.1:8002"),
    "github": os.getenv("SC_SERVICE_URL", "http://127.0.0.1:8002"),
    "source": os.getenv("SC_SERVICE_URL", "http://127.0.0.1:8002"),
    "auth_github": os.getenv("GITHUB_AUTH_SERVICE_URL", "http://127.0.0.1:8002"),

    # Port 8003: Source Code Analyzer
    "analyzer": os.getenv("REPO_ANALYZER_SERVICE_URL", "http://127.0.0.1:8003"),

    # Port 8004: Requirement Analysis Engine
    "repo": os.getenv("REQ_SERVICE_URL", "http://127.0.0.1:8004"),
    "requirements": os.getenv("REQ_SERVICE_URL", "http://127.0.0.1:8004"),

    # Port 8005: Architecture Graph Generator
    "architecture": os.getenv("ARCH_SERVICE_URL", "http://127.0.0.1:8005"),

    # Port 8006: IaC / Terraform Generator
    "iac": os.getenv("IAC_SERVICE_URL", "http://127.0.0.1:8006"),
    "terraform": os.getenv("IAC_SERVICE_URL", "http://127.0.0.1:8006"),

    # Port 8007: FinOps Cost Optimizer
    "finops": os.getenv("FINOPS_SERVICE_URL", "http://127.0.0.1:8007"),

    # Port 8008: Security & Compliance Engine
    "security": os.getenv("SEC_SERVICE_URL", "http://127.0.0.1:8008"),

    # Port 8009: CI/CD Pipeline Generator
    "cicd": os.getenv("CICD_SERVICE_URL", "http://127.0.0.1:8009"),

    # Port 8010: Observability & Monitoring
    "monitoring": os.getenv("OBS_SERVICE_URL", "http://127.0.0.1:8010"),
    "observability": os.getenv("OBS_SERVICE_URL", "http://127.0.0.1:8010"),

    # Port 8011: Cloud Deployer & Drift Engine
    "deployments": os.getenv("DEPLOYER_SERVICE_URL", "http://127.0.0.1:8011"),
    "cloud-deployer": os.getenv("DEPLOYER_SERVICE_URL", "http://127.0.0.1:8011"),

    # Port 8012: Admin Console & Control Plane
    "admin": os.getenv("ADMIN_SERVICE_URL", "http://127.0.0.1:8012"),
}

EXCLUDE_HEADERS = {
    "host",
    "content-length",
    "transfer-encoding",
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "upgrade",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AetherOps Central API Gateway & Unified Dashboard on port 8000...")
    yield
    logger.info("Shutting down AetherOps Central API Gateway...")


app = FastAPI(
    title="AetherOps - Central API Gateway & Unified Dashboard",
    description="Main user entry point and API reverse proxy for AetherOps cloud platform (Port 8000)",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount compiled assets
if os.path.exists(FRONTEND_ASSETS):
    app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS), name="react_assets")


def _get_shell_response():
    """Serves the compiled SPA shell index.html."""
    if os.path.exists(INDEX_HTML):
        return FileResponse(INDEX_HTML, media_type="text/html")
    # Fallback minimal HTML
    return HTMLResponse(
        content="""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>AetherOps</title></head>
<body><div id="root"><h1>AetherOps Cloud Platform</h1><p>Building frontend assets...</p></div></body>
</html>""",
        status_code=200,
    )


async def _proxy_to_upstream(
    upstream_base_url: str,
    upstream_path: str,
    request: Request,
    timeout_sec: float = 30.0,
) -> Response:
    """Transparently proxies an incoming HTTP request to upstream microservice."""
    url = f"{upstream_base_url.rstrip('/')}/{upstream_path.lstrip('/')}"
    query = request.url.query
    if query:
        url = f"{url}?{query}"

    req_headers = {}
    for k, v in request.headers.items():
        if k.lower() not in EXCLUDE_HEADERS:
            req_headers[k] = v

    client_ip = request.client.host if request.client else "127.0.0.1"
    req_headers["x-forwarded-for"] = client_ip
    req_headers["x-forwarded-proto"] = request.url.scheme
    req_headers["x-forwarded-host"] = request.headers.get("host", "localhost:8000")

    body = None
    if request.method not in ("GET", "HEAD"):
        body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=timeout_sec, follow_redirects=False) as client:
            upstream_resp = await client.request(
                method=request.method,
                url=url,
                headers=req_headers,
                content=body,
            )

        resp_headers = {}
        for k, v in upstream_resp.headers.items():
            if k.lower() not in EXCLUDE_HEADERS:
                resp_headers[k] = v

        return Response(
            content=upstream_resp.content,
            status_code=upstream_resp.status_code,
            headers=resp_headers,
            media_type=upstream_resp.headers.get("content-type"),
        )
    except httpx.ConnectError:
        logger.warning(f"Gateway Upstream Offline: Unable to connect to {url}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "OFFLINE",
                "service": upstream_base_url,
                "detail": f"Upstream microservice at {upstream_base_url} is currently offline or starting up.",
            },
        )
    except httpx.TimeoutException:
        logger.warning(f"Gateway Upstream Timeout: {url}")
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "status": "TIMEOUT",
                "service": upstream_base_url,
                "detail": f"Upstream microservice at {upstream_base_url} timed out after {timeout_sec}s.",
            },
        )
    except Exception as exc:
        logger.error(f"Gateway Proxy Error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "status": "BAD_GATEWAY",
                "service": upstream_base_url,
                "detail": f"Gateway failed to proxy request: {str(exc)}",
            },
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Health & Telemetry
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "gateway",
        "port": 8000,
        "timestamp": time.time(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# OAuth Initiation & Callback Forwarding Routes
# ═══════════════════════════════════════════════════════════════════════════════

@app.api_route("/auth/google/{path:path}", methods=["GET", "POST", "OPTIONS"])
async def proxy_google_auth(path: str, request: Request):
    """Routes Google OAuth initiation and callback directly to Port 8001."""
    upstream = UPSTREAM_MAP["auth_google"]
    return await _proxy_to_upstream(upstream, f"/auth/google/{path}", request)


@app.api_route("/auth/github/{path:path}", methods=["GET", "POST", "OPTIONS"])
async def proxy_github_auth(path: str, request: Request):
    """Routes GitHub OAuth initiation and callback directly to Port 8002."""
    upstream = UPSTREAM_MAP["auth_github"]
    return await _proxy_to_upstream(upstream, f"/auth/github/{path}", request)


# ═══════════════════════════════════════════════════════════════════════════════
# Admin Console API Reverse Proxy Routes (Port 8012)
# ═══════════════════════════════════════════════════════════════════════════════

@app.api_route(
    "/api/admin",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
)
@app.api_route(
    "/api/admin/{subpath:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
)
async def proxy_admin_api(request: Request, subpath: str = ""):
    target_path = f"/api/admin/{subpath}".rstrip("/") if subpath else "/api/admin"
    return await _proxy_to_upstream(UPSTREAM_MAP["admin"], target_path, request)


# ═══════════════════════════════════════════════════════════════════════════════
# Unified Microservice API Reverse Proxy Routes
# ═══════════════════════════════════════════════════════════════════════════════

@app.api_route(
    "/api/v1/{module}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
)
@app.api_route(
    "/api/v1/{module}/{subpath:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
)
async def proxy_microservice_api(module: str, request: Request, subpath: str = ""):
    """Dispatches /api/v1/{module}/* requests to the correct independent microservice."""
    target_path = f"/api/v1/{module}/{subpath}".rstrip("/")

    if module == "auth":
        if subpath.startswith("github"):
            upstream = UPSTREAM_MAP["auth_github"]
        elif subpath.startswith("google"):
            upstream = UPSTREAM_MAP["auth_google"]
        else:
            upstream = UPSTREAM_MAP["auth_pm"]

    elif module in ("projects", "tenants", "workspaces"):
        upstream = UPSTREAM_MAP["projects"]

    elif module in ("connections", "cloud", "github", "source"):
        upstream = UPSTREAM_MAP["connections"]

    elif module in ("analyzer", "repo-analyzer"):
        upstream = UPSTREAM_MAP["analyzer"]

    elif module in ("repo", "requirements", "analyze", "catalog", "recommendation"):
        upstream = UPSTREAM_MAP["repo"]

    elif module in ("architecture", "generate-graph"):
        upstream = UPSTREAM_MAP["architecture"]

    elif module in ("iac", "terraform"):
        upstream = UPSTREAM_MAP["iac"]

    elif module == "finops":
        upstream = UPSTREAM_MAP["finops"]

    elif module == "security":
        upstream = UPSTREAM_MAP["security"]

    elif module == "cicd":
        upstream = UPSTREAM_MAP["cicd"]

    elif module in ("monitoring", "observability"):
        upstream = UPSTREAM_MAP["monitoring"]

    elif module in ("deployments", "cloud-deployer"):
        upstream = UPSTREAM_MAP["deployments"]

    elif module == "admin":
        upstream = UPSTREAM_MAP["admin"]

    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Unknown microservice module: '{module}'"},
        )

    return await _proxy_to_upstream(upstream, target_path, request)


# ═══════════════════════════════════════════════════════════════════════════════
# SPA Clean URL Routes & Primary Entrypoint
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def serve_root_page(request: Request):
    """Primary user entry point: always serves the React SPA unified dashboard."""
    return _get_shell_response()


@app.get("/app", response_class=HTMLResponse)
@app.get("/app/{rest:path}", response_class=HTMLResponse)
async def serve_app_redirect(request: Request, rest: str = ""):
    """Redirects legacy /app routes directly to clean URLs."""
    target = f"/{rest}" if rest else "/"
    return RedirectResponse(url=target, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


PAGE_ROUTES = [
    "/projects",
    "/projects/{rest:path}",
    "/environments",
    "/source-connection",
    "/source-analysis",
    "/requirements",
    "/architecture",
    "/architecture/{rest:path}",
    "/risk-analysis",
    "/architecture/validation",
    "/security",
    "/terraform",
    "/execution",
    "/deployment",
    "/cicd",
    "/monitoring",
    "/optimization",
    "/audit",
    "/documentation",
    "/login",
    "/settings",
    "/admin",
]

for route_path in PAGE_ROUTES:
    app.add_api_route(
        route_path,
        endpoint=_get_shell_response,
        methods=["GET"],
        response_class=HTMLResponse,
    )
