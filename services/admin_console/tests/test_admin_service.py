# services/admin_console/tests/test_admin_service.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_admin_console_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["port"] == 2470

def test_admin_console_dashboard_renders():
    response = client.get("/admin")
    assert response.status_code == 200
    assert "AetherOps Cloud - Admin Catalog Dashboard" in response.text
    assert "AetherOps" in response.text

def test_admin_console_login_renders():
    response = client.get("/admin/login")
    assert response.status_code == 200
    assert "AetherOps Cloud - Admin Login" in response.text
    assert "Admin Authentication" in response.text

def test_admin_console_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in [302, 307]
    assert response.headers["location"] == "/admin"

def test_admin_console_catalog_endpoint():
    response = client.get("/api/admin/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "ec2" in data
    assert "rds" in data
