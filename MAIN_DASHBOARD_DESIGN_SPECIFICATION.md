# AETHEROPS — MAIN DASHBOARD DESIGN SPECIFICATION

**Document:** `MAIN_DASHBOARD_DESIGN_SPECIFICATION.md`  
**Project:** AetherOps  
**Scope:** Main Platform Dashboard  
**Status:** DESIGN APPROVED FOR IMPLEMENTATION  

## 1. Objective
Build a single, lifecycle-driven Main Dashboard that dynamically adapts its content, sections, recommendations and primary actions to the actual progress of each user's AetherOps workspace.

## 2. Core Architectural Principle
- **Lifecycle** determines the dashboard experience.
- **User permissions** determine available actions.
- **User persona** determines the appropriate level of explanation and presentation preferences.

## 3. Supported User Personas
- Beginner / Student
- Software Developer
- DevOps / Cloud Engineer
- Administrator

## 4. Dashboard Lifecycle States
- L00 FIRST_VISIT
- L01 NO_PROJECTS
- L02 PROJECT_SETUP
- L03 ENVIRONMENT_SETUP
- L04 CONNECTION_SETUP
- L05 READY_FOR_ANALYSIS
- L06 ANALYSIS_IN_PROGRESS
- L07 ARCHITECTURE_REVIEW
- L08 PRE_DEPLOYMENT
- L09 DEPLOYMENT_IN_PROGRESS
- L10 ACTIVE_OPERATIONS
- L11 ATTENTION_REQUIRED
- L12 RETURNING_USER

## 5. Persistent Application Shell
Maintains the full-width global top bar, left navigation sidebar, profile/account modals, and responsive navigation without duplication.

## 6. Adaptive Components
- WelcomeSection
- NextActionPanel
- ProjectOverview
- ProjectCard
- LifecycleProgress
- EnvironmentOverview
- ConnectionOverview
- ActivityTimeline
- AttentionPanel
- QuickActions
- DashboardSkeleton
- DashboardEmptyState

## 7. Next Best Action Engine
Dynamically resolves the primary recommended engineering action based on confirmed backend workspace data.
