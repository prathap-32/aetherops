# services/project_and_environment_management/app/router.py
import os
import json
import uuid
import logging
import datetime
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import AetherProject, AetherEnvironment, Tenant, TenantMembership, AetherDashboardPreference
from app.schemas import (
    ProjectCreate, ProjectUpdate,
    EnvironmentCreate, EnvironmentUpdate, EnvironmentStatusUpdate,
    ProjectOut, ProjectListOut, EnvironmentOut,
    TenantCreate, TenantUpdate, TenantOut, TenantListOut,
    TenantMemberAdd, TenantMemberRoleUpdate, TenantMemberOut,
    EnvironmentCloneRequest, BatchEnvironmentCreate,
    ProjectSummaryOut, EnvironmentHealthOut, EnvironmentHealthCheckItem,
    AWS_REGIONS, VALID_ENV_STATUSES,
)
from app.tenant_context import (
    TenantContext, get_tenant_context, create_personal_workspace_for_user, slugify,
    TENANT_ROLES,
)
from app.auth import (
    get_current_admin, login_admin, register_user,
    SESSION_COOKIE_NAME, create_access_token, get_admin_db_session
)
from app.security_models import AdminUser
from app.cache import cache_manager

logger = logging.getLogger("project-manager-router")

router = APIRouter()

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/api/v1/auth/login")
async def api_login(payload: Dict[str, Any], request: Request, response: Response):
    """Authenticate via username or email and return JWT + set HttpOnly session cookie."""
    username = payload.get("username", "") or payload.get("email", "")
    password = payload.get("password", "")
    remember = bool(payload.get("remember_me", False))

    result = await login_admin(username, password, request)
    hours = 168 if remember else 8  # 7 days vs 8 hours

    token = create_access_token(
        result["username"],
        result["role"],
        result.get("email", username),
        hours=hours,
        user_uuid=result.get("uuid"),
    )
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=hours * 3600,
        path="/",
    )
    return {
        "token": token,
        "username": result["username"],
        "role": result["role"],
        "email": result.get("email", ""),
        "uuid": result.get("uuid"),
    }


