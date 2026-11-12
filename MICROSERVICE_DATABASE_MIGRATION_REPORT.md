# Microservice Database Migration Report

**Date:** November 11, 2026  

---

## 1. Microservices Audit & Migration Status

| Service Name | Port | Previous Persistence | New Persistence | Status |
|---|---|---|---|---|
| Auth Service | 7999 | SQLite (`auth.db`) | PostgreSQL / SQLite | MIGRATED & VERIFIED |
| API Gateway | 8000 | Redis / Proxy | Redis / Proxy | VERIFIED |
| Project Manager | 8001 | SQLite (`projects.db`) | PostgreSQL / SQLite | MIGRATED & VERIFIED |
| Source & Cloud | 8002 | SQLite (`source_connections.db`) | PostgreSQL / SQLite | MIGRATED & VERIFIED |
| Source Analyzer | 8003 | In-Memory / SQLite | PostgreSQL / SQLite | MIGRATED & VERIFIED |
| Architecture Engine | 8004 | SQLite | PostgreSQL / SQLite | MIGRATED & VERIFIED |
| Architecture Studio | 8005 | SQLite (`architecture.db`) | PostgreSQL / SQLite | MIGRATED & VERIFIED |
| Architecture Validation | 8006 | SQLite | PostgreSQL / SQLite | MIGRATED & VERIFIED |
| Risk Engine | 8007 | SQLite | PostgreSQL / SQLite | MIGRATED & VERIFIED |
| Terraform IaC Generator | 8008 | SQLite (`iac.db`) | PostgreSQL / SQLite | MIGRATED & VERIFIED |
| Approval Service | 8009 | SQLite | PostgreSQL / SQLite | MIGRATED & VERIFIED |
| App Deployment | 8010 | SQLite | PostgreSQL / SQLite | MIGRATED & VERIFIED |
| Monitoring Service | 8011 | SQLite | PostgreSQL / SQLite | MIGRATED & VERIFIED |
| Audit History | 8012 | SQLite | PostgreSQL / SQLite | MIGRATED & VERIFIED |
| Admin Console | 8013 | SQLite (`admin_security.db`) | PostgreSQL / SQLite | MIGRATED & VERIFIED |
