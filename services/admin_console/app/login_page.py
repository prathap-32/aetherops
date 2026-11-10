# services/admin_console/app/login_page.py
def get_login_page_html(redirect: str = "/admin") -> str:
    return fr"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AetherOps Cloud - Admin Login</title>
    <link rel="stylesheet" href="/static/fonts/fonts.css">
    <script src="/static/js/tailwind.js"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Amazon Ember', 'Segoe UI', 'sans-serif'],
                        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
                    }},
                    colors: {{
                        aether: {{
                            header: '#161e2e',
                            orange: '#ec7211',
                            orangeHover: '#eb5f07',
                            orangeLight: '#ff9900',
                            blue: '#0972d3',
                            blueHover: '#033ebc',
                            green: '#1d8102',
                            red: '#d13212'
                        }}
                    }}
                }}
            }}
        }}
    </script>
    <style>
        :root {{
            --bg-page: #f8fafc;
            --bg-card: #ffffff;
            --border-card: #e2e8f0;
            --text-title: #0f172a;
            --text-body: #334155;
            --text-muted: #64748b;
            --input-bg: #ffffff;
            --input-border: #cbd5e1;
            --input-text: #0f172a;
            --card-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.08), 0 2px 6px -1px rgba(0, 0, 0, 0.04);
        }}
        html.dark {{
            --bg-page: #0f141c;
            --bg-card: #1b2533;
            --border-card: #2d3748;
            --text-title: #ffffff;
            --text-body: #eaeded;
            --text-muted: #9ba7b6;
            --input-bg: #0f141c;
            --input-border: #3b444b;
            --input-text: #ffffff;
            --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        }}
        body {{
            background-color: var(--bg-page);
            color: var(--text-body);
            transition: background-color 0.15s ease, color 0.15s ease;
        }}
        .console-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-card);
            box-shadow: var(--card-shadow);
        }}
        .btn-primary {{
            background-color: #ec7211;
            color: #ffffff;
            transition: all 0.15s ease-in-out;
        }}
        .btn-primary:hover {{
            background-color: #eb5f07;
        }}
        .btn-primary:active {{
            background-color: #dd5706;
        }}
        .console-input {{
            background-color: var(--input-bg);
            border: 1px solid var(--input-border);
            color: var(--input-text);
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }}
        .aws-btn-secondary {{
            background-color: var(--input-bg);
            border: 1px solid var(--border-card);
            color: var(--text-title);
            transition: all 0.15s ease-in-out;
        }}
        .aws-btn-secondary:hover {{
            border-color: #ec7211;
        }}

        /* Light mode specific header element adjustments */
        html:not(.dark) header {{
            background-color: #ffffff !important;
            border-bottom: 1px solid #e2e8f0 !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
        }}
        html:not(.dark) header .text-white:not(.btn-primary):not(.bg-\[\#ec7211\]) {{
            color: #0f172a !important;
        }}
        html:not(.dark) header .text-gray-300 {{
            color: #334155 !important;
        }}
        html:not(.dark) header .bg-\[\#0f141c\],
        html:not(.dark) header .bg-\[\#232f3e\] {{
            background-color: #ffffff !important;
            border-color: #cbd5e1 !important;
            color: #1e293b !important;
        }}
        html:not(.dark) .aws-btn-secondary {{
            background-color: #ffffff !important;
            border-color: #cbd5e1 !important;
            color: #1e293b !important;
        }}
        html:not(.dark) .aws-btn-secondary:hover {{
            background-color: #f8fafc !important;
            border-color: #ec7211 !important;
            color: #0f172a !important;
        }}
    </style>
