# services/project_and_environment_management/tests/test_tenant_rbac.py
"""
Focused tests for Phase 1 Checkpoint 2:
Multi-Tenant Identity, Personal Workspaces, RBAC, and Tenant Isolation.
"""
import uuid
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


RUN_ID = uuid.uuid4().hex[:6]


async def _register_and_login(client, username_prefix: str):
    uname = f"{username_prefix}_{RUN_ID}_{uuid.uuid4().hex[:4]}"
    email = f"{uname}@example.com"
    pwd = "StrongSecurePassword123!"

    reg_res = await client.post("/api/v1/auth/register", json={
        "username": uname,
        "email": email,
        "password": pwd,
    })
    assert reg_res.status_code == 200, reg_res.text
    token = reg_res.json()["token"]
    user_uuid = reg_res.json().get("uuid")
    headers = {"Authorization": f"Bearer {token}"}
    return {"username": uname, "email": email, "uuid": user_uuid, "token": token, "headers": headers}


@pytest.mark.anyio
async def test_user_registration_auto_provisions_personal_workspace(client):
    """Every newly registered user must automatically receive a personal workspace and TENANT_OWNER role."""
    user = await _register_and_login(client, "alice_personal")

    res = await client.get("/api/v1/tenants", headers=user["headers"])
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["total"] >= 1
    tenants = data["tenants"]

    personal = next((t for t in tenants if t["tenant_type"] == "PERSONAL"), None)
    assert personal is not None, "Personal workspace was not created"
    assert personal["role"] == "OWNER"
    assert "Workspace" in personal["name"]


@pytest.mark.anyio
async def test_organization_tenant_creation_and_membership(client):
    """Users can create organization workspaces and are assigned OWNER role."""
    user = await _register_and_login(client, "bob_org")

    create_res = await client.post("/api/v1/tenants", json={
        "name": f"Acme Corp {RUN_ID}",
    }, headers=user["headers"])
    assert create_res.status_code == 201, create_res.text
    tenant = create_res.json()
    assert tenant["tenant_type"] == "ORGANIZATION"
    assert tenant["role"] == "OWNER"

    list_res = await client.get("/api/v1/tenants", headers=user["headers"])
    assert list_res.status_code == 200
    tenant_ids = [t["id"] for t in list_res.json()["tenants"]]
    assert tenant["id"] in tenant_ids


@pytest.mark.anyio
async def test_tenant_member_invitation_and_role_management(client):
    """Owners can invite members and update their roles."""
    owner = await _register_and_login(client, "carol_owner")
    member = await _register_and_login(client, "dave_member")

    t_res = await client.post("/api/v1/tenants", json={"name": f"Team Carol {RUN_ID}"}, headers=owner["headers"])
    tenant_id = t_res.json()["id"]

    # 1. Invite Dave as MEMBER
    add_res = await client.post(
        f"/api/v1/tenants/{tenant_id}/members",
        json={"username": member["username"], "user_id": member["uuid"], "role": "MEMBER"},
        headers=owner["headers"],
    )
    assert add_res.status_code == 201, add_res.text
    membership = add_res.json()
    assert membership["role"] == "MEMBER"

    # 2. Duplicate invite rejected
    dup_res = await client.post(
        f"/api/v1/tenants/{tenant_id}/members",
        json={"user_id": member["uuid"], "role": "MEMBER"},
        headers=owner["headers"],
    )
    assert dup_res.status_code == 409

    # 3. List members
    list_res = await client.get(f"/api/v1/tenants/{tenant_id}/members", headers=owner["headers"])
    assert list_res.status_code == 200
    roles = {m["user_id"]: m["role"] for m in list_res.json()}
    assert roles.get(member["uuid"]) == "MEMBER"

    # 4. Promote Dave to ADMIN
    update_res = await client.patch(
        f"/api/v1/tenants/{tenant_id}/members/{member['uuid']}",
        json={"role": "ADMIN"},
        headers=owner["headers"],
    )
    assert update_res.status_code == 200
    assert update_res.json()["role"] == "ADMIN"


