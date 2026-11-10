# services/source_and_cloud_connection/tests/test_isolation_security.py
"""
Multi-tenant isolation and cache-bypass tests for Module 2: Source & Cloud Connection.
"""
import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.auth import create_access_token


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def client():
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


UID = str(uuid.uuid4())[:8]
USER_ALICE = f"sc_alice_{UID}"
USER_BOB = f"sc_bob_{UID}"


@pytest.mark.anyio
async def test_git_connection_cross_tenant_isolation_and_cache_bypass(client):
    """
    Verify:
    1. Bob cannot see Alice's GitConnection in list_connections.
    2. Bob cannot view Alice's GitConnection detail.
    3. Cache hit on Alice's GitConnection does not grant Bob access.
    4. Bob cannot access Alice's connection snapshot.
    5. Bob cannot delete Alice's GitConnection.
    """
    token_alice = create_access_token(USER_ALICE, "USER", f"{USER_ALICE}@example.com")
    token_bob = create_access_token(USER_BOB, "USER", f"{USER_BOB}@example.com")
    headers_alice = {"Authorization": f"Bearer {token_alice}"}
    headers_bob = {"Authorization": f"Bearer {token_bob}"}

    # 1. Alice creates a Git connection
    res_a = await client.post(
        "/api/v1/connections",
        json={
            "project_id": f"proj_a_{UID}",
            "environment_id": f"env_a_{UID}",
            "repo_url": "https://github.com/alice/private-repo",
            "branch": "main",
            "pat_label": "alice-pat",
        },
        headers=headers_alice,
    )
    assert res_a.status_code == 201, res_a.text
    alice_conn = res_a.json()
    alice_conn_id = alice_conn["id"]

    # 2. Bob creates a Git connection
    res_b = await client.post(
        "/api/v1/connections",
        json={
            "project_id": f"proj_b_{UID}",
            "environment_id": f"env_b_{UID}",
            "repo_url": "https://github.com/bob/public-repo",
            "branch": "main",
            "pat_label": "bob-pat",
        },
        headers=headers_bob,
    )
    assert res_b.status_code == 201, res_b.text
    bob_conn = res_b.json()
    bob_conn_id = bob_conn["id"]

    # 3. Bob lists connections: Alice's connection must NOT be visible
    bob_list = await client.get("/api/v1/connections", headers=headers_bob)
    assert bob_list.status_code == 200
    bob_conn_ids = [c["id"] for c in bob_list.json()["connections"]]
    assert bob_conn_id in bob_conn_ids
    assert alice_conn_id not in bob_conn_ids

    # 4. Bob tries to get Alice's connection: must 404
    bob_get_alice_direct = await client.get(f"/api/v1/connections/{alice_conn_id}", headers=headers_bob)
    assert bob_get_alice_direct.status_code == 404

    # 5. Alice accesses her connection (populating detail cache)
    alice_get = await client.get(f"/api/v1/connections/{alice_conn_id}", headers=headers_alice)
    assert alice_get.status_code == 200
    assert alice_get.json()["id"] == alice_conn_id

    # 6. Bob tries to access Alice's connection after cache is warm: must STILL 404
    bob_get_alice_cached = await client.get(f"/api/v1/connections/{alice_conn_id}", headers=headers_bob)
    assert bob_get_alice_cached.status_code == 404

    # 7. Bob tries to access Alice's connection snapshot: must 404
    bob_snap = await client.get(f"/api/v1/connections/{alice_conn_id}/snapshot", headers=headers_bob)
    assert bob_snap.status_code == 404

    # 8. Bob attempts to delete Alice's connection: must 404
    bob_del = await client.delete(f"/api/v1/connections/{alice_conn_id}", headers=headers_bob)
    assert bob_del.status_code == 404