</head>
<body class="min-h-screen antialiased flex flex-col justify-between font-sans selection:bg-[#ec7211]/30 selection:text-[#ff9900]">

    <!-- Top Navigation Bar -->
    <header class="app-header h-14 bg-white dark:bg-[#161e2e] border-b border-gray-200 dark:border-[#2d3748] px-4 sm:px-6 flex items-center justify-between shadow-xs transition-colors duration-150">
        <div class="flex items-center space-x-3 shrink-0">
            <div class="flex items-center space-x-2 cursor-pointer">
                <span class="font-extrabold text-title text-base sm:text-lg tracking-tight">AetherOps</span>
                <span class="text-[#ea580c] dark:text-[#ff9900] text-[10px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-orange-100 dark:bg-[#232f3e] border border-orange-200 dark:border-[#ff9900]/40 font-mono">CLOUD CONSOLE</span>
            </div>
            <div class="h-4 w-px bg-gray-300 dark:bg-gray-700 hidden sm:block"></div>
            <span class="text-xs text-muted-custom hidden sm:inline">Infrastructure Management & Catalog Control Plane</span>
        </div>

        <div class="flex items-center space-x-2 text-xs shrink-0">
            <span class="inline-flex items-center gap-1.5 h-8 px-2.5 rounded-md bg-gray-100 dark:bg-[#0f141c] border border-gray-200 dark:border-[#2d3748] text-gray-700 dark:text-gray-300 font-mono text-[11px]">
                <span class="h-2 w-2 rounded-full bg-[#16a34a] animate-pulse"></span>
                <span>Console Gateway :8000</span>
            </span>
            <button onclick="toggleTheme()" id="theme-toggle-btn" class="h-8 px-2.5 rounded-md aws-btn-secondary text-yellow-500 dark:text-yellow-400 transition cursor-pointer flex items-center gap-1.5 text-xs font-semibold" title="Toggle Light / Dark Theme">
                <span id="theme-toggle-icon">☀️</span>
                <span id="theme-toggle-text" class="text-xs">Light</span>
            </button>
        </div>
    </header>

    <!-- Main Sign-In Workspace -->
    <main class="flex-1 flex items-center justify-center p-4 sm:p-6 my-6">
        <div class="console-card w-full max-w-md p-6 sm:p-8 rounded-lg space-y-6">
            
            <!-- Header Section -->
            <div class="space-y-1.5 border-b border-gray-200 dark:border-[#2d3748] pb-5">
                <div class="flex items-center justify-between">
                    <h2 class="text-xl font-bold tracking-tight" style="color: var(--text-title);">Admin Authentication</h2>
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-[#ec7211]/20 text-[#ff9900] border border-[#ec7211]/40 font-mono">SECURE ROOT</span>
                </div>
                <p class="text-xs" style="color: var(--text-muted);">Sign in to access AetherOps Cloud Management Console</p>
            </div>

            <!-- Account Type Indicator -->
            <div class="p-3 bg-gray-50 dark:bg-[#0f141c] rounded border border-gray-200 dark:border-[#2d3748] flex items-center space-x-3">
                <div class="p-2 rounded bg-[#232f3e] text-[#ff9900] shrink-0">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
                </div>
                <div class="text-xs">
                    <div class="font-bold" style="color: var(--text-title);">Root Account Authentication</div>
                    <div class="text-[11px]" style="color: var(--text-muted);">PostgreSQL Credential Vault & JWT HttpOnly Session</div>
                </div>
            </div>

            <!-- Error Banner -->
            <div id="error-banner" class="hidden p-3 rounded bg-red-50 dark:bg-[#3d1314] border border-red-300 dark:border-[#d13212] text-red-700 dark:text-[#ff9492] text-xs flex items-center space-x-2.5">
                <svg class="w-4 h-4 text-red-600 dark:text-[#d13212] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span id="error-text">Authentication failed</span>
            </div>

            <!-- Success Banner -->
            <div id="success-banner" class="hidden p-3 rounded bg-green-50 dark:bg-[#0e3118] border border-green-300 dark:border-[#1d8102] text-green-800 dark:text-[#8ce299] text-xs flex items-center space-x-2.5">
                <svg class="w-4 h-4 text-green-600 dark:text-[#1d8102] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                <span>Authenticated! Redirecting to Console Dashboard...</span>
            </div>

            <!-- Login Form -->
            <form id="login-form" onsubmit="handleAdminLogin(event)" class="space-y-4">
                
                <!-- Username Input -->
                <div class="space-y-1.5">
                    <label for="username" class="block text-xs font-bold" style="color: var(--text-title);">Root Username or Email</label>
                    <div class="relative">
                        <input type="text" id="username" name="username" required autocomplete="username" placeholder="admin"
                            class="console-input w-full px-3 py-2 rounded text-sm font-mono">
                    </div>
                </div>

                <!-- Password Input -->
                <div class="space-y-1.5">
                    <div class="flex justify-between items-center">
                        <label for="password" class="block text-xs font-bold" style="color: var(--text-title);">Master Password</label>
                        <button type="button" onclick="togglePasswordVisibility()" class="text-[11px] text-[#0972d3] hover:text-[#033ebc] font-semibold cursor-pointer">
                            Show / Hide
                        </button>
                    </div>
                    <div class="relative">
                        <input type="password" id="password" name="password" required autocomplete="current-password" placeholder="••••••••••••"
                            class="console-input w-full px-3 py-2 pr-10 rounded text-sm font-mono">
                        <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-gray-400">
                            <svg id="eye-icon" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                        </div>
                    </div>
                </div>

                <!-- Remember Me & Security Policy -->
                <div class="flex items-center justify-between pt-1">
                    <label class="flex items-center space-x-2 cursor-pointer">
                        <input type="checkbox" id="remember-me" class="rounded border-gray-300 dark:border-[#3b444b] text-[#ec7211] focus:ring-[#ec7211]">
                        <span class="text-xs" style="color: var(--text-muted);">Remember account (7 days)</span>
                    </label>
                    <span class="text-[10px] font-mono" style="color: var(--text-muted);">HttpOnly • SameSite</span>
                </div>

                <!-- Submit Button -->
                <button type="submit" id="submit-btn" class="btn-primary w-full py-2.5 px-4 rounded font-bold text-sm shadow-sm flex items-center justify-center space-x-2 cursor-pointer mt-2">
                    <span id="btn-text">Sign In to AetherOps Console</span>
                    <svg id="btn-arrow" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                    <svg id="btn-spinner" class="w-4 h-4 animate-spin hidden" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
                </button>

            </form>

            <!-- Auto-fill Demo Box -->
            <div class="pt-4 border-t border-gray-200 dark:border-[#2d3748]">
                <button onclick="fillDemoCredentials()" class="w-full py-2 px-3 rounded bg-gray-50 hover:bg-gray-100 dark:bg-[#0f141c] dark:hover:bg-[#232f3e] border border-gray-200 dark:border-[#2d3748] hover:border-[#ec7211]/50 text-xs transition flex items-center justify-between cursor-pointer">
                    <span class="font-mono text-[11px]" style="color: var(--text-muted);">Default: <strong style="color: var(--text-title);">admin</strong> / <strong style="color: var(--text-title);">AetherOps@2026!</strong></span>
                    <span class="text-[10px] font-bold text-[#ff9900] bg-[#ec7211]/15 px-2 py-0.5 rounded border border-[#ec7211]/30">Auto Fill</span>
                </button>
            </div>

            <!-- Platform Architecture Footnote -->
            <div class="text-center pt-2">
                <div class="inline-flex items-center space-x-1.5 text-[11px]" style="color: var(--text-muted);">
                    <svg class="w-3.5 h-3.5 text-[#1d8102]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
                    <span>Autonomous Infrastructure Platform • Orchestrated by Kubernetes (K8s)</span>
                </div>
            </div>

        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-[#161e2e] border-t border-[#2d3748] py-4 px-6 text-center text-xs text-gray-400 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div class="flex items-center space-x-4">
            <a href="#" class="hover:text-white transition">Terms of Use</a>
            <a href="#" class="hover:text-white transition">Privacy Notice</a>
            <a href="#" class="hover:text-white transition">Documentation</a>
            <a href="#" class="hover:text-white transition">Support</a>
        </div>
        <div class="font-mono text-[11px] text-gray-400">
            &copy; 2026 AetherOps Cloud • Distributed Microservices Orchestrated by Kubernetes (K8s)
        </div>
    </footer>

    <script>
        const targetRedirect = "{redirect}";

        function applyTheme(theme) {{
            const btnIcon = document.getElementById('theme-toggle-icon');
            const btnText = document.getElementById('theme-toggle-text');
            if (theme === 'dark') {{
                document.documentElement.classList.add('dark');
                if (btnIcon) btnIcon.innerText = '☀️';
                if (btnText) btnText.innerText = 'Dark';
            }} else {{
                document.documentElement.classList.remove('dark');
                if (btnIcon) btnIcon.innerText = '🌙';
                if (btnText) btnText.innerText = 'Light';
            }}
            localStorage.setItem('aether_theme', theme);
        }}

        function toggleTheme() {{
            const isDark = document.documentElement.classList.contains('dark');
            applyTheme(isDark ? 'light' : 'dark');
        }}

        // Default theme is white / light
        const savedTheme = localStorage.getItem('aether_theme') || 'light';
        applyTheme(savedTheme);

        function togglePasswordVisibility() {{
            const pwd = document.getElementById('password');
            if (pwd.type === 'password') {{
                pwd.type = 'text';
            }} else {{
                pwd.type = 'password';
            }}
        }}

        function fillDemoCredentials() {{
            document.getElementById('username').value = 'admin';
            document.getElementById('password').value = 'AetherOps@2026!';
            document.getElementById('password').type = 'text';
            setTimeout(() => {{
                document.getElementById('password').type = 'password';
            }}, 1500);
        }}

        async function handleAdminLogin(e) {{
            e.preventDefault();
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            const rememberMe = document.getElementById('remember-me').checked;

            const errBanner = document.getElementById('error-banner');
            const errText = document.getElementById('error-text');
            const successBanner = document.getElementById('success-banner');
            const btnText = document.getElementById('btn-text');
            const btnArrow = document.getElementById('btn-arrow');
            const btnSpinner = document.getElementById('btn-spinner');
            const submitBtn = document.getElementById('submit-btn');

            errBanner.classList.add('hidden');
            successBanner.classList.add('hidden');
            btnText.innerText = "Signing in...";
            btnArrow.classList.add('hidden');
            btnSpinner.classList.remove('hidden');
            submitBtn.disabled = true;

            try {{
                const res = await fetch('/api/admin/auth/login', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        username: username,
                        password: password,
                        remember_me: rememberMe
                    }})
                }});

                const data = await res.json();

                if (!res.ok) {{
                    throw new Error(data.detail || "Authentication rejected");
                }}

                if (data.token) {{
                    localStorage.setItem('X-Admin-Key', data.token);
                }}

                successBanner.classList.remove('hidden');
                btnText.innerText = "Redirecting...";

                setTimeout(() => {{
                    window.location.href = targetRedirect || '/admin';
                }}, 600);

            }} catch (err) {{
                errText.innerText = err.message;
                errBanner.classList.remove('hidden');
                btnText.innerText = "Sign In to AetherOps Console";
                btnArrow.classList.remove('hidden');
                btnSpinner.classList.add('hidden');
                submitBtn.disabled = false;
            }}
        }}
    </script>
</body>
</html>
"""
