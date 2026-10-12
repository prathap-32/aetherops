# services/source_and_cloud_connection/tests/test_source_connection.py
"""
End-to-end pytest suite for Module 2: Source & Cloud Connection.

Covers:
- Health check + root endpoint
- Auth (login / logout / invalid credentials / API key)
- GitConnection CRUD (create, list, get, update, delete)
- Connection validation + snapshot capture
- Snapshot retrieval + refresh
- Validation edge-cases (bad URL, duplicate env, missing fields)
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport


@pytest_asyncio.fixture(scope="session")
async def client():
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def hdrs():
    return {"X-Admin-Key": "aetherops-secret-admin-key"}


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _mk_conn(client, hdrs, proj="proj-001", env="env-001",
                   url="https://github.com/test/repo", branch="main"):
    res = await client.post("/api/v1/connections",
        json={"project_id": proj, "environment_id": env,
              "repo_url": url, "branch": branch, "pat_label": "test-pat"},
        headers=hdrs)
    assert res.status_code == 201, res.text
    return res.json()


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH + ROOT
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
    assert "Module 2" in data["service"]
    assert data["port"] == 8002


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_auth_api_key(client, hdrs):
    res = await client.get("/api/v1/connections", headers=hdrs)
    assert res.status_code == 200


@pytest.mark.anyio
async def test_auth_login_valid(client):
    res = await client.post("/api/v1/auth/login",
        json={"username": "admin", "password": "AetherOps@2026!"})
    assert res.status_code == 200
    assert "token" in res.json()
    assert res.json()["username"] == "admin"


@pytest.mark.anyio
async def test_auth_login_invalid(client):
    res = await client.post("/api/v1/auth/login",
        json={"username": "admin", "password": "wrongpass"})
    assert res.status_code == 401


@pytest.mark.anyio
async def test_auth_logout(client):
    res = await client.post("/api/v1/auth/logout")
    assert res.status_code == 200


@pytest.mark.anyio
async def test_unauth_rejected(client):
    res = await client.get("/api/v1/connections")
    assert res.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# GIT CONNECTION CRUD
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_create_connection(client, hdrs):
    conn = await _mk_conn(client, hdrs, proj="p1", env="e1")
    assert conn["repo_name"] == "test/repo"
    assert conn["branch"] == "main"
    assert conn["status"] == "PENDING"
    assert conn["project_id"] == "p1"
    assert conn["environment_id"] == "e1"
    assert "id" in conn


@pytest.mark.anyio
async def test_list_connections(client, hdrs):
    await _mk_conn(client, hdrs, proj="p2", env="e2", url="https://github.com/org/repoA")
    await _mk_conn(client, hdrs, proj="p3", env="e3", url="https://github.com/org/repoB")
    res = await client.get("/api/v1/connections", headers=hdrs)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 2
    assert "connections" in data


@pytest.mark.anyio
async def test_get_connection(client, hdrs):
    conn = await _mk_conn(client, hdrs, proj="pg1", env="eg1", url="https://github.com/org/get-test")
    res  = await client.get(f"/api/v1/connections/{conn['id']}", headers=hdrs)
    assert res.status_code == 200
    assert res.json()["id"] == conn["id"]


@pytest.mark.anyio
async def test_get_connection_not_found(client, hdrs):
    res = await client.get("/api/v1/connections/nonexistent-id", headers=hdrs)
    assert res.status_code == 404


@pytest.mark.anyio
async def test_get_connection_by_env(client, hdrs):
    conn = await _mk_conn(client, hdrs, proj="penv1", env="envlookup1",
                          url="https://github.com/org/envlookup")
    res = await client.get(f"/api/v1/connections/env/{conn['environment_id']}", headers=hdrs)
    assert res.status_code == 200
    assert res.json()["environment_id"] == conn["environment_id"]


@pytest.mark.anyio
async def test_update_connection_branch(client, hdrs):
    conn = await _mk_conn(client, hdrs, proj="pupd", env="eupd",
                          url="https://github.com/org/upd-test")
    res = await client.patch(f"/api/v1/connections/{conn['id']}",
        json={"branch": "develop"}, headers=hdrs)
    assert res.status_code == 200
    assert res.json()["branch"] == "develop"


@pytest.mark.anyio
async def test_delete_connection(client, hdrs):
    conn = await _mk_conn(client, hdrs, proj="pdel", env="edel",
                          url="https://github.com/org/del-test")
    res = await client.delete(f"/api/v1/connections/{conn['id']}", headers=hdrs)
    assert res.status_code == 204
    res2 = await client.get(f"/api/v1/connections/{conn['id']}", headers=hdrs)
    assert res2.status_code == 404


@pytest.mark.anyio
async def test_reconnect_same_env_overwrites(client, hdrs):
    """Creating a second connection for the same env should replace the first."""
    proj, env = "pover", "eover"
    c1 = await _mk_conn(client, hdrs, proj=proj, env=env, url="https://github.com/org/first")
    c2 = await _mk_conn(client, hdrs, proj=proj, env=env, url="https://github.com/org/second")
    assert c1["id"] != c2["id"]
    # Old connection should be gone
    r = await client.get(f"/api/v1/connections/{c1['id']}", headers=hdrs)
    assert r.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION + SNAPSHOT
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_validate_connection(client, hdrs):
    conn = await _mk_conn(client, hdrs, proj="pval", env="eval",
                          url="https://github.com/org/validate-test")
    assert conn["status"] == "PENDING"
    res = await client.post(f"/api/v1/connections/{conn['id']}/validate", headers=hdrs)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "CONNECTED"
    assert data["last_commit_sha"] is not None
    assert data["last_commit_msg"] is not None


@pytest.mark.anyio
async def test_snapshot_after_validate(client, hdrs):
    conn = await _mk_conn(client, hdrs, proj="psnap", env="esnap",
                          url="https://github.com/org/snap-test")
    await client.post(f"/api/v1/connections/{conn['id']}/validate", headers=hdrs)
    res = await client.get(f"/api/v1/connections/{conn['id']}/snapshot", headers=hdrs)
    assert res.status_code == 200
    snap = res.json()
    assert len(snap["file_tree"]) > 0
    assert "primary" in snap["language_hints"]
    assert snap["total_files"] is not None


@pytest.mark.anyio
async def test_snapshot_refresh(client, hdrs):
    conn = await _mk_conn(client, hdrs, proj="pref", env="eref",
                          url="https://github.com/org/refresh-test")
    await client.post(f"/api/v1/connections/{conn['id']}/validate", headers=hdrs)
    res = await client.post(f"/api/v1/connections/{conn['id']}/refresh", headers=hdrs)
    assert res.status_code == 200
    assert len(res.json()["file_tree"]) > 0


@pytest.mark.anyio
async def test_snapshot_not_found_before_validate(client, hdrs):
    conn = await _mk_conn(client, hdrs, proj="pnosnap", env="enosnap",
                          url="https://github.com/org/no-snap")
    res = await client.get(f"/api/v1/connections/{conn['id']}/snapshot", headers=hdrs)
    assert res.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_invalid_repo_url_rejected(client, hdrs):
    res = await client.post("/api/v1/connections",
        json={"project_id": "px", "environment_id": "ex",
              "repo_url": "https://notgithub.com/org/repo", "branch": "main"},
        headers=hdrs)
    assert res.status_code == 422


@pytest.mark.anyio
async def test_empty_project_id_rejected(client, hdrs):
    res = await client.post("/api/v1/connections",
        json={"project_id": "", "environment_id": "ex",
              "repo_url": "https://github.com/org/repo", "branch": "main"},
        headers=hdrs)
    assert res.status_code == 422


@pytest.mark.anyio
async def test_empty_branch_rejected(client, hdrs):
    res = await client.post("/api/v1/connections",
        json={"project_id": "px", "environment_id": "ex",
              "repo_url": "https://github.com/org/repo", "branch": "   "},
        headers=hdrs)
    assert res.status_code == 422


@pytest.mark.anyio
async def test_gitlab_url_accepted(client, hdrs):
    res = await client.post("/api/v1/connections",
        json={"project_id": "pgl", "environment_id": "egl",
              "repo_url": "https://gitlab.com/org/my-project", "branch": "main"},
        headers=hdrs)
    assert res.status_code == 201
    assert res.json()["repo_name"] == "org/my-project"


@pytest.mark.anyio
async def test_pat_token_not_stored_as_plaintext(client, hdrs):
    conn = await _mk_conn(client, hdrs, proj="ppat", env="epat",
                          url="https://github.com/org/pat-test")
    # The API response must never include the raw token
    assert "pat_token" not in conn
    assert "pat_token_hash" not in conn


@pytest.mark.anyio
async def test_repo_name_extracted_correctly(client, hdrs):
    cases = [
        ("https://github.com/myorg/myrepo",      "myorg/myrepo"),
        ("https://github.com/myorg/myrepo.git",  "myorg/myrepo"),
        ("https://github.com/myorg/myrepo/",     "myorg/myrepo"),
    ]
    for i, (url, expected) in enumerate(cases):
        conn = await _mk_conn(client, hdrs, proj=f"pn{i}", env=f"en{i}", url=url)
        assert conn["repo_name"] == expected, f"Expected {expected}, got {conn['repo_name']}"


# ═══════════════════════════════════════════════════════════════════════════════
# GITHUB OAUTH & PAT VERIFICATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_github_oauth_login_endpoint(client):
    res = await client.get("/api/v1/auth/github/login", headers={"Accept": "application/json"})
    assert res.status_code == 200
    data = res.json()
    assert "url" in data
    assert "github.com/login/oauth/authorize" in data["url"]


@pytest.mark.anyio
async def test_github_oauth_mock(client, hdrs):
    res = await client.post("/api/v1/auth/github/mock", headers=hdrs)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["login"] == "aether-developer"


@pytest.mark.anyio
async def test_github_verify_pat_valid(client, hdrs):
    res = await client.post("/api/v1/github/verify-pat",
        json={"pat_token": "ghp_mock_test_token_12345678901234567890"},
        headers=hdrs)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert "username" in data


@pytest.mark.anyio
async def test_github_verify_pat_empty_rejected(client, hdrs):
    res = await client.post("/api/v1/github/verify-pat",
        json={"pat_token": ""},
        headers=hdrs)
    assert res.status_code == 400


@pytest.mark.anyio
async def test_github_list_repos(client, hdrs):
    res = await client.get("/api/v1/github/repos", headers=hdrs)
    assert res.status_code == 200
    data = res.json()
    assert "repos" in data
    assert data["total"] > 0
    assert any(r["name"] == "aethershop" for r in data["repos"])


@pytest.mark.anyio
async def test_github_list_branches(client, hdrs):
    res = await client.get("/api/v1/github/repos/aetherops/aethershop/branches", headers=hdrs)
    assert res.status_code == 200
    data = res.json()
    assert "branches" in data
    assert "main" in data["branches"]


# ═══════════════════════════════════════════════════════════════════════════════
# AWS CLOUD CONNECTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_aws_validate_access_keys(client, hdrs):
    res = await client.post("/api/v1/cloud/aws/validate",
        json={
            "auth_type": "ACCESS_KEYS",
            "aws_region": "us-east-1",
            "access_key_id": "AKIAIOSFODNN7EXAMPLE",
            "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        },
        headers=hdrs)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["account_id"] == "123456789012"
    assert "masked_key" in data
    assert data["masked_key"].startswith("AKIA")


@pytest.mark.anyio
async def test_aws_validate_iam_role_arn(client, hdrs):
    res = await client.post("/api/v1/cloud/aws/validate",
        json={
            "auth_type": "IAM_ROLE_ARN",
            "aws_region": "ap-south-1",
            "role_arn": "arn:aws:iam::112233445566:role/AetherOpsExecutionRole",
            "external_id": "aether-secure-ext-id",
        },
        headers=hdrs)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["account_id"] == "112233445566"
    assert data["role_name"] == "AetherOpsExecutionRole"


@pytest.mark.anyio
async def test_aws_validate_invalid_arn_rejected(client, hdrs):
    res = await client.post("/api/v1/cloud/aws/validate",
        json={
            "auth_type": "IAM_ROLE_ARN",
            "aws_region": "us-east-1",
            "role_arn": "not-a-valid-arn",
        },
        headers=hdrs)
    assert res.status_code == 400


@pytest.mark.anyio
async def test_create_and_get_cloud_connection(client, hdrs):
    res = await client.post("/api/v1/cloud/connections",
        json={
            "project_id": "proj-cloud-01",
            "environment_id": "env-cloud-01",
            "provider": "AWS",
            "auth_type": "ACCESS_KEYS",
            "aws_region": "us-west-2",
            "access_key_id": "AKIAIOSFODNN7EXAMPLE",
            "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        },
        headers=hdrs)
    assert res.status_code == 201
    conn = res.json()
    assert conn["provider"] == "AWS"
    assert conn["status"] == "CONNECTED"
    assert conn["account_id"] == "123456789012"
    assert "secret_access_key" not in conn

    # Get by ID
    get_res = await client.get(f"/api/v1/cloud/connections/{conn['id']}", headers=hdrs)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == conn["id"]

    # Get by Env
    env_res = await client.get(f"/api/v1/cloud/connections/env/env-cloud-01", headers=hdrs)
    assert env_res.status_code == 200
    assert env_res.json()["environment_id"] == "env-cloud-01"

    # List
    list_res = await client.get("/api/v1/cloud/connections", headers=hdrs)
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1


@pytest.mark.anyio
async def test_delete_cloud_connection(client, hdrs):
    res = await client.post("/api/v1/cloud/connections",
        json={
            "project_id": "proj-cloud-del",
            "environment_id": "env-cloud-del",
            "provider": "AWS",
            "auth_type": "IAM_ROLE_ARN",
            "aws_region": "eu-central-1",
            "role_arn": "arn:aws:iam::998877665544:role/TestRole",
        },
        headers=hdrs)
    assert res.status_code == 201
    cid = res.json()["id"]

    del_res = await client.delete(f"/api/v1/cloud/connections/{cid}", headers=hdrs)
    assert del_res.status_code == 204

    get_res = await client.get(f"/api/v1/cloud/connections/{cid}", headers=hdrs)
    assert get_res.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED FINALIZE CONNECTION TEST
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_unified_finalize_connection(client, hdrs):
    """
    Tests end-to-end atomic finalization of both GitHub repository
    and AWS Cloud account in one call.
    """
    payload = {
        "project_id": "proj-finalize-001",
        "environment_id": "env-finalize-001",
        "repo_url": "https://github.com/aetherops/aethershop",
        "branch": "main",
        "git_auth_type": "PAT",
        "github_user": "aether-dev",
        "pat_token": "ghp_mock_token_for_finalize_12345678",
        "pat_label": "prod-git-pat",
        "cloud_provider": "AWS",
        "cloud_auth_type": "ACCESS_KEYS",
        "aws_region": "ap-south-1",
        "access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    }
    res = await client.post("/api/v1/connections/finalize", json=payload, headers=hdrs)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["status"] == "CONNECTED"
    assert "git_connection" in data
    assert data["git_connection"]["repo_name"] == "aetherops/aethershop"
    assert data["git_connection"]["status"] == "CONNECTED"

    assert "cloud_connection" in data
    assert data["cloud_connection"]["provider"] == "AWS"
    assert data["cloud_connection"]["account_id"] == "123456789012"
    assert data["cloud_connection"]["status"] == "CONNECTED"

    assert "snapshot" in data
    assert data["snapshot"] is not None
    assert len(data["snapshot"]["file_tree"]) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# GITHUB OAUTH CONFIG & AWS ENDPOINT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.anyio
async def test_github_oauth_config_get_and_post(client, hdrs):
    # GET config
    res = await client.get("/api/v1/auth/github/config", headers=hdrs)
    assert res.status_code == 200
    cfg = res.json()
    assert "is_configured" in cfg
    assert "redirect_uri" in cfg

    # POST new config
    update_payload = {
        "client_id": "test_client_id_123456",
        "client_secret": "test_client_secret_abcdef",
        "redirect_uri": "http://localhost:8000/api/v1/auth/github/callback"
    }
    res = await client.post("/api/v1/auth/github/config", json=update_payload, headers=hdrs)
    assert res.status_code == 200
    updated = res.json()
    assert updated["is_configured"] is True
    assert updated["client_id"] == "test_client_id_123456"

    # Verify GET reflects update
    res = await client.get("/api/v1/auth/github/config", headers=hdrs)
    assert res.status_code == 200
    cfg2 = res.json()
    assert cfg2["is_configured"] is True
    assert cfg2["client_id"] == "test_client_id_123456"


@pytest.mark.anyio
async def test_aws_validate_endpoints(client, hdrs):
    # Test Access Keys validation
    res = await client.post("/api/v1/cloud/aws/validate", json={
        "auth_type": "ACCESS_KEYS",
        "aws_region": "us-east-1",
        "access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    }, headers=hdrs)
    assert res.status_code == 200
    val_ak = res.json()
    assert val_ak["valid"] is True
    assert val_ak["account_id"] is not None

    # Test IAM Role ARN validation
    res = await client.post("/api/v1/cloud/aws/validate", json={
        "auth_type": "IAM_ROLE_ARN",
        "aws_region": "us-west-2",
        "role_arn": "arn:aws:iam::123456789012:role/AetherDeploymentRole",
        "external_id": "aether-corp-ext-id"
    }, headers=hdrs)
    assert res.status_code == 200
    val_arn = res.json()
    assert val_arn["valid"] is True
    assert val_arn["account_id"] == "123456789012"


@pytest.mark.anyio
async def test_cloud_connection_crud(client, hdrs):
    create_payload = {
        "project_id": "proj-crud-001",
        "environment_id": "env-crud-001",
        "provider": "AWS",
        "auth_type": "ACCESS_KEYS",
        "aws_region": "eu-central-1",
        "access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    }
    res = await client.post("/api/v1/cloud/connections", json=create_payload, headers=hdrs)
    assert res.status_code == 201
    created = res.json()
    conn_id = created["id"]
    assert created["provider"] == "AWS"
    assert created["aws_region"] == "eu-central-1"
    assert created["status"] == "CONNECTED"

    # Get by ID
    res = await client.get(f"/api/v1/cloud/connections/{conn_id}", headers=hdrs)
    assert res.status_code == 200
    assert res.json()["id"] == conn_id

    # List by project
    res = await client.get("/api/v1/cloud/connections?project_id=proj-crud-001", headers=hdrs)
    assert res.status_code == 200
    listed = res.json()
    assert listed["total"] >= 1
    assert any(c["id"] == conn_id for c in listed["connections"])


@pytest.mark.anyio
async def test_aws_validate_iam_user_arn(client, hdrs):
    # Test real IAM User ARN
    res = await client.post("/api/v1/cloud/aws/validate", json={
        "auth_type": "IAM_ROLE_ARN",
        "aws_region": "ap-south-1",
        "role_arn": "arn:aws:iam::123456789012:user/prathap",
    }, headers=hdrs)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["account_id"] == "123456789012"
    assert data["resource_type"] == "user"
    assert data["user_name"] == "prathap"
    assert data["arn"] == "arn:aws:iam::123456789012:user/prathap"

    # Test nested path IAM User ARN
    res = await client.post("/api/v1/cloud/aws/validate", json={
        "auth_type": "IAM_ROLE_ARN",
        "aws_region": "us-east-1",
        "role_arn": "arn:aws:iam::987654321098:user/engineering/prathap.kumar",
    }, headers=hdrs)
    assert res.status_code == 200
    data2 = res.json()
    assert data2["valid"] is True
    assert data2["account_id"] == "987654321098"
    assert data2["resource_type"] == "user"
    assert data2["user_name"] == "prathap.kumar"

    # Test auto-detection when user puts ARN in access_key_id
    res = await client.post("/api/v1/cloud/aws/validate", json={
        "auth_type": "ACCESS_KEYS",
        "aws_region": "ap-south-1",
        "access_key_id": "arn:aws:iam::123456789012:user/prathap",
    }, headers=hdrs)
    assert res.status_code == 200
    data3 = res.json()
    assert data3["valid"] is True
    assert data3["account_id"] == "123456789012"
    assert data3["resource_type"] == "user"


@pytest.mark.anyio
async def test_unified_finalize_with_iam_user_arn(client, hdrs):
    payload = {
        "project_id": "proj-iam-user-001",
        "environment_id": "env-iam-user-001",
        "repo_url": "https://github.com/aetherops/aethershop",
        "branch": "main",
        "git_auth_type": "PAT",
        "github_user": "aether-dev",
        "pat_token": "ghp_mock_token_for_finalize_iam_user",
        "cloud_provider": "AWS",
        "cloud_auth_type": "IAM_ROLE_ARN",
        "aws_region": "ap-south-1",
        "role_arn": "arn:aws:iam::123456789012:user/prathap",
    }
    res = await client.post("/api/v1/connections/finalize", json=payload, headers=hdrs)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["status"] == "CONNECTED"
    assert data["cloud_connection"]["account_id"] == "123456789012"
    assert data["cloud_connection"]["role_arn"] == "arn:aws:iam::123456789012:user/prathap"
    assert data["cloud_connection"]["status"] == "CONNECTED"



