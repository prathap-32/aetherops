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
import sys
import time
import logging
import secrets
from typing import Optional
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import httpx
import jwt
from rich.logging import RichHandler

# Centralized Application Secrets Manager
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SHARED_DIR = os.path.join(ROOT_DIR, "shared")
for p in (SHARED_DIR, ROOT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from aetherops_common.secrets import load_application_secrets, get_application_secrets_status
    load_application_secrets()
except Exception as _sec_err:
    pass
ENVIRONMENT = os.getenv("AETHER_ENV", os.getenv("ENVIRONMENT", "development")).lower()
INSECURE_DEV_JWT_SECRETS = {
    "aetherops-super-secure-production-cryptographic-jwt-token-signing-key-2026-cloudops-master",
    "secret",
    "changeme",
    "admin",
    "default",
    "test",
    "dev",
}


def validate_production_secrets(env: Optional[str] = None, secret: Optional[str] = None) -> None:
    target_env = (env or os.getenv("AETHER_ENV", os.getenv("ENVIRONMENT", "development"))).lower()
    target_secret = secret if secret is not None else os.getenv("JWT_SECRET_KEY")
    if target_env == "production":
        if not target_secret or target_secret in INSECURE_DEV_JWT_SECRETS:
            raise RuntimeError("FATAL: JWT_SECRET_KEY must be explicitly configured with a secure non-default secret in production.")


raw_jwt_key = os.getenv("JWT_SECRET_KEY")
validate_production_secrets()
if ENVIRONMENT == "production":
    JWT_SECRET_KEY = raw_jwt_key
else:
    JWT_SECRET_KEY = raw_jwt_key or "aetherops-super-secure-production-cryptographic-jwt-token-signing-key-2026-cloudops-master"
JWT_ALGORITHM = "HS256"

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
    # Port 7999: Dedicated Auth Service (API Only, Google/GitHub OAuth, Tenant & Account Authority)
    "auth": os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:7999"),
    "auth_google": os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:7999"),
    "auth_github": os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:7999"),

    # Port 8001: Project & Environment Management
    "projects": os.getenv("PM_SERVICE_URL", "http://127.0.0.1:8001"),
    "auth_pm": os.getenv("PM_SERVICE_URL", "http://127.0.0.1:8001"),

    # Port 8002: Source & Cloud Connection
    "connections": os.getenv("SC_SERVICE_URL", "http://127.0.0.1:8002"),
    "cloud": os.getenv("SC_SERVICE_URL", "http://127.0.0.1:8002"),
    "github": os.getenv("SC_SERVICE_URL", "http://127.0.0.1:8002"),
    "source": os.getenv("SC_SERVICE_URL", "http://127.0.0.1:8002"),

    # Port 8003: Source Code Analyzer
    "analyzer": os.getenv("REPO_ANALYZER_SERVICE_URL", "http://127.0.0.1:8003"),
    "repo": os.getenv("REPO_ANALYZER_SERVICE_URL", "http://127.0.0.1:8003"),

    # Port 8004: Requirement Analysis Engine
    "requirements": os.getenv("REQUIREMENTS_SERVICE_URL", "http://127.0.0.1:8004"),

    # Port 8005: Cloud Architecture Studio (Module 4)
    "architecture": os.getenv("ARCH_SERVICE_URL", "http://127.0.0.1:8005"),
    "studio": os.getenv("ARCH_SERVICE_URL", "http://127.0.0.1:8005"),

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

UNTRUSTED_IDENTITY_HEADERS = {
    "x-account-id",
    "x-accountid",
    "x-tenant-id",
    "x-tenantid",
    "x-user-id",
    "x-userid",
    "x-user-uuid",
    "x-user-role",
    "x-user-roles",
    "x-roles",
    "x-role",
    "x-auth-type",
    "x-user-email",
    "x-authenticated-user",
}

PUBLIC_API_PREFIXES = (
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/check-email",
    "/api/v1/auth/verify-email",
    "/api/v1/auth/resend-verification",
    "/api/v1/auth/google",
    "/api/v1/auth/github",
    "/auth/google",
    "/auth/github",
    "/api/v1/connections/github/login",
    "/api/v1/connections/github/callback",
    "/api/v1/connections/github/oauth",
    "/api/v1/meta",
    "/api/v1/health/secrets",
)


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

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8000,http://127.0.0.1:8000,http://localhost:7999,http://127.0.0.1:7999,http://localhost:5173,http://127.0.0.1:5173,http://100.125.96.14:8000,http://100.125.96.14:7999,http://warmachine-1:8000,http://warmachine-1:7999",
    ).split(",")
    if origin.strip()
]

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|100\.\d{1,3}\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|.*\.ts\.net|warmachine-1|.*\.local)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount compiled assets
if os.path.exists(FRONTEND_ASSETS):
    app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS), name="react_assets")

