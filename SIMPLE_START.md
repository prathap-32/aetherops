# ✅ AetherOps - Simple Startup Guide

## ⚡ Quick Start (2 Commands)

### 1. First Time Setup (Run Once)
```bash
cd /home/ren/Proj/1/aetherops
python3 -m venv .venv
.venv/bin/pip install fastapi uvicorn httpx pydantic rich pyjwt bcrypt
```

### 2. Start Services (Every Time)
```bash
cd /home/ren/Proj/1/aetherops

# Terminal 1: Auth Service
.venv/bin/python -m uvicorn services.auth_service.app.main:app --host 0.0.0.0 --port 7999

# Terminal 2: Dashboard
.venv/bin/python -m uvicorn services.gateway.app.main:app --host 0.0.0.0 --port 8000
```

---

## 🌐 Access

**Open in browser:**
```
http://localhost:7999
```

**Login:**
- Username: `admin`
- Password: `admin123`

**After login → Redirects to:** `http://localhost:8000`

---

## 🛑 Stop Services

Press `Ctrl+C` in each terminal

Or kill all:
```bash
pkill -f 'uvicorn.*app.main:app'
```

---

## ✨ What's Working

- ✅ **Port 7999**: Auth Service (Login/Signup)
- ✅ **Port 8000**: Dashboard (React SPA)
- ✅ **Warm Amber Design**: New UI with spacious layouts
- ✅ **Separated Architecture**: Auth → Dashboard flow

---

## 📋 Add More Modules (Optional)

Start additional services in separate terminals:

```bash
# Projects (Port 8001)
.venv/bin/python -m uvicorn services.project_and_environment_management.app.main:app --port 8001

# Source Connection (Port 8002)
.venv/bin/python -m uvicorn services.source_and_cloud_connection.app.main:app --port 8002

# Requirements (Port 8004)
.venv/bin/python -m uvicorn services.requirement_analysis.app.main:app --port 8004

# Architecture (Port 8005)
.venv/bin/python -m uvicorn services.architecture_generator.app.main:app --port 8005

# IaC (Port 8006)
.venv/bin/python -m uvicorn services.iac_generator.app.main:app --port 8006

# FinOps (Port 8007)
.venv/bin/python -m uvicorn services.finops_optimizer.app.main:app --port 8007

# Security (Port 8008)
.venv/bin/python -m uvicorn services.security_scanner.app.main:app --port 8008

# CI/CD (Port 8009)
.venv/bin/python -m uvicorn services.cicd_pipeline.app.main:app --port 8009

# Observability (Port 8010)
.venv/bin/python -m uvicorn services.observability_setup.app.main:app --port 8010

# Deployer (Port 8011)
.venv/bin/python -m uvicorn services.cloud_deployer.app.main:app --port 8011

# Admin Console (Port 8012)
.venv/bin/python -m uvicorn services.admin_console.app.main:app --port 8012
```

---

## 🔍 Check Status

```bash
# See running services
ps aux | grep uvicorn

# Test endpoints
curl http://localhost:7999/health
curl http://localhost:8000/health
```
