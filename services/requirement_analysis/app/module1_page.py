# services/requirement_analysis/app/module1_page.py

def get_module1_page_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AetherOps Cloud - Module 1: Requirement Analysis & Sizing</title>
    <link rel="stylesheet" href="/static/fonts/fonts.css">
    <script src="/static/js/tailwind.js"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Plus Jakarta Sans', 'Segoe UI', -apple-system, BlinkMacSystemFont, 'sans-serif'],
                        mono: ['JetBrains Mono', 'Consolas', 'monospace']
                    },
                    colors: {
                        aws: {
                            squid: '#161e2e',
                            squidDark: '#0f141c',
                            navy: '#232f3e',
                            navyHover: '#2a384c',
                            orange: '#ec7211',
                            orangeHover: '#eb5f07',
                            orangeLight: '#ff9900',
                            blue: '#0972d3',
                            blueHover: '#033ebc',
                            card: '#1b2533',
                            border: '#2d3748',
                            borderLight: '#39465a',
                            textMuted: '#9ba7b6',
                            green: '#1d8102',
                            red: '#d13212'
                        }
                    }
                }
            }
        }
    </script>
    <style>
        body { background-color: #0f141c; color: #eaeded; }
        .aws-card { background-color: #1b2533; border: 1px solid #2d3748; }
        .aws-btn-primary { background-color: #ec7211; color: #ffffff; font-weight: 700; transition: all 0.15s ease-in-out; }
        .aws-btn-primary:hover { background-color: #eb5f07; }
        .aws-btn-secondary { background-color: #232f3e; border: 1px solid #414d5c; color: #ffffff; transition: all 0.15s ease-in-out; }
        .aws-btn-secondary:hover { background-color: #2a384c; border-color: #ec7211; }
        .aws-input { background-color: #0f141c; border: 1px solid #3b444b; color: #ffffff; transition: border-color 0.15s; }
        .aws-input:focus { border-color: #ec7211; outline: none; box-shadow: 0 0 0 1px #ec7211; }
        .tab-active { border-bottom: 2px solid #ec7211; color: #ffffff; font-weight: 700; }
        .tab-inactive { color: #9ba7b6; }
        .tab-inactive:hover { color: #ffffff; }
    </style>
</head>
<body class="min-h-screen flex flex-col font-sans selection:bg-[#ec7211]/30 selection:text-[#ff9900]">

    <!-- Top AWS Console Header -->
    <header class="bg-[#161e2e] border-b border-[#2d3748] px-4 sm:px-6 py-2.5 flex items-center justify-between sticky top-0 z-40 shadow-sm">
        
        <!-- Left: AetherOps Branding & Breadcrumb -->
        <div class="flex items-center space-x-3">
            <div class="flex items-center space-x-2">
                <span class="font-extrabold text-white text-base tracking-tight">AetherOps</span>
                <span class="text-[#ff9900] text-[10px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-[#232f3e] border border-[#ff9900]/40 font-mono">MODULE 1</span>
                <span class="text-gray-500 hidden sm:inline">/</span>
                <span class="text-xs font-bold text-gray-300 font-mono hidden sm:inline">REQUIREMENT ANALYSIS & SIZING</span>
            </div>
        </div>

        <!-- Center: Telemetry Status Badges -->
        <div class="hidden lg:flex items-center space-x-2 text-xs">
            <span class="px-2 py-0.5 rounded bg-[#0f141c] border border-[#2d3748] flex items-center gap-1.5 text-gray-300 font-mono text-[11px]">
                <span class="h-2 w-2 rounded-full bg-[#1d8102]"></span>
                <span>SQLite (requirements.db)</span>
            </span>
            <span class="px-2 py-0.5 rounded bg-[#0f141c] border border-[#2d3748] flex items-center gap-1.5 text-gray-300 font-mono text-[11px]">
                <span class="h-2 w-2 rounded-full bg-[#1d8102]"></span>
                <span>Redis L1 Cache</span>
            </span>
            <span class="px-2 py-0.5 rounded bg-[#0f141c] border border-[#2d3748] flex items-center gap-1.5 text-[#ff9900] font-mono text-[11px]">
                <span class="h-2 w-2 rounded-full bg-[#ec7211] animate-pulse"></span>
                <span>Port :8001</span>
            </span>
        </div>

        <!-- Right: Actions & Links -->
        <div class="flex items-center space-x-3 text-xs">
            <a href="/admin" class="aws-btn-secondary px-3 py-1.5 rounded flex items-center gap-1.5 cursor-pointer text-xs font-semibold">
                <svg class="w-3.5 h-3.5 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                <span>AWS Catalog & Admin</span>
            </a>
        </div>

    </header>

    <!-- Main Workspace -->
    <main class="flex-1 p-4 sm:p-6 space-y-6 max-w-7xl mx-auto w-full">
        
        <!-- Hero Microservice Banner -->
        <div class="aws-card p-5 border-l-4 border-l-[#ec7211] flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
                <div class="flex items-center space-x-2">
                    <span class="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-[#ec7211]/20 text-[#ff9900] border border-[#ec7211]/40 font-mono">MICROSERVICE 1 / 8</span>
                    <span class="text-xs text-gray-400 font-mono">• Autonomous Workload Profiler</span>
                </div>
                <h1 class="text-xl font-bold text-white mt-1.5">Intelligent AWS Architecture Sizing & Cost Optimization Engine</h1>
                <p class="text-xs text-[#9ba7b6] mt-1 max-w-3xl">
                    Configure your high-level system requirements below. The engine calculates precise compute, database, networking, and security topologies, provides technical justification ("Why that service"), and identifies immediate FinOps cost optimizations.
                </p>
            </div>
            <div class="flex flex-col sm:flex-row gap-2 shrink-0">
                <button onclick="fillSamplePreset('fintech')" class="px-3 py-1.5 rounded bg-[#232f3e] hover:bg-[#2a384c] border border-[#414d5c] text-xs text-gray-200 transition font-medium">
                    Load FinTech Preset
                </button>
                <button onclick="fillSamplePreset('saas')" class="px-3 py-1.5 rounded bg-[#232f3e] hover:bg-[#2a384c] border border-[#414d5c] text-xs text-gray-200 transition font-medium">
                    Load SaaS Starter
                </button>
            </div>
        </div>

        <!-- Two-Column Primary Layout -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            
            <!-- LEFT COLUMN: Requirements Intake Form (5 Cols) -->
            <div class="lg:col-span-5 space-y-5">
                
                <!-- AI Natural Language Prompt Card -->
                <div class="aws-card p-5 space-y-3.5 border-t-2 border-t-[#ec7211]">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <span class="text-xs font-bold text-white flex items-center gap-1.5">
                                <svg class="w-4 h-4 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                                AI Natural Language Requirement Intake
                            </span>
                        </div>
                        <span class="text-[10px] font-mono text-[#ff9900] px-2 py-0.5 rounded bg-[#ec7211]/20 border border-[#ec7211]/30">Zero Hallucination</span>
                    </div>
                    <p class="text-[11px] text-[#9ba7b6]">
                        Describe your workload in plain English. The AI parser extracts technical parameters, sizes infrastructure against regional SQLite databases & Redis, and computes FinOps savings.
                    </p>
                    <textarea id="ai-prompt-input" rows="3" placeholder="e.g. Deploy a high-throughput healthcare API using Python FastAPI and PostgreSQL. Requires HIPAA compliance, multi-AZ HA, 50 GB storage, and budget under $300/mo."
                        class="aws-input w-full p-2.5 rounded text-xs leading-relaxed resize-none"></textarea>
                    
                    <!-- Quick Prompt Scenario Chips -->
                    <div class="space-y-1.5">
                        <div class="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Quick Scenarios:</div>
                        <div class="flex flex-wrap gap-1.5 text-[10px]">
                            <button type="button" onclick="setPromptAndAnalyze('Fintech payment engine on FastAPI and PostgreSQL, PCI-DSS compliance, multi-AZ HA, 300 RPS, budget under $450/mo.')" 
                                class="px-2 py-1 rounded bg-[#0f141c] hover:bg-[#232f3e] border border-[#2d3748] text-gray-300 font-mono transition">
                                🏦 Fintech PCI-DSS
                            </button>
                            <button type="button" onclick="setPromptAndAnalyze('Enterprise healthcare portal with Python FastAPI and PostgreSQL, HIPAA security, multi-AZ, 100 GB storage under $500/mo.')" 
                                class="px-2 py-1 rounded bg-[#0f141c] hover:bg-[#232f3e] border border-[#2d3748] text-gray-300 font-mono transition">
                                🏥 Healthcare HIPAA
                            </button>
                            <button type="button" onclick="setPromptAndAnalyze('AI machine learning inference pipeline on FastAPI with EKS, high traffic 500 RPS, CloudFront CDN, budget $600.')" 
                                class="px-2 py-1 rounded bg-[#0f141c] hover:bg-[#232f3e] border border-[#2d3748] text-gray-300 font-mono transition">
                                🤖 AI/ML Inference
                            </button>
                            <button type="button" onclick="setPromptAndAnalyze('Lightweight internal dev sandbox for testing prototypes on React and Node.js, single-AZ, budget under $40.')" 
                                class="px-2 py-1 rounded bg-[#0f141c] hover:bg-[#232f3e] border border-[#2d3748] text-gray-300 font-mono transition">
                                🧪 Dev Sandbox &lt;$40
                            </button>
                        </div>
                    </div>

                    <div class="flex gap-2 pt-1">
                        <button type="button" id="btn-ai-autofill" onclick="handleAiAutoFill()" class="flex-1 aws-btn-secondary py-2 rounded text-xs font-semibold flex items-center justify-center gap-1.5">
                            <svg class="w-3.5 h-3.5 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                            <span>AI Auto-Fill Form</span>
                        </button>
                        <button type="button" id="btn-ai-analyze" onclick="handleAiAnalyzeDirect()" class="flex-1 aws-btn-primary py-2 rounded text-xs font-bold flex items-center justify-center gap-1.5 shadow-sm">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                            <span>AI Sizing & Analysis</span>
                        </button>
                    </div>
                </div>

                <div class="aws-card p-5 space-y-4">
                    
                    <div class="border-b border-[#2d3748] pb-3 flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <span class="h-2.5 w-2.5 rounded-full bg-[#ec7211]"></span>
                            <h2 class="text-sm font-bold text-white uppercase tracking-wider">Workload Parameters</h2>
                        </div>
                        <span class="text-[10px] text-gray-400 font-mono">SQLite Input</span>
                    </div>

                    <form id="requirements-form" onsubmit="handleAnalyzeSubmit(event)" class="space-y-4 text-xs">
                        
                        <!-- Project Identity -->
                        <div class="space-y-3">
                            <div>
                                <label class="block text-[#9ba7b6] font-semibold mb-1">Project Name</label>
                                <input type="text" id="req-project-name" required placeholder="e.g., payment-gateway-core" value="fintech-payment-engine"
                                    class="aws-input w-full p-2 rounded text-xs font-mono">
                            </div>
                            
                            <div class="grid grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-[#9ba7b6] font-semibold mb-1">Cloud Stream</label>
                                    <select id="req-stream" class="aws-input w-full p-2 rounded text-xs">
                                        <option value="web_application" selected>Web Application</option>
                                        <option value="ai_ml">AI / Machine Learning</option>
                                        <option value="iot">IoT Ingestion Hub</option>
                                        <option value="devops_tooling">DevOps Tooling / CI</option>
                                        <option value="dev_sandbox">Developer Sandbox</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-[#9ba7b6] font-semibold mb-1">Target Region</label>
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

                        <!-- Technology Stack -->
                        <div class="pt-2 border-t border-[#2d3748]">
                            <div class="text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider mb-2">Software Stack</div>
                            <div class="grid grid-cols-3 gap-2">
                                <div>
                                    <label class="block text-[10px] text-gray-400 mb-1">Frontend</label>
                                    <select id="req-frontend" class="aws-input w-full p-1.5 rounded text-[11px]">
                                        <option value="react_vue_angular" selected>React / Vue</option>
                                        <option value="simple_html_css">HTML / CSS</option>
                                        <option value="none">None (API only)</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-[10px] text-gray-400 mb-1">Backend</label>
                                    <select id="req-backend" class="aws-input w-full p-1.5 rounded text-[11px]">
                                        <option value="python_fastapi_django" selected>Python / FastAPI</option>
                                        <option value="nodejs_express">Node.js Express</option>
                                        <option value="java_spring">Java Spring</option>
                                        <option value="none">None</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-[10px] text-gray-400 mb-1">Database</label>
                                    <select id="req-database" class="aws-input w-full p-1.5 rounded text-[11px]">
                                        <option value="postgresql" selected>PostgreSQL</option>
                                        <option value="mysql">MySQL</option>
                                        <option value="none">None</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <!-- Traffic & Reliability -->
                        <div class="pt-2 border-t border-[#2d3748]">
                            <div class="text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider mb-2">Scale & Reliability</div>
                            <div class="grid grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-[10px] text-gray-400 mb-1">Traffic Scale</label>
                                    <select id="req-traffic" class="aws-input w-full p-2 rounded text-xs">
                                        <option value="hobby_dev">Hobby / Dev (1 RPS)</option>
                                        <option value="growth" selected>Growth (30-45 RPS)</option>
                                        <option value="production">Production (200-400 RPS)</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-[10px] text-gray-400 mb-1">Reliability Tier</label>
                                    <select id="req-reliability" class="aws-input w-full p-2 rounded text-xs">
                                        <option value="dev_testing">Dev/Test (95% SLA)</option>
                                        <option value="production_safe" selected>Prod-Safe (Multi-AZ 99.9%)</option>
                                        <option value="mission_critical">Mission-Critical (99.99%)</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <!-- Storage, Security & Budget -->
                        <div class="pt-2 border-t border-[#2d3748]">
                            <div class="text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider mb-2">Governance & Budget</div>
                            <div class="grid grid-cols-3 gap-2">
                                <div>
                                    <label class="block text-[10px] text-gray-400 mb-1">Storage (GB)</label>
                                    <input type="number" id="req-storage" min="0" value="80" class="aws-input w-full p-1.5 rounded text-xs font-mono">
                                </div>
                                <div>
                                    <label class="block text-[10px] text-gray-400 mb-1">Compliance</label>
                                    <select id="req-security" class="aws-input w-full p-1.5 rounded text-[11px]">
                                        <option value="standard">Standard</option>
                                        <option value="payment_processing" selected>PCI-DSS / Finance</option>
                                        <option value="healthcare">HIPAA Healthcare</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-[10px] text-gray-400 mb-1">Max Budget ($/mo)</label>
                                    <input type="number" id="req-budget" min="0" placeholder="Optional" value="600" class="aws-input w-full p-1.5 rounded text-xs font-mono">
                                </div>
                            </div>
                        </div>

                        <!-- DevOps / Orchestration Preferences -->
                        <div class="pt-2 border-t border-[#2d3748]">
                            <div class="text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider mb-2">DevOps Tooling</div>
                            <div class="grid grid-cols-2 gap-3">
                                <div>
                                    <label class="block text-[10px] text-gray-400 mb-1">Orchestration</label>
                                    <select id="req-orchestration" class="aws-input w-full p-2 rounded text-xs">
                                        <option value="kubernetes" selected>Kubernetes (K8s / EKS)</option>
                                        <option value="ecs_fargate">AWS ECS Fargate</option>
                                        <option value="docker_compose">Docker Compose</option>
                                        <option value="none">None (VM Bare)</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-[10px] text-gray-400 mb-1">Monitoring</label>
                                    <select id="req-monitoring" class="aws-input w-full p-2 rounded text-xs">
                                        <option value="advanced" selected>Advanced (CloudWatch + Slack)</option>
                                        <option value="basic">Basic (Email Alerting)</option>
                                        <option value="none">None</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <!-- Submit CTA Buttons -->
                        <div class="pt-3 flex items-center gap-3">
                            <button type="submit" id="btn-analyze" class="aws-btn-primary flex-1 py-2.5 px-4 rounded text-xs font-bold shadow flex items-center justify-center gap-2 cursor-pointer">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                                <span>Analyze & Size Workload</span>
                            </button>
                            <button type="button" onclick="saveCurrentProject()" class="aws-btn-secondary py-2.5 px-4 rounded text-xs font-bold flex items-center gap-1.5 cursor-pointer">
                                <svg class="w-4 h-4 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/></svg>
                                <span>Save</span>
                            </button>
                        </div>

                    </form>
                </div>
            </div>

            <!-- RIGHT COLUMN: Sizing Breakdown & Rationales (7 Cols) -->
            <div class="lg:col-span-7 space-y-5">
                
                <!-- Sizing Output Card -->
                <div class="aws-card p-5 space-y-4" id="results-card">
                    
                    <!-- Sizing Header Summary Bar -->
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-3 border-b border-[#2d3748]">
                        <div>
                            <div class="flex items-center space-x-2">
                                <span id="out-tier-badge" class="px-2.5 py-0.5 rounded text-[10px] font-extrabold uppercase bg-[#1d8102]/20 text-[#1d8102] border border-[#1d8102]/40 font-mono">
                                    PRODUCTION-STANDARD
                                </span>
                                <span id="out-ha-badge" class="px-2 py-0.5 rounded text-[10px] font-mono text-gray-300 bg-[#0f141c] border border-[#2d3748]">
                                    Multi-AZ
                                </span>
                            </div>
                            <h2 class="text-base font-bold text-white mt-1" id="out-project-title">fintech-payment-engine</h2>
                        </div>
                        <div class="text-right">
                            <div class="text-xs text-[#9ba7b6]">Estimated Monthly Spend</div>
                            <div class="text-xl font-extrabold text-white font-mono" id="out-total-cost">$148.20 <span class="text-xs text-[#9ba7b6] font-normal">/ mo</span></div>
                            <div class="text-[10px] text-[#1d8102] font-semibold" id="out-budget-status">Within $600.00 Budget Limit</div>
                        </div>
                    </div>

                    <!-- Output Navigation Tabs -->
                    <div class="flex items-center space-x-4 border-b border-[#2d3748] text-xs font-semibold">
                        <button onclick="switchResultTab('specs')" id="tab-btn-specs" class="pb-2.5 tab-active flex items-center gap-1.5 cursor-pointer">
                            <svg class="w-3.5 h-3.5 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                            <span>Services & Sizing</span>
                        </button>
                        <button onclick="switchResultTab('why')" id="tab-btn-why" class="pb-2.5 tab-inactive flex items-center gap-1.5 cursor-pointer">
                            <svg class="w-3.5 h-3.5 text-[#539fe5]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></svg>
                            <span>Why These Services?</span>
                        </button>
                        <button onclick="switchResultTab('finops')" id="tab-btn-finops" class="pb-2.5 tab-inactive flex items-center gap-1.5 cursor-pointer">
                            <svg class="w-3.5 h-3.5 text-[#a87ffb]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                            <span>Cost Optimization (FinOps)</span>
                        </button>
                        <button onclick="switchResultTab('ai')" id="tab-btn-ai" class="pb-2.5 tab-inactive flex items-center gap-1.5 cursor-pointer">
                            <svg class="w-3.5 h-3.5 text-[#1d8102]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                            <span>AI Well-Architected Advisor</span>
                        </button>
                    </div>

                    <!-- TAB 1: Sizing Specifications Cards -->
                    <div id="tab-content-specs" class="space-y-3">
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3" id="specs-cards-container">
                            <!-- Populated dynamically via JavaScript -->
                        </div>
                    </div>

                    <!-- TAB 2: Why These Services? (Detailed Technical Rationales) -->
                    <div id="tab-content-why" class="space-y-3 hidden">
                        <div class="text-[11px] text-[#9ba7b6] italic mb-2">
                            Architectural justification and design rationale mapped directly to your workload requirements:
                        </div>
                        <div class="space-y-3" id="rationales-container">
                            <!-- Populated dynamically via JavaScript -->
                        </div>
                    </div>

                    <!-- TAB 3: FinOps Cost Optimization Opportunities -->
                    <div id="tab-content-finops" class="space-y-3 hidden">
                        <div class="text-[11px] text-[#9ba7b6] mb-2">
                            High-impact cost reduction opportunities identified for this workload:
                        </div>
                        <div class="space-y-3" id="finops-container">
                            <!-- Populated dynamically via JavaScript -->
                        </div>
                    </div>

                    <!-- TAB 4: AI Well-Architected Advisor -->
                    <div id="tab-content-ai" class="space-y-3 hidden">
                        <div class="text-[11px] text-[#9ba7b6] mb-2">
                            AWS Well-Architected Framework 6-Pillar Evaluation & Grounded Synthesis:
                        </div>
                        <div class="space-y-3" id="ai-advisor-container">
                            <!-- Populated dynamically via JavaScript -->
                        </div>
                    </div>


                    <!-- Module 2 Dispatch Strip -->
                    <div class="pt-4 border-t border-[#2d3748] flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#0f141c] p-3 rounded">
                        <div>
                            <div class="text-xs font-bold text-white flex items-center gap-1.5">
                                <span>Next Pipeline Step: Module 2</span>
                                <span class="px-1.5 py-0.2 rounded text-[9px] font-mono bg-[#232f3e] text-[#ff9900]">Architecture Diagram</span>
                            </div>
                            <p class="text-[11px] text-[#9ba7b6]">Forward this compiled profile to the Visual Graph Builder on port :8002.</p>
                        </div>
                        <button onclick="dispatchToModule2()" id="btn-dispatch" class="aws-btn-secondary py-2 px-3.5 rounded text-xs font-bold flex items-center gap-1.5 shrink-0 cursor-pointer">
                            <span>Dispatch to Module 2</span>
                            <svg class="w-3.5 h-3.5 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                        </button>
                    </div>

                </div>

            </div>

        </div>

        <!-- BOTTOM SECTION: Saved Projects in SQLite -->
        <div class="aws-card p-5 space-y-4">
            <div class="flex items-center justify-between border-b border-[#2d3748] pb-3">
                <div class="flex items-center space-x-2">
                    <span class="h-2.5 w-2.5 rounded-full bg-[#1d8102]"></span>
                    <h3 class="text-sm font-bold text-white uppercase tracking-wider">Persisted Requirement Projects</h3>
                    <span class="text-[10px] px-2 py-0.5 rounded bg-[#0f141c] text-gray-400 font-mono border border-[#2d3748]" id="saved-count">2 Saved</span>
                </div>
                <button onclick="loadSavedProjects()" class="text-xs text-gray-400 hover:text-white flex items-center gap-1 cursor-pointer">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                    <span>Refresh</span>
                </button>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse">
                    <thead>
                        <tr class="border-b border-[#2d3748] bg-[#161e2e] text-[10px] font-bold text-[#9ba7b6] uppercase tracking-wider">
                            <th class="p-3">Project</th>
                            <th class="p-3">Stream / Region</th>
                            <th class="p-3">Architecture Tier</th>
                            <th class="p-3 text-right">Est. Cost</th>
                            <th class="p-3 text-center">Status</th>
                            <th class="p-3 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-[#263244] bg-[#1b2533]" id="saved-projects-tbody">
                        <!-- Populated dynamically via JavaScript -->
                    </tbody>
                </table>
            </div>
        </div>

    </main>

    <!-- Footer -->
    <footer class="mt-auto border-t border-[#2d3748] bg-[#161e2e] py-3.5 px-6 text-xs text-[#9ba7b6] flex flex-col sm:flex-row justify-between items-center gap-2">
        <div class="flex items-center space-x-2">
            <span class="font-semibold text-gray-300">&copy; 2026 AetherOps Cloud</span>
            <span class="text-gray-600">•</span>
            <span>Module 1: Requirement Analysis Microservice</span>
        </div>
        <div class="flex items-center space-x-2 font-mono text-[11px] text-[#9ba7b6]">
            <span class="inline-block w-2 h-2 rounded-full bg-[#1d8102]"></span>
            <span>Architecture: Distributed Microservices • Orchestrated by Kubernetes (K8s)</span>
        </div>
    </footer>

    <!-- DISPATCH MODAL -->
    <div id="dispatch-modal" class="fixed inset-0 bg-black/75 z-50 hidden flex items-center justify-center p-4">
        <div class="aws-card w-full max-w-lg p-5 space-y-4 rounded-lg bg-[#1b2533] shadow-2xl">
            <div class="flex justify-between items-center pb-2 border-b border-[#2d3748]">
                <h3 class="text-sm font-bold text-white flex items-center gap-2">
                    <span class="h-2.5 w-2.5 rounded-full bg-[#1d8102]"></span>
                    <span>Dispatched to Module 2 (Architecture Generator)</span>
                </h3>
                <button onclick="closeDispatchModal()" class="text-gray-400 hover:text-white">&times;</button>
            </div>
            <div class="space-y-3 text-xs" id="dispatch-modal-content">
                <!-- Populated dynamically -->
            </div>
            <div class="pt-2 flex justify-end">
                <button onclick="closeDispatchModal()" class="aws-btn-secondary px-4 py-1.5 rounded text-xs">Close</button>
            </div>
        </div>
    </div>

    <script>
        let currentAnalysisData = null;
        let currentProjectId = null;

        const presets = {
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
                monitoring: "advanced"
            },
            saas: {
                project_name: "cloud-saas-starter",
                stream: "web_application",
                region: "us-east-1",
                frontend: "simple_html_css",
                backend: "nodejs_express",
                database: "postgresql",
                traffic: "hobby_dev",
                reliability: "dev_testing",
                storage: 15,
                security: "standard",
                budget: 100,
                orchestration: "docker_compose",
                monitoring: "basic"
            }
        };

        function fillSamplePreset(name) {
            const p = presets[name];
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

        function getFormData() {
            return {
                project_name: document.getElementById('req-project-name').value.trim() || "untitled-workload",
                stream: document.getElementById('req-stream').value,
                technology: {
                    frontend: document.getElementById('req-frontend').value,
                    backend: document.getElementById('req-backend').value,
                    database: document.getElementById('req-database').value
                },
                operations: {
                    container_orchestration: document.getElementById('req-orchestration').value,
                    infrastructure_as_code: "terraform",
                    configuration_management: "none",
                    ci_cd_pipeline: "github_actions"
                },
                monitoring: {
                    level: document.getElementById('req-monitoring').value,
                    alerting_channel: document.getElementById('req-monitoring').value === "advanced" ? "slack_webhook" : "email"
                },
                traffic_scale: document.getElementById('req-traffic').value,
                reliability: document.getElementById('req-reliability').value,
                data_storage_gb: parseFloat(document.getElementById('req-storage').value) || 10.0,
                security_need: document.getElementById('req-security').value,
                monthly_budget: parseFloat(document.getElementById('req-budget').value) || null
            };
        }

        function applyParsedInputToForm(p) {
            if (!p) return;
            if (p.project_name) document.getElementById('req-project-name').value = p.project_name;
            if (p.stream) document.getElementById('req-stream').value = p.stream;
            if (p.technology) {
                if (p.technology.frontend) document.getElementById('req-frontend').value = p.technology.frontend;
                if (p.technology.backend) document.getElementById('req-backend').value = p.technology.backend;
                if (p.technology.database) document.getElementById('req-database').value = p.technology.database;
            }
            if (p.operations && p.operations.container_orchestration) {
                document.getElementById('req-orchestration').value = p.operations.container_orchestration;
            }
            if (p.monitoring && p.monitoring.level) {
                document.getElementById('req-monitoring').value = p.monitoring.level;
            }
            if (p.traffic_scale) document.getElementById('req-traffic').value = p.traffic_scale;
            if (p.reliability) document.getElementById('req-reliability').value = p.reliability;
            if (p.security_need) document.getElementById('req-security').value = p.security_need;
            if (p.data_storage_gb) document.getElementById('req-storage').value = p.data_storage_gb;
            if (p.monthly_budget) document.getElementById('req-budget').value = p.monthly_budget;
            
            // Visual highlight animation
            const formCard = document.getElementById('requirements-form');
            formCard.classList.add('ring-2', 'ring-[#ff9900]/50');
            setTimeout(() => formCard.classList.remove('ring-2', 'ring-[#ff9900]/50'), 1200);
        }

        function setPromptAndAnalyze(text) {
            document.getElementById('ai-prompt-input').value = text;
            handleAiAnalyzeDirect();
        }

        async function handleAiAutoFill() {
            const prompt = document.getElementById('ai-prompt-input').value.trim();
            if (!prompt) {
                alert("Please enter a natural language requirement prompt first.");
                return;
            }
            const btn = document.getElementById('btn-ai-autofill');
            btn.innerHTML = `<span>Parsing...</span>`;
            btn.disabled = true;
            try {
                const res = await fetch('/api/v1/requirements/parse-prompt', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: prompt })
                });
                const json = await res.json();
                if (json.status === 'SUCCESS') {
                    applyParsedInputToForm(json.parsed_input);
                } else {
                    alert("Parsing failed: " + (json.detail || "Unknown error"));
                }
            } catch(err) {
                alert("Error parsing prompt: " + err.message);
            } finally {
                btn.innerHTML = `<svg class="w-3.5 h-3.5 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg><span>AI Auto-Fill Form</span>`;
                btn.disabled = false;
            }
        }

        async function handleAiAnalyzeDirect() {
            const prompt = document.getElementById('ai-prompt-input').value.trim();
            if (!prompt) {
                alert("Please enter a natural language requirement prompt first.");
                return;
            }
            const region = document.getElementById('req-region').value || "us-east-1";
            const btn = document.getElementById('btn-ai-analyze');
            btn.innerHTML = `<span>AI Sizing...</span>`;
            btn.disabled = true;
            try {
                const res = await fetch('/api/v1/requirements/ai-analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: prompt, target_region: region, auto_save: true })
                });
                const json = await res.json();
                if (json.status === 'SUCCESS') {
                    applyParsedInputToForm(json.parsed_input);
                    currentAnalysisData = json.data;
                    currentProjectId = json.project_id;
                    renderAnalysisResults(json.data);
                    loadSavedProjects();
                } else {
                    alert("AI analysis error: " + (json.detail || "Unknown error"));
                }
            } catch(err) {
                alert("Error in AI analysis: " + err.message);
            } finally {
                btn.innerHTML = `<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg><span>AI Sizing & Analysis</span>`;
                btn.disabled = false;
            }
        }

        async function handleAnalyzeSubmit(e) {
            e.preventDefault();
            triggerAnalyze();
        }

        async function triggerAnalyze() {
            const payload = getFormData();
            const btn = document.getElementById('btn-analyze');
            btn.innerHTML = `<span>Analyzing...</span>`;
            btn.disabled = true;

            try {
                const res = await fetch('/api/v1/requirements/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const json = await res.json();
                if (json.status === 'SUCCESS') {
                    currentAnalysisData = json.data;
                    currentProjectId = json.project_id;
                    renderAnalysisResults(json.data);
                } else {
                    alert("Analysis error: " + (json.detail || "Unknown error"));
                }
            } catch (err) {
                console.error("Error:", err);
                alert("Failed to analyze workload: " + err.message);
            } finally {
                btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg><span>Analyze & Size Workload</span>`;
                btn.disabled = false;
            }
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
                if (json.status === 'CREATED') {
                    currentProjectId = json.project.id;
                    alert("✓ Project '" + json.project.project_name + "' saved to SQLite requirements.db!");
                    loadSavedProjects();
                } else {
                    alert("Save failed: " + JSON.stringify(json));
                }
            } catch (err) {
                alert("Failed to save: " + err.message);
            }
        }

        function renderAnalysisResults(data) {
            const profile = data.profile;
            const rationales = data.service_rationales;
            const optimizations = data.cost_optimizations;
            const breakdown = data.cost_breakdown;

            document.getElementById('out-project-title').textContent = document.getElementById('req-project-name').value;
            document.getElementById('out-tier-badge').textContent = profile.architecture_tier.toUpperCase();
            document.getElementById('out-ha-badge').textContent = profile.high_availability_mode.toUpperCase();
            document.getElementById('out-total-cost').innerHTML = `$${data.total_estimated_cost.toFixed(2)} <span class="text-xs text-[#9ba7b6] font-normal">/ mo</span>`;

            const budgetLimit = profile.monthly_budget_limit;
            const budgetStatus = document.getElementById('out-budget-status');
            if (budgetLimit) {
                if (data.total_estimated_cost <= budgetLimit) {
                    budgetStatus.textContent = `Within $${budgetLimit.toFixed(2)} budget limit (Est. $${(budgetLimit - data.total_estimated_cost).toFixed(2)} headroom)`;
                    budgetStatus.className = "text-[10px] text-[#1d8102] font-semibold";
                } else {
                    budgetStatus.textContent = `Exceeds budget of $${budgetLimit.toFixed(2)} by $${(data.total_estimated_cost - budgetLimit).toFixed(2)}/mo`;
                    budgetStatus.className = "text-[10px] text-[#d13212] font-semibold";
                }
            } else {
                budgetStatus.textContent = "Unlimited Budget (Targeting Cost-Optimized Spec)";
                budgetStatus.className = "text-[10px] text-gray-400 font-normal";
            }

            // 1. Render Specs Cards
            const comp = profile.components;
            const specsHtml = `
                <div class="p-3.5 rounded bg-[#0f141c] border border-[#2d3748] space-y-2">
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] font-bold text-[#ec7211] uppercase tracking-wider font-mono">Compute (EC2)</span>
                        <span class="font-mono text-xs font-bold text-white">$${comp.compute.monthly_cost.toFixed(2)}/mo</span>
                    </div>
                    <div class="text-xs font-bold text-white font-mono">${comp.compute.instance_type}</div>
                    <div class="text-[11px] text-[#9ba7b6]">${comp.compute.vcpus} vCPUs • ${comp.compute.ram_gb} GB RAM</div>
                    <div class="text-[10px] text-gray-400">Min: ${comp.compute.min_instances} | Max: ${comp.compute.max_instances} | Target CPU: ${comp.compute.target_cpu_utilization}%</div>
                </div>

                <div class="p-3.5 rounded bg-[#0f141c] border border-[#2d3748] space-y-2">
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] font-bold text-[#539fe5] uppercase tracking-wider font-mono">Database (RDS)</span>
                        <span class="font-mono text-xs font-bold text-white">$${comp.database.monthly_cost.toFixed(2)}/mo</span>
                    </div>
                    <div class="text-xs font-bold text-white font-mono">${comp.database.instance_type}</div>
                    <div class="text-[11px] text-[#9ba7b6]">${comp.database.storage_gb} GB ${comp.database.storage_type} • Multi-AZ: ${comp.database.multi_az ? 'Yes' : 'No'}</div>
                    <div class="text-[10px] text-gray-400">Backups: ${comp.database.backup_retention_days} days PITR recovery</div>
                </div>

                <div class="p-3.5 rounded bg-[#0f141c] border border-[#2d3748] space-y-2">
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] font-bold text-[#a87ffb] uppercase tracking-wider font-mono">Networking (VPC)</span>
                        <span class="font-mono text-xs font-bold text-white">$${comp.networking.monthly_cost.toFixed(2)}/mo</span>
                    </div>
                    <div class="text-xs font-bold text-white">VPC with Public/Private Subnets</div>
                    <div class="text-[11px] text-[#9ba7b6]">ALB: ${comp.networking.has_alb ? 'Enabled' : 'None'} • NAT Gateways: ${comp.networking.nat_gateway_count}</div>
                    <div class="text-[10px] text-gray-400">CloudFront CDN: ${comp.networking.has_cloudfront ? 'Active' : 'Disabled'}</div>
                </div>

                <div class="p-3.5 rounded bg-[#0f141c] border border-[#2d3748] space-y-2">
                    <div class="flex justify-between items-center">
                        <span class="text-[10px] font-bold text-[#1d8102] uppercase tracking-wider font-mono">Storage & Security</span>
                        <span class="font-mono text-xs font-bold text-white">$${comp.storage.monthly_cost.toFixed(2)}/mo</span>
                    </div>
                    <div class="text-xs font-bold text-white">EBS ${comp.storage.ebs_gb_per_instance} GB gp3 + S3 ${comp.storage.s3_gb} GB</div>
                    <div class="text-[11px] text-[#9ba7b6]">KMS Encryption: ${comp.security.encryption_enabled ? 'Enforced' : 'Default'}</div>
                    <div class="text-[10px] text-gray-400">WAF: ${comp.security.waf_enabled ? 'Active' : 'None'} • Compliance: ${profile.compliance_applied.join(', ') || 'Standard'}</div>
                </div>
            `;
            document.getElementById('specs-cards-container').innerHTML = specsHtml;

            // 2. Render Rationales (Why that service)
            let whyHtml = '';
            for (const [key, item] of Object.entries(rationales)) {
                whyHtml += `
                    <div class="p-3 rounded bg-[#0f141c] border border-[#2d3748] space-y-1.5">
                        <div class="flex items-center justify-between">
                            <span class="font-bold text-white text-xs font-mono text-[#ff9900]">${item.service_name}</span>
                            <span class="text-[10px] px-1.5 py-0.2 rounded bg-[#232f3e] text-gray-300">${item.category}</span>
                        </div>
                        <p class="text-xs text-gray-300 leading-relaxed">${item.why}</p>
                        <div class="text-[10px] text-[#9ba7b6] font-mono">${item.specs}</div>
                    </div>
                `;
            }
            document.getElementById('rationales-container').innerHTML = whyHtml;

            // 3. Render FinOps Cost Optimizations
            let finopsHtml = '';
            optimizations.forEach(opt => {
                finopsHtml += `
                    <div class="p-3 rounded bg-[#0f141c] border-l-4 border-l-[#ec7211] border border-[#2d3748] space-y-1">
                        <div class="flex items-center justify-between">
                            <h4 class="font-bold text-white text-xs">${opt.title}</h4>
                            <span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-[#1d8102]/20 text-[#1d8102] border border-[#1d8102]/30">
                                Save ~$${opt.estimated_monthly_savings}/mo
                            </span>
                        </div>
                        <p class="text-xs text-[#9ba7b6] leading-relaxed">${opt.recommendation}</p>
                        <div class="text-[10px] text-gray-400 font-mono flex gap-2">
                            <span>Category: ${opt.category}</span>
                            <span>•</span>
                            <span class="text-[#ff9900]">${opt.savings_percentage}</span>
                        </div>
                    </div>
                `;
            });
            document.getElementById('finops-container').innerHTML = finopsHtml;

            // 4. Render AI Well-Architected Framework Analysis
            if (data.ai_advice) {
                const ai = data.ai_advice;
                const sc = ai.scorecard;
                const syn = ai.synthesis;

                let scoreColor = sc.overall_score >= 85 ? '#1d8102' : (sc.overall_score >= 70 ? '#ec7211' : '#d13212');

                let pillarsHtml = '';
                const pillarKeys = ['security', 'reliability', 'performance', 'cost_optimization', 'operational_excellence', 'sustainability'];
                pillarKeys.forEach(pk => {
                    const p = sc[pk];
                    if (!p) return;
                    let pColor = p.score >= 85 ? 'bg-[#1d8102]' : (p.score >= 70 ? 'bg-[#ec7211]' : 'bg-[#d13212]');
                    let insightsList = p.insights.map(i => `<li class="text-[11px] text-[#9ba7b6] list-disc list-inside">${i}</li>`).join('');
                    pillarsHtml += `
                        <div class="p-3 rounded bg-[#0f141c] border border-[#2d3748] space-y-2">
                            <div class="flex justify-between items-center">
                                <span class="font-bold text-xs text-white">${p.pillar}</span>
                                <span class="text-xs font-mono font-bold text-white">${p.score}/100</span>
                            </div>
                            <div class="w-full bg-[#1b2533] rounded-full h-1.5 overflow-hidden">
                                <div class="${pColor} h-1.5 rounded-full" style="width: ${p.score}%"></div>
                            </div>
                            <ul class="space-y-1 pt-1">
                                ${insightsList}
                            </ul>
                        </div>
                    `;
                });

                let tradeoffsHtml = '';
                if (syn.key_tradeoffs && syn.key_tradeoffs.length > 0) {
                    tradeoffsHtml = syn.key_tradeoffs.map(t => `<div class="p-2 rounded bg-[#161e2e] border border-[#2d3748] text-xs text-amber-200">⚖️ ${t}</div>`).join('');
                }

                const aiContainerHtml = `
                    <div class="p-4 rounded bg-[#161e2e] border border-[#2d3748] space-y-3">
                        <div class="flex items-center justify-between flex-wrap gap-2">
                            <div class="flex items-center gap-2">
                                <span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-[#1d8102]/20 text-[#1d8102] border border-[#1d8102]/30 uppercase">
                                    Well-Architected Score: ${sc.overall_score}/100
                                </span>
                                <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-[#232f3e] text-gray-300">
                                    ${syn.confidence_level}
                                </span>
                            </div>
                            <span class="text-[10px] text-gray-400 font-mono">${syn.ai_engine}</span>
                        </div>
                        <p class="text-xs text-gray-200 leading-relaxed font-sans bg-[#0f141c] p-3 rounded border border-[#2d3748]">
                            ${syn.executive_summary}
                        </p>
                        ${tradeoffsHtml ? `<div class="space-y-1 pt-1"><div class="text-[10px] font-bold text-[#ff9900] uppercase tracking-wider font-mono">Workload Architecture Trade-offs</div>${tradeoffsHtml}</div>` : ''}
                    </div>

                    <div class="text-xs font-bold text-white pt-2">AWS Well-Architected 6-Pillar Scorecard</div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        ${pillarsHtml}
                    </div>
                `;
                document.getElementById('ai-advisor-container').innerHTML = aiContainerHtml;
            }
        }

        function switchResultTab(tab) {
            const tabs = ['specs', 'why', 'finops', 'ai'];
            tabs.forEach(t => {
                document.getElementById('tab-content-' + t).classList.add('hidden');
                document.getElementById('tab-btn-' + t).className = 'pb-2.5 tab-inactive flex items-center gap-1.5 cursor-pointer';
            });
            document.getElementById('tab-content-' + tab).classList.remove('hidden');
            document.getElementById('tab-btn-' + tab).className = 'pb-2.5 tab-active flex items-center gap-1.5 cursor-pointer';
        }


        async function dispatchToModule2() {
            if (!currentProjectId) {
                // First save project to get ID
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
                    alert("Dispatch failed: " + (json.detail || "Module 2 unreachable"));
                }
            } catch (err) {
                alert("Dispatch error: " + err.message);
            } finally {
                btn.innerHTML = `<span>Dispatch to Module 2</span><svg class="w-3.5 h-3.5 text-[#ff9900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>`;
                btn.disabled = false;
            }
        }

        function showDispatchModal(data) {
            const modal = document.getElementById('dispatch-modal');
            const content = document.getElementById('dispatch-modal-content');
            content.innerHTML = `
                <div class="p-3 rounded bg-[#0f141c] border border-[#1d8102]/50 space-y-1">
                    <div class="font-bold text-white text-xs">Module 2 (Architecture Generator) Response: 200 OK</div>
                    <div class="text-[11px] text-gray-300">Generated deterministic ReactFlow visual diagram in <strong>${data.dispatch_duration_ms}ms</strong>.</div>
                </div>
                <div class="grid grid-cols-2 gap-2 text-center">
                    <div class="p-2.5 rounded bg-[#0f141c] border border-[#2d3748]">
                        <div class="text-lg font-bold text-[#ff9900] font-mono">${data.graph_nodes}</div>
                        <div class="text-[10px] text-gray-400">Diagram Nodes</div>
                    </div>
                    <div class="p-2.5 rounded bg-[#0f141c] border border-[#2d3748]">
                        <div class="text-lg font-bold text-[#539fe5] font-mono">${data.graph_edges}</div>
                        <div class="text-[10px] text-gray-400">Network Edges</div>
                    </div>
                </div>
                <p class="text-[11px] text-[#9ba7b6]">
                    The requirement specifications were successfully mapped to coordinate nodes and topological edges. Ready for Module 3 (IaC Generator).
                </p>
            `;
            modal.classList.remove('hidden');
        }

        function closeDispatchModal() {
            document.getElementById('dispatch-modal').classList.add('hidden');
        }

        async function loadSavedProjects() {
            try {
                const res = await fetch('/api/v1/requirements?limit=20');
                const json = await res.json();
                if (json.status === 'SUCCESS') {
                    renderSavedProjectsTable(json.projects);
                }
            } catch (err) {
                console.error("Failed to load saved projects:", err);
            }
        }

        function renderSavedProjectsTable(projects) {
            document.getElementById('saved-count').textContent = `${projects.length} Saved`;
            const tbody = document.getElementById('saved-projects-tbody');
            if (projects.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-gray-500">No saved requirement projects yet. Fill form and click Save.</td></tr>`;
                return;
            }

            let html = '';
            projects.forEach(p => {
                const dateStr = p.created_at ? p.created_at.replace('T', ' ').slice(0, 16) : '';
                const dispatchedBadge = p.dispatched_to_m2
                    ? `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-[#1d8102]/20 text-[#1d8102] border border-[#1d8102]/40">M2 DISPATCHED</span>`
                    : `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-[#232f3e] text-gray-400 border border-[#414d5c]">SAVED</span>`;

                html += `
                    <tr class="hover:bg-[#232f3e]/40 transition">
                        <td class="p-3">
                            <div class="font-bold text-white">${p.project_name}</div>
                            <div class="text-[10px] text-gray-400 font-mono truncate max-w-xs">${p.description || p.id}</div>
                        </td>
                        <td class="p-3 font-mono text-[11px]">
                            <div>${p.stream}</div>
                            <div class="text-gray-400">${p.target_region}</div>
                        </td>
                        <td class="p-3">
                            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[#232f3e] text-[#ff9900] border border-[#ec7211]/30">
                                ${p.architecture_tier}
                            </span>
                        </td>
                        <td class="p-3 text-right font-mono font-bold text-white">
                            $${p.estimated_monthly_cost.toFixed(2)}/mo
                        </td>
                        <td class="p-3 text-center">
                            ${dispatchedBadge}
                        </td>
                        <td class="p-3 text-right space-x-1.5">
                            <button onclick="inspectSavedProject('${p.id}')" class="px-2 py-1 rounded bg-[#232f3e] hover:bg-[#2a384c] text-white border border-[#414d5c] text-[10px] font-semibold cursor-pointer">
                                Inspect
                            </button>
                            <button onclick="deleteProject('${p.id}')" class="px-2 py-1 rounded bg-[#3d1314] hover:bg-[#52191b] text-[#ff9492] border border-[#d13212]/50 text-[10px] font-semibold cursor-pointer">
                                Delete
                            </button>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        }

        async function inspectSavedProject(id) {
            try {
                const res = await fetch(`/api/v1/requirements/${id}`);
                const json = await res.json();
                if (json.status === 'SUCCESS') {
                    const p = json.project;
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

                    // Render results
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
