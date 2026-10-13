# AetherOps - Project Structure & Module Status

## 📊 Overview

**Architecture**: API Gateway + 13 Microservices  
**Frontend**: Single React SPA (served from port 8000)  
**Total Services**: 14 (1 Gateway + 1 Auth + 12 Backend APIs)  
**Implementation Status**: 35% Complete

---

## 🏗️ Microservices Architecture Pattern

```
User Browser
    ↓
http://localhost:8000 (Gateway - Serves React SPA)
    ↓
    ├─→ Port 7999 - Auth API
    ├─→ Port 8001 - Projects API
    ├─→ Port 8002 - Connections API
    ├─→ Port 8003 - Repo Analyzer API
    ├─→ Port 8004 - Requirements API
    ├─→ Port 8005 - Architecture API
    ├─→ Port 8006 - IaC Generator API
    ├─→ Port 8007 - FinOps API
    ├─→ Port 8008 - Security API
    ├─→ Port 8009 - CI/CD API
    ├─→ Port 8010 - Monitoring API
    ├─→ Port 8011 - Deployer API
    └─→ Port 8012 - Admin API
```

---

## 📁 Folder Structure

### Root Level
```
aetherops/
├── README.md                      # Project overview
├── QUICK_START.md                 # Quick start guide
├── ARCHITECTURE_FLOW.md           # Architecture documentation
├── PROJECT_STRUCTURE.md           # This file
├── START_COMMANDS.md              # Service startup commands
├── start-both.sh                  # Start auth + gateway
├── start-all-services.sh          # Start all services
├── stop-all-services.sh           # Stop all services
├── test-auth-flow.sh              # Automated tests
├── docker-compose.yml             # Docker orchestration
├── pyproject.toml                 # Python config
├── requirements.txt               # Python dependencies
└── .venv/                         # Python virtual environment
```

### Frontend (Single React Application)
```
frontend/
├── src/
│   ├── main.jsx                   # App entry point
│   ├── index.css                  # Global styles (design tokens)
│   │
│   ├── pages/                     # Page components
│   │   ├── LoginPage.jsx          # http://localhost:8000/login
│   │   ├── DashboardPage.jsx      # http://localhost:8000/
│   │   ├── ProjectsPage.jsx       # http://localhost:8000/projects
│   │   ├── ProjectDetailPage.jsx  # http://localhost:8000/projects/:id
│   │   ├── EnvironmentsPage.jsx   # http://localhost:8000/environments
│   │   ├── SourceConnectionPage.jsx # http://localhost:8000/source-connection
│   │   ├── SourceAnalysisPage.jsx # http://localhost:8000/source-analysis
│   │   ├── RequirementsPage.jsx   # http://localhost:8000/requirements
│   │   ├── ArchitecturePage.jsx   # http://localhost:8000/architecture
│   │   ├── ArchitectureDesignerPage.jsx # http://localhost:8000/architecture/designer
│   │   ├── RiskAnalysisPage.jsx   # http://localhost:8000/risk-analysis
│   │   ├── SecurityPage.jsx       # http://localhost:8000/security
│   │   ├── TerraformPage.jsx      # http://localhost:8000/terraform
│   │   ├── ExecutionPage.jsx      # http://localhost:8000/execution
│   │   ├── DeploymentPage.jsx     # http://localhost:8000/deployment
│   │   ├── CICDPage.jsx           # http://localhost:8000/cicd
│   │   ├── MonitoringPage.jsx     # http://localhost:8000/monitoring
│   │   ├── OptimizationPage.jsx   # http://localhost:8000/optimization
│   │   ├── AuditPage.jsx          # http://localhost:8000/audit
│   │   ├── DocumentationPage.jsx  # http://localhost:8000/documentation
│   │   └── SettingsPage.jsx       # http://localhost:8000/settings
│   │
│   ├── components/                # Reusable components
│   │   ├── Layout.jsx             # Main layout wrapper
│   │   ├── Sidebar.jsx            # Navigation sidebar
│   │   ├── TopNav.jsx             # Top navigation bar
│   │   ├── Button.jsx             # Button component
│   │   ├── Card.jsx               # Card component
│   │   └── ...                    # Other components
│   │
│   ├── context/                   # React Context
│   │   ├── AuthContext.jsx        # Authentication state
│   │   └── ThemeContext.jsx       # Theme (light/dark)
│   │
│   └── services/                  # API layer
│       └── api.js                 # All API calls to backend
│
├── dist/                          # Production build (served by gateway)
│   ├── index.html                 # Entry HTML file
│   └── assets/                    # Bundled JS/CSS
│
├── package.json                   # NPM dependencies
├── vite.config.js                 # Vite bundler config
└── tailwind.config.js             # Tailwind CSS config
```

