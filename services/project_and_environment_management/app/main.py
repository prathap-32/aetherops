# services/project_and_environment_management/app/main.py
import os
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from rich.logging import RichHandler

from app.database import init_projects_db
from app.auth import init_admin_security, SESSION_COOKIE_NAME, decode_access_token, MASTER_ADMIN_KEY
from app.cache import cache_manager
from app.seed import seed_initial_data
from app.router import router
from app.dashboard_page import get_dashboard_html
from app.project_page import get_project_detail_html
from app.terminal_ui import print_banner, run_startup_diagnostics, print_shutdown_banner

# ── Logging ───────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR   = os.path.dirname(os.path.dirname(BASE_DIR))
FRONTEND_DIST = os.path.join(ROOT_DIR, "frontend", "dist")
FRONTEND_ASSETS = os.path.join(FRONTEND_DIST, "assets")
logs_dir   = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
_fh  = logging.FileHandler(os.path.join(logs_dir, "project_manager.log"))
_fh.setFormatter(_fmt)
_fh.setLevel(logging.INFO)

_ch = RichHandler(level=logging.INFO, show_time=True, show_path=False, markup=True, rich_tracebacks=True)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.handlers = []
root_logger.addHandler(_fh)
root_logger.addHandler(_ch)

for _name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
    _l = logging.getLogger(_name)
    _l.handlers = [_ch]
    _l.propagate = False

logger = logging.getLogger("project-manager-service")


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print_banner()
    await run_startup_diagnostics()

    logger.info("Starting Project & Environment Management Service…")
    await cache_manager.connect()

    try:
        await init_projects_db()
        await init_admin_security()
        await seed_initial_data()
    except Exception as exc:
        logger.error(f"Startup initialisation error: {exc}", exc_info=True)

    logger.info("Module 1 ready → http://localhost:8001/app")
    yield

    # Shutdown
    logger.info("Shutting down Project Manager…")
    await cache_manager.disconnect()
    print_shutdown_banner()


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AetherOps AI — Module 1: Project & Environment Management",
    description="Create and manage projects and deployment environments.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files & React Assets ───────────────────────────────────────────────
if os.path.exists(FRONTEND_ASSETS):
    app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS), name="react_assets")

_local_static  = os.path.join(BASE_DIR, "static")
_shared_static = os.path.join(
    BASE_DIR, "..", "requirement_analysis", "static"
)
_static_dir = _local_static if os.path.exists(_local_static) else (
    _shared_static if os.path.exists(_shared_static) else None
)
if _static_dir:
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")

# ── Include API router ────────────────────────────────────────────────────────
app.include_router(router)


# ── Auth helper: redirect to login if no session ─────────────────────────────
def _is_authenticated(request: Request) -> bool:
    import secrets as _sec
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token and decode_access_token(token):
        return True
    bearer = request.headers.get("Authorization", "")
    if bearer.startswith("Bearer ") and decode_access_token(bearer.split(" ", 1)[1]):
        return True
    key = request.headers.get("X-Admin-Key", "")
    if key and _sec.compare_digest(key.strip(), MASTER_ADMIN_KEY):
        return True
    return False


# ── UI Pages (Serving Unified React SPA) ──────────────────────────────────────
@app.get("/app", response_class=HTMLResponse)
@app.get("/login", response_class=HTMLResponse)
@app.get("/app/{rest:path}", response_class=HTMLResponse)
async def unified_react_app(request: Request):
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse(content=_build_login_page())


@app.post("/login")
async def login_form(request: Request):
    """
    Form-based login — used by the login page HTML form submission.
    Delegates to the JSON API endpoint logic.
    """
    form = await request.form()
    username = str(form.get("username", ""))
    password = str(form.get("password", ""))

    from app.auth import login_admin, create_access_token, SESSION_COOKIE_NAME
    try:
        result = await login_admin(username, password, request)
        token  = create_access_token(result["username"], result["role"], username)
        resp   = RedirectResponse(url="/app", status_code=302)
        resp.set_cookie(SESSION_COOKIE_NAME, token, httponly=True, samesite="lax", max_age=28800)
        return resp
    except Exception:
        return RedirectResponse(url="/login?error=1", status_code=302)


# ── Health / Root ─────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "project-manager", "port": 8001, "timestamp": time.time()}


