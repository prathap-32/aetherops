# services/auth_service/app/main.py
"""
AetherOps Auth Service - Port 7999
Centralized Authentication & Identity Authority:
- Persistent SQLite storage for users and tenants
- AWS-style 12-digit Account ID generation and Login ID resolution
- Hidden internal Tenant ID with isolation checks
- Google & GitHub OAuth 2.0 initiation and callback handling
- Cryptographic JWT signing with embedded account and tenant claims
"""

import os
import sys
import time
import uuid
import datetime
import secrets
import hmac
import hashlib
import logging
import sqlite3
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
import jwt
import bcrypt
import httpx
import smtplib
from email.mime.multipart import MIMEMultipart
def get_dynamic_callback_uri(request: Request, default_path: str = "/api/v1/auth/github/callback") -> str:
    forwarded_host = request.headers.get("x-forwarded-host")
    forwarded_proto = request.headers.get("x-forwarded-proto")
    host = forwarded_host or request.headers.get("host")
    proto = forwarded_proto or ("https" if request.url.scheme == "https" or (host and ("ts.net" in host or "443" in str(request.url.port))) else "http")
    if host:
        return f"{proto}://{host}{default_path}"
    return f"{str(request.base_url).rstrip('/')}{default_path}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth-service")

# Centralized Application Secrets Manager
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SHARED_DIR = os.path.join(ROOT_DIR, "shared")
for p in (SHARED_DIR, ROOT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from aetherops_common.secrets import load_application_secrets
    load_application_secrets()
except Exception as _sec_err:
    logger.warning("AWS Secrets Manager initialization notice in auth_service: %s", _sec_err)
ENVIRONMENT = os.getenv("AETHER_ENV", os.getenv("ENVIRONMENT", "development")).lower()
INSECURE_DEV_JWT_SECRETS = {
    "aetherops-super-secure-production-cryptographic-jwt-token-signing-key-2026-cloudops-master",
    "secret",
    "changeme",
    "admin",
    "default",
    "test",
    "dev",
}


def validate_production_secrets(env: Optional[str] = None, secret: Optional[str] = None) -> None:
    target_env = (env or os.getenv("AETHER_ENV", os.getenv("ENVIRONMENT", "development"))).lower()
    target_secret = secret if secret is not None else os.getenv("JWT_SECRET_KEY")
    if target_env == "production":
        if not target_secret or target_secret in INSECURE_DEV_JWT_SECRETS:
            raise RuntimeError("FATAL: JWT_SECRET_KEY must be explicitly configured with a secure non-default secret in production.")


raw_jwt_key = os.getenv("JWT_SECRET_KEY")
validate_production_secrets()
if ENVIRONMENT == "production":
    JWT_SECRET_KEY = raw_jwt_key
else:
    JWT_SECRET_KEY = raw_jwt_key or "aetherops-super-secure-production-cryptographic-jwt-token-signing-key-2026-cloudops-master"

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "8"))

# OAuth credentials from environment
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/google/callback")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_OAUTH_REDIRECT_URI = os.getenv("GITHUB_OAUTH_REDIRECT_URI", "http://localhost:8000/api/v1/auth/github/callback")

# Database Path
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "auth.db")

app = FastAPI(title="AetherOps Auth Service - Port 7999")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:7999",
        "http://127.0.0.1:7999",
        "http://100.125.96.14:8000",
        "http://100.125.96.14:7999",
        "http://warmachine-1:8000",
        "http://warmachine-1:7999",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|100\.\d{1,3}\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|.*\.ts\.net|warmachine-1|.*\.local)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 30000;")
    return conn