### Microservices
```
services/
│
├── 01_gateway/                    # Port 8000 - Frontend + API Proxy
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py                # Serves React + proxies APIs
│   └── logs/
│
├── 02_auth_service/               # Port 7999 - Authentication
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py                # Login, register, OAuth
│   └── logs/
│
├── 03_project_and_environment_management/  # Port 8001
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app
│   │   ├── database.py            # SQLAlchemy setup
│   │   ├── models.py              # ORM models
│   │   ├── router.py              # API routes
│   │   ├── schemas.py             # Pydantic schemas
│   │   ├── auth.py                # Session auth
│   │   ├── cache.py               # Cache manager
│   │   └── seed.py                # Initial data
│   ├── logs/
│   └── tests/
│
├── 04_source_and_cloud_connection/  # Port 8002
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # Git + cloud connections
│   │   ├── github_integration.py  # GitHub API client
│   │   ├── aws_integration.py     # AWS boto3 client
│   │   └── models.py              # Connection models
│   ├── logs/
│   └── tests/
│
├── 05_repo_analyzer_service/      # Port 8003
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # Code analysis
│   │   ├── analyzer.py            # Analysis engine
│   │   └── schemas.py             # Analysis schemas
│   ├── logs/
│   └── tests/
│
├── 06_requirement_analysis/       # Port 8004
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # Requirements analysis
│   │   ├── analyzer.py            # Analysis engine
│   │   ├── catalog.py             # AWS service catalog
│   │   └── schemas.py             # Requirement schemas
│   ├── logs/
│   └── tests/
│
├── 07_architecture_generator/     # Port 8005
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # Architecture graphs
│   │   ├── generator.py           # Graph generator
│   │   └── schemas.py             # Graph schemas
│   ├── logs/
│   └── tests/
│
├── 08_iac_generator/              # Port 8006
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # Terraform generation
│   │   ├── terraform_engine.py    # IaC generator
│   │   └── schemas.py             # IaC schemas
│   ├── logs/
│   └── tests/
│
├── 09_finops_optimizer/           # Port 8007
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # Cost optimization
│   │   ├── optimizer.py           # Cost engine
│   │   └── schemas.py             # Cost schemas
│   ├── logs/
│   └── tests/
│
├── 10_security_scanner/           # Port 8008
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # Security scanning
│   │   ├── scanner.py             # Security engine
│   │   └── schemas.py             # Security schemas
│   ├── logs/
│   └── tests/
│
├── 11_cicd_pipeline/              # Port 8009
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # CI/CD generation
│   │   ├── pipeline_generator.py  # Pipeline engine
│   │   └── schemas.py             # Pipeline schemas
│   ├── logs/
│   └── tests/
│
├── 12_observability_setup/        # Port 8010
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # Monitoring setup
│   │   ├── monitoring_engine.py   # Monitoring engine
│   │   └── schemas.py             # Monitoring schemas
│   ├── logs/
│   └── tests/
│
├── 13_cloud_deployer/             # Port 8011
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # Cloud deployment
│   │   ├── deployer.py            # Deployment engine
│   │   └── schemas.py             # Deployment schemas
│   ├── logs/
│   └── tests/
│
└── 14_admin_console/              # Port 8012
    ├── app/
    │   ├── __init__.py
    │   ├── main.py                # Admin operations
    │   ├── database.py            # Admin DB
    │   ├── models.py              # Admin models
    │   └── security.py            # Admin security
    ├── logs/
    └── tests/
```

