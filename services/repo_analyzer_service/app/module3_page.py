"""
module3_page.py — Module 3 Repository Analyzer Service UI

Dark AWS Console theme (CloudScape design language):
  #0f141c  page background (Squid Ink Deep)
  #161e2e  header / sidebar (Squid Ink)
  #232f3e  nav / cards (Navy)
  #1b2533  card surface
  #2d3748  card border
  #ec7211  primary accent (AWS Orange)
  #ff9900  secondary accent
  #0972d3  info / link blue
  #1d8102  success green
  #d13212  error red
"""


def get_module3_page_html() -> str:
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AetherOps Cloud — Module 3: Repository Analyzer</title>
    <link rel="stylesheet" href="/static/fonts/fonts.css">
    <script src="/static/js/tailwind.js"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Plus Jakarta Sans', 'Segoe UI', 'system-ui', 'sans-serif'],
                        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
                    },
                    colors: {
                        aws: {
                            squid:     '#161e2e',
                            squidDark: '#0f141c',
                            navy:      '#232f3e',
                            card:      '#1b2533',
                            border:    '#2d3748',
                            borderL:   '#414d5c',
                            orange:    '#ec7211',
                            orangeL:   '#ff9900',
                            blue:      '#0972d3',
                            green:     '#1d8102',
                            red:       '#d13212',
                            muted:     '#9ba7b6',
                            light:     '#eaeded',
                        }
                    }
                }
            }
        }
    </script>
    <style>
        /* ── Base ── */
        *, *::before, *::after { box-sizing: border-box; }
        body   { background: #0f141c; color: #eaeded; font-family: 'Plus Jakarta Sans', 'Segoe UI', system-ui, sans-serif; }

        /* ── Scrollbar ── */
        ::-webkit-scrollbar         { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track   { background: #0f141c; }
        ::-webkit-scrollbar-thumb   { background: #2d3748; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #414d5c; }

        /* ── Cards ── */
        .aws-card {
            background: #1b2533;
            border: 1px solid #2d3748;
            border-radius: 6px;
            box-shadow: 0 1px 4px rgba(0,0,0,.45);
        }

        /* ── Buttons ── */
        .btn-primary {
            background: #ec7211; color: #fff; font-weight: 700;
            border: none; border-radius: 4px; cursor: pointer;
            transition: background .15s, box-shadow .15s;
        }
        .btn-primary:hover   { background: #eb5f07; }
        .btn-primary:active  { background: #dd5706; }
        .btn-primary:disabled { background: #414d5c; cursor: not-allowed; }

        .btn-secondary {
            background: #232f3e; border: 1px solid #414d5c; color: #eaeded;
            border-radius: 4px; cursor: pointer;
            transition: background .15s, border-color .15s;
        }
        .btn-secondary:hover { background: #2a384c; border-color: #68778d; }

        /* ── Inputs ── */
        .aws-input {
            background: #0f141c; border: 1px solid #3b444b;
            color: #eaeded; border-radius: 4px;
            transition: border-color .15s;
        }
        .aws-input:focus { border-color: #ec7211; outline: none; box-shadow: 0 0 0 1px #ec7211; }
        .aws-input::placeholder { color: #68778d; }

        /* ── Tabs ── */
        .tab-active   { border-bottom: 2px solid #ec7211; color: #ff9900; font-weight: 700; }
        .tab-inactive { color: #9ba7b6; border-bottom: 2px solid transparent; }
        .tab-inactive:hover { color: #eaeded; }

        /* ── Badge variants ── */
        .badge-orange  { background: rgba(236,114,17,.2); color: #ff9900; border: 1px solid rgba(236,114,17,.4); }
        .badge-green   { background: rgba(29,129,2,.2);   color: #1d8102; border: 1px solid rgba(29,129,2,.4);  }
        .badge-red     { background: rgba(209,50,18,.2);  color: #d13212; border: 1px solid rgba(209,50,18,.4); }
        .badge-blue    { background: rgba(9,114,211,.2);  color: #539fe5; border: 1px solid rgba(9,114,211,.4); }
        .badge-gray    { background: #232f3e; color: #9ba7b6; border: 1px solid #414d5c; }

        /* ── Tag chips ── */
        .chip { display: inline-flex; align-items: center; padding: 2px 8px;
                border-radius: 3px; font-family: 'JetBrains Mono', monospace;
                font-size: 10px; font-weight: 600; }

        /* ── Loading spinner ── */
        .spin { animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* ── Progress bar ── */
        .progress-bar { transition: width .4s ease; }
    </style>
</head>
<body class="min-h-screen flex flex-col">

    <!-- ════════════════════════════════════════════
         TOP NAVIGATION BAR — AWS Console Dark
    ═════════════════════════════════════════════ -->
    <header class="bg-[#161e2e] border-b border-[#2d3748] px-4 py-2.5 flex items-center justify-between sticky top-0 z-40 shadow-md">

        <!-- Left: Brand + Breadcrumb -->
        <div class="flex items-center space-x-3">
            <div class="w-8 h-8 rounded bg-[#ec7211] flex items-center justify-center font-mono font-extrabold text-xs text-white shadow">AO</div>
            <div class="flex items-center space-x-2 text-sm">
                <a href="http://localhost:8009/app" class="font-bold text-[#eaeded] hover:text-[#ff9900] transition">AetherOps</a>
                <span class="text-[#414d5c]">/</span>
                <span class="text-xs font-extrabold px-2 py-0.5 rounded font-mono badge-orange">MODULE 3</span>
                <span class="text-[#414d5c] hidden sm:inline">/</span>
                <span class="text-xs font-semibold text-[#9ba7b6] font-mono hidden sm:inline">REPOSITORY ANALYZER</span>
            </div>
        </div>

        <!-- Centre: Status indicators -->
        <div class="hidden lg:flex items-center space-x-2 text-xs">
            <span class="px-2 py-0.5 rounded badge-gray flex items-center gap-1.5 font-mono text-[11px]">
                <span class="h-2 w-2 rounded-full bg-[#1d8102]"></span> Service Active
            </span>
            <span class="px-2 py-0.5 rounded badge-gray flex items-center gap-1.5 font-mono text-[11px]">
                <span class="h-2 w-2 rounded-full bg-[#1d8102]"></span> repo_analyzer v0.1
            </span>
            <span class="px-2 py-0.5 rounded badge-orange font-mono text-[11px] flex items-center gap-1.5">
                <span class="h-2 w-2 rounded-full bg-[#ec7211] animate-pulse"></span> Port :8003
            </span>
        </div>

        <!-- Right: Navigation links -->
        <div class="flex items-center space-x-2 text-xs">
            <a href="http://localhost:8001/app" class="btn-secondary px-2.5 py-1.5 rounded text-xs font-semibold flex items-center gap-1">
                <svg class="w-3.5 h-3.5 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                Module 1: Sizing
            </a>
            <a href="http://localhost:8002/app" class="btn-secondary px-2.5 py-1.5 rounded text-xs font-semibold">Module 2: Architect</a>
            <a href="/docs" class="btn-secondary px-2.5 py-1.5 rounded text-xs font-semibold flex items-center gap-1">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                API Docs
            </a>
        </div>
    </header>


    <!-- ════════════════════════════════════════════
         MAIN CONTENT
    ═════════════════════════════════════════════ -->
    <main class="flex-1 p-4 sm:p-6 max-w-7xl mx-auto w-full space-y-6">

        <!-- Hero Banner -->
        <div class="aws-card p-5 border-l-4 border-[#ec7211] flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
                <div class="flex items-center gap-2 mb-1.5">
                    <span class="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded badge-orange font-mono">MODULE 3</span>
                    <span class="text-xs text-[#9ba7b6] font-mono">• Zero-Network • Zero-LLM • Deterministic</span>
                </div>
                <h1 class="text-xl font-extrabold text-[#eaeded]">Repository Analyzer &amp; AWS Sizing Bridge</h1>
                <p class="text-xs text-[#9ba7b6] mt-1 max-w-2xl leading-relaxed">
                    Point at any local repository. Module 3 scans the file tree with
                    evidence-backed static detectors, fingerprints your tech stack, and
                    dispatches the result to Module 1 for precise AWS infrastructure sizing
                    and FinOps cost breakdown — all without executing a single line of repo code.
                </p>
            </div>
            <div class="flex flex-col sm:flex-row gap-2 shrink-0">
                <button onclick="loadSamplePath('fastapi_pg')" class="btn-secondary px-3 py-1.5 rounded text-xs font-medium">
                    Load FastAPI+PG Sample
                </button>
                <button onclick="loadSamplePath('node_monorepo')" class="btn-secondary px-3 py-1.5 rounded text-xs font-medium">
                    Load Node Monorepo Sample
                </button>
            </div>
        </div>

        <!-- Two-Column Layout -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

            <!-- ── LEFT: Scan Input ── -->
            <div class="lg:col-span-4 space-y-5">

                <!-- Scan Form Card -->
                <div class="aws-card p-5 space-y-4 border-t-2 border-[#ec7211]">
                    <div class="flex items-center justify-between pb-2 border-b border-[#2d3748]">
                        <div class="flex items-center gap-2">
                            <span class="h-2.5 w-2.5 rounded-full bg-[#ec7211]"></span>
                            <h2 class="text-sm font-bold text-[#eaeded] uppercase tracking-wider">Repository Target</h2>
                        </div>
                        <span class="text-[10px] font-mono text-[#9ba7b6]">Static Analysis Only</span>
                    </div>

                    <div class="space-y-3 text-xs">
                        <!-- Repo Path -->
                        <div>
                            <label class="block text-[#9ba7b6] font-semibold mb-1">
                                Repository Path <span class="text-[#d13212]">*</span>
                            </label>
                            <input
                                id="inp-repo-path"
                                type="text"
                                placeholder="/home/user/my-project"
                                class="aws-input w-full p-2 rounded text-xs font-mono"
                            />
                            <p class="text-[10px] text-[#9ba7b6] mt-1">Absolute path to the local repository root directory.</p>
                        </div>

                        <!-- Project Name Override -->
                        <div>
                            <label class="block text-[#9ba7b6] font-semibold mb-1">Project Name Override</label>
                            <input
                                id="inp-project-name"
                                type="text"
                                placeholder="auto-detect from folder name"
                                class="aws-input w-full p-2 rounded text-xs font-mono"
                            />
                        </div>

                        <!-- Region + Budget -->
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block text-[10px] text-[#9ba7b6] font-semibold mb-1">Target Region</label>
                                <select id="inp-region" class="aws-input w-full p-1.5 rounded text-xs">
                                    <option value="us-east-1" selected>us-east-1 (N. Virginia)</option>
                                    <option value="us-east-2">us-east-2 (Ohio)</option>
                                    <option value="us-west-2">us-west-2 (Oregon)</option>
                                    <option value="ap-south-1">ap-south-1 (Mumbai)</option>
                                    <option value="eu-west-1">eu-west-1 (Ireland)</option>
                                    <option value="eu-central-1">eu-central-1 (Frankfurt)</option>
                                    <option value="ap-southeast-1">ap-southeast-1 (Singapore)</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-[10px] text-[#9ba7b6] font-semibold mb-1">Max Budget ($/mo)</label>
                                <input id="inp-budget" type="number" min="0" placeholder="Optional"
                                    class="aws-input w-full p-1.5 rounded text-xs font-mono">
                            </div>
                        </div>

                        <!-- Traffic / Reliability overrides -->
                        <div class="grid grid-cols-2 gap-2">
                            <div>
                                <label class="block text-[10px] text-[#9ba7b6] font-semibold mb-1">Traffic Scale</label>
                                <select id="inp-traffic" class="aws-input w-full p-1.5 rounded text-xs">
                                    <option value="">Auto-detect</option>
                                    <option value="hobby_dev">Hobby / Dev</option>
                                    <option value="growth">Growth</option>
                                    <option value="production">Production</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-[10px] text-[#9ba7b6] font-semibold mb-1">Reliability</label>
                                <select id="inp-reliability" class="aws-input w-full p-1.5 rounded text-xs">
                                    <option value="">Auto-detect</option>
                                    <option value="dev_testing">Dev / Testing</option>
                                    <option value="production_safe">Prod-Safe (Multi-AZ)</option>
                                    <option value="mission_critical">Mission-Critical</option>
                                </select>
                            </div>
                        </div>

                        <!-- Options -->
                        <div class="flex items-center gap-3 pt-1">
                            <label class="flex items-center gap-1.5 cursor-pointer">
                                <input id="inp-auto-save" type="checkbox" checked class="rounded">
                                <span class="text-[#9ba7b6]">Save to requirements.db</span>
                            </label>
                            <label class="flex items-center gap-1.5 cursor-pointer">
                                <input id="inp-include-findings" type="checkbox" class="rounded">
                                <span class="text-[#9ba7b6]">Include raw findings</span>
                            </label>
                        </div>

                        <!-- Scan CTA -->
                        <div class="pt-2 flex gap-2">
                            <button id="btn-scan" onclick="runScan()" class="btn-primary flex-1 py-2.5 rounded text-xs font-bold flex items-center justify-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                                Scan &amp; Size Repository
                            </button>
                            <button onclick="runScanOnly()" class="btn-secondary px-3 py-2.5 rounded text-xs font-semibold" title="Scan only — no sizing">
                                Scan Only
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Scan Stats Summary -->
                <div id="stats-card" class="aws-card p-4 space-y-3 hidden">
                    <div class="text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider font-mono border-b border-[#2d3748] pb-2">
                        Scan Statistics
                    </div>
                    <div class="grid grid-cols-2 gap-2 text-center text-xs">
                        <div class="p-2 rounded bg-[#0f141c] border border-[#2d3748]">
                            <div class="text-lg font-extrabold text-[#ff9900] font-mono" id="stat-files">—</div>
                            <div class="text-[10px] text-[#9ba7b6]">Files Scanned</div>
                        </div>
                        <div class="p-2 rounded bg-[#0f141c] border border-[#2d3748]">
                            <div class="text-lg font-extrabold text-[#539fe5] font-mono" id="stat-findings">—</div>
                            <div class="text-[10px] text-[#9ba7b6]">Findings</div>
                        </div>
                        <div class="p-2 rounded bg-[#0f141c] border border-[#2d3748]">
                            <div class="text-lg font-extrabold text-[#1d8102] font-mono" id="stat-components">—</div>
                            <div class="text-[10px] text-[#9ba7b6]">Components</div>
                        </div>
                        <div class="p-2 rounded bg-[#0f141c] border border-[#2d3748]">
                            <div class="text-lg font-extrabold text-[#a87ffb] font-mono" id="stat-kb">—</div>
                            <div class="text-[10px] text-[#9ba7b6]">KB Read</div>
                        </div>
                    </div>
                </div>

            </div>

            <!-- ── RIGHT: Results Panel ── -->
            <div class="lg:col-span-8 space-y-5">

                <!-- Results Card -->
                <div class="aws-card p-5 space-y-4" id="results-card">

                    <!-- Header Bar -->
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-3 border-b border-[#2d3748]">
                        <div>
                            <div class="flex items-center gap-2">
                                <span id="badge-monorepo" class="hidden px-2 py-0.5 rounded badge-blue text-[10px] font-mono font-bold">MONOREPO</span>
                                <span id="badge-arch-tier" class="px-2 py-0.5 rounded badge-orange text-[10px] font-mono font-bold">—</span>
                            </div>
                            <h2 class="text-base font-bold text-[#eaeded] mt-1" id="out-repo-name">Repository Scan Results</h2>
                        </div>
                        <div class="text-right" id="cost-summary-block">
                            <div class="text-xs text-[#9ba7b6]">Estimated Monthly Spend</div>
                            <div class="text-xl font-extrabold text-[#eaeded] font-mono" id="out-total-cost">—</div>
                        </div>
                    </div>

                    <!-- Tabs -->
                    <div class="flex items-center space-x-5 border-b border-[#2d3748] text-xs">
                        <button onclick="switchTab('stack')" id="tab-btn-stack"
                            class="pb-2.5 tab-active flex items-center gap-1.5 cursor-pointer">
                            <svg class="w-3.5 h-3.5 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"/></svg>
                            Tech Stack
                        </button>
                        <button onclick="switchTab('components')" id="tab-btn-components"
                            class="pb-2.5 tab-inactive flex items-center gap-1.5 cursor-pointer">
                            <svg class="w-3.5 h-3.5 text-[#539fe5]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                            Components
                        </button>
                        <button onclick="switchTab('sizing')" id="tab-btn-sizing"
                            class="pb-2.5 tab-inactive flex items-center gap-1.5 cursor-pointer">
                            <svg class="w-3.5 h-3.5 text-[#a87ffb]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                            AWS Sizing &amp; Costs
                        </button>
                        <button onclick="switchTab('diagnostics')" id="tab-btn-diagnostics"
                            class="pb-2.5 tab-inactive flex items-center gap-1.5 cursor-pointer">
                            <svg class="w-3.5 h-3.5 text-[#1d8102]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                            Diagnostics
                        </button>
                    </div>

                    <!-- ── Tab: Tech Stack ── -->
                    <div id="tab-content-stack" class="space-y-4">
                        <div id="stack-placeholder" class="text-center py-12 text-[#9ba7b6] text-sm">
                            <svg class="w-10 h-10 mx-auto mb-3 text-[#414d5c]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                            Enter a repository path and click <strong class="text-[#ff9900]">Scan</strong> to begin analysis.
                        </div>
                        <div id="stack-content" class="hidden space-y-4">
                            <!-- languages / frameworks / databases / ports / orchestration rows -->
                            <div id="stack-rows"></div>
                            <!-- Mapped requirement preview -->
                            <div class="p-3.5 rounded bg-[#0f141c] border border-[#2d3748] space-y-2">
                                <div class="text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider font-mono">
                                    Mapped Module 1 Input (Auto-Derived)
                                </div>
                                <div id="mapped-input-grid" class="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs"></div>
                            </div>
                        </div>
                    </div>

                    <!-- ── Tab: Components ── -->
                    <div id="tab-content-components" class="space-y-3 hidden">
                        <div id="components-container"></div>
                    </div>

                    <!-- ── Tab: AWS Sizing & Costs ── -->
                    <div id="tab-content-sizing" class="space-y-4 hidden">
                        <div id="sizing-placeholder" class="text-center py-8 text-[#9ba7b6] text-xs">
                            Run <strong>Scan &amp; Size</strong> to fetch AWS sizing from Module 1.
                        </div>
                        <div id="sizing-content" class="hidden space-y-3">
                            <!-- Sizing cards rendered by JS -->
                            <div id="sizing-specs-grid" class="grid grid-cols-1 sm:grid-cols-2 gap-3"></div>
                            <!-- FinOps Optimizations -->
                            <div id="finops-section" class="space-y-2 hidden">
                                <div class="text-xs font-bold text-[#9ba7b6] uppercase tracking-wider font-mono pt-2">
                                    FinOps Cost Optimizations
                                </div>
                                <div id="finops-list" class="space-y-2"></div>
                            </div>
                        </div>
                    </div>

                    <!-- ── Tab: Diagnostics ── -->
                    <div id="tab-content-diagnostics" class="space-y-3 hidden">
                        <div id="diagnostics-content" class="space-y-3">
                            <div class="text-center py-8 text-[#9ba7b6] text-xs">No scan result yet.</div>
                        </div>
                    </div>

                    <!-- Dispatch strip -->
                    <div class="pt-4 border-t border-[#2d3748] flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#0f141c] p-3 rounded" id="dispatch-strip">
                        <div>
                            <div class="text-xs font-bold text-[#eaeded] flex items-center gap-1.5">
                                Forward to Module 1 Sizing Engine
                                <span class="px-1.5 py-0.2 rounded text-[9px] font-mono badge-orange">:8001</span>
                            </div>
                            <p class="text-[11px] text-[#9ba7b6]">
                                Send the scanned repo profile to Module 1 for detailed AWS cost analysis and rationales.
                            </p>
                        </div>
                        <button id="btn-dispatch" onclick="dispatchToModule1()"
                            class="btn-secondary py-2 px-3.5 rounded text-xs font-bold flex items-center gap-1.5 shrink-0">
                            <span>Dispatch to Module 1</span>
                            <svg class="w-3.5 h-3.5 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                        </button>
                    </div>

                </div>

            </div>
        </div>

        <!-- ── Bottom: Recent Scans Table ── -->
        <div class="aws-card p-5 space-y-4">
            <div class="flex items-center justify-between border-b border-[#2d3748] pb-3">
                <div class="flex items-center gap-2">
                    <span class="h-2.5 w-2.5 rounded-full bg-[#1d8102]"></span>
                    <h3 class="text-sm font-bold text-[#eaeded] uppercase tracking-wider">Recent Repository Scans</h3>
                    <span class="text-[10px] px-2 py-0.5 rounded badge-gray font-mono border" id="scans-count">0 Scans</span>
                </div>
                <button onclick="refreshScans()" class="text-xs text-[#9ba7b6] hover:text-[#eaeded] flex items-center gap-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                    Refresh
                </button>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse">
                    <thead>
                        <tr class="border-b border-[#2d3748] bg-[#161e2e] text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider">
                            <th class="p-3">Repository</th>
                            <th class="p-3">Languages</th>
                            <th class="p-3">Arch Tier</th>
                            <th class="p-3 text-right">Est. Cost</th>
                            <th class="p-3 text-center">Monorepo</th>
                            <th class="p-3 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="scans-tbody" class="divide-y divide-[#263244] bg-[#1b2533]">
                        <tr><td colspan="6" class="p-4 text-center text-[#9ba7b6]">No scans recorded yet.</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

    </main>


    <!-- ════════════════════════════════════════════
         FOOTER
    ═════════════════════════════════════════════ -->
    <footer class="mt-auto border-t border-[#2d3748] bg-[#161e2e] py-3 px-6 text-xs text-[#9ba7b6] flex flex-col sm:flex-row justify-between items-center gap-2">
        <div class="flex items-center gap-2">
            <span class="font-semibold text-[#eaeded]">&copy; 2026 AetherOps Cloud</span>
            <span class="text-[#414d5c]">•</span>
            <span>Module 3: Repository Analyzer Service (Port :8003)</span>
        </div>
        <div class="flex items-center gap-2 font-mono text-[11px]">
            <span class="inline-block w-2 h-2 rounded-full bg-[#1d8102]"></span>
            <span>Engine: repo_analyzer v0.1 • Zero-Network • Zero-LLM • Deterministic</span>
        </div>
    </footer>


    <!-- ════════════════════════════════════════════
         JAVASCRIPT
    ═════════════════════════════════════════════ -->
    <script>
        // -------------------------------------------------------------------
        // State
        // -------------------------------------------------------------------
        let lastScanResult  = null;
        let lastSizingData  = null;
        let recentScans     = [];

        // -------------------------------------------------------------------
        // Sample path shortcuts (using the repo_analyzer test fixtures)
        // -------------------------------------------------------------------
        const FIXTURE_BASE = '/home/prathap32/GP/devops-lab/projects/repo_analyzer/tests/fixtures';
        const SAMPLES = {
            fastapi_pg:    FIXTURE_BASE + '/fastapi_pg',
            node_monorepo: FIXTURE_BASE + '/node_monorepo',
            java_spring:   FIXTURE_BASE + '/java_spring',
            go_gin:        FIXTURE_BASE + '/go_gin',
        };
        function loadSamplePath(key) {
            document.getElementById('inp-repo-path').value = SAMPLES[key] || '';
        }

        // -------------------------------------------------------------------
        // Tab switching
        // -------------------------------------------------------------------
        function switchTab(tab) {
            ['stack', 'components', 'sizing', 'diagnostics'].forEach(t => {
                document.getElementById('tab-content-' + t).classList.add('hidden');
                document.getElementById('tab-btn-' + t).className =
                    'pb-2.5 tab-inactive flex items-center gap-1.5 cursor-pointer';
            });
            document.getElementById('tab-content-' + tab).classList.remove('hidden');
            document.getElementById('tab-btn-' + tab).className =
                'pb-2.5 tab-active flex items-center gap-1.5 cursor-pointer';
        }

        // -------------------------------------------------------------------
        // Build API payload from form
        // -------------------------------------------------------------------
        function getPayload(autoSave) {
            return {
                repo_path:    document.getElementById('inp-repo-path').value.trim(),
                project_name: document.getElementById('inp-project-name').value.trim() || null,
                monthly_budget: parseFloat(document.getElementById('inp-budget').value) || null,
                traffic_scale: document.getElementById('inp-traffic').value || null,
                reliability:   document.getElementById('inp-reliability').value || null,
                target_region: document.getElementById('inp-region').value || 'us-east-1',
                auto_save: (autoSave !== undefined) ? autoSave : document.getElementById('inp-auto-save').checked,
            };
        }

        // -------------------------------------------------------------------
        // Scan + Size (calls Module 1 analyze-repo via this service's proxy)
        // -------------------------------------------------------------------
        async function runScan() {
            const payload = getPayload();
            if (!payload.repo_path) { alert('Please enter a repository path.'); return; }

            const btn = document.getElementById('btn-scan');
            btn.innerHTML = '<svg class="w-4 h-4 spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg><span>Scanning…</span>';
            btn.disabled = true;

            try {
                const include = document.getElementById('inp-include-findings').checked;
                const res = await fetch('/api/v1/repo/scan-and-size', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ...payload, include_findings: include }),
                });
                const json = await res.json();
                if (json.status === 'SUCCESS') {
                    lastScanResult = json.scan_result;
                    lastSizingData = json.sizing_data || null;
                    renderResults(json);
                    addToRecentScans(json);
                } else {
                    alert('Scan error: ' + (json.detail || JSON.stringify(json)));
                }
            } catch (err) {
                alert('Request failed: ' + err.message);
            } finally {
                btn.innerHTML = '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>Scan & Size Repository';
                btn.disabled = false;
            }
        }

        async function runScanOnly() {
            const payload = getPayload(false);
            if (!payload.repo_path) { alert('Please enter a repository path.'); return; }

            const btn = document.getElementById('btn-scan');
            btn.disabled = true;

            try {
                const include = document.getElementById('inp-include-findings').checked;
                const res = await fetch('/api/v1/repo/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ repo_path: payload.repo_path, include_findings: include }),
                });
                const json = await res.json();
                if (json.status === 'SUCCESS') {
                    lastScanResult = json;
                    lastSizingData = null;
                    renderScanOnly(json);
                } else {
                    alert('Scan error: ' + (json.detail || JSON.stringify(json)));
                }
            } catch (err) {
                alert('Request failed: ' + err.message);
            } finally {
                btn.disabled = false;
            }
        }

        // -------------------------------------------------------------------
        // Dispatch repo to Module 1 analyze-repo endpoint
        // -------------------------------------------------------------------
        async function dispatchToModule1() {
            const payload = getPayload();
            if (!payload.repo_path && !lastScanResult) {
                alert('Please run a scan first.');
                return;
            }
            if (lastSizingData) {
                // Already have sizing — open Module 1 UI
                window.open('http://localhost:8001/app', '_blank');
                return;
            }
            await runScan();
        }

        // -------------------------------------------------------------------
        // Rendering helpers
        // -------------------------------------------------------------------
        function chipHtml(text, color) {
            const colors = {
                orange: 'bg-[#ec7211]/20 text-[#ff9900] border border-[#ec7211]/40',
                blue:   'bg-[#0972d3]/20 text-[#539fe5] border border-[#0972d3]/40',
                green:  'bg-[#1d8102]/20 text-[#1d8102] border border-[#1d8102]/40',
                gray:   'bg-[#232f3e] text-[#9ba7b6] border border-[#414d5c]',
                purple: 'bg-[#7c3aed]/20 text-[#a87ffb] border border-[#7c3aed]/40',
                red:    'bg-[#d13212]/20 text-[#ff9492] border border-[#d13212]/40',
            };
            return `<span class="chip ${colors[color] || colors.gray}">${text}</span>`;
        }

        function renderResults(json) {
            const scan = json.scan_result;
            const sizing = json.sizing_data;
            const parsed = json.parsed_input;

            renderScanOnly(scan);

            // Update header
            document.getElementById('badge-arch-tier').textContent =
                sizing?.architecture_tier?.toUpperCase() || '—';
            if (sizing?.total_estimated_cost != null) {
                document.getElementById('out-total-cost').textContent =
                    '$' + sizing.total_estimated_cost.toFixed(2) + ' / mo';
            }

            // Sizing tab
            if (sizing) {
                renderSizingTab(sizing);
                document.getElementById('sizing-placeholder').classList.add('hidden');
                document.getElementById('sizing-content').classList.remove('hidden');
            }

            // Mapped input preview
            if (parsed) renderMappedInput(parsed);
        }

        function renderScanOnly(scan) {
            // Header
            document.getElementById('out-repo-name').textContent = scan.repo_name || scan.repo_path;
            if (scan.is_monorepo) {
                document.getElementById('badge-monorepo').classList.remove('hidden');
            } else {
                document.getElementById('badge-monorepo').classList.add('hidden');
            }

            // Stats card
            document.getElementById('stat-files').textContent     = scan.coverage?.files_scanned ?? '—';
            document.getElementById('stat-findings').textContent  = scan.findings_count ?? '—';
            document.getElementById('stat-components').textContent = (scan.components?.length ?? '—');
            document.getElementById('stat-kb').textContent        = scan.coverage?.bytes_read_kb ?? '—';
            document.getElementById('stats-card').classList.remove('hidden');

            // Tech stack tab
            renderStackTab(scan);
            document.getElementById('stack-placeholder').classList.add('hidden');
            document.getElementById('stack-content').classList.remove('hidden');

            // Components tab
            renderComponentsTab(scan.components || []);

            // Diagnostics tab
            renderDiagnosticsTab(scan);

            switchTab('stack');
        }

        function renderStackTab(scan) {
            const rows = [
                { label: 'Languages',     items: scan.languages_detected,  color: 'orange' },
                { label: 'Frameworks',    items: scan.frameworks_detected,  color: 'blue'   },
                { label: 'Databases',     items: scan.databases_detected,   color: 'green'  },
                { label: 'Ports',         items: scan.ports_detected.map(String), color: 'purple' },
            ];

            let html = '';
            rows.forEach(r => {
                if (!r.items || !r.items.length) return;
                html += `<div class="flex flex-wrap items-center gap-2 py-2 border-b border-[#2d3748] last:border-0">
                    <span class="text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider w-24 shrink-0">${r.label}</span>
                    <div class="flex flex-wrap gap-1.5">${r.items.map(i => chipHtml(i, r.color)).join('')}</div>
                </div>`;
            });
            document.getElementById('stack-rows').innerHTML = html || '<p class="text-xs text-[#9ba7b6]">No detectable tech stack signals found.</p>';
        }

        function renderMappedInput(parsed) {
            const tech = parsed.technology || {};
            const ops  = parsed.operations || {};
            const grid = [
                ['Frontend',     tech.frontend || '—',          'orange'],
                ['Backend',      tech.backend  || '—',          'blue'],
                ['Database',     tech.database || '—',          'green'],
                ['Traffic',      parsed.traffic_scale || '—',   'gray'],
                ['Reliability',  parsed.reliability || '—',     'gray'],
                ['Orchestration',ops.container_orchestration||'—','purple'],
                ['Stream',       parsed.stream || '—',          'gray'],
                ['Security',     parsed.security_need || '—',   'gray'],
            ];
            document.getElementById('mapped-input-grid').innerHTML = grid.map(([k, v, c]) =>
                `<div class="p-2 rounded bg-[#161e2e] border border-[#2d3748]">
                    <div class="text-[10px] text-[#9ba7b6] font-semibold">${k}</div>
                    <div class="mt-0.5">${chipHtml(v, c)}</div>
                </div>`
            ).join('');
        }

        function renderComponentsTab(components) {
            if (!components.length) {
                document.getElementById('components-container').innerHTML =
                    '<p class="text-xs text-[#9ba7b6] text-center py-8">No components detected.</p>';
                return;
            }
            const kindColors = {
                backend: 'orange', frontend: 'blue', worker: 'purple',
                library: 'gray', infra: 'green', service: 'orange', unknown: 'red',
            };
            document.getElementById('components-container').innerHTML = components.map(c => `
                <div class="p-3.5 rounded bg-[#0f141c] border border-[#2d3748] space-y-2 mb-2">
                    <div class="flex items-center justify-between flex-wrap gap-2">
                        <span class="font-mono text-xs font-bold text-[#ff9900]">${c.path}</span>
                        ${chipHtml(c.kind, kindColors[c.kind] || 'gray')}
                    </div>
                    <div class="flex flex-wrap gap-1.5">
                        ${c.languages.map(l => chipHtml(l, 'orange')).join('')}
                        ${c.frameworks.map(f => chipHtml(f, 'blue')).join('')}
                        ${c.databases.map(d => chipHtml(d, 'green')).join('')}
                        ${c.ports.map(p => chipHtml(':' + p, 'purple')).join('')}
                    </div>
                    ${c.start_commands.length ? `<div class="text-[10px] text-[#9ba7b6] font-mono">Start: ${c.start_commands.join(' | ')}</div>` : ''}
                    ${c.has_container_config ? '<div class="text-[10px] text-[#1d8102]">✓ Container config detected</div>' : ''}
                </div>
            `).join('');
        }

        function renderSizingTab(sizing) {
            const comp = sizing.profile?.components;
            if (!comp) return;
            const specs = [
                {
                    label: 'Compute (EC2)', accent: '#ec7211',
                    title: comp.compute.instance_type,
                    rows: [
                        `${comp.compute.vcpus} vCPUs • ${comp.compute.ram_gb} GB RAM`,
                        `Min ${comp.compute.min_instances} / Max ${comp.compute.max_instances} instances`,
                        `CPU target: ${comp.compute.target_cpu_utilization}%`,
                    ],
                    cost: comp.compute.monthly_cost,
                },
                {
                    label: 'Database (RDS)', accent: '#539fe5',
                    title: comp.database.instance_type,
                    rows: [
                        `${comp.database.storage_gb} GB ${comp.database.storage_type}`,
                        `Multi-AZ: ${comp.database.multi_az ? 'Yes' : 'No'}`,
                        `Backups: ${comp.database.backup_retention_days}d PITR`,
                    ],
                    cost: comp.database.monthly_cost,
                },
                {
                    label: 'Networking (VPC)', accent: '#a87ffb',
                    title: 'VPC + ALB + NAT',
                    rows: [
                        `ALB: ${comp.networking.has_alb ? 'Enabled' : 'None'}`,
                        `NAT Gateways: ${comp.networking.nat_gateway_count}`,
                        `CloudFront: ${comp.networking.has_cloudfront ? 'Active' : 'Off'}`,
                    ],
                    cost: comp.networking.monthly_cost,
                },
                {
                    label: 'Storage', accent: '#1d8102',
                    title: `EBS ${comp.storage.ebs_gb_per_instance}GB + S3 ${comp.storage.s3_gb}GB`,
                    rows: [
                        `S3 class: ${comp.storage.s3_class}`,
                        `Encryption: ${comp.security.encryption_enabled ? 'Enforced' : 'Default'}`,
                        `WAF: ${comp.security.waf_enabled ? 'Active' : 'None'}`,
                    ],
                    cost: comp.storage.monthly_cost,
                },
            ];

            document.getElementById('sizing-specs-grid').innerHTML = specs.map(s => `
                <div class="p-3.5 rounded bg-[#0f141c] border border-[#2d3748] space-y-1.5">
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] font-bold uppercase tracking-wider font-mono" style="color:${s.accent}">${s.label}</span>
                        <span class="font-mono text-xs font-bold text-[#eaeded]">$${s.cost.toFixed(2)}/mo</span>
                    </div>
                    <div class="text-xs font-bold text-[#eaeded] font-mono">${s.title}</div>
                    ${s.rows.map(r => `<div class="text-[11px] text-[#9ba7b6]">${r}</div>`).join('')}
                </div>
            `).join('');

            // FinOps
            const opts = sizing.cost_optimizations || [];
            if (opts.length) {
                document.getElementById('finops-section').classList.remove('hidden');
                document.getElementById('finops-list').innerHTML = opts.map(o => `
                    <div class="p-3 rounded bg-[#0f141c] border-l-4 border-[#ec7211] border border-[#2d3748]">
                        <div class="flex justify-between items-center flex-wrap gap-1">
                            <span class="text-xs font-bold text-[#eaeded]">${o.title}</span>
                            <span class="chip badge-green">Save ~$${o.estimated_monthly_savings}/mo</span>
                        </div>
                        <p class="text-[11px] text-[#9ba7b6] mt-1">${o.recommendation}</p>
                    </div>
                `).join('');
            }
        }

        function renderDiagnosticsTab(scan) {
            const sections = [];

            if (scan.unknowns?.length) {
                sections.push(`
                    <div class="space-y-1.5">
                        <div class="text-[10px] font-bold text-[#ff9900] uppercase tracking-wider font-mono">
                            Unknowns (${scan.unknowns.length})
                        </div>
                        ${scan.unknowns.map(u => `<div class="text-xs text-[#9ba7b6] p-2 rounded bg-[#0f141c] border border-[#2d3748]">⚠ ${u}</div>`).join('')}
                    </div>
                `);
            }

            if (scan.conflicts?.length) {
                sections.push(`
                    <div class="space-y-1.5">
                        <div class="text-[10px] font-bold text-[#d13212] uppercase tracking-wider font-mono">
                            Conflicts (${scan.conflicts.length})
                        </div>
                        ${scan.conflicts.map(c => `<div class="text-xs text-[#ff9492] p-2 rounded bg-[#0f141c] border border-[#d13212]/40">⛔ ${c}</div>`).join('')}
                    </div>
                `);
            }

            if (scan.errors?.length) {
                sections.push(`
                    <div class="space-y-1.5">
                        <div class="text-[10px] font-bold text-[#d13212] uppercase tracking-wider font-mono">
                            Errors (${scan.errors.length})
                        </div>
                        ${scan.errors.map(e => `<div class="text-xs text-[#ff9492] p-2 rounded bg-[#0f141c] border border-[#d13212]/40">✗ ${e}</div>`).join('')}
                    </div>
                `);
            }

            // Coverage info
            const cov = scan.coverage || {};
            sections.push(`
                <div class="space-y-1.5">
                    <div class="text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider font-mono">Coverage</div>
                    <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
                        <div class="p-2 rounded bg-[#0f141c] border border-[#2d3748]">
                            <div class="text-[#9ba7b6]">Detectors Run</div>
                            <div class="font-mono text-[#eaeded]">${(cov.detectors_run||[]).length}</div>
                        </div>
                        <div class="p-2 rounded bg-[#0f141c] border border-[#2d3748]">
                            <div class="text-[#9ba7b6]">Detectors Failed</div>
                            <div class="font-mono ${(cov.detectors_failed||[]).length ? 'text-[#d13212]' : 'text-[#1d8102]'}">${(cov.detectors_failed||[]).length}</div>
                        </div>
                        <div class="p-2 rounded bg-[#0f141c] border border-[#2d3748]">
                            <div class="text-[#9ba7b6]">Limits Hit</div>
                            <div class="font-mono ${(cov.limits_hit||[]).length ? 'text-[#ff9900]' : 'text-[#1d8102]'}">${(cov.limits_hit||[]).length}</div>
                        </div>
                    </div>
                    ${(cov.detectors_run||[]).length ? `<div class="text-[10px] text-[#9ba7b6] font-mono">${cov.detectors_run.join(' • ')}</div>` : ''}
                </div>
            `);

            document.getElementById('diagnostics-content').innerHTML = sections.join('') ||
                '<p class="text-xs text-[#9ba7b6]">No diagnostics issues detected.</p>';
        }

        // -------------------------------------------------------------------
        // Recent scans table
        // -------------------------------------------------------------------
        function addToRecentScans(json) {
            const scan   = json.scan_result || json;
            const sizing = json.sizing_data;
            recentScans.unshift({
                repo_name:   scan.repo_name || scan.repo_path,
                repo_path:   scan.repo_path,
                languages:   (scan.languages_detected || []).slice(0, 3),
                arch_tier:   sizing?.architecture_tier || '—',
                total_cost:  sizing?.total_estimated_cost ?? null,
                is_monorepo: scan.is_monorepo,
                project_id:  json.project_id,
            });
            if (recentScans.length > 20) recentScans.pop();
            renderScansTable();
        }

        function renderScansTable() {
            document.getElementById('scans-count').textContent = recentScans.length + ' Scans';
            if (!recentScans.length) return;
            document.getElementById('scans-tbody').innerHTML = recentScans.map(s => `
                <tr class="hover:bg-[#232f3e]/40 transition">
                    <td class="p-3">
                        <div class="font-bold text-[#eaeded]">${s.repo_name}</div>
                        <div class="text-[10px] text-[#9ba7b6] font-mono truncate max-w-xs">${s.repo_path}</div>
                    </td>
                    <td class="p-3">
                        <div class="flex flex-wrap gap-1">${s.languages.map(l => chipHtml(l, 'orange')).join('')}</div>
                    </td>
                    <td class="p-3">
                        <span class="chip badge-orange">${s.arch_tier}</span>
                    </td>
                    <td class="p-3 text-right font-mono font-bold text-[#eaeded]">
                        ${s.total_cost != null ? '$' + s.total_cost.toFixed(2) + '/mo' : '—'}
                    </td>
                    <td class="p-3 text-center">
                        ${s.is_monorepo ? '<span class="chip badge-blue">YES</span>' : '<span class="chip badge-gray">No</span>'}
                    </td>
                    <td class="p-3 text-right">
                        ${s.project_id ? `<a href="http://localhost:8001/app?project_id=${s.project_id}" target="_blank" class="btn-secondary px-2 py-1 rounded text-[10px] font-semibold">View in M1</a>` : '<span class="text-[10px] text-[#9ba7b6]">Scan-only</span>'}
                    </td>
                </tr>
            `).join('');
        }

        function refreshScans() { renderScansTable(); }

    </script>
</body>
</html>
"""
