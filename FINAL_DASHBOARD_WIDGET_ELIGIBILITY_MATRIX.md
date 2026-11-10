# AETHEROPS FINAL DASHBOARD WIDGET ELIGIBILITY MATRIX

## 1. Executive Summary

This matrix defines the precise eligibility rules, required backend data sources, empty states, loading behavior, and error handling for every widget on the AetherOps dashboard. Operational telemetry widgets are strictly gated to ensure brand-new users are never presented with misleading empty charts or idle status monitors.

---

## 2. Widget Eligibility Matrix

| Widget ID | Title | Eligible Lifecycle Stages | Required Backend Data | Empty-State Behavior | Loading Behavior | Error Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`getting_started`** | Getting Started & Workspace Setup | `stage_1_onboarding` | `projectsState` (count == 0) | Displays 10-step onboarding wizard | Animated pulse skeleton | Fallback static guide |
| **`overview_metrics`** | Platform Overview Metrics | Stage 2, Stage 3, Stage 4 | `projectsState`, `environmentsState`, `connectionsState`, `deploymentsState` | Displays 0 counts with actionable CTAs | Numeric spinner skeleton | Graceful zero-state fallback |
| **`recent_projects`** | Recent Projects Fleet | Stage 2, Stage 3, Stage 4 | `projectsState` (`projects.db`) | "No projects provisioned yet" with Create CTA | Card skeleton loader | Error banner with retry action |
| **`environments_summary`** | Target Environments Fleet | Stage 3, Stage 4 | `environmentsState` (`projects.db`) | "No target environments configured" | List placeholder skeleton | Error alert with link |
| **`deployments_overview`** | Deployments & Telemetry | Stage 4 Only (`stage_4_active_operations`) | `deploymentsState` (`application_deployment_service`) | Hidden until active operations | Row skeleton loader | "Deployments service offline" notice |
| **`attention_required`** | Attention Required & Risk Gate | All Stages (Critical Alerts Only) | Deployments & Risk APIs | Hidden when no critical alerts exist | Suppressed until loaded | Suppressed on failure |
| **`system_health`** | Platform Microservices Health | Stage 2, Stage 3, Stage 4 | Local health probes (Ports 8000–8011) | Shows service ping status | Pulsing probe status | "DEGRADED" / "OFFLINE" badge |
| **`recent_activity`** | Recent Activity & Audit | Stage 2, Stage 3, Stage 4 | Auth sessions & Audit history API | "No recent audit events" | Activity item skeletons | Error retry state |
| **`recommendations`** | Lifecycle Recommendations Engine | All Stages (Adaptive) | Computed dashboard summary & lifecycle stage | Displays contextual next action | Banner skeleton | Default setup recommendation |

---

## 3. Key Governance Rules

1. **No Hardcoded Operational Eligibility**: Operational widgets (e.g. `deployments_overview`, `overview_metrics`) are gated by concrete backend evidence (`total_projects > 0`, `lifecycle_stage === 'stage_4_active_operations'`).
2. **Critical Security Alerts**: `attention_required` remains active across all stages if critical security or deployment failures occur.
3. **Graceful Loading & Error Handling**: Every widget provides dedicated skeleton loading states and explicit error distinction (distinguishing between empty resources and service communication errors).