@pytest.mark.anyio
async def test_admin_connection_not_leaked_to_regular_user(client):
    """
    Ensure GitConnections created by admin or root_admin are NOT accessible
    to arbitrary regular users (fixing the legacy owner.in_(['root_admin', 'admin']) leak).
    """
    admin_headers = {"X-Admin-Key": "aetherops-secret-admin-key"}
    regular_token = create_access_token(f"reg_user_{UID}", "USER", f"reg_{UID}@example.com")
    reg_headers = {"Authorization": f"Bearer {regular_token}"}

    env_id = f"env_admin_{UID}_{uuid.uuid4().hex[:4]}"
    proj_id = f"proj_admin_{UID}_{uuid.uuid4().hex[:4]}"

    # 1. Admin creates a connection
    res_admin = await client.post(
        "/api/v1/connections",
        json={
            "project_id": proj_id,
            "environment_id": env_id,
            "repo_url": "https://github.com/admin-corp/top-secret-infra",
            "branch": "main",
            "pat_label": "admin-pat",
        },
        headers=admin_headers,
    )
    assert res_admin.status_code == 201, res_admin.text
    admin_conn_id = res_admin.json()["id"]

    # 2. Regular user tries to access admin's connection directly by ID -> MUST be 404 Not Found
    res_reg_get = await client.get(f"/api/v1/connections/{admin_conn_id}", headers=reg_headers)
    assert res_reg_get.status_code == 404, "VULNERABILITY: Regular user accessed admin connection by ID!"

    # 3. Regular user tries to access admin's connection by environment ID -> MUST be 404 Not Found
    res_reg_env = await client.get(f"/api/v1/connections/env/{env_id}", headers=reg_headers)
    assert res_reg_env.status_code == 404, "VULNERABILITY: Regular user accessed admin connection by environment!"

    # 4. Admin CAN access their own connection
    res_admin_get = await client.get(f"/api/v1/connections/{admin_conn_id}", headers=admin_headers)
    assert res_admin_get.status_code == 200
    assert res_admin_get.json()["id"] == admin_conn_id


@pytest.mark.anyio
async def test_cloud_connection_cross_tenant_isolation(client):
    """
    Verify CloudConnection endpoints strictly enforce tenant and caller ownership.
    """
    token_tenant1 = create_access_token(f"alice_cloud_{UID}", "USER", f"alice_{UID}@example.com")
    token_tenant2 = create_access_token(f"bob_cloud_{UID}", "USER", f"bob_{UID}@example.com")
    tenant1_id = f"tenant-1-{UID}"
    tenant2_id = f"tenant-2-{UID}"

    headers_t1 = {"Authorization": f"Bearer {token_tenant1}", "X-Tenant-ID": tenant1_id}
    headers_t2 = {"Authorization": f"Bearer {token_tenant2}", "X-Tenant-ID": tenant2_id}

    env_id = f"env_cloud_{UID}_{uuid.uuid4().hex[:4]}"
    proj_id = f"proj_cloud_{UID}_{uuid.uuid4().hex[:4]}"

    # 1. Alice creates cloud connection in Tenant 1
    create_res = await client.post(
        "/api/v1/cloud/connections",
        json={
            "project_id": proj_id,
            "environment_id": env_id,
            "auth_type": "ACCESS_KEYS",
            "aws_region": "us-east-1",
            "access_key_id": "AKIAIOSFODNN7EXAMPLE",
            "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        },
        headers=headers_t1,
    )
    assert create_res.status_code == 201, create_res.text
    cloud_id = create_res.json()["id"]

    # 2. Bob in Tenant 2 tries to read Alice's cloud connection by ID -> 404
    bob_get = await client.get(f"/api/v1/cloud/connections/{cloud_id}", headers=headers_t2)
    assert bob_get.status_code == 404

    # 3. Bob in Tenant 2 tries to read Alice's cloud connection by env -> 404
    bob_env = await client.get(f"/api/v1/cloud/connections/env/{env_id}", headers=headers_t2)
    assert bob_env.status_code == 404

    # 4. Bob in Tenant 2 tries to update Alice's cloud connection -> 404
    bob_patch = await client.patch(
        f"/api/v1/cloud/connections/{cloud_id}",
        json={"aws_region": "eu-west-1"},
        headers=headers_t2,
    )
    assert bob_patch.status_code == 404

    # 5. Bob in Tenant 2 tries to delete Alice's cloud connection -> 404
    bob_del = await client.delete(f"/api/v1/cloud/connections/{cloud_id}", headers=headers_t2)
    assert bob_del.status_code == 404

    # 6. Alice in Tenant 1 CAN read her cloud connection
    alice_get = await client.get(f"/api/v1/cloud/connections/{cloud_id}", headers=headers_t1)
    assert alice_get.status_code == 200
    assert alice_get.json()["id"] == cloud_id
    assert alice_get.json()["tenant_id"] == tenant1_id

