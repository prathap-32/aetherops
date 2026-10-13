# AetherOps - Individual Service Startup Commands

## Prerequisites
```bash
cd /home/ren/Proj/1/aetherops
python3 -m venv .venv
.venv/bin/pip install fastapi uvicorn httpx pydantic rich pyjwt bcrypt
```

---

## Individual Service Commands

### 1. Auth Service (Port 7999)
```bash
cd /home/ren/Proj/1/aetherops/services/auth_service
../../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 7999
```

### 2. Gateway & Dashboard (Port 8000)
```bash
cd /home/ren/Proj/1/aetherops/services/gateway
../../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Project Management (Port 8001)
```bash
cd /home/ren/Proj/1/aetherops/services/project_and_environment_management
../../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 4. Source & Cloud Connection (Port 8002)
```bash
cd /home/ren/Proj/1/aetherops/services/source_and_cloud_connection
../../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### 5. Repo Analyzer (Port 8003)
```bash
cd /home/ren/Proj/1/aetherops/services/repo_analyzer_service
../../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8003
```

### 6. Requirement Analysis (Port 8004)
```bash
cd /home/ren/Proj/1/aetherops/services/requirement_analysis
../../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8004
```

### 7. Architecture Generator (Port 8005)
```bash
cd /home/ren/Proj/1/aetherops/services/architecture_generator
../../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8005
```

### 8. IaC Generator (Port 8006)
```bash
cd /home/ren/Proj/1/aetherops/services/iac_generator
../../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8006
```

### 9. FinOps Optimizer (Port 8007)
```bash
cd /home/ren/Proj/1/aetherops/services/finops_optimizer
../../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8007
```

### 10. Security Scanner (Port 8008)
```bash
cd /home/ren/Proj/1/aetherops/services/security_scanner
../../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8008
```

### 11. CI/CD Pipeline (Port 8009)
```bash
cd /home/ren/Proj/1/aetherops/services/cicd_pipeline
../../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8009
```

### 12. Observability Setup (Port 8010)
```bash
cd /home/ren/Proj/1/aetherops/services/observability_setup
../../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8010
```

### 13. Cloud Deployer (Port 8011)
```bash
cd /home/ren/Proj/1/aetherops/services/cloud_deployer
../../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8011
```

### 14. Admin Console (Port 8012)
```bash
cd /home/ren/Proj/1/aetherops/services/admin_console
../../.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8012
```

---

## Quick Start - All Services at Once

### Start All Services:
```bash
cd /home/ren/Proj/1/aetherops
bash start-all-services.sh
```

### Stop All Services:
```bash
cd /home/ren/Proj/1/aetherops
bash stop-all-services.sh
```

Or manually:
```bash
pkill -f 'uvicorn app.main:app'
```

---

## Check Service Status
```bash
# Check all running services
ps aux | grep uvicorn | grep -v grep

# Check specific port
lsof -i :7999  # Auth
lsof -i :8000  # Dashboard
lsof -i :8001  # Projects
# etc...

# Test health endpoints
curl http://localhost:7999/health  # Auth
curl http://localhost:8000/health  # Gateway
curl http://localhost:8001/health  # Projects
```

---

## View Logs
```bash
# All logs are in /tmp/
tail -f /tmp/aether-auth.log
tail -f /tmp/aether-gateway.log
tail -f /tmp/aether-projects.log
# etc...

# Or view all logs:
tail -f /tmp/aether-*.log
```

---

## Port Mapping Reference

| Port | Service | Description |
|------|---------|-------------|
| 7999 | Auth | Login/Signup (User Entry Point) |
| 8000 | Gateway | Unified Dashboard (React SPA) |
| 8001 | Projects | Project & Environment Management |
| 8002 | Source | Source & Cloud Connection |
| 8003 | Analyzer | Repository Analyzer |
| 8004 | Requirements | Requirement Analysis & Sizing |
| 8005 | Architecture | Architecture Graph Generator |
| 8006 | IaC | Infrastructure as Code Generator |
| 8007 | FinOps | Cost Optimization Engine |
| 8008 | Security | Security & Compliance Scanner |
| 8009 | CI/CD | Pipeline Automation |
| 8010 | Observability | Monitoring & APM Setup |
| 8011 | Deployer | Cloud Deployment & Drift Detection |
| 8012 | Admin | Admin Console & Control Plane |

---

## User Flow

1. **User starts at**: http://localhost:7999 (Auth Service)
2. **After login**: Redirects to http://localhost:8000 (Dashboard)
3. **Dashboard sidebar**: Click any module → Nginx proxies to backend (8001-8012)
4. **Users never access**: Ports 8001+ directly (only via Nginx)
