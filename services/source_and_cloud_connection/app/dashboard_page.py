# services/source_and_cloud_connection/app/dashboard_page.py


def get_dashboard_html() -> str:
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>AetherOps — Source & Cloud Connections</title>
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
        brand:{ DEFAULT:'#1e40af', hover:'#1d4ed8', light:'#eff6ff', ring:'rgba(30,64,175,0.2)' },
        surface:{ DEFAULT:'#ffffff', raised:'#f8f9ff', card:'#ffffff', border:'#e2e8f0', divider:'#e2e8f0' },
        ink:{ primary:'#0b1c30', secondary:'#475569', tertiary:'#94a3b8', inverse:'#ffffff' },
        aws:{ DEFAULT:'#ff9900', light:'#fff7ed', border:'#fed7aa', text:'#c2410c' },
        github:{ DEFAULT:'#24292f', light:'#f6f8fa', border:'#d0d7de' },
        success:{ DEFAULT:'#16a34a', bg:'#f0fdf4', border:'#bbf7d0', text:'#16a34a' },
        warning:{ DEFAULT:'#d97706', bg:'#fffbeb', border:'#fde68a', text:'#d97706' },
        danger: { DEFAULT:'#dc2626', bg:'#fff1f2', border:'#fecdd3', text:'#dc2626' },
        pending:{ DEFAULT:'#64748b', bg:'#f8fafc', border:'#e2e8f0', text:'#64748b' },
      },
      boxShadow: {
        apple:'0 1px 3px rgba(0,0,0,.04),0 8px 24px rgba(0,0,0,.03)',
        'apple-lg':'0 4px 6px rgba(0,0,0,.04),0 16px 48px rgba(0,0,0,.06)',
        'apple-btn':'0 1px 0 rgba(255,255,255,.25) inset,0 1px 2px rgba(0,0,0,.12)',
      },
      borderRadius:{ xl2:'0.75rem', xl3:'1rem' }
    }
  }
}
</script>
<style>
*{box-sizing:border-box;-webkit-font-smoothing:antialiased}
body{background:#f8f9ff;color:#0b1c30;min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,"Inter","Segoe UI",Roboto,sans-serif}
.glass-nav{background:rgba(255,255,255,.92);backdrop-filter:blur(16px);border-bottom:1px solid #e2e8f0}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.04),0 4px 16px rgba(0,0,0,.02);transition:box-shadow .2s,border-color .2s,transform .15s}
.card:hover{box-shadow:0 4px 6px rgba(0,0,0,.04),0 16px 48px rgba(0,0,0,.06);border-color:#cbd5e1;transform:translateY(-1px)}
.btn-primary{background:#1e40af;color:#fff;font-weight:600;border-radius:8px;border:none;transition:background .15s,box-shadow .15s;cursor:pointer;box-shadow:0 1px 2px rgba(30,64,175,.2)}
.btn-primary:hover{background:#1d4ed8;box-shadow:0 2px 8px rgba(30,64,175,.3)}
.btn-primary:active{background:#00288e}
.btn-secondary{background:#fff;color:#1e40af;font-weight:600;border-radius:8px;border:1px solid #cbd5e1;transition:all .15s;cursor:pointer}
.btn-secondary:hover{background:#eff6ff;border-color:#1e40af}
.btn-ghost{background:transparent;color:#475569;font-weight:500;border-radius:8px;border:1px solid #e2e8f0;transition:all .15s;cursor:pointer}
.btn-ghost:hover{background:#f1f5f9;color:#0b1c30}
.inp{background:#fff;border:1px solid #e2e8f0;border-radius:8px;color:#0b1c30;font-size:.875rem;transition:border-color .15s,box-shadow .15s}
.inp:focus{border-color:#2563eb;outline:none;box-shadow:0 0 0 3px rgba(37,99,235,.12)}
select.inp option{background:#fff;color:#0b1c30}
.pill-connected{background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0}
.pill-pending{background:#f8fafc;color:#64748b;border:1px solid #e2e8f0}
.pill-failed{background:#fff1f2;color:#dc2626;border:1px solid #fecdd3}
.pill-disconnected{background:#fffbeb;color:#d97706;border:1px solid #fde68a}
.modal-overlay{position:fixed;inset:0;background:rgba(15,23,42,.45);backdrop-filter:blur(4px);z-index:50;display:flex;align-items:center;justify-content:center;padding:1rem;overflow-y:auto}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:4px}
.spinner{animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.toast{position:fixed;bottom:1.5rem;left:50%;transform:translateX(-50%) translateY(120%);z-index:100;transition:transform .3s cubic-bezier(.34,1.56,.64,1);white-space:nowrap}
.toast.show{transform:translateX(-50%) translateY(0)}
.tab-btn{padding:.4rem 1rem;font-size:.8125rem;font-weight:600;border-radius:8px;transition:all .15s;cursor:pointer}
.tab-btn.active{background:#1e40af;color:#fff}
.tab-btn:not(.active){background:#f1f5f9;color:#64748b}
.tab-btn:not(.active):hover{background:#e2e8f0;color:#0b1c30}
</style>
</head>
<body class="font-sans antialiased">

<!-- ── NAV ─────────────────────────────────────────────────────────────────── -->
<nav class="glass-nav sticky top-0 z-40 px-4 sm:px-6 py-3">
  <div class="max-w-6xl mx-auto flex items-center justify-between gap-3">
    <div class="flex items-center gap-2 sm:gap-3 min-w-0">
      <div class="w-8 h-8 rounded-lg bg-[#1e40af] flex items-center justify-center text-white font-mono font-bold text-xs shadow-sm shrink-0">
        AO
      </div>
      <a href="http://localhost:8009/app" class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold flex items-center gap-1 transition shrink-0" title="Back to Master Dashboard">
        <span>&larr; <span class="hidden xs:inline">Master </span>Dashboard</span>
      </a>
      <span class="text-slate-300 hidden sm:inline">/</span>
      <span class="text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 text-[#1e40af] border border-blue-200 font-mono hidden md:inline">MODULE 2</span>
      <span class="text-xs sm:text-sm font-semibold text-slate-900 truncate">Source &amp; Cloud</span>
    </div>
    <div class="flex items-center gap-2 shrink-0">
      <a href="http://localhost:8001/app" target="_blank" class="hidden md:flex px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-white text-xs font-semibold text-slate-600 hover:text-slate-900 transition items-center gap-1">
        <span>Module 3: Repo Analyzer</span>
        <svg class="w-3 h-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
      </a>
      <button onclick="showConnectModal()" class="btn-primary px-3 sm:px-4 py-1.5 text-xs font-semibold flex items-center gap-1.5 shadow-sm">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/></svg>
        <span>Connect<span class="hidden sm:inline"> Source &amp; Cloud</span></span>
      </button>
      <button onclick="logout()" class="btn-ghost px-2.5 sm:px-3 py-1.5 text-xs font-semibold flex items-center gap-1">
        Sign Out
      </button>
    </div>
  </div>
</nav>

<!-- ── MAIN ─────────────────────────────────────────────────────────────────── -->
<main class="max-w-6xl mx-auto px-6 py-10 space-y-8">

  <!-- Page header -->
  <div class="space-y-1">
    <h1 class="text-3xl font-bold text-[#1d1d1f] tracking-tight">Source &amp; Cloud Connections</h1>
    <p class="text-[#6e6e73]">Connect GitHub repositories via OAuth or Personal Access Token (PAT), and pair with AWS Cloud credentials (Access Keys or IAM Role ARN).</p>
  </div>

  <!-- Stats row -->
  <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
    <div class="card p-5 space-y-3">
      <div class="w-fit p-2 rounded-xl bg-blue-50 text-[#0071e3]">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
      </div>
      <div><div class="text-2xl font-bold text-[#1d1d1f]" id="stat-total">0</div><div class="text-xs text-[#6e6e73] mt-0.5">Total Connections</div></div>
    </div>
    <div class="card p-5 space-y-3">
      <div class="w-fit p-2 rounded-xl bg-emerald-50 text-emerald-600">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      </div>
      <div><div class="text-2xl font-bold text-[#1d1d1f]" id="stat-git-connected">0</div><div class="text-xs text-[#6e6e73] mt-0.5">GitHub Connected</div></div>
    </div>
    <div class="card p-5 space-y-3">
      <div class="w-fit p-2 rounded-xl bg-amber-50 text-amber-600">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 00-9.78 2.096A4.001 4.001 0 003 15z"/></svg>
      </div>
      <div><div class="text-2xl font-bold text-[#1d1d1f]" id="stat-aws-connected">0</div><div class="text-xs text-[#6e6e73] mt-0.5">AWS Accounts Linked</div></div>
    </div>
    <div class="card p-5 space-y-3">
      <div class="w-fit p-2 rounded-xl bg-purple-50 text-purple-600">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
      </div>
      <div><div class="text-2xl font-bold text-[#1d1d1f]" id="stat-repos">0</div><div class="text-xs text-[#6e6e73] mt-0.5">Repositories Tracked</div></div>
    </div>
  </div>

  <!-- Loading -->
  <div id="loading" class="card p-20 text-center space-y-4">
    <svg class="spinner w-8 h-8 text-[#0071e3] mx-auto" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
    <p class="text-sm text-[#6e6e73]">Loading connections…</p>
  </div>

  <!-- Empty state -->
  <div id="empty" class="hidden card p-16 text-center space-y-5">
    <div class="mx-auto w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <svg class="w-8 h-8 text-[#0071e3]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
    </div>
    <div class="space-y-2">
      <h3 class="text-xl font-semibold text-[#1d1d1f]">No connections linked yet</h3>
      <p class="text-sm text-[#6e6e73] max-w-md mx-auto">Connect your GitHub repository and link your AWS Cloud account (Access Keys or IAM Role ARN) to establish your deployment target.</p>
    </div>
    <button onclick="showConnectModal()" class="btn-primary px-6 py-2.5 text-sm mx-auto flex items-center gap-2">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/></svg>
      Connect First Environment
    </button>
  </div>

  <!-- Connection cards grid -->
  <div id="connections-grid" class="hidden grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"></div>

</main>

<!-- ═══════════════════ UNIFIED CONNECT WIZARD MODAL ═══════════════════════════════════════ -->
<div id="connect-modal" class="modal-overlay hidden">
  <div class="bg-white rounded-2xl shadow-apple-lg w-full max-w-2xl p-7 space-y-6 my-auto" style="border:1px solid rgba(0,0,0,.08)">

    <!-- Modal Header -->
    <div class="flex items-start justify-between border-b border-[#e5e5ea] pb-4">
      <div>
        <h3 class="text-xl font-bold text-[#1d1d1f]">Connect Source &amp; Cloud</h3>
        <p class="text-xs text-[#6e6e73] mt-0.5">Pair your Git repository with your AWS target deployment account.</p>
      </div>
      <button onclick="hideConnectModal()" class="text-[#aeaeb2] hover:text-[#1d1d1f] text-lg font-bold">&times;</button>
    </div>

    <!-- Stepper Navigation -->
    <div id="wizard-stepper" class="flex border-b border-[#e5e5ea] pb-2 gap-2">
      <button id="tab-btn-1" type="button" onclick="setStep(1)" class="tab-btn active flex items-center gap-1.5">
        <span class="w-4 h-4 rounded-full bg-white/20 text-xs flex items-center justify-center">1</span>
        GitHub Source
      </button>
      <button id="tab-btn-2" type="button" onclick="setStep(2)" class="tab-btn flex items-center gap-1.5">
        <span class="w-4 h-4 rounded-full bg-black/10 text-xs flex items-center justify-center">2</span>
        AWS Cloud
      </button>
      <button id="tab-btn-3" type="button" onclick="setStep(3)" class="tab-btn flex items-center gap-1.5">
        <span class="w-4 h-4 rounded-full bg-black/10 text-xs flex items-center justify-center">3</span>
        Review &amp; Finalize
      </button>
    </div>
    <form id="unified-connect-form" onsubmit="submitUnifiedConnect(event)" class="space-y-4">

      <!-- ── STEP 1: GITHUB SOURCE ── -->
      <div id="step-1-content" class="space-y-4">
        <div class="space-y-2">
          <label class="block text-xs font-semibold text-[#1d1d1f]">GitHub Authentication Mode</label>
          <div class="grid grid-cols-3 gap-2">
            <button type="button" id="gh-mode-oauth" onclick="setGhMode('OAUTH')" class="p-2.5 rounded-xl border text-xs font-semibold flex flex-col items-center gap-1 border-[#0071e3] bg-[#e8f1fb] text-[#0071e3]">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
              <span>GitHub OAuth</span>
            </button>
            <button type="button" id="gh-mode-pat" onclick="setGhMode('PAT')" class="p-2.5 rounded-xl border text-xs font-semibold flex flex-col items-center gap-1 border-[#e5e5ea] bg-white text-[#6e6e73]">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/></svg>
              <span>PAT Token</span>
            </button>
            <button type="button" id="gh-mode-manual" onclick="setGhMode('MANUAL')" class="p-2.5 rounded-xl border text-xs font-semibold flex flex-col items-center gap-1 border-[#e5e5ea] bg-white text-[#6e6e73]">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/></svg>
              <span>Manual URL</span>
            </button>
          </div>
        </div>

        <!-- OAUTH SECTION -->
        <div id="gh-oauth-box" class="p-4 rounded-xl bg-[#f5f5f7] border border-[#e5e5ea] space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold text-[#1d1d1f]">GitHub OAuth App</span>
            <span id="oauth-status-badge" class="text-[11px] px-2 py-0.5 rounded-full bg-gray-100 text-[#6e6e73] font-bold">Checking…</span>
          </div>

          <!-- OAuth Not Configured Banner -->
          <div id="oauth-unconfigured-panel" class="hidden p-3 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 space-y-2">
            <div class="font-bold flex items-center gap-1">
              <span>⚠️</span> GitHub OAuth App Credentials Needed
            </div>
            <p class="text-[11px] text-amber-800 leading-relaxed">
              GitHub web OAuth requires registering an OAuth App on GitHub to obtain a <strong>Client ID</strong> and <strong>Client Secret</strong>.
            </p>
            <div class="flex gap-2 pt-1 flex-wrap">
              <button type="button" onclick="toggleOAuthConfigForm()" class="px-2.5 py-1 rounded-lg bg-amber-200 hover:bg-amber-300 text-amber-900 text-xs font-semibold">
                ⚙️ Configure Client ID &amp; Secret
              </button>
              <button type="button" onclick="setGhMode('PAT')" class="px-2.5 py-1 rounded-lg bg-white border border-amber-300 text-[#1d1d1f] text-xs font-semibold">
                Use PAT Token Instead (No App Setup)
              </button>
            </div>
          </div>

          <!-- Inline OAuth Config Form -->
          <div id="oauth-config-form" class="hidden p-3.5 rounded-xl bg-white border border-[#d2d2d7] space-y-2.5 text-xs">
            <div class="font-bold text-[#1d1d1f] flex items-center justify-between">
              <span>GitHub OAuth App Settings</span>
              <button type="button" onclick="toggleOAuthConfigForm()" class="text-[#aeaeb2] text-xs">&times;</button>
            </div>
            <div class="space-y-1">
              <span class="text-[#6e6e73] text-[11px]">Callback URL (register this on GitHub):</span>
              <div class="flex gap-1.5">
                <input id="cfg-cb-url" type="text" readonly class="inp flex-1 px-2.5 py-1.5 font-mono text-[11px] bg-gray-50 select-all"/>
                <button type="button" onclick="copyCallbackUrl()" class="px-2 py-1 bg-gray-100 hover:bg-gray-200 text-[11px] rounded-lg font-medium">Copy</button>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div class="space-y-1">
                <label class="block text-[11px] font-semibold">Client ID</label>
                <input id="cfg-client-id" type="text" placeholder="Ov23li..." class="inp w-full px-2.5 py-1.5 font-mono text-[11px]"/>
              </div>
              <div class="space-y-1">
                <label class="block text-[11px] font-semibold">Client Secret</label>
                <input id="cfg-client-secret" type="password" placeholder="••••••••••••••••••••" class="inp w-full px-2.5 py-1.5 font-mono text-[11px]"/>
              </div>
            </div>
            <div class="flex justify-end gap-2 pt-1">
              <button type="button" onclick="saveOAuthConfig()" class="btn-primary px-3 py-1.5 text-xs">Save &amp; Activate OAuth</button>
            </div>
          </div>

          <!-- Connected / Actions Bar -->
          <div id="oauth-actions-row" class="flex gap-2">
            <button type="button" id="btn-oauth-connect" onclick="startGithubOAuth()" class="flex-1 py-2 px-3 rounded-lg bg-[#24292f] hover:bg-black text-white text-xs font-semibold flex items-center justify-center gap-2 transition shadow-sm">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
              <span>Connect with GitHub (OAuth)</span>
            </button>
          </div>

          <div id="oauth-connected-info" class="hidden p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-emerald-600 text-white flex items-center justify-center text-[10px] font-bold">✓</span>
              <span class="font-semibold" id="oauth-connected-user">Connected</span>
            </div>
            <div class="flex items-center gap-2">
              <button type="button" onclick="loadUserRepos()" class="text-[11px] underline font-bold text-emerald-800">Refresh Repos</button>
              <button type="button" onclick="disconnectGithub()" class="text-[11px] text-red-600 hover:underline">Disconnect</button>
            </div>
          </div>
        </div>

        <!-- PAT SECTION -->
        <div id="gh-pat-box" class="hidden p-4 rounded-xl bg-[#f5f5f7] border border-[#e5e5ea] space-y-3">
          <div class="space-y-1">
            <label class="block text-xs font-semibold text-[#1d1d1f]">Personal Access Token (PAT)</label>
            <div class="flex gap-2">
              <input id="f-pat-token" type="password" placeholder="ghp_••••••••••••••••••••••••••••••••" class="inp flex-1 px-3 py-2 font-mono text-xs"/>
              <button type="button" onclick="verifyPatToken()" class="btn-primary px-3 py-2 text-xs shrink-0">Verify &amp; Load Repos</button>
            </div>
            <p class="text-[11px] text-[#aeaeb2]">Requires <code>repo</code> and <code>read:user</code> permissions. Token is securely hashed with bcrypt upon finalization.</p>
          </div>
          <div id="pat-verified-info" class="hidden p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 font-medium"></div>
        </div>

        <!-- REPO PICKER DROPDOWN (shared between OAuth & PAT) -->
        <div id="repo-picker-container" class="space-y-3">
          <div class="space-y-1.5">
            <div class="flex items-center justify-between">
              <label class="block text-xs font-semibold text-[#1d1d1f]">Select Repository <span class="text-[#0071e3]">*</span></label>
              <span id="repo-loading-spinner" class="hidden text-xs text-[#0071e3] flex items-center gap-1">
                <svg class="spinner w-3 h-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                Fetching from GitHub…
              </span>
            </div>
            <select id="f-repo-select" onchange="onRepoSelectChanged()" class="inp w-full px-3 py-2 text-xs font-mono">
              <option value="">-- Choose from your GitHub repositories --</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1">
              <label class="block text-xs font-semibold text-[#1d1d1f]">Branch <span class="text-[#0071e3]">*</span></label>
              <select id="f-branch-select" class="inp w-full px-3 py-2 text-xs font-mono">
                <option value="main">main</option>
              </select>
            </div>
            <div class="space-y-1">
              <label class="block text-xs font-semibold text-[#1d1d1f]">Token Label (Optional)</label>
              <input id="f-token-label" type="text" placeholder="e.g. dev-access-pat" class="inp w-full px-3 py-2 text-xs"/>
            </div>
          </div>
        </div>

        <!-- MANUAL URL SECTION -->
        <div id="gh-manual-box" class="hidden space-y-3">
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-[#1d1d1f]">Repository URL <span class="text-[#0071e3]">*</span></label>
            <input id="f-manual-url" type="url" placeholder="https://github.com/org/repo" class="inp w-full px-3 py-2.5 font-mono text-xs"/>
          </div>
          <div class="space-y-1.5">
            <label class="block text-xs font-semibold text-[#1d1d1f]">Branch</label>
            <input id="f-manual-branch" type="text" value="main" class="inp w-full px-3 py-2.5 font-mono text-xs"/>
          </div>
        </div>

        <div class="flex justify-end pt-2">
          <button type="button" onclick="setStep(2)" class="btn-primary px-5 py-2 text-xs flex items-center gap-1.5">
            Next: Configure AWS Cloud &rarr;
          </button>
        </div>
      </div>

      <!-- ── STEP 2: AWS CLOUD CONNECTION ── -->
      <div id="step-2-content" class="hidden space-y-4">
        <div class="space-y-2">
          <label class="block text-xs font-semibold text-[#1d1d1f]">AWS Authentication Method</label>
          <div class="grid grid-cols-2 gap-3">
            <button type="button" id="aws-mode-keys" onclick="setAwsMode('ACCESS_KEYS')" class="p-3 rounded-xl border text-xs font-semibold flex items-center gap-2 border-[#ff9900] bg-[#fff7ed] text-[#c2410c]">
              <span class="w-6 h-6 rounded-lg bg-[#ff9900] text-white flex items-center justify-center text-xs font-bold">AK</span>
              <div class="text-left">
                <div>Access Key &amp; Secret Key</div>
                <div class="text-[10px] text-[#9a3412] font-normal">IAM User programmatic keys</div>
              </div>
            </button>
            <button type="button" id="aws-mode-arn" onclick="setAwsMode('IAM_ROLE_ARN')" class="p-3 rounded-xl border text-xs font-semibold flex items-center gap-2 border-[#e5e5ea] bg-white text-[#6e6e73]">
              <span class="w-6 h-6 rounded-lg bg-gray-200 text-gray-700 flex items-center justify-center text-xs font-bold">ARN</span>
              <div class="text-left">
                <div>IAM ARN / User / Role</div>
                <div class="text-[10px] text-[#aeaeb2] font-normal">IAM User ARN, Role ARN, or Account ID</div>
              </div>
            </button>
          </div>
        </div>

        <!-- AWS Region -->
        <div class="space-y-1.5">
          <label class="block text-xs font-semibold text-[#1d1d1f]">AWS Target Region <span class="text-[#0071e3]">*</span></label>
          <select id="f-aws-region" class="inp w-full px-3 py-2 text-xs font-mono">
            <option value="us-east-1">us-east-1 (N. Virginia)</option>
            <option value="us-west-2">us-west-2 (Oregon)</option>
            <option value="ap-south-1" selected>ap-south-1 (Mumbai)</option>
            <option value="eu-west-1">eu-west-1 (Ireland)</option>
            <option value="eu-central-1">eu-central-1 (Frankfurt)</option>
            <option value="ap-southeast-1">ap-southeast-1 (Singapore)</option>
            <option value="ap-northeast-1">ap-northeast-1 (Tokyo)</option>
          </select>
        </div>

        <!-- ACCESS KEYS FORM -->
        <div id="aws-keys-fields" class="space-y-3 p-4 rounded-xl bg-[#f5f5f7] border border-[#e5e5ea]">
          <div class="space-y-1">
            <label class="block text-xs font-semibold text-[#1d1d1f]">AWS Access Key ID <span class="text-[#0071e3]">*</span></label>
            <input id="f-aws-key-id" type="text" placeholder="AKIAIOSFODNN7EXAMPLE" class="inp w-full px-3 py-2 font-mono text-xs"/>
          </div>
          <div class="space-y-1">
            <label class="block text-xs font-semibold text-[#1d1d1f]">AWS Secret Access Key <span class="text-[#0071e3]">*</span></label>
            <input id="f-aws-secret-key" type="password" placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" class="inp w-full px-3 py-2 font-mono text-xs"/>
          </div>
          <div class="space-y-1">
            <label class="block text-xs font-semibold text-[#1d1d1f]">Session Token <span class="text-[#aeaeb2] font-normal">(Optional for temporary STS credentials)</span></label>
            <input id="f-aws-session-token" type="password" placeholder="AQoDYXdzEJr1..." class="inp w-full px-3 py-2 font-mono text-xs"/>
          </div>
        </div>

        <!-- IAM ROLE / USER ARN FORM -->
        <div id="aws-arn-fields" class="hidden space-y-3 p-4 rounded-xl bg-[#f5f5f7] border border-[#e5e5ea]">
          <div class="space-y-1">
            <label class="block text-xs font-semibold text-[#1d1d1f]">IAM ARN (User or Role ARN) <span class="text-[#0071e3]">*</span></label>
            <input id="f-aws-role-arn" type="text" placeholder="arn:aws:iam::123456789012:user/username or arn:aws:iam::123456789012:role/RoleName" class="inp w-full px-3 py-2 font-mono text-xs"/>
            <p class="text-[11px] text-[#86868b] leading-tight">Accepts AWS IAM User ARN (<code>arn:aws:iam::…:user/…</code>), Role ARN (<code>arn:aws:iam::…:role/…</code>), or 12-digit AWS Account ID.</p>
          </div>
          <div class="space-y-1">
            <label class="block text-xs font-semibold text-[#1d1d1f]">External ID <span class="text-[#aeaeb2] font-normal">(Optional cross-account protection)</span></label>
            <input id="f-aws-external-id" type="text" placeholder="e.g. aether-corp-production-env" class="inp w-full px-3 py-2 font-mono text-xs"/>
          </div>
        </div>

        <!-- Live AWS Test Button & Banner -->
        <div class="flex items-center justify-between pt-1">
          <button type="button" onclick="testAwsConnection()" class="py-1.5 px-3 rounded-lg bg-white border border-[#d2d2d7] hover:bg-[#f5f5f7] text-xs font-semibold text-[#1d1d1f] flex items-center gap-1.5 transition">
            <svg class="w-3.5 h-3.5 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            Test AWS Connection (STS)
          </button>
          <div id="aws-test-badge" class="hidden text-xs font-bold px-2.5 py-1 rounded-full"></div>
        </div>

        <div id="aws-test-result" class="hidden p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 space-y-0.5">
          <div class="font-bold flex items-center gap-1"><span>✓</span> AWS STS GetCallerIdentity Verified</div>
          <div id="aws-test-details" class="font-mono text-[11px] text-emerald-700"></div>
        </div>

        <div class="flex justify-between pt-2">
          <button type="button" onclick="setStep(1)" class="btn-ghost px-4 py-2 text-xs">&larr; Back to Source</button>
          <div class="flex gap-2">
            <button type="button" onclick="skipAwsAndFinalize()" class="px-3 py-2 text-xs font-semibold rounded-lg bg-gray-100 hover:bg-gray-200 text-[#1d1d1f] transition">
              Skip AWS (Git Only) &rarr;
            </button>
            <button type="button" onclick="setStep(3)" class="btn-primary px-5 py-2 text-xs flex items-center gap-1.5">
              Next: Review &amp; Finalize &rarr;
            </button>
          </div>
        </div>
      </div>

      <!-- ── STEP 3: REVIEW & FINALIZE ── -->
      <div id="step-3-content" class="hidden space-y-4">
        <div class="p-4 rounded-xl bg-[#f5f5f7] border border-[#e5e5ea] space-y-3">
          <div class="flex items-center justify-between">
            <h4 class="text-xs font-bold uppercase tracking-wider text-[#6e6e73]">Target Environment Assignment</h4>
            <div class="flex items-center gap-1 bg-white p-0.5 rounded-lg border border-[#e5e5ea]">
              <button type="button" id="btn-target-mode-existing" onclick="setTargetMode('EXISTING')" class="px-2.5 py-1 text-[11px] font-semibold rounded-md transition text-[#0071e3] bg-[#e8f1fb]">
                Existing in Module 1
              </button>
              <button type="button" id="btn-target-mode-new" onclick="setTargetMode('NEW')" class="px-2.5 py-1 text-[11px] font-semibold rounded-md transition text-[#6e6e73] hover:text-[#1d1d1f]">
                + Quick Create New
              </button>
            </div>
          </div>

          <!-- Mode A: Existing Project/Environment from Module 1 -->
          <div id="target-mode-existing-box" class="space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1">
                <label class="block text-xs font-semibold text-[#1d1d1f]">Project <span class="text-[#0071e3]">*</span></label>
                <select id="f-final-project" onchange="onProjectSelectChanged()" class="inp w-full px-3 py-2 text-xs font-mono">
                  <option value="">-- Select Project from Module 1 --</option>
                </select>
              </div>
              <div class="space-y-1">
                <label class="block text-xs font-semibold text-[#1d1d1f]">Environment <span class="text-[#0071e3]">*</span></label>
                <select id="f-final-env" onchange="onEnvSelectChanged()" class="inp w-full px-3 py-2 text-xs font-mono">
                  <option value="">-- Select Environment --</option>
                </select>
              </div>
            </div>
            <div class="flex items-center justify-between pt-1 text-[11px] text-[#6e6e73]">
              <div class="flex items-center gap-2">
                <span id="projects-load-status">Loading projects…</span>
                <button type="button" onclick="loadProjectsForSelect()" class="text-[#0071e3] hover:underline font-semibold flex items-center gap-0.5">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                  <span>Refresh</span>
                </button>
              </div>
              <button type="button" onclick="setTargetMode('NEW')" class="text-[#0071e3] hover:underline font-semibold">
                Or create new project &rarr;
              </button>
            </div>
          </div>

          <!-- Mode B: Quick Create New Environment in Module 1 -->
          <div id="target-mode-new-box" class="hidden space-y-3">
            <div class="p-2.5 rounded-lg bg-blue-50/70 border border-blue-200/60 text-[11px] text-[#0071e3] flex items-center justify-between">
              <span>Auto-registers this project and environment into Module 1 project registry.</span>
              <button type="button" onclick="setTargetMode('EXISTING')" class="underline font-semibold text-[#0071e3]">Pick existing instead</button>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1">
                <label class="block text-xs font-semibold text-[#1d1d1f]">Project Name <span class="text-[#0071e3]">*</span></label>
                <input id="f-new-proj-name" type="text" placeholder="e.g. cloud-service-api" class="inp w-full px-3 py-2 text-xs font-mono" oninput="updateReviewSummary()">
              </div>
              <div class="space-y-1">
                <label class="block text-xs font-semibold text-[#1d1d1f]">Project Type</label>
                <select id="f-new-proj-type" class="inp w-full px-3 py-2 text-xs">
                  <option value="web_application" selected>Web Application</option>
                  <option value="api_service">API Service</option>
                  <option value="microservices">Microservices</option>
                  <option value="data_pipeline">Data Pipeline</option>
                  <option value="static_site">Static Site</option>
                  <option value="ml_workload">ML Workload</option>
                </select>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div class="space-y-1">
                <label class="block text-xs font-semibold text-[#1d1d1f]">Environment Name <span class="text-[#0071e3]">*</span></label>
                <input id="f-new-env-name" type="text" placeholder="production" value="production" class="inp w-full px-3 py-2 text-xs font-mono" oninput="updateReviewSummary()">
              </div>
              <div class="space-y-1">
                <label class="block text-xs font-semibold text-[#1d1d1f]">Environment Type</label>
                <select id="f-new-env-type" class="inp w-full px-3 py-2 text-xs">
                  <option value="production" selected>Production</option>
                  <option value="staging">Staging</option>
                  <option value="development">Development</option>
                </select>
              </div>
            </div>
            <div class="text-[11px] text-[#6e6e73] flex items-center justify-between pt-1">
              <span>Target Region: <span id="new-env-region-preview" class="font-mono font-bold text-[#c2410c]">us-east-1</span> (synced from Step 2)</span>
              <span class="text-emerald-700 font-medium">Ready to initialize</span>
            </div>
          </div>
        </div>

        <!-- Summary Card -->
        <div class="card p-4 space-y-3 border-[#bfdbfe] bg-[#f0f7ff]">
          <h4 class="text-xs font-bold text-[#0071e3] uppercase tracking-wider">Connection Summary</h4>
          <div class="grid grid-cols-3 gap-3 text-xs">
            <div class="space-y-1">
              <div class="font-semibold text-[#1d1d1f] flex items-center gap-1">
                <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
                Source Repo
              </div>
              <div id="sum-repo" class="font-mono text-[#0071e3] font-bold truncate">—</div>
              <div id="sum-branch" class="text-[#6e6e73] truncate">Branch: —</div>
            </div>
            <div class="space-y-1">
              <div class="font-semibold text-[#1d1d1f] flex items-center gap-1">
                <span class="w-3.5 h-3.5 rounded bg-[#ff9900] text-white flex items-center justify-center text-[8px] font-bold">AWS</span>
                AWS Target
              </div>
              <div id="sum-aws" class="font-mono text-[#c2410c] font-bold truncate">—</div>
              <div id="sum-region" class="text-[#6e6e73] truncate">Region: —</div>
            </div>
            <div class="space-y-1">
              <div class="font-semibold text-[#1d1d1f] flex items-center gap-1">
                <svg class="w-3.5 h-3.5 text-[#0071e3]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>
                Environment
              </div>
              <div id="sum-target-proj" class="font-mono text-[#1d1d1f] font-bold truncate">—</div>
              <div id="sum-target-env" class="text-[#6e6e73] truncate">Env: —</div>
            </div>
          </div>
        </div>

        <div id="finalize-err" class="hidden p-3 rounded-xl bg-[#fff1f2] border border-[#fecdd3] text-xs text-[#dc2626]"></div>

        <div class="flex justify-between pt-2">
          <button type="button" onclick="setStep(2)" class="btn-ghost px-4 py-2 text-xs">&larr; Back to AWS</button>
          <button type="submit" id="btn-finalize" class="btn-primary px-6 py-2.5 text-sm flex items-center gap-2">
            <svg id="final-spin" class="spinner w-4 h-4 hidden" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
            Finalize &amp; Connect Environment
          </button>
        </div>
      </div>

    </form>
  </div>
</div>

<!-- ── LINK AWS CLOUD MODAL ── -->
<div id="aws-link-modal" class="modal-overlay hidden">
  <div class="bg-white rounded-2xl shadow-apple-lg w-full max-w-lg p-6 space-y-5 my-auto" style="border:1px solid rgba(0,0,0,.08)">
    <div class="flex items-start justify-between border-b border-[#e5e5ea] pb-3">
      <div>
        <h3 class="text-lg font-bold text-[#1d1d1f]">Link AWS Cloud Account</h3>
        <p class="text-xs text-[#6e6e73] mt-0.5">Provide AWS credentials for environment <code id="aws-link-proj-lbl" class="font-mono text-xs font-bold text-[#0071e3]"></code></p>
      </div>
      <button onclick="hideAwsModal()" class="text-[#aeaeb2] hover:text-[#1d1d1f] text-lg font-bold">&times;</button>
    </div>

    <form onsubmit="submitAwsLink(event)" class="space-y-4">
      <input type="hidden" id="aws-link-proj-id">
      <input type="hidden" id="aws-link-env-id">

      <div class="space-y-1.5">
        <label class="block text-xs font-semibold text-[#1d1d1f]">AWS Target Region <span class="text-[#0071e3]">*</span></label>
        <select id="aws-link-region" class="inp w-full px-3 py-2 text-xs font-mono">
          <option value="us-east-1">us-east-1 (N. Virginia)</option>
          <option value="us-west-2">us-west-2 (Oregon)</option>
          <option value="ap-south-1" selected>ap-south-1 (Mumbai)</option>
          <option value="eu-west-1">eu-west-1 (Ireland)</option>
          <option value="eu-central-1">eu-central-1 (Frankfurt)</option>
          <option value="ap-southeast-1">ap-southeast-1 (Singapore)</option>
          <option value="ap-northeast-1">ap-northeast-1 (Tokyo)</option>
        </select>
      </div>

      <div class="space-y-3 p-4 rounded-xl bg-[#f5f5f7] border border-[#e5e5ea]">
        <div class="space-y-1">
          <label class="block text-xs font-semibold text-[#1d1d1f]">AWS Access Key ID <span class="text-[#0071e3]">*</span></label>
          <input id="aws-link-key-id" type="text" required placeholder="AKIAIOSFODNN7EXAMPLE" class="inp w-full px-3 py-2 font-mono text-xs"/>
        </div>
        <div class="space-y-1">
          <label class="block text-xs font-semibold text-[#1d1d1f]">AWS Secret Access Key <span class="text-[#0071e3]">*</span></label>
          <input id="aws-link-secret-key" type="password" required placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" class="inp w-full px-3 py-2 font-mono text-xs"/>
        </div>
      </div>

      <div id="aws-link-err" class="hidden p-2.5 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-800"></div>

      <div class="flex items-center justify-end gap-2 pt-2 border-t border-[#e5e5ea]">
        <button type="button" onclick="hideAwsModal()" class="px-4 py-2 text-xs font-medium rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600">Cancel</button>
        <button type="submit" id="btn-aws-link" class="btn-primary px-5 py-2 text-xs flex items-center gap-1.5">
          <span>Save &amp; Link AWS Account</span>
        </button>
      </div>
    </form>
  </div>
</div>
<!-- ── TOAST ── -->
<div id="toast" class="toast bg-white rounded-2xl shadow-apple-lg px-5 py-3 flex items-center gap-3 border border-[#e5e5ea] text-sm font-medium text-[#1d1d1f]">
  <span id="toast-icon" class="text-base">✅</span>
  <span id="toast-msg"></span>
</div>

<script>
const API = '';
const adminKey = localStorage.getItem('X-Admin-Key') || 'aetherops-secret-admin-key';
let currentGhMode = 'OAUTH';
let currentAwsMode = 'ACCESS_KEYS';
let loadedRepos = [];
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

function logout(){
  fetch(`${API}/api/v1/auth/logout`,{method:'POST',headers:hdrs()});
  window.location.href='/login';
}

function pillClass(status){
  const m={CONNECTED:'pill-connected',PENDING:'pill-pending',FAILED:'pill-failed',DISCONNECTED:'pill-disconnected'};
  return m[status]||'pill-pending';
}

function langIcon(lang){
  const m={Python:'🐍',JavaScript:'🟨',TypeScript:'🔷',Go:'🐹',Java:'☕',Ruby:'💎',PHP:'🐘'};
  return m[lang]||'📦';
}

// ── WIZARD NAVIGATION ────────────────────────────────────────────────────────
function setStep(step){
  [1,2,3].forEach(s=>{
    document.getElementById(`step-${s}-content`).classList.toggle('hidden', s!==step);
    const btn = document.getElementById(`tab-btn-${s}`);
    btn.className = `tab-btn flex items-center gap-1.5 ${s===step?'active':''}`;
  });
  if(step===3){
    autoSuggestProjectName();
    const reg = document.getElementById('f-aws-region').value || 'us-east-1';
    const regPrev = document.getElementById('new-env-region-preview');
    if(regPrev) regPrev.textContent = reg;
    updateReviewSummary();
  }
}

function setTargetMode(mode){
  currentTargetMode = mode;
  const isExist = mode === 'EXISTING';
  const existBox = document.getElementById('target-mode-existing-box');
  const newBox = document.getElementById('target-mode-new-box');
  if(existBox) existBox.classList.toggle('hidden', !isExist);
  if(newBox) newBox.classList.toggle('hidden', isExist);

  const btnEx = document.getElementById('btn-target-mode-existing');
  const btnNew = document.getElementById('btn-target-mode-new');
  if(btnEx && btnNew){
    btnEx.className = `px-2.5 py-1 text-[11px] font-semibold rounded-md transition ${isExist ? 'text-[#0071e3] bg-[#e8f1fb]' : 'text-[#6e6e73] hover:text-[#1d1d1f]'}`;
    btnNew.className = `px-2.5 py-1 text-[11px] font-semibold rounded-md transition ${!isExist ? 'text-[#0071e3] bg-[#e8f1fb]' : 'text-[#6e6e73] hover:text-[#1d1d1f]'}`;
  }
  if(!isExist) autoSuggestProjectName();
  updateReviewSummary();
}

function autoSuggestProjectName(){
  const pInput = document.getElementById('f-new-proj-name');
  if(!pInput || pInput.value.trim()) return;
  let repoUrl = '';
  if(currentGhMode==='MANUAL'){
    repoUrl = document.getElementById('f-manual-url').value.trim();
  } else {
    repoUrl = document.getElementById('f-repo-select').value;
  }
  if(repoUrl){
    const parts = repoUrl.split('/').filter(Boolean);
    const rawName = parts[parts.length - 1] || '';
    const clean = rawName.replace(/\.git$/, '').toLowerCase().replace(/[^a-z0-9_-]/g, '-');
    if(clean) pInput.value = clean;
  }
}

function setGhMode(mode){
  currentGhMode = mode;
  ['oauth','pat','manual'].forEach(m=>{
    const btn = document.getElementById(`gh-mode-${m}`);
    const isAct = m.toUpperCase()===mode;
    btn.className = `p-2.5 rounded-xl border text-xs font-semibold flex flex-col items-center gap-1 ${isAct?'border-[#0071e3] bg-[#e8f1fb] text-[#0071e3]':'border-[#e5e5ea] bg-white text-[#6e6e73]'}`;
  });
  document.getElementById('gh-oauth-box').classList.toggle('hidden', mode!=='OAUTH');
  document.getElementById('gh-pat-box').classList.toggle('hidden', mode!=='PAT');
  document.getElementById('repo-picker-container').classList.toggle('hidden', mode==='MANUAL');
  document.getElementById('gh-manual-box').classList.toggle('hidden', mode!=='MANUAL');
}

function setAwsMode(mode){
  currentAwsMode = mode;
  const isKey = mode==='ACCESS_KEYS';
  document.getElementById('aws-mode-keys').className = `p-3 rounded-xl border text-xs font-semibold flex items-center gap-2 ${isKey?'border-[#ff9900] bg-[#fff7ed] text-[#c2410c]':'border-[#e5e5ea] bg-white text-[#6e6e73]'}`;
  document.getElementById('aws-mode-arn').className = `p-3 rounded-xl border text-xs font-semibold flex items-center gap-2 ${!isKey?'border-[#ff9900] bg-[#fff7ed] text-[#c2410c]':'border-[#e5e5ea] bg-white text-[#6e6e73]'}`;
  document.getElementById('aws-keys-fields').classList.toggle('hidden', !isKey);
  document.getElementById('aws-arn-fields').classList.toggle('hidden', isKey);
}

// ── GITHUB OAUTH & CONFIG ────────────────────────────────────────────────────
async function checkOAuthConfig(){
  try{
    const res = await fetch(`${API}/api/v1/auth/github/config`, {headers:hdrs()});
    if(!res.ok) return;
    const data = await res.json();
    isOAuthConfigured = Boolean(data.is_configured);
    const badge = document.getElementById('oauth-status-badge');
    const unconfigured = document.getElementById('oauth-unconfigured-panel');
    const actionsRow = document.getElementById('oauth-actions-row');
    document.getElementById('cfg-cb-url').value = data.callback_url_hint;
    if(data.client_id) document.getElementById('cfg-client-id').value = data.client_id;

    if(isOAuthConfigured){
      badge.textContent = 'OAuth Ready ✓';
      badge.className = 'text-[11px] px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-bold border border-emerald-200';
      unconfigured.classList.add('hidden');
      actionsRow.classList.remove('hidden');
    } else {
      badge.textContent = 'Setup Required';
      badge.className = 'text-[11px] px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 font-bold border border-amber-200';
      if(!currentGhToken){
        unconfigured.classList.remove('hidden');
        actionsRow.classList.add('hidden');
      }
    }
  }catch(e){
    console.warn('checkOAuthConfig error:', e);
  }
}

function toggleOAuthConfigForm(){
  const f = document.getElementById('oauth-config-form');
  f.classList.toggle('hidden');
}

function copyCallbackUrl(){
  const el = document.getElementById('cfg-cb-url');
  navigator.clipboard.writeText(el.value).then(()=>{
    toast('Callback URL copied to clipboard!', true);
  }).catch(()=>{
    el.select();
    document.execCommand('copy');
    toast('Copied!', true);
  });
}

async function saveOAuthConfig(){
  const cid = document.getElementById('cfg-client-id').value.trim();
  const csec = document.getElementById('cfg-client-secret').value.trim();
  const cb = document.getElementById('cfg-cb-url').value.trim();
  if(!cid || !csec){ toast('Please provide both Client ID and Client Secret', false); return; }

  try{
    const res = await fetch(`${API}/api/v1/auth/github/config`, {
      method:'POST', headers:hdrs(),
      body:JSON.stringify({client_id:cid, client_secret:csec, redirect_uri:cb})
    });
    const data = await res.json();
    if(!res.ok) throw new Error(data.detail||'Failed to save config');
    toast('GitHub OAuth App activated!', true);
    toggleOAuthConfigForm();
    await checkOAuthConfig();
  }catch(e){ toast(e.message, false); }
}

async function startGithubOAuth(){
  if(!isOAuthConfigured){
    toggleOAuthConfigForm();
    toast('Please enter your GitHub OAuth App Client ID & Secret first, or use PAT token.', false);
    return;
  }

  // Open in popup window
  const popup = window.open('/api/v1/auth/github/login?popup=1', 'github_oauth', 'width=620,height=750,status=no,resizable=yes');
  if(!popup || popup.closed || typeof popup.closed==='undefined'){
    // Popup was blocked, fallback to redirect
    window.location.href = '/api/v1/auth/github/login';
  }
}

// Window message listener for popup callback
window.addEventListener('message', async (e)=>{
  if(e.data && e.data.type === 'GITHUB_OAUTH_SUCCESS'){
    currentGhToken = e.data.token;
    currentGhUser = e.data.user?.login || 'developer';
    localStorage.setItem('X-GH-Token', currentGhToken);
    localStorage.setItem('X-GH-User', currentGhUser);
    onGithubConnected(e.data.user);
    toast(`GitHub connected as @${currentGhUser}!`, true);
    await loadUserRepos();
  } else if(e.data && e.data.type === 'GITHUB_OAUTH_ERROR'){
    toast(e.data.error || 'Authorization cancelled', false);
  }
});

function onGithubConnected(user){
  const login = user?.login || currentGhUser || 'developer';
  document.getElementById('oauth-connected-info').classList.remove('hidden');
  document.getElementById('oauth-connected-user').textContent = `Connected as @${login}`;
  document.getElementById('oauth-actions-row').classList.add('hidden');
  document.getElementById('oauth-unconfigured-panel').classList.add('hidden');
}

function disconnectGithub(){
  currentGhToken = '';
  currentGhUser = '';
  localStorage.removeItem('X-GH-Token');
  localStorage.removeItem('X-GH-User');
  document.getElementById('oauth-connected-info').classList.add('hidden');
  document.getElementById('oauth-actions-row').classList.remove('hidden');
  document.getElementById('f-repo-select').innerHTML = '<option value="">-- Choose from your GitHub repositories --</option>';
  toast('GitHub disconnected');
  checkOAuthConfig();
}

async function connectMockOAuth(){
  try{
    const res = await fetch(`${API}/api/v1/auth/github/mock`, {method:'POST',headers:hdrs()});
    const data = await res.json();
    if(data.access_token){
      currentGhToken = data.access_token;
      currentGhUser = data.user?.login || 'aether-developer';
      localStorage.setItem('X-GH-Token', currentGhToken);
      localStorage.setItem('X-GH-User', currentGhUser);
      onGithubConnected(data.user);
      toast('Connected to GitHub (Demo Mode)!', true);
      await loadUserRepos();
    }
  }catch(e){
    toast('Demo OAuth error: '+e.message, false);
  }
}

async function verifyPatToken(){
  const pat = document.getElementById('f-pat-token').value.trim();
  if(!pat){ toast('Please input a Personal Access Token', false); return; }
  try{
    const res = await fetch(`${API}/api/v1/github/verify-pat`, {
      method:'POST', headers:hdrs(), body:JSON.stringify({pat_token: pat})
    });
    const data = await res.json();
    if(!res.ok) throw new Error(data.detail||'Verification failed');
    currentGhToken = pat;
    currentGhUser = data.username;
    localStorage.setItem('X-GH-Token', pat);
    localStorage.setItem('X-GH-User', data.username);
    const box = document.getElementById('pat-verified-info');
    box.classList.remove('hidden');
    box.textContent = `✓ Token Verified for user @${data.username} (Scopes: ${data.scopes||'repo'})`;
    toast(`Token valid! Welcome, @${data.username}`, true);
    await loadUserRepos();
  }catch(e){
    toast(e.message, false);
  }
}

async function loadUserRepos(){
  const spin = document.getElementById('repo-loading-spinner');
  spin.classList.remove('hidden');
  try{
    const res = await fetch(`${API}/api/v1/github/repos`, {headers:hdrs()});
    const data = await res.json();
    loadedRepos = data.repos||[];
    const sel = document.getElementById('f-repo-select');
    sel.innerHTML = '<option value="">-- Choose from your GitHub repositories --</option>';
    loadedRepos.forEach(r=>{
      sel.innerHTML += `<option value="${r.html_url}" data-name="${r.name}" data-branch="${r.default_branch}">${r.full_name} (${r.language||'Code'})</option>`;
    });
    if(loadedRepos.length>0){
      sel.selectedIndex = 1;
      onRepoSelectChanged();
    }
  }catch(e){
    console.warn('Failed to load repos:', e);
  }finally{
    spin.classList.add('hidden');
  }
}

async function onRepoSelectChanged(){
  const sel = document.getElementById('f-repo-select');
  const opt = sel.options[sel.selectedIndex];
  if(!opt||!opt.value) return;
  const defBranch = opt.getAttribute('data-branch') || 'main';
  const bSel = document.getElementById('f-branch-select');
  bSel.innerHTML = `<option value="${defBranch}" selected>${defBranch}</option>`;

  // Try fetching real branches for this repo
  const parts = opt.value.split('/').filter(Boolean);
  if(parts.length>=2){
    const owner = parts[parts.length-2];
    const repo = parts[parts.length-1].replace(/\.git$/,'');
    try{
      const res = await fetch(`${API}/api/v1/github/repos/${owner}/${repo}/branches`, {headers:hdrs()});
      if(res.ok){
        const bData = await res.json();
        if(bData.branches && bData.branches.length>0){
          bSel.innerHTML = '';
          bData.branches.forEach(b=>{
            const isSel = b === defBranch ? 'selected' : '';
            bSel.innerHTML += `<option value="${b}" ${isSel}>${b}</option>`;
          });
        }
      }
    }catch(e){}
  }
}

// ── AWS ACTIONS ─────────────────────────────────────────────────────────────
async function testAwsConnection(){
  const region = document.getElementById('f-aws-region').value;
  const badge = document.getElementById('aws-test-badge');
  const resBox = document.getElementById('aws-test-result');
  const dBox = document.getElementById('aws-test-details');
  badge.classList.remove('hidden');
  badge.className = 'text-xs font-bold px-2.5 py-1 rounded-full bg-blue-50 text-[#0071e3] border border-blue-200';
  badge.textContent = 'Verifying STS…';

  let keyInput = document.getElementById('f-aws-key-id').value.trim();
  let arnInput = document.getElementById('f-aws-role-arn').value.trim();

  // Smart detect: if user typed an ARN in the access key input, switch to ARN mode
  if(currentAwsMode==='ACCESS_KEYS' && keyInput.startsWith('arn:')){
    setAwsMode('IAM_ROLE_ARN');
    document.getElementById('f-aws-role-arn').value = keyInput;
    arnInput = keyInput;
  }

  let payload = {auth_type: currentAwsMode, aws_region: region};
  if(currentAwsMode==='ACCESS_KEYS'){
    if(!keyInput || !document.getElementById('f-aws-secret-key').value.trim()){
      throw new Error("Please enter both AWS Access Key ID and Secret Access Key to test.");
    }
    payload.access_key_id = keyInput;
    payload.secret_access_key = document.getElementById('f-aws-secret-key').value.trim();
    payload.session_token = document.getElementById('f-aws-session-token').value.trim() || null;
  } else {
    if(!arnInput){
      throw new Error("Please enter an IAM Role ARN to test.");
    }
    payload.role_arn = arnInput;
    payload.external_id = document.getElementById('f-aws-external-id').value.trim() || null;
  }

  try{
    const res = await fetch(`${API}/api/v1/cloud/aws/validate`, {
      method:'POST', headers:hdrs(), body:JSON.stringify(payload)
    });
    const data = await res.json();
    if(!res.ok) throw new Error(data.detail||'AWS verification failed');
    verifiedAwsIdentity = data;
    badge.className = 'text-xs font-bold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200';
    badge.textContent = 'Verified ✓';
    resBox.classList.remove('hidden');
    const typeLabel = (data.resource_type || data.auth_type).toUpperCase();
    dBox.innerHTML = `Account ID: <strong>${data.account_id}</strong> · Type: <span class="font-bold text-[#c2410c]">${typeLabel}</span><br>Identity: <code>${data.arn}</code> (${data.region})`;
    toast(`AWS Identity verified! Account: ${data.account_id}`, true);
  }catch(e){
    badge.className = 'text-xs font-bold px-2.5 py-1 rounded-full bg-rose-50 text-rose-700 border border-rose-200';
    badge.textContent = 'Failed ✗';
    resBox.classList.add('hidden');
    toast(e.message, false);
  }
}

// ── SUMMARY & FINALIZE ───────────────────────────────────────────────────────
let module1Projects = [];

async function loadProjectsForSelect(preselectedProjectId = '', preselectedEnvId = ''){
  const selProj = document.getElementById('f-final-project');
  const statusEl = document.getElementById('projects-load-status');
  if(!selProj) return;
  if(statusEl) statusEl.textContent = 'Loading projects…';

  try {
    const res = await fetch(`${API}/api/v1/projects`, {headers: hdrs()});
    if(!res.ok) throw new Error('Failed to load projects');
    const data = await res.json();
    module1Projects = data.projects || [];

    selProj.innerHTML = '<option value="">-- Select Project from Module 1 --</option>';
    if(module1Projects.length === 0){
      selProj.innerHTML = '<option value="">No projects in Module 1 yet</option>';
      if(statusEl) statusEl.textContent = '0 projects found — switched to Quick Create';
      setTargetMode('NEW');
      return;
    }

    module1Projects.forEach(p => {
      selProj.innerHTML += `<option value="${p.id}">${p.name} (${p.id.slice(0, 8)}…)</option>`;
    });

    if(statusEl) statusEl.textContent = `${module1Projects.length} project(s) ready`;

    if(preselectedProjectId){
      selProj.value = preselectedProjectId;
      setTargetMode('EXISTING');
      await onProjectSelectChanged(preselectedEnvId);
    } else if(module1Projects.length >= 1 && currentTargetMode === 'EXISTING'){
      selProj.selectedIndex = 1;
      await onProjectSelectChanged(preselectedEnvId);
    }
  } catch(e) {
    if(statusEl) statusEl.textContent = 'Module 1 offline / error';
    console.warn('loadProjectsForSelect error:', e);
    setTargetMode('NEW');
  }
}

async function onProjectSelectChanged(preselectedEnvId = ''){
  const selProj = document.getElementById('f-final-project');
  const selEnv  = document.getElementById('f-final-env');
  const projId  = selProj ? selProj.value : '';
  if(!selEnv) return;

  selEnv.innerHTML = '<option value="">-- Select Environment --</option>';
  if(!projId) return;

  try {
    const res = await fetch(`${API}/api/v1/projects/${projId}/environments`, {headers: hdrs()});
    if(!res.ok) throw new Error('Failed to load environments');
    const data = await res.json();
    const envs = data.environments || [];

    if(envs.length === 0){
      selEnv.innerHTML = '<option value="">No environments in this project (Use Quick Create)</option>';
      return;
    }

    envs.forEach(e => {
      selEnv.innerHTML += `<option value="${e.id}" data-region="${e.aws_region}">${e.name} (${e.env_type} - ${e.aws_region})</option>`;
    });

    if(preselectedEnvId){
      selEnv.value = preselectedEnvId;
      onEnvSelectChanged();
    } else if(envs.length >= 1){
      selEnv.selectedIndex = 1;
      onEnvSelectChanged();
    }
  } catch(e) {
    console.warn('onProjectSelectChanged error:', e);
  }
}

function onEnvSelectChanged(){
  const selEnv = document.getElementById('f-final-env');
  if(!selEnv) return;
  const opt = selEnv.options[selEnv.selectedIndex];
  if(opt){
    const reg = opt.getAttribute('data-region');
    if(reg){
      const regSel = document.getElementById('f-aws-region');
      if(regSel) regSel.value = reg;
    }
  }
  updateReviewSummary();
}

function updateReviewSummary(){
  let repoUrl = '';
  let branch = 'main';
  if(currentGhMode==='MANUAL'){
    repoUrl = document.getElementById('f-manual-url').value.trim();
    branch = document.getElementById('f-manual-branch').value.trim() || 'main';
  } else {
    repoUrl = document.getElementById('f-repo-select').value;
    branch = document.getElementById('f-branch-select').value || 'main';
  }
  const repoName = repoUrl ? (repoUrl.split('/').filter(Boolean).slice(-2).join('/') || repoUrl) : '—';
  const elRepo = document.getElementById('sum-repo');
  const elBranch = document.getElementById('sum-branch');
  if(elRepo) elRepo.textContent = repoName;
  if(elBranch) elBranch.textContent = `Branch: ${branch}`;

  const region = document.getElementById('f-aws-region').value;
  const accId = verifiedAwsIdentity ? verifiedAwsIdentity.account_id : (document.getElementById('f-aws-key-id').value.trim() || 'Unverified');
  const elAws = document.getElementById('sum-aws');
  const elReg = document.getElementById('sum-region');
  if(elAws) elAws.textContent = `Account: ${accId}`;
  if(elReg) elReg.textContent = `Region: ${region}`;

  // Target Env Summary
  const sumProj = document.getElementById('sum-target-proj');
  const sumEnv = document.getElementById('sum-target-env');
  if(sumProj && sumEnv){
    if(currentTargetMode === 'EXISTING'){
      const selProj = document.getElementById('f-final-project');
      const selEnv = document.getElementById('f-final-env');
      const pText = selProj && selProj.selectedIndex >= 0 ? (selProj.options[selProj.selectedIndex]?.text || '—') : '—';
      const eText = selEnv && selEnv.selectedIndex >= 0 ? (selEnv.options[selEnv.selectedIndex]?.text || '—') : '—';
      sumProj.textContent = (selProj && selProj.value) ? pText.split(' (')[0] : 'Not Selected';
      sumEnv.textContent = (selEnv && selEnv.value) ? `Env: ${eText.split(' (')[0]}` : 'Env: Not Selected';
    } else {
      const pName = document.getElementById('f-new-proj-name').value.trim() || 'New Project';
      const eName = document.getElementById('f-new-env-name').value.trim() || 'production';
      sumProj.textContent = pName;
      sumEnv.textContent = `Env: ${eName} (${region})`;
    }
  }
}

async function submitUnifiedConnect(e){
  e.preventDefault();
  const errEl = document.getElementById('finalize-err');
  const btn = document.getElementById('btn-finalize');
  const spin = document.getElementById('final-spin');
  errEl.classList.add('hidden');

  let repoUrl = '';
  let branch = 'main';
  let patToken = null;
  let patLabel = null;

  if(currentGhMode==='MANUAL'){
    repoUrl = document.getElementById('f-manual-url').value.trim();
    branch = document.getElementById('f-manual-branch').value.trim() || 'main';
  } else {
    repoUrl = document.getElementById('f-repo-select').value;
    branch = document.getElementById('f-branch-select').value || 'main';
    patLabel = document.getElementById('f-token-label').value.trim() || null;
    patToken = currentGhToken || document.getElementById('f-pat-token').value.trim() || null;
  }

  if(!repoUrl){
    errEl.textContent = 'Please select or enter a repository URL in Step 1.';
    errEl.classList.remove('hidden');
    setStep(1);
    toast('Please select or enter a repository URL', false);
    return;
  }

  let proj = '';
  let env  = '';

  if(currentTargetMode === 'EXISTING'){
    proj = document.getElementById('f-final-project').value.trim();
    env  = document.getElementById('f-final-env').value.trim();
    if(!proj || !env){
      errEl.textContent = 'Please choose a Target Project and Environment, or click "+ Quick Create New" to create one.';
      errEl.classList.remove('hidden');
      toast('Please assign a Target Project and Environment', false);
      return;
    }
  } else {
    const projName = document.getElementById('f-new-proj-name').value.trim();
    const envName  = document.getElementById('f-new-env-name').value.trim() || 'production';
    const projType = document.getElementById('f-new-proj-type').value || 'web_application';
    const envType  = document.getElementById('f-new-env-type').value || 'production';

    if(!projName){
      errEl.textContent = 'Please enter a Project Name.';
      errEl.classList.remove('hidden');
      toast('Please enter a Project Name', false);
      return;
    }

    try{
      let createdProjId = '';
      const pRes = await fetch(`${API}/api/v1/projects`, {
        method: 'POST',
        headers: hdrs(),
        body: JSON.stringify({
          name: projName,
          description: `Created via Source Connection Wizard for ${repoUrl}`,
          project_type: projType
        })
      });

      if(pRes.ok){
        const pData = await pRes.json();
        createdProjId = pData.id;
      } else {
        createdProjId = 'proj-' + projName.toLowerCase().replace(/[^a-z0-9_-]/g, '-').slice(0, 30);
      }

      let createdEnvId = '';
      const region = document.getElementById('f-aws-region').value;
      const eRes = await fetch(`${API}/api/v1/projects/${createdProjId}/environments`, {
        method: 'POST',
        headers: hdrs(),
        body: JSON.stringify({
          name: envName,
          env_type: envType,
          aws_region: region,
          description: `${envName} deployment environment`
        })
      });

      if(eRes.ok){
        const eData = await eRes.json();
        createdEnvId = eData.id;
      } else {
        createdEnvId = 'env-' + envName.toLowerCase().replace(/[^a-z0-9_-]/g, '-').slice(0, 30);
      }

      proj = createdProjId;
      env = createdEnvId;
    }catch(err){
      proj = 'proj-' + projName.toLowerCase().replace(/[^a-z0-9_-]/g, '-').slice(0, 30);
      env = 'env-' + envName.toLowerCase().replace(/[^a-z0-9_-]/g, '-').slice(0, 30);
    }
  }

  btn.disabled = true; spin.classList.remove('hidden');

  // If Git Only mode, submit ONLY Git connection (zero AWS credentials, zero mock keys)
  if(currentConnectionMode === 'GIT_ONLY'){
    try{
      const res = await fetch(`${API}/api/v1/connections`, {
        method: 'POST',
        headers: hdrs(),
        body: JSON.stringify({
          project_id: proj,
          environment_id: env,
          repo_url: repoUrl,
          branch: branch,
          auth_type: currentGhMode,
          pat_token: patToken,
          pat_label: patLabel,
          github_user: currentGhUser || 'developer'
        })
      });
      const data = await res.json();
      if(!res.ok) throw new Error(data.detail || JSON.stringify(data));
      hideConnectModal();
      toast(`Git repository connected successfully (${data.repo_name})!`, true);
      await loadConnections();
    }catch(err){
      errEl.textContent = err.message;
      errEl.classList.remove('hidden');
    }finally{
      btn.disabled = false; spin.classList.add('hidden');
    }
    return;
  }
    branch = document.getElementById('f-manual-branch').value.trim() || 'main';
  } else {
    repoUrl = document.getElementById('f-repo-select').value;
    branch = document.getElementById('f-branch-select').value || 'main';
    patLabel = document.getElementById('f-token-label').value.trim() || null;
    patToken = currentGhToken || document.getElementById('f-pat-token').value.trim() || null;
  }

  if(!repoUrl){
    errEl.textContent = 'Please select or enter a repository URL in Step 1.';
    errEl.classList.remove('hidden');
    setStep(1);
    toast('Please select or enter a repository URL', false);
    return;
  }

  const region = document.getElementById('f-aws-region').value;
  let awsKeyId = null, awsSecret = null, sessionTok = null, roleArn = null, extId = null;

  if(currentAwsMode==='ACCESS_KEYS'){
    let keyInput = document.getElementById('f-aws-key-id').value.trim();
    if(keyInput.startsWith('arn:')){
      currentAwsMode = 'IAM_ROLE_ARN';
      roleArn = keyInput;
    } else {
      awsKeyId = keyInput;
      awsSecret = document.getElementById('f-aws-secret-key').value.trim();
      sessionTok = document.getElementById('f-aws-session-token').value.trim() || null;
    }
  }
  if(currentAwsMode==='IAM_ROLE_ARN'){
    roleArn = document.getElementById('f-aws-role-arn').value.trim() || roleArn;
    extId = document.getElementById('f-aws-external-id').value.trim() || null;
  }

  let proj = '';
  let env  = '';

  btn.disabled = true; spin.classList.remove('hidden');

  if(currentTargetMode === 'EXISTING'){
    proj = document.getElementById('f-final-project').value.trim();
    env  = document.getElementById('f-final-env').value.trim();
    if(!proj || !env){
      btn.disabled = false; spin.classList.add('hidden');
      errEl.textContent = 'Please choose a Target Project and Environment, or click "+ Quick Create New" to create one.';
      errEl.classList.remove('hidden');
      toast('Please assign a Target Project and Environment', false);
      return;
    }
  } else {
    // Mode B: Quick Create in Module 1
    const projName = document.getElementById('f-new-proj-name').value.trim();
    const envName  = document.getElementById('f-new-env-name').value.trim() || 'production';
    const projType = document.getElementById('f-new-proj-type').value || 'web_application';
    const envType  = document.getElementById('f-new-env-type').value || 'production';

    if(!projName){
      btn.disabled = false; spin.classList.add('hidden');
      errEl.textContent = 'Please enter a Project Name.';
      errEl.classList.remove('hidden');
      toast('Please enter a Project Name', false);
      return;
    }

    try{
      // 1. Create project in Module 1 via bridge
      let createdProjId = '';
      const pRes = await fetch(`${API}/api/v1/projects`, {
        method: 'POST',
        headers: hdrs(),
        body: JSON.stringify({
          name: projName,
          description: `Created via Source Connection Wizard for ${repoUrl}`,
          project_type: projType
        })
      });

      if(pRes.ok){
        const pData = await pRes.json();
        createdProjId = pData.id;
      } else {
        const pErr = await pRes.json().catch(()=>({}));
        console.warn('Project creation note:', pErr);
        createdProjId = 'proj-' + projName.toLowerCase().replace(/[^a-z0-9_-]/g, '-').slice(0, 30);
      }

      // 2. Create environment under this project in Module 1 via bridge
      let createdEnvId = '';
      const eRes = await fetch(`${API}/api/v1/projects/${createdProjId}/environments`, {
        method: 'POST',
        headers: hdrs(),
        body: JSON.stringify({
          name: envName,
          env_type: envType,
          aws_region: region,
          description: `${envName} deployment environment`
        })
      });

      if(eRes.ok){
        const eData = await eRes.json();
        createdEnvId = eData.id;
      } else {
        const eErr = await eRes.json().catch(()=>({}));
        console.warn('Environment creation note:', eErr);
        createdEnvId = 'env-' + envName.toLowerCase().replace(/[^a-z0-9_-]/g, '-').slice(0, 30);
      }

      proj = createdProjId;
      env = createdEnvId;
    }catch(err){
      console.warn('Auto-provisioning fallback:', err);
      proj = 'proj-' + projName.toLowerCase().replace(/[^a-z0-9_-]/g, '-').slice(0, 30);
      env = 'env-' + envName.toLowerCase().replace(/[^a-z0-9_-]/g, '-').slice(0, 30);
    }
  }

  const payload = {
    project_id: proj,
    environment_id: env,
    repo_url: repoUrl,
    branch: branch,
    git_auth_type: currentGhMode,
    pat_token: patToken,
    pat_label: patLabel,
    github_user: currentGhUser || 'developer',
    cloud_provider: 'AWS',
    cloud_auth_type: currentAwsMode,
    aws_region: region,
    access_key_id: awsKeyId,
    secret_access_key: awsSecret,
    session_token: sessionTok,
    role_arn: roleArn,
    external_id: extId
  };

  try{
    const res = await fetch(`${API}/api/v1/connections/finalize`, {
      method:'POST', headers:hdrs(), body:JSON.stringify(payload)
    });
    const data = await res.json();
    if(!res.ok) throw new Error(data.detail||JSON.stringify(data));
    hideConnectModal();
    toast(`Environment connected to ${data.git_connection.repo_name}!`, true);
    await loadConnections();
  }catch(err){
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  }finally{
    btn.disabled = false; spin.classList.add('hidden');
  }
}

function showConnectModal(preselectedProj = '', preselectedEnv = ''){
  document.getElementById('connect-modal').classList.remove('hidden');
  setStep(1);
  checkOAuthConfig();
  loadProjectsForSelect(preselectedProj, preselectedEnv);
  if(currentGhToken){
    onGithubConnected({login: currentGhUser});
    loadUserRepos();
  }
}

function skipAwsAndFinalize(){
  document.getElementById('f-aws-key-id').value = '';
  document.getElementById('f-aws-secret-key').value = '';
  document.getElementById('f-aws-session-token').value = '';
  document.getElementById('f-aws-role-arn').value = '';
  document.getElementById('f-aws-external-id').value = '';
  setStep(3);
}

function hideConnectModal(){
  document.getElementById('connect-modal').classList.add('hidden');
}

function openAwsModal(projId, envId, region){
  document.getElementById('aws-link-proj-id').value = projId;
  document.getElementById('aws-link-env-id').value = envId;
  document.getElementById('aws-link-proj-lbl').textContent = envId;
  if(region) document.getElementById('aws-link-region').value = region;
  document.getElementById('aws-link-key-id').value = '';
  document.getElementById('aws-link-secret-key').value = '';
  document.getElementById('aws-link-err').classList.add('hidden');
  document.getElementById('aws-link-modal').classList.remove('hidden');
}

function hideAwsModal(){
  document.getElementById('aws-link-modal').classList.add('hidden');
}

async function submitAwsLink(e){
  e.preventDefault();
  const projId = document.getElementById('aws-link-proj-id').value;
  const envId = document.getElementById('aws-link-env-id').value;
  const region = document.getElementById('aws-link-region').value;
  const keyId = document.getElementById('aws-link-key-id').value.trim();
  const secret = document.getElementById('aws-link-secret-key').value.trim();
  const errEl = document.getElementById('aws-link-err');
  const btn = document.getElementById('btn-aws-link');
  errEl.classList.add('hidden');

  if(!keyId || !secret){
    errEl.textContent = 'Please enter both Access Key ID and Secret Access Key.';
    errEl.classList.remove('hidden');
    return;
  }

  btn.disabled = true;
  try {
    const res = await fetch(`${API}/api/v1/cloud/connections`, {
      method: 'POST',
      headers: hdrs(),
      body: JSON.stringify({
        project_id: projId,
        environment_id: envId,
        auth_type: 'ACCESS_KEYS',
        aws_region: region,
        access_key_id: keyId,
        secret_access_key: secret
      })
    });
    const data = await res.json();
    if(!res.ok) throw new Error(data.detail || JSON.stringify(data));
    hideAwsModal();
    toast(`AWS account linked successfully! (${data.account_id})`, true);
    await loadConnections();
  } catch(err){
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  } finally {
    btn.disabled = false;
  }
}
// ── DASHBOARD RENDERING ─────────────────────────────────────────────────────
async function loadConnections(){
  try{
    const [gitRes, cloudRes] = await Promise.all([
      fetch(`${API}/api/v1/connections`,{headers:hdrs()}),
      fetch(`${API}/api/v1/cloud/connections`,{headers:hdrs()})
    ]);
    if(gitRes.status===401||cloudRes.status===401){ window.location.href='/login'; return; }
    const gitData = await gitRes.json();
    const cloudData = await cloudRes.json();
    renderDashboard(gitData.connections||[], cloudData.connections||[]);
  } catch(e){
    document.getElementById('loading').innerHTML=`<p class="text-sm text-[#dc2626]">${e.message}</p>`;
  }
}

function renderDashboard(gitConns, cloudConns){
  document.getElementById('loading').classList.add('hidden');

  const cloudMap = {};
  cloudConns.forEach(c=>{ cloudMap[c.environment_id] = c; });

  const gitConnected = gitConns.filter(c=>c.status==='CONNECTED').length;
  const awsConnected = cloudConns.filter(c=>c.status==='CONNECTED').length;
  const repos = new Set(gitConns.map(c=>c.repo_name)).size;

  document.getElementById('stat-total').textContent = gitConns.length;
  document.getElementById('stat-git-connected').textContent = gitConnected;
  document.getElementById('stat-aws-connected').textContent = awsConnected;
  document.getElementById('stat-repos').textContent = repos;

  if(gitConns.length===0){
    document.getElementById('empty').classList.remove('hidden');
    document.getElementById('connections-grid').classList.add('hidden');
    return;
  }
  document.getElementById('empty').classList.add('hidden');
  const grid = document.getElementById('connections-grid');
  grid.classList.remove('hidden');
  grid.innerHTML='';

  gitConns.forEach(c=>{
    const cloud = cloudMap[c.environment_id];
    const pill = pillClass(c.status);
    const lang = c.language||'Unknown';
    const icon = langIcon(lang);
    const sha  = c.last_commit_sha ? c.last_commit_sha.slice(0,7) : null;
    const msg  = c.last_commit_msg ? (c.last_commit_msg.length>55?c.last_commit_msg.slice(0,55)+'…':c.last_commit_msg) : null;

    const m3Url = `http://localhost:8001/app?project_id=${encodeURIComponent(c.project_id)}&environment_id=${encodeURIComponent(c.environment_id)}&repo_url=${encodeURIComponent(c.repo_url)}&branch=${encodeURIComponent(c.branch)}&repo_name=${encodeURIComponent(c.repo_name)}`;
    const m1Url = `http://localhost:8009/app/projects/${encodeURIComponent(c.project_id)}`;

    grid.innerHTML+=`
    <div class="card cursor-pointer p-5 space-y-4 group" onclick="openConnection('${c.id}')">
      <!-- Header -->
      <div class="flex items-start justify-between gap-2">
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-[#1d1d1f] to-[#424245] flex items-center justify-center text-xl shrink-0">
            <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
          </div>
          <div class="min-w-0">
            <div class="font-semibold text-[#1d1d1f] text-sm truncate">${escHtml(c.repo_name)}</div>
            <div class="text-xs text-[#6e6e73] font-mono flex items-center gap-1.5">
              <span>${c.branch}</span>
              <span class="text-[10px] px-1.5 py-0.2 rounded bg-gray-100 text-gray-600">${c.auth_type||'PAT'}</span>
            </div>
          </div>
        </div>
        <span class="px-2.5 py-1 rounded-full text-[10px] font-bold shrink-0 ${pill}">${c.status}</span>
      </div>

      <!-- Environment & Project Tag -->
      <div class="flex items-center justify-between text-xs py-1 px-2.5 rounded-lg bg-gray-50 border border-gray-100">
        <a href="${m1Url}" onclick="event.stopPropagation()" class="font-mono text-[11px] text-[#0071e3] hover:underline truncate max-w-[150px]" title="View in Module 1">
          📁 ${escHtml(c.project_id)}
        </a>
        <span class="font-mono text-[10px] text-gray-500">${escHtml(c.environment_id)}</span>
      </div>

      <!-- AWS Cloud Badge -->
      <div class="p-2.5 rounded-xl bg-[#fff7ed] border border-[#fed7aa] flex items-center justify-between text-xs">
        <div class="flex items-center gap-2">
          <span class="px-1.5 py-0.5 rounded bg-[#ea580c] text-white text-[9px] font-bold">AWS</span>
          <span class="font-mono text-[#9a3412] font-semibold">${cloud ? cloud.account_id||'Configured' : 'No AWS account linked'}</span>
        </div>
        ${cloud ? `<span class="text-[11px] text-[#c2410c] font-medium">${cloud.aws_region}</span>` : `
          <button onclick="event.stopPropagation(); openAwsModal('${c.project_id}', '${c.environment_id}', '${c.aws_region || 'us-east-1'}')" class="px-2.5 py-1 rounded-md bg-[#ea580c] hover:bg-[#d9480f] text-white text-[10px] font-bold transition flex items-center gap-1 shadow-xs">
            <span>+ Connect AWS</span>
          </button>
        `}
      </div>
      <!-- Commit info -->
      ${sha && msg ? `
      <div class="bg-[#f5f5f7] rounded-xl p-3 space-y-1">
        <div class="flex items-center gap-1.5">
          <span class="font-mono text-[11px] font-bold text-[#0071e3]">${sha}</span>
          <span class="text-[#d2d2d7]">·</span>
          <span class="text-[11px] text-[#6e6e73] truncate">${escHtml(msg)}</span>
        </div>
        ${c.last_commit_author?`<div class="text-[10px] text-[#aeaeb2]">by ${escHtml(c.last_commit_author)}</div>`:''}
      </div>` : `<div class="bg-[#f5f5f7] rounded-xl p-3 text-xs text-[#aeaeb2] italic">Pending validation snapshot</div>`}

      <!-- Footer with Module 3 Link & Manage -->
      <div class="flex items-center justify-between border-t border-[#f5f5f7] pt-3 text-xs text-[#6e6e73]">
        <div class="flex items-center gap-2">
          <span>${icon} ${lang}</span>
          ${c.is_private?'<span class="px-1.5 py-0.5 rounded bg-[#f5f5f7] text-[#636366] text-[10px] font-medium border border-[#e5e5ea]">Private</span>':''}
        </div>
        <div class="flex items-center gap-2">
          <button onclick="event.stopPropagation(); window.location.href='${m3Url}'" class="px-2.5 py-1 rounded-md bg-[#e8f1fb] hover:bg-[#d0e4f7] text-[#0071e3] text-[11px] font-bold transition flex items-center gap-1">
            <span>Repo Analyzer</span>
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
          </button>
          <span class="text-[11px] text-[#0071e3] font-semibold group-hover:underline">
            Manage &rarr;
          </span>
        </div>
      </div>
    </div>`;
  });
}

function openConnection(id){ window.location.href=`/app/source/${id}`; }

function escHtml(s){ const d=document.createElement('div'); d.textContent=s||''; return d.innerHTML; }

window.addEventListener('DOMContentLoaded', ()=>{
  // Handle OAuth query params if returning from GitHub redirect
  const params = new URLSearchParams(window.location.search);
  if(params.get('github_connected')==='1'){
    const token = params.get('gh_token');
    const user = params.get('gh_user');
    if(token){ currentGhToken = token; localStorage.setItem('X-GH-Token', token); }
    if(user){ currentGhUser = user; localStorage.setItem('X-GH-User', user); }
    toast(`GitHub connected as @${user||'developer'}!`, true);
    window.history.replaceState({}, document.title, window.location.pathname);
    showConnectModal();
  }

  // Handle incoming project_id and environment_id from Module 1
  const qProj = params.get('project_id');
  const qEnv  = params.get('environment_id');
  if(qProj || qEnv){
    showConnectModal(qProj, qEnv);
  }

  loadConnections();
  checkOAuthConfig();
});
</script>
</body>
</html>"""
