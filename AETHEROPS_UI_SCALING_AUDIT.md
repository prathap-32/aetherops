# AETHEROPS UI SCALING & RESPONSIVENESS AUDIT

## 1. Service Inventory
AetherOps consists of 15 microservices and frontend entry points operating on ports 7999–8013:
1. **Auth Service** (Port 7999) - Authentication, session management, OAuth callback.
2. **API Gateway & Frontend** (Port 8000) - Main React Single Page Application (SPA) entry point and reverse proxy.
3. **Project & Environment Service** (Port 8001) - Tenant projects, environments, workspace seed data, and FastAPI dashboard templates.
4. **Source, Cloud & Git Service** (Port 8002) - GitHub & AWS credential connection workflows, connection status dashboards.
5. **Source Code Analyzer** (Port 8003) - Universal repository scanner and Gemini sizer engine (`module3_page.py`).
6. **AI Architecture Engine** (Port 8004) - AWS multi-AZ architecture recommender and rule generator.
7. **Architecture Designer** (Port 8005) - Interactive canvas studio for visual architecture composition.
8. **Architecture Validation** (Port 8006) - AWS Well-Architected framework compliance validator.
9. **Pre-Deployment Risk Engine** (Port 8007) - AI dry-run and risk evaluation.
10. **Terraform / IaC Generator** (Port 8008) - Terraform HCL synthesis engine.
11. **Approval & Execution Service** (Port 8009) - Approval gates and execution pipelines.
12. **Application Deployment Engine** (Port 8010) - Infrastructure provisioning and state inventory.
13. **Monitoring Service** (Port 8011) - APM, metrics, and observability dashboards.
14. **Audit & History Service** (Port 8012) - Security audit ledger and session history.
15. **Admin Console** (Port 8013) - Privileged fleet health, container status, and maintenance (`admin_console/app/dashboard_page.py`, `login_page.py`).

---

## 2. Shared Assets & Typography Baseline
- **Primary Font Family**: `"Amazon Ember", sans-serif` (loaded via `/static/fonts/fonts.css`).
- **Monospaced Font**: `"JetBrains Mono", monospace`.
- **Existing Scaling Deficiencies**:
  - Body text was previously compressed (13px–14px on mobile), causing readability strain.
  - Button and input heights averaged 36px–40px, failing comfortable touch target standards (48px target).
  - Mobile header height was 56px, leaving insufficient spacing for title and touch controls.
  - Metric values on cards were sized at 24px, lacking strong dashboard hierarchy.
