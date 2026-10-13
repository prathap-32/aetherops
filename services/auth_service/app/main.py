# services/auth_service/app/main.py
"""
AetherOps Auth Service - Port 7999
ONLY handles authentication API - NO FRONTEND
Frontend is served from port 8000 (Gateway)

Microservice Architecture:
- This service: Authentication API only
- Port 8000: Serves frontend + proxies to this service
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
import logging

logger = logging.getLogger("auth-service")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AetherOps Auth Service - API Only")

# CORS - Allow requests from dashboard (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock user database (replace with actual DB)
MOCK_USERS = {
    "admin": {"password": "admin123", "role": "ADMIN", "email": "admin@aetherops.local"},
    "user": {"password": "user123", "role": "USER", "email": "user@aetherops.local"},
}


class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "USER"


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "auth", "port": 7999}


@app.post("/api/v1/auth/login")
async def login(req: LoginRequest):
    """Login endpoint - validates credentials"""
    user = MOCK_USERS.get(req.username)
    
    if not user or user["password"] != req.password:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid username or password"}
        )
    
    # Generate mock JWT token
    token = f"mock_token_{req.username}_12345"
    
    return {
        "token": token,
        "user": {
            "username": req.username,
            "email": user["email"],
            "role": user["role"]
        },
        "redirect_url": "http://localhost:8000"
    }


@app.post("/api/v1/auth/register")
async def register(req: RegisterRequest):
    """Register endpoint - creates new user"""
    if req.username in MOCK_USERS:
        return JSONResponse(
            status_code=400,
            content={"detail": "Username already exists"}
        )
    
    # Add to mock database
    MOCK_USERS[req.username] = {
        "password": req.password,
        "role": req.role,
        "email": req.email
    }
    
    # Generate mock JWT token
    token = f"mock_token_{req.username}_12345"
    
    return {
        "token": token,
        "user": {
            "username": req.username,
            "email": req.email,
            "role": req.role
        },
        "redirect_url": "http://localhost:8000"
    }


@app.get("/api/v1/auth/me")
async def get_me(request: Request):
    """Get current user info from token"""
    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    x_admin_key = request.headers.get("X-Admin-Key", "")
    
    token = ""
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    elif x_admin_key:
        token = x_admin_key
    
    if not token or not token.startswith("mock_token_"):
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or missing token"}
        )
    
    # Extract username from mock token
    username = token.replace("mock_token_", "").split("_")[0]
    user = MOCK_USERS.get(username)
    
    if not user:
        return JSONResponse(
            status_code=401,
            content={"detail": "User not found"}
        )
    
    return {
        "username": username,
        "email": user["email"],
        "role": user["role"]
    }


@app.get("/api/v1/auth/google/login")
async def google_login():
    """Google OAuth initiation"""
    return {"redirect": "https://accounts.google.com/o/oauth2/v2/auth"}


@app.get("/api/v1/auth/github/login")
async def github_login():
    """GitHub OAuth initiation"""
    return {"redirect": "https://github.com/login/oauth/authorize"}


@app.get("/")
async def root():
    """Root endpoint - inform that this is API only"""
    return {
        "service": "AetherOps Auth Service",
        "version": "1.0",
        "note": "This is an API-only service. Access the frontend at http://localhost:8000",
        "endpoints": {
            "health": "/health",
            "login": "POST /api/v1/auth/login",
            "register": "POST /api/v1/auth/register",
            "google_oauth": "/api/v1/auth/google/login",
            "github_oauth": "/api/v1/auth/github/login"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7999)
