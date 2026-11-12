# AetherOps Database Discovery and Inventory Report

**Date:** November 11, 2026  
**Target Database:** PostgreSQL 15 (`aether_catalog` / `aetherops`)  

---

## 1. Executive Summary
A comprehensive repository audit discovered 29 SQLite database instances (runtime and test/catalog artifacts) and an active PostgreSQL 15 container (`aether_postgres`). This report catalogs all discovered database assets, service ownership, table schemas, and record counts.

---

## 2. SQLite Database Inventory

| Database Path | Owning Service | Key Tables | Record Count Summary |
|---|---|---|---|
| `./services/auth_service/app/auth.db` | Auth Service | `users`, `tenants`, `user_sessions`, `session_audit_logs`, `email_verifications` | Users: 21, Sessions: 92, Tenants: 21 |
| `./services/project_environment_service/projects.db` | Project Manager | `aether_projects`, `aether_environments`, `aether_tenants` | Projects: 2, Environments: 3, Tenants: 1 |
| `./services/source_cloud_git_service/source_connections.db` | Source & Cloud | `sc_git_connections`, `sc_cloud_connections`, `sc_source_snapshots` | Git Conns: 0, Cloud Conns: 0 |
| `./services/architecture_designer/architecture.db` | Architecture Designer | `architecture_versions`, `studio_sessions` | Versions: 0, Sessions: 0 |
| `./services/admin_console/admin_security.db` | Admin Console | `admin_users`, `admin_audit_logs`, `ec2_catalog`, `rds_catalog` | Admin Users: 1, Catalogs: regional tables |

---

## 3. PostgreSQL Discovery
- **Container:** `aether_postgres` (`postgres:15-alpine`)
- **Port:** `127.0.0.1:5432` (secured)
- **Databases:** `aether_catalog`, `postgres`, `template0`, `template1`
- **Volume:** `./data/postgres:/var/lib/postgresql/data` (persistent)

---

## 4. Service-to-Database Dependency Mapping
- **Auth Service:** Authoritative store for user identity, sessions, and authentication provider tracking (`auth.db` / PostgreSQL).
- **Project Manager:** Authoritative store for multi-tenant projects and environments (`projects.db` / PostgreSQL).
- **Source & Cloud Service:** Authoritative store for GitHub repositories and AWS connections.
- **Admin Console:** Authoritative store for AWS pricing catalogs and admin audit ledgers.