---

## 📊 Service Implementation Status

### Legend
- ✅ **Production Ready** - Fully implemented and tested
- 🟢 **Complete** - Core features done, minor enhancements needed
- 🟡 **Partial** - Basic structure, needs major work
- 🔴 **Skeleton** - Only API skeleton, needs full implementation

---

### ✅ Tier 1: Production Ready (2 services)

#### 1. Gateway Service (Port 8000)
**Status**: ✅ Production Ready  
**Implementation**: 100%

**Features**:
- ✅ Serves React SPA from `frontend/dist/`
- ✅ Routes all clean URLs
- ✅ Reverse proxy to all microservices
- ✅ OAuth callback routing
- ✅ Health checks
- ✅ Error handling
- ✅ CORS configured

**Endpoints**:
```
GET  /                      # React SPA (index.html)
GET  /login                 # React SPA
GET  /projects              # React SPA
GET  /health                # Health check
ANY  /api/v1/{module}/*     # Proxy to microservices
ANY  /auth/google/*         # OAuth proxy
ANY  /auth/github/*         # OAuth proxy
```

---

#### 2. Auth Service (Port 7999)
**Status**: ✅ Production Ready  
**Implementation**: 90% (mock tokens, needs JWT)

**Features**:
- ✅ Login API
- ✅ Register API
- ✅ Get user info API
- ✅ OAuth endpoints (Google, GitHub)
- ✅ CORS for port 8000
- ✅ API-only (no frontend)
- ⚠️ Mock tokens (needs real JWT)

**Endpoints**:
```
POST /api/v1/auth/login     # User login
POST /api/v1/auth/register  # User registration
GET  /api/v1/auth/me        # Get current user
GET  /api/v1/auth/google/login  # Google OAuth
GET  /api/v1/auth/github/login  # GitHub OAuth
GET  /health                # Health check
```

**Test Accounts**:
- Admin: `admin` / `admin123`
- User: `user` / `user123`

---

### 🟢 Tier 2: Core Complete (3 services)

#### 3. Project & Environment Management (Port 8001)
**Status**: 🟢 Core Complete  
**Implementation**: 70%

**Features**:
- ✅ Projects CRUD
- ✅ Environments CRUD
- ✅ SQLite database
- ✅ Session auth
- ✅ Initial data seeding
- ❌ Multi-tenancy
- ❌ RBAC
- ❌ PostgreSQL

**Endpoints**:
```
GET    /api/v1/projects              # List projects
POST   /api/v1/projects              # Create project
GET    /api/v1/projects/{id}         # Get project
PUT    /api/v1/projects/{id}         # Update project
DELETE /api/v1/projects/{id}         # Delete project
GET    /api/v1/projects/{id}/environments  # List environments
POST   /api/v1/projects/{id}/environments  # Create environment
```

**Next Steps**:
1. Add PostgreSQL support
2. Implement multi-tenancy
3. Add RBAC system
4. Add audit logging

---

#### 4. Source & Cloud Connection (Port 8002)
**Status**: 🟢 GitHub Complete, AWS Partial  
**Implementation**: 60%

**Features**:
- ✅ GitHub PAT verification
- ✅ List GitHub repos
- ✅ List GitHub branches
- ✅ AWS credential validation (basic)
- ❌ OAuth callback handling
- ❌ Connection persistence
- ❌ Credentials encryption
- ❌ Azure/GCP support

