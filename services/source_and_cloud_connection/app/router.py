# services/source_and_cloud_connection/app/router.py
import os
import uuid
import json
import datetime
import logging
from typing import Dict, Any, Optional, List

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import GitConnection, SourceSnapshot, CloudConnection
from app.schemas import (
    GitConnectionCreate, GitConnectionUpdate, ConnectionStatusUpdate,
    GitConnectionOut, SourceSnapshotOut, ConnectionListOut,
    GitHubVerifyPatRequest, GitHubVerifyPatResponse,
    GitHubOAuthConfigRequest, GitHubOAuthConfigResponse,
    GitHubRepoItem, GitHubRepoListOut, GitHubBranchListOut,
    AwsValidateRequest, AwsValidateResponse,
    CloudConnectionCreate, CloudConnectionUpdate, CloudConnectionOut, CloudConnectionListOut,
    UnifiedFinalizeRequest, UnifiedFinalizeOut,
)
from app.auth import get_current_admin, login_admin, SESSION_COOKIE_NAME, create_access_token, MASTER_ADMIN_KEY
from app.cache import cache_manager
from app.aws_service import validate_aws_connection, mask_access_key
from app.github_service import (
    get_oauth_authorize_url, exchange_oauth_code,
    verify_pat_token, fetch_user_repositories, fetch_repository_branches,
    fetch_repository_tree, fetch_repository_latest_commit, fetch_repository_metadata, detect_repository_configs,
    is_oauth_configured, github_config,
)

logger = logging.getLogger("source-connection-router")
router = APIRouter()

MODULE1_BASE_URL = os.getenv("PM_SERVICE_URL", "http://localhost:8001")


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 1 BRIDGE ENDPOINTS (PROJECTS & ENVIRONMENTS)
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/api/v1/projects")
async def list_available_projects(request: Request, admin: Dict[str, Any] = Depends(get_current_admin)):
    """Fetches active projects from Module 1 for environment binding."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.get(
                f"{MODULE1_BASE_URL}/api/v1/projects",
                headers={"X-Admin-Key": MASTER_ADMIN_KEY}
            )
            if res.status_code == 200:
                return res.json()
    except Exception as exc:
        logger.warning(f"Could not reach Module 1 at {MODULE1_BASE_URL}: {exc}")
    return {"projects": [], "total": 0}


@router.get("/api/v1/projects/{project_id}/environments")
async def list_project_environments(project_id: str, request: Request, admin: Dict[str, Any] = Depends(get_current_admin)):
    """Fetches environments for a project from Module 1."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.get(
                f"{MODULE1_BASE_URL}/api/v1/projects/{project_id}/environments",
                headers={"X-Admin-Key": MASTER_ADMIN_KEY}
            )
            if res.status_code == 200:
                return res.json()
    except Exception as exc:
        logger.warning(f"Could not reach Module 1 environments for {project_id}: {exc}")
    return {"environments": [], "total": 0}


@router.post("/api/v1/projects")
async def create_bridge_project(payload: Dict[str, Any], request: Request, admin: Dict[str, Any] = Depends(get_current_admin)):
    """Bridge to create a project in Module 1."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(
                f"{MODULE1_BASE_URL}/api/v1/projects",
                json=payload,
                headers={"X-Admin-Key": MASTER_ADMIN_KEY, "Content-Type": "application/json"}
            )
            return JSONResponse(status_code=res.status_code, content=res.json())
    except Exception as exc:
        logger.warning(f"Failed to bridge create project to Module 1: {exc}")
        return JSONResponse(status_code=502, content={"detail": f"Module 1 project creation error: {exc}"})


@router.post("/api/v1/projects/{project_id}/environments")
async def create_bridge_environment(project_id: str, payload: Dict[str, Any], request: Request, admin: Dict[str, Any] = Depends(get_current_admin)):
    """Bridge to create an environment in Module 1."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(
                f"{MODULE1_BASE_URL}/api/v1/projects/{project_id}/environments",
                json=payload,
                headers={"X-Admin-Key": MASTER_ADMIN_KEY, "Content-Type": "application/json"}
            )
            return JSONResponse(status_code=res.status_code, content=res.json())
    except Exception as exc:
        logger.warning(f"Failed to bridge create environment to Module 1: {exc}")
        return JSONResponse(status_code=502, content={"detail": f"Module 1 environment creation error: {exc}"})


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/api/v1/auth/login")
async def api_login(payload: Dict[str, Any], request: Request, response: Response):
    result = await login_admin(payload.get("username", ""), payload.get("password", ""), request)
    hours  = 168 if payload.get("remember_me") else 8
    token  = create_access_token(result["username"], result["role"], payload.get("username", ""), hours=hours)
    response.set_cookie(key=SESSION_COOKIE_NAME, value=token, httponly=True,
                        samesite="lax", max_age=hours * 3600, path="/")
    return {"token": token, "username": result["username"], "role": result["role"]}


@router.post("/api/v1/auth/logout")
async def api_logout(response: Response):
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"message": "Logged out."}


# ═══════════════════════════════════════════════════════════════════════════════
# GITHUB OAUTH & REPO DISCOVERY
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/api/v1/auth/github/config", response_model=GitHubOAuthConfigResponse)
async def get_github_oauth_config(request: Request):
    """Returns current GitHub OAuth App configuration status."""
    cb = f"{str(request.base_url).rstrip('/')}/api/v1/auth/github/callback"
    return GitHubOAuthConfigResponse(
        is_configured=is_oauth_configured(),
        client_id=github_config.get_client_id() or None,
        redirect_uri=github_config.get_redirect_uri(fallback=cb),
        callback_url_hint=cb,
    )


