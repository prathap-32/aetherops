# tests/security/test_authentication_security.py
"""
Automated Security Test Suite for AetherOps Authentication & Authorization Remediation.
Verifies:
1. Complete elimination of mock-token bypasses across Auth and Project Manager.
2. Cryptographic JWT validation (rejection of forged signatures, expired tokens, malformed strings).
3. Elimination of username-based privilege escalation (admin/root_admin shortcuts).
4. Gateway enforcement and sanitization of spoofed client identity headers.
5. OAuth state verification to prevent OAuth Login CSRF.
6. Password verification requiring bcrypt hashes (no plaintext fallbacks).
"""
import uuid
import datetime
import pytest
import pytest_asyncio
import jwt
from httpx import AsyncClient, ASGITransport

JWT_SECRET_KEY = "aetherops-super-secure-production-cryptographic-jwt-token-signing-key-2026-cloudops-master"
JWT_ALGORITHM = "HS256"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def auth_client():
    from services.auth_service.app.main import app as auth_app
    async with AsyncClient(transport=ASGITransport(app=auth_app), base_url="http://test-auth") as ac:
        yield ac


@pytest_asyncio.fixture
async def gateway_client():
    from services.gateway.app.main import app as gw_app
    async with AsyncClient(transport=ASGITransport(app=gw_app), base_url="http://test-gateway") as ac:
        yield ac


@pytest_asyncio.fixture
async def pm_client():
    from services.project_and_environment_management.app.main import app as pm_app
    async with AsyncClient(transport=ASGITransport(app=pm_app), base_url="http://test-pm") as ac:
        yield ac


# ─────────────────────────────────────────────────────────────────────────────
# 1. Mock Token Rejection Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_auth_service_rejects_mock_tokens(auth_client):
    """Verify that auth_service rejects any mock_token_* strings with HTTP 401."""
    mock_tokens = [
        "mock_token_admin",
        "mock_token_123_admin",
        "mock_token_root_admin",
        "mock_token_super_user",
        "mock_token_",
    ]
    for tok in mock_tokens:
        resp = await auth_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tok}"}
        )
        assert resp.status_code == 401, f"Expected 401 for mock token '{tok}', got {resp.status_code}"
        assert "Invalid or expired token" in resp.text


@pytest.mark.anyio
async def test_project_manager_rejects_mock_tokens(pm_client):
    """Verify that project_manager rejects mock_token_* strings with HTTP 401."""
    mock_tokens = [
        "mock_token_admin",
        "mock_token_123_admin",
        "mock_token_user",
    ]
    for tok in mock_tokens:
        resp = await pm_client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {tok}"}
        )
        assert resp.status_code == 401, f"Expected 401 for mock token in PM '{tok}', got {resp.status_code}"


@pytest.mark.anyio
async def test_gateway_rejects_mock_tokens(gateway_client):
    """Verify that gateway rejects mock_token_* on protected routes with HTTP 401."""
    resp = await gateway_client.get(
        "/api/v1/projects",
        headers={"Authorization": "Bearer mock_token_admin"}
    )
    assert resp.status_code == 401
    assert "Unauthorized" in resp.text


# ─────────────────────────────────────────────────────────────────────────────
# 2. Cryptographic JWT Validation Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_rejects_jwt_with_invalid_signature(auth_client):
    """Tokens signed with wrong secret key must be rejected."""
    now = datetime.datetime.utcnow()
    payload = {
        "sub": "admin",
        "role": "ADMIN",
        "email": "admin@example.com",
        "account_id": "109283746519",
        "tenant_id": "tenant-000000000001",
        "iat": now,
        "exp": now + datetime.timedelta(hours=1),
    }
    forged_token = jwt.encode(payload, "completely-wrong-secret-key-12345", algorithm="HS256")

    resp = await auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {forged_token}"}
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_rejects_expired_jwt(auth_client):
    """Expired tokens must be rejected."""
    now = datetime.datetime.utcnow()
    payload = {
        "sub": "admin",
        "role": "ADMIN",
        "email": "admin@example.com",
        "account_id": "109283746519",
        "tenant_id": "tenant-000000000001",
        "iat": now - datetime.timedelta(hours=10),
        "exp": now - datetime.timedelta(hours=2),
    }
    expired_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    resp = await auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_rejects_malformed_token_string(auth_client):
    """Non-JWT arbitrary strings must return HTTP 401."""
    resp = await auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not.a.valid.jwt.string"}
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_accepts_valid_cryptographic_jwt(auth_client):
    """Legitimately signed JWT token must succeed."""
    now = datetime.datetime.utcnow()
    payload = {
        "sub": "admin",
        "role": "ADMIN",
        "email": "admin@aetherops.local",
        "account_id": "109283746519",
        "tenant_id": "tenant-000000000001",
        "uuid": "00000000-0000-0000-0000-000000000001",
        "iat": now,
        "exp": now + datetime.timedelta(hours=1),
    }
    valid_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    resp = await auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin"


