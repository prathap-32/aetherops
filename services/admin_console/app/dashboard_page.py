# services/requirement_analysis/app/dashboard_page.py

def get_dashboard_page_html() -> str:
    """
    Renders the master AWS Management Console theme for AWS Quick Infra Manager (AetherOps AI).
    Adheres to AWS CloudScape design principles:
    - Deep Squid Ink navigation headers (#161e2e / #232f3e)
    - AWS Orange action accents (#ec7211 / #ff9900)
    - Clean enterprise card containers (#1b2533) with crisp borders (#2d3748)
    - Professional, authoritative AWS typography and status telemetry
    """
    return r"""<!DOCTYPE html>
<html lang="en" class="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AetherOps Cloud - Admin Catalog Dashboard</title>
    <link rel="stylesheet" href="/static/fonts/fonts.css">
    <script src="/static/js/tailwind.js"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Plus Jakarta Sans', 'Segoe UI', -apple-system, BlinkMacSystemFont, 'sans-serif'],
                        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
                    },
                    colors: {
                        aws: {
                            squid: '#161e2e',
                            squidDark: '#0f141c',
                            navy: '#232f3e',
                            card: '#1b2533',
                            cardHover: '#222f42',
                            border: '#2d3748',
                            borderLight: '#414d5c',
                            orange: '#ec7211',
                            orangeHover: '#eb5f07',
                            orangeLight: '#ff9900',
                            blue: '#0972d3',
                            blueHover: '#033ebc',
                            green: '#1d8102',
                            red: '#d13212',
                            yellow: '#f59e0b',
                            textMuted: '#9ba7b6',
                            textLight: '#eaeded'
                        }
                    }
                }
            }
        }
    </script>
    <style>
        :root {
            --bg-page: #f8fafc;
            --bg-card: #ffffff;
            --bg-subtle-card: #f8fafc;
            --bg-subtle: #f1f5f9;
            --border-card: #e2e8f0;
            --border-subtle: #cbd5e1;
            --text-title: #0f172a;
            --text-body: #334155;
            --text-muted: #64748b;
            --input-bg: #ffffff;
            --input-border: #cbd5e1;
            --input-text: #0f172a;
            --btn-sec-bg: #ffffff;
            --btn-sec-border: #cbd5e1;
            --btn-sec-text: #1e293b;
            --btn-sec-hover: #f1f5f9;
            --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.03);
            --tab-active-col: #ea580c;
            --tab-inactive-col: #64748b;
        }

        html.dark {
            --bg-page: #0f141c;
            --bg-card: #1b2533;
            --bg-subtle-card: #0f141c;
            --bg-subtle: #161e2e;
            --border-card: #2d3748;
            --border-subtle: #414d5c;
            --text-title: #ffffff;
            --text-body: #eaeded;
            --text-muted: #9ba7b6;
            --input-bg: #0f141c;
            --input-border: #3b444b;
            --input-text: #ffffff;
            --btn-sec-bg: #232f3e;
            --btn-sec-border: #414d5c;
            --btn-sec-text: #ffffff;
            --btn-sec-hover: #2a384c;
            --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.4);
            --tab-active-col: #ff9900;
            --tab-inactive-col: #9ba7b6;
        }

        body {
            background-color: var(--bg-page);
            color: var(--text-body);
            transition: background-color 0.15s ease, color 0.15s ease;
        }
        .aws-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 6px;
            box-shadow: var(--card-shadow);
        }
        .aws-btn-primary {
            background-color: #ec7211;
            color: #ffffff;
            font-weight: 700;
            border-radius: 4px;
            transition: all 0.15s ease-in-out;
        }
        .aws-btn-primary:hover {
            background-color: #eb5f07;
        }
        .aws-btn-primary:active {
            background-color: #dd5706;
        }
        .aws-btn-secondary {
            background-color: var(--btn-sec-bg);
            border: 1px solid var(--btn-sec-border);
            color: var(--btn-sec-text);
            border-radius: 4px;
            transition: all 0.15s ease-in-out;
        }
        .aws-btn-secondary:hover {
            background-color: var(--btn-sec-hover);
            border-color: #ec7211;
        }
        .aws-input {
            background-color: var(--input-bg);
            border: 1px solid var(--input-border);
            color: var(--input-text);
            border-radius: 4px;
            transition: border-color 0.15s ease-in-out;
        }
        .aws-input:focus {
            border-color: #ec7211;
            box-shadow: 0 0 0 1px #ec7211;
            outline: none;
        }
        .aws-nav-active {
            background-color: #232f3e;
            color: #ffffff;
            border-left: 3px solid #ec7211;
        }
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-page);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--border-subtle);
            border-radius: 3px;
        }

        /* Light mode specific element adjustments */
        html:not(.dark) main .aws-card {
            background-color: #ffffff !important;
            border-color: #e2e8f0 !important;
        }
        html:not(.dark) main .text-white {
            color: #0f172a !important;
        }
        html:not(.dark) main .text-\[\#9ba7b6\] {
            color: #64748b !important;
        }
        html:not(.dark) main .text-gray-300,
        html:not(.dark) main .text-gray-200 {
            color: #334155 !important;
        }
        html:not(.dark) main .text-gray-400 {
            color: #64748b !important;
        }
        html:not(.dark) main .border-\[\#2d3748\] {
            border-color: #e2e8f0 !important;
        }
        html:not(.dark) main .bg-\[\#0f141c\] {
            background-color: #f1f5f9 !important;
            border-color: #e2e8f0 !important;
        }
        html:not(.dark) main .bg-\[\#161e2e\] {
            background-color: #f8fafc !important;
            border-color: #e2e8f0 !important;
        }
        html:not(.dark) main .bg-\[\#1b2533\] {
            background-color: #ffffff !important;
        }
        html:not(.dark) #catalog-table thead tr {
            background-color: #f1f5f9 !important;
            border-bottom: 1px solid #e2e8f0 !important;
        }
        html:not(.dark) #catalog-table thead th {
            color: #475569 !important;
        }
        html:not(.dark) #catalog-table tbody {
            background-color: #ffffff !important;
        }
        html:not(.dark) #catalog-table tbody tr {
            border-bottom: 1px solid #e2e8f0 !important;
        }
        html:not(.dark) #catalog-table tbody tr:hover {
            background-color: #f8fafc !important;
        }
        html:not(.dark) #modal-add-resource .aws-card,
        html:not(.dark) #modal-inspector .aws-card {
            background-color: #ffffff !important;
            border-color: #e2e8f0 !important;
        }
        html:not(.dark) #modal-add-resource .text-white,
        html:not(.dark) #modal-inspector .text-white {
            color: #0f172a !important;
        }
        html:not(.dark) #modal-add-resource .text-\[\#9ba7b6\] {
            color: #64748b !important;
        }
        html:not(.dark) #modal-inspector pre {
            background-color: #f8fafc !important;
            color: #0f172a !important;
            border-color: #e2e8f0 !important;
        }
        html:not(.dark) #cat-chip-all.bg-\[\#ec7211\] {
            background-color: #ec7211 !important;
            color: #ffffff !important;
        }
        html:not(.dark) .cat-chip-inactive {
            color: #475569 !important;
        }
        html:not(.dark) .cat-chip-inactive:hover {
            background-color: #f1f5f9 !important;
            color: #0f172a !important;
        }
        #sidebar {
            transition: width 0.2s cubic-bezier(0.4, 0, 0.2, 1), min-width 0.2s cubic-bezier(0.4, 0, 0.2, 1), transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.15s ease;
        }
        @media (min-width: 1024px) {
            #sidebar {
                position: static !important;
                transform: translateX(0) !important;
                width: 17rem;
                min-width: 17rem;
                opacity: 1;
            }
            #sidebar.is-desktop-collapsed {
                width: 0 !important;
                min-width: 0 !important;
                max-width: 0 !important;
                overflow: hidden !important;
                border-right-width: 0 !important;
                opacity: 0 !important;
                pointer-events: none !important;
            }
        }
        @media (max-width: 1023px) {
            #sidebar {
                position: fixed !important;
                top: 0;
                bottom: 0;
                left: 0;
                width: 17rem;
                transform: translateX(-100%) !important;
                z-index: 50;
            }
            #sidebar.is-mobile-open {
                transform: translateX(0) !important;
                box-shadow: 8px 0 30px rgba(0, 0, 0, 0.8);
            }
        }
    </style>
</head>
<body class="min-h-screen antialiased flex flex-col font-sans selection:bg-[#ec7211]/30 selection:text-[#ff9900]">

    <!-- App Shell Wrapper with Sidebar & Main Area -->
    <div class="flex flex-1 overflow-hidden relative">

        <!-- Sidebar Overlay on Mobile -->
        <div id="sidebar-overlay" onclick="toggleSidebar()" class="fixed inset-0 bg-black/60 z-40 hidden transition-opacity"></div>

        <!-- AWS Console Navigation Drawer (Collapsible) -->
        <aside id="sidebar" class="bg-[#161e2e] border-r border-[#2d3748] flex flex-col justify-between shrink-0 overflow-hidden select-none z-40">
            <div class="w-[17rem] h-full flex flex-col justify-between overflow-hidden">
                <div>
                    <!-- AetherOps Console Brand Header -->
                    <div class="p-3.5 border-b border-[#2d3748] flex items-center justify-between bg-[#161e2e]">
                        <div class="min-w-0">
                            <div class="flex items-center space-x-2">
                                <span class="font-extrabold text-white text-base tracking-tight">AetherOps</span>
                                <span class="text-[#ff9900] text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-[#232f3e] border border-[#ff9900]/40 font-mono">AWS</span>
                            </div>
                            <p class="text-[9px] text-[#9ba7b6] tracking-wider uppercase truncate mt-0.5">Autonomous Cloud Infrastructure</p>
                        </div>
                        <button onclick="toggleSidebar()" class="text-gray-400 hover:text-white p-1 rounded hover:bg-[#232f3e] transition cursor-pointer" title="Close Drawer" aria-label="Close Drawer">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                        </button>
                    </div>

                    <!-- Navigation Sections -->
                    <div class="p-2.5 space-y-4 overflow-y-auto max-h-[calc(100vh-140px)]">
                        
                        <!-- Core Console Views -->
                        <div>
                            <div class="text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider px-2.5 mb-1.5">Console Views</div>
                            <nav class="space-y-0.5">
                                <button onclick="switchMainView('catalog')" id="nav-btn-catalog" class="w-full flex items-center justify-between px-2.5 py-2 text-xs font-semibold rounded text-left aws-nav-active transition cursor-pointer">
                                    <div class="flex items-center space-x-2">
                                        <svg class="w-4 h-4 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7C5 4 4 5 4 7z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-6h6v6"></path></svg>
                                        <span>AWS Service Catalog</span>
                                    </div>
                                    <span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-[#1d8102]/20 text-[#1d8102] border border-[#1d8102]/30">Active</span>
                                </button>

                                <button onclick="switchMainView('modules')" id="nav-btn-modules" class="w-full flex items-center justify-between px-2.5 py-2 text-xs font-medium rounded text-[#9ba7b6] hover:text-white hover:bg-[#232f3e] transition text-left cursor-pointer">
                                    <div class="flex items-center space-x-2">
                                        <svg class="w-4 h-4 text-[#539fe5]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                                        <span>Platform Modules (8)</span>
                                    </div>
                                    <span class="text-[9px] px-1.5 py-0.2 rounded bg-[#0f141c] text-gray-400 font-mono border border-[#2d3748]">8 Services</span>
                                </button>

                                <button onclick="switchMainView('matrix')" id="nav-btn-matrix" class="w-full flex items-center justify-between px-2.5 py-2 text-xs font-medium rounded text-[#9ba7b6] hover:text-white hover:bg-[#232f3e] transition text-left cursor-pointer">
                                    <div class="flex items-center space-x-2">
                                        <svg class="w-4 h-4 text-[#a87ffb]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064"></path></svg>
                                        <span>39-Region Matrix</span>
                                    </div>
                                    <span class="text-[9px] px-1.5 py-0.2 rounded bg-[#0f141c] text-gray-400 font-mono border border-[#2d3748]">Global</span>
                                </button>

                                <button onclick="switchMainView('probes')" id="nav-btn-probes" class="w-full flex items-center justify-between px-2.5 py-2 text-xs font-medium rounded text-[#9ba7b6] hover:text-white hover:bg-[#232f3e] transition text-left cursor-pointer">
                                    <div class="flex items-center space-x-2">
                                        <svg class="w-4 h-4 text-[#1d8102]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                        <span>Diagnostics Probes</span>
                                    </div>
                                    <span class="h-2 w-2 rounded-full bg-[#1d8102]"></span>
                                </button>
                            </nav>
                        </div>

                        <!-- 8 Platform Microservices -->
                        <div>
                            <div class="text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider px-2.5 mb-1.5 flex justify-between items-center">
                                <span>AWS Modules</span>
                                <span class="text-[9px] text-[#ff9900] font-mono">8 Deployed</span>
                            </div>
                            <nav class="space-y-0.5" id="sidebar-modules-list">
                                <!-- Populated dynamically -->
                            </nav>
                        </div>

                        <!-- Quick Operations -->
                        <div>
                            <div class="text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider px-2.5 mb-1.5">Operations</div>
                            <div class="space-y-1">
                                <button onclick="triggerUploadAllRegions()" class="w-full py-1.5 px-2.5 text-left text-xs text-white bg-[#232f3e] hover:bg-[#2a384c] border border-[#414d5c] rounded transition flex items-center justify-between cursor-pointer">
                                    <span>Sync 39 Regions</span>
                                    <svg class="w-3.5 h-3.5 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                                </button>
                                <button onclick="clearRedisCache()" class="w-full py-1.5 px-2.5 text-left text-xs text-gray-300 bg-[#232f3e] hover:bg-[#2a384c] border border-[#414d5c] rounded transition flex items-center justify-between cursor-pointer">
                                    <span>Purge Redis L1</span>
                                    <svg class="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                                </button>
                            </div>
                        </div>

                    </div>
                </div>

                <!-- Sidebar Footer -->
                <div class="p-3 border-t border-[#2d3748] bg-[#0f141c] text-[11px] text-[#9ba7b6] flex items-center justify-between shrink-0">
                    <div class="flex items-center space-x-2">
                        <div class="h-2 w-2 rounded-full bg-[#1d8102]"></div>
                        <span class="font-medium text-gray-300">K8s Cluster Healthy</span>
                    </div>
                    <span class="font-mono text-[10px] text-[#ff9900]">8 Microservices</span>
                </div>
            </div>
        </aside>

        <!-- Main Content Area -->
        <div class="flex-1 flex flex-col min-w-0 overflow-y-auto">

            <!-- Official AWS Console Top Navigation Bar -->
            <header class="bg-[#161e2e] border-b border-[#2d3748] px-3 sm:px-5 py-2 flex items-center justify-between gap-3 sticky top-0 z-30 shadow-sm">
                
                <!-- Left: Hamburger Services Launcher & Breadcrumb -->
                <div class="flex items-center space-x-2 sm:space-x-3 shrink-0">
                    <button onclick="toggleSidebar()" id="hamburger-btn" class="px-2.5 py-1.5 rounded bg-[#232f3e] hover:bg-[#2a384c] text-white border border-[#414d5c] focus:outline-none transition flex items-center gap-1.5 text-xs font-bold cursor-pointer" title="AetherOps Modules Menu">
                        <svg class="w-4 h-4 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
                        <span>Services</span>
                    </button>
                    <div class="flex items-center space-x-2 shrink-0">
                        <span class="font-extrabold text-white text-base tracking-tight">AetherOps</span>
                        <span class="text-[#ff9900] text-[10px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-[#232f3e] border border-[#ff9900]/40 font-mono hidden sm:inline">AWS CONSOLE</span>
                        <span class="text-gray-500 hidden md:inline">/</span>
                        <span class="text-xs font-bold text-[#ff9900] font-mono hidden md:inline" id="nav-view-label">CATALOG</span>
                    </div>
                </div>

                <!-- Center: AWS Console View Switcher Tabs -->
                <div class="hidden xl:flex items-center space-x-1 bg-[#0f141c] border border-[#2d3748] p-1 rounded shrink-0">
                    <button onclick="switchMainView('catalog')" id="header-tab-catalog" class="px-3 py-1 text-xs font-bold rounded transition bg-[#ec7211] text-white flex items-center gap-1.5 cursor-pointer">
                        <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7C5 4 4 5 4 7z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-6h6v6"></path></svg>
                        <span>Catalog</span>
                    </button>
                    <button onclick="switchMainView('modules')" id="header-tab-modules" class="px-3 py-1 text-xs font-medium text-gray-300 hover:text-white hover:bg-[#232f3e] rounded transition flex items-center gap-1.5 cursor-pointer">
                        <svg class="w-3.5 h-3.5 text-[#539fe5] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                        <span>Modules (8)</span>
                    </button>
                    <button onclick="switchMainView('matrix')" id="header-tab-matrix" class="px-3 py-1 text-xs font-medium text-gray-300 hover:text-white hover:bg-[#232f3e] rounded transition flex items-center gap-1.5 cursor-pointer">
                        <svg class="w-3.5 h-3.5 text-[#a87ffb] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064"></path></svg>
                        <span>39 Regions</span>
                    </button>
                    <button onclick="switchMainView('probes')" id="header-tab-probes" class="px-3 py-1 text-xs font-medium text-gray-300 hover:text-white hover:bg-[#232f3e] rounded transition flex items-center gap-1.5 cursor-pointer">
                        <svg class="w-3.5 h-3.5 text-[#1d8102] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                        <span>Probes</span>
                    </button>
                </div>

                <!-- Right: Module 1 Link, Region Selector, Cluster Pill, User Badge & Logout -->
                <div class="flex items-center space-x-1.5 sm:space-x-2 shrink-0">
                    
                    <!-- Quick Link: Module 1 Sizing Console -->
                    <a id="header-module1-link" href="http://localhost:8001/app" target="_blank" class="px-2.5 py-1 rounded bg-[#ec7211] hover:bg-[#eb5f07] text-white text-xs font-bold transition flex items-center gap-1.5 cursor-pointer shadow-sm" title="Launch Module 1: Requirement Sizing Engine">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                        <span class="hidden md:inline">Module 1 (Sizing)</span>
                    </a>

                    <!-- Quick Link: Instance Type Finder (Decision Matrix) -->
                    <a href="http://localhost:8001/app" target="_blank" class="px-2.5 py-1 rounded bg-[#232f3e] hover:bg-[#2a384c] border border-[#ff9900]/40 text-[#ff9900] text-xs font-bold transition flex items-center gap-1.5 cursor-pointer shadow-sm" title="Launch Core Math Instance Type Finder & Decision Matrix">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                        <span class="hidden lg:inline">Instance Finder</span>
                    </a>

                    <!-- AWS Region Selector -->
                    <div class="flex items-center space-x-1.5 bg-[#0f141c] border border-[#2d3748] rounded px-2.5 py-1 shrink-0">
                        <svg class="w-3.5 h-3.5 text-[#ff9900] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                        <select id="region-filter" onchange="onRegionFilterChange()" class="bg-transparent text-xs text-gray-200 font-bold focus:outline-none cursor-pointer max-w-[90px] sm:max-w-[140px] md:max-w-[170px] truncate">
                            <!-- Populated dynamically -->
                        </select>
                    </div>

                    <!-- Live Cluster Health Pill -->
                    <button onclick="switchMainView('probes')" id="pill-cluster" class="flex items-center space-x-1.5 px-2.5 py-1 rounded text-xs font-semibold bg-[#0f141c] border border-[#1d8102]/50 text-[#8ce299] hover:bg-[#1b2533] transition shrink-0 cursor-pointer" title="Cluster Health Status">
                        <span class="h-2 w-2 rounded-full bg-[#1d8102] shrink-0"></span>
                        <span id="pill-cluster-text" class="font-mono text-[11px] hidden sm:inline">Cluster Healthy</span>
                        <span class="font-mono text-[10px] sm:hidden">Live</span>
                    </button>

                    <!-- Authenticated Admin Account Dropdown Badge -->
                    <div id="auth-user-pill" class="flex items-center space-x-1.5 bg-[#232f3e] border border-[#414d5c] rounded px-2.5 py-1 text-xs shrink-0" title="Active AWS Account Session">
                        <svg class="w-3.5 h-3.5 text-[#ff9900] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                        <span id="auth-username" class="font-bold text-white font-mono text-xs">admin</span>
                        <span id="auth-role" class="hidden md:inline-block px-1.5 py-0.2 text-[9px] font-extrabold uppercase rounded bg-[#0f141c] text-[#ff9900] border border-[#2d3748]">ROOT</span>
                    </div>

                    <!-- API Key Button -->
                    <button onclick="promptChangeAdminKey()" class="p-1 px-2 rounded text-xs font-semibold bg-[#232f3e] text-gray-300 border border-[#414d5c] hover:text-white transition flex items-center gap-1 shrink-0 cursor-pointer hidden sm:flex" title="Manage API Secret Key">
                        <svg class="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path></svg>
                        <span class="hidden lg:inline text-[11px]">API Key</span>
                    </button>

                    <!-- Theme Toggler -->
                    <button onclick="toggleTheme()" id="theme-toggle-btn" class="px-2.5 py-1 rounded bg-[#232f3e] hover:bg-[#2a384c] border border-[#414d5c] text-yellow-400 transition cursor-pointer flex items-center gap-1.5 text-xs font-semibold" title="Toggle Light / Dark Theme">
                        <span id="theme-toggle-icon">☀️</span>
                        <span id="theme-toggle-text" class="text-xs text-gray-200">Light</span>
                    </button>

                    <!-- Sign Out Button -->
                    <button onclick="logoutAdmin()" class="aws-btn-secondary px-2.5 py-1 text-xs font-bold text-white flex items-center gap-1 shrink-0 cursor-pointer" title="Sign out of AWS Console">
                        <svg class="w-3.5 h-3.5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
                        <span class="hidden sm:inline text-[11px]">Sign Out</span>
                    </button>

                </div>

            </header>

            <!-- Dashboard Content Container -->
            <main class="flex-1 p-4 md:p-6 space-y-6 max-w-7xl mx-auto w-full">

                <!-- VIEW 1: LIVE PROBES SECTION (AWS Health / CloudWatch style) -->
                <section id="view-probes" class="space-y-4">
                    <div class="flex items-center justify-between border-b border-[#2d3748] pb-2">
                        <div class="flex items-center space-x-2">
                            <span class="h-2.5 w-2.5 rounded-full bg-[#1d8102]"></span>
                            <h3 class="text-xs font-bold uppercase tracking-wider text-white">Live Multi-Tier Database & Cache Telemetry</h3>
                            <span class="text-[11px] text-[#9ba7b6] font-mono ml-2" id="probe-timestamp">-</span>
                        </div>
                        <button onclick="refreshProbes()" class="aws-btn-secondary text-xs px-2.5 py-1 flex items-center space-x-1.5">
                            <svg class="w-3.5 h-3.5 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                            <span>Refresh Probes</span>
                        </button>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        
                        <!-- 1. Redis L1 In-Memory Probe -->
                        <div class="aws-card p-4 space-y-2.5 border-l-4 border-l-[#1d8102]">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="text-[10px] font-bold uppercase tracking-wider text-[#9ba7b6]">L1 In-Memory Cache (RAM)</div>
                                    <div class="text-sm font-bold text-white mt-0.5 flex items-center gap-2">
                                        <span>Redis 7 (Container)</span>
                                        <span id="probe-redis-badge" class="px-1.5 py-0.2 text-[9px] rounded font-mono font-bold bg-[#1d8102]/20 text-[#1d8102] border border-[#1d8102]/40">AVAILABLE</span>
                                    </div>
                                </div>
                                <span id="probe-redis-latency" class="text-xs font-mono font-bold text-[#1d8102]">0.0ms</span>
                            </div>
                            <div class="pt-2 border-t border-[#2d3748] text-xs space-y-1 text-[#9ba7b6]">
                                <div class="flex justify-between">
                                    <span>Selected Region Data:</span>
                                    <span id="probe-redis-region-status" class="font-bold text-white">Checking...</span>
                                </div>
                                <div class="flex justify-between">
                                    <span>Total Keys Cached:</span>
                                    <span id="probe-redis-keys" class="font-mono text-gray-200">-</span>
                                </div>
                                <div class="flex justify-between text-[11px]">
                                    <span>Persistence:</span>
                                    <span class="text-gray-300 font-mono">AOF + RDB Enabled</span>
                                </div>
                            </div>
                        </div>

                        <!-- 2. PostgreSQL L3 Master Container Probe -->
                        <div class="aws-card p-4 space-y-2.5 border-l-4 border-l-[#0972d3]">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="text-[10px] font-bold uppercase tracking-wider text-[#9ba7b6]">L3 Master Database (Disk)</div>
                                    <div class="text-sm font-bold text-white mt-0.5 flex items-center gap-2">
                                        <span>PostgreSQL 15</span>
                                        <span id="probe-pg-badge" class="px-1.5 py-0.2 text-[9px] rounded font-mono font-bold bg-[#0972d3]/20 text-[#539fe5] border border-[#0972d3]/40">AVAILABLE</span>
                                    </div>
                                </div>
                                <span id="probe-pg-latency" class="text-xs font-mono font-bold text-[#539fe5]">0.0ms</span>
                            </div>
                            <div class="pt-2 border-t border-[#2d3748] text-xs space-y-1 text-[#9ba7b6]">
                                <div class="flex justify-between">
                                    <span>Selected Region Data:</span>
                                    <span id="probe-pg-region-status" class="font-bold text-white">Checking...</span>
                                </div>
                                <div class="flex justify-between">
                                    <span>Regional Schemas:</span>
                                    <span id="probe-pg-schemas" class="font-mono text-white font-bold">39 Schemas</span>
                                </div>
                                <div class="flex justify-between text-[11px]">
                                    <span>Catalog Database:</span>
                                    <span class="text-gray-300 font-mono">aether_catalog</span>
                                </div>
                            </div>
                        </div>

                        <!-- 3. SQLite L2 Engine Probe -->
                        <div class="aws-card p-4 space-y-2.5 border-l-4 border-l-[#ec7211]">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="text-[10px] font-bold uppercase tracking-wider text-[#9ba7b6]">L2 Local Replica (Host)</div>
                                    <div class="text-sm font-bold text-white mt-0.5 flex items-center gap-2">
                                        <span>SQLite WAL Engine</span>
                                        <span class="px-1.5 py-0.2 text-[9px] rounded font-mono font-bold bg-[#ec7211]/20 text-[#ff9900] border border-[#ec7211]/40">ACTIVE</span>
                                    </div>
                                </div>
                                <span class="text-xs font-mono font-bold text-[#ff9900]">0.05ms</span>
                            </div>
                            <div class="pt-2 border-t border-[#2d3748] text-xs space-y-1 text-[#9ba7b6]">
                                <div class="flex justify-between">
                                    <span>Active Database File:</span>
                                    <span id="probe-sqlite-file" class="font-mono text-white text-[11px]">catalog_us-east-1.db</span>
                                </div>
                                <div class="flex justify-between">
                                    <span>Access Mode:</span>
                                    <span class="font-mono text-gray-200 font-bold">WAL (Zero-Latency)</span>
                                </div>
                                <div class="flex justify-between text-[11px]">
                                    <span>Failover Route:</span>
                                    <span class="text-[#1d8102] font-semibold">PostgreSQL Docker</span>
                                </div>
                            </div>
                        </div>

                    </div>
                </section>

                <!-- VIEW 2: GLOBAL AWS CATALOG SECTION -->
                <div id="view-catalog" class="space-y-5">

                    <!-- Actions & Global Operations Bar -->
                    <section class="aws-card p-4 flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
                        
                        <div class="flex items-center space-x-6 overflow-x-auto pb-1 lg:pb-0">
                            <div>
                                <div class="text-[10px] font-bold uppercase tracking-wider text-[#9ba7b6]">Compute Profiles</div>
                                <div class="text-xl font-bold text-white mt-0.5" id="compute-count">0</div>
                            </div>
                            <div class="h-7 w-px bg-[#2d3748]"></div>
                            <div>
                                <div class="text-[10px] font-bold uppercase tracking-wider text-[#9ba7b6]">Platform Services</div>
                                <div class="text-xl font-bold text-white mt-0.5" id="other-count">0</div>
                            </div>
                            <div class="h-7 w-px bg-[#2d3748]"></div>
                            <div>
                                <div class="text-[10px] font-bold uppercase tracking-wider text-[#9ba7b6]">Replication Status</div>
                                <div class="text-xs font-bold text-[#1d8102] mt-1 flex items-center gap-1.5" id="region-sync-status">
                                    <span>READY</span>
                                </div>
                            </div>
                        </div>

                        <!-- AWS Operations CTA Buttons -->
                        <div class="flex flex-wrap items-center gap-2">
                            
                            <!-- Sync Live AWS Pricing (Primary Orange CTA) -->
                            <button onclick="triggerDynamicSync()" id="sync-btn" class="aws-btn-primary py-2 px-3.5 text-xs flex items-center space-x-2 cursor-pointer shadow-sm">
                                <svg class="h-3.5 w-3.5 animate-spin hidden" id="sync-spinner" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                                <span>Sync Live AWS Pricing</span>
                            </button>

                            <!-- Add Custom SKU Button -->
                            <button onclick="openAddResourceModal()" class="aws-btn-secondary py-2 px-3 text-xs flex items-center space-x-1.5 cursor-pointer">
                                <svg class="w-3.5 h-3.5 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                                <span>Add Custom SKU</span>
                            </button>

                            <!-- Upload All 39 Regions Button -->
                            <button onclick="triggerUploadAllRegions()" id="upload-all-btn" class="aws-btn-secondary py-2 px-3 text-xs flex items-center space-x-1.5 cursor-pointer">
                                <svg class="w-3.5 h-3.5 text-[#539fe5]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                                <span>Upload 39 Regions</span>
                            </button>

                            <!-- Clear Cache Button -->
                            <button onclick="clearRedisCache()" class="aws-btn-secondary py-2 px-3 text-xs text-gray-400 hover:text-white cursor-pointer">
                                Purge Redis
                            </button>

                        </div>

                    </section>

                    <!-- Organized Catalog Workspace -->
                    <section class="grid grid-cols-1 lg:grid-cols-4 gap-5">
                        
                        <!-- Left Service Category Navigator -->
                        <div class="lg:col-span-1 space-y-4">
                            
                            <!-- Category Filter Tabs -->
                            <div class="aws-card p-3 space-y-1">
                                <div class="text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider px-2 mb-1.5">Service Categories</div>
                                <div class="grid grid-cols-1 gap-0.5" id="category-filter-chips">
                                    <button onclick="filterServiceGroup('all')" id="cat-chip-all" class="w-full text-left px-2.5 py-1.5 text-xs font-bold rounded bg-[#ec7211] text-white">All Services (15)</button>
                                    <button onclick="filterServiceGroup('compute')" id="cat-chip-compute" class="w-full text-left px-2.5 py-1.5 text-xs font-medium text-gray-400 hover:text-white hover:bg-[#232f3e] rounded transition">Compute & Containers (4)</button>
                                    <button onclick="filterServiceGroup('database')" id="cat-chip-database" class="w-full text-left px-2.5 py-1.5 text-xs font-medium text-gray-400 hover:text-white hover:bg-[#232f3e] rounded transition">Databases & Storage (4)</button>
                                    <button onclick="filterServiceGroup('network')" id="cat-chip-network" class="w-full text-left px-2.5 py-1.5 text-xs font-medium text-gray-400 hover:text-white hover:bg-[#232f3e] rounded transition">Networking & CDN (3)</button>
                                    <button onclick="filterServiceGroup('security')" id="cat-chip-security" class="w-full text-left px-2.5 py-1.5 text-xs font-medium text-gray-400 hover:text-white hover:bg-[#232f3e] rounded transition">Security & Governance (3)</button>
                                    <button onclick="filterServiceGroup('monitoring')" id="cat-chip-monitoring" class="w-full text-left px-2.5 py-1.5 text-xs font-medium text-gray-400 hover:text-white hover:bg-[#232f3e] rounded transition">Observability (1)</button>
                                </div>
                            </div>

                            <!-- Service Navigation List -->
                            <div class="aws-card p-3 space-y-1.5">
                                <div class="text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider px-2 mb-1 flex justify-between items-center">
                                    <span>AWS Services</span>
                                    <span class="text-[10px] text-[#ff9900] font-mono" id="current-service-tag">EC2</span>
                                </div>
                                <nav class="space-y-0.5 max-h-[500px] overflow-y-auto pr-1" id="service-nav">
                                    <!-- Populated dynamically -->
                                </nav>
                            </div>

                        </div>

                        <!-- Right Main Table Workspace -->
                        <div class="lg:col-span-3 space-y-4">
                            
                            <!-- Table Container (AWS CloudScape Table format) -->
                            <div class="aws-card overflow-hidden">
                                
                                <!-- Table Header with Search Strip -->
                                <div class="p-4 border-b border-[#2d3748] bg-[#161e2e] flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                                    <div>
                                        <h4 class="text-sm font-bold text-white uppercase tracking-wide flex items-center gap-2">
                                            <span class="h-2 w-2 rounded-full bg-[#1d8102]"></span>
                                            <span id="table-title">EC2 Compute Catalog</span>
                                        </h4>
                                        <p class="text-[11px] text-[#9ba7b6] mt-0.5">
                                            <span id="table-subtitle">Live regional pricing and specs</span>
                                            • <span id="table-price-range" class="text-white font-mono font-bold">$0.0104 - $0.3400/hr</span>
                                        </p>
                                    </div>
                                    <div class="relative w-full sm:w-64">
                                        <input type="text" onkeyup="filterTable('catalog-table', this.value)" placeholder="Find resources..." class="aws-input w-full py-1.5 pl-8 pr-3 text-xs placeholder-gray-500">
                                        <svg class="w-3.5 h-3.5 text-gray-500 absolute left-2.5 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                                    </div>
                                </div>

                                <!-- Table Element -->
                                <div class="overflow-x-auto">
                                    <table class="w-full text-left border-collapse" id="catalog-table">
                                        <thead>
                                            <tr class="border-b border-[#2d3748] bg-[#161e2e] text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider">
                                                <th class="p-3">Resource / SKU</th>
                                                <th class="p-3">vCPUs</th>
                                                <th class="p-3">Memory</th>
                                                <th class="p-3">Unit</th>
                                                <th class="p-3">Category</th>
                                                <th class="p-3">Network / Specs</th>
                                                <th class="p-3 text-right">Hourly Rate</th>
                                                <th class="p-3 text-right">Est. Monthly</th>
                                                <th class="p-3 text-center">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody class="divide-y divide-[#263244] text-xs bg-[#1b2533]" id="table-rows">
                                            <!-- Populated dynamically -->
                                        </tbody>
                                    </table>
                                </div>

                            </div>

                        </div>

                    </section>

                </div>

                <!-- VIEW 3: ALL 8 PLATFORM MODULES HUB -->
                <div id="view-modules" class="space-y-5 hidden">
                    
                    <!-- Modules Hub Header -->
                    <div class="aws-card p-5 border-l-4 border-l-[#539fe5] flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                        <div>
                            <div class="text-[10px] font-bold text-[#539fe5] uppercase tracking-widest">Kubernetes Microservices Architecture</div>
                            <h3 class="text-lg font-bold text-white mt-1">AetherOps Microservices Ecosystem (8 Modules)</h3>
                            <p class="text-xs text-[#9ba7b6] mt-1 max-w-3xl">
                                Distributed cloud-native microservices orchestrated by Kubernetes (K8s). Each service queries real-time regional rates and instance profiles to deliver automated, right-sized AWS cloud infrastructure.
                            </p>
                        </div>
                        <span class="px-2.5 py-1 rounded bg-[#0f141c] text-white border border-[#2d3748] text-xs font-mono">
                            K8s Managed
                        </span>
                    </div>

                    <!-- Pipeline Flow Diagram (AWS Architecture Style) -->
                    <div class="aws-card p-4 overflow-x-auto">
                        <div class="text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider mb-3">Module Pipeline & Catalog Dependency Flow</div>
                        <div class="flex items-center min-w-[850px] justify-between text-xs font-mono">
                            <div class="p-2.5 rounded bg-[#0f141c] border border-[#1d8102]/60 text-center space-y-0.5">
                                <span class="text-[9px] text-[#1d8102] font-bold">:8001 ONLINE</span>
                                <div class="font-bold text-white">1. Requirements</div>
                                <div class="text-[9px] text-[#9ba7b6]">EC2/RDS Sizing</div>
                            </div>
                            <span class="text-gray-500">→</span>
                            <div class="p-2.5 rounded bg-[#0f141c] border border-[#1d8102]/60 text-center space-y-0.5">
                                <span class="text-[9px] text-[#1d8102] font-bold">:8002 ONLINE</span>
                                <div class="font-bold text-white">2. Architecture</div>
                                <div class="text-[9px] text-[#9ba7b6]">VPC/EKS Network</div>
                            </div>
                            <span class="text-gray-500">→</span>
                            <div class="p-2.5 rounded bg-[#0f141c] border border-[#2d3748] text-center space-y-0.5">
                                <span class="text-[9px] text-gray-400 font-bold">:8003 READY</span>
                                <div class="font-bold text-white">3. IaC Code</div>
                                <div class="text-[9px] text-[#9ba7b6]">Terraform / HCL</div>
                            </div>
                            <span class="text-gray-500">→</span>
                            <div class="p-2.5 rounded bg-[#0f141c] border border-[#0972d3]/60 text-center space-y-0.5">
                                <span class="text-[9px] text-[#539fe5] font-bold">:8004 CONNECTED</span>
                                <div class="font-bold text-white">4. FinOps Cost</div>
                                <div class="text-[9px] text-[#9ba7b6]">Redis 0ms TCO</div>
                            </div>
                            <span class="text-gray-500">→</span>
                            <div class="p-2.5 rounded bg-[#0f141c] border border-[#2d3748] text-center space-y-0.5">
                                <span class="text-[9px] text-gray-400 font-bold">:8005 READY</span>
                                <div class="font-bold text-white">5. Security</div>
                                <div class="text-[9px] text-[#9ba7b6]">WAF / IAM CIS</div>
                            </div>
                            <span class="text-gray-500">→</span>
                            <div class="p-2.5 rounded bg-[#0f141c] border border-[#2d3748] text-center space-y-0.5">
                                <span class="text-[9px] text-gray-400 font-bold">:8006 READY</span>
                                <div class="font-bold text-white">6. CI/CD</div>
                                <div class="text-[9px] text-[#9ba7b6]">ECR Registry</div>
                            </div>
                            <span class="text-gray-500">→</span>
                            <div class="p-2.5 rounded bg-[#0f141c] border border-[#2d3748] text-center space-y-0.5">
                                <span class="text-[9px] text-gray-400 font-bold">:8007 READY</span>
                                <div class="font-bold text-white">7. Observability</div>
                                <div class="text-[9px] text-[#9ba7b6]">CloudWatch Logs</div>
                            </div>
                            <span class="text-gray-500">→</span>
                            <div class="p-2.5 rounded bg-[#0f141c] border border-[#2d3748] text-center space-y-0.5">
                                <span class="text-[9px] text-gray-400 font-bold">:8008 READY</span>
                                <div class="font-bold text-white">8. Deployer</div>
                                <div class="text-[9px] text-[#9ba7b6]">Drift Repair</div>
                            </div>
                        </div>
                    </div>

                    <!-- 8 Module Cards Grid -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4" id="modules-cards-container">
                        <!-- Populated dynamically via JS -->
                    </div>

                </div>

                <!-- VIEW 4: 39-REGION MULTI-CLOUD MATRIX -->
                <div id="view-matrix" class="space-y-5 hidden">
                    
                    <div class="aws-card p-5 border-l-4 border-l-[#ff9900] flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                        <div>
                            <div class="text-[10px] font-bold text-[#ff9900] uppercase tracking-widest">Global Cloud Infrastructure Matrix</div>
                            <h3 class="text-lg font-bold text-white mt-1">AWS 39-Region Multi-Tier Replication</h3>
                            <p class="text-xs text-[#9ba7b6] mt-1">
                                Complete replication telemetry across all 39 global AWS regions. Every region is co-located in SQLite (L2), schema-isolated in PostgreSQL (L3), and cached in Redis (L1).
                            </p>
                        </div>
                        <button onclick="triggerUploadAllRegions()" class="aws-btn-primary py-2 px-3 text-xs">
                            Sync All 39 Regions
                        </button>
                    </div>

                    <!-- Regions Grid grouped by Geography -->
                    <div class="space-y-5" id="matrix-regions-container">
                        <!-- Populated dynamically via JS -->
                    </div>

                </div>

            </main>

            <!-- AetherOps Console Footer -->
            <footer class="mt-auto border-t border-[#2d3748] bg-[#161e2e] py-3.5 px-6 text-xs text-[#9ba7b6] flex flex-col sm:flex-row justify-between items-center gap-2">
                <div class="flex items-center space-x-2">
                    <span class="font-semibold text-gray-300">&copy; 2026 AetherOps Cloud</span>
                    <span class="text-gray-600">•</span>
                    <span>Autonomous AWS Infrastructure Management</span>
                </div>
                <div class="flex items-center space-x-2 font-mono text-[11px] text-[#9ba7b6]">
                    <span class="inline-block w-2 h-2 rounded-full bg-[#1d8102]"></span>
                    <span>Architecture: Distributed Microservices • Orchestrated by Kubernetes (K8s)</span>
                </div>
            </footer>

        </div>

    </div>

    <!-- MODAL 1: ADD CUSTOM SKU / RESOURCE -->
    <div id="modal-add-resource" class="fixed inset-0 bg-black/70 z-50 hidden flex items-center justify-center p-4">
        <div class="aws-card w-full max-w-lg p-6 space-y-4 shadow-2xl bg-[#1b2533]">
            <div class="flex justify-between items-center pb-3 border-b border-[#2d3748]">
                <h3 class="text-sm font-bold text-white flex items-center gap-2">
                    <span class="h-2 w-2 rounded-full bg-[#ec7211]"></span>
                    <span>Add Custom Resource / SKU</span>
                </h3>
                <button onclick="closeAddResourceModal()" class="text-gray-400 hover:text-white text-lg">&times;</button>
            </div>
            <form id="add-resource-form" onsubmit="submitCustomResource(event)" class="space-y-3 text-xs">
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-[#9ba7b6] font-semibold mb-1">Target Service</label>
                        <select id="modal-service" class="aws-input w-full p-2 text-white">
                            <option value="ec2">EC2 (Compute Instance)</option>
                            <option value="rds">RDS (Database Instance)</option>
                            <option value="s3">S3 (Storage Profile)</option>
                            <option value="vpc">VPC (Network Profile)</option>
                            <option value="iam">IAM (Security)</option>
                            <option value="waf">WAF (Firewall)</option>
                            <option value="cloudwatch">CloudWatch</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-[#9ba7b6] font-semibold mb-1">Instance / SKU Code</label>
                        <input type="text" id="modal-instance-type" required placeholder="e.g. c7i.2xlarge" class="aws-input w-full p-2 text-white font-mono">
                    </div>
                </div>
                <div class="grid grid-cols-3 gap-3">
                    <div>
                        <label class="block text-[#9ba7b6] font-semibold mb-1">vCPUs</label>
                        <input type="number" id="modal-vcpus" value="4" class="aws-input w-full p-2 text-white font-mono">
                    </div>
                    <div>
                        <label class="block text-[#9ba7b6] font-semibold mb-1">RAM (GB)</label>
                        <input type="number" step="0.5" id="modal-ram" value="16.0" class="aws-input w-full p-2 text-white font-mono">
                    </div>
                    <div>
                        <label class="block text-[#9ba7b6] font-semibold mb-1">Hourly Price ($)</label>
                        <input type="number" step="0.0001" id="modal-price" required value="0.1700" class="aws-input w-full p-2 text-[#1d8102] font-mono font-bold">
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-[#9ba7b6] font-semibold mb-1">Category</label>
                        <select id="modal-category" class="aws-input w-full p-2 text-white">
                            <option value="general">General Purpose</option>
                            <option value="compute_optimized">Compute Optimized</option>
                            <option value="memory_optimized">Memory Optimized</option>
                            <option value="burstable">Burstable</option>
                            <option value="storage">Storage</option>
                            <option value="networking">Networking</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-[#9ba7b6] font-semibold mb-1">Network / Details</label>
                        <input type="text" id="modal-details" placeholder="e.g. 12.5 Gbps" class="aws-input w-full p-2 text-white">
                    </div>
                </div>
                <div class="pt-3 flex justify-end space-x-2 border-t border-[#2d3748]">
                    <button type="button" onclick="closeAddResourceModal()" class="aws-btn-secondary px-3 py-1.5 text-xs">Cancel</button>
                    <button type="submit" class="aws-btn-primary px-4 py-1.5 text-xs">Save Resource SKU</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL 2: RAW JSON INSPECTOR -->
    <div id="modal-inspector" class="fixed inset-0 bg-black/75 z-50 hidden flex items-center justify-center p-4">
        <div class="aws-card w-full max-w-2xl p-6 space-y-3 shadow-2xl flex flex-col max-h-[85vh] bg-[#1b2533]">
            <div class="flex justify-between items-center pb-2.5 border-b border-[#2d3748]">
                <h3 class="text-sm font-bold text-white flex items-center gap-2">
                    <span class="h-2 w-2 rounded-full bg-[#ff9900]"></span>
                    <span id="inspector-title">Resource Specification Inspector</span>
                </h3>
                <button onclick="closeInspectorModal()" class="text-gray-400 hover:text-white text-lg">&times;</button>
            </div>
            <div class="flex-1 overflow-y-auto bg-[#0f141c] p-3 rounded border border-[#2d3748] font-mono text-xs text-gray-200">
                <pre id="inspector-json">{}</pre>
            </div>
            <div class="flex justify-between items-center pt-2">
                <span class="text-[10px] text-[#9ba7b6] font-mono">Source: PostgreSQL / Redis Dual Vault</span>
                <button onclick="copyInspectorJSON()" class="aws-btn-secondary px-3 py-1 text-xs">Copy JSON</button>
            </div>
        </div>
    </div>

    <!-- Notification Toast -->
    <div id="toast" class="fixed bottom-6 right-6 px-4 py-3 rounded shadow-2xl border border-[#1d8102] bg-[#1b2533] text-white flex items-center space-x-3 max-w-sm hidden z-50">
        <span id="toast-text" class="text-xs font-semibold">Notification message</span>
    </div>

    <script>
        function applyTheme(theme) {
            const btnIcon = document.getElementById('theme-toggle-icon');
            const btnText = document.getElementById('theme-toggle-text');
            if (theme === 'dark') {
                document.documentElement.classList.add('dark');
                document.documentElement.classList.remove('light');
                if (btnIcon) btnIcon.innerText = '☀️';
                if (btnText) btnText.innerText = 'Dark';
            } else {
                document.documentElement.classList.remove('dark');
                document.documentElement.classList.add('light');
                if (btnIcon) btnIcon.innerText = '🌙';
                if (btnText) btnText.innerText = 'Light';
            }
            localStorage.setItem('aether_theme', theme);
        }

        function toggleTheme() {
            const isDark = document.documentElement.classList.contains('dark');
            applyTheme(isDark ? 'light' : 'dark');
        }

        const initialTheme = localStorage.getItem('aether_theme') || 'light';
        applyTheme(initialTheme);

        let regionsList = [];
        let currentService = 'ec2';
        let currentRegion = 'us-east-1';
        let catalogData = {};
        let modulesData = [];
        let currentGroup = 'all';
        const adminKey = localStorage.getItem('X-Admin-Key') || 'aetherops-secret-admin-key';

        function getServiceSvg(code) {
            const map = {
                ec2: `<svg class="w-3.5 h-3.5 text-[#ff9900] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"></path></svg>`,
                eks: `<svg class="w-3.5 h-3.5 text-[#ff9900] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>`,
                ecs: `<svg class="w-3.5 h-3.5 text-[#ff9900] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>`,
                ecr: `<svg class="w-3.5 h-3.5 text-[#ff9900] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path></svg>`,
                rds: `<svg class="w-3.5 h-3.5 text-[#539fe5] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path></svg>`,
                s3: `<svg class="w-3.5 h-3.5 text-[#539fe5] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path></svg>`,
                ebs: `<svg class="w-3.5 h-3.5 text-[#539fe5] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"></path></svg>`,
                efs: `<svg class="w-3.5 h-3.5 text-[#539fe5] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>`,
                vpc: `<svg class="w-3.5 h-3.5 text-[#a87ffb] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path></svg>`,
                route53: `<svg class="w-3.5 h-3.5 text-[#a87ffb] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"></path></svg>`,
                cloudfront: `<svg class="w-3.5 h-3.5 text-[#a87ffb] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>`,
                iam: `<svg class="w-3.5 h-3.5 text-[#f59e0b] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path></svg>`,
                waf: `<svg class="w-3.5 h-3.5 text-[#f59e0b] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>`,
                cloudtrail: `<svg class="w-3.5 h-3.5 text-[#f59e0b] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>`,
                cloudwatch: `<svg class="w-3.5 h-3.5 text-[#1d8102] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>`
            };
            return map[code] || `<svg class="w-3.5 h-3.5 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>`;
        }

        const servicesList = [
            { code: "ec2", name: "EC2 (Compute)", group: "compute" },
            { code: "eks", name: "EKS (Kubernetes)", group: "compute" },
            { code: "ecs", name: "ECS (Containers)", group: "compute" },
            { code: "ecr", name: "ECR (Registry)", group: "compute" },
            { code: "rds", name: "RDS (Databases)", group: "database" },
            { code: "s3", name: "S3 (Object Storage)", group: "database" },
            { code: "ebs", name: "EBS (Block Storage)", group: "database" },
            { code: "efs", name: "EFS (File Storage)", group: "database" },
            { code: "vpc", name: "VPC (Networking)", group: "network" },
            { code: "route53", name: "Route 53 (DNS)", group: "network" },
            { code: "cloudfront", name: "CloudFront (CDN)", group: "network" },
            { code: "iam", name: "IAM (Security)", group: "security" },
            { code: "waf", name: "WAF (Firewall)", group: "security" },
            { code: "cloudtrail", name: "CloudTrail (Audit)", group: "security" },
            { code: "cloudwatch", name: "CloudWatch (Metrics)", group: "monitoring" }
        ];

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            if (!sidebar) return;
            const isDesktop = window.innerWidth >= 1024;

            if (isDesktop) {
                sidebar.classList.toggle('is-desktop-collapsed');
                if (overlay) overlay.classList.add('hidden');
            } else {
                const isOpen = sidebar.classList.toggle('is-mobile-open');
                if (overlay) {
                    if (isOpen) {
                        overlay.classList.remove('hidden');
                    } else {
                        overlay.classList.add('hidden');
                    }
                }
            }
        }

        function closeSidebarOnMobile() {
            if (window.innerWidth < 1024) {
                const sidebar = document.getElementById('sidebar');
                const overlay = document.getElementById('sidebar-overlay');
                if (sidebar) sidebar.classList.remove('is-mobile-open');
                if (overlay) overlay.classList.add('hidden');
            }
        }

        function showToast(text, type = 'success') {
            const toast = document.getElementById('toast');
            const toastText = document.getElementById('toast-text');
            if (!toast || !toastText) return;
            toastText.innerText = text;
            if (type === 'error') {
                toast.className = "fixed bottom-6 right-6 px-4 py-3 rounded shadow-xl border border-[#d13212] bg-[#1b2533] text-[#ff9492] flex items-center space-x-3 max-w-sm z-50";
            } else {
                toast.className = "fixed bottom-6 right-6 px-4 py-3 rounded shadow-xl border border-[#1d8102] bg-[#1b2533] text-white flex items-center space-x-3 max-w-sm z-50";
            }
            toast.classList.remove('hidden');
            setTimeout(() => { toast.classList.add('hidden'); }, 4000);
        }

        function promptChangeAdminKey() {
            const current = localStorage.getItem('X-Admin-Key') || 'aetherops-secret-admin-key';
            const res = prompt("Enter AWS Administrator API Key (X-Admin-Key):", current);
            if (res) {
                localStorage.setItem('X-Admin-Key', res.trim());
                showToast("Admin Key updated! Reloading telemetry...");
                setTimeout(() => location.reload(), 800);
            }
        }

        async function checkAuthStatus() {
            try {
                const res = await fetch('/api/admin/auth/me', {
                    headers: adminKey ? { 'X-Admin-Key': adminKey } : {}
                });
                if (res.ok) {
                    const data = await res.json();
                    if (data && data.user) {
                        const u = document.getElementById('auth-username');
                        const r = document.getElementById('auth-role');
                        if (u) u.textContent = data.user.username || 'admin';
                        if (r) r.textContent = data.user.role === 'SUPER_ADMIN' ? 'ROOT' : (data.user.role || 'ADMIN');
                    }
                } else if (res.status === 401 || res.status === 403) {
                    window.location.href = '/admin/login?redirect=' + encodeURIComponent(window.location.pathname);
                }
            } catch (e) {
                console.warn("Auth check warning:", e);
            }
        }

        async function logoutAdmin() {
            try {
                await fetch('/api/admin/auth/logout', {
                    method: 'POST',
                    headers: adminKey ? { 'X-Admin-Key': adminKey } : {}
                });
            } catch (e) {
                console.warn("Logout error:", e);
            }
            localStorage.removeItem('X-Admin-Key');
            showToast("Logged out from AWS Console. Redirecting...");
            setTimeout(() => {
                window.location.href = '/admin/login';
            }, 500);
        }

        function switchMainView(viewName) {
            const views = ['catalog', 'modules', 'matrix', 'probes'];
            views.forEach(v => {
                const el = document.getElementById(`view-${v}`);
                if (el) {
                    if (viewName === 'catalog') {
                        if (v === 'catalog' || v === 'probes') {
                            el.classList.remove('hidden');
                        } else {
                            el.classList.add('hidden');
                        }
                    } else {
                        if (v === viewName) {
                            el.classList.remove('hidden');
                        } else {
                            el.classList.add('hidden');
                        }
                    }
                }
                const navBtn = document.getElementById(`nav-btn-${v}`);
                if (navBtn) {
                    if (v === viewName) {
                        navBtn.className = "w-full flex items-center justify-between px-2.5 py-2 text-xs font-semibold rounded text-left aws-nav-active transition cursor-pointer";
                    } else {
                        navBtn.className = "w-full flex items-center justify-between px-2.5 py-2 text-xs font-medium rounded text-[#9ba7b6] hover:text-white hover:bg-[#232f3e] transition text-left cursor-pointer";
                    }
                }
                const headerTab = document.getElementById(`header-tab-${v}`);
                if (headerTab) {
                    if (v === viewName) {
                        headerTab.className = "px-3 py-1 text-xs font-bold rounded transition bg-[#ec7211] text-white flex items-center gap-1.5 cursor-pointer";
                    } else {
                        headerTab.className = "px-3 py-1 text-xs font-medium text-gray-300 hover:text-white hover:bg-[#232f3e] rounded transition flex items-center gap-1.5 cursor-pointer";
                    }
                }
            });

            const navLabel = document.getElementById('nav-view-label');
            if (navLabel) {
                const map = { catalog: 'CATALOG', modules: 'MODULES (8)', matrix: '39 REGIONS', probes: 'PROBES' };
                navLabel.innerText = map[viewName] || viewName.toUpperCase();
            }

            closeSidebarOnMobile();
        }

        async function onRegionFilterChange() {
            currentRegion = document.getElementById('region-filter').value;
            await refreshProbes();
            await fetchCatalog();
            await checkRegionSyncStatus();
        }

        async function refreshProbes() {
            try {
                const res = await fetch(`/api/admin/probe?region=${currentRegion}`, {
                    headers: { 'X-Admin-Key': adminKey }
                });
                if (!res.ok) return;
                const probe = await res.json();
                
                const timeEl = document.getElementById('probe-timestamp');
                if (timeEl) timeEl.innerText = new Date(probe.timestamp * 1000).toLocaleTimeString();

                // Redis Probe Update
                const redisBadge = document.getElementById('probe-redis-badge');
                const redisLatency = document.getElementById('probe-redis-latency');
                const redisRegionStatus = document.getElementById('probe-redis-region-status');
                const redisKeys = document.getElementById('probe-redis-keys');
                
                if (probe.redis.connected) {
                    if (redisBadge) {
                        redisBadge.innerText = 'AVAILABLE';
                        redisBadge.className = 'px-1.5 py-0.2 text-[9px] rounded font-mono font-bold bg-[#1d8102]/20 text-[#1d8102] border border-[#1d8102]/40';
                    }
                    if (redisLatency) redisLatency.innerText = `${probe.redis.latency_ms}ms`;
                    if (redisKeys) redisKeys.innerText = `${probe.redis.total_keys} keys cached`;
                    
                    if (redisRegionStatus) {
                        if (probe.redis.region_data_cached) {
                            redisRegionStatus.innerHTML = `<span class="text-[#1d8102] font-semibold">✔ CACHED (${probe.redis.region_keys_count} keys)</span>`;
                        } else {
                            redisRegionStatus.innerHTML = `<span class="text-[#f59e0b] font-semibold">COLD</span>`;
                        }
                    }
                } else {
                    if (redisBadge) {
                        redisBadge.innerText = 'OFFLINE';
                        redisBadge.className = 'px-1.5 py-0.2 text-[9px] rounded font-mono font-bold bg-[#d13212]/20 text-[#ff9492] border border-[#d13212]/40';
                    }
                    if (redisLatency) redisLatency.innerText = 'ERR';
                    if (redisRegionStatus) redisRegionStatus.innerHTML = '<span class="text-[#d13212]">UNAVAILABLE</span>';
                }

                // PostgreSQL Probe Update
                const pgBadge = document.getElementById('probe-pg-badge');
                const pgLatency = document.getElementById('probe-pg-latency');
                const pgRegionStatus = document.getElementById('probe-pg-region-status');
                const pgSchemas = document.getElementById('probe-pg-schemas');
                
                if (probe.postgres.connected) {
                    if (pgBadge) {
                        pgBadge.innerText = 'AVAILABLE';
                        pgBadge.className = 'px-1.5 py-0.2 text-[9px] rounded font-mono font-bold bg-[#0972d3]/20 text-[#539fe5] border border-[#0972d3]/40';
                    }
                    if (pgLatency) pgLatency.innerText = `${probe.postgres.latency_ms}ms`;
                    if (pgSchemas) pgSchemas.innerText = `${probe.postgres.schemas_count} Schemas`;
                    
                    if (pgRegionStatus) {
                        if (probe.postgres.region_schema_exists) {
                            pgRegionStatus.innerHTML = `<span class="text-[#539fe5] font-semibold">✔ READY (${probe.postgres.region_records_count} records)</span>`;
                        } else {
                            pgRegionStatus.innerHTML = `<span class="text-gray-500">NO SCHEMA</span>`;
                        }
                    }
                } else {
                    if (pgBadge) {
                        pgBadge.innerText = 'OFFLINE';
                        pgBadge.className = 'px-1.5 py-0.2 text-[9px] rounded font-mono font-bold bg-[#d13212]/20 text-[#ff9492] border border-[#d13212]/40';
                    }
                    if (pgLatency) pgLatency.innerText = 'ERR';
                    if (pgRegionStatus) pgRegionStatus.innerHTML = '<span class="text-[#d13212]">UNAVAILABLE</span>';
                }

                // SQLite Probe Update
                const sqliteFile = document.getElementById('probe-sqlite-file');
                if (sqliteFile && probe.sqlite) {
                    sqliteFile.innerText = probe.sqlite.file || `catalog_${currentRegion}.db`;
                }

                // Cluster status pill
                const clusterPill = document.getElementById('pill-cluster');
                const clusterText = document.getElementById('pill-cluster-text');
                if (clusterPill && clusterText) {
                    if (probe.redis.connected && probe.postgres.connected) {
                        clusterText.innerText = 'Cluster Healthy';
                        clusterPill.className = 'flex items-center space-x-1.5 px-2.5 py-1 rounded text-xs font-semibold bg-[#0f141c] border border-[#1d8102]/50 text-[#8ce299] hover:bg-[#1b2533] transition shrink-0 cursor-pointer';
                    } else {
                        clusterText.innerText = 'Cluster Degraded';
                        clusterPill.className = 'flex items-center space-x-1.5 px-2.5 py-1 rounded text-xs font-semibold bg-[#0f141c] border border-[#d13212]/50 text-[#ff9492] hover:bg-[#1b2533] transition shrink-0 cursor-pointer';
                    }
                }

            } catch (err) {
                console.error("Probe refresh failed", err);
            }
        }

        async function triggerUploadAllRegions() {
            const btn = document.getElementById('upload-all-btn');
            if (btn) btn.disabled = true;
            showToast("Initiating bulk synchronization of all 39 AWS regions...");
            try {
                const res = await fetch('/api/admin/catalog/seed-all', {
                    method: 'POST',
                    headers: { 'X-Admin-Key': adminKey }
                });
                const data = await res.json();
                showToast(`Bulk sync complete: ${data.seeded_regions_count} regions updated in PostgreSQL and Redis!`);
                await refreshProbes();
                await fetchCatalog();
                await loadRegionsMatrix();
            } catch (e) {
                showToast("Bulk sync failed: " + e.message, "error");
            } finally {
                if (btn) btn.disabled = false;
            }
        }

        function filterServiceGroup(group) {
            currentGroup = group;
            const chips = ['all', 'compute', 'database', 'network', 'security', 'monitoring'];
            chips.forEach(c => {
                const chip = document.getElementById(`cat-chip-${c}`);
                if (chip) {
                    if (c === group) {
                        chip.className = "w-full text-left px-2.5 py-1.5 text-xs font-bold rounded bg-[#ec7211] text-white";
                    } else {
                        chip.className = "w-full text-left px-2.5 py-1.5 text-xs font-medium text-gray-400 hover:text-white hover:bg-[#232f3e] rounded transition";
                    }
                }
            });
            renderServiceNav();
        }

        function renderServiceNav() {
            const nav = document.getElementById('service-nav');
            nav.innerHTML = '';

            const filteredServices = (currentGroup === 'all') 
                ? servicesList 
                : servicesList.filter(s => s.group === currentGroup);

            filteredServices.forEach(svc => {
                const items = catalogData[svc.code] || [];
                const count = items.length;
                
                const activeClass = (currentService === svc.code) 
                    ? "bg-[#232f3e] text-white border-l-4 border-[#ec7211] font-semibold" 
                    : "text-gray-400 hover:bg-[#232f3e]/60 hover:text-white border-l-4 border-transparent";

                nav.innerHTML += `
                    <button onclick="switchService('${svc.code}')" class="w-full flex items-center justify-between px-2.5 py-1.5 text-xs rounded transition ${activeClass} cursor-pointer">
                        <div class="flex items-center space-x-2 min-w-0">
                            ${getServiceSvg(svc.code)}
                            <span class="truncate">${svc.name}</span>
                        </div>
                        <span class="px-1.5 py-0.2 rounded bg-[#0f141c] text-[10px] font-semibold text-gray-300 font-mono shrink-0 border border-[#2d3748]">${count}</span>
                    </button>
                `;
            });
        }

        async function fetchCatalog() {
            try {
                const res = await fetch(`/api/admin/catalog?region=${currentRegion}`);
                catalogData = await res.json();

                let totalCompute = 0;
                let totalPlatform = 0;

                servicesList.forEach(svc => {
                    const items = catalogData[svc.code] || [];
                    if (['ec2', 'eks', 'ecs', 'ecr'].includes(svc.code)) {
                        totalCompute += items.length;
                    } else {
                        totalPlatform += items.length;
                    }
                });

                document.getElementById('compute-count').innerText = totalCompute;
                document.getElementById('other-count').innerText = totalPlatform;
                document.getElementById('current-service-tag').innerText = currentService.toUpperCase();

                renderServiceNav();
                renderTable();

            } catch (e) {
                showToast("Failed to fetch catalog: " + e.message, "error");
            }
        }

        function switchService(serviceCode) {
            currentService = serviceCode;
            document.getElementById('current-service-tag').innerText = currentService.toUpperCase();
            renderServiceNav();
            renderTable();
        }

        function renderTable() {
            const tableTitle = document.getElementById('table-title');
            const tableSubtitle = document.getElementById('table-subtitle');
            const tablePriceRange = document.getElementById('table-price-range');
            const tableRows = document.getElementById('table-rows');

            const svcObj = servicesList.find(s => s.code === currentService);
            const serviceName = svcObj ? svcObj.name : currentService.toUpperCase();
            tableTitle.innerText = `${serviceName} Catalog`;
            tableSubtitle.innerText = `Region: ${currentRegion.toUpperCase()} • PostgreSQL Master & Redis L1`;

            tableRows.innerHTML = '';
            const items = catalogData[currentService] || [];

            if (items.length === 0) {
                tablePriceRange.innerText = "$0.00/hr";
                tableRows.innerHTML = `<tr><td colspan="9" class="p-8 text-center text-xs text-gray-500">No catalog records stored for ${serviceName} in ${currentRegion.toUpperCase()}. Click 'Sync Live AWS Pricing' or 'Add Custom SKU'.</td></tr>`;
                return;
            }

            const prices = items.map(i => i.price_per_hour || 0.0);
            const minP = Math.min(...prices);
            const maxP = Math.max(...prices);
            tablePriceRange.innerText = `$${minP.toFixed(4)} - $${maxP.toFixed(4)}/hr (${items.length} items)`;

            items.forEach((item, idx) => {
                const vcpuDisp = (item.vcpus && item.vcpus > 0) ? item.vcpus : '-';
                const ramDisp = (item.ram_gb && item.ram_gb > 0) ? `${item.ram_gb} GB` : '-';
                const unitDisp = item.unit || 'Hrs';
                const netOrDetailDisp = item.network_performance || item.details || '-';
                const hourlyPrice = item.price_per_hour || 0.0;
                const isMonthlyUnit = (item.unit && (item.unit.includes('Month') || item.unit.includes('month') || item.unit.includes('mo')));
                const monthlyPrice = isMonthlyUnit ? hourlyPrice.toFixed(2) : (hourlyPrice * 730).toFixed(2);
                
                tableRows.innerHTML += `
                    <tr class="hover:bg-[#232f3e]/60 transition border-b border-[#263244]">
                        <td class="p-3 font-bold text-white font-mono flex items-center space-x-2">
                            <span class="text-[#ff9900]">${item.instance_type}</span>
                        </td>
                        <td class="p-3 text-gray-300 font-mono">${vcpuDisp}</td>
                        <td class="p-3 text-gray-300 font-mono">${ramDisp}</td>
                        <td class="p-3 text-gray-400 font-mono text-[11px]">${unitDisp}</td>
                        <td class="p-3"><span class="px-2 py-0.5 rounded bg-[#0f141c] text-[10px] capitalize text-[#9ba7b6] border border-[#2d3748] font-semibold">${item.category || 'Standard'}</span></td>
                        <td class="p-3 text-gray-300 text-xs">${netOrDetailDisp}</td>
                        <td class="p-3 text-right font-mono font-bold text-[#1d8102]">$${hourlyPrice.toFixed(4)}</td>
                        <td class="p-3 text-right font-mono font-semibold text-gray-300">$${monthlyPrice}</td>
                        <td class="p-3 text-center">
                            <button onclick="inspectItemByIndex(${idx})" class="p-1 px-2.5 text-[10px] font-semibold bg-[#232f3e] hover:bg-[#2a384c] text-gray-200 rounded border border-[#414d5c] transition inline-flex items-center gap-1 cursor-pointer" title="View SKU Specifications">
                                <svg class="w-3 h-3 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                                <span>View</span>
                            </button>
                        </td>
                    </tr>
                `;
            });
        }

        function filterTable(tableId, query) {
            const filter = query.toLowerCase();
            const rows = document.querySelectorAll(`#${tableId} tbody tr`);
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        }

        function inspectItemByIndex(idx) {
            const items = catalogData[currentService] || [];
            const item = items[idx];
            if (!item) return;

            document.getElementById('inspector-title').innerText = `${item.instance_type} (${currentService.toUpperCase()})`;
            document.getElementById('inspector-json').innerText = JSON.stringify(item, null, 2);
            document.getElementById('modal-inspector').classList.remove('hidden');
        }

        function closeInspectorModal() {
            document.getElementById('modal-inspector').classList.add('hidden');
        }

        function copyInspectorJSON() {
            const code = document.getElementById('inspector-json').innerText;
            navigator.clipboard.writeText(code).then(() => {
                showToast("JSON copied to clipboard!");
            });
        }

        function openAddResourceModal() {
            document.getElementById('modal-service').value = currentService;
            document.getElementById('modal-add-resource').classList.remove('hidden');
        }

        function closeAddResourceModal() {
            document.getElementById('modal-add-resource').classList.add('hidden');
        }

        async function submitCustomResource(e) {
            e.preventDefault();
            const service = document.getElementById('modal-service').value;
            const instanceType = document.getElementById('modal-instance-type').value.trim();
            const vcpus = parseInt(document.getElementById('modal-vcpus').value) || 0;
            const ram = parseFloat(document.getElementById('modal-ram').value) || 0.0;
            const price = parseFloat(document.getElementById('modal-price').value) || 0.0;
            const category = document.getElementById('modal-category').value;
            const details = document.getElementById('modal-details').value;

            const payload = {
                instance_type: instanceType,
                vcpus: vcpus,
                ram_gb: ram,
                price_per_hour: price,
                category: category,
                details: details,
                region: currentRegion
            };

            try {
                const res = await fetch(`/api/admin/catalog/${service}`, {
                    method: 'POST',
                    headers: { 'X-Admin-Key': adminKey, 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if (res.ok) {
                    showToast(`SKU '${instanceType}' added to ${service.toUpperCase()} successfully!`);
                    closeAddResourceModal();
                    await refreshProbes();
                    await fetchCatalog();
                } else {
                    const err = await res.json();
                    showToast(`Error: ${err.detail}`, 'error');
                }
            } catch (err) {
                showToast("Request failed: " + err.message, "error");
            }
        }

        async function deleteSku(service, instanceType) {
            if (!confirm(`Delete '${instanceType}' from ${service.toUpperCase()} in ${currentRegion.toUpperCase()}?`)) return;
            try {
                const res = await fetch(`/api/admin/catalog/${service}/${instanceType}?region=${currentRegion}`, {
                    method: 'DELETE',
                    headers: { 'X-Admin-Key': adminKey }
                });
                if (res.ok) {
                    showToast(`SKU '${instanceType}' deleted from catalog.`);
                    await refreshProbes();
                    await fetchCatalog();
                } else {
                    const err = await res.json();
                    showToast(`Delete failed: ${err.detail}`, 'error');
                }
            } catch (err) {
                showToast("Delete failed", "error");
            }
        }

        let pollingInterval = null;

        async function triggerDynamicSync() {
            const syncBtn = document.getElementById('sync-btn');
            const spinner = document.getElementById('sync-spinner');
            syncBtn.disabled = true;
            spinner.classList.remove('hidden');
            showToast(`Triggering dynamic pricing sync for ${currentRegion.toUpperCase()}...`);

            try {
                const res = await fetch(`/api/admin/catalog/sync/${currentRegion}`, {
                    method: 'POST',
                    headers: { 'X-Admin-Key': adminKey, 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh_cache: true })
                });
                
                if (res.status === 202) {
                    pollingInterval = setInterval(checkRegionSyncStatus, 2000);
                } else {
                    syncBtn.disabled = false;
                    spinner.classList.add('hidden');
                }
            } catch (err) {
                syncBtn.disabled = false;
                spinner.classList.add('hidden');
                showToast("Failed to initiate sync", 'error');
            }
        }

        async function checkRegionSyncStatus() {
            try {
                const res = await fetch(`/api/admin/catalog/status/${currentRegion}`, {
                    headers: { 'X-Admin-Key': adminKey }
                });
                if (!res.ok) return;
                const data = await res.json();
                
                const statusEl = document.getElementById('region-sync-status');
                if (data.status === 'SUCCESS') {
                    statusEl.innerHTML = `<span class="text-[#1d8102] font-bold">READY (${data.total_records} items)</span>`;
                } else if (data.status === 'IN_PROGRESS') {
                    statusEl.innerHTML = '<span class="text-[#ff9900] font-bold animate-pulse">SYNCING...</span>';
                } else {
                    statusEl.innerHTML = '<span class="text-gray-400 font-bold">READY</span>';
                }

                if (data.status === 'SUCCESS' || data.status === 'FAILED') {
                    if (pollingInterval) {
                        clearInterval(pollingInterval);
                        pollingInterval = null;
                        document.getElementById('sync-spinner').classList.add('hidden');
                        document.getElementById('sync-btn').disabled = false;
                        
                        if (data.status === 'SUCCESS') {
                            showToast(`Sync completed for ${currentRegion.toUpperCase()}! (${data.total_records} records)`);
                            await refreshProbes();
                            await fetchCatalog();
                        } else {
                            showToast(`Sync error: ${data.error_message}`, 'error');
                        }
                    }
                }
            } catch (err) {
                console.error("Status check failed", err);
            }
        }

        async function clearRedisCache() {
            try {
                const res = await fetch('/api/admin/clear-cache', {
                    method: 'POST',
                    headers: { 'X-Admin-Key': adminKey }
                });
                await res.json();
                showToast("Redis L1 cache purged successfully.");
                await refreshProbes();
                await fetchCatalog();
            } catch (err) {
                showToast("Cache operation failed", "error");
            }
        }

        async function loadModules() {
            try {
                const res = await fetch('/api/admin/modules');
                if (!res.ok) return;
                const data = await res.json();
                modulesData = data.modules || [];
                
                // Render Sidebar Modules Navigation
                const sidebarNav = document.getElementById('sidebar-modules-list');
                sidebarNav.innerHTML = '';

                // Render Modules Hub Cards
                const cardsContainer = document.getElementById('modules-cards-container');
                cardsContainer.innerHTML = '';

                modulesData.forEach(mod => {
                    const statusColor = mod.status === 'ONLINE' ? 'bg-[#1d8102]' : (mod.status === 'CONNECTED' ? 'bg-[#539fe5]' : 'bg-gray-400');
                    const badgeClass = mod.status === 'ONLINE' ? 'bg-[#1d8102]/20 text-[#1d8102] border border-[#1d8102]/40' : (mod.status === 'CONNECTED' ? 'bg-[#0972d3]/20 text-[#539fe5] border border-[#0972d3]/40' : 'bg-[#0f141c] text-gray-400 border border-[#2d3748]');

                    // Sidebar Item
                    sidebarNav.innerHTML += `
                        <div onclick="selectModuleFromSidebar('${mod.code}')" class="cursor-pointer flex items-center justify-between px-2.5 py-1.5 text-xs font-medium rounded text-gray-300 hover:bg-[#232f3e] hover:text-white border border-transparent transition">
                            <div class="flex items-center space-x-2">
                                <span class="h-1.5 w-1.5 rounded-full ${statusColor}"></span>
                                <span>${mod.id}. ${mod.name.replace(' Engine', '').replace(' Service', '')}</span>
                            </div>
                            <span class="text-[9px] px-1.5 py-0.2 rounded ${badgeClass} font-mono">${mod.status === 'ONLINE' ? `:${mod.port}` : mod.status}</span>
                        </div>
                    `;

                    const moduleTargetUrl = mod.ui_url ? mod.ui_url.replace('localhost', window.location.hostname) : (mod.port ? `http://${window.location.hostname}:${mod.port}${mod.ui_path || '/health'}` : null);
                    const launchBtnHtml = moduleTargetUrl ? `
                        <div class="pt-2 flex justify-between items-center">
                            <a href="${moduleTargetUrl}" target="_blank" class="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-[#232f3e] hover:bg-[#2d3748] border border-[#414d5c] text-xs font-semibold text-white transition">
                                <span>Launch ${mod.ui_path ? 'Console' : 'Health API'}</span>
                                <svg class="w-3.5 h-3.5 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                            </a>
                            <span class="text-[10px] text-gray-400 font-mono">Port :${mod.port}</span>
                        </div>
                    ` : '';

                    // Module Card in Hub
                    cardsContainer.innerHTML += `
                        <div id="module-card-${mod.code}" class="aws-card p-4 space-y-2.5 transition">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="text-[9px] font-bold uppercase tracking-wider text-[#ff9900] font-mono">${mod.phase}</div>
                                    <h4 class="text-sm font-bold text-white mt-0.5 flex items-center gap-2">
                                        <span>${mod.id}. ${mod.name}</span>
                                    </h4>
                                </div>
                                <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold ${badgeClass}">
                                    ${mod.status} ${mod.port ? `(:${mod.port})` : ''}
                                </span>
                            </div>
                            <p class="text-xs text-[#9ba7b6] leading-relaxed">${mod.description}</p>
                            
                            <div class="pt-2.5 border-t border-[#2d3748] space-y-1.5">
                                <div class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Catalog Integration:</div>
                                <p class="text-[11px] text-gray-300">${mod.catalog_role}</p>
                                <div class="flex flex-wrap gap-1 mt-1">
                                    ${mod.catalog_dependencies.map(dep => `<span class="px-2 py-0.5 rounded bg-[#0f141c] text-[10px] text-[#ff9900] font-mono border border-[#2d3748]">${dep}</span>`).join('')}
                                </div>
                            </div>
                            ${launchBtnHtml}
                        </div>
                    `;
                });

            } catch (e) {
                console.error("Failed to load modules:", e);
            }
        }

        function selectModuleFromSidebar(modCode) {
            switchMainView('modules');
            setTimeout(() => {
                const el = document.getElementById(`module-card-${modCode}`);
                if (el) {
                    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    el.classList.add('ring-2', 'ring-[#ec7211]');
                    setTimeout(() => el.classList.remove('ring-2', 'ring-[#ec7211]'), 2500);
                }
            }, 100);
        }

        async function loadRegionsMatrix() {
            try {
                const res = await fetch('/api/admin/catalog/regions', {
                    headers: { 'X-Admin-Key': adminKey }
                });
                if (!res.ok) return;
                regionsList = await res.json();

                const container = document.getElementById('matrix-regions-container');
                container.innerHTML = '';

                // Group regions by geography
                const groups = {
                    "North America": ["us-east-1", "us-east-2", "us-west-1", "us-west-2", "ca-central-1", "ca-west-1", "mx-central-1", "us-gov-east-1", "us-gov-west-1"],
                    "Europe": ["eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1", "eu-central-2", "eu-north-1", "eu-south-1", "eu-south-2"],
                    "Asia Pacific": ["ap-south-1", "ap-south-2", "ap-southeast-1", "ap-southeast-2", "ap-southeast-3", "ap-southeast-4", "ap-southeast-5", "ap-southeast-6", "ap-southeast-7", "ap-east-1", "ap-east-2", "ap-northeast-1", "ap-northeast-2", "ap-northeast-3"],
                    "Middle East & Africa": ["me-south-1", "me-central-1", "me-central-2", "il-central-1", "af-south-1"],
                    "South America & China": ["sa-east-1", "cn-north-1", "cn-northwest-1"]
                };

                for (const [geoName, regionCodes] of Object.entries(groups)) {
                    let cardsHtml = '';
                    regionCodes.forEach(code => {
                        const r = regionsList.find(item => item.region_code === code) || { region_code: code, region_name: code, az_count: 3, pricing_tier_multiplier: 1.0, cached_in_redis: true, db_exists: true };
                        
                        cardsHtml += `
                            <div onclick="selectRegionFromMatrix('${r.region_code}')" class="cursor-pointer aws-card p-3.5 hover:border-[#ec7211]/60 transition space-y-2">
                                <div class="flex justify-between items-start">
                                    <div>
                                        <div class="font-bold text-sm text-white font-mono">${r.region_code}</div>
                                        <div class="text-[11px] text-[#9ba7b6] truncate max-w-[150px]">${r.region_name}</div>
                                    </div>
                                    <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-[#0f141c] text-[#ff9900] font-bold border border-[#2d3748]">${r.pricing_tier_multiplier}x</span>
                                </div>
                                <div class="pt-2 border-t border-[#2d3748] flex justify-between items-center text-[10px]">
                                    <span class="text-gray-400">${r.az_count} AZs</span>
                                    <div class="flex items-center space-x-1 font-mono">
                                        <span class="px-1.5 py-0.2 rounded bg-[#0972d3]/20 text-[#539fe5] font-bold text-[9px]">L3 MASTER</span>
                                        <span class="px-1.5 py-0.2 rounded bg-[#1d8102]/20 text-[#1d8102] font-bold text-[9px]">L1 CACHE</span>
                                    </div>
                                </div>
                            </div>
                        `;
                    });

                    container.innerHTML += `
                        <div class="space-y-2.5">
                            <h4 class="text-xs font-bold uppercase tracking-wider text-[#9ba7b6] flex items-center gap-2">
                                <span class="h-1.5 w-1.5 rounded-full bg-[#ff9900]"></span>
                                <span>${geoName} (${regionCodes.length} Regions)</span>
                            </h4>
                            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                                ${cardsHtml}
                            </div>
                        </div>
                    `;
                }

            } catch (e) {
                console.error("Failed to load regions matrix:", e);
            }
        }

        function selectRegionFromMatrix(regionCode) {
            currentRegion = regionCode;
            document.getElementById('region-filter').value = regionCode;
            switchMainView('catalog');
            showToast(`Switched active region to ${regionCode.toUpperCase()}`);
            onRegionFilterChange();
        }

        window.addEventListener('load', async () => {
            const m1Link = document.getElementById('header-module1-link');
            if (m1Link) {
                m1Link.href = 'http://' + window.location.hostname + ':8001/app';
            }
            await checkAuthStatus();
            try {
                const res = await fetch('/api/admin/catalog/regions', {
                    headers: { 'X-Admin-Key': adminKey }
                });
                if (res.ok) {
                    regionsList = await res.json();
                }
            } catch (e) {
                console.error("Failed to load regions", e);
            }
            
            const filterSelect = document.getElementById('region-filter');
            filterSelect.innerHTML = '';
            
            if (regionsList.length > 0) {
                regionsList.forEach(r => {
                    filterSelect.innerHTML += `<option value="${r.region_code}" class="bg-[#0f141c] text-white font-mono">${r.region_code} — ${r.region_name}</option>`;
                });
            } else {
                filterSelect.innerHTML = `<option value="us-east-1" class="bg-[#0f141c] text-white font-mono">us-east-1 — US East (N. Virginia)</option>`;
            }
            
            filterSelect.value = currentRegion;
            await refreshProbes();
            await checkRegionSyncStatus();
            await fetchCatalog();
            await loadModules();
            await loadRegionsMatrix();
        });
    </script>
</body>
</html>
"""