@router.post("/api/v1/auth/register")
async def api_register(
    payload: Dict[str, Any],
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account with email and password, creating their personal workspace."""
    username = payload.get("username", "").strip()
    email = payload.get("email", "").strip().lower()
    password = payload.get("password", "")

    if not username or len(username) < 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username must be at least 3 characters.")
    if not email or "@" not in email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A valid email address is required.")
    if not password or len(password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 6 characters.")

    result = await register_user(username, email, password)
    token = result["token"]
    user_uuid = result.get("uuid", "")

    # Automatically provision personal workspace with TENANT_OWNER
    try:
        await create_personal_workspace_for_user(db, user_uuid, username)
    except Exception as exc:
        logger.warning(f"Could not provision personal workspace immediately during registration: {exc}")

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=8 * 3600,
        path="/",
    )
    return {
        "token": token,
        "username": result["username"],
        "role": result["role"],
        "email": result["email"],
        "uuid": user_uuid,
    }
@router.get("/auth/google/login")
@router.get("/api/v1/auth/google/login")
async def google_oauth_login(request: Request, redirect_uri: Optional[str] = None):
    """
    Initiates Google OAuth 2.0 flow.
    Prompts account selector ('select_account') so all browser accounts are displayed to choose from.
    """
    from aetherops_common.secrets import get_application_setting
    google_cid = get_application_setting("GOOGLE_CLIENT_ID")
    if not google_cid:
        raise HTTPException(status_code=400, detail="Google OAuth Client ID is not configured in AWS Secrets Manager or environment.")

    cb = redirect_uri or (lambda req: (lambda h=req.headers.get("x-forwarded-host") or req.headers.get("host"), p=req.headers.get("x-forwarded-proto") or ("https" if req.url.scheme=="https" or (h and "ts.net" in h) else "http"): f"{p}://{h}/api/v1/auth/google/callback" if h else f"{str(req.base_url).rstrip('/')}/api/v1/auth/google/callback"))(request)
    state = str(uuid.uuid4())
    scope = "openid email profile"
    
    # Prompt='select_account' forces Google to show all signed-in Google accounts
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={google_cid}"
        f"&redirect_uri={cb}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&prompt=select_account"
        f"&state={state}"
    )
    return RedirectResponse(google_auth_url)


@router.get("/auth/google/callback")
@router.get("/api/v1/auth/google/callback")
async def google_oauth_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
):
    """
    Handles Google OAuth redirect callback, exchanges authorization code for user token,
    and returns user information to parent window.
    """
    if error:
        return HTMLResponse(content=f"""<!DOCTYPE html>
<html><body style="font-family:sans-serif;text-align:center;padding:3rem;">
<h3 style="color:#dc2626;">Google Authorization Error</h3>
<p>{error}</p>
<script>if(window.opener) setTimeout(()=>window.close(), 2000);</script>
</body></html>""", status_code=400)

    if not code:
        return JSONResponse(status_code=400, content={"error": "Missing code parameter."})

    from aetherops_common.secrets import get_application_setting
    google_cid = get_application_setting("GOOGLE_CLIENT_ID")
    google_sec = get_application_setting("GOOGLE_CLIENT_SECRET")
    cb = os.getenv("GOOGLE_REDIRECT_URI", f"{str(request.base_url).rstrip('/')}/api/v1/auth/google/callback")

    user_info = {}
    try:
        import httpx
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": google_cid,
            "client_secret": google_sec,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": cb,
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            token_res = await client.post(token_url, data=payload)
            token_res.raise_for_status()
            token_data = token_res.json()
            access_token = token_data.get("access_token")

            # Fetch user info with access token
            user_res = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_res.raise_for_status()
            user_info = user_res.json()

        verified_email = user_info.get("email", "").strip().lower()
        raw_name = user_info.get("name") or verified_email.split("@")[0]
        verified_name = raw_name.strip()
        clean_username = verified_name.replace(" ", "_").lower()

        # Find or create user in DB
        user_data = None
        async for session in get_admin_db_session():
            res = await session.execute(
                select(AdminUser).where((AdminUser.email == verified_email) | (AdminUser.username == clean_username))
            )
            user = res.scalar_one_or_none()
            if not user:
                import secrets as _sec
                from app.auth import hash_password
                dummy_pw = _sec.token_urlsafe(24)
                user = AdminUser(
                    username=clean_username,
                    email=verified_email,
                    password_hash=hash_password(dummy_pw),
                    role="USER",
                    is_active=True,
                    created_at=datetime.datetime.utcnow(),
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)

            user.last_login_at = datetime.datetime.utcnow()
            await session.commit()
            user_data = {"username": user.username, "role": user.role, "email": user.email}

        u_name = user_data["username"]
        u_email = user_data["email"]
        u_role = user_data["role"]
        token = create_access_token(u_name, u_role, u_email, hours=24)

        import json as _json
        html_content = f"""<!DOCTYPE html>
<html>
<head><title>Google Verified — AetherOps</title></head>
<body style="font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;background:#0f172a;margin:0;color:white;">
  <div style="background:#1e293b;padding:2.5rem;border-radius:1rem;border:1px solid #334155;text-align:center;max-width:380px;">
    <div style="width:48px;height:48px;background:#2563eb;color:white;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 1rem auto;font-size:24px;">✓</div>
    <h3 style="margin:0 0 0.5rem 0;color:white;">Google Account Verified</h3>
    <p style="font-size:13px;color:#94a3b8;margin:0 0 1rem 0;">Signed in as <strong style="color:white;">{u_email}</strong></p>
    <div style="font-size:11px;color:#64748b;">Redirecting to Dashboard...</div>
  </div>
  <script>
    const payload = {{
      type: 'GOOGLE_OAUTH_SUCCESS',
      token: '{token}',
      user: {{
        username: '{u_name}',
        email: '{u_email}',
        role: '{u_role}'
      }}
    }};
    try {{
      localStorage.setItem('X-Admin-Key', '{token}');
      localStorage.setItem('aether_user', JSON.stringify(payload.user));
    }} catch(e) {{}}
    if(window.opener && !window.opener.closed) {
      window.opener.postMessage(payload, '*');
      setTimeout(() => window.close(), 600);
    } else {
      const targetHost = window.location.protocol + '//' + window.location.hostname + ':8000';
      window.location.href = targetHost + '/?token={token}&username={u_name}&email={u_email}&role={u_role}';
    }
  </script>
</body>
</html>"""
        resp = HTMLResponse(content=html_content, status_code=200)
        resp.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=token,
            httponly=True,
            samesite="lax",
            max_age=24 * 3600,
            path="/"
        )
        return resp

    except Exception as exc:
        logger.error(f"Google OAuth callback exchange failed: {exc}")
        return HTMLResponse(content=f"""<!DOCTYPE html>
<html><body style="font-family:sans-serif;text-align:center;padding:3rem;">
<h3 style="color:#dc2626;">Google Authentication Failed</h3>
<p style="color:#64748b;font-size:13px;">{str(exc)}</p>
<button onclick="window.close()" style="margin-top:1rem;padding:0.5rem 1rem;background:#1e40af;color:white;border:none;border-radius:6px;cursor:pointer;">Close Window</button>
</body></html>""", status_code=400)


@router.post("/api/v1/auth/oauth-callback")
async def api_oauth_callback(payload: Dict[str, Any], response: Response):
    """
    Handle Google OAuth or GitHub OAuth user profile callbacks,
    provisioning or logging in the user account safely.
    """
    provider = payload.get("provider", "github").lower()  # "google" or "github"
    email = (payload.get("email") or "").strip().lower()
    username = (payload.get("username") or payload.get("name") or "").strip()

    if not email and not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth profile must provide email or username.")

    if not username:
        username = email.split("@")[0]
    username = username.replace(" ", "_").lower()
    if not email:
        email = f"{username}@{provider}.oauth.local"

    # Find or create user in DB
    user_data = None
    async for session in get_admin_db_session():
        res = await session.execute(
            select(AdminUser).where((AdminUser.username == username) | (AdminUser.email == email))
        )
        user = res.scalar_one_or_none()
        if not user:
            import secrets as _sec
            from app.auth import hash_password
            dummy_pw = _sec.token_urlsafe(24)
            user = AdminUser(
                uuid=str(uuid.uuid4()),
                username=username,
                email=email,
                password_hash=hash_password(dummy_pw),
                role="USER",
                is_active=True,
                created_at=datetime.datetime.utcnow(),
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        elif not user.uuid:
            user.uuid = str(uuid.uuid4())
            await session.commit()

        user.last_login_at = datetime.datetime.utcnow()
        await session.commit()
        user_data = {"username": user.username, "role": user.role, "email": user.email, "uuid": user.uuid}

    token = create_access_token(user_data["username"], user_data["role"], user_data["email"], hours=24, user_uuid=user_data.get("uuid"))
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=24 * 3600,
        path="/",
    )
    return {"token": token, "username": user_data["username"], "role": user_data["role"], "email": user_data["email"], "uuid": user_data.get("uuid"), "provider": provider}


@router.get("/api/v1/auth/me")
async def api_get_me(admin: Dict[str, Any] = Depends(get_current_admin)):
    """Return currently authenticated profile from DB."""
    username = admin.get("username", "")
    async for session in get_admin_db_session():
        res = await session.execute(
            select(AdminUser).where((AdminUser.username == username) | (AdminUser.email == admin.get("email", "")))
        )
        user = res.scalar_one_or_none()
        if user:
            return {
                "id": user.id,
                "uuid": user.uuid,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }

    return {
        "id": 1,
        "uuid": admin.get("uuid"),
        "username": username or "admin",
        "email": admin.get("email", f"{username}@aetherops.cloud"),
        "role": admin.get("role", "ADMIN"),
        "is_active": True,
    }


@router.put("/api/v1/auth/profile")
@router.patch("/api/v1/auth/profile")
async def api_update_profile(
    payload: Dict[str, Any],
    response: Response,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """Update user username or display handle in DB and issue refreshed token."""
    old_username = admin.get("username", "")
    new_username = (payload.get("username") or "").strip()
    new_email = (payload.get("email") or "").strip().lower()

    if not new_username or len(new_username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")

    async for session in get_admin_db_session():
        # Check conflict
        conflict = await session.execute(
            select(AdminUser).where((AdminUser.username == new_username) & (AdminUser.username != old_username))
        )
        if conflict.scalar_one_or_none():
            raise HTTPException(status_code=409, detail=f"Username '{new_username}' is already taken.")

        res = await session.execute(
            select(AdminUser).where(AdminUser.username == old_username)
        )
        user = res.scalar_one_or_none()
        if not user:
            from app.auth import hash_password
            import secrets as _sec
            user_uuid = str(uuid.uuid4())
            user = AdminUser(
                uuid=user_uuid,
                username=new_username,
                email=new_email or f"{new_username}@aetherops.cloud",
                password_hash=hash_password(_sec.token_urlsafe(16)),
                role=admin.get("role", "USER"),
                is_active=True,
                created_at=datetime.datetime.utcnow(),
            )
            session.add(user)
        else:
            if not user.uuid:
                import uuid as _uuid
                user.uuid = str(_uuid.uuid5(_uuid.NAMESPACE_DNS, f"{user.username}.aetherops.local"))
            user.username = new_username
            if new_email and "@" in new_email:
                user.email = new_email

        await session.commit()
        await session.refresh(user)

        # Safely preserve historical project ownership by propagating the change to projects & memberships
        if new_username != old_username:
            from sqlalchemy import update
            await db.execute(
                update(AetherProject)
                .where(AetherProject.owner == old_username)
                .values(owner=new_username, created_by_user_id=user.uuid)
            )
            await db.execute(
                update(TenantMembership)
                .where(TenantMembership.user_id == old_username)
                .values(user_id=user.uuid)
            )
            await db.commit()

        token = create_access_token(user.username, user.role, user.email, hours=24, user_uuid=user.uuid)
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=token,
            httponly=True,
            samesite="lax",
            max_age=24 * 3600,
            path="/",
        )
        return {
            "message": "Profile updated successfully.",
            "token": token,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "uuid": user.uuid,
        }


@router.post("/api/v1/auth/logout")
async def api_logout(response: Response):
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"message": "Logged out successfully."}


# ═══════════════════════════════════════════════════════════════════════════════
# TENANT & RBAC ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/api/v1/tenants", response_model=TenantListOut)
async def list_user_tenants(
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """List all tenants accessible to the current user with their membership role."""
    user_name = admin.get("username", "")
    user_uuid = admin.get("uuid") or user_name
    is_platform_admin = admin.get("role") == "SUPER_ADMIN"

    mem_query = (
        select(TenantMembership, Tenant)
        .join(Tenant, Tenant.id == TenantMembership.tenant_id)
        .where(
            (TenantMembership.user_id == user_uuid) | (TenantMembership.user_id == user_name),
            TenantMembership.status == "ACTIVE",
            Tenant.status != "ARCHIVED",
        )
    )
    res = await db.execute(mem_query)
    rows = res.all()

    if not rows and not is_platform_admin:
        tenant = await create_personal_workspace_for_user(db, user_uuid, user_name)
        mem_res = await db.execute(
            select(TenantMembership).where(
                TenantMembership.tenant_id == tenant.id,
                TenantMembership.user_id == user_uuid,
            )
        )
        mem = mem_res.scalar_one_or_none()
        t_dict = tenant.to_dict()
        t_dict["role"] = mem.role if mem else "OWNER"
        return TenantListOut(tenants=[TenantOut(**t_dict)], total=1)

    out: List[TenantOut] = []
    seen_tenant_ids = set()
    for mem, tenant in rows:
        t_dict = tenant.to_dict()
        t_dict["role"] = mem.role
        out.append(TenantOut(**t_dict))
        seen_tenant_ids.add(tenant.id)

    if is_platform_admin and request.query_params.get("all") == "true":
        all_res = await db.execute(select(Tenant).where(Tenant.status != "ARCHIVED"))
        for t in all_res.scalars().all():
            if t.id not in seen_tenant_ids:
                t_dict = t.to_dict()
                t_dict["role"] = "SUPER_ADMIN"
                out.append(TenantOut(**t_dict))
                seen_tenant_ids.add(t.id)

    return TenantListOut(tenants=out, total=len(out))


@router.post("/api/v1/tenants", response_model=TenantOut, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    payload: TenantCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """Create a new organization workspace. The creator becomes TENANT_OWNER."""
    user_name = admin.get("username", "")
    user_uuid = admin.get("uuid") or user_name

    slug_base = slugify(payload.slug or payload.name)
    slug = f"{slug_base}-{uuid.uuid4().hex[:6]}"
    tenant_id = str(uuid.uuid4())

    tenant = Tenant(
        id=tenant_id,
        name=payload.name.strip(),
        slug=slug,
        tenant_type="ORGANIZATION",
        status="ACTIVE",
    )
    db.add(tenant)
    await db.flush()

    membership = TenantMembership(
        id=str(uuid.uuid4()),
        tenant_id=tenant.id,
        user_id=user_uuid,
        role="OWNER",
        status="ACTIVE",
    )
    db.add(membership)
    await db.commit()
    await db.refresh(tenant)

    t_dict = tenant.to_dict()
    t_dict["role"] = "OWNER"
    return TenantOut(**t_dict)


@router.get("/api/v1/tenants/current", response_model=TenantOut)
async def get_current_tenant(
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Return the currently resolved tenant context."""
    t_dict = ctx.tenant.to_dict()
    t_dict["role"] = ctx.role
    return TenantOut(**t_dict)


@router.get("/api/v1/tenants/{tenant_id}/members", response_model=List[TenantMemberOut])
async def list_tenant_members(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """List members of a tenant. User must be a member of this tenant."""
    if ctx.tenant.id != tenant_id and not ctx.is_platform_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to tenant members.")

    res = await db.execute(
        select(TenantMembership).where(TenantMembership.tenant_id == tenant_id)
    )
    members = res.scalars().all()
    return [TenantMemberOut(**m.to_dict()) for m in members]


@router.post(
    "/api/v1/tenants/{tenant_id}/members",
    response_model=TenantMemberOut,
    status_code=status.HTTP_201_CREATED,
)
async def add_tenant_member(
    tenant_id: str,
    payload: TenantMemberAdd,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Add a member to the tenant. Requires OWNER or ADMIN role. Prevents privilege escalation."""
    if ctx.tenant.id != tenant_id and not ctx.is_platform_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    ctx.require_role("OWNER", "ADMIN")

    target_role = payload.role.strip().upper()
    if ctx.role == "ADMIN" and target_role == "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privilege escalation denied: Tenant ADMIN cannot assign OWNER role.",
        )

    target_identifier = (payload.user_id or payload.username or "").strip()
    if not target_identifier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id or username required.")

    # Validate target user exists in AdminUser registry
    target_user = None
    async for s in get_admin_db_session():
        u_res = await s.execute(
            select(AdminUser).where(
                (AdminUser.uuid == target_identifier)
                | (AdminUser.username == target_identifier)
                | (AdminUser.email == target_identifier)
            )
        )
        target_user = u_res.scalar_one_or_none()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target user '{target_identifier}' not found.",
        )

    canonical_user_id = target_user.uuid or target_user.username

    existing_res = await db.execute(
        select(TenantMembership).where(
            TenantMembership.tenant_id == tenant_id,
            (TenantMembership.user_id == canonical_user_id)
            | (TenantMembership.user_id == target_user.username),
        )
    )
    if existing_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User '{target_identifier}' is already a member of this tenant.",
        )

    membership = TenantMembership(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        user_id=canonical_user_id,
        role=target_role,
        status="ACTIVE",
    )
    db.add(membership)
    await db.commit()
    await db.refresh(membership)
    return TenantMemberOut(**membership.to_dict())


@router.patch("/api/v1/tenants/{tenant_id}/members/{user_id}", response_model=TenantMemberOut)
async def update_tenant_member_role(
    tenant_id: str,
    user_id: str,
    payload: TenantMemberRoleUpdate,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Update tenant member role. Requires OWNER or ADMIN. Prevents privilege escalation."""
    if ctx.tenant.id != tenant_id and not ctx.is_platform_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    ctx.require_role("OWNER", "ADMIN")
    target_role = payload.role.strip().upper()

    res = await db.execute(
        select(TenantMembership).where(
            TenantMembership.tenant_id == tenant_id,
            TenantMembership.user_id == user_id,
        )
    )
    target_mem = res.scalar_one_or_none()
    if not target_mem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")

    if ctx.role == "ADMIN":
        if target_mem.role in ("OWNER", "ADMIN"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ADMIN cannot modify OWNER or fellow ADMIN.")
        if target_role in ("OWNER", "ADMIN"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Privilege escalation denied: ADMIN cannot promote to OWNER or ADMIN.")

    if target_mem.role == "OWNER" and target_role != "OWNER":
        owners_res = await db.execute(
            select(TenantMembership).where(
                TenantMembership.tenant_id == tenant_id,
                TenantMembership.role == "OWNER",
                TenantMembership.status == "ACTIVE",
            )
        )
        if len(owners_res.scalars().all()) <= 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot demote the only remaining OWNER of the workspace.")

    target_mem.role = target_role
    target_mem.updated_at = datetime.datetime.utcnow()
    await db.commit()
    await db.refresh(target_mem)
    return TenantMemberOut(**target_mem.to_dict())


@router.delete("/api/v1/tenants/{tenant_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tenant_member(
    tenant_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Remove member from tenant. Requires OWNER or ADMIN."""
    if ctx.tenant.id != tenant_id and not ctx.is_platform_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    ctx.require_role("OWNER", "ADMIN")

    res = await db.execute(
        select(TenantMembership).where(
            TenantMembership.tenant_id == tenant_id,
            TenantMembership.user_id == user_id,
        )
    )
    target_mem = res.scalar_one_or_none()
    if not target_mem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found.")

    if ctx.role == "ADMIN" and target_mem.role in ("OWNER", "ADMIN"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ADMIN cannot remove OWNER or fellow ADMIN.")

    if target_mem.role == "OWNER":
        owners_res = await db.execute(
            select(TenantMembership).where(
                TenantMembership.tenant_id == tenant_id,
                TenantMembership.role == "OWNER",
                TenantMembership.status == "ACTIVE",
            )
        )
        if len(owners_res.scalars().all()) <= 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the only remaining OWNER of the workspace.")

    await db.delete(target_mem)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ═══════════════════════════════════════════════════════════════════════════════
# METADATA ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/api/v1/meta/regions")
async def get_supported_aws_regions():
    from app.schemas import AWS_REGIONS
    return {"regions": sorted(list(AWS_REGIONS)), "total": len(AWS_REGIONS)}

@router.get("/api/v1/meta/project-types")
async def get_supported_project_types():
    from app.schemas import PROJECT_TYPES
    return {"project_types": sorted(list(PROJECT_TYPES)), "total": len(PROJECT_TYPES)}

@router.get("/api/v1/meta/env-types")
async def get_supported_env_types():
    from app.schemas import ENV_TYPES
    return {"env_types": sorted(list(ENV_TYPES)), "total": len(ENV_TYPES)}


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/api/v1/projects", response_model=ProjectListOut)
async def list_projects(
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Return projects accessible within the current user's isolated tenant context."""
    owner = ctx.user["username"]
    user_uuid = ctx.user.get("uuid")
    cache_key = f"{ctx.tenant.id}:{owner}"

    cached = await cache_manager.get_projects_list(cache_key)
    if cached:
        return ProjectListOut(projects=cached, total=len(cached))

    has_explicit_tenant = bool(request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id"))
    show_all = request.query_params.get("all") == "true" and ctx.is_platform_admin

    if show_all and not has_explicit_tenant:
        query = select(AetherProject).order_by(AetherProject.created_at.desc())
    else:
        # Strict user-tenant isolation: only show projects belonging to this user's tenant or owned by this user
        query = select(AetherProject).where(
            (AetherProject.tenant_id == ctx.tenant.id)
            | ((AetherProject.tenant_id.is_(None)) & (AetherProject.owner == owner))
            | (AetherProject.owner == owner)
            | ((AetherProject.created_by_user_id.is_not(None)) & (AetherProject.created_by_user_id == user_uuid))
        ).order_by(AetherProject.created_at.desc())

    res = await db.execute(query)
    projects = res.scalars().all()

    out = [ProjectOut(**p.to_dict()) for p in projects]
    await cache_manager.set_projects_list(cache_key, [o.model_dump() for o in out])

    return ProjectListOut(projects=out, total=len(out))


@router.post("/api/v1/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Create a new project scoped to the current tenant boundary."""
    ctx.require_role("OWNER", "ADMIN", "MEMBER")
    owner = ctx.user["username"]
    user_uuid = ctx.user.get("uuid")
    acc_id = (
        payload.account_id
        or ctx.user.get("account_id")
        or request.headers.get("x-account-id")
        or request.headers.get("X-Account-ID")
        or "109283746519"
    )

    project = AetherProject(
        id=str(uuid.uuid4()),
        name=payload.name,
        description=payload.description,
        project_type=payload.project_type,
        owner=owner,
        tenant_id=ctx.tenant.id,
        created_by_user_id=user_uuid,
        account_id=acc_id,
        status="CREATED",
        environment_count=0,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    db.add(project)

    PRESETS = {
        "standard": [
            {"name": "Development", "env_type": "development", "aws_region": "us-east-1", "description": "Development sandbox for rapid iteration"},
            {"name": "Staging", "env_type": "staging", "aws_region": "us-east-1", "description": "Pre-production validation and integration cluster"},
            {"name": "Production", "env_type": "production", "aws_region": "us-east-1", "description": "High-availability live customer workload"},
        ],
        "minimal": [
            {"name": "Development", "env_type": "development", "aws_region": "us-east-1", "description": "Default primary development environment"},
        ],
        "multi_region": [
            {"name": "Development-US", "env_type": "development", "aws_region": "us-east-1", "description": "Dev environment in US East (N. Virginia)"},
            {"name": "Staging-EU", "env_type": "staging", "aws_region": "eu-west-1", "description": "Staging tier in Europe (Ireland)"},
            {"name": "Production-Global", "env_type": "production", "aws_region": "us-west-2", "description": "Production tier in US West (Oregon)"},
        ],
    }

    preset_name = payload.environments_preset or ("standard" if payload.auto_provision_environments else None)
    created_envs = []
    if preset_name and preset_name in PRESETS:
        for spec in PRESETS[preset_name]:
            env = AetherEnvironment(
                id=str(uuid.uuid4()),
                project_id=project.id,
                tenant_id=ctx.tenant.id,
                created_by_user_id=user_uuid,
                account_id=acc_id,
                name=spec["name"],
                env_type=spec["env_type"],
                aws_region=spec["aws_region"],
                description=spec["description"],
                status="CREATED",
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
            )
            db.add(env)
            created_envs.append(env)
        project.environment_count = len(created_envs)

    await db.commit()
    await db.refresh(project)

    await cache_manager.invalidate_projects_list(f"{ctx.tenant.id}:{owner}")
    await cache_manager.invalidate_projects_list(owner)
    logger.info(f"Created project '{project.name}' (id={project.id}) for owner='{owner}', tenant='{ctx.tenant.id}' with {len(created_envs)} envs")

    return ProjectOut(**project.to_dict(environments=created_envs))


@router.get("/api/v1/projects/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Return project + all its environments. Authorizes tenant ownership BEFORE returning cache."""
    project = await _get_project_or_404(db, project_id, ctx)

    cached = await cache_manager.get_project_detail(project_id)
    if cached:
        return ProjectOut(**cached)

    env_res = await db.execute(
        select(AetherEnvironment)
        .where(AetherEnvironment.project_id == project_id)
        .order_by(AetherEnvironment.created_at.asc())
    )
    environments = env_res.scalars().all()

    out = ProjectOut(**project.to_dict(environments=environments))
    await cache_manager.set_project_detail(project_id, out.model_dump())

    return out


@router.patch("/api/v1/projects/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Update project name, description, or status. Requires MEMBER, ADMIN, or OWNER."""
    ctx.require_role("OWNER", "ADMIN", "MEMBER")
    project = await _get_project_or_404(db, project_id, ctx)

    if payload.name is not None:
        project.name = payload.name.strip()
    if payload.description is not None:
        project.description = payload.description
    if payload.status is not None:
        project.status = payload.status.upper()

    project.updated_at = datetime.datetime.utcnow()
    await db.commit()
    await db.refresh(project)

    owner = ctx.user["username"]
    await cache_manager.invalidate_all_for_owner(owner, project_id)
    await cache_manager.invalidate_projects_list(f"{ctx.tenant.id}:{owner}")
    return ProjectOut(**project.to_dict())


@router.delete("/api/v1/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Delete project and all its environments. Denied for VIEWER and regular MEMBER."""
    ctx.require_role("OWNER", "ADMIN")
    project = await _get_project_or_404(db, project_id, ctx)

    env_res = await db.execute(
        select(AetherEnvironment).where(AetherEnvironment.project_id == project_id)
    )
    for env in env_res.scalars().all():
        await db.delete(env)

    await db.delete(project)
    await db.commit()

    owner = ctx.user["username"]
    await cache_manager.invalidate_all_for_owner(owner, project_id)
    await cache_manager.invalidate_projects_list(f"{ctx.tenant.id}:{owner}")
    logger.info(f"Deleted project '{project_id}' for owner='{owner}', tenant='{ctx.tenant.id}'")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/api/v1/projects/{project_id}/summary", response_model=ProjectSummaryOut)
async def get_project_summary(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Provide operational telemetry, region footprint, and health metrics for a project."""
    project = await _get_project_or_404(db, project_id, ctx)
    env_res = await db.execute(
        select(AetherEnvironment)
        .where(AetherEnvironment.project_id == project_id)
        .order_by(AetherEnvironment.created_at.asc())
    )
    envs = env_res.scalars().all()

    status_counts: Dict[str, int] = {}
    type_counts: Dict[str, int] = {}
    regions = set()
    active_count = 0
    for e in envs:
        status_counts[e.status] = status_counts.get(e.status, 0) + 1
        type_counts[e.env_type] = type_counts.get(e.env_type, 0) + 1
        if e.aws_region:
            regions.add(e.aws_region)
        if e.status in ("ACTIVE", "CONFIGURED", "READY_TO_DEPLOY"):
            active_count += 1

    total_env = len(envs)
    failed_count = status_counts.get("FAILED", 0)
    health_score = 100.0 if total_env > 0 and failed_count == 0 else (
        max(0.0, 100.0 - (failed_count / max(total_env, 1) * 100.0))
    )

    lifecycle = "ACTIVE" if active_count > 0 else ("INITIALIZING" if total_env > 0 else "EMPTY")

    return ProjectSummaryOut(
        project_id=project.id,
        name=project.name,
        owner=project.owner,
        tenant_id=project.tenant_id,
        account_id=project.account_id or ctx.user.get("account_id"),
        project_type=project.project_type,
        status=project.status,
        environment_count=total_env,
        active_environments_count=active_count,
        status_breakdown=status_counts,
        type_breakdown=type_counts,
        regions=sorted(list(regions)),
        health_score=round(health_score, 1),
        deployment_ready=total_env > 0,
        lifecycle_phase=lifecycle,
        created_at=project.created_at.isoformat() if project.created_at else None,
        updated_at=project.updated_at.isoformat() if project.updated_at else None,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/api/v1/projects/{project_id}/environments")
async def list_environments(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    await _get_project_or_404(db, project_id, ctx)

    res = await db.execute(
        select(AetherEnvironment)
        .where(AetherEnvironment.project_id == project_id)
        .order_by(AetherEnvironment.created_at.asc())
    )
    envs = res.scalars().all()
    return {"environments": [e.to_dict() for e in envs], "total": len(envs)}


@router.post(
    "/api/v1/projects/{project_id}/environments",
    response_model=EnvironmentOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_environment(
    project_id: str,
    payload: EnvironmentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Create a new environment under a project. Scoped to tenant."""
    ctx.require_role("OWNER", "ADMIN", "MEMBER")
    project = await _get_project_or_404(db, project_id, ctx)

    dup = await db.execute(
        select(AetherEnvironment).where(
            AetherEnvironment.project_id == project_id,
            AetherEnvironment.name == payload.name,
        )
    )
    if dup.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Environment '{payload.name}' already exists in this project.",
        )

    env_acc_id = (
        payload.account_id
        or project.account_id
        or ctx.user.get("account_id")
        or request.headers.get("x-account-id")
        or "109283746519"
    )

    env = AetherEnvironment(
        id=str(uuid.uuid4()),
        project_id=project_id,
        tenant_id=ctx.tenant.id,
        created_by_user_id=ctx.user.get("uuid"),
        account_id=env_acc_id,
        name=payload.name,
        env_type=payload.env_type,
        aws_region=payload.aws_region,
        description=payload.description,
        status="CREATED",
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    db.add(env)

    project.environment_count = (project.environment_count or 0) + 1
    project.updated_at = datetime.datetime.utcnow()

    await db.commit()
    await db.refresh(env)

    owner = ctx.user["username"]
    await cache_manager.invalidate_all_for_owner(owner, project_id)
    await cache_manager.invalidate_projects_list(f"{ctx.tenant.id}:{owner}")
    logger.info(f"Created environment '{env.name}' (id={env.id}) in project '{project_id}', tenant='{ctx.tenant.id}'")

    return EnvironmentOut(**env.to_dict())


@router.post(
    "/api/v1/projects/{project_id}/environments/batch",
    status_code=status.HTTP_201_CREATED,
)
async def batch_create_environments(
    project_id: str,
    payload: BatchEnvironmentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Atomic batch provisioning of multiple fleet environments under a project."""
    ctx.require_role("OWNER", "ADMIN", "MEMBER")
    project = await _get_project_or_404(db, project_id, ctx)
    if not payload.environments:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No environments provided in batch payload.")

    created_list = []
    for item in payload.environments:
        dup = await db.execute(
            select(AetherEnvironment).where(
                AetherEnvironment.project_id == project_id,
                AetherEnvironment.name == item.name,
            )
        )
        if dup.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Environment '{item.name}' already exists in this project.",
            )
        env = AetherEnvironment(
            id=str(uuid.uuid4()),
            project_id=project_id,
            tenant_id=ctx.tenant.id,
            created_by_user_id=ctx.user.get("uuid"),
            account_id=item.account_id or project.account_id or ctx.user.get("account_id") or "109283746519",
            name=item.name,
            env_type=item.env_type or "development",
            aws_region=item.aws_region or "us-east-1",
            description=item.description,
            status="CREATED",
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        db.add(env)
        created_list.append(env)

    project.environment_count = (project.environment_count or 0) + len(created_list)
    project.updated_at = datetime.datetime.utcnow()
    await db.commit()

    owner = ctx.user["username"]
    await cache_manager.invalidate_all_for_owner(owner, project_id)
    await cache_manager.invalidate_projects_list(f"{ctx.tenant.id}:{owner}")
    logger.info(f"Batch provisioned {len(created_list)} environments for project '{project_id}'")

    return {"environments": [e.to_dict() for e in created_list], "total": len(created_list)}


@router.get("/api/v1/environments")
async def list_all_environments(
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """List all environments belonging to projects accessible by this tenant."""
    projects_out = await list_projects(request=request, db=db, ctx=ctx)
    project_ids = [p.id for p in projects_out.projects]
    if not project_ids:
        return {"environments": [], "total": 0}

    res = await db.execute(
        select(AetherEnvironment)
        .where(AetherEnvironment.project_id.in_(project_ids))
        .order_by(AetherEnvironment.created_at.desc())
    )
    envs = res.scalars().all()
    return {"environments": [e.to_dict() for e in envs], "total": len(envs)}


@router.post(
    "/api/v1/environments",
    response_model=EnvironmentOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_environment_root(
    payload: EnvironmentCreate,
    request: Request,
    project_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Create an environment specifying the target project in the body or query."""
    target_pid = project_id or payload.project_id or payload.target_project
    if not target_pid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target project_id is required in query param or body to create an environment.",
        )
    return await create_environment(
        project_id=target_pid,
        payload=payload,
        request=request,
        db=db,
        ctx=ctx,
    )


@router.get("/api/v1/projects/{project_id}/environments/{env_id}", response_model=EnvironmentOut)
async def get_environment(
    project_id: str,
    env_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    await _get_project_or_404(db, project_id, ctx)
    env = await _get_env_or_404(db, env_id, project_id)
    return EnvironmentOut(**env.to_dict())


@router.patch("/api/v1/projects/{project_id}/environments/{env_id}", response_model=EnvironmentOut)
async def update_environment(
    project_id: str,
    env_id: str,
    payload: EnvironmentUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Update environment name or description. Requires MEMBER, ADMIN, or OWNER."""
    ctx.require_role("OWNER", "ADMIN", "MEMBER")
    await _get_project_or_404(db, project_id, ctx)
    env = await _get_env_or_404(db, env_id, project_id)

    if payload.name is not None:
        env.name = payload.name.strip()
    if payload.description is not None:
        env.description = payload.description

    env.updated_at = datetime.datetime.utcnow()
    await db.commit()
    await db.refresh(env)

    owner = ctx.user["username"]
    await cache_manager.invalidate_all_for_owner(owner, project_id)
    await cache_manager.invalidate_projects_list(f"{ctx.tenant.id}:{owner}")
    return EnvironmentOut(**env.to_dict())


@router.patch(
    "/api/v1/projects/{project_id}/environments/{env_id}/status",
    response_model=EnvironmentOut,
)
async def update_environment_status(
    project_id: str,
    env_id: str,
    payload: EnvironmentStatusUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """
    Advance the environment lifecycle state.
    Requires active membership role MEMBER, ADMIN, or OWNER.
    """
    ctx.require_role("OWNER", "ADMIN", "MEMBER")
    await _get_project_or_404(db, project_id, ctx)
    env = await _get_env_or_404(db, env_id, project_id)

    old_status = env.status
    env.status = payload.status
    env.updated_at = datetime.datetime.utcnow()
    await db.commit()
    await db.refresh(env)

    owner = ctx.user["username"]
    await cache_manager.invalidate_all_for_owner(owner, project_id)
    await cache_manager.invalidate_projects_list(f"{ctx.tenant.id}:{owner}")
    logger.info(f"Environment '{env.id}' status: {old_status} → {env.status}")
    return EnvironmentOut(**env.to_dict())


@router.delete(
    "/api/v1/projects/{project_id}/environments/{env_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_environment(
    project_id: str,
    env_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Delete environment. Denied for MEMBER and VIEWER."""
    ctx.require_role("OWNER", "ADMIN")
    project = await _get_project_or_404(db, project_id, ctx)
    env = await _get_env_or_404(db, env_id, project_id)

    await db.delete(env)
    project.environment_count = max(0, (project.environment_count or 1) - 1)
    project.updated_at = datetime.datetime.utcnow()
    await db.commit()

    owner = ctx.user["username"]
    await cache_manager.invalidate_all_for_owner(owner, project_id)
    await cache_manager.invalidate_projects_list(f"{ctx.tenant.id}:{owner}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/api/v1/projects/{project_id}/environments/{env_id}/clone",
    response_model=EnvironmentOut,
    status_code=status.HTTP_201_CREATED,
)
async def clone_environment(
    project_id: str,
    env_id: str,
    payload: EnvironmentCloneRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Clone an existing environment tier into a new environment under the project."""
    ctx.require_role("OWNER", "ADMIN", "MEMBER")
    project = await _get_project_or_404(db, project_id, ctx)
    source_env = await _get_env_or_404(db, env_id, project_id)

    dup = await db.execute(
        select(AetherEnvironment).where(
            AetherEnvironment.project_id == project_id,
            AetherEnvironment.name == payload.new_name,
        )
    )
    if dup.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Environment '{payload.new_name}' already exists in this project.",
        )

    cloned = AetherEnvironment(
        id=str(uuid.uuid4()),
        project_id=project_id,
        tenant_id=ctx.tenant.id,
        created_by_user_id=ctx.user.get("uuid"),
        account_id=source_env.account_id or project.account_id or ctx.user.get("account_id") or "109283746519",
        name=payload.new_name,
        env_type=payload.env_type or source_env.env_type,
        aws_region=payload.aws_region or source_env.aws_region,
        description=payload.description or f"Cloned from {source_env.name}",
        status="CREATED",
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    db.add(cloned)
    project.environment_count = (project.environment_count or 0) + 1
    project.updated_at = datetime.datetime.utcnow()

    await db.commit()
    await db.refresh(cloned)

    owner = ctx.user["username"]
    await cache_manager.invalidate_all_for_owner(owner, project_id)
    await cache_manager.invalidate_projects_list(f"{ctx.tenant.id}:{owner}")
    logger.info(f"Cloned environment '{source_env.id}' into '{cloned.id}' ({cloned.name})")

    return EnvironmentOut(**cloned.to_dict())


@router.get(
    "/api/v1/projects/{project_id}/environments/{env_id}/health",
    response_model=EnvironmentHealthOut,
)
async def get_environment_health(
    project_id: str,
    env_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Evaluate deep configuration health, region support, and lifecycle status of an environment."""
    project = await _get_project_or_404(db, project_id, ctx)
    env = await _get_env_or_404(db, env_id, project_id)

    region_valid = env.aws_region in AWS_REGIONS
    checks = [
        EnvironmentHealthCheckItem(
            check="aws_region_validity",
            passed=region_valid,
            detail=f"AWS region '{env.aws_region}' is supported." if region_valid else f"AWS region '{env.aws_region}' unrecognized.",
        ),
        EnvironmentHealthCheckItem(
            check="project_binding",
            passed=True,
            detail=f"Bound to parent workspace '{project.name}' ({project.id}).",
        ),
        EnvironmentHealthCheckItem(
            check="tenant_isolation",
            passed=bool(env.tenant_id == ctx.tenant.id),
            detail=f"Isolated to tenant '{ctx.tenant.name}'.",
        ),
        EnvironmentHealthCheckItem(
            check="lifecycle_integrity",
            passed=env.status in VALID_ENV_STATUSES,
            detail=f"Current lifecycle status is {env.status}.",
        ),
    ]

    all_passed = all(c.passed for c in checks)
    health_status = "HEALTHY" if (all_passed and env.status != "FAILED") else ("FAILED" if env.status == "FAILED" else "DEGRADED")
    phase = "READY" if env.status in ("ACTIVE", "CONFIGURED", "READY_TO_DEPLOY") else ("FAILED" if env.status == "FAILED" else "INITIALIZING")

    return EnvironmentHealthOut(
        env_id=env.id,
        project_id=project.id,
        name=env.name,
        account_id=env.account_id or project.account_id or ctx.user.get("account_id"),
        status=env.status,
        env_type=env.env_type,
        aws_region=env.aws_region,
        region_supported=region_valid,
        health_status=health_status,
        lifecycle_phase=phase,
        checks=checks,
        checked_at=datetime.datetime.utcnow().isoformat(),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

async def _get_project_or_404(
    db: AsyncSession,
    project_id: str,
    ctx_or_owner: Any,
    role: Optional[str] = None,
) -> AetherProject:
    """
    Fetch project ensuring isolation. Supports both TenantContext and legacy (owner, role) signatures.
    """
    if isinstance(ctx_or_owner, TenantContext):
        ctx = ctx_or_owner
        owner = ctx.user["username"]
        user_uuid = ctx.user.get("uuid")
        query = select(AetherProject).where(
            AetherProject.id == project_id,
            (
                (AetherProject.tenant_id == ctx.tenant.id)
                | (AetherProject.owner == owner)
                | ((AetherProject.created_by_user_id.is_not(None)) & (AetherProject.created_by_user_id == user_uuid))
                | ((AetherProject.tenant_id.is_(None)) & (AetherProject.owner == owner))
            )
        )
    else:
        owner = str(ctx_or_owner)
        user_role = role or "USER"
        if user_role == "SUPER_ADMIN":
            query = select(AetherProject).where(AetherProject.id == project_id)
        else:
            query = select(AetherProject).where(
                AetherProject.id == project_id,
                AetherProject.owner == owner,
            )

    res = await db.execute(query)
    project = res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
    return project


async def _get_env_or_404(db: AsyncSession, env_id: str, project_id: str) -> AetherEnvironment:
    res = await db.execute(
        select(AetherEnvironment).where(
            AetherEnvironment.id == env_id,
            AetherEnvironment.project_id == project_id,
        )
    )
    env = res.scalar_one_or_none()
    if not env:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Environment '{env_id}' not found.")
    return env


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD AGGREGATION & ADAPTIVE PREFERENCES ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_DASHBOARD_PREFERENCES = {
    "widget_order": [
        "getting_started",
        "recommendations",
        "attention_required",
        "overview_metrics",
        "recent_projects",
        "environments_summary",
        "deployments_overview",
        "system_health",
        "recent_activity",
    ],
    "widget_visibility": {
        "getting_started": True,
        "recommendations": True,
        "attention_required": True,
        "overview_metrics": True,
        "recent_projects": True,
        "environments_summary": True,
        "deployments_overview": True,
        "system_health": True,
        "recent_activity": True,
    },
    "widget_sizes": {
        "getting_started": "full",
        "recommendations": "full",
        "attention_required": "full",
        "overview_metrics": "full",
        "recent_projects": "full",
        "environments_summary": "half",
        "deployments_overview": "half",
        "system_health": "half",
        "recent_activity": "half",
    },
    "pinned_widgets": [],
}


@router.get("/api/v1/dashboard")
async def get_dashboard_summary(
    request: Request,
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """
    Adaptive Dashboard Aggregator:
    Computes user lifecycle stage, widget eligibility, project metrics,
    and next recommended actions based on deterministic business rules.
    """
    owner = ctx.user["username"]
    user_uuid = ctx.user.get("uuid")

    # 1. Fetch user projects
    proj_query = select(AetherProject).where(
        (AetherProject.tenant_id == ctx.tenant.id)
        | ((AetherProject.tenant_id.is_(None)) & (AetherProject.owner == owner))
        | (AetherProject.owner == owner)
        | ((AetherProject.created_by_user_id.is_not(None)) & (AetherProject.created_by_user_id == user_uuid))
    ).order_by(AetherProject.created_at.desc())

    proj_res = await db.execute(proj_query)
    projects = proj_res.scalars().all()
    total_projects = len(projects)

    project_ids = [p.id for p in projects]

    # 2. Fetch environments for user's projects
    environments = []
    if project_ids:
        env_query = select(AetherEnvironment).where(
            AetherEnvironment.project_id.in_(project_ids)
        ).order_by(AetherEnvironment.created_at.desc())
        env_res = await db.execute(env_query)
        environments = env_res.scalars().all()

    total_environments = len(environments)

    # 3. Categorization summaries
    projects_by_type: Dict[str, int] = {}
    projects_by_status: Dict[str, int] = {}
    for p in projects:
        pt = p.project_type or "web_application"
        projects_by_type[pt] = projects_by_type.get(pt, 0) + 1
        st = p.status or "CREATED"
        projects_by_status[st] = projects_by_status.get(st, 0) + 1

    environments_by_region: Dict[str, int] = {}
    environments_by_type: Dict[str, int] = {}
    for e in environments:
        reg = e.aws_region or "us-east-1"
        environments_by_region[reg] = environments_by_region.get(reg, 0) + 1
        et = e.env_type or "development"
        environments_by_type[et] = environments_by_type.get(et, 0) + 1

    # 4. Determine lifecycle stage (Deterministic Rule Engine)
    if total_projects == 0:
        lifecycle_stage = "stage_1_onboarding"
    elif total_environments == 0:
        lifecycle_stage = "stage_2_project_created"
    elif total_environments <= 2:
        lifecycle_stage = "stage_3_infrastructure_workflow"
    else:
        lifecycle_stage = "stage_4_active_operations"

    # 5. Widget eligibility based on lifecycle & data state
    widget_eligibility = {
        "getting_started": total_projects == 0,
        "overview_metrics": total_projects > 0,
        "recent_projects": total_projects > 0,
        "environments_summary": total_environments > 0,
        "deployments_overview": True,
        "attention_required": True,
        "system_health": True,
        "recent_activity": True,
        "recommendations": True,
    }

    # 6. Intelligent deterministic recommendation
    if lifecycle_stage == "stage_1_onboarding":
        recommended_action = {
            "id": "create_first_project",
            "title": "Create Your First Project Workspace",
            "description": "Provision an isolated project workspace to begin designing architectures and automating cloud infrastructure.",
            "action_label": "Create Project",
            "route": "/projects",
            "action_type": "modal",
        }
    elif lifecycle_stage == "stage_2_project_created":
        recommended_action = {
            "id": "connect_sources",
            "title": "Link Cloud Credentials & Git Repository",
            "description": "Connect your AWS deployment credentials and repository to enable automated AST codebase analysis.",
            "action_label": "Connect Cloud & Git",
            "route": "/source-connection",
            "action_type": "navigate",
        }
    elif lifecycle_stage == "stage_3_infrastructure_workflow":
        recommended_action = {
            "id": "analyze_codebase",
            "title": "Run Source Code & Architecture Sizing",
            "description": "Inspect repository frameworks, services, and sizing parameters to generate production AWS architecture.",
            "action_label": "Analyze Codebase",
            "route": "/source-analysis",
            "action_type": "navigate",
        }
    else:
        recommended_action = {
            "id": "review_fleet",
            "title": "Review Target Environments & Deployments",
            "description": "Monitor active cloud infrastructure workloads, approval gates, and drift across fleet environments.",
            "action_label": "Inspect Deployments",
            "route": "/deployment",
            "action_type": "navigate",
        }

    # 7. Recent projects projection (top 6)
    recent_projects_out = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "project_type": p.project_type,
            "status": p.status,
            "environment_count": p.environment_count,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }
        for p in projects[:6]
    ]

    # 8. Recent environments projection (top 6)
    recent_environments_out = [
        {
            "id": e.id,
            "project_id": e.project_id,
            "name": e.name,
            "env_type": e.env_type,
            "aws_region": e.aws_region,
            "status": e.status,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in environments[:6]
    ]

    return {
        "lifecycle_stage": lifecycle_stage,
        "summary": {
            "total_projects": total_projects,
            "total_environments": total_environments,
            "projects_by_type": projects_by_type,
            "projects_by_status": projects_by_status,
            "environments_by_region": environments_by_region,
            "environments_by_type": environments_by_type,
        },
        "recent_projects": recent_projects_out,
        "recent_environments": recent_environments_out,
        "widget_eligibility": widget_eligibility,
        "recommended_action": recommended_action,
        "user": {
            "username": owner,
            "tenant_id": ctx.tenant.id,
            "tenant_name": ctx.tenant.name,
        },
    }


@router.get("/api/v1/dashboard/preferences")
async def get_dashboard_preferences(
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Retrieve persistent dashboard layout preferences for the authenticated user."""
    user_key = ctx.user.get("uuid") or ctx.user.get("username")
    query = select(AetherDashboardPreference).where(AetherDashboardPreference.user_id == user_key)
    res = await db.execute(query)
    pref_record = res.scalar_one_or_none()

    if pref_record and pref_record.layout:
        try:
            parsed = json.loads(pref_record.layout)
            # Merge with defaults in case new widgets were added
            merged = {
                "widget_order": parsed.get("widget_order") or DEFAULT_DASHBOARD_PREFERENCES["widget_order"],
                "widget_visibility": {**DEFAULT_DASHBOARD_PREFERENCES["widget_visibility"], **(parsed.get("widget_visibility") or {})},
                "widget_sizes": {**DEFAULT_DASHBOARD_PREFERENCES["widget_sizes"], **(parsed.get("widget_sizes") or {})},
                "pinned_widgets": parsed.get("pinned_widgets") or [],
            }
            return merged
        except Exception:
            pass

    return DEFAULT_DASHBOARD_PREFERENCES


@router.put("/api/v1/dashboard/preferences")
async def save_dashboard_preferences(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Persist updated dashboard layout preferences for the authenticated user."""
    user_key = ctx.user.get("uuid") or ctx.user.get("username")
    layout_json = json.dumps(payload)

    query = select(AetherDashboardPreference).where(AetherDashboardPreference.user_id == user_key)
    res = await db.execute(query)
    pref_record = res.scalar_one_or_none()

    if pref_record:
        pref_record.layout = layout_json
        pref_record.updated_at = datetime.datetime.utcnow()
    else:
        pref_record = AetherDashboardPreference(
            id=str(uuid.uuid4()),
            user_id=user_key,
            tenant_id=ctx.tenant.id,
            layout=layout_json,
        )
        db.add(pref_record)

    await db.commit()
    await db.refresh(pref_record)
    return json.loads(pref_record.layout)


@router.post("/api/v1/dashboard/preferences/reset")
async def reset_dashboard_preferences(
    db: AsyncSession = Depends(get_db),
    ctx: TenantContext = Depends(get_tenant_context),
):
    """Reset dashboard preferences to system defaults for the authenticated user."""
    user_key = ctx.user.get("uuid") or ctx.user.get("username")
    query = select(AetherDashboardPreference).where(AetherDashboardPreference.user_id == user_key)
    res = await db.execute(query)
    pref_record = res.scalar_one_or_none()

    if pref_record:
        await db.delete(pref_record)
        await db.commit()

    return DEFAULT_DASHBOARD_PREFERENCES