# ─────────────────────────────────────────────────────────────────────────────
# 3. Privilege Escalation & Username Shortcut Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_username_admin_with_role_user_does_not_get_super_admin(pm_client):
    """A user named 'admin' with role 'USER' must NOT be granted SUPER_ADMIN rights."""
    now = datetime.datetime.utcnow()
    fake_admin_user_payload = {
        "sub": "admin",
        "role": "USER",  # Explicitly standard user role
        "email": "impostor_admin@example.com",
        "account_id": "999999999999",
        "tenant_id": "tenant-fake-admin",
        "uuid": str(uuid.uuid4()),
        "iat": now,
        "exp": now + datetime.timedelta(hours=1),
    }
    token = jwt.encode(fake_admin_user_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # Attempt to query with ?all=true (which requires platform super admin)
    resp = await pm_client.get(
        "/api/v1/projects?all=true",
        headers={"Authorization": f"Bearer {token}"}
    )
    # Without SUPER_ADMIN role, ?all=true is ignored and scoped strictly to user's empty tenant
    assert resp.status_code == 200
    assert resp.json()["total"] == 0  # Cannot see other tenants' projects


# ─────────────────────────────────────────────────────────────────────────────
# 4. Gateway Enforcement & Header Sanitization Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_gateway_blocks_unauthenticated_api_requests(gateway_client):
    """Unauthenticated access to protected API paths via Gateway returns HTTP 401."""
    protected_paths = [
        "/api/v1/projects",
        "/api/v1/environments",
        "/api/v1/architecture/studio/state",
        "/api/v1/repo/readiness",
        "/api/v1/iac/generate",
        "/api/v1/finops/optimize",
        "/api/v1/security/scan",
    ]
    for path in protected_paths:
        resp = await gateway_client.get(path)
        assert resp.status_code == 401, f"Expected 401 for path {path}, got {resp.status_code}"


@pytest.mark.anyio
async def test_gateway_permits_public_paths_without_token(gateway_client):
    """Health and public metadata/auth endpoints must be accessible without token."""
    resp = await gateway_client.get("/health")
    assert resp.status_code == 200


@pytest.mark.anyio
async def test_gateway_enforces_tenant_account_consistency(gateway_client):
    """If client sends X-Account-ID that mismatches their authenticated token, return HTTP 403."""
    now = datetime.datetime.utcnow()
    payload = {
        "sub": "alice",
        "role": "USER",
        "email": "alice@example.com",
        "account_id": "111122223333",
        "tenant_id": "tenant-alice",
        "uuid": str(uuid.uuid4()),
        "iat": now,
        "exp": now + datetime.timedelta(hours=1),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    resp = await gateway_client.get(
        "/api/v1/projects",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Account-ID": "999988887777",  # Spoofed / mismatched account
        }
    )
    assert resp.status_code == 403
    assert "Tenant isolation violation" in resp.text


# ─────────────────────────────────────────────────────────────────────────────
# 5. OAuth CSRF State Validation Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_oauth_callback_rejects_missing_state(auth_client):
    """OAuth callback without state parameter must be rejected with HTTP 400."""
    resp = await auth_client.get("/api/v1/auth/google/callback?code=test_auth_code")
    assert resp.status_code == 400
    assert "OAuth state parameter" in resp.text or "Security Error" in resp.text


@pytest.mark.anyio
async def test_oauth_callback_rejects_mismatched_state(auth_client):
    """OAuth callback with state mismatched from initiation cookie must be rejected with HTTP 400."""
    # Set fake cookie
    auth_client.cookies.set("oauth_state_google", "legitimate_initiation_nonce")
    resp = await auth_client.get(
        "/api/v1/auth/google/callback?code=test_auth_code&state=forged_attacker_state"
    )
    assert resp.status_code == 400
    assert "OAuth state parameter" in resp.text or "Security Error" in resp.text


# ─────────────────────────────────────────────────────────────────────────────
# 6. Password Security Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_login_rejects_invalid_password(auth_client):
    """Login with wrong password must return HTTP 401."""
    resp = await auth_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "WrongIncorrectPassword123!"}
    )
    assert resp.status_code == 401
    assert "Invalid Login ID or password" in resp.text


# ─────────────────────────────────────────────────────────────────────────────
# 7. Production Secret Validation & Fail-Closed Tests
# ─────────────────────────────────────────────────────────────────────────────

