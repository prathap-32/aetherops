# services/admin_console/tests/test_admin_service.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import MASTER_ADMIN_KEY

client = TestClient(app)

def test_admin_console_health():
    """Health check is public for cluster and orchestrator probes."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["port"] in (8000, 8012)

def test_admin_console_unauthenticated_dashboard_redirects():
    """Unauthenticated access to /admin must redirect to /admin/login."""
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/admin/login?redirect=/admin"

def test_admin_console_root_redirect_unauthenticated():
    """Unauthenticated access to / must redirect to /admin/login."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in [302, 307]
    assert response.headers["location"] == "/admin/login?redirect=/admin"

def test_admin_console_login_renders():
    """Admin login page is publicly reachable to allow sign-in."""
    response = client.get("/admin/login")
    assert response.status_code == 200
    assert "AetherOps Cloud - Admin Login" in response.text
    assert "Admin Authentication" in response.text

def test_admin_console_unauthenticated_api_calls_rejected():
    """Direct API calls without cookie session, token, or API key must be rejected with 401."""
    # 1. Catalog endpoint
    res1 = client.get("/api/admin/catalog")
    assert res1.status_code == 401
    assert "Unauthorized" in res1.json().get("detail", "")

    # 2. Modules fleet endpoint
    res2 = client.get("/api/admin/modules")
    assert res2.status_code == 401

    # 3. Cache clear endpoint
    res3 = client.post("/api/admin/clear-cache")
    assert res3.status_code == 401

def test_admin_console_login_flow_and_authenticated_access():
    """Login sets HttpOnly JWT cookie and unlocks dashboard and API endpoints."""
    # 1. Login with valid credentials
    login_res = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "AetherOps@2026!"}
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["status"] == "SUCCESS"
    assert "token" in login_data
    assert "aether_session" in login_res.cookies

    # 2. Access dashboard with authenticated session cookie
    dash_res = client.get("/admin")
    assert dash_res.status_code == 200
    assert "AetherOps Cloud - Admin Catalog Dashboard" in dash_res.text

    # 3. Access catalog API with authenticated session cookie
    cat_res = client.get("/api/admin/catalog")
    assert cat_res.status_code == 200
    data = cat_res.json()
    assert "ec2" in data
    assert "rds" in data

    # 4. Access modules API with authenticated session cookie
    mod_res = client.get("/api/admin/modules")
    assert mod_res.status_code == 200
    assert mod_res.json()["status"] == "success"

def test_admin_console_api_key_access():
    """Automation / DevOps can access protected APIs using X-Admin-Key header."""
    headers = {"X-Admin-Key": MASTER_ADMIN_KEY}
    response = client.get("/api/admin/catalog", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "ec2" in data