@pytest.mark.anyio
async def test_rbac_privilege_escalation_denied(client):
    """Admins cannot assign OWNER role, demote an OWNER, or delete the last OWNER."""
    owner = await _register_and_login(client, "eve_owner")
    admin_user = await _register_and_login(client, "frank_admin")
    regular_user = await _register_and_login(client, "grace_user")

    t_res = await client.post("/api/v1/tenants", json={"name": f"Security Org {RUN_ID}"}, headers=owner["headers"])
    tenant_id = t_res.json()["id"]

    # Add frank as ADMIN
    await client.post(
        f"/api/v1/tenants/{tenant_id}/members",
        json={"user_id": admin_user["uuid"], "role": "ADMIN"},
        headers=owner["headers"],
    )

    admin_headers = {**admin_user["headers"], "X-Tenant-ID": tenant_id}

    # 1. Admin attempts to assign OWNER role to Grace -> 403 Forbidden
    escalate_res = await client.post(
        f"/api/v1/tenants/{tenant_id}/members",
        json={"user_id": regular_user["uuid"], "role": "OWNER"},
        headers=admin_headers,
    )
    assert escalate_res.status_code == 403, escalate_res.text

    # 2. Admin attempts to demote Owner Eve -> 403 Forbidden
    demote_res = await client.patch(
        f"/api/v1/tenants/{tenant_id}/members/{owner['uuid']}",
        json={"role": "MEMBER"},
        headers=admin_headers,
    )
    assert demote_res.status_code == 403

    # 3. Owner attempts to demote self when sole owner -> 400 Bad Request
    owner_demote_self = await client.patch(
        f"/api/v1/tenants/{tenant_id}/members/{owner['uuid']}",
        json={"role": "MEMBER"},
        headers={**owner["headers"], "X-Tenant-ID": tenant_id},
    )
    assert owner_demote_self.status_code == 400


@pytest.mark.anyio
async def test_rbac_project_and_environment_permissions(client):
    """
    Role-based permissions on projects:
    - VIEWER: read only, create/update/delete denied.
    - MEMBER: create and update allowed, delete denied.
    - OWNER / ADMIN: full project management allowed.
    """
    owner = await _register_and_login(client, "heidi_owner")
    viewer = await _register_and_login(client, "ivan_viewer")
    member = await _register_and_login(client, "judy_member")

    t_res = await client.post("/api/v1/tenants", json={"name": f"Project Perms {RUN_ID}"}, headers=owner["headers"])
    tenant_id = t_res.json()["id"]

    # Invite viewer and member
    await client.post(
        f"/api/v1/tenants/{tenant_id}/members",
        json={"user_id": viewer["uuid"], "role": "VIEWER"},
        headers=owner["headers"],
    )
    await client.post(
        f"/api/v1/tenants/{tenant_id}/members",
        json={"user_id": member["uuid"], "role": "MEMBER"},
        headers=owner["headers"],
    )

    viewer_headers = {**viewer["headers"], "X-Tenant-ID": tenant_id}
    member_headers = {**member["headers"], "X-Tenant-ID": tenant_id}
    owner_headers = {**owner["headers"], "X-Tenant-ID": tenant_id}

    # 1. Viewer attempts to create project -> 403 Forbidden
    v_create = await client.post("/api/v1/projects", json={
        "name": "ViewerProj",
        "project_type": "web_application",
    }, headers=viewer_headers)
    assert v_create.status_code == 403

    # 2. Member creates project -> 201 Created
    m_create = await client.post("/api/v1/projects", json={
        "name": "MemberProj",
        "project_type": "web_application",
    }, headers=member_headers)
    assert m_create.status_code == 201
    proj_id = m_create.json()["id"]

    # 3. Viewer attempts to update project -> 403 Forbidden
    v_patch = await client.patch(f"/api/v1/projects/{proj_id}", json={
        "name": "HackedName",
    }, headers=viewer_headers)
    assert v_patch.status_code == 403

    # 4. Member attempts to delete project -> 403 Forbidden (requires OWNER or ADMIN)
    m_del = await client.delete(f"/api/v1/projects/{proj_id}", headers=member_headers)
    assert m_del.status_code == 403

    # 5. Owner deletes project -> 204 No Content
    o_del = await client.delete(f"/api/v1/projects/{proj_id}", headers=owner_headers)
    assert o_del.status_code == 204


