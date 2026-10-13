# AetherOps Microservices Architecture Flow

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         USER ACCESS                          │
└─────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
        ┌───────▼────────┐            ┌────────▼──────────┐
        │  Port 8000     │            │   Port 7999       │
        │  GATEWAY       │◄───────────┤   AUTH SERVICE    │
        │  (Frontend)    │  API Calls │   (API Only)      │
        └───────┬────────┘            └───────────────────┘
                │
                │ Reverse Proxy
                │
        ┌───────▼──────────────────────────────────────────┐
        │         Microservices (Ports 8001-8012)          │
        │  • Project Manager (8001)                        │
        │  • Source Connector (8002)                       │
        │  • Repo Analyzer (8003)                          │
        │  • Requirements Engine (8004)                    │
        │  • Architecture Generator (8005)                 │
        │  • IaC Generator (8006)                          │
        │  • FinOps Optimizer (8007)                       │
        │  • Security Engine (8008)                        │
        │  • CI/CD Pipeline (8009)                         │
        │  • Monitoring (8010)                             │
        │  • Cloud Deployer (8011)                         │
        │  • Admin Console (8012)                          │
        └──────────────────────────────────────────────────┘
```

## Service Separation

### Port 7999: Auth Service (API-Only)
- **Purpose**: Authentication API microservice
- **Serves**: JSON API responses only
- **NO Frontend**: Does not serve HTML/React
- **Endpoints**:
  - `POST /api/v1/auth/login` - User login
  - `POST /api/v1/auth/register` - User registration
  - `GET /api/v1/auth/me` - Get current user
  - `GET /api/v1/auth/google/login` - Google OAuth
  - `GET /api/v1/auth/github/login` - GitHub OAuth
- **CORS**: Allows requests from `http://localhost:8000`
- **Docker**: Deployed as separate container

### Port 8000: Gateway Service
- **Purpose**: Main user entry point & reverse proxy
- **Serves**: React SPA frontend from `/home/ren/Proj/1/aetherops/frontend/dist`
- **Routes**:
  - All frontend routes (`/`, `/login`, `/projects`, etc.)
  - API proxy to microservices (ports 8001-8012)
- **Does NOT**: Handle authentication logic (delegates to port 7999)

## Login Flow (Correct Architecture)

```
1. User opens browser → http://localhost:8000
   ├─ Gateway serves React SPA (index.html + assets)
   └─ User sees login page at http://localhost:8000/login

2. User enters credentials and clicks "Sign In"
   ├─ React frontend makes API call:
   │  fetch('http://localhost:7999/api/v1/auth/login', {
   │    method: 'POST',
   │    body: { username, password }
   │  })
   │
   └─ Auth Service (7999) validates credentials

3. Auth Service responds with:
   {
     "token": "mock_token_admin_12345",
     "user": { "username": "admin", "email": "...", "role": "ADMIN" },
     "redirect_url": "http://localhost:8000"
   }

4. React frontend:
   ├─ Stores token in localStorage
   ├─ Updates AuthContext state
   └─ Redirects to http://localhost:8000/ (dashboard)

5. User stays on http://localhost:8000
   ├─ All pages served from Gateway
   └─ All auth API calls go to http://localhost:7999
```

## Key Points

### ✅ Correct Behavior
- User **ONLY** accesses `http://localhost:8000` in browser
- Auth Service (7999) is **API-only**, never serves frontend
- Frontend makes cross-origin API calls to port 7999 (CORS enabled)
- Login redirects happen **within** port 8000 (React Router)
- Gateway proxies other microservice APIs (ports 8001-8012)

### ❌ What We Fixed
- Before: Auth service was serving React frontend on port 7999
- Before: User would be redirected to port 7999 for login page
- Before: Confusion about which port serves frontend
- After: Clear separation - 7999 = API only, 8000 = Frontend only

## Docker Deployment

Each microservice runs in its own container:

```yaml
# docker-compose.yml
services:
  auth:
    build: ./services/auth_service
    ports:
      - "7999:7999"
    # API only, no frontend
    
  gateway:
    build: ./services/gateway
    ports:
      - "8000:8000"
    # Serves frontend + proxies APIs
    depends_on:
      - auth
      
  # ... other microservices (8001-8012)
```

### Nginx Configuration (Optional)

For production, Nginx can:
1. Terminate SSL
2. Route `/api/v1/auth/*` from 8000 → 7999 (hide port 7999 from public)
3. Route other `/api/v1/*` to respective microservices

```nginx
server {
    listen 443 ssl;
    server_name aetherops.cloud;
    
    # Frontend (React SPA)
    location / {
        proxy_pass http://localhost:8000;
    }
    
    # Auth API (internal)
    location /api/v1/auth/ {
        proxy_pass http://localhost:7999;
    }
    
    # Other APIs
    location /api/v1/ {
        proxy_pass http://localhost:8000;
    }
}
```

## Testing the Flow

### 1. Start Services
```bash
cd /home/ren/Proj/1/aetherops

# Start Gateway (Frontend)
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start Auth (API)
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 7999 &
```

### 2. Open Browser
```
http://localhost:8000
```

### 3. Test Login
- Username: `admin`
- Password: `admin123`
- Click "Sign In"
- Should redirect to `http://localhost:8000/` (dashboard)
- URL should **NOT** change to port 7999

### 4. Verify API Calls (DevTools Network Tab)
```
Request to: http://localhost:7999/api/v1/auth/login
Status: 200 OK
Response: { "token": "...", "user": {...}, "redirect_url": "http://localhost:8000" }
```

### 5. Check Browser Address Bar
```
Before login: http://localhost:8000/login
After login:  http://localhost:8000/
             ^^^^^^^^^^^^^^^^^^^ Should stay on 8000
```

## Current Status

✅ Auth Service (7999) - API only, no frontend
✅ Gateway Service (8000) - Serves React SPA
✅ Frontend configured to call auth API at port 7999
✅ CORS enabled for cross-origin auth requests
✅ Login flow keeps user on port 8000
✅ Microservices architecture ready for Docker

## Files Modified

1. `/services/auth_service/app/main.py` - Removed frontend serving
2. `/frontend/src/services/api.js` - Auth API points to port 7999
3. `/services/gateway/app/main.py` - Serves frontend exclusively
4. Frontend rebuilt with new config

## Next Steps for Production

1. Add real JWT token generation (not mock)
2. Add database for user storage (PostgreSQL)
3. Implement token refresh mechanism
4. Add rate limiting to auth endpoints
5. Set up HTTPS with SSL certificates
6. Configure Nginx reverse proxy
7. Build Docker images for all services
8. Deploy to Kubernetes/ECS cluster
