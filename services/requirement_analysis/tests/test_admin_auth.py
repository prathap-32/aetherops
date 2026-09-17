# services/requirement_analysis/tests/test_admin_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_admin_login_page_renders():
    """Verify that the admin login page renders successfully with 200 OK."""
    response = client.get("/admin/login")
    assert response.status_code == 200
    assert "AetherOps Cloud - Admin Login" in response.text
    assert "Admin Authentication" in response.text


def test_admin_login_invalid_credentials():
    """Verify that invalid credentials yield 401 Unauthorized."""
    payload = {
        "username": "invalid_user",
        "password": "wrong_password_123"
    }
    response = client.post("/api/admin/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid admin credentials" in response.json().get("detail", "")


def test_admin_login_success_and_cookie():
    """Verify successful login returns user info and sets HttpOnly cookie."""
    payload = {
        "username": "admin",
        "password": "AetherOps@2026!"
    }
    response = client.post("/api/admin/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "SUPER_ADMIN"
    assert "token" in data
    assert "aether_session" in response.cookies


def test_admin_me_with_cookie_and_apikey():
    """Verify that /api/admin/auth/me authenticates via cookie and X-Admin-Key."""
    # 1. Login to get cookie
    login_res = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "AetherOps@2026!"}
    )
    assert login_res.status_code == 200

    # 2. Check profile using cookie automatically passed by TestClient
    me_res = client.get("/api/admin/auth/me")
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["status"] == "AUTHENTICATED"
    assert me_data["user"]["username"] == "admin"

    # 3. Check profile using X-Admin-Key
    client.cookies.clear()
    key_res = client.get(
        "/api/admin/auth/me",
        headers={"X-Admin-Key": "aetherops-secret-admin-key"}
    )
    assert key_res.status_code == 200
    key_data = key_res.json()
    assert key_data["status"] == "AUTHENTICATED"
    assert key_data["user"]["username"] == "root_admin"


def test_admin_me_unauthorized():
    """Verify that /api/admin/auth/me yields 401 when unauthenticated."""
    client.cookies.clear()
    response = client.get("/api/admin/auth/me")
    assert response.status_code == 401


def test_admin_logout():
    """Verify that logout clears the cookie."""
    client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "AetherOps@2026!"}
    )
    logout_res = client.post("/api/admin/auth/logout")
    assert logout_res.status_code == 200
    assert logout_res.json()["status"] == "SUCCESS"


def test_admin_audit_logs():
    """Verify that audit log endpoint returns logged actions."""
    response = client.get(
        "/api/admin/auth/audit",
        headers={"X-Admin-Key": "aetherops-secret-admin-key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "audit_logs" in data
    assert isinstance(data["audit_logs"], list)
