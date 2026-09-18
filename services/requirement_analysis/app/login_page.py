# services/requirement_analysis/app/login_page.py
def get_login_page_html(redirect: str = "/admin") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AetherOps Cloud - Admin Login</title>
    <link rel="stylesheet" href="/static/fonts/fonts.css">
    <script src="/static/js/tailwind.js"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Plus Jakarta Sans', 'Segoe UI', 'sans-serif'],
                        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
                    }},
                    colors: {{
                        aws: {{
                            squid: '#161e2e',
                            squidDark: '#0f141c',
                            navy: '#232f3e',
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
                        }}
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{
            background-color: #0f141c;
            color: #eaeded;
        }}
        .aws-card {{
            background-color: #1b2533;
            border: 1px solid #2d3748;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        }}
        .aws-btn-primary {{
            background-color: #ec7211;
            color: #ffffff;
            transition: all 0.15s ease-in-out;
        }}
        .aws-btn-primary:hover {{
            background-color: #eb5f07;
        }}
        .aws-btn-primary:active {{
            background-color: #dd5706;
        }}
        .aws-input {{
            background-color: #0f141c;
            border: 1px solid #3b444b;
            color: #ffffff;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }}
        .aws-input:focus {{
            border-color: #ec7211;
            box-shadow: 0 0 0 1px #ec7211;
            outline: none;
        }}
    </style>
</head>
<body class="min-h-screen antialiased flex flex-col justify-between font-sans selection:bg-[#ec7211]/30 selection:text-[#ff9900]">

    <!-- AWS Console Top Navigation Bar -->
    <header class="bg-[#161e2e] border-b border-[#2d3748] px-6 py-3 flex items-center justify-between shadow-sm">
        <div class="flex items-center space-x-3">
            <div class="flex items-center space-x-2 cursor-pointer">
                <span class="font-extrabold text-white text-lg tracking-tight">AetherOps</span>
                <span class="text-[#ff9900] text-[10px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-[#232f3e] border border-[#ff9900]/40 font-mono">AWS CLOUD</span>
            </div>
            <div class="h-4 w-px bg-gray-600 hidden sm:block"></div>
            <span class="text-xs text-[#9ba7b6] hidden sm:inline">Infrastructure Management Console</span>
        </div>

        <div class="flex items-center space-x-3 text-xs text-gray-400 font-medium">
            <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#0f141c] border border-[#2d3748] text-gray-300 font-mono text-[11px]">
                <span class="h-2 w-2 rounded-full bg-[#1d8102] animate-pulse"></span>
                <span>Console Gateway</span>
            </span>
            <span class="hidden sm:inline text-gray-500">|</span>
            <span class="hidden sm:inline text-xs text-gray-400">Global (39 Regions)</span>
        </div>
    </header>

    <!-- Main Sign-In Workspace (Modeled directly after AWS Management Console Sign-In) -->
    <main class="flex-1 flex items-center justify-center p-4 sm:p-6 my-6">
        <div class="aws-card w-full max-w-md p-6 sm:p-8 rounded-lg space-y-6">
            
            <!-- AWS Header Section -->
            <div class="space-y-1.5 border-b border-[#2d3748] pb-5">
                <div class="flex items-center justify-between">
                    <h2 class="text-xl font-bold text-white tracking-tight">Admin Authentication</h2>
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-[#ec7211]/20 text-[#ff9900] border border-[#ec7211]/40 font-mono">ROOT SECURE</span>
                </div>
                <p class="text-xs text-[#9ba7b6]">Sign in to AetherOps AWS Infrastructure Management Console</p>
            </div>

            <!-- AWS Account Type Indicator (Root User vs IAM User style) -->
            <div class="p-3 bg-[#0f141c] rounded border border-[#2d3748] flex items-center space-x-3">
                <div class="p-2 rounded bg-[#232f3e] text-[#ff9900] shrink-0">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
                </div>
                <div class="text-xs">
                    <div class="font-bold text-white">Root Account Authentication</div>
                    <div class="text-[11px] text-[#9ba7b6]">PostgreSQL Credential Vault & JWT HttpOnly Session</div>
                </div>
            </div>

            <!-- Error Banner -->
            <div id="error-banner" class="hidden p-3 rounded bg-[#3d1314] border border-[#d13212] text-[#ff9492] text-xs flex items-center space-x-2.5">
                <svg class="w-4 h-4 text-[#d13212] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span id="error-text">Authentication failed</span>
            </div>

            <!-- Success Banner -->
            <div id="success-banner" class="hidden p-3 rounded bg-[#0e3118] border border-[#1d8102] text-[#8ce299] text-xs flex items-center space-x-2.5">
                <svg class="w-4 h-4 text-[#1d8102] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                <span>Authenticated! Redirecting to AWS Console Dashboard...</span>
            </div>

            <!-- Login Form -->
            <form id="login-form" onsubmit="handleAdminLogin(event)" class="space-y-4">
                
                <!-- Username Input -->
                <div class="space-y-1.5">
                    <label for="username" class="block text-xs font-bold text-gray-300">Root User Username or Email</label>
                    <div class="relative">
                        <input type="text" id="username" name="username" required autocomplete="username" placeholder="admin"
                            class="aws-input w-full px-3 py-2 rounded text-sm placeholder-gray-500 font-mono">
                    </div>
                </div>

                <!-- Password Input -->
                <div class="space-y-1.5">
                    <div class="flex justify-between items-center">
                        <label for="password" class="block text-xs font-bold text-gray-300">Master Password</label>
                        <button type="button" onclick="togglePasswordVisibility()" class="text-[11px] text-[#0972d3] hover:text-[#033ebc] font-semibold cursor-pointer">
                            Show / Hide
                        </button>
                    </div>
                    <div class="relative">
                        <input type="password" id="password" name="password" required autocomplete="current-password" placeholder="••••••••••••"
                            class="aws-input w-full px-3 py-2 pr-10 rounded text-sm placeholder-gray-500 font-mono">
                        <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-gray-500">
                            <svg id="eye-icon" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                        </div>
                    </div>
                </div>

                <!-- Remember Me & Security Policy -->
                <div class="flex items-center justify-between pt-1">
                    <label class="flex items-center space-x-2 cursor-pointer">
                        <input type="checkbox" id="remember-me" class="rounded bg-[#0f141c] border-[#3b444b] text-[#ec7211] focus:ring-[#ec7211] focus:ring-offset-0">
                        <span class="text-xs text-[#9ba7b6]">Remember this account (7 days)</span>
                    </label>
                    <span class="text-[10px] text-[#9ba7b6] font-mono">HttpOnly • SameSite</span>
                </div>

                <!-- Submit Button: Official AWS Orange CTA -->
                <button type="submit" id="submit-btn" class="aws-btn-primary w-full py-2.5 px-4 rounded font-bold text-sm shadow-sm flex items-center justify-center space-x-2 cursor-pointer mt-2">
                    <span id="btn-text">Sign In to AetherOps Console</span>
                    <svg id="btn-arrow" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                    <svg id="btn-spinner" class="w-4 h-4 animate-spin hidden" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
                </button>

            </form>

            <!-- Auto-fill Demo Box -->
            <div class="pt-4 border-t border-[#2d3748]">
                <button onclick="fillDemoCredentials()" class="w-full py-2 px-3 rounded bg-[#0f141c] hover:bg-[#232f3e] border border-[#2d3748] hover:border-[#ec7211]/50 text-xs text-gray-300 transition flex items-center justify-between cursor-pointer">
                    <span class="font-mono text-[11px] text-[#9ba7b6]">Default: <strong class="text-white">admin</strong> / <strong class="text-white">AetherOps@2026!</strong></span>
                    <span class="text-[10px] font-bold text-[#ff9900] bg-[#ec7211]/15 px-2 py-0.5 rounded border border-[#ec7211]/30">Auto Fill</span>
                </button>
            </div>

            <!-- Platform Architecture Footnote -->
            <div class="text-center pt-2">
                <div class="inline-flex items-center space-x-1.5 text-[11px] text-[#9ba7b6]">
                    <svg class="w-3.5 h-3.5 text-[#1d8102]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>
                    <span>Autonomous Infrastructure Platform • Orchestrated by Kubernetes (K8s)</span>
                </div>
            </div>

        </div>
    </main>

    <!-- Standard AWS Console Footer -->
    <footer class="bg-[#161e2e] border-t border-[#2d3748] py-4 px-6 text-center text-xs text-[#9ba7b6] flex flex-col sm:flex-row items-center justify-between gap-3">
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

                // Store token in localStorage as automated client fallback
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
                btnText.innerText = "Sign In to AWS Console";
                btnArrow.classList.remove('hidden');
                btnSpinner.classList.add('hidden');
                submitBtn.disabled = false;
            }}
        }}
    </script>
</body>
</html>
"""
