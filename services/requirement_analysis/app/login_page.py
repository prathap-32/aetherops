# services/requirement_analysis/app/login_page.py
def get_login_page_html(redirect: str = "/admin") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AetherOps Cloud - Admin Login</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Plus Jakarta Sans', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace'],
                    }},
                    colors: {{
                        cyber: {{
                            bg: '#07080c',
                            card: 'rgba(17, 20, 31, 0.85)',
                            border: 'rgba(255, 255, 255, 0.08)',
                            accent: '#6366f1',
                            violet: '#8b5cf6',
                            mint: '#10b981',
                            amber: '#f59e0b',
                            coral: '#ef4444',
                            cyan: '#06b6d4'
                        }}
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{
            background-color: #07080c;
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.18) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.15) 0px, transparent 50%);
            background-attachment: fixed;
        }}
        .glass-panel {{
            background: rgba(15, 18, 28, 0.75);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}
        .glow-accent {{
            box-shadow: 0 0 35px -5px rgba(99, 102, 241, 0.35);
        }}
    </style>
</head>
<body class="text-gray-100 min-h-screen antialiased flex flex-col justify-between font-sans selection:bg-indigo-500/30 selection:text-indigo-200">

    <!-- Top Minimal Navigation -->
    <header class="p-6 flex items-center justify-between max-w-7xl mx-auto w-full">
        <div class="flex items-center space-x-3">
            <div class="h-10 w-10 rounded-2xl bg-gradient-to-tr from-cyber-accent via-indigo-500 to-cyber-cyan flex items-center justify-center shadow-lg shadow-cyber-accent/25">
                <span class="font-extrabold text-lg text-white">A</span>
            </div>
            <div>
                <h1 class="text-base font-extrabold tracking-tight text-white flex items-center gap-1.5">
                    <span>AetherOps</span>
                    <span class="text-[9px] px-1.5 py-0.5 rounded bg-cyber-accent/20 text-indigo-300 font-semibold border border-cyber-accent/30 font-mono">CORE</span>
                </h1>
                <p class="text-[10px] text-gray-400 tracking-wider uppercase font-medium">Autonomous CloudOps Platform</p>
            </div>
        </div>
        <div class="flex items-center space-x-2 text-xs text-gray-400 font-mono">
            <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Auth Gate v1.0.0</span>
        </div>
    </header>

    <!-- Main Central Login Card -->
    <main class="flex-1 flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-md p-8 rounded-3xl border border-cyber-border shadow-2xl space-y-6 glow-accent">
            
            <!-- Card Header & Icon -->
            <div class="text-center space-y-2">
                <div class="inline-flex p-3.5 rounded-2xl bg-gradient-to-br from-indigo-600/20 to-cyber-cyan/20 border border-indigo-500/30 text-indigo-400 mb-1">
                    <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                </div>
                <h2 class="text-2xl font-extrabold text-white tracking-tight">Admin Authentication</h2>
                <p class="text-xs text-gray-400">PostgreSQL Credential Vault & JWT HttpOnly Session</p>
            </div>

            <!-- Error Banner (Hidden by default) -->
            <div id="error-banner" class="hidden p-3.5 rounded-xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs flex items-center space-x-2.5">
                <svg class="w-4 h-4 text-rose-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span id="error-text">Authentication failed</span>
            </div>

            <!-- Success Banner (Hidden by default) -->
            <div id="success-banner" class="hidden p-3.5 rounded-xl bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-xs flex items-center space-x-2.5">
                <svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                <span>Authenticated! Redirecting to AetherOps Console...</span>
            </div>

            <!-- Login Form -->
            <form id="login-form" onsubmit="handleAdminLogin(event)" class="space-y-4">
                
                <!-- Username Input -->
                <div class="space-y-1.5">
                    <label for="username" class="block text-xs font-bold text-gray-300 uppercase tracking-wider">Username or Email</label>
                    <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                        </div>
                        <input type="text" id="username" name="username" required autocomplete="username" placeholder="admin"
                            class="w-full pl-10 pr-4 py-2.5 bg-slate-900/90 border border-cyber-border rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition font-mono">
                    </div>
                </div>

                <!-- Password Input -->
                <div class="space-y-1.5">
                    <label for="password" class="block text-xs font-bold text-gray-300 uppercase tracking-wider">Master Password</label>
                    <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-500">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                        </div>
                        <input type="password" id="password" name="password" required autocomplete="current-password" placeholder="••••••••••••"
                            class="w-full pl-10 pr-10 py-2.5 bg-slate-900/90 border border-cyber-border rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition font-mono">
                        <button type="button" onclick="togglePasswordVisibility()" class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-500 hover:text-gray-300 cursor-pointer">
                            <svg id="eye-icon" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                        </button>
                    </div>
                </div>

                <!-- Remember Me & Security Policy -->
                <div class="flex items-center justify-between pt-1">
                    <label class="flex items-center space-x-2 cursor-pointer">
                        <input type="checkbox" id="remember-me" class="rounded bg-slate-900 border-cyber-border text-indigo-600 focus:ring-indigo-500 focus:ring-offset-0">
                        <span class="text-xs text-gray-400">Remember session (7 days)</span>
                    </label>
                    <span class="text-[10px] text-indigo-400 font-mono">JWT • HttpOnly</span>
                </div>

                <!-- Submit Button -->
                <button type="submit" id="submit-btn" class="w-full py-3 px-4 rounded-xl font-bold text-sm bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyber-cyan text-white shadow-lg shadow-indigo-600/30 hover:shadow-indigo-600/50 hover:brightness-110 active:scale-[0.99] transition flex items-center justify-center space-x-2 cursor-pointer">
                    <span id="btn-text">Authenticate & Enter Console</span>
                    <svg id="btn-arrow" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                    <svg id="btn-spinner" class="w-4 h-4 animate-spin hidden" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
                </button>

            </form>

            <!-- Auto-fill Demo Box -->
            <div class="pt-4 border-t border-cyber-border/60">
                <button onclick="fillDemoCredentials()" class="w-full py-2 px-3 rounded-xl bg-slate-900/60 hover:bg-indigo-950/30 border border-cyber-border hover:border-indigo-500/30 text-xs text-gray-400 hover:text-indigo-300 transition flex items-center justify-between cursor-pointer">
                    <span class="font-mono text-[11px]">Demo: admin / AetherOps@2026!</span>
                    <span class="text-[10px] font-bold text-indigo-400 bg-indigo-950/60 px-2 py-0.5 rounded border border-indigo-500/20">Auto Fill</span>
                </button>
            </div>

            <!-- Security Footer Guarantee -->
            <div class="text-center pt-2">
                <div class="inline-flex items-center space-x-1.5 text-[10px] text-gray-500 font-mono">
                    <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
                    <span>PostgreSQL Vault • Redis Rate Guard • Zero-Trust</span>
                </div>
            </div>

        </div>
    </main>

    <!-- Footer -->
    <footer class="p-6 text-center text-xs text-gray-500 font-mono">
        &copy; 2026 AetherOps Cloud Platform • Master Security Protocol
    </footer>

    <script>
        const targetRedirect = "{redirect}";

        function togglePasswordVisibility() {{
            const pwd = document.getElementById('password');
            const icon = document.getElementById('eye-icon');
            if (pwd.type === 'password') {{
                pwd.type = 'text';
                icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18"></path>';
            }} else {{
                pwd.type = 'password';
                icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>';
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
            btnText.innerText = "Verifying Vault...";
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
                btnText.innerText = "Access Granted";

                setTimeout(() => {{
                    window.location.href = targetRedirect || '/admin';
                }}, 600);

            }} catch (err) {{
                errText.innerText = err.message;
                errBanner.classList.remove('hidden');
                btnText.innerText = "Authenticate & Enter Console";
                btnArrow.classList.remove('hidden');
                btnSpinner.classList.add('hidden');
                submitBtn.disabled = false;
            }}
        }}
    </script>
</body>
</html>
"""