**Endpoints**:
```
POST /api/v1/github/verify-pat          # Verify GitHub PAT
GET  /api/v1/github/repos               # List repos
GET  /api/v1/github/repos/{owner}/{repo}/branches  # List branches
POST /api/v1/cloud/aws/validate         # Validate AWS credentials
POST /api/v1/connections/finalize       # Save connection
GET  /api/v1/connections/{id}/snapshot  # Get connection snapshot
```

**Next Steps**:
1. Complete OAuth flow
2. Add database storage
3. Encrypt credentials
4. Add Azure/GCP support

---

#### 5. Admin Console (Port 8012)
**Status**: 🟢 Basic Admin Complete  
**Implementation**: 50%

**Features**:
- ✅ System health probes
- ✅ Service catalog
- ✅ Cache management
- ✅ Basic audit logs
- ❌ User management UI
- ❌ System metrics
- ❌ Configuration management

**Endpoints**:
```
GET  /api/admin/probe               # System health
GET  /api/admin/catalog             # Service catalog
POST /api/admin/sync                # Sync catalog
POST /api/admin/clear-cache         # Clear cache
GET  /api/admin/auth/audit          # Audit logs
GET  /api/admin/modules             # List modules
```

---

### 🟡 Tier 3: Partial Implementation (3 services)

#### 6. Requirement Analysis (Port 8004)
**Status**: 🟡 Catalog Done, Analysis Basic  
**Implementation**: 40%

**Features**:
- ✅ AWS service catalog
- ✅ Basic recommendations
- ❌ Advanced ML recommendations
- ❌ Cost estimation
- ❌ Multi-cloud support

**Next Steps**:
1. Add ML-based recommendations
2. Integrate cost estimation
3. Add Azure/GCP catalogs
4. Improve analysis algorithms

---

#### 7. Architecture Generator (Port 8005)
**Status**: 🟡 Basic Graph Generation  
**Implementation**: 40%

**Features**:
- ✅ ReactFlow graph generation
- ✅ Node/edge creation
- ❌ Advanced patterns
- ❌ Cost annotations
- ❌ Security visualization

**Next Steps**:
1. Add architecture pattern library
2. Add cost annotations
3. Visualize security groups
4. Network topology

---

#### 8. Repo Analyzer (Port 8003)
**Status**: 🟡 Skeleton with Basic Logic  
**Implementation**: 30%

**Features**:
- ✅ API skeleton
- 🟡 Basic scan endpoint
- ❌ Language detection
- ❌ Dependency analysis
- ❌ Code complexity
- ❌ File structure analysis

**Next Steps**:
1. Implement code parsing (AST)
2. Add language detection
3. Dependency graph
4. Complexity metrics

---

### 🔴 Tier 4: Skeleton Only (6 services)

#### 9. IaC Generator (Port 8006) - **HIGH PRIORITY**
**Status**: 🔴 Skeleton Only  
**Implementation**: 10%

**Needs**:
- Terraform code generation
- Module organization
- Variable management
- State configuration
- Multi-environment support

**Priority**: **CRITICAL** - Core feature

---

#### 10. Security Scanner (Port 8008) - **HIGH PRIORITY**
**Status**: 🔴 Skeleton Only  
**Implementation**: 10%

**Needs**:
- IAM policy analysis
- Security group audit
- S3 bucket permissions
- Encryption verification
- Compliance checks

**Priority**: **HIGH** - Enterprise requirement

---

#### 11. Cloud Deployer (Port 8011) - **HIGH PRIORITY**
**Status**: 🔴 Skeleton Only  
**Implementation**: 10%

**Needs**:
- Terraform apply automation
- Deployment tracking
- Rollback capability
- Drift detection
- Change preview

**Priority**: **CRITICAL** - Core deployment

---

#### 12. FinOps Optimizer (Port 8007)
**Status**: 🔴 Skeleton Only  
**Implementation**: 5%

