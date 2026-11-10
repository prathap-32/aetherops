# services/project_and_environment_management/tests/test_isolation_security.py
"""
Phase 0 Security Containment & Multi-Tenant Isolation Tests.

Verifies:
1. Universal ADMIN role assignment is eliminated (default role is USER).
2. Users can only list and view their own projects.
3. Cache-aside authorization bypass is prevented (cache hit on Alice's project does not grant Bob access).
4. Cross-tenant mutation (delete) is blocked.
5. Super admin retains platform-wide visibility.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def client():
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


import uuid

UID = str(uuid.uuid4())[:8]
ALICE_USER = f"alice_{UID}"
BOB_USER = f"bob_{UID}"
ALICE_EMAIL = f"alice_{UID}@example.com"
BOB_EMAIL = f"bob_{UID}@example.com"


@pytest.mark.anyio
async def test_user_registration_defaults_to_user_role(client):
    """Verify new user registration defaults to role USER rather than ADMIN."""
    from app.auth import register_user
    res = await register_user(ALICE_USER, ALICE_EMAIL, "SecurePass123!")
    assert res["role"] == "USER"
    assert res["username"] == ALICE_USER

    res_b = await register_user(BOB_USER, BOB_EMAIL, "SecurePass123!")
    assert res_b["role"] == "USER"
    assert res_b["username"] == BOB_USER


@pytest.mark.anyio
async def test_project_cross_tenant_isolation_and_cache_bypass(client):
    """
    Verify:
    1. Bob cannot see Alice's project in list_projects.
    2. Bob cannot view Alice's project detail.
    3. Alice viewing her project populates detail cache.
    4. Bob cannot view Alice's cached project (cache-aside bypass is closed).
    5. Bob cannot delete Alice's project.
    """
    # 1. Login Alice
    res_a = await client.post("/api/v1/auth/login", json={"username": ALICE_USER, "password": "SecurePass123!"})
    assert res_a.status_code == 200, res_a.text
    token_alice = res_a.json()["token"]
    headers_alice = {"Authorization": f"Bearer {token_alice}"}

    # 2. Login Bob
    res_b = await client.post("/api/v1/auth/login", json={"username": BOB_USER, "password": "SecurePass123!"})
    assert res_b.status_code == 200, res_b.text
    token_bob = res_b.json()["token"]
    headers_bob = {"Authorization": f"Bearer {token_bob}"}

    # 3. Alice creates a project
    create_a = await client.post(
        "/api/v1/projects",
        json={"name": f"AliceConf_{UID}", "project_type": "web_application", "description": "Alice private project"},
        headers=headers_alice,
    )
    assert create_a.status_code == 201, create_a.text
    alice_proj = create_a.json()
    alice_proj_id = alice_proj["id"]

    # 4. Bob creates a project
    create_b = await client.post(
        "/api/v1/projects",
        json={"name": f"BobPub_{UID}", "project_type": "web_application", "description": "Bob project"},
        headers=headers_bob,
    )
    assert create_b.status_code == 201, create_b.text
    bob_proj = create_b.json()
    bob_proj_id = bob_proj["id"]

    # 5. Bob lists projects: must NOT contain Alice's project
    bob_list = await client.get("/api/v1/projects", headers=headers_bob)
    assert bob_list.status_code == 200
    bob_project_ids = [p["id"] for p in bob_list.json()["projects"]]
    assert bob_proj_id in bob_project_ids
    assert alice_proj_id not in bob_project_ids

    # 6. Bob tries to get Alice's project (uncached): must 404
    bob_get_alice_direct = await client.get(f"/api/v1/projects/{alice_proj_id}", headers=headers_bob)
    assert bob_get_alice_direct.status_code == 404

    # 7. Alice gets her own project (populating cache)
    alice_get = await client.get(f"/api/v1/projects/{alice_proj_id}", headers=headers_alice)
    assert alice_get.status_code == 200
    assert alice_get.json()["id"] == alice_proj_id

    # 8. Bob tries to get Alice's project now that it is cached: must STILL 404
    bob_get_alice_cached = await client.get(f"/api/v1/projects/{alice_proj_id}", headers=headers_bob)
    assert bob_get_alice_cached.status_code == 404

    # 9. Bob attempts to delete Alice's project: must 404
    bob_del_alice = await client.delete(f"/api/v1/projects/{alice_proj_id}", headers=headers_bob)
    assert bob_del_alice.status_code == 404


@pytest.mark.anyio
async def test_super_admin_can_view_all_projects(client):
    """Verify super admin retains administrative oversight across all projects via explicit audit view."""
    admin_login = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "AetherOps@2026!"})
    assert admin_login.status_code == 200
    headers_admin = {"Authorization": f"Bearer {admin_login.json()['token']}"}

    all_projs = await client.get("/api/v1/projects?all=true", headers=headers_admin)
    assert all_projs.status_code == 200
    names = [p["name"] for p in all_projs.json()["projects"]]
    assert f"AliceConf_{UID}" in names
    assert f"BobPub_{UID}" in names
