# services/source_and_cloud_connection/app/connection_page.py


def get_connection_detail_html() -> str:
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AetherOps — Connection Detail</title>
<link rel="stylesheet" href="/static/fonts/fonts.css">
<script src="/static/js/tailwind.js"></script>
<script>
tailwind.config = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"Inter"', '"Segoe UI"', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'Menlo', 'monospace']
      },
      colors: {
        brand:{ DEFAULT:'#1e40af', hover:'#1d4ed8', light:'#eff6ff' },
        surface:{ DEFAULT:'#ffffff', raised:'#f8f9ff', border:'#e2e8f0', divider:'#e2e8f0' },
        ink:{ primary:'#0b1c30', secondary:'#475569', tertiary:'#94a3b8' }
      }
    }
  }
}
</script>
<style>
*{box-sizing:border-box;-webkit-font-smoothing:antialiased}
body{background:#f8f9ff;color:#0b1c30;min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,"Inter","Segoe UI",Roboto,sans-serif}
.glass-nav{background:rgba(255,255,255,.92);backdrop-filter:blur(16px);border-bottom:1px solid #e2e8f0}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.04),0 4px 16px rgba(0,0,0,.02)}
.btn-primary{background:#1e40af;color:#fff;font-weight:600;border-radius:8px;border:none;transition:background .15s,box-shadow .15s;cursor:pointer}
.btn-primary:hover{background:#1d4ed8}
.btn-secondary{background:#fff;color:#1e40af;font-weight:600;border-radius:8px;border:1px solid #cbd5e1;transition:all .15s;cursor:pointer}
.btn-secondary:hover{background:#eff6ff;border-color:#1e40af}
.btn-ghost{background:transparent;color:#475569;border-radius:8px;border:1px solid #e2e8f0;transition:all .15s;cursor:pointer}
.btn-ghost:hover{background:#f1f5f9;color:#0b1c30}
.btn-danger{background:#fff1f2;color:#dc2626;border-radius:8px;border:1px solid #fecdd3;transition:all .15s;cursor:pointer}
.btn-danger:hover{background:#fecdd3}
.pill-connected{background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0}
.pill-pending{background:#f8fafc;color:#64748b;border:1px solid #e2e8f0}
.pill-failed{background:#fff1f2;color:#dc2626;border:1px solid #fecdd3}
.tree-row{display:flex;align-items:center;gap:.5rem;padding:.35rem .5rem;border-radius:8px;cursor:default;transition:background .1s;font-size:.8125rem}
.tree-row:hover{background:#f1f5f9}
.tree-file{color:#0b1c30}
.tree-dir{color:#1e40af;font-weight:600}
.tree-size{margin-left:auto;color:#94a3b8;font-size:.6875rem;font-family:monospace}
.spinner{animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.toast{position:fixed;bottom:1.5rem;left:50%;transform:translateX(-50%) translateY(120%);z-index:100;transition:transform .3s cubic-bezier(.34,1.56,.64,1);white-space:nowrap}
.toast.show{transform:translateX(-50%) translateY(0)}
.detect-tag-yes{background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0;padding:.2rem .65rem;border-radius:980px;font-size:.6875rem;font-weight:700}
.detect-tag-no{background:#f8fafc;color:#94a3b8;border:1px solid #e2e8f0;padding:.2rem .65rem;border-radius:980px;font-size:.6875rem}
.stat-box{background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:.875rem 1rem}
.progress-step-done{background:#1e40af;border-color:#1e40af;color:#fff}
.progress-step-current{background:#d97706;border-color:#d97706;color:#fff}
.progress-step-pending{background:#fff;border-color:#cbd5e1;color:#94a3b8}
</style>
</head>
<body class="font-sans antialiased">

<!-- ── NAV ─────────────────────────────────────────────────────────────────── -->
<nav class="glass-nav sticky top-0 z-40 px-4 sm:px-6 py-3">
  <div class="max-w-5xl mx-auto flex items-center justify-between gap-3">
    <div class="flex items-center gap-2 sm:gap-2.5 min-w-0">
      <a id="nav-module1-link" href="http://localhost:8009/app" class="text-xs font-semibold px-2 sm:px-2.5 py-1 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 transition flex items-center gap-1 shrink-0" title="Back to Module 1 Master Dashboard">
        <svg class="w-3.5 h-3.5 text-[#1e40af]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
        <span class="hidden xs:inline">Module 1</span>
      </a>
      <span class="text-[#d2d2d7]">/</span>
      <a href="/app/source" class="text-xs font-semibold px-1.5 sm:px-2 py-1 rounded text-[#1e40af] hover:underline transition shrink-0">
        <span class="hidden sm:inline">Module 2: </span>Connections
      </a>
      <span class="text-[#d2d2d7]">/</span>
      <span class="font-semibold text-[#1d1d1f] text-xs sm:text-sm truncate" id="nav-repo-name">Loading…</span>
    </div>
    <div class="flex items-center gap-2 shrink-0">
      <button onclick="doRefresh()" class="btn-ghost px-2.5 sm:px-3 py-1.5 text-xs font-medium flex items-center gap-1.5">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
        <span class="hidden xs:inline">Refresh</span>
      </button>
      <button onclick="logout()" class="btn-ghost px-2.5 sm:px-3 py-1.5 text-xs font-medium">Sign Out</button>
    </div>
  </div>
</nav>

<!-- ── MAIN ─────────────────────────────────────────────────────────────────── -->
<main class="max-w-5xl mx-auto px-6 py-8 space-y-6">

  <!-- Loading -->
  <div id="loading" class="card p-20 text-center space-y-3">
    <svg class="spinner w-8 h-8 text-[#0071e3] mx-auto" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
    <p class="text-sm text-[#6e6e73]">Loading connection…</p>
  </div>

  <!-- ── Connection Header Card ── -->
  <div id="conn-header" class="hidden card p-6">
    <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-5">
      <div class="flex items-start gap-4">
        <div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#1d1d1f] to-[#424245] flex items-center justify-center shrink-0 shadow-sm">
          <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
        </div>
        <div class="space-y-1">
          <div class="flex items-center gap-3 flex-wrap">
            <h1 class="text-xl font-bold text-[#1d1d1f]" id="conn-repo-name">—</h1>
            <span id="conn-status-pill" class="px-2.5 py-0.5 rounded-full text-[11px] font-bold"></span>
          </div>
          <div class="flex flex-wrap gap-3 text-xs text-[#6e6e73]">
            <span class="flex items-center gap-1">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
              <span id="conn-branch" class="font-mono font-semibold text-[#0071e3]">—</span>
            </span>
            <span id="conn-auth-type" class="px-2 py-0.5 rounded bg-gray-100 text-gray-700 text-[10px] font-mono"></span>
            <span id="conn-lang"></span>
            <span id="conn-private"></span>
          </div>
          <a id="conn-url" href="#" target="_blank" class="text-xs text-[#0071e3] hover:underline font-mono"></a>
        </div>
      </div>
      <div class="flex gap-2 shrink-0">
        <button id="btn-validate" onclick="doValidate()" class="btn-primary px-4 py-2 text-sm flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          Validate Source
        </button>
        <button onclick="doDelete()" class="btn-danger px-4 py-2 text-sm">Disconnect</button>
      </div>
    </div>
  </div>

  <!-- ── Two-column layout ── -->
  <div id="detail-body" class="hidden grid grid-cols-1 lg:grid-cols-5 gap-6">

    <!-- LEFT: AWS cloud card + commit + snapshot stats + detected files -->
    <div class="lg:col-span-2 space-y-5">

      <!-- AWS Cloud Connection Card -->
      <div class="card p-5 space-y-4 border-[#fed7aa] bg-[#fffaf5]">
        <div class="flex items-center justify-between">
          <h2 class="text-sm font-bold text-[#1d1d1f] flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-[#ff9900]"></span>
            AWS Cloud Target
          </h2>
          <span id="cloud-status-pill" class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">Checking…</span>
        </div>

        <div id="cloud-info-box" class="space-y-2 text-xs">
          <div class="p-3 rounded-xl bg-white border border-[#fed7aa] space-y-1.5">
            <div class="flex items-center justify-between">
              <span class="text-[#6e6e73]">Account ID:</span>
              <span id="cloud-acc-id" class="font-mono font-bold text-[#1d1d1f]">None</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-[#6e6e73]">Region:</span>
              <span id="cloud-region" class="font-mono font-semibold text-[#c2410c]">—</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-[#6e6e73]">Auth Mode:</span>
              <span id="cloud-auth-mode" class="font-medium text-[#1d1d1f]">—</span>
            </div>
            <div class="flex flex-col pt-1 border-t border-[#f5f5f7]">
              <span class="text-[10px] text-[#aeaeb2]">Caller Identity ARN:</span>
              <span id="cloud-arn" class="font-mono text-[10px] text-[#6e6e73] truncate">—</span>
            </div>
          </div>
          <div class="flex items-center justify-between pt-1">
            <span id="cloud-last-val" class="text-[10px] text-[#aeaeb2]">Verified via STS</span>
            <button onclick="doRevalidateCloud()" class="py-1 px-2.5 rounded-lg bg-white border border-[#fed7aa] hover:bg-[#fff7ed] text-[11px] font-semibold text-[#c2410c] transition">
              Re-verify STS
            </button>
          </div>
        </div>
      </div>

      <!-- Latest Commit -->
      <div class="card p-5 space-y-4">
        <h2 class="text-sm font-bold text-[#1d1d1f] flex items-center gap-2">
          <span class="w-1.5 h-1.5 rounded-full bg-[#0071e3]"></span>
          Latest Commit
        </h2>
        <div id="commit-block" class="space-y-2">
          <div class="bg-[#f5f5f7] rounded-xl p-3.5 space-y-1.5">
            <div class="flex items-center gap-2">
              <span class="text-[11px] font-bold font-mono bg-[#e8f1fb] text-[#0071e3] px-2 py-0.5 rounded" id="commit-sha">—</span>
            </div>
            <p class="text-sm text-[#1d1d1f] font-medium leading-snug" id="commit-msg">—</p>
            <div class="text-[11px] text-[#6e6e73]" id="commit-author"></div>
          </div>
        </div>
      </div>

      <!-- Stats -->
      <div class="card p-5 space-y-4">
        <h2 class="text-sm font-bold text-[#1d1d1f] flex items-center gap-2">
          <span class="w-1.5 h-1.5 rounded-full bg-[#0071e3]"></span>
          Snapshot Summary
        </h2>
        <div class="grid grid-cols-2 gap-3">
          <div class="stat-box">
            <div class="text-xl font-bold text-[#1d1d1f]" id="stat-files">—</div>
            <div class="text-[11px] text-[#6e6e73] mt-0.5">Total Files</div>
          </div>
          <div class="stat-box">
            <div class="text-xl font-bold text-[#1d1d1f]" id="stat-size">—</div>
            <div class="text-[11px] text-[#6e6e73] mt-0.5">Size (KB)</div>
          </div>
          <div class="stat-box col-span-2">
            <div class="text-sm font-bold text-[#1d1d1f]" id="stat-primary-lang">—</div>
            <div class="text-[11px] text-[#6e6e73] mt-0.5">Primary Language</div>
          </div>
        </div>
      </div>

      <!-- Detected files -->
      <div class="card p-5 space-y-4">
        <h2 class="text-sm font-bold text-[#1d1d1f] flex items-center gap-2">
          <span class="w-1.5 h-1.5 rounded-full bg-[#0071e3]"></span>
          Detected Configuration
        </h2>
        <div id="detected-files" class="flex flex-wrap gap-2"></div>
        <div id="no-snapshot" class="hidden text-xs text-[#aeaeb2] italic">No snapshot yet. Validate the connection first.</div>
      </div>

      <!-- Module 3 CTA -->
      <div class="card p-5 space-y-3" style="background:linear-gradient(135deg,#f0f7ff,#e8f1fb);border-color:#bfdbfe">
        <div class="text-[10px] font-bold text-[#0071e3] uppercase tracking-widest">Next Step (Module 3)</div>
        <h3 class="text-sm font-bold text-[#1d1d1f]">Proceed to Repo Analyzer</h3>
        <p class="text-xs text-[#6e6e73]">Module 3 scans and analyzes this repository, profiles compute/memory sizing, and builds architecture blueprints.</p>
        <button class="btn-primary px-4 py-2 text-xs flex items-center gap-2 cursor-pointer shadow-sm hover:shadow" id="btn-module3" onclick="proceedToModule3()">
          <span>Proceed to Repo Analyzer (Module 3)</span>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
        </button>
      </div>

    </div>

    <!-- RIGHT: File Tree -->
    <div class="lg:col-span-3 space-y-5">
      <div class="card p-5 space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-sm font-bold text-[#1d1d1f] flex items-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full bg-[#0071e3]"></span>
            Repository File Tree
          </h2>
          <button onclick="doRefreshSnapshot()" class="btn-ghost px-3 py-1 text-xs flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
            Refresh Tree
          </button>
        </div>

        <div id="tree-loading" class="hidden py-8 text-center">
          <svg class="spinner w-5 h-5 text-[#0071e3] mx-auto" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
        </div>

        <div id="tree-empty" class="hidden py-8 text-center text-sm text-[#aeaeb2] italic">
          No file tree yet. Validate the connection to capture a snapshot.
        </div>

        <div id="file-tree" class="space-y-0.5 max-h-[520px] overflow-y-auto pr-1"></div>
      </div>

      <!-- Lifecycle stepper -->
      <div class="card p-5 space-y-4">
        <h2 class="text-sm font-bold text-[#1d1d1f] flex items-center gap-2">
          <span class="w-1.5 h-1.5 rounded-full bg-[#0071e3]"></span>
          Environment Pipeline Progress
        </h2>
        <div class="overflow-x-auto pb-1">
          <div class="flex items-center min-w-max gap-0" id="lifecycle-stepper">
            <!-- Rendered by JS -->
          </div>
        </div>
      </div>
    </div>

  </div>
</main>

<!-- ── TOAST ── -->
<div id="toast" class="toast bg-white rounded-2xl px-5 py-3 flex items-center gap-3 border border-[#e5e5ea] shadow-lg text-sm font-medium text-[#1d1d1f]">
  <span id="toast-icon" class="text-base">✅</span>
  <span id="toast-msg"></span>
</div>

<script>
const API = '';
const adminKey = localStorage.getItem('X-Admin-Key') || 'aetherops-secret-admin-key';
const CONNECTION_ID = window.location.pathname.split('/').filter(Boolean).pop();
let currentConn = null;
let currentCloudConn = null;
let currentGhToken = localStorage.getItem('X-GH-Token') || '';

function hdrs(){
  const h = {'Content-Type':'application/json','X-Admin-Key':adminKey};
  if(currentGhToken) h['X-GitHub-Token'] = currentGhToken;
  return h;
}

function toast(msg, ok=true){
  const el=document.getElementById('toast'),txt=document.getElementById('toast-msg'),ico=document.getElementById('toast-icon');
  txt.textContent=msg; ico.textContent=ok?'✅':'⚠️';
  el.classList.add('show'); setTimeout(()=>el.classList.remove('show'),3200);
}

function logout(){ fetch(`${API}/api/v1/auth/logout`,{method:'POST',headers:hdrs()}); window.location.href='/login'; }

const LIFECYCLE = ['CREATED','CONFIGURED','REPOSITORY_CONNECTED','ANALYZED','ARCHITECTURE_READY','VALIDATED','READY_TO_DEPLOY','DEPLOYING','ACTIVE'];
const LIFECYCLE_LABELS = ['Created','Configured','Repo Connected','Analyzed','Arch Ready','Validated','Ready','Deploying','Live'];

function pillClass(s){ const m={CONNECTED:'pill-connected',PENDING:'pill-pending',FAILED:'pill-failed',DISCONNECTED:'pill-disconnected'}; return m[s]||'pill-pending'; }
function langIcon(l){ const m={Python:'🐍',JavaScript:'🟨',TypeScript:'🔷',Go:'🐹',Java:'☕'}; return m[l]||'📦'; }

function fileIcon(path, type){
  if(type==='dir') return '📁';
  if(path.endsWith('.py')) return '🐍';
  if(path.endsWith('.js')||path.endsWith('.ts')) return '🟨';
  if(path.endsWith('.go')) return '🐹';
  if(path.endsWith('.java')) return '☕';
  if(path.toLowerCase()==='dockerfile') return '🐳';
  if(path.endsWith('.yml')||path.endsWith('.yaml')) return '⚙️';
  if(path.endsWith('.json')) return '📋';
  if(path.endsWith('.md')) return '📄';
  if(path.endsWith('.toml')) return '🔧';
  if(path.endsWith('.txt')) return '📝';
  return '📄';
}

function formatSize(bytes){
  if(!bytes||bytes===0) return '';
  if(bytes<1024) return bytes+'B';
  return (bytes/1024).toFixed(1)+'KB';
}

async function loadConnection(){
  try{
    const res = await fetch(`${API}/api/v1/connections/${CONNECTION_ID}`, {headers:hdrs()});
    if(res.status===401){window.location.href='/login';return;}
    if(!res.ok) throw new Error('Connection not found');
    currentConn = await res.json();
    renderConnection(currentConn);
    await loadCloudConnection(currentConn.environment_id);
    await loadSnapshot();
  }catch(e){
    document.getElementById('loading').innerHTML=`<p class="text-[#dc2626] text-sm">${e.message}</p>`;
  }
}

async function loadCloudConnection(envId){
  try{
    const res = await fetch(`${API}/api/v1/cloud/connections/env/${envId}`, {headers:hdrs()});
    if(res.ok){
      currentCloudConn = await res.json();
      renderCloud(currentCloudConn);
    } else {
      document.getElementById('cloud-status-pill').textContent = 'Not Linked';
      document.getElementById('cloud-status-pill').className = 'px-2 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 text-gray-600';
    }
  }catch(e){
    console.warn('No cloud conn for env:', e);
  }
}

function renderCloud(cloud){
  const pill = document.getElementById('cloud-status-pill');
  pill.textContent = cloud.status;
  pill.className = `px-2 py-0.5 rounded-full text-[10px] font-bold ${pillClass(cloud.status)}`;

  document.getElementById('cloud-acc-id').textContent = cloud.account_id || '—';
  document.getElementById('cloud-region').textContent = cloud.aws_region;
  document.getElementById('cloud-auth-mode').textContent = cloud.auth_type==='ACCESS_KEYS' ? 'Access Key Pair' : 'IAM Role ARN';
  document.getElementById('cloud-arn').textContent = cloud.caller_arn || cloud.role_arn || '—';
}

function renderConnection(c){
  document.getElementById('loading').classList.add('hidden');
  document.getElementById('conn-header').classList.remove('hidden');
  document.getElementById('detail-body').classList.remove('hidden');

  document.getElementById('nav-repo-name').textContent = c.repo_name;
  document.getElementById('conn-repo-name').textContent = c.repo_name;
  document.getElementById('conn-branch').textContent = c.branch;
  document.getElementById('conn-auth-type').textContent = `Auth: ${c.auth_type||'PAT'}`;

  if(c.project_id){
    const m1Link = document.getElementById('nav-module1-link');
    if(m1Link){
      m1Link.href = `http://localhost:8009/app/projects/${c.project_id}`;
      m1Link.title = `Back to Project ${c.project_id}`;
    }
  }

  const urlEl = document.getElementById('conn-url');
  urlEl.href=c.repo_url; urlEl.textContent=c.repo_url;

  const pill = document.getElementById('conn-status-pill');
  pill.className = `px-2.5 py-0.5 rounded-full text-[11px] font-bold ${pillClass(c.status)}`;
  pill.textContent = c.status;

  document.getElementById('conn-lang').textContent  = c.language ? `${langIcon(c.language)} ${c.language}` : '';
  document.getElementById('conn-private').textContent = c.is_private ? '🔒 Private' : '🌐 Public';

  if(c.last_commit_sha){
    document.getElementById('commit-sha').textContent = c.last_commit_sha.slice(0,7);
    document.getElementById('commit-msg').textContent = c.last_commit_msg || '—';
    document.getElementById('commit-author').textContent = c.last_commit_author ? `by ${c.last_commit_author}` : '';
  } else {
    document.getElementById('commit-block').innerHTML='<p class="text-xs text-[#aeaeb2] italic">Pending validation</p>';
  }

  if(c.status==='CONNECTED'){
    document.getElementById('btn-validate').textContent='Re-validate Source';
  }

  renderStepper(c);
}

function renderStepper(c){
  const container = document.getElementById('lifecycle-stepper');
  container.innerHTML='';
  const stepIdx = LIFECYCLE.indexOf(c.status==='CONNECTED' ? 'REPOSITORY_CONNECTED' : 'CONFIGURED');

  LIFECYCLE.forEach((step, i)=>{
    const isDone    = i < stepIdx;
    const isCurrent = i === stepIdx;
    const dotClass  = isDone ? 'progress-step-done' : (isCurrent ? 'progress-step-current' : 'progress-step-pending');
    const lineClass = isDone ? 'bg-[#0071e3]' : 'bg-[#e5e5ea]';

    container.innerHTML += `
      <div class="flex flex-col items-center gap-1">
        <div class="w-6 h-6 rounded-full border-2 flex items-center justify-center text-[10px] font-bold ${dotClass}">
          ${isDone ? '✓' : (i+1)}
        </div>
        <div class="text-[9px] font-medium ${isCurrent?'text-[#ff9f0a]':(isDone?'text-[#0071e3]':'text-[#aeaeb2]')} text-center max-w-[56px] leading-tight">${LIFECYCLE_LABELS[i]}</div>
      </div>
      ${i < LIFECYCLE.length-1 ? `<div class="h-0.5 w-6 ${lineClass} mt-3 mb-5 shrink-0"></div>` : ''}
    `;
  });
}

async function loadSnapshot(){
  try{
    const res = await fetch(`${API}/api/v1/connections/${CONNECTION_ID}/snapshot`, {headers:hdrs()});
    if(res.status===404){
      // Automatically trigger validate silently to capture live file tree
      await doValidate(true);
      return;
    }
    if(!res.ok) return;
    const snap = await res.json();
    renderSnapshot(snap);
  }catch(e){ /* no snapshot yet */ }
}

function renderSnapshot(snap){
  document.getElementById('stat-files').textContent  = snap.total_files || '—';
  document.getElementById('stat-size').textContent   = snap.total_size_kb || '—';
  document.getElementById('stat-primary-lang').textContent = snap.language_hints?.primary || '—';

  const df = snap.detected_files||{};
  const dfEl = document.getElementById('detected-files');
  dfEl.innerHTML='';
  const labels = {dockerfile:'Dockerfile',docker_compose:'Docker Compose',requirements_txt:'requirements.txt',
                  package_json:'package.json',github_actions:'GitHub Actions',makefile:'Makefile'};
  Object.entries(labels).forEach(([k,label])=>{
    dfEl.innerHTML += df[k]
      ? `<span class="detect-tag-yes">✓ ${label}</span>`
      : `<span class="detect-tag-no">${label}</span>`;
  });

  const tree = snap.file_tree||[];
  const treeEl = document.getElementById('file-tree');
  document.getElementById('tree-empty').classList.add('hidden');
  treeEl.innerHTML='';
  tree.forEach(f=>{
    const depth  = (f.path.match(/\//g)||[]).length;
    const indent = depth * 16;
    const icon   = fileIcon(f.path, f.type);
    const name   = f.path.split('/').filter(Boolean).pop() || f.path;
    const sz     = formatSize(f.size);
    treeEl.innerHTML += `
      <div class="tree-row ${f.type==='dir'?'tree-dir':'tree-file'}" style="padding-left:${8+indent}px">
        <span class="text-sm">${icon}</span>
        <span>${escHtml(name)}${f.type==='dir'?'/':''}</span>
        ${sz?`<span class="tree-size">${sz}</span>`:''}
      </div>`;
  });

  if(currentConn && currentConn.status==='CONNECTED'){
    document.getElementById('btn-module3').disabled=false;
  }
}

function proceedToModule3(){
  if(!currentConn) return;
  const pId = encodeURIComponent(currentConn.project_id || '');
  const eId = encodeURIComponent(currentConn.environment_id || '');
  const rUrl = encodeURIComponent(currentConn.repo_url || '');
  const br = encodeURIComponent(currentConn.branch || 'main');
  const rName = encodeURIComponent(currentConn.repo_name || '');
  window.location.href = `http://localhost:8001/app?project_id=${pId}&environment_id=${eId}&repo_url=${rUrl}&branch=${br}&repo_name=${rName}`;
}

async function doValidate(silent=false){
  if(!silent) toast('Validating source repository…');
  try{
    const res = await fetch(`${API}/api/v1/connections/${CONNECTION_ID}/validate`,{method:'POST',headers:hdrs()});
    const data = await res.json();
    if(!res.ok) throw new Error(data.detail||'Failed');
    currentConn = data;
    renderConnection(data);
    const snapRes = await fetch(`${API}/api/v1/connections/${CONNECTION_ID}/snapshot`, {headers:hdrs()});
    if(snapRes.ok){
      const snap = await snapRes.json();
      renderSnapshot(snap);
    }
    if(!silent) toast('Repository validated & snapshot updated!', true);
  }catch(e){
    if(!silent) toast(e.message,false);
  }
}

async function doRevalidateCloud(){
  if(!currentCloudConn){ toast('No cloud connection linked to re-verify', false); return; }
  toast('Verifying AWS STS credentials…');
  try{
    const res = await fetch(`${API}/api/v1/cloud/connections/${currentCloudConn.id}/validate`,{method:'POST',headers:hdrs()});
    const data = await res.json();
    if(!res.ok) throw new Error(data.detail||'Cloud validation failed');
    currentCloudConn = data;
    renderCloud(data);
    toast('AWS STS verification successful!', true);
  }catch(e){ toast(e.message, false); }
}

async function doRefreshSnapshot(){
  document.getElementById('tree-loading').classList.remove('hidden');
  document.getElementById('file-tree').innerHTML='';
  try{
    const res = await fetch(`${API}/api/v1/connections/${CONNECTION_ID}/refresh`,{method:'POST',headers:hdrs()});
    const snap = await res.json();
    if(!res.ok) throw new Error(snap.detail||'Refresh failed');
    renderSnapshot(snap);
    toast('File tree refreshed!',true);
  }catch(e){ toast(e.message,false); }
  finally{ document.getElementById('tree-loading').classList.add('hidden'); }
}

async function doRefresh(){
  await loadConnection();
  toast('Refreshed',true);
}

async function doDelete(){
  if(!confirm('Disconnect this repository? The connection and snapshots will be removed.')) return;
  const res = await fetch(`${API}/api/v1/connections/${CONNECTION_ID}`,{method:'DELETE',headers:hdrs()});
  if(res.ok){ toast('Disconnected.'); setTimeout(()=>window.location.href='/app/source',1200); }
  else toast('Failed to disconnect.',false);
}

function escHtml(s){ const d=document.createElement('div'); d.textContent=s||''; return d.innerHTML; }

window.addEventListener('DOMContentLoaded', loadConnection);
</script>
</body>
</html>"""