DIST_STATIC = os.path.join(FRONTEND_DIST, "static")
ROOT_STATIC = os.path.join(ROOT_DIR, "static")
static_dir = DIST_STATIC if os.path.exists(DIST_STATIC) else ROOT_STATIC
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static_assets")


@app.api_route("/favicon.ico", methods=["GET", "HEAD"])
@app.api_route("/favicon.png", methods=["GET", "HEAD"])
async def get_favicon():
    for base in (DIST_STATIC, ROOT_STATIC):
        fav_path = os.path.join(base, "logo", "logo.png")
        if os.path.exists(fav_path):
            return FileResponse(fav_path, media_type="image/png")
    return Response(status_code=404)


def _get_shell_response():
    """Serves the compiled SPA shell index.html with cache-busting headers."""
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    if os.path.exists(INDEX_HTML):
        return FileResponse(INDEX_HTML, media_type="text/html", headers=headers)
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
    clean_base = str(upstream_base_url).strip().replace(": //", "://")
    url = f"{clean_base.rstrip('/')}/{upstream_path.lstrip('/')}"
    query = request.url.query
    if query:
        url = f"{url}?{query}"

    req_headers = {}
    for k, v in request.headers.items():
        k_lower = k.lower()
        if k_lower not in EXCLUDE_HEADERS and k_lower not in UNTRUSTED_IDENTITY_HEADERS:
            req_headers[k_lower] = v

    client_ip = request.client.host if request.client else "127.0.0.1"
    req_headers["x-forwarded-for"] = client_ip
    req_headers["x-forwarded-proto"] = request.url.scheme
    req_headers["x-forwarded-host"] = request.headers.get("host", "localhost:8000")

    normalized_path = "/" + upstream_path.lstrip("/")
    is_public = (
        any(normalized_path == p or normalized_path.startswith(p + "/") for p in PUBLIC_API_PREFIXES)
        or normalized_path.endswith("/health")
        or normalized_path == "/health"
    )

    # Extract bearer token or X-Admin-Key
    auth_header = request.headers.get("authorization", "")
    x_admin_key = request.headers.get("x-admin-key", "")
    token = ""
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()

    decoded_payload = None
    if token:
        try:
            decoded_payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except Exception:
            decoded_payload = None
    elif x_admin_key:
        configured_admin_key = os.getenv("ADMIN_API_KEY", "aetherops-secret-admin-key")
        # In production, default development admin key is strictly prohibited
        if ENVIRONMENT == "production" and (not configured_admin_key or configured_admin_key == "aetherops-secret-admin-key"):
            decoded_payload = None
        elif secrets.compare_digest(x_admin_key.strip(), configured_admin_key):
            decoded_payload = {
                "sub": "admin",
                "account_id": "act_admin",
                "tenant_id": "ten_default",
                "uuid": "usr_00000000000000000000000000",
                "role": "admin",
                "roles": ["admin"],
                "auth_type": "api_key",
            }

    # Enforce mandatory authentication on all non-public API paths
    if not is_public and normalized_path.startswith("/api/"):
        if not decoded_payload:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Unauthorized: valid authentication token required."},
            )

    if decoded_payload:
        token_account_id = decoded_payload.get("account_id")
        token_tenant_id = decoded_payload.get("tenant_id")
        token_user_id = decoded_payload.get("uuid")
        token_user_role = decoded_payload.get("role")
        token_sub = decoded_payload.get("sub")

        # Validate that caller isn't spoofing another account or tenant
        req_account_id = request.headers.get("x-account-id")
        req_tenant_id = request.headers.get("x-tenant-id")

        if req_account_id and token_account_id and req_account_id != token_account_id:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Tenant isolation violation: Account ID mismatch with authenticated session."},
            )
        if req_tenant_id and token_tenant_id and req_tenant_id != token_tenant_id:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Tenant isolation violation: Tenant ID mismatch with authenticated session."},
            )

        # Propagate cryptographically verified identity headers downstream
        if token_account_id:
            req_headers["x-account-id"] = str(token_account_id)
        if token_tenant_id:
            req_headers["x-tenant-id"] = str(token_tenant_id)
        if token_user_id:
            req_headers["x-user-id"] = str(token_user_id)
        if token_user_role:
            req_headers["x-user-role"] = str(token_user_role)
        if token_sub:
            req_headers["x-authenticated-user"] = str(token_sub)

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
            if k.lower() not in EXCLUDE_HEADERS and k.lower() != "set-cookie":
                resp_headers[k] = v

        gateway_resp = Response(
            content=upstream_resp.content,
            status_code=upstream_resp.status_code,
            headers=resp_headers,
            media_type=upstream_resp.headers.get("content-type"),
        )
        for cookie_str in upstream_resp.headers.get_list("set-cookie"):
            gateway_resp.raw_headers.append((b"set-cookie", cookie_str.encode("latin-1")))
        return gateway_resp
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