@app.get("/")
async def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    return {
        "service": "AetherOps AI — Module 1: Project & Environment Management",
        "version": "1.0.0",
        "port": 8001,
        "endpoints": {
            "dashboard_ui":     "/app",
            "project_detail_ui":"/app/projects/{project_id}",
            "login_ui":         "/login",
            "health":           "/health",
            "projects_api":     "/api/v1/projects",
            "environments_api": "/api/v1/projects/{id}/environments",
            "docs":             "/docs",
        },
    }


# ── Global exception handlers ─────────────────────────────────────────────────
@app.exception_handler(ValidationError)
async def _validation_err(request: Request, exc: ValidationError):
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "message": "Input validation failed."},
    )


@app.exception_handler(Exception)
async def _global_err(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error.", "error": str(exc)},
    )


# ── Login Page HTML ───────────────────────────────────────────────────────────
def _build_login_page() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AetherOps — Sign In</title>
<link rel="stylesheet" href="/static/fonts/fonts.css">
<script src="/static/js/tailwind.js"></script>
<style>
  body {
    background-color: #f8f9ff;
    color: #0b1c30;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
  }
  .font-mono {
    font-family: "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace;
  }
</style>
</head>
<body class="min-h-screen flex flex-col justify-between antialiased selection:bg-[#1e40af]/10 selection:text-[#1e40af]">
<header class="bg-white/80 backdrop-blur-md border-b border-slate-200/80 px-6 py-3.5 flex items-center justify-between">
  <div class="flex items-center gap-3">
    <div class="w-8 h-8 rounded-lg bg-[#1e40af] flex items-center justify-center text-white font-mono font-bold text-xs shadow-sm">
      AO
    </div>
    <div class="flex items-baseline gap-2">
      <span class="font-semibold text-slate-900 tracking-tight text-base">AetherOps</span>
      <span class="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-blue-50 text-[#1e40af] border border-blue-200/60 font-mono tracking-wider">MODULE 1</span>
    </div>
  </div>
  <div class="flex items-center gap-2 text-xs text-slate-500">
    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
    <span class="font-mono text-[11px]">v2.14.0 // system-online</span>
  </div>
</header>