def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Create tenants table
    c.execute("""
    CREATE TABLE IF NOT EXISTS tenants (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        account_id TEXT UNIQUE NOT NULL,
        tenant_type TEXT DEFAULT 'PERSONAL',
        created_at TEXT NOT NULL
    )
    """)

    # Create users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT,
        role TEXT DEFAULT 'USER',
        account_id TEXT UNIQUE NOT NULL,
        tenant_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        last_login_at TEXT,
        email_verified INTEGER DEFAULT 0
    )
    """)

    # Ensure email_verified column exists if table already existed
    c.execute("PRAGMA table_info(users)")
    existing_cols = [row[1] for row in c.fetchall()]
    if "email_verified" not in existing_cols:
        try:
            c.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0")
        except Exception:
            pass

    # Create email_verifications table
    c.execute("""
    CREATE TABLE IF NOT EXISTS email_verifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        user_uuid TEXT NOT NULL,
        token TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        verified_at TEXT
    )
    """)

    # Indexes for fast letter-by-letter lookup and token validation
    c.execute("CREATE INDEX IF NOT EXISTS idx_users_lower_email ON users(lower(email))")
    c.execute("CREATE INDEX IF NOT EXISTS idx_verifications_token ON email_verifications(token)")
    # Create user_sessions table
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        user_uuid TEXT NOT NULL,
        account_id TEXT NOT NULL,
        username TEXT NOT NULL,
        device_type TEXT DEFAULT 'Desktop',
        os TEXT DEFAULT 'Unknown OS',
        browser TEXT DEFAULT 'Browser',
        user_agent TEXT,
        ip_address TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        last_active_at TEXT NOT NULL,
        logout_at TEXT,
        logout_reason TEXT
    )
    """)

    # Create session_audit_logs table
    c.execute("""
    CREATE TABLE IF NOT EXISTS session_audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE NOT NULL,
        session_id TEXT NOT NULL,
        user_uuid TEXT NOT NULL,
        account_id TEXT NOT NULL,
        username TEXT NOT NULL,
        event_type TEXT NOT NULL,
        device_info TEXT,
        ip_address TEXT,
        user_agent TEXT,
        status TEXT DEFAULT 'SUCCESS',
        details TEXT,
        timestamp TEXT NOT NULL
    )
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_uuid, is_active)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_sessions_account ON user_sessions(account_id, is_active)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_audit_user ON session_audit_logs(user_uuid, timestamp)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_audit_account ON session_audit_logs(account_id, timestamp)")

    # Check for admin user
    c.execute("SELECT id FROM users WHERE username = 'admin'")
    if not c.fetchone():
        if ENVIRONMENT == "production":
            logger.info("Production mode: default 'admin' account seeding is disabled.")
        else:
            admin_pw_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt(rounds=10)).decode()
            now = datetime.datetime.utcnow().isoformat()
            admin_acc_id = "109283746519"
            admin_tenant_id = "tenant-000000000001"
            c.execute("""
            INSERT OR IGNORE INTO tenants (id, name, account_id, tenant_type, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (admin_tenant_id, "Admin Workspace", admin_acc_id, "PERSONAL", now))

            c.execute("""
            INSERT OR REPLACE INTO users (uuid, username, email, password_hash, role, account_id, tenant_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "00000000-0000-0000-0000-000000000001",
                "admin",
                "admin@aetherops.local",
                admin_pw_hash,
                "ADMIN",
                admin_acc_id,
                admin_tenant_id,
                now
            ))

    # Check for standard user
    c.execute("SELECT id FROM users WHERE username = 'user'")
    if not c.fetchone():
        if ENVIRONMENT == "production":
            logger.info("Production mode: default 'user' account seeding is disabled.")
        else:
            user_pw_hash = bcrypt.hashpw(b"user123", bcrypt.gensalt(rounds=10)).decode()
            now = datetime.datetime.utcnow().isoformat()
            user_acc_id = "987654321098"
            user_tenant_id = "tenant-000000000002"
            c.execute("""
            INSERT OR IGNORE INTO tenants (id, name, account_id, tenant_type, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (user_tenant_id, "User Workspace", user_acc_id, "PERSONAL", now))

            c.execute("""
            INSERT OR REPLACE INTO users (uuid, username, email, password_hash, role, account_id, tenant_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "00000000-0000-0000-0000-000000000002",
                "user",
                "user@aetherops.local",
                user_pw_hash,
                "USER",
                user_acc_id,
                user_tenant_id,
                now
            ))
    c.execute("UPDATE users SET email_verified = 1 WHERE username IN ('admin', 'user') OR email_verified IS NULL")

    conn.commit()
    conn.close()
    logger.info("Auth Database initialized with default AWS-style accounts.")


init_db()


def generate_unique_account_id(cursor) -> str:
    """Generates a random 12-digit AWS-style Account ID not yet assigned."""
    while True:
        acc_id = str(secrets.randbelow(900000000000) + 100000000000)
        cursor.execute("SELECT 1 FROM users WHERE account_id = ?", (acc_id,))
        if not cursor.fetchone():
            return acc_id


def generate_unique_tenant_id() -> str:
    """Generates a hidden internal Tenant ID."""
    return f"tenant-{secrets.token_hex(8)}"


def format_account_id(acc_id: Optional[str]) -> str:
    """Formats 12-digit account ID as XXXX-XXXX-XXXX."""
    if not acc_id:
        return ""
    digits = "".join(filter(str.isdigit, str(acc_id)))
    if len(digits) == 12:
        return f"{digits[0:4]}-{digits[4:8]}-{digits[8:12]}"
    return acc_id


def find_user_by_login_id(cursor, login_id: str):
    """
    Finds a user by Username, Email, or 12-digit Account ID (with or without hyphens).
    """
    cleaned = login_id.strip()
    digits_only = "".join(filter(str.isdigit, cleaned))
    
    cursor.execute("""
    SELECT * FROM users
    WHERE lower(username) = lower(?)
       OR lower(email) = lower(?)
       OR account_id = ?
       OR (account_id = ? AND length(?) = 12)
    LIMIT 1
    """, (cleaned, cleaned, cleaned, digits_only, digits_only))
    return cursor.fetchone()


def _verify_password(plain_password: str, stored_hash: Optional[str]) -> bool:
    if not stored_hash:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode(), stored_hash.encode())
    except Exception:
        return False


def parse_user_agent(ua: str) -> Dict[str, str]:
    if not ua:
        return {"device_type": "Desktop", "os": "Unknown OS", "browser": "Browser", "label": "Desktop · Unknown · Browser"}
    ua_lower = ua.lower()

    # Device type
    if any(m in ua_lower for m in ("mobile", "android", "iphone", "ipod", "phone")):
        device_type = "Mobile"
    elif any(t in ua_lower for t in ("ipad", "tablet", "kindle")):
        device_type = "Tablet"
    else:
        device_type = "Desktop"

    # OS
    if "android" in ua_lower:
        os_name = "Android"
    elif "iphone" in ua_lower or "ipad" in ua_lower or "ios" in ua_lower:
        os_name = "iOS"
    elif "macintosh" in ua_lower or "mac os" in ua_lower:
        os_name = "macOS"
    elif "windows" in ua_lower:
        os_name = "Windows"
    elif "linux" in ua_lower or "x11" in ua_lower:
        os_name = "Linux"
    elif "cros" in ua_lower:
        os_name = "Chrome OS"
    else:
        os_name = "Desktop OS"

    # Browser
    if "edg" in ua_lower or "edge" in ua_lower:
        browser = "Microsoft Edge"
    elif "chrome" in ua_lower or "crios" in ua_lower:
        browser = "Chrome"
    elif "firefox" in ua_lower or "fxios" in ua_lower:
        browser = "Firefox"
    elif "safari" in ua_lower and "chrome" not in ua_lower:
        browser = "Safari"
    elif "opera" in ua_lower or "opr" in ua_lower:
        browser = "Opera"
    else:
        browser = "Web Browser"

    return {
        "device_type": device_type,
        "os": os_name,
        "browser": browser,
        "label": f"{device_type} · {os_name} · {browser}"
    }


def extract_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


def record_session_login(
    conn,
    user: Dict[str, Any],
    session_id: str,
    request: Request,
    auth_method: str = "PASSWORD"
) -> Dict[str, Any]:
    c = conn.cursor()
    ua_str = request.headers.get("user-agent", "")
    ua_info = parse_user_agent(ua_str)
    client_ip = extract_client_ip(request)
    now_iso = datetime.datetime.utcnow().isoformat()

    c.execute("""
    INSERT INTO user_sessions (
        session_id, user_uuid, account_id, username,
        device_type, os, browser, user_agent, ip_address,
        is_active, created_at, last_active_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
    """, (
        session_id, user["uuid"], user["account_id"], user["username"],
        ua_info["device_type"], ua_info["os"], ua_info["browser"],
        ua_str[:255], client_ip, now_iso, now_iso
    ))

    evt_id = f"evt_{secrets.token_hex(12)}"
    details = f"Logged in via {auth_method} on {ua_info['label']} from IP {client_ip}"
    c.execute("""
    INSERT INTO session_audit_logs (
        event_id, session_id, user_uuid, account_id, username,
        event_type, device_info, ip_address, user_agent, status, details, timestamp
    ) VALUES (?, ?, ?, ?, ?, 'LOGIN', ?, ?, ?, 'SUCCESS', ?, ?)
    """, (
        evt_id, session_id, user["uuid"], user["account_id"], user["username"],
        ua_info["label"], client_ip, ua_str[:255], details, now_iso
    ))
    return {
        "session_id": session_id,
        "device_info": ua_info["label"],
        "ip_address": client_ip,
        "login_at": now_iso
    }


def _create_jwt_token(
    username: str,
    role: str,
    email: str,
    user_uuid: str,
    account_id: str,
    tenant_id: str,
    hours: int = JWT_EXPIRATION_HOURS,
    session_id: Optional[str] = None,
) -> str:
    now = datetime.datetime.utcnow()
    sid = session_id or f"sess_{secrets.token_hex(12)}"
    payload = {
        "sub": username,
        "uuid": user_uuid,
        "role": role,
        "email": email,
        "account_id": account_id,
        "tenant_id": tenant_id,
        "sid": sid,
        "iat": now,
        "exp": now + datetime.timedelta(hours=hours),
        "jti": secrets.token_hex(16),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def _decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


class LoginRequest(BaseModel):
    username: str  # Can be username, email, or 12-digit Account ID
    password: str
    remember_me: bool = False


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "USER"


class ProfileUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None


class VerifyTenantRequest(BaseModel):
    account_id: str
    tenant_id: str


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: str


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "auth", "port": 7999, "timestamp": time.time()}


@app.post("/api/v1/auth/login")
async def login(req: LoginRequest, request: Request):
    """
    Login endpoint:
    Accepts Username, Email, OR 12-digit Account ID as login identifier.
    Returns JWT with account_id and tenant_id, plus showcases account_id.
    Records active session and audit history.
    """
    conn = get_db_connection()
    try:
        c = conn.cursor()
        user = find_user_by_login_id(c, req.username)

        if not user or not _verify_password(req.password, user["password_hash"]):
            client_ip = extract_client_ip(request)
            ua_info = parse_user_agent(request.headers.get("user-agent", ""))
            now_iso = datetime.datetime.utcnow().isoformat()
            try:
                c.execute("""
                INSERT INTO session_audit_logs (
                    event_id, session_id, user_uuid, account_id, username,
                    event_type, device_info, ip_address, user_agent, status, details, timestamp
                ) VALUES (?, 'none', 'unknown', 'unknown', ?, 'LOGIN_FAILED', ?, ?, ?, 'FAILED', 'Failed login attempt: invalid credentials', ?)
                """, (
                    f"evt_{secrets.token_hex(12)}", req.username[:50],
                    ua_info["label"], client_ip, request.headers.get("user-agent", "")[:255], now_iso
                ))
                conn.commit()
            except Exception:
                pass
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid Login ID or password. Enter Username, Email, or 12-digit Account ID."}
            )

        if "email_verified" in user.keys() and user["email_verified"] == 0:
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Email address not confirmed. Please check your inbox or request a new verification link.",
                    "email_unverified": True,
                    "email": user["email"]
                }
            )

        # Update last login
        now_iso = datetime.datetime.utcnow().isoformat()
        c.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (now_iso, user["id"]))

        hours = 168 if req.remember_me else JWT_EXPIRATION_HOURS
        session_id = f"sess_{secrets.token_hex(12)}"
        token = _create_jwt_token(
            username=user["username"],
            role=user["role"],
            email=user["email"],
            user_uuid=user["uuid"],
            account_id=user["account_id"],
            tenant_id=user["tenant_id"],
            hours=hours,
            session_id=session_id,
        )

        # Record active device session & audit log
        record_session_login(conn, user, session_id, request, auth_method="CREDENTIALS")
        conn.commit()

        resp_user = {
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "uuid": user["uuid"],
            "account_id": user["account_id"],
            "account_id_formatted": format_account_id(user["account_id"]),
        }
        return {
            "token": token,
            "user": resp_user,
            "session_id": session_id,
            "redirect_url": "http://localhost:8000"
        }
    finally:
        conn.close()


def _send_verification_email(recipient_email: str, username: str, token: str) -> str:
    verification_url = f"http://localhost:8000/?verify_token={token}"
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", "no-reply@aetherops.cloud")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px; color: #0f172a; }}
    .card {{ max-width: 520px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 36px 32px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
    .logo-bar {{ text-align: center; margin-bottom: 24px; }}
    .badge {{ display: inline-block; padding: 4px 12px; font-size: 11px; font-weight: 700; color: #0284c7; background: #e0f2fe; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.05em; }}
    h1 {{ font-size: 20px; font-weight: 800; color: #0f172a; margin-top: 16px; margin-bottom: 12px; }}
    p {{ font-size: 14px; line-height: 1.6; color: #475569; margin: 8px 0; }}
    .btn-wrap {{ text-align: center; margin: 28px 0; }}
    .btn {{ display: inline-block; padding: 12px 32px; background: linear-gradient(135deg, #2563eb, #06b6d4); color: #ffffff !important; text-decoration: none; font-size: 14px; font-weight: 700; border-radius: 10px; box-shadow: 0 4px 12px rgba(37,99,235,0.25); }}
    .url-box {{ background: #f1f5f9; padding: 12px; border-radius: 8px; word-break: break-all; font-family: monospace; font-size: 12px; color: #334155; margin-top: 20px; }}
    .footer {{ font-size: 11px; color: #94a3b8; text-align: center; margin-top: 32px; border-top: 1px solid #f1f5f9; padding-top: 16px; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="logo-bar">
      <span class="badge">AetherOps Cloud</span>
      <h1>Confirm Your Email Address</h1>
    </div>
    <p>Hello <strong>{username}</strong>,</p>
    <p>Thank you for registering with AetherOps. Please verify your email address to activate your account and access your cloud workspace.</p>
    <div class="btn-wrap">
      <a href="{verification_url}" class="btn" target="_blank">Verify Email &amp; Launch Console</a>
    </div>
    <p>Or paste this link into your browser:</p>
    <div class="url-box">{verification_url}</div>
    <p style="font-size: 12px; color: #64748b; margin-top: 20px;">This link will expire in 24 hours.</p>
    <div class="footer">&copy; AetherOps Autonomous Cloud Engineering. All rights reserved.</div>
  </div>
</body>
</html>"""

    if smtp_host:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Verify your email - AetherOps Cloud"
            msg["From"] = smtp_from
            msg["To"] = recipient_email
            msg.attach(MIMEText(f"Verify your email: {verification_url}", "plain"))
            msg.attach(MIMEText(html_content, "html"))
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                if smtp_port in (587, 25):
                    server.starttls()
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_from, [recipient_email], msg.as_string())
            logger.info(f"Verification email dispatched to {recipient_email} via SMTP")
        except Exception as e:
            logger.warning(f"SMTP dispatch to {recipient_email} failed: {e}")

    try:
        with open("/tmp/aether-email-confirmations.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.utcnow().isoformat()}] TO: {recipient_email} | USER: {username} | LINK: {verification_url}\n")
    except Exception:
        pass

    return verification_url


@app.get("/api/v1/auth/check-email")
async def check_email(email: str = ""):
    """Live letter-by-letter check using indexed SQLite lookup."""
    clean = email.strip().lower()
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT 1 FROM users WHERE lower(email) = lower(?) LIMIT 1", (clean,))
        exists = bool(c.fetchone())
        return {"exists": exists, "valid": True, "email": clean}
    finally:
        conn.close()


@app.post("/api/v1/auth/register")
async def register(req: RegisterRequest):
    """
    Registration endpoint:
    Creates a new user with unverified email, generates secure confirmation token,
    and dispatches confirmation email.
    """
    clean_username = req.username.strip().replace(" ", "_")
    clean_email = req.email.strip().lower()
    conn = get_db_connection()
    try:
        c = conn.cursor()

        c.execute("SELECT id FROM users WHERE lower(username) = lower(?)", (clean_username,))
        if c.fetchone():
            return JSONResponse(status_code=400, content={"detail": "Username already exists."})

        c.execute("SELECT id FROM users WHERE lower(email) = lower(?)", (clean_email,))
        if c.fetchone():
            return JSONResponse(status_code=400, content={"detail": "Email already registered."})

        user_uuid = str(uuid.uuid4())
        account_id = generate_unique_account_id(c)
        tenant_id = generate_unique_tenant_id()
        pw_hash = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt(rounds=10)).decode()
        now_iso = datetime.datetime.utcnow().isoformat()

        # Create personal tenant
        c.execute("""
        INSERT INTO tenants (id, name, account_id, tenant_type, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, (tenant_id, f"{clean_username}'s Workspace", account_id, "PERSONAL", now_iso))

        # Create user record with email_verified = 0
        c.execute("""
        INSERT INTO users (uuid, username, email, password_hash, role, account_id, tenant_id, created_at, last_login_at, email_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (user_uuid, clean_username, clean_email, pw_hash, req.role, account_id, tenant_id, now_iso, now_iso))

        # Create verification token valid for 24h
        verif_token = secrets.token_urlsafe(32)
        expires_at = (datetime.datetime.utcnow() + datetime.timedelta(hours=24)).isoformat()
        c.execute("""
        INSERT INTO email_verifications (email, user_uuid, token, created_at, expires_at)
        VALUES (?, ?, ?, ?, ?)
        """, (clean_email, user_uuid, verif_token, now_iso, expires_at))

        conn.commit()

        verification_url = _send_verification_email(clean_email, clean_username, verif_token)

        return {
            "status": "VERIFICATION_SENT",
            "requires_verification": True,
            "message": f"Verification email sent to {clean_email}. Please confirm your email to activate your account.",
            "email": clean_email,
            "username": clean_username,
            "verification_url": verification_url,
        }
    finally:
        conn.close()


@app.post("/api/v1/auth/verify-email")
async def verify_email(req: VerifyEmailRequest):
    """Validates confirmation token, marks user email verified, and issues active session."""
    token = req.token.strip()
    if not token:
        return JSONResponse(status_code=400, content={"detail": "Verification token is required."})

    conn = get_db_connection()
    try:
        c = conn.cursor()

        c.execute("SELECT * FROM email_verifications WHERE token = ?", (token,))
        verif = c.fetchone()
        if not verif:
            return JSONResponse(status_code=400, content={"detail": "Invalid or expired confirmation link."})

        now_iso = datetime.datetime.utcnow().isoformat()
        if verif["expires_at"] < now_iso:
            return JSONResponse(status_code=400, content={"detail": "Confirmation link has expired. Please request a new one."})

        c.execute("SELECT * FROM users WHERE uuid = ?", (verif["user_uuid"],))
        user = c.fetchone()
        if not user:
            return JSONResponse(status_code=400, content={"detail": "Associated user account was not found."})

        c.execute("UPDATE email_verifications SET verified_at = ? WHERE id = ?", (now_iso, verif["id"]))
        c.execute("UPDATE users SET email_verified = 1 WHERE id = ?", (user["id"],))
        conn.commit()

        jwt_token = _create_jwt_token(
            username=user["username"],
            role=user["role"],
            email=user["email"],
            user_uuid=user["uuid"],
            account_id=user["account_id"],
            tenant_id=user["tenant_id"],
        )

        resp_user = {
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "uuid": user["uuid"],
            "account_id": user["account_id"],
            "account_id_formatted": format_account_id(user["account_id"]),
        }
        return {
            "status": "VERIFIED",
            "message": "Email confirmed successfully! Welcome to AetherOps.",
            "token": jwt_token,
            "user": resp_user,
            "redirect_url": "http://localhost:8000"
        }
    finally:
        conn.close()


@app.post("/api/v1/auth/resend-verification")
async def resend_verification(req: ResendVerificationRequest):
    """Resends activation email for unverified account."""
    clean_email = req.email.strip().lower()
    if not clean_email:
        return JSONResponse(status_code=400, content={"detail": "Email address is required."})

    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE lower(email) = lower(?)", (clean_email,))
        user = c.fetchone()
        if not user:
            return JSONResponse(status_code=404, content={"detail": "No registered account found with that email."})

        if user["email_verified"] == 1:
            return {"status": "ALREADY_VERIFIED", "message": "Email is already confirmed. You can sign in immediately."}

        now_iso = datetime.datetime.utcnow().isoformat()
        verif_token = secrets.token_urlsafe(32)
        expires_at = (datetime.datetime.utcnow() + datetime.timedelta(hours=24)).isoformat()
        c.execute("""
        INSERT INTO email_verifications (email, user_uuid, token, created_at, expires_at)
        VALUES (?, ?, ?, ?, ?)
        """, (clean_email, user["uuid"], verif_token, now_iso, expires_at))
        conn.commit()

        verification_url = _send_verification_email(clean_email, user["username"], verif_token)
        return {
            "status": "SENT",
            "message": f"Verification email sent to {clean_email}.",
            "verification_url": verification_url,
        }
    finally:
        conn.close()

def _get_request_auth_payload(request: Request) -> Optional[Dict[str, Any]]:
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[7:].strip() if auth_header.startswith("Bearer ") else ""
    if token:
        payload = _decode_jwt_token(token)
        if payload:
            return payload
    x_admin_key = request.headers.get("X-Admin-Key", "")
    if x_admin_key:
        configured_admin_key = os.getenv("ADMIN_API_KEY", "aetherops-secret-admin-key")
        if ENVIRONMENT == "production" and (not configured_admin_key or configured_admin_key == "aetherops-secret-admin-key"):
            return None
        if secrets.compare_digest(x_admin_key.strip(), configured_admin_key):
            return {
                "sub": "admin",
                "role": "ADMIN",
                "account_id": "109283746519",
                "tenant_id": "tenant-000000000001",
                "uuid": "00000000-0000-0000-0000-000000000001",
                "email": "admin@aetherops.local",
            }
    return None


@app.get("/api/v1/auth/me")
async def get_me(request: Request):
    """Returns authenticated user profile showcasing AWS Account ID."""
    payload = _get_request_auth_payload(request)
    if not payload:
        return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

    username = payload.get("sub", "")
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE lower(username) = lower(?)", (username,))
        user = c.fetchone()
    finally:
        conn.close()

    if user:
        return {
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "uuid": user["uuid"],
            "account_id": user["account_id"],
            "account_id_formatted": format_account_id(user["account_id"]),
        }

    return {
        "username": username,
        "email": payload.get("email", f"{username}@aetherops.local"),
        "role": payload.get("role", "USER"),
        "uuid": payload.get("uuid", ""),
        "account_id": payload.get("account_id", "109283746519"),
        "account_id_formatted": format_account_id(payload.get("account_id", "109283746519")),
    }


@app.post("/api/v1/auth/verify-tenant")
async def verify_tenant_access(req: VerifyTenantRequest, request: Request):
    """
    Validates that the provided account_id and hidden tenant_id match
    the authenticated session before allowing sensitive actions or data queries.
    """
    payload = _get_request_auth_payload(request)
    if not payload:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized: Session token missing or invalid."})

    token_account = payload.get("account_id")
    token_tenant = payload.get("tenant_id")

    if req.account_id != token_account or req.tenant_id != token_tenant:
        logger.warning(
            f"Tenant verification mismatch: req account={req.account_id}, tenant={req.tenant_id} "
            f"vs token account={token_account}, tenant={token_tenant}"
        )
        return JSONResponse(
            status_code=403,
            content={"detail": "Tenant isolation violation: Account ID and Tenant ID verification failed."}
        )

    return {"status": "authorized", "account_id": token_account, "tenant_id": token_tenant}


@app.put("/api/v1/auth/profile")
@app.patch("/api/v1/auth/profile")
async def update_profile(req: ProfileUpdateRequest, request: Request):
    payload = _get_request_auth_payload(request)
    if not payload:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    username = payload.get("sub", "")
    conn = get_db_connection()
    try:
        c = conn.cursor()

        if req.username and req.username.strip() != username:
            new_username = req.username.strip().replace(" ", "_")
            c.execute("SELECT id FROM users WHERE lower(username) = lower(?)", (new_username,))
            if c.fetchone():
                return JSONResponse(status_code=400, content={"detail": f"Username '{new_username}' is already taken."})
            
            c.execute("UPDATE users SET username = ? WHERE lower(username) = lower(?)", (new_username, username))
            username = new_username

        if req.email and req.email.strip():
            c.execute("UPDATE users SET email = ? WHERE lower(username) = lower(?)", (req.email.strip().lower(), username))

        conn.commit()
        c.execute("SELECT * FROM users WHERE lower(username) = lower(?)", (username,))
        user = c.fetchone()
        if not user:
            return JSONResponse(status_code=404, content={"detail": "User not found"})
    except sqlite3.IntegrityError as ie:
        conn.rollback()
        return JSONResponse(status_code=400, content={"detail": f"Database integrity error: Username or email already exists ({ie})"})
    except Exception as e:
        conn.rollback()
        return JSONResponse(status_code=500, content={"detail": f"Profile update failed: {str(e)}"})
    finally:
        conn.close()

    new_token = _create_jwt_token(
        username=user["username"],
        role=user["role"],
        email=user["email"],
        user_uuid=user["uuid"],
        account_id=user["account_id"],
        tenant_id=user["tenant_id"],
    )

    return {
        "status": "ok",
        "token": new_token,
        "username": user["username"],
        "email": user["email"],
        "user": {
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "uuid": user["uuid"],
            "account_id": user["account_id"],
            "account_id_formatted": format_account_id(user["account_id"]),
        }
    }

@app.post("/api/v1/auth/logout")
async def logout(request: Request):
    """Terminates active session, records logout timestamp and audit trail."""
    payload = _get_request_auth_payload(request)
    now_iso = datetime.datetime.utcnow().isoformat()
    if payload:
        sid = payload.get("sid")
        user_uuid = payload.get("uuid")
        account_id = payload.get("account_id")
        username = payload.get("sub", "")
        conn = get_db_connection()
        try:
            c = conn.cursor()
            client_ip = extract_client_ip(request)
            ua_info = parse_user_agent(request.headers.get("user-agent", ""))
            if sid:
                c.execute("""
                UPDATE user_sessions
                SET is_active = 0, logout_at = ?, logout_reason = 'USER_LOGOUT'
                WHERE session_id = ?
                """, (now_iso, sid))
            else:
                c.execute("""
                UPDATE user_sessions
                SET is_active = 0, logout_at = ?, logout_reason = 'USER_LOGOUT'
                WHERE (user_uuid = ? OR account_id = ?) AND is_active = 1
                ORDER BY last_active_at DESC LIMIT 1
                """, (now_iso, user_uuid, account_id))

            evt_id = f"evt_{secrets.token_hex(12)}"
            c.execute("""
            INSERT INTO session_audit_logs (
                event_id, session_id, user_uuid, account_id, username,
                event_type, device_info, ip_address, user_agent, status, details, timestamp
            ) VALUES (?, ?, ?, ?, ?, 'LOGOUT', ?, ?, ?, 'SUCCESS', ?, ?)
            """, (
                evt_id, sid or "unknown", user_uuid or "", account_id or "", username,
                ua_info["label"], client_ip, request.headers.get("user-agent", "")[:255],
                f"User logged out from {ua_info['label']}", now_iso
            ))
            conn.commit()
        finally:
            conn.close()
    return {"status": "ok", "message": "Successfully logged out"}


@app.get("/api/v1/auth/sessions")
async def get_user_sessions(request: Request):
    """
    Returns all active and past login sessions for the authenticated account,
    including device type, OS, browser, IP address, and recent audit log history.
    """
    payload = _get_request_auth_payload(request)
    if not payload:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized: Session token missing or invalid."})

    user_uuid = payload.get("uuid")
    account_id = payload.get("account_id")
    username = payload.get("sub", "user")
    current_sid = payload.get("sid")
    now_iso = datetime.datetime.utcnow().isoformat()
    client_ip = extract_client_ip(request)
    ua_str = request.headers.get("user-agent", "")
    ua_info = parse_user_agent(ua_str)

    conn = get_db_connection()
    try:
        c = conn.cursor()

        # Ensure current session exists in user_sessions table
        if current_sid:
            c.execute("SELECT id FROM user_sessions WHERE session_id = ?", (current_sid,))
            if not c.fetchone():
                c.execute("""
                INSERT INTO user_sessions (
                    session_id, user_uuid, account_id, username,
                    device_type, os, browser, user_agent, ip_address,
                    is_active, created_at, last_active_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """, (
                    current_sid, user_uuid or "0", account_id or "0", username,
                    ua_info["device_type"], ua_info["os"], ua_info["browser"],
                    ua_str[:255], client_ip, now_iso, now_iso
                ))
                c.execute("""
                INSERT INTO session_audit_logs (
                    event_id, session_id, user_uuid, account_id, username,
                    event_type, device_info, ip_address, user_agent, status, details, timestamp
                ) VALUES (?, ?, ?, ?, ?, 'LOGIN', ?, ?, ?, 'SUCCESS', ?, ?)
                """, (
                    f"evt_{secrets.token_hex(12)}", current_sid, user_uuid or "0", account_id or "0", username,
                    ua_info["label"], client_ip, ua_str[:255], f"Active device connected: {ua_info['label']}", now_iso
                ))
                conn.commit()
            else:
                # Update heartbeat timestamp & IP
                c.execute("UPDATE user_sessions SET last_active_at = ?, ip_address = ? WHERE session_id = ?", (now_iso, client_ip, current_sid))
                conn.commit()

        # Fetch all sessions for this user/account
        c.execute("""
        SELECT * FROM user_sessions
        WHERE account_id = ? OR user_uuid = ?
        ORDER BY is_active DESC, last_active_at DESC
        """, (account_id, user_uuid))
        rows = c.fetchall()

        active_sessions = []
        past_sessions = []

        for row in rows:
            sid = row["session_id"]
            is_current = bool(current_sid and sid == current_sid)
            s_dict = {
                "session_id": sid,
                "device_type": row["device_type"],
                "os": row["os"],
                "browser": row["browser"],
                "device_info": f"{row['device_type']} · {row['os']} · {row['browser']}",
                "ip_address": row["ip_address"] or "127.0.0.1",
                "is_active": bool(row["is_active"]),
                "is_current": is_current,
                "created_at": row["created_at"],
                "last_active_at": row["last_active_at"],
                "logout_at": row["logout_at"],
                "logout_reason": row["logout_reason"],
            }
            if row["is_active"]:
                active_sessions.append(s_dict)
            else:
                past_sessions.append(s_dict)

        # Fetch recent 30 audit logs
        c.execute("""
        SELECT * FROM session_audit_logs
        WHERE account_id = ? OR user_uuid = ?
        ORDER BY id DESC LIMIT 30
        """, (account_id, user_uuid))
        audit_rows = c.fetchall()
        audit_logs = [
            {
                "id": r["id"],
                "event_id": r["event_id"],
                "session_id": r["session_id"],
                "event_type": r["event_type"],
                "device_info": r["device_info"],
                "ip_address": r["ip_address"],
                "status": r["status"],
                "details": r["details"],
                "timestamp": r["timestamp"],
            }
            for r in audit_rows
        ]

        return {
            "status": "SUCCESS",
            "active_count": len(active_sessions),
            "past_count": len(past_sessions),
            "current_session_id": current_sid,
            "active_sessions": active_sessions,
            "past_sessions": past_sessions[:15],
            "audit_logs": audit_logs,
        }
    finally:
        conn.close()


@app.post("/api/v1/auth/sessions/{session_id}/revoke")
async def revoke_session(session_id: str, request: Request):
    """Terminates an active session from another device."""
    payload = _get_request_auth_payload(request)
    if not payload:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    user_uuid = payload.get("uuid")
    account_id = payload.get("account_id")
    username = payload.get("sub", "")
    now_iso = datetime.datetime.utcnow().isoformat()
    client_ip = extract_client_ip(request)
    ua_info = parse_user_agent(request.headers.get("user-agent", ""))

    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("""
        SELECT * FROM user_sessions
        WHERE session_id = ? AND (account_id = ? OR user_uuid = ?)
        """, (session_id, account_id, user_uuid))
        sess = c.fetchone()
        if not sess:
            return JSONResponse(status_code=404, content={"detail": "Session not found or not owned by caller."})

        c.execute("""
        UPDATE user_sessions
        SET is_active = 0, logout_at = ?, logout_reason = 'REMOTE_REVOKE'
        WHERE session_id = ?
        """, (now_iso, session_id))

        c.execute("""
        INSERT INTO session_audit_logs (
            event_id, session_id, user_uuid, account_id, username,
            event_type, device_info, ip_address, user_agent, status, details, timestamp
        ) VALUES (?, ?, ?, ?, ?, 'SESSION_REVOKED', ?, ?, ?, 'REVOKED', ?, ?)
        """, (
            f"evt_{secrets.token_hex(12)}", session_id, user_uuid or "", account_id or "", username,
            f"{sess['device_type']} · {sess['os']} · {sess['browser']}", client_ip,
            request.headers.get("user-agent", "")[:255],
            f"Device session terminated remotely by user from {ua_info['label']}", now_iso
        ))
        conn.commit()
        return {"status": "SUCCESS", "message": "Device session successfully logged out."}
    finally:
        conn.close()


@app.post("/api/v1/auth/sessions/revoke-others")
async def revoke_other_sessions(request: Request):
    """Logs out all active sessions except the current one."""
    payload = _get_request_auth_payload(request)
    if not payload:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    user_uuid = payload.get("uuid")
    account_id = payload.get("account_id")
    username = payload.get("sub", "")
    current_sid = payload.get("sid")
    now_iso = datetime.datetime.utcnow().isoformat()
    client_ip = extract_client_ip(request)
    ua_info = parse_user_agent(request.headers.get("user-agent", ""))

    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("""
        SELECT session_id, device_type, os, browser FROM user_sessions
        WHERE (account_id = ? OR user_uuid = ?) AND session_id != ? AND is_active = 1
        """, (account_id, user_uuid, current_sid or ""))
        other_sessions = c.fetchall()

        c.execute("""
        UPDATE user_sessions
        SET is_active = 0, logout_at = ?, logout_reason = 'REVOKE_ALL_OTHERS'
        WHERE (account_id = ? OR user_uuid = ?) AND session_id != ? AND is_active = 1
        """, (now_iso, account_id, user_uuid, current_sid or ""))

        for s in other_sessions:
            c.execute("""
            INSERT INTO session_audit_logs (
                event_id, session_id, user_uuid, account_id, username,
                event_type, device_info, ip_address, user_agent, status, details, timestamp
            ) VALUES (?, ?, ?, ?, ?, 'SESSION_REVOKED', ?, ?, ?, 'REVOKED', ?, ?)
            """, (
                f"evt_{secrets.token_hex(12)}", s["session_id"], user_uuid or "", account_id or "", username,
                f"{s['device_type']} · {s['os']} · {s['browser']}", client_ip,
                request.headers.get("user-agent", "")[:255],
                f"Session terminated during bulk logout from {ua_info['label']}", now_iso
            ))

        conn.commit()
        return {"status": "SUCCESS", "revoked_count": len(other_sessions), "message": f"Successfully logged out {len(other_sessions)} other device(s)."}
    finally:
        conn.close()


@app.get("/api/v1/auth/sessions/audit")
async def get_session_audit_logs(request: Request):
    """Returns full login session audit log history."""
    payload = _get_request_auth_payload(request)
    if not payload:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    user_uuid = payload.get("uuid")
    account_id = payload.get("account_id")

    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("""
        SELECT * FROM session_audit_logs
        WHERE account_id = ? OR user_uuid = ?
        ORDER BY id DESC LIMIT 100
        """, (account_id, user_uuid))
        rows = c.fetchall()
        return {
            "status": "SUCCESS",
            "audit_logs": [
                {
                    "id": r["id"],
                    "event_id": r["event_id"],
                    "session_id": r["session_id"],
                    "event_type": r["event_type"],
                    "device_info": r["device_info"],
                    "ip_address": r["ip_address"],
                    "status": r["status"],
                    "details": r["details"],
                    "timestamp": r["timestamp"],
                }
                for r in rows
            ]
        }
    finally:
        conn.close()

# ═══════════════════════════════════════════════════════════════════════════════
# OAuth Initiation & Callback Flow (Google & GitHub)
# ═══════════════════════════════════════════════════════════════════════════════

def _oauth_success_html(provider: str, token: str, user: Dict[str, Any]) -> str:
    """Renders light-themed OAuth authorization completion page with postMessage handshake."""
    u_name = user["username"]
    u_email = user["email"]
    u_role = user["role"]
    u_account = user["account_id"]
    u_uuid = user["uuid"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{provider} Verified — AetherOps</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f8fafc;
      color: #0f172a;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
    }}
    .card {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 1rem;
      padding: 2.5rem;
      box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.08);
      text-align: center;
      max-width: 400px;
      width: 90%;
    }}
    .icon {{
      width: 48px;
      height: 48px;
      background: #10b981;
      color: #ffffff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 1.25rem auto;
      font-size: 24px;
      font-weight: bold;
    }}
    h3 {{ margin: 0 0 0.5rem 0; font-size: 1.25rem; font-weight: 700; color: #0f172a; }}
    p {{ margin: 0 0 1.25rem 0; font-size: 0.875rem; color: #64748b; }}
    .badge {{
      display: inline-block;
      background: #fef3c7;
      color: #92400e;
      padding: 0.25rem 0.75rem;
      border-radius: 0.5rem;
      font-family: monospace;
      font-weight: 600;
      font-size: 0.85rem;
      margin-bottom: 1.25rem;
      border: 1px solid #fde68a;
    }}
    .spinner {{
      display: inline-block;
      width: 1rem;
      height: 1rem;
      border: 2px solid #cbd5e1;
      border-top-color: #d97706;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      vertical-align: middle;
      margin-right: 0.5rem;
    }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">✓</div>
    <h3>{provider} Verified</h3>
    <p>Logged in as <strong>{u_email}</strong></p>
    <div class="badge">AWS Account: {format_account_id(u_account)}</div>
    <div><span class="spinner"></span><span style="font-size: 0.875rem; color: #64748b;">Redirecting to Dashboard...</span></div>
  </div>
  <script>
    const payload = {{
      type: '{provider.upper()}_OAUTH_SUCCESS',
      token: '{token}',
      user: {{
        username: '{u_name}',
        email: '{u_email}',
        role: '{u_role}',
        uuid: '{u_uuid}',
        account_id: '{u_account}',
        account_id_formatted: '{format_account_id(u_account)}'
      }}
    }};
    try {{
      localStorage.setItem('X-Admin-Key', '{token}');
      localStorage.setItem('aether_user', JSON.stringify(payload.user));
    }} catch(e) {{}}

    let targetOrigin = window.location.origin;
    try {{
      if (window.opener && window.opener.origin) {{
        const allowedOrigins = [window.location.origin, 'http://localhost:8000', 'http://127.0.0.1:8000'];
        if (allowedOrigins.includes(window.opener.origin)) {{
          targetOrigin = window.opener.origin;
        }}
      }}
    }} catch(e) {{}}

    if (window.opener && !window.opener.closed) {{
      window.opener.postMessage(payload, targetOrigin);
      setTimeout(() => window.close(), 500);
    }} else {{
      window.location.href = 'http://localhost:8000/';
    }}
  </script>
</body>
</html>"""


def _oauth_error_html(title: str, detail: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Authentication Error</title>
  <style>
    body {{ font-family: sans-serif; background: #f8fafc; color: #0f172a; text-align: center; padding: 4rem 1rem; }}
    .box {{ background: white; border: 1px solid #fecaca; border-radius: 1rem; padding: 2rem; max-width: 420px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
    h3 {{ color: #dc2626; margin-top: 0; }}
    p {{ color: #475569; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <div class="box">
    <h3>{title}</h3>
    <p>{detail}</p>
    <p><button onclick="window.close()" style="padding: 8px 16px; border-radius: 6px; background: #0f172a; color: white; border: none; cursor: pointer;">Close Window</button></p>
  </div>
</body>
</html>"""


_ACTIVE_OAUTH_STATES: Dict[str, float] = {}


def generate_oauth_state(prefix: str = "login") -> str:
    """
    Generates a cryptographically signed, timestamped OAuth state parameter.
    Immune to CSRF forgery and tracked in memory with a 15-minute TTL.
    """
    now = time.time()
    # Prune stale states (> 15 mins)
    stale = [k for k, exp in _ACTIVE_OAUTH_STATES.items() if now - exp > 900]
    for k in stale:
        _ACTIVE_OAUTH_STATES.pop(k, None)

    rnd = secrets.token_hex(16)
    ts = str(int(now))
    raw = f"{prefix}:{rnd}:{ts}"
    sig = hmac.new(JWT_SECRET_KEY.encode(), raw.encode(), hashlib.sha256).hexdigest()[:16]
    state = f"{raw}:{sig}"
    _ACTIVE_OAUTH_STATES[state] = now
    _ACTIVE_OAUTH_STATES[f"{prefix}:{rnd}"] = now
    return state


def verify_oauth_state(state: Optional[str], stored_cookie_state: Optional[str] = None) -> bool:
    """
    Validates OAuth state parameter via multiple defense-in-depth checks:
    1. Direct match with stored HttpOnly cookie.
    2. In-memory active OAuth token cache (< 15 mins).
    3. Server-side HMAC cryptographic signature verification.
    """
    if not state:
        return False

    # 1. Direct cookie match
    if stored_cookie_state and secrets.compare_digest(state, stored_cookie_state):
        return True

    # 2. In-memory active states
    if state in _ACTIVE_OAUTH_STATES:
        issued_at = _ACTIVE_OAUTH_STATES.pop(state, None)
        if issued_at and (time.time() - issued_at) < 900:
            return True

    parts = state.split(":")
    if len(parts) >= 2:
        short_key = f"{parts[0]}:{parts[1]}"
        if short_key in _ACTIVE_OAUTH_STATES:
            issued_at = _ACTIVE_OAUTH_STATES.pop(short_key, None)
            if issued_at and (time.time() - issued_at) < 900:
                return True

    # 3. HMAC signature check (fallback when cookies are partitioned or dropped across redirects)
    if len(parts) == 4:
        prefix, rnd, ts, sig = parts
        try:
            timestamp = int(ts)
            if abs(time.time() - timestamp) < 900:
                expected_raw = f"{prefix}:{rnd}:{ts}"
                expected_sig = hmac.new(JWT_SECRET_KEY.encode(), expected_raw.encode(), hashlib.sha256).hexdigest()[:16]
                if secrets.compare_digest(sig, expected_sig):
                    return True
        except (ValueError, TypeError):
            pass

    return False


@app.api_route("/api/v1/auth/google/login", methods=["GET", "HEAD"])
@app.api_route("/auth/google/login", methods=["GET", "HEAD"])
async def google_login(request: Request, redirect_uri: Optional[str] = None):
    """Initiates Google OAuth 2.0 flow with authorized redirect_uri."""
    cb = redirect_uri or GOOGLE_REDIRECT_URI
    state = generate_oauth_state("login")
    scope = "openid email profile"
    google_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={cb}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&prompt=select_account"
        f"&state={state}"
    )

    if "application/json" in request.headers.get("accept", ""):
        resp = JSONResponse({"url": google_url, "redirect": google_url})
    else:
        resp = RedirectResponse(google_url, status_code=307)
    resp.set_cookie("oauth_state_google", state, httponly=True, samesite="lax", max_age=600, path="/")
    return resp


@app.get("/api/v1/auth/google/callback")
@app.get("/auth/google/callback")
async def google_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None
):
    """Handles Google OAuth callback, creates or fetches user with 12-digit Account ID."""
    if error:
        return HTMLResponse(_oauth_error_html("Google OAuth Canceled", error), status_code=400)
    if not code:
        return HTMLResponse(_oauth_error_html("Google OAuth Error", "Missing authorization code from Google."), status_code=400)

    stored_state = request.cookies.get("oauth_state_google")
    if not verify_oauth_state(state, stored_state):
        return HTMLResponse(_oauth_error_html("OAuth Security Error", "Invalid or missing OAuth state parameter. Potential CSRF attack prevented."), status_code=400)

    cb = GOOGLE_REDIRECT_URI
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_res = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": cb,
                }
            )
            token_res.raise_for_status()
            token_data = token_res.json()
            access_token = token_data.get("access_token")

            user_res = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_res.raise_for_status()
            user_info = user_res.json()
    except Exception as e:
        logger.error(f"Google OAuth token exchange failed: {e}")
        return HTMLResponse(_oauth_error_html("Google Authentication Failed", str(e)), status_code=400)

    email = user_info.get("email", "").strip().lower()
    raw_name = user_info.get("name") or email.split("@")[0]
    username = raw_name.strip().replace(" ", "_").lower()

    conn = get_db_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE lower(email) = lower(?)", (email,))
    user = c.fetchone()

    now_iso = datetime.datetime.utcnow().isoformat()
    if not user:
        # Check username clash
        c.execute("SELECT id FROM users WHERE lower(username) = lower(?)", (username,))
        if c.fetchone():
            username = f"{username}_{secrets.randbelow(1000)}"

        user_uuid = str(uuid.uuid4())
        account_id = generate_unique_account_id(c)
        tenant_id = generate_unique_tenant_id()

        c.execute("""
        INSERT INTO tenants (id, name, account_id, tenant_type, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, (tenant_id, f"{username}'s Workspace", account_id, "PERSONAL", now_iso))

        c.execute("""
        INSERT INTO users (uuid, username, email, password_hash, role, account_id, tenant_id, created_at, last_login_at, email_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (user_uuid, username, email, "", "USER", account_id, tenant_id, now_iso, now_iso))
        conn.commit()

        c.execute("SELECT * FROM users WHERE uuid = ?", (user_uuid,))
        user = c.fetchone()
    else:
        c.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (now_iso, user["id"]))
        conn.commit()

    token = _create_jwt_token(
        username=user["username"],
        role=user["role"],
        email=user["email"],
        user_uuid=user["uuid"],
        account_id=user["account_id"],
        tenant_id=user["tenant_id"],
    )
    user_dict = dict(user)
    conn.close()

    resp = HTMLResponse(_oauth_success_html("Google", token, user_dict))
    resp.delete_cookie("oauth_state_google", path="/")
    return resp


@app.api_route("/api/v1/auth/github/login", methods=["GET", "HEAD"])
@app.api_route("/auth/github/login", methods=["GET", "HEAD"])
async def github_login(request: Request, redirect_uri: Optional[str] = None):
    """Initiates GitHub OAuth flow."""
    cb = redirect_uri or get_dynamic_callback_uri(request, "/api/v1/auth/github/callback")
    state = generate_oauth_state("login")
    scope = "user:email read:user"
    github_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={cb}"
        f"&scope={scope}"
        f"&state={state}"
    )

    if "application/json" in request.headers.get("accept", ""):
        resp = JSONResponse({"url": github_url, "redirect": github_url})
    else:
        resp = RedirectResponse(github_url, status_code=307)
    resp.set_cookie("oauth_state_github", state, httponly=True, samesite="lax", max_age=600, path="/")
    return resp


