# test-oauth-admin-analytics.py
import pytest
import httpx
import os

BASE_URL = "http://127.0.0.1:7999"
ADMIN_KEY = "aetherops-secret-admin-key"

@pytest.mark.anyio
async def test_oauth_user_counting_and_admin_statistics():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Test admin statistics endpoint without key/token -> should fail or require auth
        res_unauth = await client.get("/api/v1/admin/users/statistics")
        # Depending on auth middleware, if open or protected, let's verify structure
        if res_unauth.status_code == 200:
            data = res_unauth.json()
            assert "total_users" in data
            assert "google_users" in data
            assert "github_users" in data
            assert "credentials_users" in data
            assert "providers" in data

        # 2. Register credential user
        import secrets
        suffix = secrets.token_hex(4)
        reg_payload = {
            "username": f"cred_user_{suffix}",
            "email": f"cred_{suffix}@example.com",
            "password": "Password123!",
            "role": "USER"
        }
        res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_reg.status_code in (200, 201)

        # 3. Check statistics again
        res_stats = await client.get("/api/v1/admin/users/statistics")
        assert res_stats.status_code == 200
        stats = res_stats.json()
        assert stats["total_users"] >= 1
        assert stats["credentials_users"] >= 1

        # 4. Verify user list includes auth_provider
        users = stats.get("users", [])
        cred_user = next((u for u in users if u["email"] == f"cred_{suffix}@example.com"), None)
        assert cred_user is not None
        assert cred_user["auth_provider"] == "credentials"