@pytest.mark.anyio
async def test_cross_tenant_isolation_with_header(client):
    """
    Tenant isolation via X-Tenant-ID:
    - User in Tenant A creates Project Alpha.
    - User in Tenant B cannot see Project Alpha in list or detail.
    - Unaffiliated user specifying X-Tenant-ID of Tenant A is denied (403 Forbidden).
    """
    tenant_a_user = await _register_and_login(client, "org_a_user")
    tenant_b_user = await _register_and_login(client, "org_b_user")
    unaffiliated = await _register_and_login(client, "outsider")

    # Create Org A
    t_a = (await client.post("/api/v1/tenants", json={"name": f"Org Alpha {RUN_ID}"}, headers=tenant_a_user["headers"])).json()
    # Create Org B
    t_b = (await client.post("/api/v1/tenants", json={"name": f"Org Beta {RUN_ID}"}, headers=tenant_b_user["headers"])).json()

    headers_a = {**tenant_a_user["headers"], "X-Tenant-ID": t_a["id"]}
    headers_b = {**tenant_b_user["headers"], "X-Tenant-ID": t_b["id"]}

    # Create project in Org A
    proj_a = (await client.post("/api/v1/projects", json={
        "name": "AlphaExclusive",
        "project_type": "api_service",
    }, headers=headers_a)).json()

    # User in Org B lists projects -> must NOT contain AlphaExclusive
    b_list = await client.get("/api/v1/projects", headers=headers_b)
    assert b_list.status_code == 200
    b_ids = [p["id"] for p in b_list.json()["projects"]]
    assert proj_a["id"] not in b_ids

    # User in Org B tries to get Project Alpha directly -> 404 Not Found
    b_get = await client.get(f"/api/v1/projects/{proj_a['id']}", headers=headers_b)
    assert b_get.status_code == 404

    # Outsider attempts to spoof X-Tenant-ID of Org A -> 403 Forbidden
    outsider_headers = {**unaffiliated["headers"], "X-Tenant-ID": t_a["id"]}
    spoof_res = await client.get("/api/v1/projects", headers=outsider_headers)
    assert spoof_res.status_code == 403, "Outsider was not rejected for tenant A"


@pytest.mark.anyio
async def test_add_member_nonexistent_user_rejected_404(client):
    """Adding a member with nonexistent user_id or username must return 404 Not Found."""
    owner = await _register_and_login(client, "valid_owner")
    t_res = await client.post("/api/v1/tenants", json={"name": f"Validation Org {RUN_ID}"}, headers=owner["headers"])
    assert t_res.status_code == 201
    tenant_id = t_res.json()["id"]

    # 1. Nonexistent UUID
    fake_uuid = str(uuid.uuid4())
    res_fake = await client.post(
        f"/api/v1/tenants/{tenant_id}/members",
        json={"user_id": fake_uuid, "role": "MEMBER"},
        headers=owner["headers"],
    )
    assert res_fake.status_code == 404, res_fake.text
    assert "not found" in res_fake.json()["detail"].lower()

    # 2. Nonexistent username
    res_fake_uname = await client.post(
        f"/api/v1/tenants/{tenant_id}/members",
        json={"username": f"nonexistent_ghost_user_{RUN_ID}", "role": "MEMBER"},
        headers=owner["headers"],
    )
    assert res_fake_uname.status_code == 404
    assert "not found" in res_fake_uname.json()["detail"].lower()


@pytest.mark.anyio
async def test_username_change_preserves_project_ownership(client):
    """Updating a username in profile preserves historical project ownership and prevents collisions."""
    user1 = await _register_and_login(client, "user_renamer")
    user2 = await _register_and_login(client, "user_existing")

    # User 1 creates a project
    p_res = await client.post("/api/v1/projects", json={
        "name": f"RenameProj-{RUN_ID}",
        "project_type": "web_application",
    }, headers=user1["headers"])
    assert p_res.status_code == 201
    proj_id = p_res.json()["id"]
    assert p_res.json()["owner"] == user1["username"]

    # Attempt to change username to user2's username -> 409 Conflict
    conflict_res = await client.patch("/api/v1/auth/profile", json={
        "username": user2["username"],
    }, headers=user1["headers"])
    assert conflict_res.status_code == 409, conflict_res.text

    # Change username to valid new username
    new_uname = f"new_name_{RUN_ID}_{uuid.uuid4().hex[:4]}"
    update_res = await client.patch("/api/v1/auth/profile", json={
        "username": new_uname,
    }, headers=user1["headers"])
    assert update_res.status_code == 200, update_res.text
    assert update_res.json()["username"] == new_uname

    # Verify project owner is updated and still accessible by user
    proj_fetch = await client.get(f"/api/v1/projects/{proj_id}", headers=user1["headers"])
    assert proj_fetch.status_code == 200
    assert proj_fetch.json()["owner"] == new_uname


@pytest.mark.anyio
async def test_concurrent_personal_workspace_provisioning_idempotency(client):
    """Calling create_personal_workspace_for_user multiple times is safe and idempotent."""
    from app.tenant_context import create_personal_workspace_for_user
    from app.database import get_db

    async for db in get_db():
        test_uid = f"idemp_{RUN_ID}_{uuid.uuid4().hex[:4]}"
        test_uname = f"IdempUser_{RUN_ID}"

        tenant1 = await create_personal_workspace_for_user(db, test_uid, test_uname)
        tenant2 = await create_personal_workspace_for_user(db, test_uid, test_uname)

        assert tenant1.id == tenant2.id
        assert tenant1.slug == tenant2.slug
        break
