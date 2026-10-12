# services/project_and_environment_management/app/router.py
import os
import uuid
import logging
import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import AetherProject, AetherEnvironment
from app.schemas import (
    ProjectCreate, ProjectUpdate,
    EnvironmentCreate, EnvironmentUpdate, EnvironmentStatusUpdate,
    ProjectOut, ProjectListOut, EnvironmentOut,
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

    token = create_access_token(result["username"], result["role"], result.get("email", username), hours=hours)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=hours * 3600,
        path="/",
    )
    return {"token": token, "username": result["username"], "role": result["role"], "email": result.get("email", "")}


@router.post("/api/v1/auth/register")
async def api_register(payload: Dict[str, Any], request: Request, response: Response):
    """Register a new user account with email and password."""
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
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=8 * 3600,
        path="/",
    )
@router.get("/auth/google/login")
@router.get("/api/v1/auth/google/login")
async def google_oauth_login(request: Request, redirect_uri: Optional[str] = None):
    """
    Initiates Google OAuth 2.0 flow.
    Prompts account selector ('select_account') so all browser accounts are displayed to choose from.
    """
    google_cid = os.getenv("GOOGLE_CLIENT_ID", "")
    if not google_cid:
        # Check root .env
        env_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "..", ".env")
        if os.path.exists(env_root):
            with open(env_root, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GOOGLE_CLIENT_ID="):
                        google_cid = line.split("=", 1)[1].strip().strip("'\"")

    if not google_cid:
        raise HTTPException(status_code=400, detail="Google OAuth Client ID is not configured in .env.")

    cb = redirect_uri or os.getenv("GOOGLE_REDIRECT_URI", f"{str(request.base_url).rstrip('/')}/api/v1/auth/google/callback")
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

    google_cid = os.getenv("GOOGLE_CLIENT_ID", "")
    google_sec = os.getenv("GOOGLE_CLIENT_SECRET", "")
    if not (google_cid and google_sec):
        # Load from root .env if not in memory
        env_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "..", ".env")
        if os.path.exists(env_root):
            with open(env_root, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GOOGLE_CLIENT_ID="):
                        google_cid = line.split("=", 1)[1].strip().strip("'\"")
                    elif line.startswith("GOOGLE_CLIENT_SECRET="):
                        google_sec = line.split("=", 1)[1].strip().strip("'\"")

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

    if(window.opener && !window.opener.closed) {{
      window.opener.postMessage(payload, '*');
      setTimeout(() => window.close(), 600);
    }} else {{
      const targetHost = (window.location.port === '8009') ? 'http://' + window.location.hostname + ':8000' : '';
      window.location.href = targetHost + '/?token={token}&username={u_name}&email={u_email}&role={u_role}';
    }}
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
                username=username,
                email=email,
                password_hash=hash_password(dummy_pw),
                role="ADMIN",
                is_active=True,
                created_at=datetime.datetime.utcnow(),
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

        user.last_login_at = datetime.datetime.utcnow()
        await session.commit()
        user_data = {"username": user.username, "role": user.role, "email": user.email}

    token = create_access_token(user_data["username"], user_data["role"], user_data["email"], hours=24)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=24 * 3600,
        path="/",
    )
    return {"token": token, "username": user_data["username"], "role": user_data["role"], "email": user_data["email"], "provider": provider}


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
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }

    return {
        "id": 1,
        "username": username or "admin",
        "email": admin.get("email", f"{username}@aetherops.cloud"),
        "role": admin.get("role", "ADMIN"),
        "is_active": True,
    }


@router.put("/api/v1/auth/profile")
async def api_update_profile(
    payload: Dict[str, Any],
    response: Response,
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
            # Create user if needed
            from app.auth import hash_password
            import secrets as _sec
            user = AdminUser(
                username=new_username,
                email=new_email or f"{new_username}@aetherops.cloud",
                password_hash=hash_password(_sec.token_urlsafe(16)),
                role=admin.get("role", "ADMIN"),
                is_active=True,
                created_at=datetime.datetime.utcnow(),
            )
            session.add(user)
        else:
            user.username = new_username
            if new_email and "@" in new_email:
                user.email = new_email

        await session.commit()
        await session.refresh(user)

        token = create_access_token(user.username, user.role, user.email, hours=24)
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
        }


