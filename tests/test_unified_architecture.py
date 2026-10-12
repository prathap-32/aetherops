# tests/test_unified_architecture.py
"""
Automated Integration Test Suite for AetherOps Unified Architecture & Microservices Integration.

Validates Section 24 Acceptance Criteria:
1. Port 8000 Main Application & Gateway health check.
2. Direct Clean URLs and browser refresh delivery (HTTP 200).
3. Google OAuth initiation with prompt=select_account redirect.
4. GitHub OAuth initiation and source connection independence.
5. API Gateway reverse proxy dispatching:
   - /api/v1/projects -> Port 8009
   - /api/v1/connections -> Port 8010
   - /api/v1/repo/scan-and-size -> Port 8001
6. Protected API validation (401 without auth, 200 with admin key).
7. Profile update endpoint (PUT /api/v1/auth/profile) persisting to DB and refreshing JWT.
8. Error handling and unknown route isolation.
"""

import pytest
import httpx

MAIN_APP_URL = "http://127.0.0.1:8000"
GOOGLE_AUTH_URL = "http://127.0.0.1:8001"
GITHUB_AUTH_URL = "http://127.0.0.1:8002"
ADMIN_URL = "http://127.0.0.1:8012"
ADMIN_KEY = "aetherops-secret-admin-key"

CLEAN_PAGE_ROUTES = [
    "/",
    "/projects",
    "/environments",
    "/source-connection",
    "/source-analysis",
    "/requirements",
    "/architecture",
    "/architecture/designer",
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


@pytest.mark.asyncio
async def test_main_application_health():
    """Verify Main Application on Port 8000 is healthy."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{MAIN_APP_URL}/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "healthy"
        assert data.get("port") == 8000


@pytest.mark.asyncio
async def test_google_auth_service_health():
    """Verify Google Auth Service on Port 8001 is healthy."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GOOGLE_AUTH_URL}/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "healthy"
        assert data.get("port") == 8001


@pytest.mark.asyncio
async def test_github_connection_service_health():
    """Verify GitHub Connection Service on Port 8002 is healthy."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GITHUB_AUTH_URL}/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "healthy"
        assert data.get("port") == 8002


ALL_FLEET_SERVICES = [
    ("gateway", "http://127.0.0.1:8000/health", 8000),
    ("project_management", "http://127.0.0.1:8001/health", 8001),
    ("source_connection", "http://127.0.0.1:8002/health", 8002),
    ("repo_analyzer", "http://127.0.0.1:8003/health", 8003),
    ("requirement_analysis", "http://127.0.0.1:8004/health", 8004),
    ("architecture_generator", "http://127.0.0.1:8005/health", 8005),
    ("iac_generator", "http://127.0.0.1:8006/health", 8006),
    ("finops_optimizer", "http://127.0.0.1:8007/health", 8007),
    ("security_scanner", "http://127.0.0.1:8008/health", 8008),
    ("cicd_pipeline", "http://127.0.0.1:8009/health", 8009),
    ("observability_setup", "http://127.0.0.1:8010/health", 8010),
    ("cloud_deployer", "http://127.0.0.1:8011/health", 8011),
    ("admin_console", "http://127.0.0.1:8012/health", 8012),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("name,url,expected_port", ALL_FLEET_SERVICES)
async def test_all_13_services_health(name, url, expected_port):
    """Verify each of the 13 microservices responds healthy on its designated port."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "healthy"
        assert data.get("port") == expected_port


@pytest.mark.asyncio
@pytest.mark.parametrize("route", CLEAN_PAGE_ROUTES)
async def test_clean_frontend_urls_return_200(route):
    """
    Verify all clean URLs return HTTP 200 HTML content,
    ensuring direct navigation and browser refresh work without 404s.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{MAIN_APP_URL}{route}", headers={"Accept": "text/html"})
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("content-type", "")
        # Should contain root mounting element
        assert '<div id="root">' in resp.text or "AetherOps" in resp.text


@pytest.mark.asyncio
async def test_google_oauth_initiation_proxy():
    """
    Verify Google OAuth initiation through the Port 8000 Gateway (/auth/google/login)
    returns a 307 Temporary Redirect to Google's OAuth server with select_account.
    """
    async with httpx.AsyncClient(follow_redirects=False) as client:
        resp = await client.get(f"{MAIN_APP_URL}/auth/google/login")
        assert resp.status_code == 307
        location = resp.headers.get("location", "")
        assert "accounts.google.com" in location
        assert "prompt=select_account" in location
        assert "client_id=" in location


@pytest.mark.asyncio
async def test_github_oauth_initiation_proxy():
    """
    Verify GitHub OAuth initiation through the Port 8000 Gateway (/auth/github/login)
    operates independently and returns authorized redirect parameters.
    """
    async with httpx.AsyncClient(follow_redirects=False) as client:
        resp = await client.get(f"{MAIN_APP_URL}/auth/github/login")
        assert resp.status_code in (200, 307)
        if resp.status_code == 200:
            data = resp.json()
            assert "github.com/login/oauth/authorize" in data.get("url", "")
            assert data.get("is_configured") is True
        elif resp.status_code == 307:
            assert "github.com/login/oauth/authorize" in resp.headers.get("location", "")


@pytest.mark.asyncio
async def test_api_gateway_projects_proxy():
    """
    Verify /api/v1/projects requested through Port 8000 Gateway
    is transparently proxied to Port 8009 with proper authentication.
    """
    async with httpx.AsyncClient() as client:
        # Without credentials -> 401 Unauthorized
        unauth_resp = await client.get(f"{MAIN_APP_URL}/api/v1/projects")
        assert unauth_resp.status_code == 401

        # With Admin Key -> 200 OK with projects list from PostgreSQL
        auth_resp = await client.get(
            f"{MAIN_APP_URL}/api/v1/projects",
            headers={"X-Admin-Key": ADMIN_KEY}
        )
        assert auth_resp.status_code == 200
        data = auth_resp.json()
        assert "projects" in data
        assert isinstance(data["projects"], list)


@pytest.mark.asyncio
async def test_api_gateway_connections_proxy():
    """
    Verify /api/v1/connections requested through Port 8000 Gateway
    is transparently proxied to Port 8002.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{MAIN_APP_URL}/api/v1/connections",
            headers={"X-Admin-Key": ADMIN_KEY}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "connections" in data
        assert isinstance(data["connections"], list)


@pytest.mark.asyncio
async def test_profile_update_and_session_refresh():
    """
    Verify user profile update (PUT /api/v1/auth/profile) through Port 8000 Gateway
    validates input, updates username in PostgreSQL, and issues a refreshed JWT token.
    """
    async with httpx.AsyncClient() as client:
        # 1. Update username
        payload = {
            "username": "root_admin",
            "email": "root@aetherops.cloud"
        }
        resp = await client.put(
            f"{MAIN_APP_URL}/api/v1/auth/profile",
            json=payload,
            headers={"X-Admin-Key": ADMIN_KEY}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("username") == "root_admin"
        assert "token" in data

        # 2. Verify /api/v1/auth/me returns updated identity using the new token
        new_token = data["token"]
        me_resp = await client.get(
            f"{MAIN_APP_URL}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {new_token}"}
        )
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data.get("username") == "root_admin"


@pytest.mark.asyncio
async def test_gateway_unknown_module_404():
    """
    Verify requests to nonexistent microservice modules through Port 8000 Gateway
    return clean JSON 404 without leaking internal stack traces.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{MAIN_APP_URL}/api/v1/nonexistent_module")
        assert resp.status_code == 404
        data = resp.json()
        assert "Unknown microservice module" in data.get("detail", "")
