# AETHEROPS MAIN DASHBOARD FORENSIC AUDIT

## 1. Actual Dashboard URL & Entry Point
- **URL Path**: `/`, `/app`, `/dashboard` (served by `services/gateway/app/main.py` which returns the compiled React SPA shell `frontend/dist/index.html`).
- **Initial View Resolution**: `frontend/src/pages/DashboardPage.jsx` uses `getInitialView()` to map URL pathname (`/`, `/dashboard`) to `dashboard` (rendering `DashboardOverview.jsx`).

## 2. Actual Rendered Component & Component Tree
- **Component Tree**:
  - `App.jsx` (`AuthProvider` → `AppContent`)
  - `DashboardPage.jsx` (Sidebar + Navbar + Active View Switcher)
  - `DashboardOverview.jsx` (Adaptive Dashboard Overview module)
- **Active Module Views**: Depending on navigation selection, renders `DashboardOverview`, `ProjectEnvironmentView`, `SourceCloudView`, `ArchitectureView`, `IacView`, `DeploymentsView`, `MonitoringView`, etc.

## 3. API Integration Status
- **Endpoints Integrated**:
  - `GET /api/v1/dashboard`: Fetches lifecycle stage, summary metrics, and recommended action.
  - `GET /api/v1/dashboard/preferences`: Fetches user layout preferences.
  - `PUT /api/v1/dashboard/preferences`: Saves layout preferences.
  - `POST /api/v1/dashboard/preferences/reset`: Resets layout preferences.
- **Client Integration**: `dashboardApi` in `frontend/src/services/api.js` connects directly to these endpoints inside `fetchAllDashboardData()` in `DashboardOverview.jsx`.

## 4. Lifecycle Computation & Widget Visibility Matrix
- **Lifecycle Stage Rules (`DashboardOverview.jsx`)**:
  - `stage_1_onboarding`: `projectsCount === 0`
  - `stage_2_project_created`: `environmentsCount === 0`
  - `stage_3_infrastructure_workflow`: `deploymentsCount === 0`
  - `stage_4_active_operations`: `deploymentsCount > 0`
- **Widget Eligibility**:
  - `getting_started`: `lifecycleStage === 'stage_1_onboarding'`
  - `overview_metrics`: `projectsCount > 0`
  - `recent_projects`: `projectsCount > 0`
  - `environments_summary`: `environmentsCount > 0`
  - `deployments_overview`, `attention_required`, `system_health`, `recent_activity`, `recommendations`: `true`

## 5. Authentication Redirect Analysis
- `LoginPage.jsx` handles email/password login, Google OAuth, and GitHub OAuth popups/callbacks.
- Successful authentication updates `AuthContext` state (`isAuthenticated = true`), causing `App.jsx` to render `DashboardPage` which defaults to `/dashboard`.

## 6. Root Cause Analysis
- **Why dashboards previously appeared static or unadapted**:
  1. Default widget eligibility for system health, deployment overview, and recent activity was hardcoded to `true` even for brand-new users in `stage_1_onboarding`, causing monitoring/telemetry cards to display alongside onboarding.
  2. Lifecycle transition from stage 2 to 3 depended strictly on `deploymentsCount === 0`, bypassing intermediate states where projects and environments exist but source/cloud connections have not yet been fully verified.
- **Remediation Plan**: Refine widget eligibility rules in `DashboardOverview.jsx` so new users see a focused onboarding experience, and existing users see the appropriate operational modules based on persisted backend state.
