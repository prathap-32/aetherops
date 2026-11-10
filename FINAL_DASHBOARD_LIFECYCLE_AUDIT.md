# AETHEROPS FINAL DASHBOARD LIFECYCLE AUDIT

## 1. Executive Summary

This audit establishes the definitive, deterministic lifecycle state machine for the AetherOps main dashboard. Lifecycle stages are derived directly from persisted backend evidence (`projects.db` and `source_connections.db`), preventing false operational classification and ensuring robust guidance across new-user onboarding, workspace configuration, connection validation, and active operations.

---

## 2. Deterministic Lifecycle Stages

### Stage 1 — New User Onboarding (`stage_1_onboarding`)
- **Backend Evidence**: `total_projects == 0`.
- **User State**: Brand-new user with no isolated workspace created.
- **Dashboard Experience**: Guided welcoming header, 10-step Getting Started onboarding journey, quick creation actions, and architecture workflow introduction. Telemetry and operational widgets are hidden.

### Stage 2 — Project Created (`stage_2_project_created`)
- **Backend Evidence**: `total_projects > 0` AND `total_environments == 0`.
- **User State**: Project workspace established, but target environments (Dev, Staging, Production) have not yet been provisioned.
- **Dashboard Experience**: Prompt to configure target deployment environments and link cloud/git resources.

### Stage 3 — Infrastructure & Connection Workflow (`stage_3_infrastructure_workflow`)
- **Backend Evidence**: `total_environments > 0` AND (`has_git_connection == False` OR `has_cloud_connection == False`).
- **User State**: Environments exist, but GitHub repository verification or AWS IAM role authorization is incomplete or pending.
- **Dashboard Experience**: Guided source/cloud connection workflow, highlighting missing credentials or repository verification steps.

### Stage 4 — Active Operations (`stage_4_active_operations`)
- **Backend Evidence**: `total_environments > 0` AND `has_git_connection == True` AND `has_cloud_connection == True`.
- **User State**: Fully onboarded user with provisioned environments and verified source/cloud credentials.
- **Dashboard Experience**: Professional cloud operations control center featuring platform metrics, recent project fleet, environments summary, deployments overview, system health probes, and audit history.

---

## 3. Multi-Project & Multi-Environment Aggregation Rules

- When a user manages multiple projects and environments, connection verification (`sc_git_connections` and `sc_cloud_connections`) is aggregated across active project boundaries.
- A completed environment in one project does not mask an unconfigured environment in another; the lifecycle rule evaluates overall tenant state to ensure every required workflow step is completed before advancing to Stage 4.