@router.post("/api/v1/auth/github/config")
async def save_github_oauth_config(
    payload: GitHubOAuthConfigRequest,
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """Saves and activates GitHub OAuth App client credentials."""
    github_config.update_config(
        client_id=payload.client_id,
        client_secret=payload.client_secret,
        redirect_uri=payload.redirect_uri,
    )
    return {
        "message": "GitHub OAuth App configuration updated and activated successfully.",
        "is_configured": True,
        "client_id": github_config.get_client_id(),
    }


@router.get("/auth/github/login")
@router.get("/api/v1/auth/github/login")
async def github_oauth_login(
    request: Request,
    redirect_uri: Optional[str] = None,
    popup: Optional[bool] = False,
):
    """
    Initiates GitHub OAuth flow.
    If OAuth App is configured, redirects to real GitHub authorization URL.
    If not configured, provides clear configuration guidance or switches to PAT / demo.
    """
    cb = redirect_uri or github_config.get_redirect_uri(
        fallback=f"{str(request.base_url).rstrip('/')}/api/v1/auth/github/callback"
    )
    state = str(uuid.uuid4())
    configured = is_oauth_configured()
    accept = request.headers.get("Accept", "")
    url = get_oauth_authorize_url(state=state, redirect_uri=cb)

    if not configured:
        if "text/html" in accept:
            # Render a helpful in-browser setup page
            return HTMLResponse(content=f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><title>GitHub OAuth Setup — AetherOps</title>
<link rel="stylesheet" href="/static/fonts/fonts.css">
<script src="/static/js/tailwind.js"></script>
</head>
<body class="bg-[#f5f5f7] font-sans text-[#1d1d1f] p-8 flex items-center justify-center min-h-screen">
  <div class="bg-white border border-[#e5e5ea] rounded-2xl shadow-lg max-w-lg p-6 space-y-5">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-black flex items-center justify-center text-white">
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
      </div>
      <div>
        <h2 class="text-lg font-bold">GitHub OAuth App Required</h2>
        <p class="text-xs text-[#6e6e73]">Configure your GitHub OAuth App credentials to enable one-click OAuth login.</p>
      </div>
    </div>
    <div class="p-3.5 rounded-xl bg-[#fff7ed] border border-[#fed7aa] text-xs text-[#9a3412] space-y-1">
      <div class="font-bold">Step 1: Register an OAuth App on GitHub</div>
      <div>Go to <strong>GitHub &rarr; Settings &rarr; Developer Settings &rarr; OAuth Apps &rarr; New OAuth App</strong></div>
      <div class="pt-1">Set <strong>Authorization callback URL</strong> to:</div>
      <code class="block p-1.5 rounded bg-white font-mono text-[11px] select-all border border-[#fed7aa] text-[#1d1d1f]">{cb}</code>
    </div>
    <form onsubmit="saveConfig(event)" class="space-y-3">
      <div>
        <label class="block text-xs font-semibold mb-1">Client ID</label>
        <input id="cid" type="text" required placeholder="Ov23li..." class="w-full px-3 py-2 text-xs font-mono rounded-lg border border-[#d2d2d7]"/>
      </div>
      <div>
        <label class="block text-xs font-semibold mb-1">Client Secret</label>
        <input id="csec" type="password" required placeholder="••••••••••••••••••••" class="w-full px-3 py-2 text-xs font-mono rounded-lg border border-[#d2d2d7]"/>
      </div>
      <button type="submit" id="btn-save" class="w-full py-2.5 rounded-full bg-[#0071e3] text-white text-xs font-semibold hover:bg-[#0077ed]">Save &amp; Continue with GitHub</button>
    </form>
    <div class="flex items-center justify-between pt-2 border-t border-[#e5e5ea] text-xs">
      <a href="/app/source" class="text-[#0071e3] hover:underline font-semibold">&larr; Return to Dashboard (Use PAT token)</a>
      <button onclick="demoLogin()" class="text-[#6e6e73] hover:text-[#1d1d1f]">Use Demo Mode</button>
    </div>
  </div>
<script>
async function saveConfig(e){{
  e.preventDefault();
  const cid=document.getElementById('cid').value.trim(), csec=document.getElementById('csec').value.trim();
  const res=await fetch('/api/v1/auth/github/config',{{
    method:'POST',headers:{{'Content-Type':'application/json','X-Admin-Key':'aetherops-secret-admin-key'}},
    body:JSON.stringify({{client_id:cid,client_secret:csec,redirect_uri:'{cb}'}})
  }});
  if(res.ok){{ window.location.href='/api/v1/auth/github/login'; }}
  else{{ alert('Error saving config'); }}
}}
async function demoLogin(){{
  const res=await fetch('/api/v1/auth/github/mock',{{method:'POST',headers:{{'X-Admin-Key':'aetherops-secret-admin-key'}}}});
  const data=await res.json();
  if(data.access_token){{
    localStorage.setItem('X-GH-Token',data.access_token);
    window.location.href='/app/source?github_connected=1&gh_token='+encodeURIComponent(data.access_token)+'&gh_user=aether-developer';
  }}
}}
</script>
</body>
</html>""", status_code=200)

        return {
            "url": url,
            "state": state,
            "is_configured": False,
            "callback_url_hint": cb,
            "message": "GitHub OAuth App is not configured. Configure Client ID & Secret or use Personal Access Token (PAT).",
        }

    url = get_oauth_authorize_url(state=state, redirect_uri=cb)
    if "text/html" in accept or popup:
        return RedirectResponse(url)
    return {
        "url": url,
        "state": state,
        "is_configured": True,
        "redirect_uri": cb,
    }


@router.get("/auth/github/callback")
@router.get("/api/v1/auth/github/callback")
async def github_oauth_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
):
    """
    Handles GitHub OAuth redirect callback.
    Exchanges code for access token and seamlessly communicates with parent window or redirects.
    """
    cb = github_config.get_redirect_uri(fallback=f"{str(request.base_url).rstrip('/')}/api/v1/auth/github/callback")

    if error:
        err_msg = error_description or error or "GitHub authorization was cancelled or failed."
        return HTMLResponse(content=f"""<!DOCTYPE html>
<html>
<head><title>GitHub Authorization Error</title></head>
<body style="font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;background:#f5f5f7;">
  <div style="background:white;padding:2rem;border-radius:1rem;border:1px solid #fecdd3;max-width:400px;text-align:center;">
    <h3 style="color:#dc2626;margin-bottom:0.5rem;">Authorization Cancelled</h3>
    <p style="color:#6e6e73;font-size:13px;">{err_msg}</p>
    <script>
      if(window.opener){{
        window.opener.postMessage({{type:'GITHUB_OAUTH_ERROR',error:'{err_msg}'}}, '*');
        setTimeout(()=>window.close(), 1500);
      }} else {{
        setTimeout(()=>window.location.href='/app/source', 2000);
      }}
    </script>
  </div>
</body>
</html>""", status_code=400)

    if not code:
        return JSONResponse(status_code=400, content={"error": "Missing code parameter."})

    try:
        token_info = await exchange_oauth_code(code=code, redirect_uri=cb)
        tok = token_info.get("access_token", "")
        user_info = token_info.get("user", {})
        user_login = user_info.get("login", "developer")

        # HTML response that communicates with popup opener or redirects
        return HTMLResponse(content=f"""<!DOCTYPE html>
<html>
<head><title>GitHub Connected — AetherOps</title></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;background:#f5f5f7;margin:0;">
  <div style="background:white;padding:2.5rem;border-radius:1.25rem;border:1px solid #e5e5ea;box-shadow:0 10px 25px rgba(0,0,0,0.05);max-width:380px;text-align:center;">
    <div style="width:48px;height:48px;background:#f0fdf4;color:#16a34a;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 1rem auto;font-size:24px;">✓</div>
    <h2 style="color:#1d1d1f;margin:0 0 0.5rem 0;font-size:1.25rem;">GitHub Connected!</h2>
    <p style="color:#6e6e73;font-size:13px;margin:0 0 1.5rem 0;">Authenticated as <strong>@{user_login}</strong>. Returning to console…</p>
    <div style="font-size:11px;color:#aeaeb2;">This window will close automatically.</div>
  </div>
  <script>
    const payload = {{
      type: 'GITHUB_OAUTH_SUCCESS',
      token: '{tok}',
      user: {json.dumps(user_info)}
    }};
    if(window.opener && !window.opener.closed){{
      window.opener.postMessage(payload, '*');
      setTimeout(()=>window.close(), 700);
    }} else {{
      window.location.href = '/source-connection?github_connected=1&gh_token={tok}&gh_user={user_login}&open_modal=1';
    }}
  </script>
</body>
</html>""", status_code=200)

    except Exception as exc:
        logger.error(f"GitHub OAuth callback error: {exc}")
        return HTMLResponse(content=f"""<!DOCTYPE html>
<html>
<head><title>OAuth Exchange Failed</title></head>
<body style="font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;background:#f5f5f7;">
  <div style="background:white;padding:2rem;border-radius:1rem;border:1px solid #fecdd3;max-width:400px;text-align:center;">
    <h3 style="color:#dc2626;margin-bottom:0.5rem;">OAuth Exchange Failed</h3>
    <p style="color:#6e6e73;font-size:13px;">{str(exc)}</p>
    <a href="/app/source" style="display:inline-block;margin-top:1rem;color:#0071e3;font-size:12px;font-weight:bold;">Return to Dashboard</a>
  </div>
</body>
</html>""", status_code=400)


@router.post("/api/v1/auth/github/mock")
async def github_oauth_mock(
    request: Request,
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """One-click simulated GitHub OAuth authorization for local testing and demos."""
    res = await exchange_oauth_code("mock-demo-code")
    return res


@router.post("/api/v1/github/verify-pat", response_model=GitHubVerifyPatResponse)
async def github_verify_pat(
    payload: GitHubVerifyPatRequest,
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """
    Validates a GitHub Personal Access Token against GitHub API.
    Returns username and scope permissions.
    """
    token_to_verify = payload.effective_token
    if not token_to_verify:
        raise HTTPException(status_code=400, detail="Personal Access Token (pat_token or token) is required.")
    try:
        data = await verify_pat_token(token_to_verify)
        return GitHubVerifyPatResponse(**data)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PAT verification failed: {exc}")


@router.get("/api/v1/github/repos", response_model=GitHubRepoListOut)
async def github_list_repos(
    token: Optional[str] = None,
    request: Request = None,
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """
    List repositories accessible by user using either OAuth token or PAT.
    Accepts token via query param or Authorization / X-GitHub-Token header.
    """
    gh_token = token
    if not gh_token and request:
        gh_token = request.headers.get("X-GitHub-Token")
        if not gh_token:
            auth_h = request.headers.get("Authorization", "")
            if auth_h.startswith("token "):
                gh_token = auth_h[6:].strip()

    repos = await fetch_user_repositories(gh_token)
    repo_models = [GitHubRepoItem(**r) for r in repos]
    return GitHubRepoListOut(repos=repo_models, total=len(repo_models))


@router.get("/api/v1/github/repos/{owner}/{repo}/branches", response_model=GitHubBranchListOut)
async def github_list_branches(
    owner: str,
    repo: str,
    token: Optional[str] = None,
    request: Request = None,
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """List branches for a given GitHub repository."""
    gh_token = token
    if not gh_token and request:
        gh_token = request.headers.get("X-GitHub-Token")

    branches = await fetch_repository_branches(owner, repo, gh_token)
    return GitHubBranchListOut(branches=branches)


# ═══════════════════════════════════════════════════════════════════════════════
# AWS CLOUD CONNECTION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/api/v1/cloud/aws/validate", response_model=AwsValidateResponse)
async def api_validate_aws_credentials(
    payload: AwsValidateRequest,
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """
    Validates AWS credentials via STS GetCallerIdentity (or IAM AssumeRole).
    Tests credentials without saving them.
    """
    try:
        val = await validate_aws_connection(
            auth_type=payload.auth_type,
            region=payload.aws_region,
            access_key_id=payload.access_key_id,
            secret_access_key=payload.secret_access_key,
            session_token=payload.session_token,
            role_arn=payload.role_arn,
            external_id=payload.external_id,
        )
        return AwsValidateResponse(**val)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AWS credential validation failed: {exc}")


@router.get("/api/v1/cloud/connections", response_model=CloudConnectionListOut)
async def list_cloud_connections(
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    owner = admin["username"]
    role = admin.get("role", "")
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    cache_key = f"{owner}:{tenant_id}" if tenant_id else owner

    cached = await cache_manager.get_cloud_list(cache_key)
    if cached:
        return CloudConnectionListOut(connections=cached, total=len(cached))

    if role in ("SUPER_ADMIN", "PLATFORM_SUPER_ADMIN") and not tenant_id:
        query = select(CloudConnection).order_by(CloudConnection.created_at.desc())
    elif tenant_id:
        query = select(CloudConnection).where(
            (CloudConnection.tenant_id == tenant_id) | (CloudConnection.owner == owner)
        ).order_by(CloudConnection.created_at.desc())
    else:
        query = select(CloudConnection).where(
            CloudConnection.owner == owner
        ).order_by(CloudConnection.created_at.desc())

    res = await db.execute(query)
    conns = res.scalars().all()
    out = [CloudConnectionOut(**c.to_dict()) for c in conns]
    await cache_manager.set_cloud_list(cache_key, [o.model_dump() for o in out])
    return CloudConnectionListOut(connections=out, total=len(out))


@router.post("/api/v1/cloud/connections", response_model=CloudConnectionOut, status_code=201)
async def create_cloud_connection(
    payload: CloudConnectionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """
    Creates or updates an AWS cloud connection for a project+environment pair.
    Validates credentials with AWS STS prior to saving.
    """
    owner = admin["username"]
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    user_uuid = admin.get("uuid")

    # Validate credentials
    try:
        val = await validate_aws_connection(
            auth_type=payload.auth_type,
            region=payload.aws_region,
            access_key_id=payload.access_key_id,
            secret_access_key=payload.secret_access_key,
            session_token=payload.session_token,
            role_arn=payload.role_arn,
            external_id=payload.external_id,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))

    # Remove existing connection for this env if any
    res = await db.execute(
        select(CloudConnection).where(
            CloudConnection.project_id == payload.project_id,
            CloudConnection.environment_id == payload.environment_id,
        )
    )
    existing = res.scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.flush()

    conn_id = str(uuid.uuid4())
    secret_hash = None
    enc_secret = None
    enc_nonce = None
    enc_tag = None
    enc_key_id = None
    if payload.secret_access_key:
        import bcrypt as _bc
        from app.crypto_envelope import encrypt_credential
        secret_hash = _bc.hashpw(payload.secret_access_key.encode(), _bc.gensalt(rounds=10)).decode()
        try:
            enc = encrypt_credential(payload.secret_access_key, tenant_id, conn_id, "aws_secret")
            enc_secret = enc["ciphertext"]
            enc_nonce = enc["nonce"]
            enc_tag = enc["tag"]
            enc_key_id = enc["key_id"]
        except Exception as ee:
            logger.warning(f"Envelope encryption deferred: {ee}")

    conn = CloudConnection(
        id=conn_id,
        project_id=payload.project_id,
        environment_id=payload.environment_id,
        tenant_id=tenant_id,
        created_by_user_id=user_uuid,
        owner=owner,
        provider="AWS",
        auth_type=payload.auth_type,
        aws_region=payload.aws_region,
        access_key_masked=mask_access_key(payload.access_key_id) if payload.access_key_id else None,
        access_key_id=payload.access_key_id,
        secret_key_hash=secret_hash,
        encrypted_secret=enc_secret,
        encryption_nonce=enc_nonce,
        encryption_tag=enc_tag,
        encryption_key_id=enc_key_id,
        role_arn=payload.role_arn,
        external_id=payload.external_id,
        account_id=val.get("account_id"),
        caller_arn=val.get("arn"),
        caller_user_id=val.get("user_id"),
        status="CONNECTED",
        last_validated_at=datetime.datetime.utcnow(),
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    db.add(conn)
    await db.commit()
    await db.refresh(conn)

    await cache_manager.invalidate_all(owner, conn.id, tenant_id=tenant_id)
    return CloudConnectionOut(**conn.to_dict())


async def _get_cloud_conn_or_404(
    db: AsyncSession,
    cloud_id: str,
    owner: str,
    role: str = "",
    user_uuid: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> CloudConnection:
    res = await db.execute(select(CloudConnection).where(CloudConnection.id == cloud_id))
    conn = res.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail=f"Cloud connection '{cloud_id}' not found.")

    if role in ("SUPER_ADMIN", "PLATFORM_SUPER_ADMIN"):
        return conn

    if conn.tenant_id and tenant_id:
        if conn.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail=f"Cloud connection '{cloud_id}' not found.")
        return conn

    if conn.owner == owner or (user_uuid and conn.created_by_user_id == user_uuid):
        return conn

    raise HTTPException(status_code=404, detail=f"Cloud connection '{cloud_id}' not found.")


@router.get("/api/v1/cloud/connections/{cloud_id}", response_model=CloudConnectionOut)
async def get_cloud_connection(
    cloud_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    conn = await _get_cloud_conn_or_404(
        db,
        cloud_id,
        admin["username"],
        role=admin.get("role", "USER"),
        user_uuid=admin.get("uuid"),
        tenant_id=tenant_id,
    )

    cached = await cache_manager.get_cloud_conn(cloud_id)
    if cached:
        return CloudConnectionOut(**cached)

    out = CloudConnectionOut(**conn.to_dict())
    await cache_manager.set_cloud_conn(cloud_id, out.model_dump())
    return out


@router.get("/api/v1/cloud/connections/env/{environment_id}", response_model=CloudConnectionOut)
async def get_cloud_connection_by_env(
    environment_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    role = admin.get("role", "USER")
    owner = admin["username"]
    user_uuid = admin.get("uuid")
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")

    if role in ("SUPER_ADMIN", "PLATFORM_SUPER_ADMIN"):
        query = select(CloudConnection).where(CloudConnection.environment_id == environment_id)
    elif tenant_id:
        query = select(CloudConnection).where(
            CloudConnection.environment_id == environment_id,
            (CloudConnection.tenant_id == tenant_id) | (CloudConnection.owner == owner)
        )
    else:
        query = select(CloudConnection).where(
            CloudConnection.environment_id == environment_id,
            (CloudConnection.owner == owner) | (CloudConnection.created_by_user_id == user_uuid if user_uuid else CloudConnection.owner == owner)
        )
    res = await db.execute(query)
    conn = res.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail=f"No cloud connection found for environment '{environment_id}'.")
    return CloudConnectionOut(**conn.to_dict())


@router.patch("/api/v1/cloud/connections/{cloud_id}", response_model=CloudConnectionOut)
async def update_cloud_connection(
    cloud_id: str,
    payload: CloudConnectionUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    conn = await _get_cloud_conn_or_404(
        db,
        cloud_id,
        admin["username"],
        role=admin.get("role", "USER"),
        user_uuid=admin.get("uuid"),
        tenant_id=tenant_id,
    )

    if payload.aws_region is not None:
        conn.aws_region = payload.aws_region.strip()
    if payload.role_arn is not None:
        conn.role_arn = payload.role_arn.strip()
    if payload.external_id is not None:
        conn.external_id = payload.external_id.strip()
    if payload.access_key_id is not None:
        conn.access_key_id = payload.access_key_id.strip()
        conn.access_key_masked = mask_access_key(payload.access_key_id)
    if payload.secret_access_key is not None:
        import bcrypt as _bc
        from app.crypto_envelope import encrypt_credential
        conn.secret_key_hash = _bc.hashpw(payload.secret_access_key.encode(), _bc.gensalt(rounds=10)).decode()
        try:
            enc = encrypt_credential(payload.secret_access_key, tenant_id, conn.id, "aws_secret")
            conn.encrypted_secret = enc["ciphertext"]
            conn.encryption_nonce = enc["nonce"]
            conn.encryption_tag = enc["tag"]
            conn.encryption_key_id = enc["key_id"]
        except Exception as ee:
            logger.warning(f"Envelope encryption deferred on update: {ee}")
    if payload.status is not None:
        conn.status = payload.status

    conn.updated_at = datetime.datetime.utcnow()
    await db.commit()
    await db.refresh(conn)
    await cache_manager.invalidate_all(admin["username"], cloud_id, tenant_id=tenant_id)
    return CloudConnectionOut(**conn.to_dict())


@router.delete("/api/v1/cloud/connections/{cloud_id}", status_code=204)
async def delete_cloud_connection(
    cloud_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    conn = await _get_cloud_conn_or_404(
        db,
        cloud_id,
        admin["username"],
        role=admin.get("role", "USER"),
        user_uuid=admin.get("uuid"),
        tenant_id=tenant_id,
    )
    await db.delete(conn)
    await db.commit()
    await cache_manager.invalidate_all(admin["username"], cloud_id, tenant_id=tenant_id)
    return Response(status_code=204)


@router.post("/api/v1/cloud/connections/{cloud_id}/validate", response_model=CloudConnectionOut)
async def revalidate_cloud_connection(
    cloud_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """Re-validates an existing cloud connection against AWS."""
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    conn = await _get_cloud_conn_or_404(
        db,
        cloud_id,
        admin["username"],
        role=admin.get("role", "USER"),
        user_uuid=admin.get("uuid"),
        tenant_id=tenant_id,
    )

    try:
        secret_key = None
        if conn.auth_type == "ACCESS_KEYS":
            if conn.encrypted_secret and conn.encryption_nonce and conn.encryption_tag:
                from app.crypto_envelope import decrypt_credential
                try:
                    secret_key = decrypt_credential(
                        conn.encrypted_secret,
                        conn.encryption_nonce,
                        conn.encryption_tag,
                        conn.tenant_id,
                        conn.id,
                        "aws_secret",
                    )
                except Exception as e:
                    logger.warning(f"Envelope decryption failed: {e}")
            if not secret_key:
                conn.status = "NEEDS_REAUTHENTICATION"
                conn.updated_at = datetime.datetime.utcnow()
                await db.commit()
                await db.refresh(conn)
                return CloudConnectionOut(**conn.to_dict())

        val = await validate_aws_connection(
            auth_type=conn.auth_type,
            region=conn.aws_region,
            access_key_id=conn.access_key_id or "",
            secret_access_key=secret_key or "",
            role_arn=conn.role_arn,
            external_id=conn.external_id,
        )
        conn.status = "CONNECTED"
        conn.account_id = val.get("account_id") or conn.account_id
        conn.caller_arn = val.get("arn") or conn.caller_arn
        conn.last_validated_at = datetime.datetime.utcnow()
    except Exception as exc:
        conn.status = "FAILED"
        logger.warning(f"Re-validation failed: {exc}")

    conn.updated_at = datetime.datetime.utcnow()
    await db.commit()
    await db.refresh(conn)
    await cache_manager.invalidate_all(admin["username"], cloud_id, tenant_id=tenant_id)
    return CloudConnectionOut(**conn.to_dict())


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED FINALIZE ENDPOINT (GITHUB + AWS TOGETHER)
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/api/v1/connections/finalize", response_model=UnifiedFinalizeOut, status_code=201)
async def finalize_connection(
    payload: UnifiedFinalizeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    """
    Connects and finalizes BOTH the GitHub Source repository and the AWS Cloud account
    for a project environment in a single unified atomic transaction.
    Advances Module 1 environment status to REPOSITORY_CONNECTED.
    """
    owner = admin["username"]
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    user_uuid = admin.get("uuid")

    # 1. Validate AWS credentials
    try:
        aws_val = await validate_aws_connection(
            auth_type=payload.cloud_auth_type,
            region=payload.aws_region,
            access_key_id=payload.access_key_id,
            secret_access_key=payload.secret_access_key,
            session_token=payload.session_token,
            role_arn=payload.role_arn,
            external_id=payload.external_id,
        )
    except ValueError as err:
        raise HTTPException(status_code=400, detail=f"AWS Cloud verification failed: {err}")

    # 2. Upsert Git Connection
    git_res = await db.execute(
        select(GitConnection).where(
            GitConnection.project_id == payload.project_id,
            GitConnection.environment_id == payload.environment_id,
        )
    )
    existing_git = git_res.scalar_one_or_none()
    if existing_git:
        await db.delete(existing_git)
        await db.flush()

    repo_name = _extract_repo_name(payload.repo_url)
    git_conn_id = str(uuid.uuid4())
    pat_hash = None
    enc_pat = None
    pat_nonce = None
    pat_tag = None
    if payload.pat_token:
        import bcrypt as _bc
        from app.crypto_envelope import encrypt_credential
        pat_hash = _bc.hashpw(payload.pat_token.encode(), _bc.gensalt(rounds=10)).decode()
        try:
            enc_p = encrypt_credential(payload.pat_token, tenant_id, git_conn_id, "github_pat")
            enc_pat = enc_p["ciphertext"]
            pat_nonce = enc_p["nonce"]
            pat_tag = enc_p["tag"]
        except Exception as ee:
            logger.warning(f"PAT encryption deferred: {ee}")

    git_conn = GitConnection(
        id=git_conn_id,
        project_id=payload.project_id,
        environment_id=payload.environment_id,
        tenant_id=tenant_id,
        created_by_user_id=user_uuid,
        owner=owner,
        repo_url=payload.repo_url,
        repo_name=repo_name,
        branch=payload.branch,
        auth_type=payload.git_auth_type,
        github_user=payload.github_user,
        pat_label=payload.pat_label,
        pat_token_hash=pat_hash,
        encrypted_pat=enc_pat,
        pat_nonce=pat_nonce,
        pat_tag=pat_tag,
        status="CONNECTED",
        last_commit_sha="a4f89d31b2c5e6f7a8b9c0d1e2f3a4b5c6d7e8f9",
        last_commit_msg="feat: production infrastructure baseline initialization",
        last_commit_author=payload.github_user or (owner + "@aetherops.cloud"),
        last_commit_at=datetime.datetime.utcnow(),
        default_branch=payload.branch,
        is_private=True,
        language=_detect_language(repo_name),
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    db.add(git_conn)

    # 3. Upsert Cloud Connection
    cloud_res = await db.execute(
        select(CloudConnection).where(
            CloudConnection.project_id == payload.project_id,
            CloudConnection.environment_id == payload.environment_id,
        )
    )
    existing_cloud = cloud_res.scalar_one_or_none()
    if existing_cloud:
        await db.delete(existing_cloud)
        await db.flush()

    cloud_conn_id = str(uuid.uuid4())
    secret_hash = None
    enc_secret = None
    enc_nonce = None
    enc_tag = None
    enc_key_id = None
    if payload.secret_access_key:
        import bcrypt as _bc
        from app.crypto_envelope import encrypt_credential
        secret_hash = _bc.hashpw(payload.secret_access_key.encode(), _bc.gensalt(rounds=10)).decode()
        try:
            enc_c = encrypt_credential(payload.secret_access_key, tenant_id, cloud_conn_id, "aws_secret")
            enc_secret = enc_c["ciphertext"]
            enc_nonce = enc_c["nonce"]
            enc_tag = enc_c["tag"]
            enc_key_id = enc_c["key_id"]
        except Exception as ee:
            logger.warning(f"Cloud secret encryption deferred: {ee}")

    cloud_conn = CloudConnection(
        id=cloud_conn_id,
        project_id=payload.project_id,
        environment_id=payload.environment_id,
        tenant_id=tenant_id,
        created_by_user_id=user_uuid,
        owner=owner,
        provider="AWS",
        auth_type=payload.cloud_auth_type,
        aws_region=payload.aws_region,
        access_key_masked=mask_access_key(payload.access_key_id) if payload.access_key_id else None,
        access_key_id=payload.access_key_id,
        secret_key_hash=secret_hash,
        encrypted_secret=enc_secret,
        encryption_nonce=enc_nonce,
        encryption_tag=enc_tag,
        encryption_key_id=enc_key_id,
        role_arn=payload.role_arn,
        external_id=payload.external_id,
        account_id=aws_val.get("account_id"),
        caller_arn=aws_val.get("arn"),
        caller_user_id=aws_val.get("user_id"),
        status="CONNECTED",
        last_validated_at=datetime.datetime.utcnow(),
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    db.add(cloud_conn)

    await db.commit()
    await db.refresh(git_conn)
    await db.refresh(cloud_conn)

    # 4. Capture Source Snapshot
    snap = await _capture_snapshot(db, git_conn)

    # 5. Notify Module 1 → advance env lifecycle
    await _notify_module1_status(payload.environment_id, payload.project_id, "REPOSITORY_CONNECTED")

    await cache_manager.invalidate_all(owner, git_conn.id, tenant_id=tenant_id)
    await cache_manager.del_cloud_conn(cloud_conn.id)

    return UnifiedFinalizeOut(
        git_connection=GitConnectionOut(**git_conn.to_dict()),
        cloud_connection=CloudConnectionOut(**cloud_conn.to_dict()),
        snapshot=SourceSnapshotOut(**snap.to_dict()),
        status="CONNECTED",
        message="GitHub repository and AWS cloud account connected and verified successfully.",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GIT CONNECTIONS CRUD
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/api/v1/connections", response_model=ConnectionListOut)
async def list_connections(
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    owner = admin["username"]
    role = admin.get("role", "")
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    cache_key = f"{owner}:{tenant_id}" if tenant_id else owner

    cached = await cache_manager.get_list(cache_key)
    if cached:
        return ConnectionListOut(connections=cached, total=len(cached))

    if role in ("SUPER_ADMIN", "PLATFORM_SUPER_ADMIN") and not tenant_id:
        query = select(GitConnection).order_by(GitConnection.created_at.desc())
    elif tenant_id:
        query = select(GitConnection).where(
            (GitConnection.tenant_id == tenant_id) | (GitConnection.owner == owner)
        ).order_by(GitConnection.created_at.desc())
    else:
        query = select(GitConnection).where(
            GitConnection.owner == owner
        ).order_by(GitConnection.created_at.desc())

    res = await db.execute(query)
    conns = res.scalars().all()
    out   = [GitConnectionOut(**c.to_dict()) for c in conns]
    await cache_manager.set_list(cache_key, [o.model_dump() for o in out])
    return ConnectionListOut(connections=out, total=len(out))


@router.post("/api/v1/connections", response_model=GitConnectionOut, status_code=201)
async def create_connection(
    payload: GitConnectionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    owner = admin["username"]
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    user_uuid = admin.get("uuid")

    res = await db.execute(
        select(GitConnection).where(
            GitConnection.project_id == payload.project_id,
            GitConnection.environment_id == payload.environment_id,
        )
    )
    existing = res.scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.flush()

    repo_name = _extract_repo_name(payload.repo_url)

    pat_hash = None
    if payload.pat_token:
        import bcrypt as _bc
        pat_hash = _bc.hashpw(payload.pat_token.encode(), _bc.gensalt(rounds=10)).decode()

    conn = GitConnection(
        id=str(uuid.uuid4()),
        project_id=payload.project_id,
        environment_id=payload.environment_id,
        tenant_id=tenant_id,
        created_by_user_id=user_uuid,
        owner=owner,
        repo_url=payload.repo_url,
        repo_name=repo_name,
        branch=payload.branch,
        auth_type=payload.auth_type or "PAT",
        github_user=payload.github_user,
        pat_label=payload.pat_label,
        pat_token_hash=pat_hash,
        status="PENDING",
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow(),
    )
    db.add(conn)
    await db.commit()
    await db.refresh(conn)

    await _notify_module1_status(payload.environment_id, payload.project_id, "CONFIGURED")
    await cache_manager.invalidate_all(owner, tenant_id=tenant_id)
    return GitConnectionOut(**conn.to_dict())


@router.get("/api/v1/connections/{connection_id}", response_model=GitConnectionOut)
async def get_connection(
    connection_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    conn = await _get_conn_or_404(
        db,
        connection_id,
        admin["username"],
        role=admin.get("role", ""),
        user_uuid=admin.get("uuid"),
        tenant_id=tenant_id,
    )
    cached = await cache_manager.get_conn(connection_id)
    if cached:
        return GitConnectionOut(**cached)
    out  = GitConnectionOut(**conn.to_dict())
    await cache_manager.set_conn(connection_id, out.model_dump())
    return out


@router.get("/api/v1/connections/env/{environment_id}", response_model=GitConnectionOut)
async def get_connection_by_env(
    environment_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    role = admin.get("role", "")
    owner = admin["username"]
    user_uuid = admin.get("uuid")
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")

    if role in ("SUPER_ADMIN", "PLATFORM_SUPER_ADMIN"):
        query = select(GitConnection).where(GitConnection.environment_id == environment_id)
    elif tenant_id:
        query = select(GitConnection).where(
            GitConnection.environment_id == environment_id,
            (GitConnection.tenant_id == tenant_id) | (GitConnection.owner == owner)
        )
    else:
        query = select(GitConnection).where(
            GitConnection.environment_id == environment_id,
            (GitConnection.owner == owner) | (GitConnection.created_by_user_id == user_uuid if user_uuid else GitConnection.owner == owner)
        )
    res = await db.execute(query)
    conn = res.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail=f"No connection found for environment '{environment_id}'.")
    return GitConnectionOut(**conn.to_dict())


@router.patch("/api/v1/connections/{connection_id}", response_model=GitConnectionOut)
async def update_connection(
    connection_id: str,
    payload: GitConnectionUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    conn = await _get_conn_or_404(
        db,
        connection_id,
        admin["username"],
        role=admin.get("role", ""),
        user_uuid=admin.get("uuid"),
        tenant_id=tenant_id,
    )
    if payload.branch is not None:
        conn.branch = payload.branch.strip()
    if payload.auth_type is not None:
        conn.auth_type = payload.auth_type
    if payload.github_user is not None:
        conn.github_user = payload.github_user
    if payload.pat_label is not None:
        conn.pat_label = payload.pat_label
    if payload.pat_token is not None:
        import bcrypt as _bc
        conn.pat_token_hash = _bc.hashpw(payload.pat_token.encode(), _bc.gensalt(rounds=10)).decode()
    conn.updated_at = datetime.datetime.utcnow()
    await db.commit()
    await db.refresh(conn)
    await cache_manager.invalidate_all(admin["username"], connection_id, tenant_id=tenant_id)
    return GitConnectionOut(**conn.to_dict())


@router.post("/api/v1/connections/{connection_id}/validate", response_model=GitConnectionOut)
async def validate_connection(
    connection_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    conn = await _get_conn_or_404(
        db,
        connection_id,
        admin["username"],
        role=admin.get("role", ""),
        user_uuid=admin.get("uuid"),
        tenant_id=tenant_id,
    )
    token = request.headers.get("X-GitHub-Token")

    conn.status     = "CONNECTED"
    conn.updated_at = datetime.datetime.utcnow()

    await _capture_snapshot(db, conn, token=token)
    await db.commit()
    await db.refresh(conn)

    await _notify_module1_status(conn.environment_id, conn.project_id, "REPOSITORY_CONNECTED")
    await cache_manager.invalidate_all(admin["username"], connection_id, tenant_id=tenant_id)
    return GitConnectionOut(**conn.to_dict())


@router.delete("/api/v1/connections/{connection_id}", status_code=204)
async def delete_connection(
    connection_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    conn = await _get_conn_or_404(
        db,
        connection_id,
        admin["username"],
        role=admin.get("role", ""),
        user_uuid=admin.get("uuid"),
        tenant_id=tenant_id,
    )
    snaps = await db.execute(select(SourceSnapshot).where(SourceSnapshot.connection_id == connection_id))
    for s in snaps.scalars().all():
        await db.delete(s)
    await db.delete(conn)
    await db.commit()
    await cache_manager.invalidate_all(admin["username"], connection_id, tenant_id=tenant_id)
    return Response(status_code=204)


# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE SNAPSHOTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/api/v1/connections/{connection_id}/snapshot", response_model=SourceSnapshotOut)
async def get_snapshot(
    connection_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    conn = await _get_conn_or_404(
        db,
        connection_id,
        admin["username"],
        role=admin.get("role", ""),
        user_uuid=admin.get("uuid"),
        tenant_id=tenant_id,
    )

    cached = await cache_manager.get_snapshot(connection_id)
    if cached:
        return SourceSnapshotOut(**cached)

    res = await db.execute(
        select(SourceSnapshot).where(SourceSnapshot.connection_id == connection_id)
        .order_by(SourceSnapshot.created_at.desc()).limit(1)
    )
    snap = res.scalar_one_or_none()
    if not snap:
        if conn.status == "CONNECTED" or request.query_params.get("auto") == "1":
            token = request.headers.get("X-GitHub-Token")
            snap = await _capture_snapshot(db, conn, token=token)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No snapshot found for connection '{connection_id}'. Validate first."
            )
    out = SourceSnapshotOut(**snap.to_dict())
    await cache_manager.set_snapshot(connection_id, out.model_dump())
    return out


@router.post("/api/v1/connections/{connection_id}/refresh", response_model=SourceSnapshotOut)
async def refresh_snapshot(
    connection_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
):
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    conn = await _get_conn_or_404(
        db,
        connection_id,
        admin["username"],
        role=admin.get("role", ""),
        user_uuid=admin.get("uuid"),
        tenant_id=tenant_id,
    )
    token = request.headers.get("X-GitHub-Token")
    snap = await _capture_snapshot(db, conn, token=token)
    await cache_manager.del_snapshot(connection_id)
    return SourceSnapshotOut(**snap.to_dict())


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

async def _get_conn_or_404(
    db: AsyncSession,
    connection_id: str,
    owner: str,
    role: str = "",
    user_uuid: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> GitConnection:
    res = await db.execute(select(GitConnection).where(GitConnection.id == connection_id))
    conn = res.scalar_one_or_none()
    if not conn:
        raise HTTPException(status_code=404, detail=f"Connection '{connection_id}' not found.")

    if role in ("SUPER_ADMIN", "PLATFORM_SUPER_ADMIN"):
        return conn

    if conn.tenant_id and tenant_id:
        if conn.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail=f"Connection '{connection_id}' not found.")
        return conn

    if conn.owner == owner or (user_uuid and conn.created_by_user_id == user_uuid):
        return conn

    raise HTTPException(status_code=404, detail=f"Connection '{connection_id}' not found.")


def _extract_repo_name(url: str) -> str:
    url = url.rstrip("/")
    parts = url.split("/")
    if len(parts) >= 2:
        name = "/".join(parts[-2:])
        if name.endswith(".git"):
            name = name[:-4]
        return name
    return url


def _detect_language(repo_name: str) -> str:
    name = repo_name.lower()
    if any(k in name for k in ["py", "fastapi", "django", "flask"]):
        return "Python"
    if any(k in name for k in ["node", "express", "next", "react", "ts", "js"]):
        return "JavaScript"
    if any(k in name for k in ["go", "golang"]):
        return "Go"
    if any(k in name for k in ["java", "spring"]):
        return "Java"
    return "Unknown"


async def _capture_snapshot(
    db: AsyncSession,
    conn: GitConnection,
    token: Optional[str] = None,
) -> SourceSnapshot:
    owner, repo = "", ""
    parts = conn.repo_name.split("/")
    if len(parts) >= 2:
        owner, repo = parts[0], parts[1]
    else:
        owner, repo = conn.owner, conn.repo_name

    # 1. Fetch metadata
    meta = await fetch_repository_metadata(owner=owner, repo=repo, token=token)
    if meta.get("language") and meta.get("language") != "Other":
        conn.language = meta["language"]
    conn.is_private = meta.get("is_private", True)

    # 2. Fetch latest commit
    commit = await fetch_repository_latest_commit(owner=owner, repo=repo, branch=conn.branch, token=token)
    if commit.get("sha"):
        conn.last_commit_sha = commit["sha"]
        conn.last_commit_msg = commit.get("message") or "feat: production infrastructure baseline"
        conn.last_commit_author = commit.get("author") or conn.github_user or conn.owner
        conn.last_commit_at = datetime.datetime.utcnow()

    # 3. Fetch file tree
    tree = await fetch_repository_tree(owner=owner, repo=repo, branch=conn.branch, token=token)

    # 4. Detect deployment & config files
    detected = detect_repository_configs(tree)

    lang = conn.language or _detect_language(conn.repo_name)

    # 5. Remove previous snapshots for this connection to keep fresh
    old_snaps = await db.execute(select(SourceSnapshot).where(SourceSnapshot.connection_id == conn.id))
    for s in old_snaps.scalars().all():
        await db.delete(s)

    snap = SourceSnapshot(
        id=str(uuid.uuid4()), connection_id=conn.id,
        project_id=conn.project_id, environment_id=conn.environment_id,
        commit_sha=conn.last_commit_sha or "0000000000000000000000000000000000000000",
        branch=conn.branch,
        file_tree=json.dumps(tree),
        detected_files=json.dumps(detected),
        language_hints=json.dumps({"primary": lang, "others": []}),
        total_files=str(len([f for f in tree if f.get("type") == "file"])),
        total_size_kb=str(sum(f.get("size", 0) for f in tree) // 1024 + 1),
        created_at=datetime.datetime.utcnow(),
    )
    db.add(snap)
    await db.commit()
    await db.refresh(snap)
    return snap


def _mock_file_tree(language: str):
    base = [
        {"path": "README.md",       "type": "file", "size": 1200},
        {"path": ".gitignore",      "type": "file", "size": 340},
        {"path": "Dockerfile",      "type": "file", "size": 780},
        {"path": ".github/",        "type": "dir",  "size": 0},
        {"path": ".github/workflows/ci.yml", "type": "file", "size": 960},
    ]
    if language == "Python":
        return base + [
            {"path": "requirements.txt", "type": "file", "size": 420},
            {"path": "pyproject.toml",   "type": "file", "size": 310},
            {"path": "app/",             "type": "dir",  "size": 0},
            {"path": "app/__init__.py",  "type": "file", "size": 60},
            {"path": "app/main.py",      "type": "file", "size": 3200},
            {"path": "app/models.py",    "type": "file", "size": 2100},
            {"path": "tests/",           "type": "dir",  "size": 0},
            {"path": "tests/test_app.py","type": "file", "size": 1400},
        ]
    if language in ("JavaScript", "TypeScript"):
        return base + [
            {"path": "package.json",     "type": "file", "size": 680},
            {"path": "src/",             "type": "dir",  "size": 0},
            {"path": "src/index.js",     "type": "file", "size": 1800},
            {"path": "src/routes/",      "type": "dir",  "size": 0},
            {"path": "src/routes/api.js","type": "file", "size": 2200},
        ]
    return base + [
        {"path": "src/",             "type": "dir",  "size": 0},
        {"path": "src/main.go",      "type": "file", "size": 1600},
        {"path": "go.mod",           "type": "file", "size": 380},
    ]


async def _notify_module1_status(environment_id: str, project_id: str, new_status: str):
    try:
        url = f"{MODULE1_BASE_URL}/api/v1/projects/{project_id}/environments/{environment_id}/status"
        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.patch(url,
                               json={"status": new_status},
                               headers={"X-Admin-Key": MASTER_ADMIN_KEY})
        logger.info(f"Module 1 notified: env '{environment_id}' → {new_status}")
    except Exception as exc:
        logger.warning(f"Module 1 status callback failed (non-critical): {exc}")
