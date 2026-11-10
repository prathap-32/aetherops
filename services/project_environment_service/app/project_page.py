# services/project_and_environment_management/app/project_page.py


def get_project_detail_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AetherOps — Project Detail</title>
    <link rel="stylesheet" href="/static/fonts/fonts.css">
    <script src="/static/js/tailwind.js"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Amazon Ember', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace']
                    },
                    colors: {
                        brand: {
                            50: '#eff6ff',
                            100: '#dbeafe',
                            200: '#bfdbfe',
                            500: '#2563eb',
                            600: '#1d4ed8',
                            700: '#1e40af',
                            800: '#1e3a8a',
                            900: '#00288e',
                        }
                    }
                }
            }
        }
    </script>
    <style>
        * { box-sizing: border-box; -webkit-font-smoothing: antialiased; }
        body {
            background-color: #f8f9ff;
            color: #0f172a;
            font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
            min-height: 100vh;
        }
        .sidebar {
            width: 260px;
            background: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        .card-surface {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .btn-primary {
            background: #1e40af;
            color: #ffffff;
            font-weight: 600;
            border-radius: 8px;
            border: 1px solid transparent;
            transition: all 0.15s ease;
            cursor: pointer;
        }
        .btn-primary:hover {
            background: #1d4ed8;
            box-shadow: 0 2px 8px rgba(30, 64, 175, 0.25);
        }
        .btn-secondary {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            color: #334155;
            font-weight: 600;
            border-radius: 8px;
            transition: all 0.15s ease;
            cursor: pointer;
        }
        .btn-secondary:hover {
            background: #f8fafc;
            border-color: #cbd5e1;
            color: #0f172a;
        }
        .btn-danger {
            background: #fff1f2;
            border: 1px solid #fecdd3;
            color: #dc2626;
            font-weight: 600;
            border-radius: 8px;
            transition: all 0.15s ease;
            cursor: pointer;
        }
        .btn-danger:hover {
            background: #fee2e2;
            border-color: #fca5a5;
        }
        .nav-item {
            display: flex;
            align-items: center;
            gap: 0.625rem;
            padding: 0.5rem 0.75rem;
            border-radius: 8px;
            font-size: 0.8125rem;
            font-weight: 500;
            color: #475569;
            transition: all 0.15s ease;
        }
        .nav-item:hover {
            background: #f8fafc;
            color: #0f172a;
        }
        .nav-item.active {
            background: #1e40af;
            color: #ffffff;
            font-weight: 600;
        }
        .nav-item.active svg {
            color: #ffffff;
        }
        .inp-standard {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            color: #0f172a;
            border-radius: 8px;
            transition: all 0.15s ease;
        }
        .inp-standard:focus {
            border-color: #2563eb;
            outline: none;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
        }
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.45);
            backdrop-filter: blur(4px);
            z-index: 50;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1rem;
        }
        .toast {
            position: fixed;
            bottom: 1.5rem;
            right: 1.5rem;
            z-index: 100;
            transform: translateY(120%);
            transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .toast.show { transform: translateY(0); }
        .spinner { animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
    </style>
</head>
<body class="min-h-screen bg-[#f8f9ff] text-slate-900 flex flex-col lg:flex-row antialiased">

    <!-- ═══════════════════════════════════════════════════════════════════════════
         MOBILE TOP HEADER (< 1024px)
         ═══════════════════════════════════════════════════════════════════════════ -->
    <header class="lg:hidden sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-slate-200 px-4 py-3 flex items-center justify-between shadow-xs">
        <div class="flex items-center gap-3">
            <button type="button" onclick="toggleMobileDrawer()" class="p-2 -ml-1 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition" aria-label="Open Navigation Menu">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
            </button>
            <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-lg bg-[#1e40af] text-white flex items-center justify-center font-bold text-xs tracking-tight font-mono shadow-sm">
                    AO
                </div>
                <span class="font-semibold text-slate-900 text-sm tracking-tight">AetherOps</span>
            </div>
        </div>

        <div class="flex items-center gap-2">
            <a href="/app" class="px-2.5 py-1 text-xs font-semibold rounded bg-slate-100 text-slate-700 hover:bg-slate-200 transition">
                &larr; Projects
            </a>
            <button onclick="showAddEnvModal()" class="btn-primary px-2.5 py-1 text-xs flex items-center gap-1 shadow-sm">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                <span>Add Env</span>
            </button>
        </div>
    </header>

    <!-- ═══════════════════════════════════════════════════════════════════════════
         MOBILE OFF-CANVAS DRAWER (< 1024px)
         ═══════════════════════════════════════════════════════════════════════════ -->
    <div id="mobile-drawer-backdrop" onclick="toggleMobileDrawer()" class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 hidden transition-opacity lg:hidden"></div>
    <aside id="mobile-drawer" class="fixed inset-y-0 left-0 w-72 max-w-[85vw] bg-white border-r border-slate-200 z-50 flex flex-col transform -translate-x-full transition-transform duration-200 ease-in-out lg:hidden">
        <div class="p-4 border-b border-slate-100 flex items-center justify-between">
            <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-lg bg-[#1e40af] text-white flex items-center justify-center font-bold text-sm tracking-tight font-mono shadow-sm">
                    AO
                </div>
                <div>
                    <span class="font-semibold text-slate-900 text-sm">AetherOps</span>
                    <div class="text-[10px] font-mono text-emerald-600">● v2.14.0 // port:8009</div>
                </div>
            </div>
            <button type="button" onclick="toggleMobileDrawer()" class="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
        </div>

        <div class="flex-1 overflow-y-auto px-3 py-4 space-y-5">
            <div class="space-y-1">
                <div class="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Core Navigation</div>
                <a href="/app#projects" class="nav-item">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>
                    <span>Projects &amp; Workspaces</span>
                </a>
                <a href="/app#environments" class="nav-item">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                    <span>Target Environments</span>
                </a>
            </div>

            <div class="space-y-1">
                <div class="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Platform Workflow</div>
                <a href="/app#source-cloud" class="nav-item justify-between group">
                    <span class="truncate">Source &amp; Cloud</span>
                    <span class="badge-pill text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-blue-50 text-[#1e40af] border border-blue-100">M2</span>
                </a>
                <a href="/app#repo-analyzer" class="nav-item justify-between group">
                    <span class="truncate">Repo Analyzer</span>
                    <span class="badge-pill text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-100">M3</span>
                </a>
                <a href="/app#architecture" class="nav-item justify-between group">
                    <span class="truncate">Architecture</span>
                    <span class="badge-pill text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-100">M4</span>
                </a>
                <a href="/app#deployments" class="nav-item justify-between group">
                    <span class="truncate">Deployments</span>
                    <span class="badge-pill text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">M6</span>
                </a>
                <a href="/app#monitoring" class="nav-item justify-between group">
                    <span class="truncate">Observability</span>
                    <span class="badge-pill text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">Live</span>
                </a>
            </div>
        </div>

        <div class="p-3.5 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
            <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-full bg-slate-800 text-white font-semibold text-xs flex items-center justify-center shrink-0">SC</div>
                <div>
                    <div class="text-xs font-semibold text-slate-900 truncate">Sarah Chen</div>
                    <div class="text-[10px] font-mono text-emerald-600">● operator:root</div>
                </div>
            </div>
            <button onclick="logout()" title="Sign Out" class="p-1.5 rounded-md hover:bg-slate-200 text-slate-500">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
            </button>
        </div>
    </aside>

    <!-- ═══════════════════════════════════════════════════════════════════════════
         PERSISTENT DESKTOP NAVIGATION SIDEBAR (Hidden on mobile < 1024px)
         ═══════════════════════════════════════════════════════════════════════════ -->
    <aside class="sidebar hidden lg:flex flex-col shrink-0 min-h-screen sticky top-0 h-screen z-30 select-none">
        
        <!-- Brand Header -->
        <div class="p-5 border-b border-slate-100 flex flex-col gap-3">
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-2.5">
                    <div class="w-8 h-8 rounded-lg bg-[#1e40af] text-white flex items-center justify-center font-bold text-sm tracking-tight font-mono shadow-sm">
                        AO
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="font-semibold text-slate-900 text-base tracking-tight">AetherOps</span>
                        <span class="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-[#eff6ff] text-[#1e40af] font-mono border border-blue-100">
                            ADMIN
                        </span>
                    </div>
                </div>
            </div>

            <!-- Version / Daemon Status Ribbon -->
            <div class="flex items-center justify-between text-[11px] font-mono text-slate-500 bg-slate-50 px-2.5 py-1.5 rounded-md border border-slate-200/60">
                <div class="flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span class="font-medium">module-1 // v2.14.0</span>
                </div>
                <span class="text-slate-400">8009</span>
            </div>
        </div>

        <!-- Sidebar Navigation Sections (Scrollable) -->
        <div class="flex-1 overflow-y-auto px-3.5 py-4 space-y-6">
            
            <!-- Section 1: CORE NAVIGATION -->
            <div class="space-y-1">
                <div class="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Core Navigation
                </div>
                <a href="/app#projects" class="nav-item">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>
                    <span>Projects &amp; Workspaces</span>
                </a>
                <a href="/app#environments" class="nav-item">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                    <span>Target Environments</span>
                </a>
            </div>

            <!-- Section 2: PLATFORM WORKFLOW -->
            <div class="space-y-1">
                <div class="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Platform Workflow
                </div>
                <a id="nav-module2-link" href="/app#source-cloud" class="nav-item justify-between group" title="Module 2: Source & Cloud Connection">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                        <span class="truncate">Source &amp; Cloud</span>
                    </div>
                    <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-blue-50 text-[#1e40af] border border-blue-100">
                        Module 2
                    </span>
                </a>
                <a id="nav-module3-link" href="/app#repo-analyzer" class="nav-item justify-between group" title="Module 3: Repository Analyzer">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                        <span class="truncate">Repo Analyzer</span>
                    </div>
                    <span class="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-100">
                        Module 3
                    </span>
                </a>
                <a href="/app#architecture" class="nav-item justify-between group" title="Module 4: Architecture Graph Generator">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                        <span class="truncate">Architecture Studio</span>
                    </div>
                    <span class="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-100">
                        Module 4
                    </span>
                </a>
                <a href="/app#iac" class="nav-item justify-between group" title="Module 5: IaC Code Generator">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>
                        <span class="truncate">IaC Generator</span>
                    </div>
                    <span class="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
                        Module 5
                    </span>
                </a>
                <a href="/app#deployments" class="nav-item justify-between group" title="Module 6: Deployments & Release">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                        <span class="truncate">Deployments</span>
                    </div>
                    <span class="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
                        Module 6
                    </span>
                </a>
                <a href="/app#monitoring" class="nav-item justify-between group" title="Module 7: Observability">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                        <span class="truncate">Observability</span>
                    </div>
                    <span class="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                        Telemetry
                    </span>
                </a>
                <a href="/app#finops" class="nav-item justify-between group" title="Module 8: FinOps">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        <span class="truncate">FinOps</span>
                    </div>
                    <span class="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200">
                        Cost
                    </span>
                </a>
                <a href="/app#security" class="nav-item justify-between group" title="Module 9: Security Scanner">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                        <span class="truncate">Security Scanner</span>
                    </div>
                    <span class="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200">
                        Audit
                    </span>
                </a>
            </div>

            <!-- Section 3: OPERATIONS -->
            <div class="space-y-1">
                <div class="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Operations
                </div>
                <a href="/app#docs" class="nav-item">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
                    <span>API Documentation</span>
                </a>
                <a href="/app#settings" class="nav-item">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                    <span>System Settings</span>
                </a>
            </div>
        </div>

        <!-- Sidebar Bottom User Footer -->
        <div class="p-3.5 border-t border-slate-100 bg-slate-50/70 flex items-center justify-between gap-2">
            <div class="flex items-center gap-2.5 min-w-0">
                <div class="w-8 h-8 rounded-full bg-slate-800 text-white font-semibold text-xs flex items-center justify-center shrink-0">
                    SC
                </div>
                <div class="min-w-0">
                    <div class="text-xs font-semibold text-slate-900 truncate">Sarah Chen</div>
                    <div class="text-[10px] font-mono text-emerald-600 flex items-center gap-1 truncate">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                        <span>operator:root</span>
                    </div>
                </div>
            </div>
            <button onclick="logout()" title="Sign Out" class="p-1.5 rounded-md hover:bg-slate-200/60 text-slate-500 hover:text-slate-800 transition">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
            </button>
        </div>
    </aside>

    <!-- ═══════════════════════════════════════════════════════════════════════════
         MAIN CONTENT AREA
         ═══════════════════════════════════════════════════════════════════════════ -->
    <div class="flex-1 flex flex-col min-w-0">

        <!-- Global Top Header (Height: 64px, Sticky) -->
        <header class="h-16 bg-white/95 backdrop-blur border-b border-slate-200/80 sticky top-0 z-30 px-6 sm:px-8 flex items-center justify-between gap-4">
            
            <!-- Breadcrumbs -->
            <div class="flex items-center gap-2 min-w-0 text-xs text-slate-500">
                <a href="/app" class="font-medium hover:text-slate-900 transition flex items-center gap-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
                    <span>Projects</span>
                </a>
                <span class="text-slate-300">/</span>
                <span class="font-semibold text-slate-900 truncate" id="header-project-name">Loading…</span>
            </div>

            <!-- Right Actions -->
            <div class="flex items-center gap-2.5 shrink-0">
                <a id="hdr-module2-btn" href="http://localhost:8010/app/source" target="_blank" class="hidden sm:flex btn-secondary px-3 py-1.5 text-xs items-center gap-1.5 font-semibold" title="Launch Module 2">
                    <span>Source &amp; Cloud (M2)</span>
                    <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                </a>
                <button onclick="showAddEnvModal()" class="btn-primary px-3.5 py-1.5 text-xs flex items-center gap-1.5 shadow-sm">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                    <span>Add Environment</span>
                </button>
            </div>
        </header>

        <!-- Main Workspace -->
        <main class="max-w-7xl w-full mx-auto px-6 sm:px-8 py-8 space-y-7">

            <!-- Loading State -->
            <div id="loading-state" class="card-surface p-16 text-center space-y-3">
                <svg class="spinner w-8 h-8 text-[#1e40af] mx-auto" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                <p class="text-xs font-medium text-slate-500">Loading project configuration…</p>
            </div>

            <!-- Project Overview Header Card -->
            <div id="project-header" class="hidden card-surface p-6 sm:p-7 space-y-5">
                <div class="flex flex-col md:flex-row md:items-start justify-between gap-5">
                    
                    <div class="flex items-start gap-4 min-w-0">
                        <div id="proj-icon" class="w-14 h-14 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center text-3xl shrink-0 shadow-xs">
                            📦
                        </div>
                        <div class="space-y-1.5 min-w-0">
                            <div class="flex items-center gap-3 flex-wrap">
                                <h1 class="text-2xl font-bold text-slate-900 tracking-tight" id="proj-name">—</h1>
                                <span id="proj-status-badge" class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono tracking-wide"></span>
                                <span id="proj-type-label" class="px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-100 text-slate-700 border border-slate-200">
                                    —
                                </span>
                            </div>
                            <p id="proj-desc" class="text-xs sm:text-sm text-slate-600 leading-relaxed max-w-2xl"></p>
                            <div class="flex items-center gap-4 text-xs text-slate-400 font-mono pt-1">
                                <span>Owner: <strong class="text-slate-700 font-sans" id="proj-owner">root_admin</strong></span>
                                <span>•</span>
                                <span>Created: <span id="proj-created" class="text-slate-600">—</span></span>
                                <span>•</span>
                                <span><span id="proj-env-count" class="font-bold text-[#1e40af]">0</span> environment(s) staged</span>
                            </div>
                        </div>
                    </div>

                    <!-- Actions -->
                    <div class="flex items-center gap-2 shrink-0">
                        <button onclick="archiveProject()" class="btn-secondary px-3 py-1.5 text-xs">Archive</button>
                        <button onclick="deleteProject()" class="btn-danger px-3 py-1.5 text-xs">Delete Workspace</button>
                    </div>
                </div>
            </div>

            <!-- 9-Stage Lifecycle Stepper Reference Banner (Responsive Horizontal Track) -->
            <div id="lifecycle-stepper-card" class="hidden card-surface p-5 space-y-3">
                <div class="flex items-center justify-between text-xs">
                    <span class="font-bold text-slate-800 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                        <span class="w-2 h-2 rounded-full bg-blue-600"></span>
                        <span>9-Stage Environment Lifecycle</span>
                    </span>
                    <span class="text-slate-400 font-mono text-[11px] hidden sm:inline">Standardized Pipeline Flow</span>
                </div>
                <div class="flex sm:grid sm:grid-cols-5 md:grid-cols-9 gap-1.5 overflow-x-auto pb-1 text-center text-[10px] font-mono scrollbar-thin">
                    <div class="min-w-[105px] sm:min-w-0 p-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 shrink-0 sm:shrink">1. CREATED</div>
                    <div class="min-w-[105px] sm:min-w-0 p-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 shrink-0 sm:shrink">2. CONFIGURED</div>
                    <div class="min-w-[120px] sm:min-w-0 p-2 rounded-lg bg-blue-50 border border-blue-200 text-[#1e40af] font-bold shrink-0 sm:shrink">3. REPO_CONNECTED</div>
                    <div class="min-w-[105px] sm:min-w-0 p-2 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-700 font-bold shrink-0 sm:shrink">4. ANALYZED</div>
                    <div class="min-w-[105px] sm:min-w-0 p-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 shrink-0 sm:shrink">5. ARCH_READY</div>
                    <div class="min-w-[105px] sm:min-w-0 p-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 shrink-0 sm:shrink">6. VALIDATED</div>
                    <div class="min-w-[125px] sm:min-w-0 p-2 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 shrink-0 sm:shrink">7. READY_TO_DEPLOY</div>
                    <div class="min-w-[105px] sm:min-w-0 p-2 rounded-lg bg-amber-50 border border-amber-200 text-amber-700 font-bold shrink-0 sm:shrink">8. DEPLOYING</div>
                    <div class="min-w-[105px] sm:min-w-0 p-2 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 font-bold shrink-0 sm:shrink">9. ACTIVE</div>
                </div>
            </div>

            <!-- Environments Section -->
            <div id="envs-section" class="hidden space-y-4">
                <div class="flex items-center justify-between">
                    <div>
                        <h2 class="text-base font-bold text-slate-900 tracking-tight">Deployment Environments</h2>
                        <p class="text-xs text-slate-500">Configure regions and lifecycle stages for this project.</p>
                    </div>
                    <button onclick="showAddEnvModal()" class="btn-primary px-3.5 py-1.5 text-xs flex items-center gap-1.5 shadow-sm">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                        <span>Add Environment</span>
                    </button>
                </div>

                <!-- Empty State -->
                <div id="empty-envs" class="hidden card-surface p-12 text-center space-y-4">
                    <div class="w-12 h-12 rounded-xl bg-blue-50 text-[#1e40af] flex items-center justify-center mx-auto">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                    </div>
                    <div class="space-y-1 max-w-sm mx-auto">
                        <h3 class="text-sm font-semibold text-slate-900">No environments staged yet</h3>
                        <p class="text-xs text-slate-500">Add an environment like Production or Staging with an assigned AWS region.</p>
                    </div>
                    <button onclick="showAddEnvModal()" class="btn-primary px-4 py-2 text-xs mx-auto flex items-center gap-1.5 shadow-sm">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                        <span>Add First Environment</span>
                    </button>
                </div>

                <!-- Environments Table -->
                <div id="envs-table" class="hidden card-surface overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-50/80 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
                                <tr>
                                    <th class="py-3 px-5">Environment</th>
                                    <th class="py-3 px-4">Type</th>
                                    <th class="py-3 px-4">AWS Region</th>
                                    <th class="py-3 px-4">Lifecycle Status</th>
                                    <th class="py-3 px-4">Created Date</th>
                                    <th class="py-3 px-5 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="envs-tbody" class="divide-y divide-slate-100"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Next Step Module 2 Banner -->
            <div id="module2-cta" class="hidden card-surface p-6 bg-gradient-to-r from-blue-50/70 to-indigo-50/40 border-blue-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div class="space-y-1">
                    <div class="text-[10px] font-bold text-[#1e40af] uppercase tracking-wider font-mono">Next Workflow Step</div>
                    <h3 class="text-base font-bold text-slate-900">Connect GitHub &amp; AWS Cloud Target</h3>
                    <p class="text-xs text-slate-600 max-w-xl">
                        Authorize repository access and configure IAM or Access Key credentials in Module 2 to advance this project into the deployment pipeline.
                    </p>
                </div>
                <button onclick="proceedToModule2FromProject()" class="btn-primary px-5 py-2.5 text-xs sm:text-sm shrink-0 flex items-center gap-2 shadow-sm">
                    <span>Open Module 2 Wizard</span>
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                </button>
            </div>

        </main>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════════
         ADD ENVIRONMENT MODAL
         ═══════════════════════════════════════════════════════════════════════════ -->
    <div id="add-env-modal" class="modal-overlay hidden">
        <div class="bg-white rounded-2xl w-full max-w-lg p-6 sm:p-7 space-y-6 shadow-2xl border border-slate-200">
            
            <div class="flex justify-between items-start border-b border-slate-100 pb-4">
                <div>
                    <h3 class="text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-[#1e40af]"></span>
                        Add Environment
                    </h3>
                    <p class="text-xs text-slate-500 mt-0.5">Configure deployment target stage and AWS region.</p>
                </div>
                <button onclick="hideAddEnvModal()" class="text-slate-400 hover:text-slate-700 text-xl font-bold leading-none">&times;</button>
            </div>

            <form id="add-env-form" onsubmit="submitAddEnv(event)" class="space-y-4 text-xs">
                
                <div class="space-y-1.5">
                    <label class="block font-semibold text-slate-800">Environment Name <span class="text-[#1e40af]">*</span></label>
                    <input type="text" id="ef-name" required maxlength="100" placeholder="e.g. production, staging, development"
                        class="inp-standard w-full px-3 py-2 font-mono text-xs"/>
                </div>

                <div class="space-y-1.5">
                    <label class="block font-semibold text-slate-800">Environment Type <span class="text-[#1e40af]">*</span></label>
                    <div class="grid grid-cols-3 gap-2" id="env-type-grid"></div>
                    <input type="hidden" id="ef-type" required/>
                </div>

                <div class="space-y-1.5">
                    <label class="block font-semibold text-slate-800">AWS Region <span class="text-[#1e40af]">*</span></label>
                    <select id="ef-region" required class="inp-standard w-full px-3 py-2 text-xs font-mono"></select>
                </div>

                <div class="space-y-1.5">
                    <label class="block font-semibold text-slate-800">Description <span class="text-slate-400 font-normal">(optional)</span></label>
                    <textarea id="ef-desc" rows="2" maxlength="500" placeholder="Purpose of this target environment..."
                        class="inp-standard w-full px-3 py-2 text-xs resize-none"></textarea>
                </div>

                <div id="env-err" class="hidden p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs"></div>

                <div class="flex justify-end gap-2.5 pt-3 border-t border-slate-100">
                    <button type="button" onclick="hideAddEnvModal()" class="btn-secondary px-4 py-2 text-xs">Cancel</button>
                    <button type="submit" id="env-submit" class="btn-primary px-5 py-2 text-xs flex items-center gap-2">
                        <svg id="env-spinner" class="spinner w-3.5 h-3.5 hidden" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                        <span>Add Environment</span>
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- ── TOAST ── -->
    <div id="toast" class="toast bg-white rounded-xl shadow-lg border border-slate-200 px-4 py-3 flex items-center gap-2.5 text-xs font-semibold text-slate-800">
        <span id="toast-icon" class="text-base">✓</span>
        <span id="toast-msg"></span>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════════
         APPLICATION JAVASCRIPT
         ═══════════════════════════════════════════════════════════════════════════ -->
    <script>
    const API = '';
    const adminKey = localStorage.getItem('X-Admin-Key') || 'aetherops-secret-admin-key';
    const PROJECT_ID = window.location.pathname.split('/').filter(Boolean).pop();

    const LIFECYCLE_STEPS = [
        'CREATED','CONFIGURED','REPOSITORY_CONNECTED','ANALYZED',
        'ARCHITECTURE_READY','VALIDATED','READY_TO_DEPLOY','DEPLOYING','ACTIVE'
    ];

    const ENV_TYPES = [
        { value: 'development', label: 'Development', icon: '🔧' },
        { value: 'staging',     label: 'Staging',     icon: '🔬' },
        { value: 'production',  label: 'Production',  icon: '🚀' },
    ];

    const AWS_REGIONS = [
        ['us-east-1','US East (N. Virginia)'],['us-east-2','US East (Ohio)'],['us-west-1','US West (N. California)'],
        ['us-west-2','US West (Oregon)'],['ca-central-1','Canada (Central)'],['ca-west-1','Canada West (Calgary)'],
        ['sa-east-1','South America (São Paulo)'],['eu-west-1','Europe (Ireland)'],['eu-west-2','Europe (London)'],
        ['eu-west-3','Europe (Paris)'],['eu-central-1','Europe (Frankfurt)'],['eu-central-2','Europe (Zurich)'],
        ['eu-north-1','Europe (Stockholm)'],['eu-south-1','Europe (Milan)'],['eu-south-2','Europe (Spain)'],
        ['ap-south-1','Asia Pacific (Mumbai)'],['ap-south-2','Asia Pacific (Hyderabad)'],
        ['ap-southeast-1','Asia Pacific (Singapore)'],['ap-southeast-2','Asia Pacific (Sydney)'],
        ['ap-southeast-3','Asia Pacific (Jakarta)'],['ap-southeast-4','Asia Pacific (Melbourne)'],
        ['ap-southeast-5','Asia Pacific (Malaysia)'],['ap-northeast-1','Asia Pacific (Tokyo)'],
        ['ap-northeast-2','Asia Pacific (Seoul)'],['ap-northeast-3','Asia Pacific (Osaka)'],
        ['ap-east-1','Asia Pacific (Hong Kong)'],['me-south-1','Middle East (Bahrain)'],
        ['me-central-1','Middle East (UAE)'],['il-central-1','Israel (Tel Aviv)'],
        ['af-south-1','Africa (Cape Town)'],['cn-north-1','China (Beijing)'],['cn-northwest-1','China (Ningxia)'],
    ];

    const PROJECT_TYPE_ICONS = {
        web_application:'🌐', api_service:'⚡', data_pipeline:'🔄',
        ml_workload:'🧠', static_site:'📄', microservices:'📦'
    };
    const PROJECT_TYPE_LABELS = {
        web_application:'Web Application', api_service:'API / Backend Service',
        data_pipeline:'Data Pipeline', ml_workload:'ML Workload',
        static_site:'Static Site', microservices:'Microservices',
    };

    let selectedEnvType = 'production';
    let currentProject = null;

    function headers() {
        return { 'Content-Type': 'application/json', 'X-Admin-Key': adminKey };
    }

    function toast(msg, ok = true) {
        const el = document.getElementById('toast');
        const txt = document.getElementById('toast-msg');
        const ico = document.getElementById('toast-icon');
        txt.textContent = msg;
        ico.textContent = ok ? '✅' : '⚠️';
        el.style.borderColor = ok ? '#bbf7d0' : '#fecdd3';
        el.classList.add('show');
        setTimeout(() => el.classList.remove('show'), 3500);
    }

    function logout() {
        fetch(`${API}/api/v1/auth/logout`, { method: 'POST', headers: headers() });
        window.location.href = '/login';
    }

    async function loadProject() {
        try {
            const res = await fetch(`${API}/api/v1/projects/${PROJECT_ID}`, { headers: headers() });
            if (res.status === 401) { window.location.href = '/login'; return; }
            if (!res.ok) throw new Error(await res.text());
            const p = await res.json();
            currentProject = p;
            renderProject(p);
        } catch(e) {
            document.getElementById('loading-state').innerHTML = `<p class="text-rose-600 text-xs font-semibold">${e.message}</p>`;
        }
    }

    function renderProject(p) {
        document.getElementById('loading-state').classList.add('hidden');
        document.getElementById('project-header').classList.remove('hidden');
        document.getElementById('lifecycle-stepper-card').classList.remove('hidden');
        document.getElementById('envs-section').classList.remove('hidden');
        document.getElementById('module2-cta').classList.remove('hidden');

        document.getElementById('header-project-name').textContent = p.name;
        document.title = `AetherOps — ${p.name}`;

        document.getElementById('proj-icon').textContent = PROJECT_TYPE_ICONS[p.project_type] || '📦';
        document.getElementById('proj-name').textContent = p.name;
        document.getElementById('proj-type-label').textContent = PROJECT_TYPE_LABELS[p.project_type] || p.project_type;
        document.getElementById('proj-owner').textContent = p.owner || 'root_admin';
        document.getElementById('proj-created').textContent = p.created_at
            ? new Date(p.created_at).toLocaleDateString('en-US', { day:'2-digit', month:'short', year:'numeric' }) : '—';
        document.getElementById('proj-env-count').textContent = p.environment_count || 0;
        document.getElementById('proj-desc').textContent = p.description || 'No description provided for this workspace.';

        const badge = document.getElementById('proj-status-badge');
        if(p.status === 'ACTIVE') {
            badge.className = 'px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono tracking-wide bg-emerald-50 text-emerald-700 border border-emerald-200';
            badge.textContent = 'ACTIVE';
        } else if(p.status === 'ARCHIVED') {
            badge.className = 'px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono tracking-wide bg-slate-100 text-slate-600 border border-slate-200';
            badge.textContent = 'ARCHIVED';
        } else {
            badge.className = 'px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono tracking-wide bg-blue-50 text-[#1e40af] border border-blue-200';
            badge.textContent = 'CREATED';
        }

        // Link Module 2 and Module 3
        const m2Url = `http://localhost:8010/app/source?project_id=${encodeURIComponent(PROJECT_ID)}`;
        document.getElementById('hdr-module2-btn').href = m2Url;
        document.getElementById('nav-module2-link').href = m2Url;

        renderEnvironments(p.environments || []);
    }

    function renderEnvironments(envs) {
        const empty = document.getElementById('empty-envs');
        const table = document.getElementById('envs-table');
        const tbody = document.getElementById('envs-tbody');

        if (envs.length === 0) {
            empty.classList.remove('hidden');
            table.classList.add('hidden');
            return;
        }
        empty.classList.add('hidden');
        table.classList.remove('hidden');
        tbody.innerHTML = '';

        envs.forEach(e => {
            const typeInfo = ENV_TYPES.find(t => t.value === e.env_type) || { icon: '🔧', label: e.env_type };
            const stepIdx  = LIFECYCLE_STEPS.indexOf(e.status);
            const isFailed = e.status === 'FAILED';
            const pct      = isFailed ? 0 : Math.round(((stepIdx + 1) / LIFECYCLE_STEPS.length) * 100);

            const typePillClass = e.env_type === 'production' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                                  (e.env_type === 'staging' ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-amber-50 text-amber-700 border-amber-200');

            const statusClass = e.status === 'ACTIVE' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                                (e.status === 'REPOSITORY_CONNECTED' ? 'bg-blue-50 text-[#1e40af] border-blue-200' :
                                (e.status === 'ANALYZED' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' :
                                (e.status === 'DEPLOYING' ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-slate-100 text-slate-700 border-slate-200')));

            const date = e.created_at ? new Date(e.created_at).toLocaleDateString('en-US', { day:'2-digit', month:'short', year:'numeric' }) : '—';
            const m2EnvUrl = `http://localhost:8010/app/source?project_id=${encodeURIComponent(PROJECT_ID)}&environment_id=${encodeURIComponent(e.id)}`;
            const m3EnvUrl = `http://localhost:8001/app?project_id=${encodeURIComponent(PROJECT_ID)}&environment_id=${encodeURIComponent(e.id)}`;

            tbody.innerHTML += `
            <tr class="hover:bg-slate-50/80 transition">
                <td class="px-5 py-3.5">
                    <div class="flex items-center gap-2.5">
                        <span class="text-base">${typeInfo.icon}</span>
                        <div>
                            <div class="font-bold text-slate-900 text-xs">${escHtml(e.name)}</div>
                            <div class="text-[10px] text-slate-400 font-mono">${escHtml(e.id.slice(0, 8))}…</div>
                        </div>
                    </div>
                </td>
                <td class="px-4 py-3.5">
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold font-mono border ${typePillClass}">
                        ${e.env_type.toUpperCase()}
                    </span>
                </td>
                <td class="px-4 py-3.5 font-mono text-xs font-semibold text-slate-800">${e.aws_region}</td>
                <td class="px-4 py-3.5">
                    <div class="space-y-1">
                        <span class="inline-block px-2 py-0.5 rounded text-[10px] font-bold font-mono border ${statusClass}">
                            ${e.status}
                        </span>
                        <div class="flex items-center gap-1.5">
                            <div class="w-24 h-1.5 rounded-full bg-slate-100 overflow-hidden">
                                <div class="h-full rounded-full ${isFailed ? 'bg-rose-500' : 'bg-[#1e40af]'}" style="width: ${pct}%"></div>
                            </div>
                            <span class="text-[10px] text-slate-400 font-mono font-medium">${pct}%</span>
                        </div>
                    </div>
                </td>
                <td class="px-4 py-3.5 text-slate-500 font-mono text-[11px]">${date}</td>
                <td class="px-5 py-3.5 text-right">
                    <div class="flex items-center justify-end gap-1.5 flex-wrap">
                        <a href="${m2EnvUrl}" target="_blank" class="px-2.5 py-1 text-[11px] font-semibold text-[#1e40af] bg-blue-50 hover:bg-blue-100 rounded-md transition" title="Module 2: Connect Source & Cloud">
                            Module 2
                        </a>
                        <a href="${m3EnvUrl}" target="_blank" class="px-2.5 py-1 text-[11px] font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 rounded-md transition" title="Module 3: Repo Analyzer">
                            Module 3
                        </a>
                        <button onclick="deleteEnv('${e.id}','${escHtml(e.name)}')" class="px-2 py-1 text-[11px] font-medium text-rose-600 hover:bg-rose-50 rounded-md transition">
                            Delete
                        </button>
                    </div>
                </td>
            </tr>`;
        });
    }

    function proceedToModule2FromProject() {
        let url = `http://localhost:8010/app/source?project_id=${encodeURIComponent(PROJECT_ID)}`;
        if (currentProject && currentProject.environments && currentProject.environments.length > 0) {
            url += `&environment_id=${encodeURIComponent(currentProject.environments[0].id)}`;
        }
        window.location.href = url;
    }

    async function archiveProject() {
        if (!confirm('Archive this project? It will no longer appear as active.')) return;
        const res = await fetch(`${API}/api/v1/projects/${PROJECT_ID}`, {
            method: 'PATCH', headers: headers(), body: JSON.stringify({ status: 'ARCHIVED' })
        });
        if (res.ok) { toast('Project archived.'); await loadProject(); }
        else toast('Failed to archive project.', false);
    }

    async function deleteProject() {
        if (!confirm('Delete this project and ALL its environments? This action cannot be undone.')) return;
        const res = await fetch(`${API}/api/v1/projects/${PROJECT_ID}`, {
            method: 'DELETE', headers: headers()
        });
        if (res.ok) { toast('Project deleted. Redirecting…'); setTimeout(() => window.location.href = '/app', 1200); }
        else toast('Failed to delete project.', false);
    }

    async function deleteEnv(envId, envName) {
        if (!confirm(`Delete environment "${envName}"? This action cannot be undone.`)) return;
        const res = await fetch(`${API}/api/v1/projects/${PROJECT_ID}/environments/${envId}`, {
            method: 'DELETE', headers: headers()
        });
        if (res.ok) { toast(`Environment "${envName}" deleted.`); await loadProject(); }
        else toast('Failed to delete environment.', false);
    }

    // ── Add Environment Modal ─────────────────────────────────────────────────────
    function renderEnvTypeGrid() {
        const grid = document.getElementById('env-type-grid');
        grid.innerHTML = '';
        ENV_TYPES.forEach(t => {
            const active = selectedEnvType === t.value;
            grid.innerHTML += `
            <button type="button" onclick="selectEnvType('${t.value}')"
                class="flex items-center gap-1.5 p-2 rounded-xl text-xs font-semibold border transition
                       ${active ? 'border-[#1e40af] bg-blue-50/70 text-[#1e40af]' : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'}">
                <span>${t.icon}</span><span>${t.label}</span>
            </button>`;
        });
    }

    function selectEnvType(val) {
        selectedEnvType = val;
        document.getElementById('ef-type').value = val;
        renderEnvTypeGrid();
    }

    function populateRegionDropdown() {
        const sel = document.getElementById('ef-region');
        sel.innerHTML = '<option value="">— Select an AWS region —</option>';
        AWS_REGIONS.forEach(([code, name]) => {
            const isDef = code === 'us-east-1' ? 'selected' : '';
            sel.innerHTML += `<option value="${code}" ${isDef}>${code} — ${name}</option>`;
        });
    }

    function showAddEnvModal() {
        selectedEnvType = 'production';
        document.getElementById('ef-name').value = 'production';
        document.getElementById('ef-desc').value = '';
        document.getElementById('ef-type').value = 'production';
        document.getElementById('env-err').classList.add('hidden');
        renderEnvTypeGrid();
        populateRegionDropdown();
        document.getElementById('add-env-modal').classList.remove('hidden');
        setTimeout(() => document.getElementById('ef-name').focus(), 50);
    }

    function hideAddEnvModal() {
        document.getElementById('add-env-modal').classList.add('hidden');
    }

    async function submitAddEnv(e) {
        e.preventDefault();
        const name   = document.getElementById('ef-name').value.trim();
        const type   = document.getElementById('ef-type').value;
        const region = document.getElementById('ef-region').value;
        const desc   = document.getElementById('ef-desc').value.trim();
        const errEl  = document.getElementById('env-err');
        const btn    = document.getElementById('env-submit');
        const spin   = document.getElementById('env-spinner');

        if (!type)   { errEl.textContent = 'Please choose an environment type.'; errEl.classList.remove('hidden'); return; }
        if (!region) { errEl.textContent = 'Please select an AWS region.';       errEl.classList.remove('hidden'); return; }

        errEl.classList.add('hidden');
        btn.disabled = true; spin.classList.remove('hidden');

        try {
            const res = await fetch(`${API}/api/v1/projects/${PROJECT_ID}/environments`, {
                method: 'POST', headers: headers(),
                body: JSON.stringify({ name, env_type: type, aws_region: region, description: desc || null }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || JSON.stringify(data));

            hideAddEnvModal();
            toast(`Environment "${name}" staged!`);
            await loadProject();
        } catch(err) {
            errEl.textContent = err.message; errEl.classList.remove('hidden');
        } finally {
            btn.disabled = false; spin.classList.add('hidden');
        }
    }

    function escHtml(s) {
        const d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML;
    }

    document.getElementById('add-env-modal').addEventListener('click', e => {
        if (e.target === document.getElementById('add-env-modal')) hideAddEnvModal();
    });

    function toggleMobileDrawer() {
        const drawer = document.getElementById('mobile-drawer');
        const backdrop = document.getElementById('mobile-drawer-backdrop');
        if (!drawer || !backdrop) return;
        const isOpen = !drawer.classList.contains('-translate-x-full');
        if (isOpen) {
            drawer.classList.add('-translate-x-full');
            backdrop.classList.add('hidden');
        } else {
            drawer.classList.remove('-translate-x-full');
            backdrop.classList.remove('hidden');
        }
    }

    window.addEventListener('DOMContentLoaded', loadProject);
    </script>
</body>
</html>
"""
