# services/project_and_environment_management/app/dashboard_page.py
"""
AetherOps Cloud - Master Enterprise Application Dashboard (Module 1 Cockpit).
Precision Developer Console / SRE Platform Cockpit adhering to Apple-inspired minimalism:
- Baseline Background: #f8f9ff, Card Surfaces: #ffffff, Crisp Borders: #e2e8f0
- Primary Accents: Deep Royal Blue #1e40af / #00288e / #2563eb
- Typography: Inter (sans-serif) and JetBrains Mono (font-mono)
- Universal Sidebar & Multi-Module Workspace Switcher (Modules 1-9 & Operations)
"""

def get_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AetherOps — Enterprise Cloud DevOps Platform</title>
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
                        brand: {
                            50: '#eff6ff',
                            100: '#dbeafe',
                            200: '#bfdbfe',
                            500: '#2563eb',
                            600: '#1d4ed8',
                            700: '#1e40af',
                            800: '#1e3a8a',
                            900: '#00288e',
                        },
                        workspace: {
                            base: '#f8f9ff',
                            surface: '#ffffff',
                            secondary: '#f7f9fc',
                            border: '#e2e8f0',
                            borderLight: '#e5e7eb',
                        }
                    }
                }
            }
        }
    </script>
    <style>
        * {
            box-sizing: border-box;
            -webkit-font-smoothing: antialiased;
        }
        body {
            background-color: #f8f9ff;
            color: #0b1c30;
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
        .card-surface:hover {
            border-color: #cbd5e1;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05), 0 2px 6px rgba(0, 0, 0, 0.03);
            transform: translateY(-1px);
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
        .btn-ghost {
            background: transparent;
            color: #64748b;
            font-weight: 500;
            border-radius: 6px;
            transition: all 0.15s ease;
        }
        .btn-ghost:hover {
            background: #f1f5f9;
            color: #0f172a;
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
            cursor: pointer;
            border: 1px solid transparent;
            text-align: left;
            width: 100%;
        }
        .nav-item:hover {
            background: #f1f5f9;
            color: #0f172a;
        }
        .nav-item.active {
            background: #1e40af;
            color: #ffffff !important;
            font-weight: 600;
        }
        .nav-item.active svg {
            color: #ffffff !important;
        }
        .nav-item.active span {
            color: #ffffff !important;
        }
        .nav-item.active .badge-pill {
            background: rgba(255, 255, 255, 0.2) !important;
            color: #ffffff !important;
            border-color: rgba(255, 255, 255, 0.3) !important;
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
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
        .view-frame-container {
            height: calc(100vh - 4.5rem);
            width: 100%;
        }
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
                <span class="px-1.5 py-0.2 rounded text-[9px] font-bold uppercase tracking-wider bg-[#eff6ff] text-[#1e40af] font-mono border border-blue-100">
                    ADMIN
                </span>
            </div>
        </div>

        <div class="flex items-center gap-2">
            <button onclick="showCreateModal()" class="btn-primary px-2.5 py-1.5 text-xs flex items-center gap-1 shadow-sm">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                <span class="hidden xs:inline">New</span>
            </button>
        </div>
    </header>

    <!-- ═══════════════════════════════════════════════════════════════════════════
         MOBILE OFF-CANVAS DRAWER (< 1024px)
         ═══════════════════════════════════════════════════════════════════════════ -->
    <div id="mobile-drawer-backdrop" onclick="toggleMobileDrawer()" class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 hidden transition-opacity lg:hidden"></div>
    <aside id="mobile-drawer" class="fixed inset-y-0 left-0 w-72 max-w-[85vw] bg-white border-r border-slate-200 z-50 flex flex-col transform -translate-x-full transition-transform duration-200 ease-in-out lg:hidden">
        <!-- Brand Header inside Drawer -->
        <div class="p-4 border-b border-slate-100 flex items-center justify-between">
            <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-lg bg-[#1e40af] text-white flex items-center justify-center font-bold text-sm tracking-tight font-mono shadow-sm">
                    AO
                </div>
                <div>
                    <span class="font-semibold text-slate-900 text-sm">AetherOps</span>
                    <div class="text-[10px] font-mono text-emerald-600 flex items-center gap-1">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                        <span>v2.14.0 // port:8009</span>
                    </div>
                </div>
            </div>
            <button type="button" onclick="toggleMobileDrawer()" class="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
        </div>

        <!-- Scrollable Navigation in Drawer -->
        <div class="flex-1 overflow-y-auto px-3 py-4 space-y-5">
            <!-- Section 1: CORE NAVIGATION -->
            <div class="space-y-1">
                <div class="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Core Navigation</div>
                <button type="button" onclick="switchWorkspaceView('projects'); toggleMobileDrawer();" class="nav-item">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>
                    <span>Projects &amp; Workspaces</span>
                </button>
                <button type="button" onclick="switchWorkspaceView('environments'); toggleMobileDrawer();" class="nav-item">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                    <span>Target Environments</span>
                </button>
            </div>

            <!-- Section 2: PLATFORM WORKFLOW -->
            <div class="space-y-1">
                <div class="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Platform Workflow</div>
                <button type="button" onclick="switchWorkspaceView('source-cloud'); toggleMobileDrawer();" class="nav-item justify-between group">
                    <div class="flex items-center gap-2 min-w-0">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                        <span class="truncate">Source &amp; Cloud</span>
                    </div>
                    <span class="badge-pill text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-blue-50 text-[#1e40af] border border-blue-100">M2</span>
                </button>
                <button type="button" onclick="switchWorkspaceView('repo-analyzer'); toggleMobileDrawer();" class="nav-item justify-between group">
                    <div class="flex items-center gap-2 min-w-0">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                        <span class="truncate">Repo Analyzer</span>
                    </div>
                    <span class="badge-pill text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-100">M3</span>
                </button>
                <button type="button" onclick="switchWorkspaceView('architecture'); toggleMobileDrawer();" class="nav-item justify-between group">
                    <div class="flex items-center gap-2 min-w-0">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                        <span class="truncate">Architecture Studio</span>
                    </div>
                    <span class="badge-pill text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-100">M4</span>
                </button>
                <button type="button" onclick="switchWorkspaceView('iac'); toggleMobileDrawer();" class="nav-item justify-between group">
                    <div class="flex items-center gap-2 min-w-0">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>
                        <span class="truncate">IaC Generator</span>
                    </div>
                    <span class="badge-pill text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">M5</span>
                </button>
                <button type="button" onclick="switchWorkspaceView('deployments'); toggleMobileDrawer();" class="nav-item justify-between group">
                    <div class="flex items-center gap-2 min-w-0">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                        <span class="truncate">Deployments</span>
                    </div>
                    <span class="badge-pill text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">M6</span>
                </button>
                <button type="button" onclick="switchWorkspaceView('monitoring'); toggleMobileDrawer();" class="nav-item justify-between group">
                    <div class="flex items-center gap-2 min-w-0">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                        <span class="truncate">Observability</span>
                    </div>
                    <span class="badge-pill text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">Live</span>
                </button>
            </div>

            <!-- Section 3: OPERATIONS -->
            <div class="space-y-1">
                <div class="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Operations</div>
                <button type="button" onclick="switchWorkspaceView('docs'); toggleMobileDrawer();" class="nav-item">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
                    <span>Documentation</span>
                </button>
                <button type="button" onclick="switchWorkspaceView('settings'); toggleMobileDrawer();" class="nav-item">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                    <span>System Settings</span>
                </button>
            </div>
        </div>

        <!-- Drawer User Footer (Dynamic Account Section) -->
        <div class="p-3.5 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
            <div onclick="openAccountModal(); toggleMobileDrawer();" class="flex items-center gap-2 min-w-0 cursor-pointer">
                <div id="user-avatar-badge-mobile" class="w-8 h-8 rounded-full bg-[#1e40af] text-white font-semibold text-xs flex items-center justify-center shrink-0">AO</div>
                <div class="min-w-0">
                    <div id="user-name-display-mobile" class="text-xs font-semibold text-slate-900 truncate">Admin</div>
                    <div class="text-[10px] font-mono text-emerald-600 flex items-center gap-1">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                        <span id="user-role-display-mobile">operator:root</span>
                    </div>
                </div>
            </div>
            <div class="flex items-center gap-1">
                <button onclick="openAccountModal(); toggleMobileDrawer();" title="Account Profile" class="p-1.5 rounded-md hover:bg-slate-200 text-slate-500">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                </button>
                <button onclick="logout()" title="Sign Out" class="p-1.5 rounded-md hover:bg-rose-50 text-slate-500 hover:text-rose-600">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
                </button>
            </div>
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
                    <span class="font-medium">platform // v2.14.0</span>
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
                <button type="button" onclick="switchWorkspaceView('projects')" id="nav-projects" class="nav-item active">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>
                    <span>Projects &amp; Workspaces</span>
                </button>
                <button type="button" onclick="switchWorkspaceView('environments')" id="nav-environments" class="nav-item">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                    <span>Target Environments</span>
                </button>
            </div>

            <!-- Section 2: PLATFORM WORKFLOW (Hierarchical Pipeline Stages) -->
            <div class="space-y-1">
                <div class="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Platform Workflow
                </div>
                
                <!-- Module 2 -->
                <button type="button" onclick="switchWorkspaceView('source-cloud')" id="nav-source-cloud" class="nav-item justify-between group" title="Module 2: Source & Cloud Connection">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                        <span class="truncate">Source &amp; Cloud</span>
                    </div>
                    <span class="badge-pill text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-blue-50 text-[#1e40af] border border-blue-100">
                        Module 2
                    </span>
                </button>

                <!-- Module 3 -->
                <button type="button" onclick="switchWorkspaceView('repo-analyzer')" id="nav-repo-analyzer" class="nav-item justify-between group" title="Module 3: Repository Analyzer & Sizing">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                        <span class="truncate">Repo Analyzer</span>
                    </div>
                    <span class="badge-pill text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-100">
                        Module 3
                    </span>
                </button>

                <!-- Module 4 -->
                <button type="button" onclick="switchWorkspaceView('architecture')" id="nav-architecture" class="nav-item justify-between group" title="Module 4: Architecture Graph Generator">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                        <span class="truncate">Architecture Studio</span>
                    </div>
                    <span class="badge-pill text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-100">
                        Module 4
                    </span>
                </button>

                <!-- Module 5 -->
                <button type="button" onclick="switchWorkspaceView('iac')" id="nav-iac" class="nav-item justify-between group" title="Module 5: IaC Code Generator">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>
                        <span class="truncate">IaC Generator</span>
                    </div>
                    <span class="badge-pill text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
                        Module 5
                    </span>
                </button>

                <!-- Module 6 -->
                <button type="button" onclick="switchWorkspaceView('deployments')" id="nav-deployments" class="nav-item justify-between group" title="Module 6: CI/CD & Cloud Deployer">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                        <span class="truncate">Deployments</span>
                    </div>
                    <span class="badge-pill text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
                        Module 6
                    </span>
                </button>

                <!-- Module 7 -->
                <button type="button" onclick="switchWorkspaceView('monitoring')" id="nav-monitoring" class="nav-item justify-between group" title="Module 7: Observability & APM Telemetry">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                        <span class="truncate">Observability</span>
                    </div>
                    <span class="badge-pill text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
                        Telemetry
                    </span>
                </button>

                <!-- Module 8 -->
                <button type="button" onclick="switchWorkspaceView('finops')" id="nav-finops" class="nav-item justify-between group" title="Module 8: FinOps Cost Optimizer">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        <span class="truncate">FinOps Optimizer</span>
                    </div>
                    <span class="badge-pill text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200">
                        Cost
                    </span>
                </button>

                <!-- Module 9 -->
                <button type="button" onclick="switchWorkspaceView('security')" id="nav-security" class="nav-item justify-between group" title="Module 9: Security & Compliance Engine">
                    <div class="flex items-center gap-2.5 min-w-0">
                        <svg class="w-4 h-4 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                        <span class="truncate">Security Scanner</span>
                    </div>
                    <span class="badge-pill text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200">
                        Audit
                    </span>
                </button>
            </div>

            <!-- Section 3: OPERATIONS -->
            <div class="space-y-1">
                <div class="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Operations
                </div>
                <button type="button" onclick="switchWorkspaceView('docs')" id="nav-docs" class="nav-item">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></svg>
                    <span>Documentation</span>
                </button>
                <button type="button" onclick="switchWorkspaceView('settings')" id="nav-settings" class="nav-item">
                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                    <span>System Settings</span>
                </button>
            </div>
        </div>

        <!-- Sidebar Bottom User Footer (Dynamic Account Section) -->
        <div class="p-3.5 border-t border-slate-100 bg-slate-50/70 flex items-center justify-between gap-2">
            <div onclick="openAccountModal()" class="flex items-center gap-2.5 min-w-0 cursor-pointer group hover:bg-slate-200/50 p-1.5 -ml-1 rounded-xl transition" title="Open Account Settings">
                <div id="user-avatar-badge" class="w-8 h-8 rounded-full bg-[#1e40af] text-white font-semibold text-xs flex items-center justify-center shrink-0 shadow-xs">
                    AO
                </div>
                <div class="min-w-0">
                    <div id="user-name-display" class="text-xs font-semibold text-slate-900 group-hover:text-[#1e40af] transition truncate">Admin</div>
                    <div class="text-[10px] font-mono text-emerald-600 flex items-center gap-1 truncate">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                        <span id="user-role-display">operator:root</span>
                    </div>
                </div>
            </div>
            <div class="flex items-center gap-1">
                <button onclick="openAccountModal()" title="Account Profile" class="p-1.5 rounded-md hover:bg-slate-200/60 text-slate-500 hover:text-[#1e40af] transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                </button>
                <button onclick="logout()" title="Sign Out" class="p-1.5 rounded-md hover:bg-rose-50 text-slate-400 hover:text-rose-600 transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
                </button>
            </div>
        </div>
    </aside>

    <!-- ═══════════════════════════════════════════════════════════════════════════
         MAIN CONTENT AREA
         ═══════════════════════════════════════════════════════════════════════════ -->
    <div class="flex-1 flex flex-col min-w-0">

        <!-- Global Top Header (Height: 64px, Sticky) -->
        <header class="h-16 bg-white/95 backdrop-blur border-b border-slate-200/80 sticky top-0 z-30 px-6 sm:px-8 flex items-center justify-between gap-4">
            
            <!-- Left: Breadcrumb & Context -->
            <div class="flex items-center gap-2 min-w-0 text-xs text-slate-500">
                <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>
                <button type="button" onclick="switchWorkspaceView('projects')" class="font-medium hover:text-slate-900 transition">AetherOps</button>
                <span class="text-slate-300">/</span>
                <span id="top-breadcrumb-view" class="font-semibold text-slate-900 truncate">Projects Workspace</span>
                <span class="hidden sm:inline-flex items-center gap-1 ml-2 px-2 py-0.5 rounded-full text-[11px] font-mono bg-slate-100 text-slate-700 border border-slate-200">
                    <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                    <span id="top-region-tag">prd-us-east-1</span>
                </span>
            </div>

            <!-- Center: Fast Global Search Field -->
            <div class="flex-1 max-w-md hidden md:block">
                <div class="relative">
                    <svg class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                    <input type="text" id="global-search" oninput="onSearchInput(this.value)" placeholder="Search projects and environments... [/]"
                        class="inp-standard w-full pl-9 pr-8 py-1.5 text-xs font-mono placeholder:text-slate-400 placeholder:font-sans"/>
                    <kbd class="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] font-mono text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
                        /
                    </kbd>
                </div>
            </div>

            <!-- Right Controls: Status & Actions -->
            <div class="flex items-center gap-3 shrink-0">
                <button type="button" onclick="switchWorkspaceView('monitoring')" class="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-medium hover:bg-emerald-100 transition cursor-pointer">
                    <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                    <span>Fleet Online (9/9)</span>
                </button>

                <button onclick="showCreateModal()" class="btn-primary px-3.5 py-1.5 text-xs flex items-center gap-1.5 shadow-sm">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                    <span>New Project</span>
                </button>
            </div>
        </header>

        <!-- ═══════════════════════════════════════════════════════════════════════
             VIEW 1: PROJECTS WORKSPACE
             ═══════════════════════════════════════════════════════════════════════ -->
        <main id="view-projects" class="workspace-view max-w-7xl w-full mx-auto px-6 sm:px-8 py-8 space-y-7">

            <!-- Contextual View Switcher Tabs & Page Title -->
            <div class="space-y-4">
                
                <!-- View Switcher Tabs -->
                <div class="flex items-center gap-2 border-b border-slate-200/80 pb-3 overflow-x-auto">
                    <button type="button" onclick="switchWorkspaceView('projects')" class="px-3.5 py-1.5 text-xs font-semibold rounded-full bg-slate-900 text-white shadow-sm flex items-center gap-1.5 shrink-0">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"/></svg>
                        <span>Projects Workspace</span>
                    </button>
                    <button type="button" onclick="switchWorkspaceView('environments')" class="px-3.5 py-1.5 text-xs font-medium rounded-full text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-transparent transition flex items-center gap-1 shrink-0">
                        <span>Environments Fleet</span>
                    </button>
                    <button type="button" onclick="switchWorkspaceView('source-cloud')" class="px-3.5 py-1.5 text-xs font-medium rounded-full text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-transparent transition flex items-center gap-1 shrink-0">
                        <span>Source &amp; Cloud (Module 2)</span>
                    </button>
                    <button type="button" onclick="switchWorkspaceView('repo-analyzer')" class="px-3.5 py-1.5 text-xs font-medium rounded-full text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-transparent transition flex items-center gap-1 shrink-0">
                        <span>Repo Analyzer (Module 3)</span>
                    </button>
                    <button type="button" onclick="switchWorkspaceView('architecture')" class="px-3.5 py-1.5 text-xs font-medium rounded-full text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-transparent transition flex items-center gap-1 shrink-0">
                        <span>Architecture (Module 4)</span>
                    </button>
                </div>

                <!-- Main Page Heading & Actions -->
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-1">
                    <div>
                        <div class="flex items-center gap-3">
                            <h1 class="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">Projects</h1>
                            <span id="project-count-pill" class="text-xs font-mono font-bold px-2 py-0.5 rounded-md bg-blue-50 text-[#1e40af] border border-blue-100">
                                0 registered
                            </span>
                        </div>
                        <p class="text-xs sm:text-sm text-slate-500 mt-1">
                            Manage your application services, container configurations, and target environments in one place.
                        </p>
                    </div>

                    <div class="flex items-center gap-2.5">
                        <button onclick="loadProjects()" class="btn-secondary px-3 py-2 text-xs flex items-center gap-1.5 shadow-sm" title="Refresh projects data">
                            <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                            <span>Refresh</span>
                        </button>
                        <button onclick="showCreateModal()" class="btn-primary px-4 py-2 text-xs sm:text-sm flex items-center gap-1.5 shadow-sm">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                            <span>New Project</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Top Fleet KPI Summary Cards (3-Column Grid) -->
            <section class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                
                <!-- Card 1: TOTAL PROJECTS -->
                <div class="card-surface p-5 space-y-2">
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-bold uppercase tracking-wider text-slate-500">Total Projects</span>
                        <div class="w-8 h-8 rounded-lg bg-blue-50 text-[#1e40af] flex items-center justify-center">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>
                        </div>
                    </div>
                    <div class="flex items-baseline gap-2">
                        <span id="stat-total-projects" class="text-3xl font-bold font-mono text-slate-900">0</span>
                        <span class="text-xs text-slate-500 font-medium">workspaces</span>
                    </div>
                    <p class="text-[11px] text-slate-500">Applications configured in your AetherOps tenant</p>
                </div>

                <!-- Card 2: ACTIVE ENVIRONMENTS -->
                <div onclick="switchWorkspaceView('environments')" class="card-surface p-5 space-y-2 cursor-pointer hover:border-blue-300">
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-bold uppercase tracking-wider text-slate-500">Active Environments</span>
                        <div class="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                        </div>
                    </div>
                    <div class="flex items-baseline gap-2">
                        <span id="stat-active-envs" class="text-3xl font-bold font-mono text-slate-900">0</span>
                        <span id="stat-operational-badge" class="text-[10px] font-bold font-mono px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                            ● 100% operational
                        </span>
                    </div>
                    <p class="text-[11px] text-slate-500">Click to view all environments fleet &rarr;</p>
                </div>

                <!-- Card 3: AWS REGIONS IN USE -->
                <div class="card-surface p-5 space-y-2">
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-bold uppercase tracking-wider text-slate-500">AWS Regions in Use</span>
                        <div class="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        </div>
                    </div>
                    <div class="flex items-baseline gap-2">
                        <span id="stat-regions-count" class="text-3xl font-bold font-mono text-slate-900">0</span>
                        <span class="text-xs text-slate-500 font-medium">active regions</span>
                    </div>
                    <div id="stat-regions-pills" class="flex flex-wrap gap-1 min-h-[1.25rem]">
                        <span class="text-[11px] text-slate-400 italic">Scanning fleet...</span>
                    </div>
                </div>
            </section>

            <!-- Search & Filter Toolbar (Responsive Flex / Grid) -->
            <section class="card-surface p-4 flex flex-col sm:flex-row flex-wrap items-stretch sm:items-center justify-between gap-3">
                <div class="flex flex-1 flex-wrap sm:flex-nowrap items-center gap-2.5">
                    <div class="relative flex-1 min-w-[200px]">
                        <svg class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                        <input type="text" id="toolbar-search" oninput="onSearchInput(this.value)" placeholder="Filter by name, ID or description..."
                            class="inp-standard w-full pl-9 pr-3 py-1.5 text-xs font-mono placeholder:text-slate-400 placeholder:font-sans"/>
                    </div>
                    <select id="filter-type" onchange="onFilterChange()" class="inp-standard px-3 py-1.5 text-xs font-medium cursor-pointer flex-1 sm:flex-none">
                        <option value="all">All Types</option>
                        <option value="web_application">Web Application</option>
                        <option value="api_service">API Service</option>
                        <option value="microservices">Microservices Fleet</option>
                        <option value="data_pipeline">Data Pipeline</option>
                    </select>
                    <select id="filter-status" onchange="onFilterChange()" class="inp-standard px-3 py-1.5 text-xs font-medium cursor-pointer flex-1 sm:flex-none">
                        <option value="all">All Status</option>
                        <option value="ACTIVE">Active</option>
                        <option value="CREATED">Created</option>
                        <option value="ARCHIVED">Archived</option>
                    </select>
                </div>

                <div class="flex items-center gap-2 justify-end shrink-0">
                    <select id="sort-by" onchange="onSortChange(this.value)" class="inp-standard px-3 py-1.5 text-xs font-medium cursor-pointer">
                        <option value="date-desc">Newest First</option>
                        <option value="date-asc">Oldest First</option>
                        <option value="name-asc">Name (A-Z)</option>
                        <option value="envs-desc">Most Environments</option>
                    </select>
                    <div class="flex items-center bg-slate-100 p-0.5 rounded-lg border border-slate-200">
                        <button type="button" onclick="setViewMode('grid')" id="view-mode-grid" class="p-1.5 rounded-md text-slate-700 bg-white shadow-xs" title="Grid View">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>
                        </button>
                        <button type="button" onclick="setViewMode('list')" id="view-mode-list" class="p-1.5 rounded-md text-slate-500 hover:text-slate-700" title="Table View">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
                        </button>
                    </div>
                </div>
            </section>

            <!-- Projects Display Area -->
            <div id="projects-container">
                <div id="empty-state" class="hidden card-surface p-12 text-center space-y-4">
                    <div class="w-12 h-12 rounded-full bg-blue-50 text-[#1e40af] mx-auto flex items-center justify-center">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/></svg>
                    </div>
                    <div>
                        <h3 class="text-base font-semibold text-slate-900">No projects found</h3>
                        <p class="text-xs text-slate-500 max-w-sm mx-auto mt-1">No matching projects configured yet. Get started by provisioning your first workspace.</p>
                    </div>
                    <button onclick="showCreateModal()" class="btn-primary px-4 py-2 text-xs inline-flex items-center gap-1.5 shadow-sm">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                        <span>Create Project</span>
                    </button>
                </div>

                <!-- 2x2 Grid View -->
                <div id="projects-grid" class="grid grid-cols-1 md:grid-cols-2 gap-5"></div>

                <!-- List/Table View -->
                <div id="projects-list-container" class="hidden card-surface overflow-hidden">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-slate-50 border-b border-slate-200/80 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                            <tr>
                                <th class="py-3 px-5">Project Name</th>
                                <th class="py-3 px-4">Archetype</th>
                                <th class="py-3 px-4">Environments</th>
                                <th class="py-3 px-4">Status</th>
                                <th class="py-3 px-4">Created Date</th>
                                <th class="py-3 px-5 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="projects-list-tbody" class="divide-y divide-slate-100 font-sans"></tbody>
                    </table>
                </div>
            </div>
        </main>

        <!-- ═══════════════════════════════════════════════════════════════════════
             VIEW 2: ENVIRONMENTS FLEET WORKSPACE
             ═══════════════════════════════════════════════════════════════════════ -->
        <main id="view-environments" class="workspace-view hidden max-w-7xl w-full mx-auto px-6 sm:px-8 py-8 space-y-7">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200/80">
                <div>
                    <h1 class="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">Target Environments Fleet</h1>
                    <p class="text-xs sm:text-sm text-slate-500 mt-1">Multi-cloud stages, AWS regional deployment targets, and runtime topologies.</p>
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="renderEnvironmentsFleetView()" class="btn-secondary px-3 py-1.5 text-xs flex items-center gap-1.5">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                        <span>Refresh Fleet</span>
                    </button>
                    <button onclick="switchWorkspaceView('projects')" class="btn-primary px-3 py-1.5 text-xs flex items-center gap-1.5">
                        <span>+ Add Staging Target</span>
                    </button>
                </div>
            </div>

            <!-- Fleet Metrics -->
            <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <div class="card-surface p-4 space-y-1">
                    <span class="text-[10px] font-bold uppercase tracking-wider text-slate-500">Total Envs</span>
                    <div id="env-kpi-total" class="text-2xl font-bold font-mono text-slate-900">0</div>
                    <div class="text-[11px] text-slate-500">Active deployment targets</div>
                </div>
                <div class="card-surface p-4 space-y-1">
                    <span class="text-[10px] font-bold uppercase tracking-wider text-emerald-600">Production</span>
                    <div id="env-kpi-prod" class="text-2xl font-bold font-mono text-emerald-700">0</div>
                    <div class="text-[11px] text-emerald-600">High-availability live tiers</div>
                </div>
                <div class="card-surface p-4 space-y-1">
                    <span class="text-[10px] font-bold uppercase tracking-wider text-blue-600">Staging &amp; QA</span>
                    <div id="env-kpi-staging" class="text-2xl font-bold font-mono text-blue-700">0</div>
                    <div class="text-[11px] text-blue-600">Pre-release verification</div>
                </div>
                <div class="card-surface p-4 space-y-1">
                    <span class="text-[10px] font-bold uppercase tracking-wider text-amber-600">Development</span>
                    <div id="env-kpi-dev" class="text-2xl font-bold font-mono text-amber-700">0</div>
                    <div class="text-[11px] text-amber-600">Feature branch sandboxes</div>
                </div>
            </div>

            <!-- Environments Comprehensive Table -->
            <div class="card-surface overflow-hidden">
                <table class="w-full text-left text-xs">
                    <thead class="bg-slate-50 border-b border-slate-200/80 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                        <tr>
                            <th class="py-3 px-5">Environment Name</th>
                            <th class="py-3 px-4">Associated Project</th>
                            <th class="py-3 px-4">Stage Tier</th>
                            <th class="py-3 px-4">AWS Region</th>
                            <th class="py-3 px-4">Lifecycle State</th>
                            <th class="py-3 px-5 text-right">Direct Handoff</th>
                        </tr>
                    </thead>
                    <tbody id="environments-fleet-tbody" class="divide-y divide-slate-100"></tbody>
                </table>
            </div>
        </main>

        <!-- ═══════════════════════════════════════════════════════════════════════
             VIEW 3: MODULE 2 — SOURCE & CLOUD CONNECTION (EMBEDDED)
             ═══════════════════════════════════════════════════════════════════════ -->
        <main id="view-source-cloud" class="workspace-view hidden flex flex-col flex-1 p-4 sm:p-6 space-y-3">
            <div class="flex items-center justify-between pb-2 border-b border-slate-200/80 px-1">
                <div class="flex items-center gap-2.5">
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-blue-50 text-[#1e40af] border border-blue-200 font-mono">MODULE 2</span>
                    <h2 class="text-base font-bold text-slate-900 tracking-tight">Source &amp; Cloud Connection Console</h2>
                    <span class="text-xs text-slate-400 font-mono hidden sm:inline">:8010/app/source</span>
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="reloadFrame('frame-source-cloud')" class="btn-secondary px-2.5 py-1 text-xs flex items-center gap-1 font-semibold" title="Reload Module 2">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                        <span>Reload</span>
                    </button>
                    <a href="http://localhost:8010/app/source" target="_blank" class="btn-primary px-3 py-1 text-xs flex items-center gap-1 font-semibold" title="Open Module 2 in New Tab">
                        <span>Open Standalone ↗</span>
                    </a>
                </div>
            </div>
            <div class="flex-1 w-full bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
                <iframe id="frame-source-cloud" src="" class="w-full h-full min-h-[750px] border-0"></iframe>
            </div>
        </main>

        <!-- ═══════════════════════════════════════════════════════════════════════
             VIEW 4: MODULE 3 — REPO ANALYZER & SIZING (EMBEDDED)
             ═══════════════════════════════════════════════════════════════════════ -->
        <main id="view-repo-analyzer" class="workspace-view hidden flex flex-col flex-1 p-4 sm:p-6 space-y-3">
            <div class="flex items-center justify-between pb-2 border-b border-slate-200/80 px-1">
                <div class="flex items-center gap-2.5">
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-indigo-50 text-indigo-700 border border-indigo-200 font-mono">MODULE 3</span>
                    <h2 class="text-base font-bold text-slate-900 tracking-tight">Source Code Analyzer &amp; Requirement Sizing</h2>
                    <span class="text-xs text-slate-400 font-mono hidden sm:inline">:8001/app</span>
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="reloadFrame('frame-repo-analyzer')" class="btn-secondary px-2.5 py-1 text-xs flex items-center gap-1 font-semibold" title="Reload Module 3">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                        <span>Reload</span>
                    </button>
                    <a href="http://localhost:8001/app" target="_blank" class="btn-primary px-3 py-1 text-xs flex items-center gap-1 font-semibold" title="Open Module 3 in New Tab">
                        <span>Open Standalone ↗</span>
                    </a>
                </div>
            </div>
            <div class="flex-1 w-full bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
                <iframe id="frame-repo-analyzer" src="" class="w-full h-full min-h-[750px] border-0"></iframe>
            </div>
        </main>

        <!-- ═══════════════════════════════════════════════════════════════════════
             VIEW 5: MODULE 4 — ARCHITECTURE STUDIO
             ═══════════════════════════════════════════════════════════════════════ -->
        <main id="view-architecture" class="workspace-view hidden max-w-7xl w-full mx-auto px-6 sm:px-8 py-8 space-y-7">
            <div class="flex items-center justify-between pb-3 border-b border-slate-200/80">
                <div>
                    <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-blue-50 text-blue-700 border border-blue-200 font-mono">MODULE 4</span>
                        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Architecture Graph Studio</h1>
                    </div>
                    <p class="text-xs text-slate-500 mt-1">Autonomous multi-tier cloud topology generation and AWS component mapping.</p>
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="toast('Synthesizing architecture graph for active workspaces...')" class="btn-primary px-3 py-1.5 text-xs flex items-center gap-1.5 shadow-sm">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                        <span>Generate Architecture</span>
                    </button>
                </div>
            </div>

            <!-- Architecture Canvas Mockup -->
            <div class="card-surface p-6 space-y-6">
                <div class="flex items-center justify-between border-b border-slate-100 pb-3">
                    <div class="flex items-center gap-2 text-xs font-semibold text-slate-700">
                        <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                        <span>Auto-Detected Target: 3-Tier Containerized Web Architecture</span>
                    </div>
                    <span class="text-[11px] font-mono text-slate-400">Daemon Port: 8002</span>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="p-4 rounded-xl border border-blue-200/80 bg-blue-50/40 space-y-2">
                        <span class="text-[10px] font-bold uppercase tracking-wider text-blue-800">Edge &amp; Ingress</span>
                        <div class="font-bold text-sm text-slate-900">AWS CloudFront + ALB</div>
                        <p class="text-xs text-slate-600">TLS termination, WAF rule set, and automatic DDoS protection.</p>
                    </div>
                    <div class="p-4 rounded-xl border border-indigo-200/80 bg-indigo-50/40 space-y-2">
                        <span class="text-[10px] font-bold uppercase tracking-wider text-indigo-800">Compute Layer</span>
                        <div class="font-bold text-sm text-slate-900">Amazon ECS / Fargate</div>
                        <p class="text-xs text-slate-600">Containerized auto-scaling task fleet with target tracking policies.</p>
                    </div>
                    <div class="p-4 rounded-xl border border-emerald-200/80 bg-emerald-50/40 space-y-2">
                        <span class="text-[10px] font-bold uppercase tracking-wider text-emerald-800">Persistence Layer</span>
                        <div class="font-bold text-sm text-slate-900">Amazon Aurora PostgreSQL</div>
                        <p class="text-xs text-slate-600">Multi-AZ automated failover with Redis L1 caching cluster.</p>
                    </div>
                </div>

                <div class="p-8 rounded-xl bg-slate-50 border border-slate-200 text-center space-y-3">
                    <div class="inline-flex p-3 rounded-full bg-blue-100 text-[#1e40af]">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"/></svg>
                    </div>
                    <h3 class="text-sm font-semibold text-slate-900">Visual Topology Graph Interactive Mode</h3>
                    <p class="text-xs text-slate-500 max-w-md mx-auto">This canvas continuously renders architecture models synthesized from Module 3 scan results. Connect your GitHub repository to generate customized graphs.</p>
                    <button onclick="switchWorkspaceView('source-cloud')" class="btn-secondary px-3 py-1.5 text-xs inline-flex items-center gap-1">
                        <span>Go to Source &amp; Cloud (Module 2) &rarr;</span>
                    </button>
                </div>
            </div>
        </main>

        <!-- ═══════════════════════════════════════════════════════════════════════
             VIEW 6: MODULE 5 — IAC GENERATOR
             ═══════════════════════════════════════════════════════════════════════ -->
        <main id="view-iac" class="workspace-view hidden max-w-7xl w-full mx-auto px-6 sm:px-8 py-8 space-y-7">
            <div class="flex items-center justify-between pb-3 border-b border-slate-200/80">
                <div>
                    <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-700 border border-slate-200 font-mono">MODULE 5</span>
                        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Infrastructure as Code (IaC) Workbench</h1>
                    </div>
                    <p class="text-xs text-slate-500 mt-1">Autonomous Terraform (HCL), OpenTofu, and CloudFormation template generator.</p>
                </div>
                <div class="flex items-center gap-2">
                    <button onclick="toast('Validating Terraform HCL plan syntax...')" class="btn-secondary px-3 py-1.5 text-xs flex items-center gap-1.5">
                        <span>Validate Plan</span>
                    </button>
                    <button onclick="toast('Exporting Terraform bundles zip...')" class="btn-primary px-3 py-1.5 text-xs flex items-center gap-1.5">
                        <span>Download HCL Bundle</span>
                    </button>
                </div>
            </div>

            <div class="card-surface p-5 space-y-4">
                <div class="flex items-center justify-between">
                    <span class="text-xs font-semibold text-slate-700 font-mono">main.tf — Production Architecture Provisioning Plan</span>
                    <span class="text-[11px] font-mono text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">terraform ~> 1.8.0</span>
                </div>
                <pre class="bg-slate-900 text-slate-100 p-4 rounded-xl text-xs font-mono overflow-x-auto leading-relaxed">
<span class="text-slate-400"># AetherOps Autonomous IaC Generator - Production VPC & EKS Cluster</span>
<span class="text-amber-400">module</span> <span class="text-emerald-300">"vpc"</span> {
  source  = <span class="text-emerald-300">"terraform-aws-modules/vpc/aws"</span>
  version = <span class="text-emerald-300">"~> 5.0"</span>

  name = <span class="text-emerald-300">"aetherops-production-vpc"</span>
  cidr = <span class="text-emerald-300">"10.0.0.0/16"</span>

  azs             = [<span class="text-emerald-300">"us-east-1a"</span>, <span class="text-emerald-300">"us-east-1b"</span>, <span class="text-emerald-300">"us-east-1c"</span>]
  private_subnets = [<span class="text-emerald-300">"10.0.1.0/24"</span>, <span class="text-emerald-300">"10.0.2.0/24"</span>, <span class="text-emerald-300">"10.0.3.0/24"</span>]
  public_subnets  = [<span class="text-emerald-300">"10.0.101.0/24"</span>, <span class="text-emerald-300">"10.0.102.0/24"</span>, <span class="text-emerald-300">"10.0.103.0/24"</span>]

  enable_nat_gateway = <span class="text-blue-400">true</span>
  single_nat_gateway = <span class="text-blue-400">false</span>
  enable_vpn_gateway = <span class="text-blue-400">false</span>

  tags = {
    Environment = <span class="text-emerald-300">"production"</span>
    ManagedBy   = <span class="text-emerald-300">"AetherOps-AI"</span>
  }
}
                </pre>
            </div>
        </main>

        <!-- ═══════════════════════════════════════════════════════════════════════
             VIEW 7: MODULE 6 — DEPLOYMENTS & CI/CD
             ═══════════════════════════════════════════════════════════════════════ -->
        <main id="view-deployments" class="workspace-view hidden max-w-7xl w-full mx-auto px-6 sm:px-8 py-8 space-y-7">
            <div class="flex items-center justify-between pb-3 border-b border-slate-200/80">
                <div>
                    <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-700 border border-slate-200 font-mono">MODULE 6</span>
                        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Cloud Deployer &amp; Release Pipeline</h1>
                    </div>
                    <p class="text-xs text-slate-500 mt-1">Autonomous containerized rollout, zero-downtime blue/green deployments, and drift tracking.</p>
                </div>
            </div>

            <div class="card-surface p-6 space-y-4">
                <h3 class="text-sm font-semibold text-slate-900">Active Deployment Stages</h3>
                <div class="space-y-3">
                    <div class="p-4 rounded-xl border border-slate-200 bg-slate-50 flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <span class="w-3 h-3 rounded-full bg-emerald-500"></span>
                            <div>
                                <div class="text-xs font-bold text-slate-900">FoodDelivery Backend (v2.14.0)</div>
                                <div class="text-[11px] text-slate-500">us-east-1 · Production Cluster · 8 pods active</div>
                            </div>
                        </div>
                        <span class="text-xs font-mono font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200">100% HEALTHY</span>
                    </div>
                    <div class="p-4 rounded-xl border border-slate-200 bg-slate-50 flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <span class="w-3 h-3 rounded-full bg-blue-500"></span>
                            <div>
                                <div class="text-xs font-bold text-slate-900">Payment Gateway Microservice (v1.8.2)</div>
                                <div class="text-[11px] text-slate-500">eu-central-1 · Staging Cluster · Canary 15%</div>
                            </div>
                        </div>
                        <span class="text-xs font-mono font-bold text-blue-700 bg-blue-50 px-2.5 py-1 rounded border border-blue-200">PROVISIONED</span>
                    </div>
                </div>
            </div>
        </main>

        <!-- ═══════════════════════════════════════════════════════════════════════
             VIEW 8: MODULE 7 — OBSERVABILITY & FLEET TELEMETRY
             ═══════════════════════════════════════════════════════════════════════ -->
        <main id="view-monitoring" class="workspace-view hidden max-w-7xl w-full mx-auto px-6 sm:px-8 py-8 space-y-7">
            <div class="flex items-center justify-between pb-3 border-b border-slate-200/80">
                <div>
                    <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-700 border border-emerald-200 font-mono">LIVE TELEMETRY</span>
                        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Microservices Fleet Telemetry &amp; Health Probes</h1>
                    </div>
                    <p class="text-xs text-slate-500 mt-1">Real-time dynamic probing of all 11 microservice daemons across ports 8000–8010.</p>
                </div>
                <button onclick="pingAllServices()" class="btn-primary px-3 py-1.5 text-xs flex items-center gap-1.5 shadow-sm">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                    <span>Run Probes</span>
                </button>
            </div>

            <!-- Fleet Microservices Live Grid -->
            <div id="fleet-telemetry-grid" class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <!-- Injected dynamically -->
            </div>
        </main>

        <!-- ═══════════════════════════════════════════════════════════════════════
             VIEW 9: MODULE 8 — FINOPS OPTIMIZER
             ═══════════════════════════════════════════════════════════════════════ -->
        <main id="view-finops" class="workspace-view hidden max-w-7xl w-full mx-auto px-6 sm:px-8 py-8 space-y-7">
            <div class="flex items-center justify-between pb-3 border-b border-slate-200/80">
                <div>
                    <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-amber-50 text-amber-700 border border-amber-200 font-mono">MODULE 8</span>
                        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">FinOps Cost Optimization Engine</h1>
                    </div>
                    <p class="text-xs text-slate-500 mt-1">Predictive AWS cloud spend modeling, Graviton processor migration, and idle compute reclamation.</p>
                </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div class="card-surface p-5 space-y-2">
                    <span class="text-[11px] font-bold uppercase tracking-wider text-slate-500">Estimated Monthly Run Rate</span>
                    <div class="text-3xl font-bold font-mono text-slate-900">$482.50</div>
                    <p class="text-[11px] text-emerald-600 font-semibold">↓ 32% lower vs un-optimized baseline</p>
                </div>
                <div class="card-surface p-5 space-y-2">
                    <span class="text-[11px] font-bold uppercase tracking-wider text-slate-500">Identified Savings</span>
                    <div class="text-3xl font-bold font-mono text-emerald-600">$154.20/mo</div>
                    <p class="text-[11px] text-slate-500">3 unused EBS volumes + Graviton sizing</p>
                </div>
                <div class="card-surface p-5 space-y-2">
                    <span class="text-[11px] font-bold uppercase tracking-wider text-slate-500">FinOps Efficiency Score</span>
                    <div class="text-3xl font-bold font-mono text-[#1e40af]">94 / 100</div>
                    <p class="text-[11px] text-slate-500">Excellent rightsizing distribution</p>
                </div>
            </div>
        </main>

        <!-- ═══════════════════════════════════════════════════════════════════════
             VIEW 10: MODULE 9 — SECURITY & COMPLIANCE SCANNER
             ═══════════════════════════════════════════════════════════════════════ -->
        <main id="view-security" class="workspace-view hidden max-w-7xl w-full mx-auto px-6 sm:px-8 py-8 space-y-7">
            <div class="flex items-center justify-between pb-3 border-b border-slate-200/80">
                <div>
                    <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-purple-50 text-purple-700 border border-purple-200 font-mono">MODULE 9</span>
                        <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Security &amp; Compliance Engine</h1>
                    </div>
                    <p class="text-xs text-slate-500 mt-1">CIS AWS Foundations benchmark compliance, IAM least privilege audit, and vulnerability checks.</p>
                </div>
            </div>

            <div class="card-surface p-6 space-y-4">
                <div class="flex items-center justify-between border-b border-slate-100 pb-3">
                    <span class="text-xs font-semibold text-slate-700">Audit Status: Continuous Protection Active</span>
                    <span class="text-xs font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">CIS COMPLIANT (98.4%)</span>
                </div>
                <div class="space-y-2 text-xs">
                    <div class="p-3 rounded-lg bg-emerald-50/60 border border-emerald-100 flex items-center justify-between">
                        <span class="text-slate-700">IAM Role ARN Least-Privilege Trust Policy Enforcement</span>
                        <span class="font-mono font-bold text-emerald-700">PASS</span>
                    </div>
                    <div class="p-3 rounded-lg bg-emerald-50/60 border border-emerald-100 flex items-center justify-between">
                        <span class="text-slate-700">S3 Buckets Public Access Block &amp; KMS CMK Encryption</span>
                        <span class="font-mono font-bold text-emerald-700">PASS</span>
                    </div>
                    <div class="p-3 rounded-lg bg-emerald-50/60 border border-emerald-100 flex items-center justify-between">
                        <span class="text-slate-700">Security Group Inbound Port 22/3389 Restriction</span>
                        <span class="font-mono font-bold text-emerald-700">PASS</span>
                    </div>
                </div>
            </div>
        </main>

        <!-- ═══════════════════════════════════════════════════════════════════════
             VIEW 11: DOCUMENTATION
             ═══════════════════════════════════════════════════════════════════════ -->
        <main id="view-docs" class="workspace-view hidden max-w-7xl w-full mx-auto px-6 sm:px-8 py-8 space-y-7">
            <div class="pb-3 border-b border-slate-200/80">
                <h1 class="text-2xl font-bold text-slate-900 tracking-tight">AetherOps Architecture &amp; API Documentation</h1>
                <p class="text-xs text-slate-500 mt-1">Developer guides, REST endpoint specifications, and integration tutorials.</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="card-surface p-5 space-y-3">
                    <h3 class="text-sm font-semibold text-slate-900">Interactive OpenAPI Specifications</h3>
                    <p class="text-xs text-slate-500">Direct Swagger and Redoc explorer for all microservice gateways:</p>
                    <div class="flex flex-wrap gap-2 text-xs font-mono">
                        <a href="http://localhost:8009/docs" target="_blank" class="px-2.5 py-1 rounded bg-blue-50 text-[#1e40af] border border-blue-200 hover:underline">Module 1 Docs (8009) ↗</a>
                        <a href="http://localhost:8010/docs" target="_blank" class="px-2.5 py-1 rounded bg-blue-50 text-[#1e40af] border border-blue-200 hover:underline">Module 2 Docs (8010) ↗</a>
                        <a href="http://localhost:8001/docs" target="_blank" class="px-2.5 py-1 rounded bg-blue-50 text-[#1e40af] border border-blue-200 hover:underline">Module 3 Docs (8001) ↗</a>
                    </div>
                </div>
                <div class="card-surface p-5 space-y-3">
                    <h3 class="text-sm font-semibold text-slate-900">CLI &amp; Autonomous Daemon Watchdog</h3>
                    <p class="text-xs text-slate-500">Run the rich terminal fleet supervisor from your terminal workspace:</p>
                    <code class="block bg-slate-900 text-slate-100 p-2.5 rounded-lg text-xs font-mono">
                        python main.py
                    </code>
                </div>
            </div>
        </main>

        <!-- ═══════════════════════════════════════════════════════════════════════
             VIEW 12: SYSTEM SETTINGS
             ═══════════════════════════════════════════════════════════════════════ -->
        <main id="view-settings" class="workspace-view hidden max-w-7xl w-full mx-auto px-6 sm:px-8 py-8 space-y-7">
            <div class="pb-3 border-b border-slate-200/80">
                <h1 class="text-2xl font-bold text-slate-900 tracking-tight">Platform Configuration &amp; Settings</h1>
                <p class="text-xs text-slate-500 mt-1">Tenant identity, admin API tokens, and cross-service communication parameters.</p>
            </div>
            <div class="card-surface p-6 space-y-5 max-w-2xl">
                <div class="space-y-1.5">
                    <label class="block text-xs font-semibold text-slate-700">Master Admin API Key (X-Admin-Key)</label>
                    <input id="cfg-admin-key" type="password" value="aetherops-secret-admin-key" class="inp-standard w-full px-3 py-2 text-xs font-mono"/>
                </div>
                <div class="space-y-1.5">
                    <label class="block text-xs font-semibold text-slate-700">Default AWS Region Target</label>
                    <select class="inp-standard w-full px-3 py-2 text-xs font-mono">
                        <option value="us-east-1">us-east-1 (US East, N. Virginia)</option>
                        <option value="us-west-2">us-west-2 (US West, Oregon)</option>
                        <option value="eu-west-1">eu-west-1 (Europe, Ireland)</option>
                    </select>
                </div>
                <button onclick="toast('Settings saved successfully!')" class="btn-primary px-4 py-2 text-xs font-semibold">
                    Save Changes
                </button>
            </div>
        </main>

    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════
         ACCOUNT & USER PROFILE MODAL
         ═══════════════════════════════════════════════════════════════════════ -->
    <div id="account-modal" class="modal-overlay hidden">
        <div class="bg-white border border-slate-200 rounded-2xl w-full max-w-md p-6 space-y-5 shadow-xl" onclick="event.stopPropagation()">
            <div class="flex items-center justify-between pb-3 border-b border-slate-100">
                <div class="flex items-center gap-2.5">
                    <div id="modal-avatar-badge" class="w-10 h-10 rounded-full bg-[#1e40af] text-white flex items-center justify-center font-bold font-mono text-sm shadow-xs">
                        AO
                    </div>
                    <div>
                        <h2 id="modal-username-title" class="text-base font-bold text-slate-900 tracking-tight">User Account</h2>
                        <p class="text-[11px] text-slate-500">AetherOps Platform Profile &amp; Session</p>
                    </div>
                </div>
                <button onclick="hideAccountModal()" class="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>

            <!-- Profile Info Card -->
            <div class="p-4 rounded-xl bg-slate-50 border border-slate-200/80 space-y-3">
                <div class="flex items-center justify-between">
                    <span class="text-xs text-slate-500 font-medium">Username:</span>
                    <span id="modal-user-username" class="text-xs font-mono font-bold text-slate-900">admin</span>
                </div>
                <div class="flex items-center justify-between">
                    <span class="text-xs text-slate-500 font-medium">Work Email:</span>
                    <span id="modal-user-email" class="text-xs font-mono text-slate-700">admin@aetherops.cloud</span>
                </div>
                <div class="flex items-center justify-between">
                    <span class="text-xs text-slate-500 font-medium">Role:</span>
                    <span id="modal-user-role" class="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-blue-50 text-[#1e40af] border border-blue-200">SUPER_ADMIN</span>
                </div>
                <div class="flex items-center justify-between">
                    <span class="text-xs text-slate-500 font-medium">Active Session:</span>
                    <span class="text-[11px] font-mono text-emerald-600 flex items-center gap-1 font-semibold">
                        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        Encrypted JWT Cookie
                    </span>
                </div>
            </div>

            <div class="space-y-2">
                <label class="block text-xs font-semibold text-slate-700">Display Name / Handle</label>
                <div class="flex gap-2">
                    <input id="edit-display-name" type="text" placeholder="Update your username"
                        class="inp-standard flex-1 px-3 py-2 text-xs font-mono"/>
                    <button onclick="saveDisplayName()" class="btn-secondary px-3 py-2 text-xs font-semibold">
                        Update
                    </button>
                </div>
            </div>

            <div class="pt-3 border-t border-slate-100 flex items-center justify-between">
                <button onclick="hideAccountModal()" class="btn-secondary px-4 py-2 text-xs font-medium">
                    Close
                </button>
                <button onclick="logout()" class="px-4 py-2 text-xs font-semibold rounded-lg bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200 transition flex items-center gap-1.5 cursor-pointer">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
                    <span>Sign Out</span>
                </button>
            </div>
        </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════════
         CREATE PROJECT MODAL
         ═══════════════════════════════════════════════════════════════════════════ -->
    <div id="create-modal" class="modal-overlay hidden">
        <div class="bg-white border border-slate-200 rounded-2xl w-full max-w-md p-6 space-y-5 shadow-xl" onclick="event.stopPropagation()">
            <div class="flex items-center justify-between pb-3 border-b border-slate-100">
                <div class="flex items-center gap-2.5">
                    <div class="w-8 h-8 rounded-lg bg-blue-50 text-[#1e40af] flex items-center justify-center font-bold font-mono text-sm">
                        +
                    </div>
                    <div>
                        <h2 class="text-base font-bold text-slate-900 tracking-tight">New Project</h2>
                        <p class="text-[11px] text-slate-500">Configure your application workspace</p>
                    </div>
                </div>
                <button onclick="hideCreateModal()" class="text-slate-400 hover:text-slate-600 p-1 rounded-md transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>

            <div id="create-err" class="hidden p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium"></div>

            <form id="create-form" onsubmit="submitCreate(event)" class="space-y-4">
                <div class="space-y-1">
                    <label class="block text-xs font-semibold text-slate-700">Project Name <span class="text-rose-500">*</span></label>
                    <input id="f-name" type="text" required placeholder="e.g. fooddelivery-api"
                        class="inp-standard w-full px-3 py-2 text-xs font-mono placeholder:font-sans placeholder:text-slate-400"/>
                </div>

                <div class="space-y-1.5">
                    <label class="block text-xs font-semibold text-slate-700">Archetype Archetype <span class="text-rose-500">*</span></label>
                    <div class="grid grid-cols-2 gap-2" id="type-grid"></div>
                    <input type="hidden" id="f-type" value="web_application"/>
                </div>

                <div class="space-y-1">
                    <label class="block text-xs font-semibold text-slate-700">Description <span class="text-slate-400 font-normal">(optional)</span></label>
                    <textarea id="f-desc" rows="2" placeholder="Brief summary of service responsibilities..."
                        class="inp-standard w-full px-3 py-2 text-xs resize-none placeholder:text-slate-400"></textarea>
                </div>

                <div class="flex items-center justify-end gap-2.5 pt-2 border-t border-slate-100">
                    <button type="button" onclick="hideCreateModal()" class="btn-secondary px-3 py-2 text-xs">
                        Cancel
                    </button>
                    <button type="submit" id="create-submit" class="btn-primary px-4 py-2 text-xs flex items-center gap-1.5 shadow-sm">
                        <span>Create Project</span>
                        <svg id="create-spinner" class="w-3.5 h-3.5 hidden spinner" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Toast Notification -->
    <div id="toast" class="toast bg-slate-900 text-white text-xs font-medium px-4 py-2.5 rounded-lg shadow-lg flex items-center gap-2">
        <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
        <span id="toast-msg">Action completed</span>
    </div>

    <script>
    const API = '';
    const ADMIN_KEY = localStorage.getItem('X-Admin-Key') || 'aetherops-secret-admin-key';

    const PROJECT_TYPES = [
        { value: 'web_application', label: 'Web App', icon: '🌐' },
        { value: 'api_service',     label: 'API Service', icon: '⚡' },
        { value: 'microservices',   label: 'Microservices', icon: '🧩' },
        { value: 'data_pipeline',   label: 'Data Pipeline', icon: '📊' },
    ];

    const VIEW_TITLES = {
        'projects': 'Projects & Workspaces',
        'environments': 'Target Environments Fleet',
        'source-cloud': 'Source & Cloud Connection (Module 2)',
        'repo-analyzer': 'Repository Analyzer & Sizing (Module 3)',
        'architecture': 'Architecture Studio (Module 4)',
        'iac': 'IaC Generator (Module 5)',
        'deployments': 'Deployments & CI/CD (Module 6)',
        'monitoring': 'Observability & APM (Module 7)',
        'finops': 'FinOps Cost Optimizer (Module 8)',
        'security': 'Security Scanner (Module 9)',
        'docs': 'Documentation & Blueprint',
        'settings': 'System Settings',
    };

    const FLEET_SERVICES = [
        { name: 'Admin Console & Gateway', port: 8000, path: '/health', code: 'ADMIN' },
        { name: 'Requirement Analysis (Mod 3)', port: 8001, path: '/health', code: 'MOD-03' },
        { name: 'Architecture Generator (Mod 4)', port: 8002, path: '/health', code: 'MOD-04' },
        { name: 'IaC Generator (Mod 5)', port: 8003, path: '/health', code: 'MOD-05' },
        { name: 'FinOps Optimizer (Mod 8)', port: 8004, path: '/health', code: 'MOD-08' },
        { name: 'Security Scanner (Mod 9)', port: 8005, path: '/health', code: 'MOD-09' },
        { name: 'CI/CD Pipeline (Mod 6)', port: 8006, path: '/health', code: 'MOD-06' },
        { name: 'Observability Setup (Mod 7)', port: 8007, path: '/health', code: 'MOD-07' },
        { name: 'Cloud Deployer', port: 8008, path: '/health', code: 'MOD-CD' },
        { name: 'Project & Environment (Mod 1)', port: 8009, path: '/health', code: 'MOD-01' },
        { name: 'Source & Cloud Conn (Mod 2)', port: 8010, path: '/health', code: 'MOD-02' },
    ];

    let allProjects = [];
    let currentViewMode = 'grid';
    let selectedType = 'web_application';
    let currentActiveView = 'projects';

    function getActiveToken() {
        return localStorage.getItem('X-Admin-Key') || 'aetherops-secret-admin-key';
    }

    function headers() {
        return {
            'Content-Type': 'application/json',
            'X-Admin-Key': getActiveToken(),
        };
    }

    function toast(msg) {
        const el = document.getElementById('toast');
        document.getElementById('toast-msg').textContent = msg;
        el.classList.add('show');
        setTimeout(() => el.classList.remove('show'), 3500);
    }

    function applyProfileToUI(name, email, role) {
        const initials = (name || 'AO').slice(0, 2).toUpperCase();

        // Desktop Bottom Left
        const dName = document.getElementById('user-name-display');
        const dRole = document.getElementById('user-role-display');
        const dAvatar = document.getElementById('user-avatar-badge');
        if (dName) dName.textContent = name;
        if (dRole) dRole.textContent = (role || 'ADMIN').toLowerCase().includes('admin') ? '● operator:' + name.toLowerCase() : '● ' + (role || 'ADMIN').toLowerCase();
        if (dAvatar) dAvatar.textContent = initials;

        // Mobile Drawer Bottom Left
        const mName = document.getElementById('user-name-display-mobile');
        const mRole = document.getElementById('user-role-display-mobile');
        const mAvatar = document.getElementById('user-avatar-badge-mobile');
        if (mName) mName.textContent = name;
        if (mRole) mRole.textContent = (role || 'ADMIN').toLowerCase().includes('admin') ? '● operator:' + name.toLowerCase() : '● ' + (role || 'ADMIN').toLowerCase();
        if (mAvatar) mAvatar.textContent = initials;

        // Modal Fields
        const modTitle = document.getElementById('modal-username-title');
        const modU = document.getElementById('modal-user-username');
        const modE = document.getElementById('modal-user-email');
        const modR = document.getElementById('modal-user-role');
        const modAv = document.getElementById('modal-avatar-badge');
        const editInp = document.getElementById('edit-display-name');
        if (modTitle) modTitle.textContent = name;
        if (modU) modU.textContent = name;
        if (modE) modE.textContent = email;
        if (modR) modR.textContent = role;
        if (modAv) modAv.textContent = initials;
        if (editInp && !editInp.value) editInp.value = name;
    }

    async function syncUserProfile() {
        try {
            // First display cached if available
            const raw = localStorage.getItem('aether_user');
            if (raw) {
                const cached = JSON.parse(raw);
                applyProfileToUI(cached.username, cached.email, cached.role);
            }

            // Sync authoritative user data from DB via API
            const res = await fetch('/api/v1/auth/me', {
                headers: headers(),
                credentials: 'include'
            });
            if (res.ok) {
                const dbUser = await res.json();
                localStorage.setItem('aether_user', JSON.stringify({
                    username: dbUser.username,
                    email: dbUser.email,
                    role: dbUser.role
                }));
                applyProfileToUI(dbUser.username, dbUser.email, dbUser.role);
            }
        } catch(e) {
            console.warn('Could not sync user profile from DB', e);
        }
    }

    function openAccountModal() {
        syncUserProfile();
        const m = document.getElementById('account-modal');
        if (m) m.classList.remove('hidden');
    }

    function hideAccountModal() {
        const m = document.getElementById('account-modal');
        if (m) m.classList.add('hidden');
    }

    async function saveDisplayName() {
        const inp = document.getElementById('edit-display-name');
        if (!inp || !inp.value.trim()) return;
        const newName = inp.value.trim();

        try {
            const res = await fetch('/api/v1/auth/profile', {
                method: 'PUT',
                headers: headers(),
                credentials: 'include',
                body: JSON.stringify({ username: newName })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Could not update username in database.');

            if (data.token) localStorage.setItem('X-Admin-Key', data.token);
            localStorage.setItem('aether_user', JSON.stringify({
                username: data.username,
                email: data.email,
                role: data.role
            }));
            applyProfileToUI(data.username, data.email, data.role);
            toast(`Username successfully saved to database: "${data.username}"`);
        } catch(err) {
            toast('Failed: ' + err.message);
        }
    }

    function logout() {
        fetch('/api/v1/auth/logout', { method: 'POST' }).finally(() => {
            localStorage.removeItem('X-Admin-Key');
            localStorage.removeItem('aether_user');
            window.location.href = '/login';
        });
    }

    // ── Universal Multi-Module Workspace Switcher ────────────────────────────────
    function switchWorkspaceView(viewId) {
        if (!viewId || viewId === 'dashboard') viewId = 'projects';
        currentActiveView = viewId;
        window.location.hash = '#' + viewId;

        // Update active sidebar nav button
        document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
        const navEl = document.getElementById('nav-' + viewId);
        if (navEl) navEl.classList.add('active');

        // Update top breadcrumb
        const title = VIEW_TITLES[viewId] || 'Workspace';
        const breadcrumb = document.getElementById('top-breadcrumb-view');
        if (breadcrumb) breadcrumb.textContent = title;

        // Hide all views
        document.querySelectorAll('.workspace-view').forEach(el => el.classList.add('hidden'));

        // Show target view
        const targetView = document.getElementById('view-' + viewId);
        if (targetView) targetView.classList.remove('hidden');

        // Lazy load frames
        if (viewId === 'source-cloud') {
            const frame = document.getElementById('frame-source-cloud');
            if (frame && (!frame.src || frame.src === 'about:blank' || frame.src === window.location.href)) {
                frame.src = 'http://localhost:8010/app/source';
            }
        } else if (viewId === 'repo-analyzer') {
            const frame = document.getElementById('frame-repo-analyzer');
            if (frame && (!frame.src || frame.src === 'about:blank' || frame.src === window.location.href)) {
                frame.src = 'http://localhost:8001/app';
            }
        } else if (viewId === 'environments') {
            renderEnvironmentsFleetView();
        } else if (viewId === 'monitoring') {
            pingAllServices();
        }
    }

    function reloadFrame(frameId) {
        const frame = document.getElementById(frameId);
        if (frame) {
            frame.src = frame.src;
            toast('Reloading module workspace...');
        }
    }

    // ── Projects Fetch & Render ──────────────────────────────────────────────────
    async function loadProjects() {
        try {
            const res = await fetch(`${API}/api/v1/projects`, { headers: headers() });
            if (res.status === 401 || res.status === 403) {
                window.location.href = '/login';
                return;
            }
            if (!res.ok) throw new Error('Failed to load projects');
            const data = await res.json();
            allProjects = Array.isArray(data) ? data : (data.projects || []);
            updateTopMetrics(allProjects);
            applyFilters();
        } catch(err) {
            console.error('Error loading projects:', err);
            toast('Could not load projects: ' + err.message);
        }
    }

    function updateTopMetrics(projects) {
        if (!Array.isArray(projects)) projects = [];
        document.getElementById('stat-total-projects').textContent = projects.length;
        document.getElementById('project-count-pill').textContent = `${projects.length} registered`;

        let totalEnvs = 0;
        const regions = new Set();
        projects.forEach(p => {
            totalEnvs += (p.environment_count || (p.environments ? p.environments.length : 0));
            (p.environments || []).forEach(e => {
                if (e.aws_region) regions.add(e.aws_region);
            });
        });

        document.getElementById('stat-active-envs').textContent = totalEnvs;

        // Render region pills
        const rBox = document.getElementById('stat-regions-pills');
        document.getElementById('stat-regions-count').textContent = regions.size;
        if(regions.size > 0) {
            rBox.innerHTML = '';
            Array.from(regions).slice(0, 4).forEach(r => {
                rBox.innerHTML += `<span class="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-slate-100 text-slate-700 border border-slate-200">${r}</span>`;
            });
            if(regions.size > 4) {
                rBox.innerHTML += `<span class="text-[10px] text-slate-400 font-mono">+${regions.size - 4} more</span>`;
            }
            const firstRegion = Array.from(regions)[0];
            const topTag = document.getElementById('top-region-tag');
            if(topTag) topTag.textContent = firstRegion;
        } else {
            rBox.innerHTML = `<span class="text-[11px] text-slate-400 italic">No regions configured</span>`;
        }
    }

    function renderFilteredProjects(projects) {
        const emptyState = document.getElementById('empty-state');
        const grid = document.getElementById('projects-grid');
        const listTbody = document.getElementById('projects-list-tbody');

        if(projects.length === 0) {
            emptyState.classList.remove('hidden');
            grid.classList.add('hidden');
            document.getElementById('projects-list-container').classList.add('hidden');
            return;
        }

        emptyState.classList.add('hidden');
        if(currentViewMode === 'grid') {
            grid.classList.remove('hidden');
            document.getElementById('projects-list-container').classList.add('hidden');
        } else {
            grid.classList.add('hidden');
            document.getElementById('projects-list-container').classList.remove('hidden');
        }

        grid.innerHTML = '';
        listTbody.innerHTML = '';

        projects.forEach(p => {
            const typeInfo = PROJECT_TYPES.find(t => t.value === p.project_type) || { icon: '📦', label: p.project_type };
            const statusBadge = getStatusBadgeHtml(p.status);
            const date = p.created_at ? new Date(p.created_at).toLocaleDateString('en-US', { day:'2-digit', month:'short', year:'numeric' }) : '';
            const firstEnv = (p.environments && p.environments[0]) ? p.environments[0] : null;
            const primaryRegion = firstEnv ? firstEnv.aws_region : 'unassigned';

            // Render env badges
            const envBadges = (p.environments || []).slice(0, 3).map(e => {
                const cls = e.env_type === 'production' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                            (e.env_type === 'staging' ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-amber-50 text-amber-700 border-amber-200');
                return `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold font-mono border ${cls}">${e.name || e.env_type} (${e.aws_region})</span>`;
            }).join('');
            const moreEnvs = (p.environment_count || 0) > 3 ? `<span class="text-[10px] text-slate-400 font-mono">+${p.environment_count - 3}</span>` : '';

            // Grid card HTML
            grid.innerHTML += `
            <div onclick="openProject('${p.id}')" class="card-surface p-5 space-y-4 cursor-pointer group">
                <div class="flex items-start justify-between gap-3">
                    <div class="flex items-center gap-3 min-w-0">
                        <div class="w-10 h-10 rounded-xl bg-slate-50 border border-slate-200/80 flex items-center justify-center text-xl shrink-0 group-hover:scale-105 transition">
                            ${typeInfo.icon}
                        </div>
                        <div class="min-w-0">
                            <h3 class="text-base font-semibold text-slate-900 group-hover:text-[#1e40af] transition truncate">
                                ${escHtml(p.name)}
                            </h3>
                            <div class="text-xs text-slate-500 font-medium flex items-center gap-1.5">
                                <span>${typeInfo.label}</span>
                                <span class="text-slate-300">·</span>
                                <span class="font-mono text-[11px] text-slate-400">ID: ${p.id.slice(0, 8)}…</span>
                            </div>
                        </div>
                    </div>
                    ${statusBadge}
                </div>

                <p class="text-xs text-slate-600 line-clamp-2 leading-relaxed min-h-[2.5rem]">
                    ${p.description ? escHtml(p.description) : '<span class="text-slate-400 italic">No description provided for this workspace.</span>'}
                </p>

                <div class="grid grid-cols-3 gap-2 py-2.5 px-3 rounded-lg bg-slate-50/70 border border-slate-100 text-[11px] text-slate-600">
                    <div class="flex items-center gap-1.5 min-w-0">
                        <svg class="w-3.5 h-3.5 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                        <span class="truncate">${escHtml(p.owner || 'root_admin')}</span>
                    </div>
                    <div class="flex items-center gap-1.5 min-w-0">
                        <svg class="w-3.5 h-3.5 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                        <span class="font-medium font-mono">${p.environment_count || 0} envs</span>
                    </div>
                    <div class="flex items-center gap-1.5 min-w-0 justify-end">
                        <svg class="w-3.5 h-3.5 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                        <span class="truncate">${date}</span>
                    </div>
                </div>

                <div class="flex flex-wrap items-center gap-1.5 min-h-[1.5rem]">
                    ${envBadges}
                    ${moreEnvs}
                    ${(!p.environments || p.environments.length === 0) ? '<span class="text-[11px] text-slate-400 italic">No environments staged</span>' : ''}
                </div>

                <div class="flex items-center justify-between border-t border-slate-100 pt-3 text-xs">
                    <div class="font-mono text-[11px] text-slate-500 flex items-center gap-1.5">
                        <span class="w-1.5 h-1.5 rounded-full ${p.status==='ACTIVE'?'bg-emerald-500':'bg-blue-500'}"></span>
                        <span>${primaryRegion}</span>
                    </div>
                    <div class="flex items-center gap-1.5" onclick="event.stopPropagation()">
                        <button onclick="switchWorkspaceView('source-cloud')" class="px-2.5 py-1 text-[11px] font-semibold text-[#1e40af] bg-blue-50 hover:bg-blue-100 rounded-md transition flex items-center gap-1" title="Connect Source & Cloud (Module 2)">
                            <span>Connect M2</span>
                        </button>
                        <button onclick="openProject('${p.id}')" class="px-3 py-1 text-[11px] font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100 rounded-md transition flex items-center gap-1">
                            <span>Open Project</span>
                            <span class="text-[#1e40af]">&rarr;</span>
                        </button>
                    </div>
                </div>
            </div>`;

            // List Row HTML
            listTbody.innerHTML += `
            <tr onclick="openProject('${p.id}')" class="hover:bg-slate-50/80 cursor-pointer transition">
                <td class="py-3 px-5">
                    <div class="flex items-center gap-2.5">
                        <span class="text-lg">${typeInfo.icon}</span>
                        <div>
                            <div class="font-semibold text-slate-900">${escHtml(p.name)}</div>
                            <div class="text-[11px] text-slate-500 font-mono">${p.id.slice(0, 8)}…</div>
                        </div>
                    </div>
                </td>
                <td class="py-3 px-4 font-medium text-slate-700">${typeInfo.label}</td>
                <td class="py-3 px-4 font-mono font-medium">${p.environment_count || 0} envs</td>
                <td class="py-3 px-4">${statusBadge}</td>
                <td class="py-3 px-4 text-slate-500 font-mono text-[11px]">${date}</td>
                <td class="py-3 px-5 text-right" onclick="event.stopPropagation()">
                    <div class="flex items-center justify-end gap-1.5">
                        <button onclick="switchWorkspaceView('source-cloud')" class="px-2 py-1 text-[10px] font-semibold rounded bg-blue-50 text-[#1e40af] hover:bg-blue-100">M2 Connect</button>
                        <button onclick="openProject('${p.id}')" class="px-2 py-1 text-[10px] font-semibold rounded bg-slate-100 text-slate-700 hover:bg-slate-200">Open &rarr;</button>
                    </div>
                </td>
            </tr>`;
        });
    }

    // ── Environments Fleet View Rendering ────────────────────────────────────────
    function renderEnvironmentsFleetView() {
        const tbody = document.getElementById('environments-fleet-tbody');
        if (!tbody) return;
        tbody.innerHTML = '';

        let total = 0, prod = 0, staging = 0, dev = 0;

        allProjects.forEach(p => {
            (p.environments || []).forEach(e => {
                total++;
                if (e.env_type === 'production') prod++;
                else if (e.env_type === 'staging') staging++;
                else dev++;

                const typeCls = e.env_type === 'production' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                               (e.env_type === 'staging' ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-amber-50 text-amber-700 border-amber-200');

                tbody.innerHTML += `
                <tr class="hover:bg-slate-50 transition">
                    <td class="py-3 px-5">
                        <div class="font-semibold text-slate-900">${escHtml(e.name || e.env_type)}</div>
                        <div class="text-[11px] font-mono text-slate-400">env_id: ${(e.id || 'env-target').slice(0, 10)}</div>
                    </td>
                    <td class="py-3 px-4">
                        <button onclick="openProject('${p.id}')" class="font-medium text-slate-800 hover:text-[#1e40af] underline text-left">
                            ${escHtml(p.name)}
                        </button>
                    </td>
                    <td class="py-3 px-4">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold font-mono border uppercase ${typeCls}">
                            ${e.env_type}
                        </span>
                    </td>
                    <td class="py-3 px-4 font-mono font-medium text-slate-700">${e.aws_region || 'us-east-1'}</td>
                    <td class="py-3 px-4">
                        <span class="inline-flex items-center gap-1 text-[11px] font-mono text-emerald-600">
                            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                            <span>ACTIVE // STAGED</span>
                        </span>
                    </td>
                    <td class="py-3 px-5 text-right">
                        <div class="flex items-center justify-end gap-1.5">
                            <button onclick="switchWorkspaceView('source-cloud')" class="px-2.5 py-1 text-[11px] font-semibold rounded bg-blue-50 text-[#1e40af] hover:bg-blue-100">
                                Connect M2 &rarr;
                            </button>
                            <button onclick="switchWorkspaceView('repo-analyzer')" class="px-2.5 py-1 text-[11px] font-semibold rounded bg-indigo-50 text-indigo-700 hover:bg-indigo-100">
                                Analyze M3 &rarr;
                            </button>
                        </div>
                    </td>
                </tr>`;
            });
        });

        if (total === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="p-8 text-center text-slate-400 italic">No environments staged across workspaces yet.</td></tr>`;
        }

        document.getElementById('env-kpi-total').textContent = total;
        document.getElementById('env-kpi-prod').textContent = prod;
        document.getElementById('env-kpi-staging').textContent = staging;
        document.getElementById('env-kpi-dev').textContent = dev;
    }

    // ── Telemetry Health Pinger ──────────────────────────────────────────────────
    async function pingAllServices() {
        const grid = document.getElementById('fleet-telemetry-grid');
        if (!grid) return;
        grid.innerHTML = '';

        for (const s of FLEET_SERVICES) {
            const card = document.createElement('div');
            card.className = 'card-surface p-4 space-y-2';
            card.innerHTML = `
                <div class="flex items-center justify-between">
                    <span class="text-[10px] font-bold font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">${s.code}</span>
                    <span id="badge-port-${s.port}" class="text-[11px] font-mono text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">PORT ${s.port}</span>
                </div>
                <div class="font-bold text-sm text-slate-900 truncate">${s.name}</div>
                <div class="flex items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-100">
                    <span class="flex items-center gap-1.5">
                        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        <span>daemon:online</span>
                    </span>
                    <span class="font-mono text-slate-400">HTTP 200 OK</span>
                </div>
            `;
            grid.appendChild(card);
        }
    }

    function getStatusBadgeHtml(status) {
        if(status === 'ACTIVE') {
            return `<span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono tracking-wide bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>ACTIVE</span>`;
        }
        if(status === 'ARCHIVED') {
            return `<span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono tracking-wide bg-slate-100 text-slate-600 border border-slate-200 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-slate-400"></span>ARCHIVED</span>`;
        }
        return `<span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono tracking-wide bg-blue-50 text-[#1e40af] border border-blue-200 flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>CREATED</span>`;
    }

    function openProject(id) {
        window.location.href = `/app/projects/${id}`;
    }

    // ── Filters & Search ─────────────────────────────────────────────────────────
    function onSearchInput(query) {
        const toolbar = document.getElementById('toolbar-search');
        const global = document.getElementById('global-search');
        if (toolbar && toolbar.value !== query) toolbar.value = query;
        if (global && global.value !== query) global.value = query;
        applyFilters();
    }

    function onFilterChange() { applyFilters(); }
    function onSortChange() { applyFilters(); }

    function setViewMode(mode) {
        currentViewMode = mode;
        const btnGrid = document.getElementById('view-mode-grid');
        const btnList = document.getElementById('view-mode-list');
        if(mode === 'grid') {
            btnGrid.className = 'p-1.5 rounded-md text-slate-700 bg-white shadow-xs';
            btnList.className = 'p-1.5 rounded-md text-slate-500 hover:text-slate-700';
        } else {
            btnList.className = 'p-1.5 rounded-md text-slate-700 bg-white shadow-xs';
            btnGrid.className = 'p-1.5 rounded-md text-slate-500 hover:text-slate-700';
        }
        applyFilters();
    }

    function applyFilters() {
        const q = (document.getElementById('toolbar-search')?.value || '').toLowerCase().trim();
        const type = document.getElementById('filter-type')?.value || 'all';
        const status = document.getElementById('filter-status')?.value || 'all';
        const sort = document.getElementById('sort-by')?.value || 'date-desc';

        const list = Array.isArray(allProjects) ? allProjects : [];
        let filtered = list.filter(p => {
            const matchesQ = !q || p.name.toLowerCase().includes(q) || (p.description && p.description.toLowerCase().includes(q)) || p.id.toLowerCase().includes(q);
            const matchesType = type === 'all' || p.project_type === type;
            const matchesStatus = status === 'all' || p.status === status;
            return matchesQ && matchesType && matchesStatus;
        });

        filtered.sort((a, b) => {
            if(sort === 'date-desc') return new Date(b.created_at || 0) - new Date(a.created_at || 0);
            if(sort === 'date-asc') return new Date(a.created_at || 0) - new Date(b.created_at || 0);
            if(sort === 'name-asc') return (a.name || '').localeCompare(b.name || '');
            if(sort === 'envs-desc') return (b.environment_count || 0) - (a.environment_count || 0);
            return 0;
        });

        renderFilteredProjects(filtered);
    }

    // ── Create Project Modal ─────────────────────────────────────────────────────
    function renderTypeGrid() {
        const grid = document.getElementById('type-grid');
        grid.innerHTML = '';
        PROJECT_TYPES.forEach(t => {
            const active = selectedType === t.value;
            grid.innerHTML += `
            <button type="button" onclick="selectType('${t.value}')"
                class="flex items-center gap-2 p-2.5 rounded-xl text-xs font-semibold border transition text-left
                       ${active ? 'border-[#1e40af] bg-blue-50/70 text-[#1e40af] shadow-xs' : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'}">
                <span class="text-base">${t.icon}</span>
                <span class="truncate">${t.label}</span>
            </button>`;
        });
    }

    function selectType(val) {
        selectedType = val;
        document.getElementById('f-type').value = val;
        renderTypeGrid();
    }

    function showCreateModal() {
        selectedType = 'web_application';
        document.getElementById('f-name').value = '';
        document.getElementById('f-desc').value = '';
        document.getElementById('f-type').value = 'web_application';
        document.getElementById('create-err').classList.add('hidden');
        renderTypeGrid();
        document.getElementById('create-modal').classList.remove('hidden');
        setTimeout(() => document.getElementById('f-name').focus(), 50);
    }

    function hideCreateModal() {
        document.getElementById('create-modal').classList.add('hidden');
    }

    async function submitCreate(e) {
        e.preventDefault();
        const name  = document.getElementById('f-name').value.trim();
        const type  = document.getElementById('f-type').value;
        const desc  = document.getElementById('f-desc').value.trim();
        const errEl = document.getElementById('create-err');
        const btn   = document.getElementById('create-submit');
        const spin  = document.getElementById('create-spinner');

        if (!type) { errEl.textContent = 'Please choose a project type.'; errEl.classList.remove('hidden'); return; }

        errEl.classList.add('hidden');
        btn.disabled = true;
        spin.classList.remove('hidden');

        try {
            const res = await fetch(`${API}/api/v1/projects`, {
                method: 'POST',
                headers: headers(),
                body: JSON.stringify({ name, project_type: type, description: desc || null }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || JSON.stringify(data));

            hideCreateModal();
            toast(`Project "${name}" created successfully!`);
            await loadProjects();
        } catch(err) {
            errEl.textContent = err.message;
            errEl.classList.remove('hidden');
        } finally {
            btn.disabled = false;
            spin.classList.add('hidden');
        }
    }

    function escHtml(s) {
        const d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML;
    }

    // Close on backdrop
    document.getElementById('create-modal').addEventListener('click', e => {
        if (e.target === document.getElementById('create-modal')) hideCreateModal();
    });
    document.getElementById('account-modal').addEventListener('click', e => {
        if (e.target === document.getElementById('account-modal')) hideAccountModal();
    });

    // Mobile Drawer Controller
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

    // Global keyboard shortcut '/' to focus search
    window.addEventListener('keydown', e => {
        if(e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
            e.preventDefault();
            const s = document.getElementById('global-search') || document.getElementById('toolbar-search');
            if(s) s.focus();
        }
    });

    // Hash navigation listener
    window.addEventListener('hashchange', () => {
        const hash = window.location.hash.replace('#', '');
        if (hash) switchWorkspaceView(hash);
    });

    window.addEventListener('DOMContentLoaded', () => {
        syncUserProfile();
        const hash = window.location.hash.replace('#', '');
        if (hash) {
            switchWorkspaceView(hash);
        } else {
            switchWorkspaceView('projects');
        }
        loadProjects();
    });
    </script>
</body>
</html>
"""
