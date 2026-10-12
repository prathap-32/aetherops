# services/admin_console/app/gateway_router.py
"""
AetherOps AI - Central API Gateway & Frontend Shell Router (Port 8000)

Responsibilities:
1. Serves the unified single-domain frontend shell across all clean URLs:
   - /, /projects, /projects/{id}, /environments, /source-connection,
     /source-analysis, /architecture, /architecture/designer, /risk-analysis,
     /architecture/validation, /terraform, /execution, /deployment, /cicd,
     /monitoring, /optimization, /audit, /documentation, /login, /settings.
2. Acts as an asynchronous Reverse Proxy Gateway dispatching API calls to
   their respective independent microservices:
   - /auth/google/*          -> Port 8009 (Project & Session Manager)
   - /auth/github/*          -> Port 8010 (Source & Cloud Connection)
   - /api/v1/auth/*          -> Port 8009 (and GitHub auth to 8010)
   - /api/v1/projects/*      -> Port 8009
   - /api/v1/connections/*   -> Port 8010
   - /api/v1/cloud/*         -> Port 8010
   - /api/v1/github/*        -> Port 8010
   - /api/v1/source/*        -> Port 8010
   - /api/v1/repo/*          -> Port 8001 (Requirement Analysis / Scanner)
   - /api/v1/requirements/*  -> Port 8001
   - /api/v1/architecture/*  -> Port 8002 (Architecture Graph Generator)
   - /api/v1/iac/*           -> Port 8003 (IaC Synthesizer)
   - /api/v1/terraform/*     -> Port 8003
   - /api/v1/finops/*        -> Port 8004 (FinOps Optimizer)
   - /api/v1/security/*      -> Port 8005 (Security & Compliance Scanner)
   - /api/v1/cicd/*          -> Port 8006 (CI/CD Pipeline Engine)
   - /api/v1/monitoring/*    -> Port 8007 (Observability Setup & APM)
   - /api/v1/observability/* -> Port 8007
   - /api/v1/deployments/*   -> Port 8008 (Cloud Deployer & Drift Engine)
3. Preserves HTTP methods, headers, cookies, query parameters, and streaming.
4. Preserves 302/307 redirects for OAuth handshakes without following them internally.
5. Provides honest error handling and service offline states when upstream services
   are unreachable, avoiding stack trace leakage.
"""

import os
import logging
from typing import Optional
from fastapi import APIRouter, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse, RedirectResponse
import httpx

logger = logging.getLogger("aether-gateway")

gateway_router = APIRouter()

# Resolve Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
FRONTEND_DIST = os.path.join(ROOT_DIR, "frontend", "dist")
INDEX_HTML = os.path.join(FRONTEND_DIST, "index.html")

# Upstream Microservice Endpoints (configurable via environment variables)
UPSTREAM_MAP = {
    # Port 8009: Project & Session Management + Google OAuth
    "projects": os.getenv("PM_SERVICE_URL", "http://127.0.0.1:8009"),
    "auth_pm": os.getenv("PM_SERVICE_URL", "http://127.0.0.1:8009"),
    "auth_google": os.getenv("GOOGLE_AUTH_SERVICE_URL", "http://127.0.0.1:8009"),

    # Port 8010: Source & Cloud Connection + GitHub OAuth
    "connections": os.getenv("SC_SERVICE_URL", "http://127.0.0.1:8010"),
    "cloud": os.getenv("SC_SERVICE_URL", "http://127.0.0.1:8010"),
    "github": os.getenv("SC_SERVICE_URL", "http://127.0.0.1:8010"),
    "source": os.getenv("SC_SERVICE_URL", "http://127.0.0.1:8010"),
    "auth_github": os.getenv("GITHUB_AUTH_SERVICE_URL", "http://127.0.0.1:8010"),

    # Port 8001: Requirement Analysis & Repo Sizing
    "repo": os.getenv("REQ_SERVICE_URL", "http://127.0.0.1:8001"),
    "requirements": os.getenv("REQ_SERVICE_URL", "http://127.0.0.1:8001"),

    # Port 8011: Standalone Repo Analyzer Service (Module 3)
    "analyzer": os.getenv("REPO_ANALYZER_SERVICE_URL", "http://127.0.0.1:8011"),


    # Port 8002: Architecture Graph Generator
    "architecture": os.getenv("ARCH_SERVICE_URL", "http://127.0.0.1:8002"),

    # Port 8003: IaC Code Synthesizer
    "iac": os.getenv("IAC_SERVICE_URL", "http://127.0.0.1:8003"),
    "terraform": os.getenv("IAC_SERVICE_URL", "http://127.0.0.1:8003"),

    # Port 8004: FinOps Cost Optimizer
    "finops": os.getenv("FINOPS_SERVICE_URL", "http://127.0.0.1:8004"),

    # Port 8005: Security & CIS Scanner
    "security": os.getenv("SEC_SERVICE_URL", "http://127.0.0.1:8005"),

    # Port 8006: CI/CD Pipeline Engine
    "cicd": os.getenv("CICD_SERVICE_URL", "http://127.0.0.1:8006"),

    # Port 8007: Observability & APM Engine
    "monitoring": os.getenv("OBS_SERVICE_URL", "http://127.0.0.1:8007"),
    "observability": os.getenv("OBS_SERVICE_URL", "http://127.0.0.1:8007"),

    # Port 8008: Cloud Deployer & Drift Engine
    "deployments": os.getenv("DEPLOYER_SERVICE_URL", "http://127.0.0.1:8008"),
    "cloud-deployer": os.getenv("DEPLOYER_SERVICE_URL", "http://127.0.0.1:8008"),
}