<main class="flex-1 flex items-center justify-center p-6">
  <div class="w-full max-w-sm bg-white border border-slate-200/90 rounded-2xl shadow-sm hover:shadow-md transition-shadow p-8 space-y-6">
    <div class="text-center space-y-1.5 pb-2">
      <div class="inline-flex w-12 h-12 rounded-xl bg-blue-50 border border-blue-100 items-center justify-center text-[#1e40af] font-mono font-bold text-lg mb-2 shadow-xs">
        AO
      </div>
      <h2 class="text-xl font-semibold text-slate-900 tracking-tight">Sign in to AetherOps</h2>
      <p class="text-xs text-slate-500">Project &amp; Environment Management Console</p>
    </div>

    <div id="err" class="hidden p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium"></div>
    <div id="succ" class="hidden p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium"></div>

    <!-- OAuth Provider Buttons -->
    <div class="space-y-2.5">
      <button type="button" onclick="loginWithGoogle()" class="w-full py-2.5 px-4 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-xs transition flex items-center justify-center gap-2.5 cursor-pointer">
        <svg class="w-4 h-4" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"/>
          <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"/>
          <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 10.03 0 12c0 1.97.45 3.82 1.25 5.42l4.03-3.15z"/>
          <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
        </svg>
        <span>Continue with Google</span>
      </button>

      <button type="button" onclick="loginWithGitHub()" class="w-full py-2.5 px-4 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-xs transition flex items-center justify-center gap-2.5 cursor-pointer">
        <svg class="w-4 h-4 text-slate-900" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
        <span>Continue with GitHub</span>
      </button>
    </div>

    <div class="relative flex py-1 items-center">
      <div class="flex-grow border-t border-slate-200"></div>
      <span class="flex-shrink mx-3 text-[11px] font-medium text-slate-400 uppercase tracking-wider">or with credentials</span>
      <div class="flex-grow border-t border-slate-200"></div>
    </div>

    <!-- Mode Selector Tabs: Sign In vs Register -->
    <div class="flex p-1 bg-slate-100 rounded-xl">
      <button type="button" id="tab-login" onclick="switchAuthTab('login')" class="flex-1 py-1.5 text-xs font-semibold rounded-lg bg-white text-slate-900 shadow-xs transition cursor-pointer">
        Sign In
      </button>
      <button type="button" id="tab-reg" onclick="switchAuthTab('register')" class="flex-1 py-1.5 text-xs font-semibold rounded-lg text-slate-500 hover:text-slate-900 transition cursor-pointer">
        Create Account
      </button>
    </div>

    <!-- Login Form -->
    <form id="form-login" class="space-y-4" onsubmit="doLogin(event)">
      <div class="space-y-1.5">
        <label class="block text-xs font-semibold text-slate-700">Username or Email</label>
        <input id="u" type="text" required placeholder="admin or you@domain.com" autocomplete="username"
          class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 text-sm placeholder-slate-400 focus:outline-none focus:border-[#1e40af] focus:ring-2 focus:ring-[#1e40af]/15 transition font-mono"/>
      </div>
      <div class="space-y-1.5">
        <div class="flex items-center justify-between">
          <label class="block text-xs font-semibold text-slate-700">Password</label>
          <span class="text-[11px] text-slate-400">Default: AetherOps@2026!</span>
        </div>
        <input id="p" type="password" required placeholder="••••••••" autocomplete="current-password"
          class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 text-sm placeholder-slate-400 focus:outline-none focus:border-[#1e40af] focus:ring-2 focus:ring-[#1e40af]/15 transition font-mono"/>
      </div>
      <button type="submit" id="btn-login" class="w-full py-2.5 px-4 rounded-lg bg-[#1e40af] hover:bg-[#1d4ed8] text-white text-sm font-semibold shadow-sm hover:shadow transition flex items-center justify-center gap-2 cursor-pointer mt-2">
        <span>Sign In</span>
        <svg id="arrow-login" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
        <svg id="spin-login" class="w-4 h-4 hidden animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
      </button>
      <div class="pt-1">
        <button type="button" onclick="autofill()" class="w-full py-1.5 px-3 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs text-slate-600 transition flex items-center justify-between cursor-pointer">
          <span class="font-mono text-[11px]">admin / AetherOps@2026!</span>
          <span class="text-[10px] font-semibold text-[#1e40af] bg-blue-50 px-2 py-0.5 rounded border border-blue-200/80">Auto Fill</span>
        </button>
      </div>
    </form>

    <!-- Register Form -->
    <form id="form-register" class="space-y-4 hidden" onsubmit="doRegister(event)">
      <div class="space-y-1.5">
        <label class="block text-xs font-semibold text-slate-700">Username</label>
        <input id="reg-u" type="text" placeholder="dev_engineer" autocomplete="username"
          class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 text-sm placeholder-slate-400 focus:outline-none focus:border-[#1e40af] focus:ring-2 focus:ring-[#1e40af]/15 transition font-mono"/>
      </div>
      <div class="space-y-1.5">
        <label class="block text-xs font-semibold text-slate-700">Work Email</label>
        <input id="reg-e" type="email" placeholder="dev@company.com" autocomplete="email"
          class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 text-sm placeholder-slate-400 focus:outline-none focus:border-[#1e40af] focus:ring-2 focus:ring-[#1e40af]/15 transition font-mono"/>
      </div>
      <div class="space-y-1.5">
        <label class="block text-xs font-semibold text-slate-700">Password</label>
        <input id="reg-p" type="password" placeholder="At least 6 characters" autocomplete="new-password"
          class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 text-sm placeholder-slate-400 focus:outline-none focus:border-[#1e40af] focus:ring-2 focus:ring-[#1e40af]/15 transition font-mono"/>
      </div>
      <button type="submit" id="btn-register" class="w-full py-2.5 px-4 rounded-lg bg-[#1e40af] hover:bg-[#1d4ed8] text-white text-sm font-semibold shadow-sm hover:shadow transition flex items-center justify-center gap-2 cursor-pointer mt-2">
        <span>Create Account</span>
        <svg id="arrow-reg" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
        <svg id="spin-reg" class="w-4 h-4 hidden animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
      </button>
    </form>
  </div>
</main>

<!-- Post-OAuth Name Clarification Modal -->
<div id="oauth-name-modal" class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 hidden flex items-center justify-center p-4">
  <div class="bg-white border border-slate-200 rounded-2xl w-full max-w-sm p-6 space-y-4 shadow-xl">
    <div class="flex items-center gap-3">
      <div id="oauth-icon-badge" class="w-10 h-10 rounded-xl bg-blue-50 text-[#1e40af] flex items-center justify-center font-bold text-sm">
        AO
      </div>
      <div>
        <h3 class="text-base font-bold text-slate-900 tracking-tight">Account Verified</h3>
        <p class="text-xs text-slate-500">Confirm your preferred username</p>
      </div>
    </div>
    <div class="p-3 rounded-lg bg-blue-50/70 border border-blue-100 text-xs text-slate-600">
      <span id="oauth-verified-email" class="font-mono font-medium text-slate-900">user@domain.com</span> verified successfully. Enter your display username to complete your profile:
    </div>
    <form onsubmit="submitOAuthName(event)" class="space-y-3">
      <div class="space-y-1">
        <label class="block text-xs font-semibold text-slate-700">Display Username / Handle</label>
        <input id="oauth-input-name" type="text" required minlength="3" placeholder="e.g. dev_engineer"
          class="w-full px-3 py-2 text-xs font-mono rounded-lg border border-slate-300 focus:outline-none focus:border-[#1e40af] focus:ring-1 focus:ring-[#1e40af]"/>
      </div>
      <button type="submit" id="btn-oauth-confirm" class="w-full py-2.5 rounded-lg bg-[#1e40af] hover:bg-[#1d4ed8] text-white text-xs font-semibold shadow-sm transition">
        Continue to Dashboard
      </button>
    </form>
  </div>
</div>

<footer class="bg-white border-t border-slate-200/80 py-3.5 px-6 text-center text-xs text-slate-500">
  &copy; 2026 AetherOps Cloud — Autonomous Infrastructure Management
</footer>

<script>
  let activeTab = 'login';
  let pendingOAuthSession = null;

  function switchAuthTab(tab) {
    activeTab = tab;
    const tabLogin = document.getElementById('tab-login');
    const tabReg = document.getElementById('tab-reg');
    const formLogin = document.getElementById('form-login');
    const formReg = document.getElementById('form-register');
    const errEl = document.getElementById('err');
    const succEl = document.getElementById('succ');

    errEl.classList.add('hidden');
    succEl.classList.add('hidden');

    if (tab === 'login') {
      tabLogin.className = 'flex-1 py-1.5 text-xs font-semibold rounded-lg bg-white text-slate-900 shadow-xs transition cursor-pointer';
      tabReg.className = 'flex-1 py-1.5 text-xs font-semibold rounded-lg text-slate-500 hover:text-slate-900 transition cursor-pointer';
      formLogin.classList.remove('hidden');
      formReg.classList.add('hidden');
    } else {
      tabReg.className = 'flex-1 py-1.5 text-xs font-semibold rounded-lg bg-white text-slate-900 shadow-xs transition cursor-pointer';
      tabLogin.className = 'flex-1 py-1.5 text-xs font-semibold rounded-lg text-slate-500 hover:text-slate-900 transition cursor-pointer';
      formReg.classList.remove('hidden');
      formLogin.classList.add('hidden');
    }
  }

  function autofill(){
    document.getElementById('u').value='admin';
    document.getElementById('p').value='AetherOps@2026!';
  }

  async function doLogin(e){
    e.preventDefault();
    const u=document.getElementById('u').value.trim();
    const p=document.getElementById('p').value;
    const errEl=document.getElementById('err');
    const btn=document.getElementById('btn-login');
    const arrow=document.getElementById('arrow-login');
    const spin=document.getElementById('spin-login');
    errEl.classList.add('hidden');
    btn.disabled=true; arrow.classList.add('hidden'); spin.classList.remove('hidden');
    try{
      const res=await fetch('/api/v1/auth/login',{
        method:'POST',headers:{'Content-Type':'application/json'},
        credentials: 'include',
        body:JSON.stringify({username:u,password:p})
      });
      const data=await res.json();
      if(!res.ok) throw new Error(data.detail||'Authentication failed.');
      if(data.token) localStorage.setItem('X-Admin-Key', data.token);
      localStorage.setItem('aether_user', JSON.stringify({
        username: data.username,
        email: data.email || (data.username + '@aetherops.cloud'),
        role: data.role || 'ADMIN'
      }));
      window.location.href='/app';
    }catch(err){
      errEl.textContent=err.message; errEl.classList.remove('hidden');
      btn.disabled=false; arrow.classList.remove('hidden'); spin.classList.add('hidden');
    }
  }

  async function doRegister(e){
    e.preventDefault();
    const u=document.getElementById('reg-u').value.trim();
    const em=document.getElementById('reg-e').value.trim();
    const p=document.getElementById('reg-p').value;
    const errEl=document.getElementById('err');
    const succEl=document.getElementById('succ');
    const btn=document.getElementById('btn-register');
    const arrow=document.getElementById('arrow-reg');
    const spin=document.getElementById('spin-reg');

    errEl.classList.add('hidden');
    succEl.classList.add('hidden');
    btn.disabled=true; arrow.classList.add('hidden'); spin.classList.remove('hidden');

    try{
      const res=await fetch('/api/v1/auth/register',{
        method:'POST',headers:{'Content-Type':'application/json'},
        credentials: 'include',
        body:JSON.stringify({username:u,email:em,password:p})
      });
      const data=await res.json();
      if(!res.ok) throw new Error(data.detail||'Registration failed.');
      if(data.token) localStorage.setItem('X-Admin-Key', data.token);
      localStorage.setItem('aether_user', JSON.stringify({
        username: data.username,
        email: data.email || em,
        role: data.role || 'ADMIN'
      }));
      succEl.textContent = 'Account created successfully! Redirecting...';
      succEl.classList.remove('hidden');
      setTimeout(() => { window.location.href = '/app'; }, 600);
    }catch(err){
      errEl.textContent=err.message; errEl.classList.remove('hidden');
      btn.disabled=false; arrow.classList.remove('hidden'); spin.classList.add('hidden');
    }
  }

  function promptOAuthNameClarification(email, initialUsername, provider) {
    pendingOAuthSession = { email, initialUsername, provider };
    document.getElementById('oauth-verified-email').textContent = email;
    document.getElementById('oauth-input-name').value = initialUsername;
    document.getElementById('oauth-name-modal').classList.remove('hidden');
    setTimeout(() => document.getElementById('oauth-input-name').focus(), 50);
  }

  async function submitOAuthName(e) {
    e.preventDefault();
    if (!pendingOAuthSession) return;
    const chosenName = document.getElementById('oauth-input-name').value.trim();
    if (!chosenName) return;

    try {
      const res = await fetch('/api/v1/auth/oauth-callback', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({
          provider: pendingOAuthSession.provider,
          username: chosenName,
          email: pendingOAuthSession.email,
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to complete profile.');
      if (data.token) localStorage.setItem('X-Admin-Key', data.token);
      localStorage.setItem('aether_user', JSON.stringify({
        username: data.username,
        email: pendingOAuthSession.email,
        role: data.role || 'ADMIN'
      }));
      window.location.href = '/app';
    } catch(err) {
      alert("Error saving profile: " + err.message);
    }
  }

  function loginWithGitHub(){
    const width = 600, height = 700;
    const left = window.screen.width / 2 - width / 2;
    const top = window.screen.height / 2 - height / 2;
    const popup = window.open('http://localhost:8010/api/v1/auth/github/login?popup=1', 'GitHubOAuth', `width=${width},height=${height},top=${top},left=${left}`);
    
    window.addEventListener('message', async (e) => {
      if (e.data && e.data.type === 'GITHUB_OAUTH_SUCCESS') {
        const ghUser = e.data.user || {};
        const email = ghUser.email || (ghUser.login ? ghUser.login + '@github.user' : 'github@oauth.local');
        const login = ghUser.name || ghUser.login || 'github_dev';
        promptOAuthNameClarification(email, login, 'github');
      }
    });
  }

  function loginWithGoogle(){
    const width = 550, height = 650;
    const left = window.screen.width / 2 - width / 2;
    const top = window.screen.height / 2 - height / 2;
    const popup = window.open('/api/v1/auth/google/login', 'GoogleOAuth', `width=${width},height=${height},top=${top},left=${left}`);

    window.addEventListener('message', async (e) => {
      if (e.data && e.data.type === 'GOOGLE_OAUTH_SUCCESS') {
        const email = e.data.email || 'user@gmail.com';
        const name = e.data.name || email.split('@')[0];
        promptOAuthNameClarification(email, name, 'google');
      }
    });
  }
</script>
</body>
</html>"""

