# services/source_and_cloud_connection/app/main.py
import os, logging, time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from rich.logging import RichHandler

from app.database import init_source_db
from app.auth import init_admin_security, SESSION_COOKIE_NAME, decode_access_token, MASTER_ADMIN_KEY
from app.cache import cache_manager
from app.seed import seed_initial_data
from app.router import router
from app.dashboard_page import get_dashboard_html
from app.connection_page import get_connection_detail_html
from app.terminal_ui import print_banner, run_startup_diagnostics, print_shutdown_banner

# ── Logging ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
FRONTEND_DIST = os.path.join(ROOT_DIR, "frontend", "dist")
FRONTEND_ASSETS = os.path.join(FRONTEND_DIST, "assets")
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
_fh = logging.FileHandler(os.path.join(BASE_DIR, "logs", "source_connection.log"))
_fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
_ch = RichHandler(level=logging.INFO, show_time=True, show_path=False, markup=True, rich_tracebacks=True)
root = logging.getLogger()
root.setLevel(logging.INFO)
root.handlers = []
root.addHandler(_fh)
root.addHandler(_ch)
for _n in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
    _l = logging.getLogger(_n); _l.handlers = [_ch]; _l.propagate = False

logger = logging.getLogger("source-connection-service")


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print_banner()
    await run_startup_diagnostics()
    logger.info("Starting Source & Cloud Connection Service…")
    await cache_manager.connect()
    try:
        await init_source_db()
        await init_admin_security()
        await seed_initial_data()
    except Exception as exc:
        logger.error(f"Startup error: {exc}", exc_info=True)
    logger.info("Module 2 ready → http://localhost:8002/app/source")
    yield
    logger.info("Shutting down Source Connection Service…")
    await cache_manager.disconnect()
    print_shutdown_banner()


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AetherOps AI — Module 2: Source & Cloud Connection",
    description="Connect GitHub repositories to project environments and capture source snapshots.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

# Static files & React Assets
if os.path.exists(FRONTEND_ASSETS):
    app.mount("/assets", StaticFiles(directory=FRONTEND_ASSETS), name="react_assets")

for _sd in [os.path.join(BASE_DIR, "static"),
            os.path.join(BASE_DIR, "..", "requirement_analysis", "static")]:
    if os.path.exists(_sd):
        app.mount("/static", StaticFiles(directory=_sd), name="static")
        break

app.include_router(router)


# ── Auth guard ────────────────────────────────────────────────────────────────
def _authed(request: Request) -> bool:
    import secrets as _sec
    t = request.cookies.get(SESSION_COOKIE_NAME)
    if t and decode_access_token(t):
        return True
    h = request.headers.get("Authorization", "")
    if h.startswith("Bearer ") and decode_access_token(h.split(" ", 1)[1]):
        return True
    k = request.headers.get("X-Admin-Key", "")
    return bool(k and _sec.compare_digest(k.strip(), MASTER_ADMIN_KEY))


# ── UI Pages (Serving Unified React SPA) ──────────────────────────────────────
@app.get("/app", response_class=HTMLResponse)
@app.get("/app/source", response_class=HTMLResponse)
@app.get("/app/source/{rest:path}", response_class=HTMLResponse)
@app.get("/login", response_class=HTMLResponse)
async def source_react_ui(request: Request):
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse(get_dashboard_html())


@app.get("/")
async def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        index_path = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    return {
        "service": "AetherOps AI — Module 2: Source & Cloud Connection",
        "version": "1.0.0",
        "port": 8002,
        "endpoints": {
            "source_ui": "/app/source",
            "health": "/health",
            "connections_api": "/api/v1/connections",
            "cloud_connections_api": "/api/v1/cloud/connections",
            "docs": "/docs",
        },
    }


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return HTMLResponse(_login_html())


# ── Health / Root ─────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "source-and-cloud-connection", "port": 8002, "timestamp": time.time()}


@app.get("/")
async def root():
    return {
        "service": "AetherOps AI — Module 2: Source & Cloud Connection",
        "version": "1.0.0", "port": 8002,
        "endpoints": {
            "dashboard_ui": "/app/source",
            "connection_detail_ui": "/app/source/{connection_id}",
            "login_ui": "/login",
            "health": "/health",
            "connections_api": "/api/v1/connections",
            "finalize_api": "/api/v1/connections/finalize",
            "validate": "/api/v1/connections/{id}/validate",
            "snapshot": "/api/v1/connections/{id}/snapshot",
            "github_oauth_login": "/api/v1/auth/github/login",
            "github_pat_verify": "/api/v1/github/verify-pat",
            "github_repos": "/api/v1/github/repos",
            "aws_validate": "/api/v1/cloud/aws/validate",
            "cloud_connections": "/api/v1/cloud/connections",
            "docs": "/docs",
        },
    }


# ── Exception handlers ────────────────────────────────────────────────────────
@app.exception_handler(ValidationError)
async def _val_err(request: Request, exc: ValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def _global_err(request: Request, exc: Exception):
    logger.error(f"Unhandled: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"message": "Internal server error.", "error": str(exc)})


# ── Login Page HTML ───────────────────────────────────────────────────────────
def _login_html() -> str:
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
      <span class="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-blue-50 text-[#1e40af] border border-blue-200/60 font-mono tracking-wider">MODULE 2</span>
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
      <p class="text-xs text-slate-500">Source &amp; Cloud Connection Console</p>
    </div>

    <div id="err" class="hidden p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium"></div>

    <form class="space-y-4" onsubmit="doLogin(event)">
      <div class="space-y-1.5">
        <label class="block text-xs font-semibold text-slate-700">Username</label>
        <input id="u" type="text" required placeholder="admin" autocomplete="username"
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
      <button type="submit" id="btn" class="w-full py-2.5 px-4 rounded-lg bg-[#1e40af] hover:bg-[#1d4ed8] text-white text-sm font-semibold shadow-sm hover:shadow transition flex items-center justify-center gap-2 cursor-pointer mt-2">
        <span>Sign In</span>
      </button>
    </form>

    <div class="pt-2">
      <button onclick="auto()" class="w-full py-2 px-3 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs text-slate-600 transition flex items-center justify-between cursor-pointer">
        <span class="font-mono text-[11px]">admin / AetherOps@2026!</span>
        <span class="text-[10px] font-semibold text-[#1e40af] bg-blue-50 px-2 py-0.5 rounded border border-blue-200/80">Auto Fill</span>
      </button>
    </div>
  </div>
</main>

<footer class="bg-white border-t border-slate-200/80 py-3.5 px-6 text-center text-xs text-slate-500">
  &copy; 2026 AetherOps Cloud — Autonomous Infrastructure Management
</footer>

<script>
  function auto(){ document.getElementById('u').value='admin'; document.getElementById('p').value='AetherOps@2026!'; }
  async function doLogin(e){
    e.preventDefault();
    const errEl=document.getElementById('err'), btn=document.getElementById('btn');
    errEl.classList.add('hidden'); btn.disabled=true; btn.textContent='Signing in…';
    try{
      const res=await fetch('/api/v1/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({username:document.getElementById('u').value,password:document.getElementById('p').value})});
      const data=await res.json();
      if(!res.ok) throw new Error(data.detail||'Failed');
      if(data.token) localStorage.setItem('X-Admin-Key',data.token);
      window.location.href='/app/source';
    }catch(err){
      errEl.textContent=err.message; errEl.classList.remove('hidden');
      btn.disabled=false; btn.textContent='Sign In';
    }
  }
</script>
</body>
</html>"""
