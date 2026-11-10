# AETHEROPS MAIN DASHBOARD CURRENT STATE AUDIT

## 1. Executive Summary

This audit examines the existing AetherOps main dashboard (`DashboardOverview.jsx`, `DashboardPage.jsx`, and backend microservice endpoints across `project_environment_service`, `source_cloud_git_service`, `application_deployment_service`, `monitoring_service`, etc.). The goal is to establish a rigorous baseline inventory of dashboard components, data sources, APIs, user actions, visibility conditions, and functional status to support adaptive new-user onboarding versus existing-user operational overview.

---

## 2. Dashboard Architecture & Navigation Inventory

- **Primary Entrypoint**: `gateway/app/main.py` serves the compiled React SPA shell (`frontend/dist/index.html`) at `/`, `/app`, and clean URL routes (e.g., `/dashboard`, `/projects`, `/source-connection`, `/architecture`, `/terraform`, `/deployment`, `/monitoring`, `/settings`, `/admin`).
- **Client Routing**: Managed by `DashboardPage.jsx` via clean route-to-view mapping (`PATH_VIEW_MAP`), rendering `DashboardOverview` or specific module views (`ProjectEnvironmentView`, `SourceCloudView`, `ArchitectureView`, `IacView`, `DeploymentsView`, `MonitoringView`, etc.).
- **State Management & Persistence**: Uses `AuthContext` for user session and tenant context, coupled with `localStorage` (or backend preferences API `/api/v1/dashboard/preferences`) for widget arrangement, visibility, and sizing preferences (`aether_dashboard_prefs_<user>`).

---

## 3. Comprehensive Component Inventory Table

| Component Name | Current Purpose | Data Source | API Endpoint | User Action | Visibility Conditions | Status | Target User |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Welcome / Greeting Header** | Displays dynamic greeting, username, account ID, copy ID, and summary banner | `AuthContext` user object & `/api/v1/dashboard` | `GET /api/v1/auth/me`, `GET /api/v1/dashboard` | Copy Account ID, view role/tenant | Always visible | Functional | Both |
| **Getting Started Onboarding Widget** | Step-by-step onboarding journey for new users | `projectsState`, `connectionsState`, `deploymentsState` | `GET /api/v1/projects`, `GET /api/v1/connections/*` | Click step action button (e.g. Create Project, Connect GitHub/AWS) | `lifecycleStage === 'stage_1_onboarding'` or new user state | Functional | New Users / Partially Onboarded |
| **Platform Metrics Overview Cards** | High-level counters (Total Projects, Environments, Active Connections, Deployments) | `projectsState`, `environmentsState`, `connectionsState`, `deploymentsState` | `/api/v1/projects`, `/api/v1/environments`, `/api/v1/connections/summary` | Click metric card to filter or navigate | `projectsCount > 0` | Functional | Existing Users |
| **Recent Projects Fleet Grid** | Displays recent project cards with status, type, region, and action buttons | `projectsState` | `GET /api/v1/projects` | Search projects, click project to open/configure, click "Create Project" | `projectsCount > 0` | Functional | Existing Users |
| **Target Environments Summary** | Lists deployed/configured environments across projects | `environmentsState` | `GET /api/v1/environments` or `GET /api/v1/projects/{id}/environments` | View environment status, health probe | `environmentsCount > 0` | Functional | Existing Users |
| **Attention Required & Risk Gate** | Surfaces failed deployments or unresolved risk/validation alerts | `deploymentsState`, `riskState` | `GET /api/v1/deployments`, risk API | Click action button to review or resolve failing items | Always visible if critical items exist | Functional | Existing Users |
| **Deployments Overview** | Summary of successful, failed, and in-progress deployments | `deploymentsState` | `GET /api/v1/deployments` | View deployment history, trigger new deployment | `deploymentsState.data.length > 0` | Functional | Existing Users |
| **Microservices Health Probes** | Live latency and status ping of gateway and core microservices (8000–8012) | Local fetch probes | `GET http://localhost:<port>/health` | Monitor microservice health status | Always visible | Functional | Both |
| **Recent Activity Log & Sessions** | Chronological audit log of user logins, sessions, and platform actions | `authApi.getSessions()` | `GET /api/v1/auth/sessions` | Revoke session, filter audit logs by event type or query | Always visible | Functional | Both |
| **Recommendations Engine** | Context-aware intelligent banner suggesting the next logical workflow step | Computed from dashboard state & summary | `/api/v1/dashboard` | Click primary recommended action button | Always visible | Functional | Both (Adaptive) |
| **Widget Customizer Modal** | Allows toggling widget visibility, resizing (half/full), and drag/drop ordering | Local state & `localStorage` / preferences API | `GET/PUT /api/v1/dashboard/preferences` | Customize dashboard layout and saved preferences | Click "Customize Dashboard" | Functional | Existing Users |

---

## 4. API Endpoints & Data Sources Audit

1. **Auth & Sessions**:
   - `GET /api/v1/auth/me`: Authenticated user profile and tenant metadata.
   - `GET /api/v1/auth/sessions`: Active sessions and audit logs.
   - `POST /api/v1/auth/logout`: Terminate session.
2. **Projects & Environments**:
   - `GET /api/v1/projects`: List tenant projects.
   - `POST /api/v1/projects`: Create project.
   - `GET /api/v1/projects/{id}/environments`: List project environments.
   - `POST /api/v1/projects/{id}/environments`: Create environment.
   - `GET /api/v1/environments`: List all environments across projects.
3. **Connections (Source & Cloud)**:
   - `GET /api/v1/connections/github`: GitHub connection status.
   - `GET /api/v1/connections/aws`: AWS connection status.
4. **Deployments & Operations**:
   - `GET /api/v1/deployments`: List deployments.
   - `GET /api/v1/dashboard`: Aggregate dashboard metrics and recommendations.
   - `GET /api/v1/dashboard/preferences`: Get user layout preferences.
   - `PUT /api/v1/dashboard/preferences`: Save layout preferences.

---

## 5. Current Problems & Missing Functionality

1. **Binary Onboarding vs Operational Split**: Previously, the dashboard relied heavily on widget visibility flags without a cohesive, dedicated new-user welcome experience that guides through the exact 10-step cloud operations journey.
2. **Partially Onboarded Continuity**: Users with a GitHub connection but no project were occasionally dropped into an empty operational metrics view rather than a guided continuation step.
3. **Project Context Selectors**: While global metrics exist, quick-switching project context directly from the dashboard header was limited or disjointed across certain modules.
4. **Tenant Isolation Verification**: Must rigorously ensure all project and environment queries strictly enforce tenant/user authorization headers and prevent cross-tenant data leaks.

---

## 6. Recommendations for New vs Existing Users

- **New Users (`stage_1_onboarding`)**:
  - Display prominent Welcome Banner explaining AetherOps.
  - Present the 10-step Guided Onboarding Journey (Project → Environment → GitHub → AWS → Code Analysis → Architecture → Validation → Terraform → Deployment → Monitoring).
  - Hide empty operational charts/metrics tables to prevent confusion.
  - Provide immediate 1-click CTAs for "Create Project", "Connect GitHub", "Connect AWS".
- **Existing Users (`stage_2_project_created` and beyond)**:
  - Display full Operational Dashboard (Metrics Overview, Project Fleet, Environment Summary, Deployment Status, System Health, Activity Log, and Customizer).
  - Context-aware Recommendations Engine guiding the next immediate action based on persisted state (e.g. "Validate Architecture", "Review Deployment Plan").
