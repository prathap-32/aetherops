# AetherOps Service Inventory

| Service Name | Repository Directory | Port | Responsibility | Database Schema | Status |
|---|---|---|---|---|---|
| Auth Service | `services/auth_service` | 7999 | Identity & JWT Authority | `identity` | Implemented & Verified |
| API Gateway | `services/gateway` | 8000 | Frontend SPA & Reverse Proxy | N/A | Implemented & Verified |
| Project Manager | `services/project_environment_service` | 8001 | Projects & Environments | `project_management` | Implemented & Verified |
| Source Cloud Git | `services/source_cloud_git_service` | 8002 | GitHub & AWS Connections | `source_connections`, `cloud_connections` | Implemented & Verified |
| Source Code Analyzer | `services/source_code_analyzer` | 8003 | Module 3 Source Intelligence | `source_analysis` | Upgrading for MVP |
| AI Architecture Engine | `services/ai_architecture_engine` | 8004 | Requirements & Sizing | `requirements` | Implemented & Verified |
| Architecture Designer | `services/architecture_designer` | 8005 | Cloud Architecture Studio | `architecture` | Implemented & Verified |
| Architecture Validation | `services/architecture_validation` | 8006 | Well-Architected Compliance | `architecture_validation` | Implemented & Verified |
| Risk Engine | `services/pre_deployment_risk_engine` | 8007 | Pre-Deployment Dry Run | `risk_assessment` | Implemented & Verified |
| Terraform IaC Generator | `services/terraform_iac_generator` | 8008 | Terraform HCL Synthesis | `iac_artifacts` | Implemented & Verified |
| Approval Service | `services/approval_execution_service` | 8009 | Approval Gates & Execution | `infrastructure_execution` | Implemented & Verified |
| App Deployment | `services/application_deployment_service` | 8010 | Deployment & Drift | `deployment` | Implemented & Verified |
| Monitoring Service | `services/monitoring_service` | 8011 | Observability & Metrics | `monitoring` | Implemented & Verified |
| Audit History | `services/audit_history_service` | 8012 | Immutable Event Ledger | `audit_history` | Implemented & Verified |
| Admin Console | `services/admin_console` | 8013 | Administrative Control Plane | `admin_security` | Implemented & Verified |