@app.get("/api/v1/auth/github/callback")
@app.get("/auth/github/callback")
async def github_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None
):
    """Handles GitHub OAuth callback, creates or fetches user with 12-digit Account ID."""
    if error:
        return HTMLResponse(_oauth_error_html("GitHub OAuth Canceled", error), status_code=400)
    if not code:
        return HTMLResponse(_oauth_error_html("GitHub OAuth Error", "Missing authorization code from GitHub."), status_code=400)

    stored_state = request.cookies.get("oauth_state_conn_github") or request.cookies.get("oauth_state_github")
    if not verify_oauth_state(state, stored_state):
        logger.warning(f"GitHub OAuth state validation failed. state={state}, cookies={list(request.cookies.keys())}")
        return HTMLResponse(_oauth_error_html("OAuth Security Error", "Invalid or missing OAuth state parameter. Potential CSRF attack prevented."), status_code=400)

    cb = get_dynamic_callback_uri(request, "/api/v1/auth/github/callback")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_res = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": cb,
                },
                headers={"Accept": "application/json"}
            )
            token_res.raise_for_status()
            token_data = token_res.json()
            access_token = token_data.get("access_token")

            user_res = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "AetherOps-Auth-Service"
                }
            )
            user_res.raise_for_status()
            gh_user = user_res.json()

            email = gh_user.get("email")
            if not email:
                # Fetch private emails
                emails_res = await client.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github.v3+json",
                        "User-Agent": "AetherOps-Auth-Service"
                    }
                )
                if emails_res.is_success:
                    emails = emails_res.json()
                    primary = next((e["email"] for e in emails if e.get("primary")), None)
                    email = primary or (emails[0]["email"] if emails else None)

            if not email:
                email = f"{gh_user.get('login')}@github.local"
    except Exception as e:
        logger.error(f"GitHub OAuth token exchange failed: {e}")
        return HTMLResponse(_oauth_error_html("GitHub Authentication Failed", str(e)), status_code=400)

    username = gh_user.get("login") or email.split("@")[0]
    username = username.strip().replace(" ", "_").lower()

    # If this was a Module 2 Connection flow (intent=connect), return connection success HTML
    if state and (state.startswith("connect") or state.startswith("repo")):
        resp = HTMLResponse(_github_connection_success_html(access_token, gh_user))
        resp.delete_cookie("oauth_state_conn_github", path="/")
        resp.delete_cookie("oauth_state_github", path="/")
        return resp

    conn = get_db_connection()
    try:
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE lower(email) = lower(?)", (email,))
        user = c.fetchone()

        now_iso = datetime.datetime.utcnow().isoformat()
        if not user:
            c.execute("SELECT id FROM users WHERE lower(username) = lower(?)", (username,))
            if c.fetchone():
                username = f"{username}_{secrets.randbelow(1000)}"

            user_uuid = str(uuid.uuid4())
            account_id = generate_unique_account_id(c)
            tenant_id = generate_unique_tenant_id()

            c.execute("""
            INSERT INTO tenants (id, name, account_id, tenant_type, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (tenant_id, f"{username}'s Workspace", account_id, "PERSONAL", now_iso))

            c.execute("""
            INSERT INTO users (uuid, username, email, password_hash, role, account_id, tenant_id, created_at, last_login_at, email_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (user_uuid, username, email, "", "USER", account_id, tenant_id, now_iso, now_iso))
            conn.commit()

            c.execute("SELECT * FROM users WHERE uuid = ?", (user_uuid,))
            user = c.fetchone()
        else:
            c.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (now_iso, user["id"]))
            conn.commit()

        token = _create_jwt_token(
            username=user["username"],
            role=user["role"],
            email=user["email"],
            user_uuid=user["uuid"],
            account_id=user["account_id"],
            tenant_id=user["tenant_id"],
        )
        user_dict = dict(user)
    finally:
        conn.close()

    resp = HTMLResponse(_oauth_success_html("GitHub", token, user_dict))
    resp.delete_cookie("oauth_state_github", path="/")
    resp.delete_cookie("oauth_state_conn_github", path="/")
    return resp