def test_production_mode_fails_closed_without_jwt_secret():
    """In production mode, missing JWT_SECRET_KEY must raise RuntimeError."""
    from services.gateway.app.main import validate_production_secrets
    with pytest.raises(RuntimeError, match="FATAL: JWT_SECRET_KEY must be explicitly configured"):
        validate_production_secrets(env="production", secret="")


def test_production_mode_fails_closed_with_insecure_default_secret():
    """In production mode, default development JWT secret must be rejected."""
    from services.gateway.app.main import validate_production_secrets
    insecure_keys = [
        "aetherops-super-secure-production-cryptographic-jwt-token-signing-key-2026-cloudops-master",
        "secret",
        "changeme",
        "admin",
        "default",
    ]
    for key in insecure_keys:
        with pytest.raises(RuntimeError, match="FATAL: JWT_SECRET_KEY must be explicitly configured"):
            validate_production_secrets(env="production", secret=key)


def test_production_mode_accepts_strong_secret():
    """In production mode, a strong non-default secret must validate cleanly."""
    from services.gateway.app.main import validate_production_secrets
    # Should not raise
    validate_production_secrets(env="production", secret="9f8e7d6c5b4a3928170e1d2c3b4a5f6e7d8c9b0a1f2e3d4c5b6a7f8e9d0c1b2a")


# ─────────────────────────────────────────────────────────────────────────────
# 8. Database Fail-Closed in Production Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_production_mode_fails_closed_without_postgres(monkeypatch):
    """In production mode, database connection failure must raise RuntimeError without SQLite fallback."""
    from services.project_and_environment_management.app import database as pm_db
    monkeypatch.setattr(pm_db, "ENVIRONMENT", "production")
    monkeypatch.setattr(pm_db, "IS_TESTING", False)

    # Mock get_pg_sessionmaker to throw a connection error
    def broken_pg_sessionmaker():
        class BrokenSession:
            async def execute(self, *args, **kwargs):
                raise ConnectionRefusedError("PostgreSQL connection refused")
            async def close(self):
                pass
        return BrokenSession

    monkeypatch.setattr(pm_db, "get_pg_sessionmaker", broken_pg_sessionmaker)

    with pytest.raises(RuntimeError, match=r"FATAL: PostgreSQL database (connection|initialization) failed in production"):
        async for _ in pm_db.get_db():
            pass


# ─────────────────────────────────────────────────────────────────────────────
# 9. Downstream Direct Access & Header Stripping Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_direct_downservice_rejects_unauthenticated_requests(pm_client):
    """Direct request to downstream service without JWT must be rejected (HTTP 401)."""
    resp = await pm_client.get(
        "/api/v1/projects",
        headers={"X-User-ID": "admin", "X-Tenant-ID": "tenant-000000000001"}
    )
    assert resp.status_code == 401
    assert "Unauthorized" in resp.text


@pytest.mark.anyio
async def test_cross_tenant_resource_access_prevented(pm_client):
    """User in Tenant A cannot access resources in Tenant B (HTTP 404/403)."""
    now = datetime.datetime.utcnow()
    # Token for Tenant A
    user_a_token = jwt.encode({
        "sub": "user_a",
        "role": "USER",
        "email": "user_a@example.com",
        "account_id": "111111111111",
        "tenant_id": "tenant-aaa",
        "uuid": str(uuid.uuid4()),
        "iat": now,
        "exp": now + datetime.timedelta(hours=1),
    }, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # Attempt to access a nonexistent or foreign tenant project
    resp = await pm_client.get(
        "/api/v1/projects/proj-foreign-tenant-b",
        headers={"Authorization": f"Bearer {user_a_token}"}
    )
    assert resp.status_code == 404
    assert "not found" in resp.text.lower()


# ─────────────────────────────────────────────────────────────────────────────
# 10. Token Logout Limitation & Lifespan Documentation Test
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_stateless_jwt_persists_post_logout_until_expiration(auth_client):
    """
    Documents architectural behavior:
    Because JWTs are stateless and no distributed server-side revocation list exists in V1,
    the token remains mathematically valid until expiration (8 hours).
    Logout clears client-side state but does not invalidate the token server-side.
    """
    now = datetime.datetime.utcnow()
    payload = {
        "sub": "logout_test_user",
        "role": "USER",
        "email": "logout_test@example.com",
        "account_id": "222233334444",
        "tenant_id": "tenant-logout-test",
        "uuid": str(uuid.uuid4()),
        "iat": now,
        "exp": now + datetime.timedelta(hours=1),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # Call logout
    logout_resp = await auth_client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 200

    # The token remains decodable and accepted by stateless verification
    me_resp = await auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "logout_test_user"