@app.get("/api/v1/health/secrets", status_code=status.HTTP_200_OK)
async def secrets_health_check():
    """Reports AWS Secrets Manager connectivity and metadata without exposing credentials."""
    try:
        from aetherops_common.secrets import get_application_secrets_status
        return get_application_secrets_status()
    except Exception as e:
        return {"connected": False, "provider": "failed", "error": str(e), "credentials": "REDACTED"}


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
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
)
@app.api_route(
    "/api/admin/{subpath:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
)
async def proxy_admin_api(request: Request, subpath: str = ""):
    target_path = f"/api/admin/{subpath}".rstrip("/") if subpath else "/api/admin"
    return await _proxy_to_upstream(UPSTREAM_MAP["admin"], target_path, request)


# ═══════════════════════════════════════════════════════════════════════════════
# Unified Microservice API Reverse Proxy Routes
# ═══════════════════════════════════════════════════════════════════════════════

@app.api_route(
    "/api/v1/{module}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
)
@app.api_route(
    "/api/v1/{module}/{subpath:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
)
async def proxy_microservice_api(module: str, request: Request, subpath: str = ""):
    """Dispatches /api/v1/{module}/* requests to the correct independent microservice."""
    target_path = f"/api/v1/{module}/{subpath}".rstrip("/")

    if module == "auth":
        upstream = UPSTREAM_MAP["auth"]

    elif module == "connections" and (
        subpath.startswith("github/login")
        or subpath.startswith("github/callback")
        or subpath.startswith("github/oauth")
    ):
        upstream = UPSTREAM_MAP["auth"]

    elif module in ("projects", "tenants", "workspaces", "environments", "meta", "dashboard"):
        upstream = UPSTREAM_MAP["projects"]

    elif module in ("connections", "cloud", "github", "source"):
        upstream = UPSTREAM_MAP["connections"]

    elif module in ("analyzer", "repo-analyzer", "repo"):
        upstream = UPSTREAM_MAP["analyzer"]

    elif module in ("requirements", "analyze", "catalog", "recommendation"):
        upstream = UPSTREAM_MAP["requirements"]

    elif module in ("architecture", "generate-graph", "studio", "cloud-architecture-studio"):
        upstream = UPSTREAM_MAP["architecture"]

    elif module in ("iac", "terraform", "generate-iac"):
        upstream = UPSTREAM_MAP["iac"]

    elif module == "finops":
        upstream = UPSTREAM_MAP["finops"]

    elif module == "security":
        upstream = UPSTREAM_MAP["security"]

    elif module == "cicd":
        upstream = UPSTREAM_MAP["cicd"]

    elif module in ("monitoring", "observability"):
        upstream = UPSTREAM_MAP["monitoring"]

    elif module in ("deployments", "cloud-deployer", "deploy", "drift-detection"):
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
    "/architecture-studio",
    "/architecture-studio/{rest:path}",
    "/architecture-designer",
    "/architecture-designer/{rest:path}",
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
    "/account",
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
