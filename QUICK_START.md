# AetherOps - Quick Start Guide

## 🚀 Start Services

### Option 1: Start Both (Auth + Gateway)
```bash
cd /home/ren/Proj/1/aetherops
./start-both.sh
```

### Option 2: Manual Start
```bash
# Terminal 1 - Gateway (Frontend)
cd /home/ren/Proj/1/aetherops/services/gateway
/home/ren/Proj/1/aetherops/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Auth Service (API)
cd /home/ren/Proj/1/aetherops/services/auth_service
/home/ren/Proj/1/aetherops/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 7999
```

## 🌐 Access Application

Open browser: **http://localhost:8000**

### Test Accounts
- **Admin**: `admin` / `admin123`
- **User**: `user` / `user123`

## ✅ Verify Setup

Run automated tests:
```bash
cd /home/ren/Proj/1/aetherops
./test-auth-flow.sh
```

## 🏗️ Architecture

```
User Browser
    │
    ├─ http://localhost:8000 ─────────────► Gateway (Frontend + Proxy)
    │                                        │
    │                                        ├─ Serves React SPA
    │                                        └─ Proxies API to microservices
    │
    └─ API calls to:
       http://localhost:7999 ──────────────► Auth Service (API Only)
                                             ├─ POST /api/v1/auth/login
                                             ├─ POST /api/v1/auth/register
                                             └─ GET /api/v1/auth/me
```

## 🔑 Key Points

1. **User ONLY accesses port 8000** in browser
2. **Auth service (7999) is API-only** - no HTML/frontend
3. **Login stays on port 8000** - React Router handles navigation
4. **Frontend makes cross-origin API calls** to port 7999

## 📁 Important Files

```
aetherops/
├── QUICK_START.md              ← This file
├── ARCHITECTURE_FLOW.md        ← Detailed architecture docs
├── start-both.sh               ← Start auth + gateway
├── test-auth-flow.sh           ← Run tests
├── frontend/
│   ├── dist/                   ← Built React app (served by gateway)
│   └── src/
│       ├── services/api.js     ← Auth API points to port 7999
│       └── context/AuthContext.jsx
└── services/
    ├── auth_service/           ← Port 7999 (API only)
    │   └── app/main.py
    └── gateway/                ← Port 8000 (Frontend + Proxy)
        └── app/main.py
```

## 🔧 Development Workflow

### Rebuild Frontend After Changes
```bash
cd /home/ren/Proj/1/aetherops/frontend
npm run build
```

### Restart Services
```bash
# Stop existing processes
pkill -f "uvicorn app.main:app --host 0.0.0.0 --port 8000"
pkill -f "uvicorn app.main:app --host 0.0.0.0 --port 7999"

# Start again
./start-both.sh
```

### Check Logs
```bash
# Gateway logs
tail -f /home/ren/Proj/1/aetherops/services/gateway/logs/gateway.log

# Auth service logs (stdout)
tail -f /tmp/aether-auth.log
```

## 🐳 Docker Deployment (Future)

Each service will run in its own container:

```yaml
services:
  auth:
    image: aetherops/auth:latest
    ports: ["7999:7999"]
    
  gateway:
    image: aetherops/gateway:latest
    ports: ["8000:8000"]
    depends_on: [auth]
    
  # ... 12 other microservices
```

## 🎨 UI Design

**Theme**: Clean, Minimal, Warm, Spacious
- **Primary Color**: Warm Amber `#D97706`
- **Light Background**: Off-white `#F8FAFC`
- **Dark Background**: Deep Charcoal `#0F172A`
- **Fonts**: Plus Jakarta Sans (UI), JetBrains Mono (Code)
- **Inspired by**: Vercel, Linear, Stripe

## 📊 Service Ports

| Port | Service | Type | Description |
|------|---------|------|-------------|
| 7999 | Auth | API | Authentication (login, register, OAuth) |
| 8000 | Gateway | Frontend + Proxy | Main entry point |
| 8001 | Project Manager | API | Projects & environments |
| 8002 | Source Connector | API | GitHub/Cloud connections |
| 8003 | Repo Analyzer | API | Code analysis |
| 8004 | Requirements Engine | API | Requirement analysis |
| 8005 | Architecture Generator | API | Architecture graphs |
| 8006 | IaC Generator | API | Terraform generation |
| 8007 | FinOps Optimizer | API | Cost optimization |
| 8008 | Security Engine | API | Security & compliance |
| 8009 | CI/CD Pipeline | API | Pipeline generation |
| 8010 | Monitoring | API | Observability |
| 8011 | Cloud Deployer | API | Deployment & drift |
| 8012 | Admin Console | API | Admin operations |

## 🆘 Troubleshooting

### Services not starting
```bash
# Check if ports are in use
lsof -i :7999
lsof -i :8000

# Kill existing processes
pkill -f "uvicorn"

# Restart
./start-both.sh
```

### Frontend not loading
```bash
# Rebuild frontend
cd frontend && npm run build

# Check if dist/ exists
ls -la frontend/dist/
```

### CORS errors
- Auth service already allows `http://localhost:8000`
- Check browser console for actual error
- Verify auth service is running on port 7999

### Login not working
```bash
# Test auth API directly
curl -X POST http://localhost:7999/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Should return token and user info
```

## 📚 Documentation

- [ARCHITECTURE_FLOW.md](./ARCHITECTURE_FLOW.md) - Detailed architecture
- [SIMPLE_START.md](./SIMPLE_START.md) - Simple startup guide
- [START_COMMANDS.md](./START_COMMANDS.md) - All service commands

## 🎯 Next Steps

1. ✅ Auth service separated (API-only)
2. ✅ Gateway serves frontend
3. ✅ Login flow working
4. ⏳ Add real JWT tokens
5. ⏳ Add database (PostgreSQL)
6. ⏳ Implement OAuth (Google/GitHub)
7. ⏳ Build Docker images
8. ⏳ Deploy to production

---

**Status**: Ready for browser testing
**Last Updated**: 2026-10-10