@router.post("/api/v1/auth/logout")
async def api_logout(response: Response):
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"message": "Logged out successfully."}


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/api/v1/projects", response_model=ProjectListOut)
async def list_projects(
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """Return all projects accessible to the user, with cache-aside."""
    owner = admin["username"]
    role  = admin.get("role", "ADMIN")

    # Cache check
    cached = await cache_manager.get_projects_list(owner)
    if cached:
        return ProjectListOut(projects=cached, total=len(cached))

    # If SUPER_ADMIN or root_admin, view all organization projects; otherwise user's projects
    if role in ("SUPER_ADMIN", "ADMIN") or owner in ("admin", "root_admin"):
        query = select(AetherProject).order_by(AetherProject.created_at.desc())
    else:
        query = select(AetherProject).where(AetherProject.owner == owner).order_by(AetherProject.created_at.desc())

    res = await db.execute(query)
    projects = res.scalars().all()

    out = [ProjectOut(**p.to_dict()) for p in projects]
    await cache_manager.set_projects_list(owner, [o.model_dump() for o in out])

    return ProjectListOut(projects=out, total=len(out))


@router.post("/api/v1/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """Create a new project and invalidate the owner's list cache."""
    owner = admin["username"]

    project = AetherProject(
        id=str(uuid.uuid4()),
        name=payload.name,
        description=payload.description,
        project_type=payload.project_type,
        owner=owner,
        status="CREATED",
        environment_count=0,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    await cache_manager.invalidate_projects_list(owner)
    logger.info(f"Created project '{project.name}' (id={project.id}) for owner='{owner}'")

    return ProjectOut(**project.to_dict())


@router.get("/api/v1/projects/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """Return project + all its environments. Uses detail cache."""
    owner = admin["username"]

    cached = await cache_manager.get_project_detail(project_id)
    if cached:
        return ProjectOut(**cached)

    project = await _get_project_or_404(db, project_id, owner)

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
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """Update project name, description, or status."""
    owner = admin["username"]
    project = await _get_project_or_404(db, project_id, owner)

    if payload.name is not None:
        project.name = payload.name.strip()
    if payload.description is not None:
        project.description = payload.description
    if payload.status is not None:
        project.status = payload.status.upper()

    project.updated_at = datetime.datetime.utcnow()
    await db.commit()
    await db.refresh(project)

    await cache_manager.invalidate_all_for_owner(owner, project_id)
    return ProjectOut(**project.to_dict())


@router.delete("/api/v1/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """Delete project and all its environments."""
    owner = admin["username"]
    project = await _get_project_or_404(db, project_id, owner)

    # Delete all child environments first
    env_res = await db.execute(
        select(AetherEnvironment).where(AetherEnvironment.project_id == project_id)
    )
    for env in env_res.scalars().all():
        await db.delete(env)

    await db.delete(project)
    await db.commit()

    await cache_manager.invalidate_all_for_owner(owner, project_id)
    logger.info(f"Deleted project '{project_id}' for owner='{owner}'")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ═══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/api/v1/projects/{project_id}/environments")
async def list_environments(
    project_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    owner = admin["username"]
    await _get_project_or_404(db, project_id, owner)

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
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """Create a new environment under a project."""
    owner = admin["username"]
    project = await _get_project_or_404(db, project_id, owner)

    # Check for duplicate env name within this project
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

    env = AetherEnvironment(
        id=str(uuid.uuid4()),
        project_id=project_id,
        name=payload.name,
        env_type=payload.env_type,
        aws_region=payload.aws_region,
        description=payload.description,
        status="CREATED",
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    db.add(env)

    # Update denormalised env count on project
    project.environment_count = (project.environment_count or 0) + 1
    project.updated_at = datetime.datetime.utcnow()

    await db.commit()
    await db.refresh(env)

    await cache_manager.invalidate_all_for_owner(owner, project_id)
    logger.info(f"Created environment '{env.name}' (id={env.id}) in project '{project_id}'")

    return EnvironmentOut(**env.to_dict())


@router.get("/api/v1/projects/{project_id}/environments/{env_id}", response_model=EnvironmentOut)
async def get_environment(
    project_id: str,
    env_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    owner = admin["username"]
    await _get_project_or_404(db, project_id, owner)
    env = await _get_env_or_404(db, env_id, project_id)
    return EnvironmentOut(**env.to_dict())


@router.patch("/api/v1/projects/{project_id}/environments/{env_id}", response_model=EnvironmentOut)
async def update_environment(
    project_id: str,
    env_id: str,
    payload: EnvironmentUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """Update environment name or description."""
    owner = admin["username"]
    await _get_project_or_404(db, project_id, owner)
    env = await _get_env_or_404(db, env_id, project_id)

    if payload.name is not None:
        env.name = payload.name.strip()
    if payload.description is not None:
        env.description = payload.description

    env.updated_at = datetime.datetime.utcnow()
    await db.commit()
    await db.refresh(env)

    await cache_manager.invalidate_all_for_owner(owner, project_id)
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
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """
    Advance the environment lifecycle state.
    Called by downstream modules (Module 2, 3 …) to update progress shown on the dashboard.
    """
    owner = admin["username"]
    await _get_project_or_404(db, project_id, owner)
    env = await _get_env_or_404(db, env_id, project_id)

    old_status = env.status
    env.status = payload.status
    env.updated_at = datetime.datetime.utcnow()
    await db.commit()
    await db.refresh(env)

    await cache_manager.invalidate_all_for_owner(owner, project_id)
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
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    owner = admin["username"]
    project = await _get_project_or_404(db, project_id, owner)
    env = await _get_env_or_404(db, env_id, project_id)

    await db.delete(env)
    project.environment_count = max(0, (project.environment_count or 1) - 1)
    project.updated_at = datetime.datetime.utcnow()
    await db.commit()

    await cache_manager.invalidate_all_for_owner(owner, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

async def _get_project_or_404(db: AsyncSession, project_id: str, owner: str) -> AetherProject:
    if owner in ("admin", "root_admin"):
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