**Needs**:
- Cost Explorer integration
- Utilization analysis
- Right-sizing recommendations
- Reserved Instance suggestions
- Savings plans

**Priority**: **MEDIUM** - Value-add

---

#### 13. CI/CD Pipeline (Port 8009)
**Status**: 🔴 Skeleton Only  
**Implementation**: 5%

**Needs**:
- GitHub Actions YAML
- GitLab CI config
- Jenkins pipeline
- Build/test/deploy stages
- Environment promotion

**Priority**: **MEDIUM** - Nice to have

---

#### 14. Observability Setup (Port 8010)
**Status**: 🔴 Skeleton Only  
**Implementation**: 5%

**Needs**:
- CloudWatch dashboards
- Datadog/New Relic integration
- Log aggregation
- Alerting rules
- SLO/SLI definitions

**Priority**: **MEDIUM** - Post-deployment

---

## 🎯 Implementation Roadmap

### **Phase 1: Foundation** ✅ Complete
- [x] Gateway service (frontend serving + proxy)
- [x] Auth service (login/register)
- [x] Project management (CRUD)
- [x] Source connection (GitHub)
- [x] Warm amber UI redesign

### **Phase 2: Core Features** 🚧 In Progress (35%)
- [x] Requirement analysis (basic)
- [x] Architecture generator (basic)
- [ ] IaC generator - **NEXT**
- [ ] Cloud deployer - **NEXT**
- [ ] Security scanner - **NEXT**

### **Phase 3: Advanced Features** ⏳ Not Started
- [ ] FinOps optimizer
- [ ] CI/CD pipeline generator
- [ ] Observability setup
- [ ] Advanced ML recommendations

### **Phase 4: Production Hardening** ⏳ Not Started
- [ ] Real JWT tokens
- [ ] PostgreSQL database
- [ ] OAuth completion (Google/GitHub)
- [ ] Multi-tenancy + RBAC
- [ ] Docker containerization
- [ ] Kubernetes deployment

---

## 📈 Metrics

| Category | Count | Percentage |
|----------|-------|------------|
| **Total Services** | 14 | 100% |
| **Production Ready** | 2 | 14% |
| **Core Complete** | 3 | 21% |
| **Partial Implementation** | 3 | 21% |
| **Skeleton Only** | 6 | 43% |
| **Overall Completion** | - | **~35%** |

---

## 🚀 Quick Start

```bash
# Start essential services (Auth + Gateway)
./start-both.sh

# Test auth flow
./test-auth-flow.sh

# Access application
open http://localhost:8000

# Login
Username: admin
Password: admin123
```

---

## 📝 Development Workflow

### 1. Add New Feature to Existing Service
```bash
# Edit service code
vim services/{service_name}/app/main.py

# Restart service
pkill -f "port {port}"
cd services/{service_name}
/path/to/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port {port}
```

### 2. Modify Frontend
```bash
# Edit React component
vim frontend/src/pages/SomePage.jsx

# Rebuild
cd frontend
npm run build

# Restart gateway (serves new build)
pkill -f "port 8000"
./start-both.sh
```

### 3. Add New Microservice
```bash
# Create service structure
mkdir -p services/new_service/app
touch services/new_service/app/{__init__.py,main.py,schemas.py}

# Implement FastAPI app in main.py

# Update gateway proxy routes in services/gateway/app/main.py

# Add to start-all-services.sh
```

---

## 🐳 Docker Structure (Future)

```yaml
# docker-compose.yml
services:
  auth:
    build: ./services/auth_service
    ports: ["7999:7999"]
    
  gateway:
    build: ./services/gateway
    ports: ["8000:8000"]
    depends_on: [auth]
    
  projects:
    build: ./services/project_and_environment_management
    ports: ["8001:8001"]
    
  # ... other services
```

---

**Last Updated**: October 10, 2026  
**Version**: 0.35.0  
**Status**: Early Development - Core Platform Working