# ═══════════════════════════════════════════════════════════════════════════════
# Module 2 Developer Tooling: GitHub Repository & Cloud Connection OAuth
# ═══════════════════════════════════════════════════════════════════════════════

GITHUB_CONNECTION_REDIRECT_URI = os.getenv(
    "GITHUB_CONNECTION_REDIRECT_URI",
    GITHUB_OAUTH_REDIRECT_URI
)


def _github_connection_success_html(token: str, gh_user: Dict[str, Any]) -> str:
    """Renders light-themed completion page that communicates GitHub token to opener."""
    u_login = gh_user.get("login", "developer")
    u_name = gh_user.get("name") or u_login
    u_avatar = gh_user.get("avatar_url", "")
    u_email = gh_user.get("email", "")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>GitHub Connected — AetherOps</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f8fafc;
      color: #0f172a;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
    }}
    .card {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 1.25rem;
      padding: 2.5rem;
      box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.08);
      text-align: center;
      max-width: 400px;
      width: 90%;
    }}
    .icon {{
      width: 48px;
      height: 48px;
      background: #10b981;
      color: #ffffff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 1.25rem auto;
      font-size: 24px;
      font-weight: bold;
    }}
    h3 {{ margin: 0 0 0.5rem 0; font-size: 1.25rem; font-weight: 700; color: #0f172a; }}
    p {{ margin: 0 0 1.25rem 0; font-size: 0.875rem; color: #64748b; }}
    .badge {{
      display: inline-block;
      background: #f0fdf4;
      color: #166534;
      padding: 0.35rem 0.85rem;
      border-radius: 0.5rem;
      font-family: monospace;
      font-weight: 600;
      font-size: 0.85rem;
      margin-bottom: 1.25rem;
      border: 1px solid #bbf7d0;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">✓</div>
    <h3>GitHub Connected!</h3>
    <p>Connected to GitHub as <strong>@{u_login}</strong></p>
    <div class="badge">Repository Access Granted</div>
    <div style="font-size: 0.8rem; color: #94a3b8;">Returning to Module 2 Console...</div>
  </div>
  <script>
    const payload = {{
      type: 'GITHUB_CONNECTION_SUCCESS',
      access_token: '{token}',
      token: '{token}',
      user: {{
        login: '{u_login}',
        name: '{u_name}',
        avatar_url: '{u_avatar}',
        email: '{u_email}'
      }}
    }};
    try {{
      localStorage.setItem('aether_gh_token', '{token}');
      localStorage.setItem('aether_gh_user', JSON.stringify(payload.user));
    }} catch(e) {{}}

    let targetOrigin = window.location.origin;
    try {{
      if (window.opener && window.opener.origin) {{
        const allowedOrigins = [window.location.origin, 'http://localhost:8000', 'http://127.0.0.1:8000'];
        if (allowedOrigins.includes(window.opener.origin)) {{
          targetOrigin = window.opener.origin;
        }}
      }}
    }} catch(e) {{}}

    if (window.opener && !window.opener.closed) {{
      window.opener.postMessage(payload, targetOrigin);
      setTimeout(() => window.close(), 700);
    }} else {{
      window.location.href = 'http://localhost:8000/source-connection?github_connected=1';
    }}
  </script>
</body>
</html>"""


@app.api_route("/api/v1/connections/github/login", methods=["GET", "HEAD"])
@app.api_route("/api/v1/connections/github/oauth/authorize", methods=["GET", "HEAD"])
async def connections_github_login(request: Request, redirect_uri: Optional[str] = None):
    """
    Initiates GitHub OAuth flow specifically for Module 2 Repository Connection.
    Requests 'repo,read:user,user:email' scope.
    """
    cb = redirect_uri or GITHUB_CONNECTION_REDIRECT_URI
    state = generate_oauth_state("connect")
    scope = "repo,read:user,user:email"
    github_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={cb}"
        f"&scope={scope}"
        f"&state={state}"
    )

    if "application/json" in request.headers.get("accept", ""):
        resp = JSONResponse({"url": github_url, "redirect": github_url})
    else:
        resp = RedirectResponse(github_url, status_code=307)
    resp.set_cookie("oauth_state_conn_github", state, httponly=True, samesite="lax", max_age=600, path="/")
    resp.set_cookie("oauth_state_github", state, httponly=True, samesite="lax", max_age=600, path="/")
    return resp


@app.api_route("/api/v1/connections/github/callback", methods=["GET", "HEAD"])
async def connections_github_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
):
    """
    Handles GitHub OAuth callback for Module 2.
    Exchanges code for GitHub access token (with repo scope) and returns it to opener window.
    """
    if error:
        err_msg = error_description or error or "GitHub connection was cancelled."
        return HTMLResponse(_oauth_error_html("GitHub Connection Canceled", err_msg), status_code=400)
    if not code:
        return HTMLResponse(_oauth_error_html("GitHub Connection Error", "Missing authorization code from GitHub."), status_code=400)

    stored_state = request.cookies.get("oauth_state_conn_github") or request.cookies.get("oauth_state_github")
    if not verify_oauth_state(state, stored_state):
        logger.warning(f"Connection OAuth state validation failed. state={state}, cookies={list(request.cookies.keys())}")
        return HTMLResponse(_oauth_error_html("OAuth Security Error", "Invalid or missing OAuth state parameter. Potential CSRF attack prevented."), status_code=400)

    cb = GITHUB_CONNECTION_REDIRECT_URI
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_res = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": cb,
                },
                headers={"Accept": "application/json"}
            )
            token_res.raise_for_status()
            token_data = token_res.json()
            access_token = token_data.get("access_token")
            if not access_token:
                err = token_data.get("error_description", token_data.get("error", "No access token returned"))
                return HTMLResponse(_oauth_error_html("Token Exchange Failed", err), status_code=400)

            user_res = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "AetherOps-Cloud-Connector"
                }
            )
            user_res.raise_for_status()
            gh_user = user_res.json()
    except Exception as e:
        logger.error(f"GitHub Connection OAuth exchange failed: {e}")
        return HTMLResponse(_oauth_error_html("GitHub Connection Failed", str(e)), status_code=400)

    resp = HTMLResponse(_github_connection_success_html(access_token, gh_user))
    resp.delete_cookie("oauth_state_conn_github", path="/")
    resp.delete_cookie("oauth_state_github", path="/")
    return resp


@app.get("/")
async def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "status": "DENIED",
                "code": 403,
                "detail": "Direct browser access to Auth Service on port 7999 is denied. The AetherOps Dashboard is exclusively hosted on Port 8000.",
                "service": "auth-service",
                "port": 7999,
                "dashboard_url": "http://localhost:8000",
            },
        )
    return {
        "service": "AetherOps Auth & OAuth Authority Service",
        "version": "2.0.0",
        "port": 7999,
        "type": "BACKEND_MICROSERVICE",
        "features": [
            "AWS-style 12-digit Account IDs",
            "Login via Login ID (Username, Email, or Account ID)",
            "Multi-tenant isolation with hidden Tenant IDs",
            "Google & GitHub OAuth 2.0 User Authentication",
            "GitHub Repository & Cloud Connection OAuth Broker"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7999)
