# services/project_and_environment_management/tests/test_projects.py
"""
End-to-end pytest suite for Module 1: Project & Environment Management.

Covers:
- Health check
- Auth (login / logout / invalid credentials)
- Project CRUD (create, list, get, update, delete)
- Environment CRUD (create, list, get, update, delete)
- Lifecycle status advancement
- Validation edge-cases (duplicate env name, bad region, bad type)
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# ── Test fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def client():
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def api_key_headers():
    return {"X-Admin-Key": "aetherops-secret-admin-key"}


# ── Helper ────────────────────────────────────────────────────────────────────

async def _create_project(client, headers, name="TestProj", ptype="web_application"):
    res = await client.post("/api/v1/projects",
        json={"name": name, "project_type": ptype, "description": "Test project"},
        headers=headers)
    assert res.status_code == 201, res.text
    return res.json()


async def _create_env(client, headers, project_id, name="Dev", etype="development", region="ap-south-1"):
    res = await client.post(f"/api/v1/projects/{project_id}/environments",
        json={"name": name, "env_type": etype, "aws_region": region},
        headers=headers)
    assert res.status_code == 201, res.text
    return res.json()


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_health(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


@pytest.mark.anyio
async def test_root(client):
    res = await client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "project-manager" in data["service"] or "Module 1" in data["service"]


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_auth_api_key(client, api_key_headers):
    res = await client.get("/api/v1/projects", headers=api_key_headers)
    assert res.status_code == 200


@pytest.mark.anyio
async def test_auth_login_valid(client):
    res = await client.post("/api/v1/auth/login",
        json={"username": "admin", "password": "AetherOps@2026!"})
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["username"] == "admin"


@pytest.mark.anyio
async def test_auth_login_invalid(client):
    res = await client.post("/api/v1/auth/login",
        json={"username": "admin", "password": "wrongpassword"})
    assert res.status_code == 401


@pytest.mark.anyio
async def test_auth_logout(client):
    res = await client.post("/api/v1/auth/logout")
    assert res.status_code == 200


@pytest.mark.anyio
async def test_unauth_rejected(client):
    res = await client.get("/api/v1/projects")
    assert res.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT CRUD
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_create_project(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="CRUDProject")
    assert proj["name"] == "CRUDProject"
    assert proj["project_type"] == "web_application"
    assert proj["status"] == "CREATED"
    assert proj["environment_count"] == 0
    assert "id" in proj


@pytest.mark.anyio
async def test_list_projects(client, api_key_headers):
    await _create_project(client, api_key_headers, name="ListProj1")
    await _create_project(client, api_key_headers, name="ListProj2")
    res = await client.get("/api/v1/projects", headers=api_key_headers)
    assert res.status_code == 200
    data = res.json()
    assert "projects" in data
    assert data["total"] >= 2


@pytest.mark.anyio
async def test_get_project(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="GetProj")
    res = await client.get(f"/api/v1/projects/{proj['id']}", headers=api_key_headers)
    assert res.status_code == 200
    assert res.json()["id"] == proj["id"]


@pytest.mark.anyio
async def test_get_project_not_found(client, api_key_headers):
    res = await client.get("/api/v1/projects/nonexistent-uuid", headers=api_key_headers)
    assert res.status_code == 404


@pytest.mark.anyio
async def test_update_project(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="UpdateProj")
    res = await client.patch(f"/api/v1/projects/{proj['id']}",
        json={"name": "UpdatedName", "status": "ACTIVE"},
        headers=api_key_headers)
    assert res.status_code == 200
    updated = res.json()
    assert updated["name"] == "UpdatedName"
    assert updated["status"] == "ACTIVE"


@pytest.mark.anyio
async def test_delete_project(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="DeleteProj")
    res = await client.delete(f"/api/v1/projects/{proj['id']}", headers=api_key_headers)
    assert res.status_code == 204
    # Verify gone
    res2 = await client.get(f"/api/v1/projects/{proj['id']}", headers=api_key_headers)
    assert res2.status_code == 404


@pytest.mark.anyio
async def test_create_project_invalid_type(client, api_key_headers):
    res = await client.post("/api/v1/projects",
        json={"name": "BadType", "project_type": "invalid_type"},
        headers=api_key_headers)
    assert res.status_code == 422


@pytest.mark.anyio
async def test_create_project_empty_name(client, api_key_headers):
    res = await client.post("/api/v1/projects",
        json={"name": "   ", "project_type": "api_service"},
        headers=api_key_headers)
    assert res.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT CRUD
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_create_environment(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="EnvParent")
    env  = await _create_env(client, api_key_headers, proj["id"], name="Development")
    assert env["name"] == "Development"
    assert env["env_type"] == "development"
    assert env["aws_region"] == "ap-south-1"
    assert env["status"] == "CREATED"
    assert env["project_id"] == proj["id"]


@pytest.mark.anyio
async def test_env_count_increments(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="CountProj")
    await _create_env(client, api_key_headers, proj["id"], name="Dev")
    await _create_env(client, api_key_headers, proj["id"], name="Prod", etype="production", region="us-east-1")
    # Fetch project and check count
    res = await client.get(f"/api/v1/projects/{proj['id']}", headers=api_key_headers)
    assert res.json()["environment_count"] == 2


@pytest.mark.anyio
async def test_list_environments(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="ListEnvProj")
    await _create_env(client, api_key_headers, proj["id"], name="Dev")
    res = await client.get(f"/api/v1/projects/{proj['id']}/environments", headers=api_key_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1


@pytest.mark.anyio
async def test_get_environment(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="GetEnvProj")
    env  = await _create_env(client, api_key_headers, proj["id"])
    res  = await client.get(f"/api/v1/projects/{proj['id']}/environments/{env['id']}", headers=api_key_headers)
    assert res.status_code == 200
    assert res.json()["id"] == env["id"]


@pytest.mark.anyio
async def test_update_environment(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="UpdEnvProj")
    env  = await _create_env(client, api_key_headers, proj["id"])
    res  = await client.patch(
        f"/api/v1/projects/{proj['id']}/environments/{env['id']}",
        json={"description": "Updated description"},
        headers=api_key_headers)
    assert res.status_code == 200
    assert res.json()["description"] == "Updated description"


@pytest.mark.anyio
async def test_delete_environment(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="DelEnvProj")
    env  = await _create_env(client, api_key_headers, proj["id"])
    res  = await client.delete(
        f"/api/v1/projects/{proj['id']}/environments/{env['id']}",
        headers=api_key_headers)
    assert res.status_code == 204
    # Verify gone
    res2 = await client.get(
        f"/api/v1/projects/{proj['id']}/environments/{env['id']}",
        headers=api_key_headers)
    assert res2.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# LIFECYCLE STATE MACHINE
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_lifecycle_status_advance(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="LifecycleProj")
    env  = await _create_env(client, api_key_headers, proj["id"])
    assert env["status"] == "CREATED"

    for new_status in ["CONFIGURED", "REPOSITORY_CONNECTED", "ANALYZED", "ARCHITECTURE_READY", "ACTIVE"]:
        res = await client.patch(
            f"/api/v1/projects/{proj['id']}/environments/{env['id']}/status",
            json={"status": new_status},
            headers=api_key_headers)
        assert res.status_code == 200, res.text
        assert res.json()["status"] == new_status


@pytest.mark.anyio
async def test_lifecycle_failed_state(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="FailProj")
    env  = await _create_env(client, api_key_headers, proj["id"])
    res  = await client.patch(
        f"/api/v1/projects/{proj['id']}/environments/{env['id']}/status",
        json={"status": "FAILED"},
        headers=api_key_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "FAILED"


@pytest.mark.anyio
async def test_lifecycle_invalid_status(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="BadStatusProj")
    env  = await _create_env(client, api_key_headers, proj["id"])
    res  = await client.patch(
        f"/api/v1/projects/{proj['id']}/environments/{env['id']}/status",
        json={"status": "INVALID_STATUS"},
        headers=api_key_headers)
    assert res.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_duplicate_env_name_rejected(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="DupEnvProj")
    await _create_env(client, api_key_headers, proj["id"], name="DupEnv")
    res = await client.post(f"/api/v1/projects/{proj['id']}/environments",
        json={"name": "DupEnv", "env_type": "staging", "aws_region": "us-east-1"},
        headers=api_key_headers)
    assert res.status_code == 409


@pytest.mark.anyio
async def test_invalid_aws_region_rejected(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="BadRegionProj")
    res = await client.post(f"/api/v1/projects/{proj['id']}/environments",
        json={"name": "Env", "env_type": "development", "aws_region": "invalid-region-99"},
        headers=api_key_headers)
    assert res.status_code == 422


@pytest.mark.anyio
async def test_invalid_env_type_rejected(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="BadEnvTypeProj")
    res = await client.post(f"/api/v1/projects/{proj['id']}/environments",
        json={"name": "Env", "env_type": "testing", "aws_region": "us-east-1"},
        headers=api_key_headers)
    assert res.status_code == 422


@pytest.mark.anyio
async def test_all_project_types_valid(client, api_key_headers):
    types = ["web_application", "api_service", "data_pipeline", "ml_workload", "static_site", "microservices"]
    for i, ptype in enumerate(types):
        proj = await _create_project(client, api_key_headers, name=f"TypeTest{i}", ptype=ptype)
        assert proj["project_type"] == ptype


@pytest.mark.anyio
async def test_project_with_all_env_types(client, api_key_headers):
    proj = await _create_project(client, api_key_headers, name="AllEnvTypes")
    for etype, region in [("development","ap-south-1"), ("staging","eu-west-1"), ("production","us-east-1")]:
        env = await _create_env(client, api_key_headers, proj["id"], name=etype.capitalize(), etype=etype, region=region)
        assert env["env_type"] == etype
    # Confirm count
    res = await client.get(f"/api/v1/projects/{proj['id']}", headers=api_key_headers)
    assert res.json()["environment_count"] == 3