# Hop-by-hop headers that should not be forwarded directly
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


def _get_shell_response():
    """Serves the compiled SPA shell or falls back to server-rendered dashboard."""
    if os.path.exists(INDEX_HTML):
        return FileResponse(INDEX_HTML, media_type="text/html")
    from app.dashboard_page import get_dashboard_page_html
    return HTMLResponse(content=get_dashboard_page_html(), status_code=200)


async def _proxy_to_upstream(
    upstream_base_url: str,
    upstream_path: str,
    request: Request,
    timeout_sec: float = 30.0,
) -> Response:
    """
    Transparently forwards an incoming HTTP request to the designated upstream
    microservice, streaming the response body and preserving all relevant headers.
    """
    # 1. Construct target URL preserving query string
    url = f"{upstream_base_url.rstrip('/')}/{upstream_path.lstrip('/')}"
    query = request.url.query
    if query:
        url = f"{url}?{query}"

    # 2. Extract and filter request headers
    req_headers = {}
    for k, v in request.headers.items():
        if k.lower() not in EXCLUDE_HEADERS:
            req_headers[k] = v

    # Add standard proxy tracking headers
    client_ip = request.client.host if request.client else "127.0.0.1"
    req_headers["x-forwarded-for"] = client_ip
    req_headers["x-forwarded-proto"] = request.url.scheme
    req_headers["x-forwarded-host"] = request.headers.get("host", "localhost:8000")

    # Read body bytes for non-GET/HEAD methods
    body = None
    if request.method not in ("GET", "HEAD"):
        body = await request.body()

    try:
        # We explicitly set follow_redirects=False to allow OAuth redirects (302/307)
        # to propagate directly to the client browser.
        client = httpx.AsyncClient(timeout=timeout_sec, follow_redirects=False)
        upstream_resp = await client.request(
            method=request.method,
            url=url,
            headers=req_headers,
            content=body,
        )

        # 3. Filter response headers
        resp_headers = {}
        for k, v in upstream_resp.headers.items():
            if k.lower() not in EXCLUDE_HEADERS:
                resp_headers[k] = v

        # Return response to client
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


# ============================================================================
# 1. OAuth Forwarding Routes
# ============================================================================

@gateway_router.api_route("/auth/google/{path:path}", methods=["GET", "POST", "OPTIONS"])
async def proxy_google_auth(path: str, request: Request):
    """Routes Google OAuth initiation and callback directly to Port 8009."""
    upstream = UPSTREAM_MAP["auth_google"]
    return await _proxy_to_upstream(upstream, f"/auth/google/{path}", request)


@gateway_router.api_route("/auth/github/{path:path}", methods=["GET", "POST", "OPTIONS"])
async def proxy_github_auth(path: str, request: Request):
    """Routes GitHub OAuth initiation and callback directly to Port 8010."""
    upstream = UPSTREAM_MAP["auth_github"]
    return await _proxy_to_upstream(upstream, f"/auth/github/{path}", request)


# ============================================================================
# 2. Unified Microservice API Reverse Proxy Routes
# ============================================================================

@gateway_router.api_route(
    "/api/v1/{module}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
)
@gateway_router.api_route(
    "/api/v1/{module}/{subpath:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
)
async def proxy_microservice_api(module: str, request: Request, subpath: str = ""):
    """
    Dispatches /api/v1/{module}/* requests to the correct independent microservice.
    """
    target_path = f"/api/v1/{module}/{subpath}".rstrip("/")

    # Resolve upstream service based on module prefix
    if module == "auth":
        if subpath.startswith("github"):
            upstream = UPSTREAM_MAP["auth_github"]
        elif subpath.startswith("google"):
            upstream = UPSTREAM_MAP["auth_google"]
        else:
            upstream = UPSTREAM_MAP["auth_pm"]

    elif module == "projects":
        upstream = UPSTREAM_MAP["projects"]

    elif module in ("connections", "cloud", "github", "source"):
        upstream = UPSTREAM_MAP["connections"]

    elif module in ("repo", "requirements"):
        upstream = UPSTREAM_MAP["repo"]

    elif module in ("analyzer", "repo-analyzer"):
        upstream = UPSTREAM_MAP["analyzer"]


    elif module == "architecture":
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

    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Unknown microservice module: '{module}'"},
        )

    return await _proxy_to_upstream(upstream, target_path, request)


@gateway_router.get("/", response_class=HTMLResponse)
async def serve_root_page(request: Request):
    """
    Serves the SPA frontend shell when Accept: text/html is present (browsers).
    If direct API probe or test client without text/html, redirects unauthenticated access to /admin/login.
    """
    accept = request.headers.get("accept", "")
    if "text/html" in accept and os.path.exists(INDEX_HTML):
        return FileResponse(INDEX_HTML, media_type="text/html")
    from app.auth import SESSION_COOKIE_NAME, decode_access_token
    cookie_token = request.cookies.get(SESSION_COOKIE_NAME)
    if cookie_token and decode_access_token(cookie_token):
        return RedirectResponse(url="/admin")
    return RedirectResponse(url="/admin/login?redirect=/admin", status_code=status.HTTP_307_TEMPORARY_REDIRECT)


PAGE_ROUTES = [
    "/projects",
    "/projects/{rest:path}",
    "/environments",
    "/source-connection",
    "/source-analysis",
    "/architecture",
    "/architecture/{rest:path}",
    "/risk-analysis",
    "/architecture/validation",
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
]

for route_path in PAGE_ROUTES:
    gateway_router.add_api_route(
        route_path,
        endpoint=_get_shell_response,
        methods=["GET"],
        response_class=HTMLResponse,
    )
