# services/requirement_analysis/app/module1_page.py

def get_module1_page_html() -> str:
    return r"""<!DOCTYPE html>
<html lang="en" class="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AetherOps Cloud - Module 1: Requirement Analysis & Sizing</title>
    <link rel="stylesheet" href="/static/fonts/fonts.css">
    <script src="/static/js/tailwind.js"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Plus Jakarta Sans', 'Segoe UI', -apple-system, BlinkMacSystemFont, 'sans-serif'],
                        mono: ['JetBrains Mono', 'Consolas', 'monospace']
                    },
                    colors: {
                        aether: {
                            header: '#161e2e',
                            orange: '#ec7211',
                            orangeHover: '#eb5f07',
                            orangeLight: '#ff9900',
                            blue: '#0972d3',
                            blueHover: '#033ebc',
                            green: '#16a34a',
                            red: '#dc2626'
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
            --bg-header: #ffffff;
            --border-header: #e2e8f0;
            --header-text: #0f172a;
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
            --card-shadow: none;
            --tab-active-col: #ff9900;
            --tab-inactive-col: #9ba7b6;
            --bg-header: #161e2e;
            --border-header: #2d3748;
            --header-text: #ffffff;
        }

        body { background-color: var(--bg-page); color: var(--text-body); transition: background-color 0.15s ease, color 0.15s ease; }
        .app-header { background-color: var(--bg-header); border-bottom: 1px solid var(--border-header); }
        .aws-card { background-color: var(--bg-card); border: 1px solid var(--border-card); box-shadow: var(--card-shadow); border-radius: 8px; }
        .aws-btn-primary { background-color: #ec7211; color: #ffffff; font-weight: 700; transition: all 0.15s ease-in-out; }
        .aws-btn-primary:hover { background-color: #eb5f07; }
        .aws-btn-secondary { background-color: var(--btn-sec-bg); border: 1px solid var(--btn-sec-border); color: var(--btn-sec-text); transition: all 0.15s ease-in-out; }
        .aws-btn-secondary:hover { background-color: var(--btn-sec-hover); border-color: #ec7211; }
        .aws-input { background-color: var(--input-bg); border: 1px solid var(--input-border); color: var(--input-text); transition: border-color 0.15s, box-shadow 0.15s; }
        .aws-input:focus { border-color: #ec7211; outline: none; box-shadow: 0 0 0 2px rgba(236, 114, 17, 0.2); }
        .tab-active { border-bottom: 2px solid #ec7211; color: var(--tab-active-col); font-weight: 700; }
        .tab-inactive { color: var(--tab-inactive-col); }
        .tab-inactive:hover { color: var(--text-title); }
        .box-subtle { background-color: var(--bg-subtle-card); border: 1px solid var(--border-card); }
        .text-title { color: var(--text-title); }
        .text-muted-custom { color: var(--text-muted); }

        /* Light mode specific header element adjustments */
        html:not(.dark) .app-header {
            background-color: #ffffff !important;
            border-bottom: 1px solid #e2e8f0 !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
        }
        html:not(.dark) .app-header .text-white:not(.aws-btn-primary):not(.bg-\[\#ec7211\]) {
            color: #0f172a !important;
        }
        html:not(.dark) .app-header .text-gray-300,
        html:not(.dark) .app-header .text-gray-200 {
            color: #334155 !important;
        }
        html:not(.dark) .app-header .text-gray-500 {
            color: #94a3b8 !important;
        }
        html:not(.dark) .app-header .bg-\[\#0f141c\],
        html:not(.dark) .app-header .bg-\[\#232f3e\] {
            background-color: #ffffff !important;
            border-color: #cbd5e1 !important;
            color: #1e293b !important;
        }
        html:not(.dark) .app-header .border-\[\#2d3748\],
        html:not(.dark) .app-header .border-\[\#414d5c\] {
            border-color: #e2e8f0 !important;
        }

        /* Guarantee Primary Buttons always stay vibrant orange with crisp white text */
        html:not(.dark) .aws-btn-primary,
        html:not(.dark) .aws-btn-primary *,
        html:not(.dark) .bg-\[\#ec7211\],
        html:not(.dark) .bg-\[\#ec7211\] * {
            color: #ffffff !important;
        }

        /* Secondary & theme-adaptive buttons in light mode */
        html:not(.dark) .aws-btn-secondary {
            background-color: #ffffff !important;
            border-color: #cbd5e1 !important;
            color: #1e293b !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
        }
        html:not(.dark) .aws-btn-secondary:hover {
            background-color: #f8fafc !important;
            border-color: #ec7211 !important;
            color: #0f172a !important;
        }

        /* Prevent any dark buttons from appearing in light mode across all views */
        html:not(.dark) button.bg-\[\#232f3e\],
        html:not(.dark) a.bg-\[\#232f3e\],
        html:not(.dark) div.bg-\[\#232f3e\] {
            background-color: #ffffff !important;
            border-color: #cbd5e1 !important;
            color: #1e293b !important;
        }
        html:not(.dark) button.bg-\[\#232f3e\]:hover,
        html:not(.dark) a.bg-\[\#232f3e\]:hover {
            background-color: #f8fafc !important;
            border-color: #ec7211 !important;
            color: #0f172a !important;
        }
    </style>
</head>
<body class="min-h-screen flex flex-col font-sans selection:bg-[#ec7211]/30 selection:text-[#ff9900]">

    <!-- Top Navigation Header -->
    <header class="app-header h-14 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-40 shadow-xs transition-colors duration-150">
        
        <!-- Left: Branding & Breadcrumb -->
        <div class="flex items-center space-x-3 shrink-0">
            <div class="flex items-center space-x-2">
                <span class="font-extrabold text-title text-base tracking-tight">AetherOps</span>
                <span class="text-[#ea580c] dark:text-[#ff9900] text-[10px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-orange-100 dark:bg-[#232f3e] border border-orange-200 dark:border-[#ff9900]/40 font-mono">MODULE 1</span>
                <span class="text-gray-400 dark:text-gray-500 hidden sm:inline">/</span>
                <span class="text-xs font-bold text-gray-600 dark:text-gray-300 font-mono hidden sm:inline">REQUIREMENT ANALYSIS & SIZING</span>
            </div>
        </div>

        <!-- Center: Telemetry Status Badges -->
        <div class="hidden lg:flex items-center space-x-2 text-xs">
            <span class="h-7 px-2.5 rounded-md bg-gray-100 dark:bg-[#0f141c] border border-gray-200 dark:border-[#2d3748] flex items-center gap-1.5 text-gray-700 dark:text-gray-300 font-mono text-[11px]">
                <span class="h-2 w-2 rounded-full bg-[#16a34a]"></span>
                <span>SQLite (requirements.db)</span>
            </span>
            <span class="h-7 px-2.5 rounded-md bg-gray-100 dark:bg-[#0f141c] border border-gray-200 dark:border-[#2d3748] flex items-center gap-1.5 text-gray-700 dark:text-gray-300 font-mono text-[11px]">
                <span class="h-2 w-2 rounded-full bg-[#16a34a]"></span>
                <span>Redis L1 Cache</span>
            </span>
            <span class="h-7 px-2.5 rounded-md bg-orange-50 dark:bg-[#0f141c] border border-orange-200 dark:border-[#2d3748] flex items-center gap-1.5 text-[#ea580c] dark:text-[#ff9900] font-mono text-[11px]">
                <span class="h-2 w-2 rounded-full bg-[#ec7211] animate-pulse"></span>
                <span>Port :8001</span>
            </span>
        </div>

        <!-- Right: Actions, Links & Theme Toggle -->
        <div class="flex items-center space-x-2 text-xs shrink-0">
            <a href="http://localhost:8000/admin" class="h-8 aws-btn-secondary px-3 rounded-md flex items-center gap-1.5 cursor-pointer text-xs font-semibold">
                <svg class="w-3.5 h-3.5 text-[#ec7211]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                <span class="hidden sm:inline">Admin Catalog</span>
            </a>

            <!-- Theme Toggler -->
            <button onclick="toggleTheme()" id="theme-toggle-btn" class="h-8 px-2.5 rounded-md aws-btn-secondary text-yellow-500 dark:text-yellow-400 transition cursor-pointer flex items-center gap-1.5 text-xs font-semibold" title="Toggle Light / Dark Theme">
                <span id="theme-toggle-icon">☀️</span>
                <span id="theme-toggle-text" class="text-xs">Light</span>
            </button>
        </div>

    </header>

    <!-- Main Workspace -->
    <main class="flex-1 p-4 sm:p-6 space-y-6 max-w-7xl mx-auto w-full">
        
        <!-- Hero Banner -->
        <div class="aws-card p-5 border-l-4 border-l-[#ec7211] flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
                <div class="flex items-center space-x-2">
                    <span class="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-[#ec7211]/20 text-[#ea580c] dark:text-[#ff9900] border border-[#ec7211]/40 font-mono">MICROSERVICE 1 / 8</span>
                    <span class="text-xs text-muted-custom font-mono">• Autonomous Workload Profiler</span>
                </div>
                <h1 class="text-xl font-bold text-title mt-1.5">Intelligent Cloud Architecture Sizing & Cost Optimization Engine</h1>
                <p class="text-xs text-muted-custom mt-1 max-w-3xl">
                    Configure your high-level system requirements below. The engine calculates precise compute, database, networking, and security topologies, provides technical justification ("Why that service"), and identifies immediate FinOps cost optimizations.
                </p>
            </div>
            <div class="flex flex-col sm:flex-row gap-2 shrink-0">
                <button onclick="fillSamplePreset('fintech')" class="aws-btn-secondary px-3 py-1.5 rounded text-xs transition font-semibold">
                    Load FinTech Preset
                </button>
                <button onclick="fillSamplePreset('saas')" class="aws-btn-secondary px-3 py-1.5 rounded text-xs transition font-semibold">
                    Load SaaS Starter
                </button>
            </div>
        </div>

        <!-- Two-Column Primary Layout -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            
            <!-- LEFT COLUMN: Modern Unified Workload Intake Console (5 Cols) -->
            <div class="lg:col-span-5 space-y-4">
                
                <div class="aws-card p-5 space-y-4 border-t-2 border-t-[#ec7211]">
                    
                    <!-- Header with Mode Switcher -->
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-3 border-b border-[var(--border-card)]">
                        <div class="flex items-center space-x-2">
                            <span class="h-2.5 w-2.5 rounded-full bg-[#ec7211]"></span>
                            <h2 class="text-sm font-bold text-title uppercase tracking-wider">Workload Parameters & Sizing Intake</h2>
                        </div>
                        
                        <!-- Modern Intake Mode Switcher -->
                        <div class="flex items-center p-1 rounded-lg bg-gray-100 dark:bg-[#0f141c] border border-gray-200 dark:border-[#2d3748] text-xs">
                            <button type="button" onclick="switchIntakeMode('prompt')" id="tab-intake-prompt" 
                                class="px-2.5 py-1 text-xs font-bold rounded-md bg-[#ec7211] text-white shadow-xs transition flex items-center gap-1 cursor-pointer">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                                <span>Prompt Sizing</span>
                            </button>
                            <button type="button" onclick="switchIntakeMode('form')" id="tab-intake-form" 
                                class="px-2.5 py-1 text-xs font-semibold rounded-md text-muted-custom hover:text-title transition flex items-center gap-1 cursor-pointer">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/></svg>
                                <span>Manual Specs</span>
                            </button>
                        </div>
                    </div>

                    <!-- MODE 1: PROMPT-BASED SIZING (Default) -->
                    <div id="intake-mode-prompt" class="space-y-4">
                        <div class="space-y-1">
                            <div class="flex items-center justify-between">
                                <label class="block text-xs font-bold text-title">
                                    Describe your architecture in plain English:
                                </label>
                                <span class="text-[10px] font-mono text-[#ea580c] dark:text-[#ff9900] px-2 py-0.5 rounded bg-[#ec7211]/15 border border-[#ec7211]/30">Zero Hallucination</span>
                            </div>
                            <p class="text-[11px] text-muted-custom leading-relaxed">
                                Our autonomous NLP parser extracts computing streams, technologies, traffic scale, and compliance parameters with exact pricing grounding.
                            </p>
                        </div>

                        <!-- Prompt Input Area with Modern Focus State -->
                        <div class="relative">
                            <textarea id="ai-prompt-input" rows="4" 
                                placeholder="e.g. Architect a scalable Fintech payment gateway with Python FastAPI and PostgreSQL. Requires PCI-DSS compliance, multi-AZ HA, Redis caching, handling ~300 RPS under $400/month in us-east-1."
                                class="aws-input w-full p-3 rounded-lg text-xs leading-relaxed resize-none font-sans border-2 border-gray-200 dark:border-gray-700 focus:border-[#ec7211] shadow-xs"></textarea>
                        </div>

                        <!-- Quick Template Pills -->
                        <div class="space-y-1.5">
                            <div class="text-[10px] font-bold text-muted-custom uppercase tracking-wider font-mono">
                                Quick Workload Scenarios:
                            </div>
                            <div class="flex flex-wrap gap-1.5 text-[10px]">
                                <button type="button" onclick="setPromptAndAnalyze('Fintech payment engine on FastAPI and PostgreSQL, PCI-DSS compliance, multi-AZ HA, 300 RPS, budget under $450/mo in us-east-1.')" 
                                    class="px-2.5 py-1 rounded-full box-subtle text-muted-custom hover:text-title hover:border-[#ec7211] font-mono transition cursor-pointer">
                                    🏦 Fintech PCI-DSS
                                </button>
                                <button type="button" onclick="setPromptAndAnalyze('Enterprise healthcare portal with Python FastAPI and PostgreSQL, HIPAA security, multi-AZ, 100 GB storage under $500/mo.')" 
                                    class="px-2.5 py-1 rounded-full box-subtle text-muted-custom hover:text-title hover:border-[#ec7211] font-mono transition cursor-pointer">
                                    🏥 Healthcare HIPAA
                                </button>
                                <button type="button" onclick="setPromptAndAnalyze('High-traffic E-commerce store with Node.js, React, Redis caching, MySQL, CloudFront CDN, 400 RPS under $600/mo.')" 
                                    class="px-2.5 py-1 rounded-full box-subtle text-muted-custom hover:text-title hover:border-[#ec7211] font-mono transition cursor-pointer">
                                    🛒 E-Commerce
                                </button>
                                <button type="button" onclick="setPromptAndAnalyze('AI machine learning inference pipeline on FastAPI with EKS, high traffic 500 RPS, CloudFront CDN, budget $600.')" 
                                    class="px-2.5 py-1 rounded-full box-subtle text-muted-custom hover:text-title hover:border-[#ec7211] font-mono transition cursor-pointer">
                                    🤖 AI Inference
                                </button>
                                <button type="button" onclick="setPromptAndAnalyze('Lightweight internal dev sandbox for testing prototypes on React and Node.js, single-AZ, budget under $40.')" 
                                    class="px-2.5 py-1 rounded-full box-subtle text-muted-custom hover:text-title hover:border-[#ec7211] font-mono transition cursor-pointer">
                                    🧪 Dev Sandbox &lt;$40
                                </button>
                            </div>
                        </div>

                        <!-- Real-time Extracted Profile Badges -->
                        <div id="extracted-profile-preview" class="hidden">
                            <!-- Populated dynamically via JS -->
                        </div>

                        <!-- Action Buttons -->
                        <div class="flex flex-col sm:flex-row gap-2 pt-1">
                            <button type="button" id="btn-ai-analyze" onclick="handleAiAnalyzeDirect()" 
                                class="flex-1 aws-btn-primary py-2.5 px-4 rounded-lg text-xs font-bold flex items-center justify-center gap-2 cursor-pointer shadow-sm">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                                <span>Identify & Analyze Workload</span>
                            </button>
                            <button type="button" onclick="handleAiAutoFillAndSwitch()" 
                                class="aws-btn-secondary py-2.5 px-3.5 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer">
                                <svg class="w-3.5 h-3.5 text-[#ec7211]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                                <span>Edit in Form</span>
                            </button>
                        </div>
                    </div>

                    <!-- MODE 2: DETAILED PARAMETERS FORM (Hidden by default, cleanly toggled) -->
                    <div id="intake-mode-form" class="space-y-4 hidden">
                        <form id="requirements-form" onsubmit="handleAnalyzeSubmit(event)" class="space-y-3 text-xs">
                            
                            <!-- Group 1: Project Identity & Region -->
                            <div class="box-subtle p-3 rounded-lg space-y-2">
                                <div class="text-[10px] font-bold text-muted-custom uppercase tracking-wider font-mono">1. Project & Region</div>
                                <div>
                                    <label class="block text-muted-custom font-semibold mb-1">Project Name</label>
                                    <input type="text" id="req-project-name" required placeholder="e.g., payment-gateway-core" value="fintech-payment-engine"
                                        class="aws-input w-full p-2 rounded text-xs font-mono">
                                </div>
                                <div class="grid grid-cols-2 gap-2.5">
                                    <div>
                                        <label class="block text-muted-custom font-semibold mb-1">Cloud Stream</label>
                                        <select id="req-stream" class="aws-input w-full p-2 rounded text-xs">
                                            <option value="web_application" selected>Web Application</option>
                                            <option value="ai_ml">AI / Machine Learning</option>
                                            <option value="iot">IoT Ingestion Hub</option>
                                            <option value="devops_tooling">DevOps Tooling / CI</option>
                                            <option value="dev_sandbox">Developer Sandbox</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label class="block text-muted-custom font-semibold mb-1">Target Region</label>
                                        <select id="req-region" class="aws-input w-full p-2 rounded text-xs font-mono">
                                            <option value="us-east-1" selected>us-east-1 (N. Virginia)</option>
                                            <option value="us-east-2">us-east-2 (Ohio)</option>
                                            <option value="us-west-2">us-west-2 (Oregon)</option>
                                            <option value="ap-south-1">ap-south-1 (Mumbai)</option>
                                            <option value="eu-west-1">eu-west-1 (Ireland)</option>
                                            <option value="eu-central-1">eu-central-1 (Frankfurt)</option>
                                            <option value="ap-southeast-1">ap-southeast-1 (Singapore)</option>
                                            <option value="ca-central-1">ca-central-1 (Central)</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <!-- Group 2: Software Technology Stack -->
                            <div class="box-subtle p-3 rounded-lg space-y-2">
                                <div class="text-[10px] font-bold text-muted-custom uppercase tracking-wider font-mono">2. Technology Stack</div>
                                <div class="grid grid-cols-3 gap-2">
                                    <div>
                                        <label class="block text-[10px] text-muted-custom mb-1">Frontend</label>
                                        <select id="req-frontend" class="aws-input w-full p-1.5 rounded text-[11px]">
                                            <option value="react_vue_angular" selected>React / Vue</option>
                                            <option value="simple_html_css">HTML / CSS</option>
                                            <option value="none">None (API only)</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label class="block text-[10px] text-muted-custom mb-1">Backend</label>
                                        <select id="req-backend" class="aws-input w-full p-1.5 rounded text-[11px]">
                                            <option value="python_fastapi_django" selected>Python / FastAPI</option>
                                            <option value="nodejs_express">Node.js Express</option>
                                            <option value="java_spring">Java Spring</option>
                                            <option value="none">None</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label class="block text-[10px] text-muted-custom mb-1">Database</label>
                                        <select id="req-database" class="aws-input w-full p-1.5 rounded text-[11px]">
                                            <option value="postgresql" selected>PostgreSQL</option>
                                            <option value="mysql">MySQL</option>
                                            <option value="none">None</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <!-- Group 3: Scale & Reliability SLA -->
                            <div class="box-subtle p-3 rounded-lg space-y-2">
                                <div class="text-[10px] font-bold text-muted-custom uppercase tracking-wider font-mono">3. Scale & High Availability</div>
                                <div class="grid grid-cols-2 gap-2.5">
                                    <div>
                                        <label class="block text-[10px] text-muted-custom mb-1">Traffic Scale</label>
                                        <select id="req-traffic" class="aws-input w-full p-2 rounded text-xs">
                                            <option value="hobby_dev">Hobby / Dev (1 RPS)</option>
                                            <option value="growth" selected>Growth (30-45 RPS)</option>
                                            <option value="production">Production (200-400 RPS)</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label class="block text-[10px] text-muted-custom mb-1">Reliability Tier</label>
                                        <select id="req-reliability" class="aws-input w-full p-2 rounded text-xs">
                                            <option value="dev_testing">Dev/Test (95% SLA)</option>
                                            <option value="production_safe" selected>Prod-Safe (Multi-AZ 99.9%)</option>
                                            <option value="mission_critical">Mission-Critical (99.99%)</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <!-- Group 4: Storage, Governance & Budget -->
                            <div class="box-subtle p-3 rounded-lg space-y-2">
                                <div class="text-[10px] font-bold text-muted-custom uppercase tracking-wider font-mono">4. Storage, Governance & Budget</div>
                                <div class="grid grid-cols-3 gap-2">
                                    <div>
                                        <label class="block text-[10px] text-muted-custom mb-1">Storage (GB)</label>
                                        <input type="number" id="req-storage" min="0" value="80" class="aws-input w-full p-1.5 rounded text-xs font-mono">
                                    </div>
                                    <div>
                                        <label class="block text-[10px] text-muted-custom mb-1">Compliance</label>
                                        <select id="req-security" class="aws-input w-full p-1.5 rounded text-[11px]">
                                            <option value="standard">Standard</option>
                                            <option value="payment_processing" selected>PCI-DSS / Finance</option>
                                            <option value="healthcare">HIPAA Healthcare</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label class="block text-[10px] text-muted-custom mb-1">Budget ($/mo)</label>
                                        <input type="number" id="req-budget" min="0" placeholder="Optional" value="600" class="aws-input w-full p-1.5 rounded text-xs font-mono">
                                    </div>
                                </div>
                            </div>

                            <!-- Group 5: DevOps Tooling -->
                            <div class="box-subtle p-3 rounded-lg space-y-2">
                                <div class="text-[10px] font-bold text-muted-custom uppercase tracking-wider font-mono">5. DevOps & Orchestration</div>
                                <div class="grid grid-cols-2 gap-2.5">
                                    <div>
                                        <label class="block text-[10px] text-muted-custom mb-1">Orchestration</label>
                                        <select id="req-orchestration" class="aws-input w-full p-2 rounded text-xs">
                                            <option value="kubernetes" selected>Kubernetes (K8s / EKS)</option>
                                            <option value="ecs_fargate">AWS ECS Fargate</option>
                                            <option value="docker_compose">Docker Compose</option>
                                            <option value="none">None (VM Bare)</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label class="block text-[10px] text-muted-custom mb-1">Monitoring</label>
                                        <select id="req-monitoring" class="aws-input w-full p-2 rounded text-xs">
                                            <option value="comprehensive_prom_grafana" selected>Prometheus + Grafana</option>
                                            <option value="cloudwatch_native">AWS CloudWatch Native</option>
                                            <option value="basic_health_only">Basic Health Only</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <!-- Submit Buttons -->
                            <div class="pt-2 flex items-center gap-2">
                                <button type="submit" id="btn-analyze" class="aws-btn-primary flex-1 py-2.5 px-4 rounded-lg text-xs font-bold shadow flex items-center justify-center gap-2 cursor-pointer">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                                    <span>Analyze & Size Workload</span>
                                </button>
                                <button type="button" onclick="saveCurrentProject()" class="aws-btn-secondary py-2.5 px-3.5 rounded-lg text-xs font-bold flex items-center gap-1.5 cursor-pointer">
                                    <svg class="w-4 h-4 text-[#ec7211]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/></svg>
                                    <span>Save</span>
                                </button>
                            </div>

                        </form>
                    </div>

                </div>

            </div>

            <!-- RIGHT COLUMN: Sizing Breakdown & Rationales (7 Cols) -->
            <div class="lg:col-span-7 space-y-5">
                
                <!-- Sizing Output Card -->
                <div class="aws-card p-5 space-y-4" id="results-card">
                    
                    <!-- Sizing Header Summary Bar -->
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-3 border-b border-[var(--border-card)]">
                        <div>
                            <div class="flex items-center space-x-2">
                                <span id="out-tier-badge" class="px-2.5 py-0.5 rounded text-[10px] font-extrabold uppercase bg-green-100 dark:bg-[#1d8102]/20 text-green-700 dark:text-[#1d8102] border border-green-300 dark:border-[#1d8102]/40 font-mono">
                                    PRODUCTION-STANDARD
                                </span>
                                <span id="out-ha-badge" class="px-2 py-0.5 rounded text-[10px] font-mono box-subtle text-title">
                                    Multi-AZ
                                </span>
                            </div>
                            <h2 class="text-base font-bold text-title mt-1" id="out-project-title">fintech-payment-engine</h2>
                        </div>
                        <div class="text-right">
                            <div class="text-xs text-muted-custom">Estimated Monthly Spend</div>
                            <div class="text-xl font-extrabold text-title font-mono" id="out-total-cost">$148.20 <span class="text-xs text-muted-custom font-normal">/ mo</span></div>
                            <div class="text-[10px] text-green-600 dark:text-[#1d8102] font-semibold" id="out-budget-status">Within $600.00 Budget Limit</div>
                        </div>
                    </div>

                    <!-- Output Navigation Tabs -->
                    <div class="flex items-center space-x-4 border-b border-[var(--border-card)] text-xs font-semibold overflow-x-auto">
                        <button onclick="switchResultTab('specs')" id="tab-btn-specs" class="pb-2.5 tab-active flex items-center gap-1.5 cursor-pointer shrink-0">
                            <svg class="w-3.5 h-3.5 text-[#ec7211]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                            <span>Services & Sizing</span>
                        </button>
                        <button onclick="switchResultTab('why')" id="tab-btn-why" class="pb-2.5 tab-inactive flex items-center gap-1.5 cursor-pointer shrink-0">
                            <svg class="w-3.5 h-3.5 text-[#0972d3]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
                            <span>Why These Services?</span>
                        </button>
                        <button onclick="switchResultTab('finops')" id="tab-btn-finops" class="pb-2.5 tab-inactive flex items-center gap-1.5 cursor-pointer shrink-0">
                            <svg class="w-3.5 h-3.5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                            <span>Cost Optimization</span>
                        </button>
                        <button onclick="switchResultTab('ai')" id="tab-btn-ai" class="pb-2.5 tab-inactive flex items-center gap-1.5 cursor-pointer shrink-0">
                            <svg class="w-3.5 h-3.5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                            <span>Well-Architected Review</span>
                        </button>
                        <button onclick="switchResultTab('finder')" id="tab-btn-finder" class="pb-2.5 tab-inactive flex items-center gap-1.5 cursor-pointer shrink-0">
                            <svg class="w-3.5 h-3.5 text-[#ec7211]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                            <span>Smart Sizing & Recommendations</span>
                        </button>
                    </div>

                    <!-- TAB 1: Sizing Specifications Cards -->
                    <div id="tab-content-specs" class="space-y-3">
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3" id="specs-cards-container">
                            <!-- Populated dynamically via JavaScript -->
                        </div>
                    </div>

                    <!-- TAB 2: Why These Services? -->
                    <div id="tab-content-why" class="space-y-3 hidden">
                        <div class="text-[11px] text-muted-custom italic mb-2">
                            Architectural justification and design rationale mapped directly to your workload requirements:
                        </div>
                        <div class="space-y-3" id="rationales-container">
                            <!-- Populated dynamically via JavaScript -->
                        </div>
                    </div>

                    <!-- TAB 3: FinOps Cost Optimization Opportunities -->
                    <div id="tab-content-finops" class="space-y-3 hidden">
                        <div class="text-[11px] text-muted-custom mb-2">
                            High-impact cost reduction opportunities identified for this workload:
                        </div>
                        <div class="space-y-3" id="finops-container">
                            <!-- Populated dynamically via JavaScript -->
                        </div>
                    </div>

                    <!-- TAB 4: Well-Architected Framework Evaluation -->
                    <div id="tab-content-ai" class="space-y-3 hidden">
                        <div class="text-[11px] text-muted-custom mb-2">
                            Cloud Architecture 6-Pillar Evaluation & Grounded Synthesis:
                        </div>
                        <div class="space-y-3" id="ai-advisor-container">
                            <!-- Populated dynamically via JavaScript -->
                        </div>
                    </div>

                    <!-- TAB 5: Smart Sizing & Recommendations (Human-friendly UI) -->
                    <div id="tab-content-finder" class="space-y-4 hidden">
                        <div class="box-subtle rounded-lg p-4 space-y-4">
                            <div class="flex items-center justify-between border-b border-[var(--border-card)] pb-3">
                                <div>
                                    <div class="text-xs font-bold text-title flex items-center gap-1.5">
                                        <svg class="w-4 h-4 text-[#ec7211]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                                        <span>Smart Workload Instance Matcher</span>
                                    </div>
                                    <p class="text-[11px] text-muted-custom mt-0.5">
                                        Evaluates compute, memory, and traffic requirements to identify the best price-performance instances.
                                    </p>
                                </div>
                                <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-[#ec7211]/15 text-[#ea580c] dark:text-[#ff9900] border border-[#ec7211]/30">Intelligent Sizing</span>
                            </div>

                            <!-- Input Grid -->
                            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                                <div>
                                    <label class="block text-[11px] text-muted-custom mb-1 font-semibold">Min vCPUs</label>
                                    <input type="number" id="finder-min-vcpus" value="2" min="1" max="128" class="aws-input w-full p-2 rounded text-xs font-mono">
                                </div>
                                <div>
                                    <label class="block text-[11px] text-muted-custom mb-1 font-semibold">Min RAM (GiB)</label>
                                    <input type="number" id="finder-min-ram" value="4.0" step="0.5" min="0.5" class="aws-input w-full p-2 rounded text-xs font-mono">
                                </div>
                                <div>
                                    <label class="block text-[11px] text-muted-custom mb-1 font-semibold">RAM:vCPU Profile</label>
                                    <select id="finder-target-ratio" class="aws-input w-full p-2 rounded text-xs font-mono">
                                        <option value="4.0" selected>General Purpose (4:1)</option>
                                        <option value="2.0">Compute Intensive (2:1)</option>
                                        <option value="8.0">Memory Intensive (8:1)</option>
                                        <option value="1.0">Balanced Batch (1:1)</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-[11px] text-muted-custom mb-1 font-semibold">Optimization Focus</label>
                                    <select id="finder-opt-goal" class="aws-input w-full p-2 rounded text-xs">
                                        <option value="balanced" selected>⚖️ Balanced (Recommended)</option>
                                        <option value="lowest_cost">💰 Lowest Cost First</option>
                                        <option value="performance">⚡ Maximum Headroom</option>
                                        <option value="high_availability">🛡️ High Reliability</option>
                                    </select>
                                </div>
                            </div>

                            <!-- Workload Concurrency & Architecture Row -->
                            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-1">
                                <div>
                                    <label class="block text-[11px] text-muted-custom mb-1 font-semibold">Target Traffic (RPS)</label>
                                    <input type="number" id="finder-target-rps" value="250" min="1" class="aws-input w-full p-2 rounded text-xs font-mono">
                                </div>
                                <div>
                                    <label class="block text-[11px] text-muted-custom mb-1 font-semibold">Avg Latency (ms)</label>
                                    <input type="number" id="finder-avg-lat" value="120" min="1" class="aws-input w-full p-2 rounded text-xs font-mono">
                                </div>
                                <div>
                                    <label class="block text-[11px] text-muted-custom mb-1 font-semibold">Hardware Architecture</label>
                                    <select id="finder-arch" class="aws-input w-full p-2 rounded text-xs">
                                        <option value="any" selected>Any Architecture</option>
                                        <option value="arm64">AWS Graviton (arm64)</option>
                                        <option value="x86_64">Intel / AMD (x86_64)</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-[11px] text-muted-custom mb-1 font-semibold">Cloud Service</label>
                                    <select id="finder-service" class="aws-input w-full p-2 rounded text-xs font-mono">
                                        <option value="ec2" selected>Amazon EC2 (Compute)</option>
                                        <option value="rds">Amazon RDS (Database)</option>
                                    </select>
                                </div>
                            </div>

                            <!-- Action button -->
                            <div class="flex items-center justify-between pt-2">
                                <div class="text-[11px] text-muted-custom">
                                    <span>Workload-Aware Sizing • Real AWS Console On-Demand Pricing</span>
                                </div>
                                <button type="button" onclick="runInstanceFinderEvaluation()" id="btn-run-finder" class="aws-btn-primary px-4 py-2 rounded text-xs font-bold flex items-center gap-1.5 shadow cursor-pointer">
                                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                                    <span>Find Best Matching Instances</span>
                                </button>
                            </div>
                        </div>

                        <!-- Results Container -->
                        <div id="finder-results-container" class="space-y-3">
                            <div class="text-center py-8 text-xs text-muted-custom font-mono box-subtle rounded-lg">
                                Adjust requirements above and click "Find Best Matching Instances" to view ranked recommendations.
                            </div>
                        </div>
                    </div>


                    <!-- Module 2 Dispatch Strip -->
                    <div class="pt-4 border-t border-[var(--border-card)] flex flex-col sm:flex-row items-center justify-between gap-3 box-subtle p-3 rounded">
                        <div>
                            <div class="text-xs font-bold text-title flex items-center gap-1.5">
                                <span>Next Pipeline Step: Module 2</span>
                                <span class="px-1.5 py-0.2 rounded text-[9px] font-mono bg-orange-100 dark:bg-[#232f3e] text-[#ea580c] dark:text-[#ff9900]">Architecture Diagram</span>
                            </div>
                            <p class="text-[11px] text-muted-custom">Forward this compiled profile to the Visual Graph Builder on port :8002.</p>
                        </div>
                        <button onclick="dispatchToModule2()" id="btn-dispatch" class="aws-btn-secondary py-2 px-3.5 rounded text-xs font-bold flex items-center gap-1.5 shrink-0 cursor-pointer">
                            <span>Dispatch to Module 2</span>
                            <svg class="w-3.5 h-3.5 text-[#ec7211]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                        </button>
                    </div>

                </div>

            </div>

        </div>

        <!-- Saved Projects History -->
        <div class="aws-card p-5 space-y-3">
            <div class="flex items-center justify-between border-b border-[var(--border-card)] pb-3">
                <div class="flex items-center space-x-2">
                    <span class="h-2.5 w-2.5 rounded-full bg-[#16a34a]"></span>
                    <h3 class="text-sm font-bold text-title uppercase tracking-wider">Saved Requirement Profiles (SQLite)</h3>
                </div>
                <button onclick="loadSavedProjects()" class="text-xs text-[#0972d3] hover:underline flex items-center gap-1 font-semibold">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                    Refresh List
                </button>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse">
                    <thead>
                        <tr class="border-b border-[var(--border-card)] text-muted-custom">
                            <th class="py-2 px-3 font-semibold">Project Name</th>
                            <th class="py-2 px-3 font-semibold">Region</th>
                            <th class="py-2 px-3 font-semibold">Stream</th>
                            <th class="py-2 px-3 font-semibold">Tier</th>
                            <th class="py-2 px-3 font-semibold text-right">Est. Monthly</th>
                            <th class="py-2 px-3 font-semibold text-center">Status</th>
                            <th class="py-2 px-3 font-semibold text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="saved-projects-tbody" class="divide-y divide-[var(--border-card)]">
                        <tr>
                            <td colspan="7" class="py-4 text-center text-muted-custom">Loading saved projects from requirements.db...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

    </main>

    <!-- Footer -->
    <footer class="app-header py-4 px-6 text-center text-xs text-muted-custom flex flex-col sm:flex-row items-center justify-between gap-3 mt-12 transition-colors">
        <div class="flex items-center space-x-4">
            <span class="font-bold text-title">AetherOps Cloud</span>
            <span>•</span>
            <span>Module 1: Autonomous Workload Profiler</span>
            <span>•</span>
            <span class="font-mono text-muted-custom">Port :8001</span>
        </div>
        <div class="font-mono text-[11px] text-muted-custom">
            &copy; 2026 AetherOps Cloud • Orchestrated by Kubernetes (K8s)
        </div>
    </footer>

    <!-- JavaScript Logic -->
    <script>
        let currentProjectId = null;

        // Cross-Application Theme Synchronization
        function getCrossAppTheme() {
            const urlParams = new URLSearchParams(window.location.search);
            const urlTheme = urlParams.get('theme');
            if (urlTheme === 'light' || urlTheme === 'dark') return urlTheme;

            const match = document.cookie.match(/(?:^|;\s*)aether_theme=([^;]+)/);
            if (match && (match[1] === 'light' || match[1] === 'dark')) return match[1];

            const stored = localStorage.getItem('aether_theme');
            if (stored === 'light' || stored === 'dark') return stored;

            return 'light';
        }

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
            document.cookie = "aether_theme=" + theme + "; path=/; max-age=31536000; SameSite=Lax";

            // Update links to Admin Console to pass current theme
            const adminLinks = document.querySelectorAll('a[href*=":8000"], a[href^="/admin"]');
            adminLinks.forEach(a => {
                try {
                    const u = new URL(a.href, window.location.origin);
                    u.searchParams.set('theme', theme);
                    a.href = u.toString();
                } catch(e) {}
            });
        }

        function toggleTheme() {
            const isDark = document.documentElement.classList.contains('dark');
            applyTheme(isDark ? 'light' : 'dark');
        }

        // Initialize cross-app theme
        applyTheme(getCrossAppTheme());

        window.addEventListener('focus', () => {
            const current = getCrossAppTheme();
            const isDark = document.documentElement.classList.contains('dark');
            const shouldBeDark = (current === 'dark');
            if (isDark !== shouldBeDark) {
                applyTheme(current);
            }
        });

        const samplePresets = {
            fintech: {
                project_name: "fintech-payment-engine",
                stream: "web_application",
                region: "us-east-1",
                frontend: "react_vue_angular",
                backend: "python_fastapi_django",
                database: "postgresql",
                traffic: "growth",
                reliability: "production_safe",
                storage: 80,
                security: "payment_processing",
                budget: 600,
                orchestration: "kubernetes",
                monitoring: "comprehensive_prom_grafana"
            },
            saas: {
                project_name: "saas-starter-portal",
                stream: "web_application",
                region: "us-east-1",
                frontend: "react_vue_angular",
                backend: "nodejs_express",
                database: "postgresql",
                traffic: "growth",
                reliability: "production_safe",
                storage: 40,
                security: "standard",
                budget: 250,
                orchestration: "ecs_fargate",
                monitoring: "cloudwatch_native"
            }
        };

        function fillSamplePreset(key) {
            const p = samplePresets[key];
            if (!p) return;
            document.getElementById('req-project-name').value = p.project_name;
            document.getElementById('req-stream').value = p.stream;
            document.getElementById('req-region').value = p.region;
            document.getElementById('req-frontend').value = p.frontend;
            document.getElementById('req-backend').value = p.backend;
            document.getElementById('req-database').value = p.database;
            document.getElementById('req-traffic').value = p.traffic;
            document.getElementById('req-reliability').value = p.reliability;
            document.getElementById('req-storage').value = p.storage;
            document.getElementById('req-security').value = p.security;
            document.getElementById('req-budget').value = p.budget;
            document.getElementById('req-orchestration').value = p.orchestration;
            document.getElementById('req-monitoring').value = p.monitoring;
            triggerAnalyze();
        }

        function switchIntakeMode(mode) {
            const promptView = document.getElementById('intake-mode-prompt');
            const formView = document.getElementById('intake-mode-form');
            const tabPrompt = document.getElementById('tab-intake-prompt');
            const tabForm = document.getElementById('tab-intake-form');

            if (mode === 'prompt') {
                if (promptView) promptView.classList.remove('hidden');
                if (formView) formView.classList.add('hidden');
                if (tabPrompt) tabPrompt.className = 'px-2.5 py-1 text-xs font-bold rounded-md bg-[#ec7211] text-white shadow-xs transition flex items-center gap-1 cursor-pointer';
                if (tabForm) tabForm.className = 'px-2.5 py-1 text-xs font-semibold rounded-md text-muted-custom hover:text-title transition flex items-center gap-1 cursor-pointer';
            } else {
                if (promptView) promptView.classList.add('hidden');
                if (formView) formView.classList.remove('hidden');
                if (tabForm) tabForm.className = 'px-2.5 py-1 text-xs font-bold rounded-md bg-[#ec7211] text-white shadow-xs transition flex items-center gap-1 cursor-pointer';
                if (tabPrompt) tabPrompt.className = 'px-2.5 py-1 text-xs font-semibold rounded-md text-muted-custom hover:text-title transition flex items-center gap-1 cursor-pointer';
            }
        }

        async function handleAiAutoFillAndSwitch() {
            await handleAiAutoFill();
            switchIntakeMode('form');
        }

        function renderExtractedProfileBadges(p, conf, engine) {
            const container = document.getElementById('extracted-profile-preview');
            if (!container) return;
            container.classList.remove('hidden');
            const confPercent = conf ? Math.round(conf * 100) : 98;
            container.innerHTML = `
                <div class="p-3 rounded-lg box-subtle space-y-2 border border-[#ec7211]/30 bg-orange-50/60 dark:bg-orange-950/20">
                    <div class="flex items-center justify-between text-[11px]">
                        <span class="font-bold text-title flex items-center gap-1.5 font-mono">
                            <span class="h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
                            AI Identified Architecture Profile
                        </span>
                        <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300">
                            ${confPercent}% Match Confidence
                        </span>
                    </div>
                    <div class="flex flex-wrap gap-1.5 text-[11px] font-mono">
                        <span class="px-2 py-0.5 rounded bg-white dark:bg-[#1b2533] border border-gray-200 dark:border-gray-700 text-title">🏢 Stream: <strong>${p.stream || 'web_application'}</strong></span>
                        <span class="px-2 py-0.5 rounded bg-white dark:bg-[#1b2533] border border-gray-200 dark:border-gray-700 text-title">🐍 Backend: <strong>${p.technology?.backend || 'fastapi'}</strong></span>
                        <span class="px-2 py-0.5 rounded bg-white dark:bg-[#1b2533] border border-gray-200 dark:border-gray-700 text-title">🐘 Database: <strong>${p.technology?.database || 'postgresql'}</strong></span>
                        <span class="px-2 py-0.5 rounded bg-white dark:bg-[#1b2533] border border-gray-200 dark:border-gray-700 text-title">📈 Scale: <strong>${p.traffic_scale || 'growth'}</strong></span>
                        <span class="px-2 py-0.5 rounded bg-white dark:bg-[#1b2533] border border-gray-200 dark:border-gray-700 text-title">🛡️ Security: <strong>${p.security_need || 'standard'}</strong></span>
                        <span class="px-2 py-0.5 rounded bg-white dark:bg-[#1b2533] border border-gray-200 dark:border-gray-700 text-title">💰 Budget: <strong>$${p.monthly_budget || 400}/mo</strong></span>
                    </div>
                </div>
            `;
        }

        function setPromptAndAnalyze(promptText) {
            document.getElementById('ai-prompt-input').value = promptText;
            switchIntakeMode('prompt');
            handleAiAnalyzeDirect();
        }

        function getFormData() {
            return {
                project_name: document.getElementById('req-project-name').value.trim() || 'unnamed-project',
                stream: document.getElementById('req-stream').value,
                target_region: document.getElementById('req-region').value,
                technology: {
                    frontend: document.getElementById('req-frontend').value,
                    backend: document.getElementById('req-backend').value,
                    database: document.getElementById('req-database').value
                },
                traffic_scale: document.getElementById('req-traffic').value,
                reliability: document.getElementById('req-reliability').value,
                data_storage_gb: parseFloat(document.getElementById('req-storage').value) || 20,
                security_need: document.getElementById('req-security').value,
                monthly_budget: parseFloat(document.getElementById('req-budget').value) || null,
                operations: {
                    container_orchestration: document.getElementById('req-orchestration').value,
                    ci_cd_provider: 'github_actions',
                    iac_tool: 'terraform'
                },
                monitoring: {
                    level: document.getElementById('req-monitoring').value,
                    log_retention_days: 30
                }
            };
        }

        async function triggerAnalyze() {
            const payload = getFormData();
            const btn = document.getElementById('btn-analyze');
            btn.innerHTML = `<span>Sizing Workload...</span>`;
            btn.disabled = true;

            try {
                const res = await fetch('/api/v1/requirements/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                renderAnalysisResults(data);
            } catch (err) {
                console.error("Analysis failed:", err);
            } finally {
                btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg><span>Analyze & Size Workload</span>`;
                btn.disabled = false;
            }
        }

        async function handleAiAutoFill() {
            const prompt = document.getElementById('ai-prompt-input').value.trim();
            if (!prompt) {
                alert("Please enter a workload description in the prompt box first.");
                return;
            }
            const btn = document.getElementById('btn-ai-autofill');
            btn.innerHTML = `<span>Parsing...</span>`;
            btn.disabled = true;

            try {
                const res = await fetch('/api/v1/requirements/parse-prompt', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt })
                });
                const data = await res.json();
                if (data.status === 'SUCCESS' && data.parsed_input) {
                    const p = data.parsed_input;
                    if (p.project_name) document.getElementById('req-project-name').value = p.project_name;
                    if (p.stream) document.getElementById('req-stream').value = p.stream;
                    if (p.technology) {
                        if (p.technology.frontend) document.getElementById('req-frontend').value = p.technology.frontend;
                        if (p.technology.backend) document.getElementById('req-backend').value = p.technology.backend;
                        if (p.technology.database) document.getElementById('req-database').value = p.technology.database;
                    }
                    if (p.traffic_scale) document.getElementById('req-traffic').value = p.traffic_scale;
                    if (p.reliability) document.getElementById('req-reliability').value = p.reliability;
                    if (p.data_storage_gb) document.getElementById('req-storage').value = p.data_storage_gb;
                    if (p.security_need) document.getElementById('req-security').value = p.security_need;
                    if (p.monthly_budget) document.getElementById('req-budget').value = p.monthly_budget;
                    if (p.operations && p.operations.container_orchestration) {
                        document.getElementById('req-orchestration').value = p.operations.container_orchestration;
                    }
                    if (p.monitoring && p.monitoring.level) {
                        document.getElementById('req-monitoring').value = p.monitoring.level;
                    }
                    triggerAnalyze();
                }
            } catch (err) {
                alert("Failed to parse prompt: " + err.message);
            } finally {
                btn.innerHTML = `<svg class="w-3.5 h-3.5 text-[#ec7211]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg><span>AI Auto-Fill Form</span>`;
                btn.disabled = false;
            }
        }

        async function handleAiAnalyzeDirect() {
            const prompt = document.getElementById('ai-prompt-input').value.trim();
            if (!prompt) {
                alert("Please enter a workload description in the prompt box first.");
                return;
            }
            const btn = document.getElementById('btn-ai-analyze');
            btn.innerHTML = `<span>AI Sizing...</span>`;
            btn.disabled = true;

            try {
                const targetReg = document.getElementById('req-region').value || 'us-east-1';
                const res = await fetch('/api/v1/requirements/ai-analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: prompt,
                        target_region: targetReg,
                        auto_save: true
                    })
                });
                const data = await res.json();
                
                if (data.status === 'SUCCESS') {
                    if (data.project_id) currentProjectId = data.project_id;
                    const p = data.parsed_input;
                    if (p) {
                        if (p.project_name) document.getElementById('req-project-name').value = p.project_name;
                        if (p.stream) document.getElementById('req-stream').value = p.stream;
                        if (p.technology) {
                            if (p.technology.frontend) document.getElementById('req-frontend').value = p.technology.frontend;
                            if (p.technology.backend) document.getElementById('req-backend').value = p.technology.backend;
                            if (p.technology.database) document.getElementById('req-database').value = p.technology.database;
                        }
                        if (p.traffic_scale) document.getElementById('req-traffic').value = p.traffic_scale;
                        if (p.reliability) document.getElementById('req-reliability').value = p.reliability;
                        if (p.data_storage_gb) document.getElementById('req-storage').value = p.data_storage_gb;
                        if (p.security_need) document.getElementById('req-security').value = p.security_need;
                        if (p.monthly_budget) document.getElementById('req-budget').value = p.monthly_budget;
                        renderExtractedProfileBadges(p, data.confidence_score, data.engine_used);
                    }
                    const sizingRes = data.data || data.sizing_result || data;
                    renderAnalysisResults(sizingRes);
                    loadSavedProjects();
                }
            } catch (err) {
                alert("AI Sizing failed: " + err.message);
            } finally {
                btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg><span>Identify & Analyze Workload</span>`;
                btn.disabled = false;
            }
        }

        function handleAnalyzeSubmit(e) {
            e.preventDefault();
            triggerAnalyze();
        }

        function renderAnalysisResults(data) {
            const profile = data.profile;
            const rationales = data.service_rationales;
            const optimizations = data.cost_optimizations;

            document.getElementById('out-project-title').textContent = document.getElementById('req-project-name').value;
            document.getElementById('out-tier-badge').textContent = profile.architecture_tier.toUpperCase();
            document.getElementById('out-ha-badge').textContent = profile.high_availability_mode.toUpperCase();
            document.getElementById('out-total-cost').innerHTML = `$${data.total_estimated_cost.toFixed(2)} <span class="text-xs text-muted-custom font-normal">/ mo</span>`;

            const budgetLimit = profile.monthly_budget_limit;
            const budgetStatus = document.getElementById('out-budget-status');
            if (budgetLimit) {
                if (data.total_estimated_cost <= budgetLimit) {
                    budgetStatus.textContent = `Within $${budgetLimit.toFixed(2)} budget limit (Est. $${(budgetLimit - data.total_estimated_cost).toFixed(2)} headroom)`;
                    budgetStatus.className = "text-[10px] text-green-600 dark:text-[#1d8102] font-semibold";
                } else {
                    budgetStatus.textContent = `Exceeds budget of $${budgetLimit.toFixed(2)} by $${(data.total_estimated_cost - budgetLimit).toFixed(2)}/mo`;
                    budgetStatus.className = "text-[10px] text-red-600 dark:text-[#d13212] font-semibold";
                }
            } else {
                budgetStatus.textContent = "Unlimited Budget (Targeting Cost-Optimized Spec)";
                budgetStatus.className = "text-[10px] text-muted-custom font-normal";
            }

            // 1. Render Specs Cards
            const comp = profile.components;
            const specsHtml = `
                <div class="p-3.5 rounded box-subtle space-y-2">
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] font-bold text-[#ec7211] uppercase tracking-wider font-mono">Compute (EC2)</span>
                        <span class="font-mono text-xs font-bold text-title">$${comp.compute.monthly_cost.toFixed(2)}/mo</span>
                    </div>
                    <div class="text-xs font-bold text-title font-mono">${comp.compute.instance_type}</div>
                    <div class="text-[11px] text-muted-custom">${comp.compute.vcpus} vCPUs • ${comp.compute.ram_gb} GB RAM</div>
                    <div class="text-[10px] text-muted-custom">Min: ${comp.compute.min_instances} | Max: ${comp.compute.max_instances} | Target CPU: ${comp.compute.target_cpu_utilization}%</div>
                </div>

                <div class="p-3.5 rounded box-subtle space-y-2">
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] font-bold text-[#0972d3] uppercase tracking-wider font-mono">Database (RDS)</span>
                        <span class="font-mono text-xs font-bold text-title">$${comp.database.monthly_cost.toFixed(2)}/mo</span>
                    </div>
                    <div class="text-xs font-bold text-title font-mono">${comp.database.instance_type}</div>
                    <div class="text-[11px] text-muted-custom">${comp.database.storage_gb} GB ${comp.database.storage_type} • Multi-AZ: ${comp.database.multi_az ? 'Yes' : 'No'}</div>
                    <div class="text-[10px] text-muted-custom">Backups: ${comp.database.backup_retention_days} days PITR recovery</div>
                </div>

                <div class="p-3.5 rounded box-subtle space-y-2">
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] font-bold text-purple-600 uppercase tracking-wider font-mono">Networking (VPC)</span>
                        <span class="font-mono text-xs font-bold text-title">$${comp.networking.monthly_cost.toFixed(2)}/mo</span>
                    </div>
                    <div class="text-xs font-bold text-title">VPC with Public/Private Subnets</div>
                    <div class="text-[11px] text-muted-custom">ALB: ${comp.networking.has_alb ? 'Enabled' : 'None'} • NAT Gateways: ${comp.networking.nat_gateway_count}</div>
                    <div class="text-[10px] text-muted-custom">CloudFront CDN: ${comp.networking.has_cloudfront ? 'Active' : 'Disabled'}</div>
                </div>

                <div class="p-3.5 rounded box-subtle space-y-2">
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] font-bold text-green-600 uppercase tracking-wider font-mono">Storage & Security</span>
                        <span class="font-mono text-xs font-bold text-title">$${comp.storage.monthly_cost.toFixed(2)}/mo</span>
                    </div>
                    <div class="text-xs font-bold text-title">EBS ${comp.storage.ebs_gb_per_instance} GB gp3 + S3 ${comp.storage.s3_gb} GB</div>
                    <div class="text-[11px] text-muted-custom">KMS Encryption: ${comp.security.encryption_enabled ? 'Enforced' : 'Default'}</div>
                    <div class="text-[10px] text-muted-custom">WAF: ${comp.security.waf_enabled ? 'Active' : 'None'} • Compliance: ${profile.compliance_applied.join(', ') || 'Standard'}</div>
                </div>
            `;
            document.getElementById('specs-cards-container').innerHTML = specsHtml;

            // 2. Render Rationales (Why that service)
            let whyHtml = '';
            for (const [svc, rat] of Object.entries(rationales)) {
                whyHtml += `
                    <div class="p-3 rounded box-subtle space-y-1">
                        <div class="flex items-center space-x-2">
                            <span class="h-2 w-2 rounded-full bg-[#ec7211]"></span>
                            <span class="font-mono text-xs font-bold text-title uppercase">${svc}</span>
                        </div>
                        <p class="text-xs text-muted-custom leading-relaxed">${rat}</p>
                    </div>
                `;
            }
            document.getElementById('rationales-container').innerHTML = whyHtml;

            // 3. Render FinOps Optimizations
            let finopsHtml = '';
            optimizations.forEach(opt => {
                finopsHtml += `
                    <div class="p-3 rounded box-subtle flex items-start justify-between gap-3">
                        <div class="space-y-1">
                            <div class="font-bold text-xs text-title">${opt.title}</div>
                            <p class="text-xs text-muted-custom leading-relaxed">${opt.description}</p>
                        </div>
                        <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300 shrink-0">
                            Save $${opt.estimated_monthly_savings_usd}/mo
                        </span>
                    </div>
                `;
            });
            document.getElementById('finops-container').innerHTML = finopsHtml;

            // 4. Render Well-Architected Framework
            if (data.well_architected) {
                const wa = data.well_architected;
                let pillarsHtml = '';
                for (const [pilName, pilData] of Object.entries(wa.pillar_scores || {})) {
                    const sc = pilData.score_percent || 80;
                    pillarsHtml += `
                        <div class="p-2.5 rounded box-subtle space-y-1">
                            <div class="flex justify-between items-center text-xs">
                                <span class="capitalize font-semibold text-title">${pilName.replace('_', ' ')}</span>
                                <span class="font-mono font-bold ${sc >= 85 ? 'text-green-600' : 'text-[#ec7211]'}">${sc}%</span>
                            </div>
                            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 overflow-hidden">
                                <div class="bg-[#ec7211] h-1.5 rounded-full" style="width: ${sc}%"></div>
                            </div>
                            <div class="text-[10px] text-muted-custom truncate">${pilData.summary || ''}</div>
                        </div>
                    `;
                }

                const aiContainerHtml = `
                    <div class="p-4 rounded box-subtle space-y-3">
                        <div class="flex items-center justify-between border-b border-[var(--border-card)] pb-2.5">
                            <div>
                                <span class="text-xs font-bold text-title">Well-Architected Compliance</span>
                                <div class="text-[10px] text-muted-custom">Engine: ${wa.evaluator_engine || 'Autonomous Ruleset'}</div>
                            </div>
                            <div class="text-right font-mono">
                                <span class="text-lg font-extrabold text-green-600">${wa.overall_score_percent}%</span>
                                <div class="text-[10px] text-muted-custom">Overall Compliance</div>
                            </div>
                        </div>
                        <p class="text-xs text-muted-custom leading-relaxed">${wa.synthesis || 'Architectural posture satisfies enterprise resilience benchmarks.'}</p>
                    </div>

                    <div class="text-xs font-bold text-title pt-2">6-Pillar Scorecard</div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        ${pillarsHtml}
                    </div>
                `;
                document.getElementById('ai-advisor-container').innerHTML = aiContainerHtml;
            }
        }

        function switchResultTab(tab) {
            const tabs = ['specs', 'why', 'finops', 'ai', 'finder'];
            tabs.forEach(t => {
                const el = document.getElementById('tab-content-' + t);
                const btn = document.getElementById('tab-btn-' + t);
                if (el) el.classList.add('hidden');
                if (btn) btn.className = 'pb-2.5 tab-inactive flex items-center gap-1.5 cursor-pointer shrink-0';
            });
            const activeEl = document.getElementById('tab-content-' + tab);
            const activeBtn = document.getElementById('tab-btn-' + tab);
            if (activeEl) activeEl.classList.remove('hidden');
            if (activeBtn) activeBtn.className = 'pb-2.5 tab-active flex items-center gap-1.5 cursor-pointer shrink-0';
            if (tab === 'finder') {
                const resultsCont = document.getElementById('finder-results-container');
                if (resultsCont && resultsCont.innerHTML.includes('Adjust requirements above')) {
                    runInstanceFinderEvaluation();
                }
            }
        }

        async function runInstanceFinderEvaluation() {
            const btn = document.getElementById('btn-run-finder');
            const container = document.getElementById('finder-results-container');
            if (!container) return;
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = `<span>Evaluating...</span>`;
            }
            
            const payload = {
                min_vcpus: parseInt(document.getElementById('finder-min-vcpus')?.value) || 2,
                min_ram_gb: parseFloat(document.getElementById('finder-min-ram')?.value) || 4.0,
                target_ratio: parseFloat(document.getElementById('finder-target-ratio')?.value) || 4.0,
                optimization_goal: document.getElementById('finder-opt-goal')?.value || 'balanced',
                target_rps: parseInt(document.getElementById('finder-target-rps')?.value) || 250,
                avg_latency_ms: parseFloat(document.getElementById('finder-avg-lat')?.value) || 120.0,
                architecture_preference: document.getElementById('finder-arch')?.value || 'any',
                service_type: document.getElementById('finder-service')?.value || 'ec2',
                region: document.getElementById('req-region') ? document.getElementById('req-region').value : 'us-east-1',
                top_n: 6
            };

            try {
                const res = await fetch('/api/v1/instance-finder/evaluate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                
                if (data.status === 'EMPTY' || data.status === 'NO_MATCH' || !data.ranked_instances || data.ranked_instances.length === 0) {
                    container.innerHTML = `<div class="p-4 rounded bg-red-50 dark:bg-[#3d1314] border border-red-300 dark:border-red-800 text-red-700 dark:text-red-300 text-xs font-mono">No instance candidates matched your constraints. Try reducing minimum vCPU/RAM or relaxing architecture filters.</div>`;
                    return;
                }

                let html = `
                    <div class="box-subtle p-3.5 rounded-lg flex flex-wrap items-center justify-between gap-3 text-xs">
                        <div class="space-y-0.5">
                            <div class="font-bold text-title flex items-center gap-2">
                                <span>Evaluated ${data.total_candidates_evaluated} Candidate Instances</span>
                                <span class="text-[10px] px-2 py-0.5 rounded bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300 font-mono font-bold">Priority: ${data.optimization_goal.toUpperCase()}</span>
                            </div>
                            <div class="text-[11px] text-muted-custom font-mono">
                                Target Traffic: <span class="text-[#ec7211] font-bold">~${data.workload_demand_concurrency} concurrent requests</span> • Ideal Ratio: <span class="text-title">${data.mathematical_summary.target_ratio}:1</span>
                            </div>
                        </div>
                        <div class="text-[10px] text-muted-custom font-mono">
                            Region: ${data.region.toUpperCase()} • Service: ${data.service_type.toUpperCase()}
                        </div>
                    </div>
                    <div class="space-y-3">
                `;

                data.ranked_instances.forEach(inst => {
                    const isTop = inst.rank === 1;
                    const borderCol = isTop ? 'border-[#ec7211]' : 'border-[var(--border-card)]';
                    const badgeBg = isTop ? 'bg-[#ec7211]/15 text-[#ea580c] dark:text-[#ff9900] border-[#ec7211]/40' : 'bg-gray-100 dark:bg-[#232f3e] text-muted-custom border-[var(--border-subtle)]';
                    const slaPercent = (inst.sla_probability * 100).toFixed(1);
                    const slaColor = inst.sla_probability >= 0.95 ? 'text-green-600 dark:text-green-400' : (inst.sla_probability >= 0.8 ? 'text-[#ec7211]' : 'text-red-500');
                    const matchPercent = Math.min(99.9, inst.composite_score).toFixed(0);
                    
                    html += `
                        <div class="aws-card p-4 rounded-lg border ${borderCol} hover:border-[#ec7211]/60 transition space-y-3">
                            <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                                <div class="flex items-center space-x-2">
                                    <span class="px-2.5 py-0.5 rounded text-[11px] font-mono font-extrabold ${badgeBg} border">
                                        #${inst.rank} ${inst.fit_label}
                                    </span>
                                    <span class="text-sm font-bold text-title font-mono">${inst.instance_type}</span>
                                    <span class="text-[10px] px-2 py-0.5 rounded box-subtle text-muted-custom font-mono">${inst.architecture}</span>
                                </div>
                                <div class="text-right">
                                    <span class="text-base font-extrabold text-title font-mono">$${inst.price_per_hour.toFixed(4)}/hr</span>
                                    <span class="text-[11px] text-muted-custom font-mono ml-1.5">($${inst.monthly_price.toFixed(2)}/mo)</span>
                                </div>
                            </div>
                            
                            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs pt-1 border-t border-[var(--border-card)]">
                                <div class="box-subtle p-2.5 rounded">
                                    <div class="text-[10px] text-muted-custom">Compute & Memory</div>
                                    <div class="text-title font-mono font-bold">${inst.vcpus} vCPU • ${inst.ram_gb} GB</div>
                                    <div class="text-[10px] text-muted-custom font-mono">Ratio: ${inst.ratio}:1</div>
                                </div>
                                <div class="box-subtle p-2.5 rounded">
                                    <div class="text-[10px] text-muted-custom">Workload Match</div>
                                    <div class="text-[#ec7211] font-mono font-bold text-sm">${matchPercent}% Fit</div>
                                    <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1 mt-1">
                                        <div class="bg-[#ec7211] h-1 rounded-full" style="width: ${matchPercent}%"></div>
                                    </div>
                                </div>
                                <div class="box-subtle p-2.5 rounded">
                                    <div class="text-[10px] text-muted-custom">Traffic Burst Safety</div>
                                    <div class="${slaColor} font-mono font-bold text-sm">${slaPercent}% Safe</div>
                                    <div class="text-[10px] text-muted-custom font-mono">Zero saturation headroom</div>
                                </div>
                                <div class="box-subtle p-2.5 rounded">
                                    <div class="text-[10px] text-muted-custom">Network Bandwidth</div>
                                    <div class="text-title font-mono font-bold">${inst.network_performance}</div>
                                    <div class="text-[10px] text-muted-custom font-mono">EBS-Optimized</div>
                                </div>
                            </div>

                            <div class="text-xs text-muted-custom box-subtle p-2.5 rounded flex items-start gap-2">
                                <svg class="w-4 h-4 text-[#ec7211] shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                                <span>${inst.decision_rationale}</span>
                            </div>

                            <details class="text-[10px] text-muted-custom font-mono">
                                <summary class="cursor-pointer hover:text-title">▸ View Advanced Technical Metrics</summary>
                                <div class="mt-1.5 p-2 rounded box-subtle text-[10px] space-y-0.5">
                                    <div>TOPSIS Relative Closeness: <strong class="text-title">${inst.topsis_score.toFixed(4)}</strong></div>
                                    <div>Probabilistic SLA Confidence (erf): <strong class="text-title">${inst.sla_probability.toFixed(4)}</strong></div>
                                    <div>Target Ratio Divergence: <strong class="text-title">${inst.ratio_divergence}</strong></div>
                                </div>
                            </details>
                        </div>
                    `;
                });

                html += `</div>`;
                container.innerHTML = html;

            } catch (err) {
                container.innerHTML = `<div class="p-4 rounded bg-red-50 dark:bg-[#3d1314] border border-red-300 dark:border-red-800 text-red-700 dark:text-red-300 text-xs font-mono">Error evaluating instance recommendations: ${err.message}</div>`;
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = `<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg><span>Find Best Matching Instances</span>`;
                }
            }
        }

        async function dispatchToModule2() {
            if (!currentProjectId) {
                const payload = getFormData();
                const res = await fetch('/api/v1/requirements', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const json = await res.json();
                currentProjectId = json.project.id;
            }

            const btn = document.getElementById('btn-dispatch');
            btn.innerHTML = `<span>Dispatching to :8002...</span>`;
            btn.disabled = true;

            try {
                const res = await fetch(`/api/v1/requirements/${currentProjectId}/dispatch`, {
                    method: 'POST'
                });
                const json = await res.json();
                if (json.status === 'DISPATCHED_SUCCESSFULLY') {
                    showDispatchModal(json);
                    loadSavedProjects();
                } else {
                    alert("Module 2 Dispatch error: " + (json.detail || "Unknown error"));
                }
            } catch (err) {
                alert("Could not reach Module 2 on :8002: " + err.message);
            } finally {
                btn.innerHTML = `<span>Dispatch to Module 2</span><svg class="w-3.5 h-3.5 text-[#ec7211]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>`;
                btn.disabled = false;
            }
        }

        function showDispatchModal(data) {
            const modal = document.createElement('div');
            modal.className = "fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4";
            modal.innerHTML = `
                <div class="aws-card max-w-lg w-full p-6 space-y-4">
                    <div class="flex items-center space-x-2 text-green-600">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        <h3 class="text-base font-bold text-title">Dispatched to Module 2 Successfully</h3>
                    </div>
                    <p class="text-xs text-muted-custom">
                        The workload profile was delivered to the Module 2 Architecture Generator engine on port 8002 in ${data.dispatch_duration_ms}ms.
                    </p>
                    <div class="box-subtle p-3 rounded text-xs space-y-1 font-mono text-muted-custom">
                        <div>Graph Nodes Created: <strong class="text-title">${data.graph_nodes}</strong></div>
                        <div>Graph Edges Created: <strong class="text-title">${data.graph_edges}</strong></div>
                        <div>Target Module: <strong class="text-[#ec7211]">${data.target_module}</strong></div>
                    </div>
                    <div class="flex justify-end pt-2">
                        <button onclick="this.closest('.fixed').remove()" class="aws-btn-primary px-4 py-2 rounded text-xs font-bold cursor-pointer">
                            Close
                        </button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }

        async function saveCurrentProject() {
            const payload = getFormData();
            try {
                const res = await fetch('/api/v1/requirements', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const json = await res.json();
                if (json.status === 'CREATED' || json.status === 'SUCCESS') {
                    currentProjectId = json.project.id;
                    alert(`Project '${payload.project_name}' saved to requirements.db!`);
                    loadSavedProjects();
                }
            } catch (err) {
                alert("Failed to save project: " + err.message);
            }
        }

        async function loadSavedProjects() {
            try {
                const res = await fetch('/api/v1/requirements');
                const json = await res.json();
                const tbody = document.getElementById('saved-projects-tbody');
                tbody.innerHTML = '';

                if (!json.projects || json.projects.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="7" class="py-4 text-center text-muted-custom">No projects saved yet. Enter requirements and click Save.</td></tr>`;
                    return;
                }

                json.projects.forEach(p => {
                    const isDispatched = p.dispatched_to_m2 || p.status === 'DISPATCHED_TO_M2';
                    tbody.innerHTML += `
                        <tr class="hover:bg-gray-50 dark:hover:bg-[#232f3e]/40 transition">
                            <td class="py-2.5 px-3 font-bold font-mono text-title">${p.project_name}</td>
                            <td class="py-2.5 px-3 font-mono text-muted-custom">${p.target_region}</td>
                            <td class="py-2.5 px-3 capitalize text-muted-custom">${p.stream.replace('_', ' ')}</td>
                            <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300">${p.architecture_tier || 'STANDARD'}</span></td>
                            <td class="py-2.5 px-3 text-right font-mono font-bold text-title">$${(p.estimated_monthly_cost || 0).toFixed(2)}</td>
                            <td class="py-2.5 px-3 text-center">
                                <span class="px-2 py-0.5 rounded text-[9px] font-mono ${isDispatched ? 'bg-orange-100 dark:bg-[#232f3e] text-[#ea580c] dark:text-[#ff9900] border border-[#ec7211]/40' : 'bg-gray-100 dark:bg-gray-800 text-muted-custom'}">
                                    ${p.status}
                                </span>
                            </td>
                            <td class="py-2.5 px-3 text-right space-x-2">
                                <button onclick="loadProjectIntoForm('${p.id}')" class="text-xs text-[#0972d3] hover:underline font-semibold cursor-pointer">Restore</button>
                                <button onclick="deleteProject('${p.id}')" class="text-xs text-red-600 hover:underline font-semibold cursor-pointer">Delete</button>
                            </td>
                        </tr>
                    `;
                });
            } catch (err) {
                console.error("Failed to load saved projects:", err);
            }
        }

        async function loadProjectIntoForm(id) {
            try {
                const res = await fetch(`/api/v1/requirements/${id}`);
                const p = await res.json();
                if (p) {
                    currentProjectId = p.id;
                    document.getElementById('req-project-name').value = p.project_name;
                    document.getElementById('req-stream').value = p.stream;
                    document.getElementById('req-region').value = p.target_region;
                    if (p.tech_stack) {
                        if (p.tech_stack.frontend) document.getElementById('req-frontend').value = p.tech_stack.frontend;
                        if (p.tech_stack.backend) document.getElementById('req-backend').value = p.tech_stack.backend;
                        if (p.tech_stack.database) document.getElementById('req-database').value = p.tech_stack.database;
                    }
                    document.getElementById('req-traffic').value = p.traffic_scale;
                    document.getElementById('req-reliability').value = p.reliability;
                    document.getElementById('req-storage').value = p.data_storage_gb;
                    document.getElementById('req-security').value = p.security_need;
                    document.getElementById('req-budget').value = p.monthly_budget || '';
                    if (p.operations && p.operations.container_orchestration) {
                        document.getElementById('req-orchestration').value = p.operations.container_orchestration;
                    }
                    if (p.monitoring && p.monitoring.level) {
                        document.getElementById('req-monitoring').value = p.monitoring.level;
                    }

                    const simulatedResult = {
                        profile: p.profile_output,
                        service_rationales: p.service_rationales,
                        cost_optimizations: p.cost_optimizations,
                        cost_breakdown: p.cost_breakdown,
                        architecture_tier: p.architecture_tier,
                        total_estimated_cost: p.estimated_monthly_cost
                    };
                    renderAnalysisResults(simulatedResult);
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                }
            } catch (err) {
                alert("Failed to load project: " + err.message);
            }
        }

        async function deleteProject(id) {
            if (!confirm("Are you sure you want to delete this requirement project?")) return;
            try {
                const res = await fetch(`/api/v1/requirements/${id}`, { method: 'DELETE' });
                const json = await res.json();
                if (json.status === 'DELETED') {
                    loadSavedProjects();
                }
            } catch (err) {
                alert("Delete failed: " + err.message);
            }
        }

        // Initialize on load
        window.addEventListener('DOMContentLoaded', () => {
            triggerAnalyze();
            loadSavedProjects();
        });
    </script>
</body>
</html>
"""
