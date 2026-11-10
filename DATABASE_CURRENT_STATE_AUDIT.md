# AetherOps Complete Database Architecture Audit

**Audit Date:** November 2026  
**Repository Path:** `/home/ubuntu/aetherops`  
**Execution Mode:** Read-Only Dynamic & Static Code Investigation  
**Auditor:** Senior Database Architect, Principal Backend Engineer, DRE & Distributed Systems Auditor  

---

## 1. Executive Summary

This document presents a comprehensive technical audit of the database architecture across the multi-service AetherOps cloud automation platform. AetherOps is structured as a modular microservices architecture utilizing FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, SQLite (local development and fallback), and PostgreSQL 15+ (production schema isolation via search paths).

### Key Architectural Findings:
1. **Hybrid Persistence Strategy**: Each microservice maintains its own isolated SQLAlchemy `Base`, database engine, and connection pool. Services use local SQLite database files (e.g., `projects.db`, `source_connection.db`, `admin.db`, `iac.db`, `architecture.db`) by default and PostgreSQL when configured.
2. **PostgreSQL Schema Isolation**: Production PostgreSQL engines connect to a single PostgreSQL cluster instance but route operations to isolated logical schemas (e.g., `search_path: "source_connection", public`, `project_manager`, `admin`, `iac`, `architecture`) using connection string parameters and event listeners.
3. **Dual-Write / Fallback Patterns**: In several services (e.g., `project_and_environment_management` and `admin_console`), dual persistence pathways (SQLite security DB + PostgreSQL primary DB) are initialized during startup.
4. **Decentralized Data Ownership**: Cross-service references (e.g., `project_id`, `tenant_id`, `user_id`) are maintained across independent databases via string UUIDs (`String(36)`) without distributed foreign key constraints.

---

## 2. Repository Discovery

A thorough scan of `/home/ubuntu/aetherops` reveals the following repository directory layout and database-related modules:

```text
aetherops/
├── main.py
├── pyproject.toml
├── uv.lock
├── migrations/
│   ├── cli.py
│   ├── runner.py
│   └── versions/
│       ├── v20261027_02_crypto_envelope.py
│       └── v20261012_01_user_uuid_and_tenants.py
├── services/
│   ├── admin_console/app/ (database.py, models.py, auth.py)
│   ├── architecture_generator/app/ (database.py, models.py)
│   ├── cloud_deployer/app/ (crypto_envelope.py)
│   ├── gateway/app/ (main.py)
│   ├── iac_generator/app/ (database.py, models.py)
│   ├── observability_setup/app/ (observability_engine.py)
│   ├── project_and_environment_management/app/ (database.py, models.py, auth.py)
│   ├── repo_analyzer_service/app/ (universal_scanner.py)
│   └── source_and_cloud_connection/app/ (database.py, models.py, auth.py)
└── shared/
    └── aetherops_common/ (secrets.py)
```

---

## 3. Implemented Service Inventory

| Service Name | Directory | Implementation Status | Port | Primary DB Dependencies | Database Config Files | ORM Base |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **API Gateway** | `services/gateway/` | Implemented | 8000 | Redis (optional) / Proxy | `services/gateway/app/main.py` | N/A |
| **Project & Environment Manager** | `services/project_and_environment_management/` | Implemented | 8001 | SQLite / PostgreSQL + Admin SQLite | `services/project_and_environment_management/app/database.py` | `Base` (`models.py`) |
| **Source & Cloud Connection** | `services/source_and_cloud_connection/` | Implemented | 8002 | SQLite / PostgreSQL + Admin SQLite | `services/source_and_cloud_connection/app/database.py` | `Base` (`models.py`) |
| **Repo Analyzer Service** | `services/repo_analyzer_service/` | Implemented | 8003 | AST / Scanner / Stateless | `services/repo_analyzer_service/app/` | N/A |
| **AI AWS Architecture Generator** | `services/architecture_generator/` | Implemented | 8004 | SQLite / PostgreSQL | `services/architecture_generator/app/database.py` | `Base` (`models.py`) |
| **IaC Generator** | `services/iac_generator/` | Implemented | 8005 | SQLite / PostgreSQL | `services/iac_generator/app/database.py` | `Base` (`models.py`) |
| **Cloud Deployer & Risk Engine** | `services/cloud_deployer/` | Implemented | 8007 | In-Memory / State Files | `services/cloud_deployer/app/deployer_engine.py` | N/A |
| **Observability Service** | `services/observability_setup/` | Implemented | 8008 | Metrics Engine / In-Memory | `services/observability_setup/app/` | N/A |
| **Admin & Credential Console** | `services/admin_console/` | Implemented | 8010 | SQLite / PostgreSQL + Admin SQLite | `services/admin_console/app/database.py` | `Base` (`models.py`) |

---

## 4. Complete Database Inventory

| Storage Technology | Purpose | Location / Connection String Pattern | Services Using It | Persistence Characteristics |
| :--- | :--- | :--- | :--- | :--- |
| **SQLite (`aiosqlite`)** | Local dev / fallback relational state | `sqlite+aiosqlite:///projects.db`, `sc.db`, `arch.db`, `iac.db`, `admin.db` | All core microservices | Persistent on local disk; recreated if missing or via `create_all()`. |
| **PostgreSQL (`asyncpg`)** | Production multi-tenant relational persistence | `postgresql+asyncpg://user:pass@host:5432/db` (isolated schemas) | All core microservices | Highly durable; transactional; ACID compliant. |
| **Redis** | Caching, session coordination, pub/sub | `redis://localhost:6379/0` (when configured) | Gateway, Auth, Deployer | Volatile / TTL-based cache and ephemeral state. |
| **Local Filesystem / State** | Terraform state locks, crypto envelopes | Local disk / JSON files | Cloud Deployer, IAC Generator | File-based state. |

---

## 5. SQLite Audit

- **Files Discovered**: Local files such as `projects.db`, `sc.db`, `architecture.db`, `iac.db`, `admin.db`, `pm_admin_security.db`, `sc_admin.db`.
- **Engine Configuration**: Created via `create_async_engine(url, echo=ECHO_SQL, future=True, connect_args={"check_same_thread": False})`.
- **Asynchronous Access**: Accessed via SQLAlchemy 2.0 `AsyncSession` and `async_sessionmaker` with `aiosqlite`.
- **Initialization**: Automatic table creation (`Base.metadata.create_all`) triggered during service lifespan startup (`@app.on_event("startup")` or lifespan async context manager).

---

## 6. PostgreSQL Audit

- **Connection Pattern**: Dynamic URL construction (`get_postgres_url()`) checking environment variables (`DATABASE_URL`, `POSTGRES_URL`, or assembled from components).
- **Engine Configuration**: Configured with `pool_size=5`, `max_overflow=10`, `pool_pre_ping=True`, and `connect_args={"command_timeout": 10, "server_settings": {"search_path": '"{schema}", public'}}`.
- **Transaction Handling**: Managed through async context managers `async with session.begin():` or explicit `session.commit()` / `session.rollback()`.

---

## 7. Redis Audit

- **Configuration**: Optional Redis connection strings sourced from environment variables.
- **Usage**: Used for pub/sub logging, rate limiting hooks, and state coordination. Core relational entities (projects, environments, deployments, approvals) are persisted in relational databases (`SQLite` or `PostgreSQL`), not Redis.

---

## 8. Complete Table & Schema Inventory

### Service: Project & Environment Management (`services/project_and_environment_management/app/models.py`)
- `aether_tenants`: Workspace isolation boundaries (`id`, `name`, `slug`, `tenant_type`, `status`, `created_at`, `updated_at`).
- `aether_tenant_memberships`: Tenant user roles (`id`, `tenant_id`, `user_id`, `role`, `status`, `created_at`, `updated_at`).
- `aether_projects`: Top-level deployment boundary (`id`, `name`, `description`, `project_type`, `owner`, `tenant_id`, `created_by_user_id`, `account_id`, `status`, `environment_count`, timestamps).
- `aether_environments`: Deployment tiers (`id`, `project_id`, `tenant_id`, `name`, `type`, `aws_region`, `account_id`, `status`, `variables`, timestamps).

### Service: Source & Cloud Connection (`services/source_and_cloud_connection/app/models.py`)
- `github_connections`: GitHub OAuth / PAT integrations (`id`, `project_id`, `environment_id`, `repo_url`, `branch`, `status`, credentials, timestamps).
- `aws_connections`: AWS IAM role / access key credentials (`id`, `project_id`, `environment_id`, `aws_region`, `role_arn`, `status`, encrypted credentials, timestamps).

### Service: Architecture Generator (`services/architecture_generator/app/models.py`)
- `architecture_versions`: Saved architecture topologies (`id`, `project_id`, `environment_id`, `version_number`, `status`, `nodes_json`, `edges_json`, `resource_inventory`, `monthly_cost_usd`, timestamps).
- `architecture_reviews`: Well-Architected review records (`id`, `version_id`, `project_id`, `status`, `findings_json`, timestamps).

### Service: IaC Generator (`services/iac_generator/app/models.py`)
- `iac_plans`: Generated Terraform HCL artifacts (`id`, `project_id`, `environment_id`, `architecture_version_id`, `terraform_version`, `files_json`, `digest`, timestamps).

### Service: Admin & Credential Console (`services/admin_console/app/models.py`)
- `admin_users`: Platform users and RBAC credentials (`uuid`, `username`, `email`, `password_hash`, `role`, `is_active`, timestamps).

---

## 9. Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    Tenant ||--o{ TenantMembership : contains
    Tenant ||--o{ AetherProject : owns
    AetherProject ||--o{ AetherEnvironment : contains
    AetherEnvironment ||--o{ GithubConnection : has
    AetherEnvironment ||--o{ AwsConnection : has
    AetherEnvironment ||--o{ ArchitectureVersion : generates
    ArchitectureVersion ||--o{ ArchitectureReview : reviewed
    ArchitectureVersion ||--o{ IacPlan : synthesizes
    AdminUser ||--o{ TenantMembership : member
```

---

## 10. Service-to-Database Dependency Diagram

```mermaid
graph TD
    Client[FastAPI Client / Gateway Port 8000] -->|Proxy| PM[Project Manager Port 8001]
    Client -->|Proxy| SC[Source & Cloud Connection Port 8002]
    Client -->|Proxy| Arch[Architecture Generator Port 8004]
    Client -->|Proxy| IAC[IaC Generator Port 8005]
    Client -->|Proxy| Deploy[Cloud Deployer Port 8007]
    Client -->|Proxy| Admin[Admin Console Port 8010]

    PM -->|Async SQLAlchemy| PM_DB[(projects.db / pg_schema)]
    SC -->|Async SQLAlchemy| SC_DB[(sc.db / pg_schema)]
    Arch -->|Async SQLAlchemy| Arch_DB[(architecture.db / pg_schema)]
    IAC -->|Async SQLAlchemy| IAC_DB[(iac.db / pg_schema)]
    Admin -->|Async SQLAlchemy| Admin_DB[(admin.db / pg_schema)]
```

---

## 11. Database Connection Architecture

Each service factory implements `get_sqlite_engine()` and `get_postgres_url()` in its respective `app/database.py`. Engines are initialized lazily upon first request or application startup, injecting an `AsyncSession` into FastAPI route dependencies (`db: AsyncSession = Depends(get_db)`).

---

## 12. SQLite / PostgreSQL Consistency Analysis

- **Switching Mechanism**: Determined at runtime by the presence of `DATABASE_URL` or `POSTGRES_URL` environment variables. If present, PostgreSQL is used; otherwise, SQLite is used.
- **Dual-Write Risks**: Services maintain separate database files, eliminating cross-service transaction locks. However, where admin security tables are maintained alongside primary tables, dual initialization requires careful bootstrap ordering.

---

## 13. Data Ownership & Relationships

- **Tenant / Account**: Owned by `admin_console` and `project_and_environment_management`.
- **Project & Environment**: Owned exclusively by `project_and_environment_management`.
- **Source & Cloud Connections**: Owned by `source_and_cloud_connection`.
- **Architecture & Reviews**: Owned by `architecture_generator`.
- **IaC Plans**: Owned by `iac_generator`.

---

## 14. Authentication & Security Audit

- **Passwords**: Secured using `bcrypt` password hashing via `passlib` or direct `bcrypt` in `auth.py`.
- **JWT**: Stateless JWT access tokens signed with a secret key; subjects verified against `admin_users` or tenant context.
- **Isolation**: Multi-tenant isolation is enforced via `tenant_id` foreign keys and query filters across services.

---

## 15. Transactions & Data Integrity

- **Transactions**: Managed using explicit async session commits (`await session.commit()`) and rollbacks (`await session.rollback()`) within `try/except` blocks.
- **Idempotency**: Implemented on critical paths (e.g., project creation, tenant initialization, environment provisioning) using unique constraints (`slug`, `email`).

---

## 16. Migration Architecture

- **Alembic**: Managed via `migrations/` directory with custom runner scripts (`migrations/runner.py`, `migrations/cli.py`) supporting both SQLite and PostgreSQL dialects.
- **Startup Auto-Creation**: Individual services also utilize `Base.metadata.create_all()` on startup as a fallback for local development convenience.

---

## 17. Cache Consistency Analysis

- **Redis Caching**: Used purely as an ephemeral coordination and rate-limiting layer.
- **Source of Truth**: Relational databases (`SQLite` / `PostgreSQL`) remain the absolute source of truth for all projects, environments, architectures, and deployments.

---

## 18. Performance & Reliability Assessment

- **Async IO**: Complete asynchronous stack (`FastAPI` + `SQLAlchemy 2.0` + `aiosqlite` / `asyncpg`) prevents thread blocking under concurrent load.
- **Connection Pooling**: PostgreSQL engines configure pool sizes (`pool_size=5`, `max_overflow=10`, `pool_pre_ping=True`) to handle connection drops gracefully.

---

## 19. Cross-Service Data Flow

Data flows strictly via REST / HTTP JSON APIs between microservices. For example:
1. User creates a project in `project_and_environment_management`.
2. Project ID is passed to `source_and_cloud_connection` for credential binding.
3. Project & Environment IDs are passed to `architecture_generator` for topology synthesis.
4. Architecture Version ID is passed to `iac_generator` for Terraform HCL generation.
5. Final plan and digests are passed to `cloud_deployer` for dry-run risk analysis and approval gates.

---

## 20. Current Architecture Diagram

```mermaid
graph LR
    subgraph Client Tier
        UI[Frontend SPA / React]
    end

    subgraph API Gateway (Port 8000)
        GW[FastAPI Reverse Proxy & Router]
    end

    subgraph Microservices Tier
        M1[Project Manager :8001]
        M2[Source & Cloud :8002]
        M3[Repo Analyzer :8003]
        M4[Architecture Generator :8005]
        M5[IaC Generator :8005]
        M6[Cloud Deployer :8007]
        M7[Admin Console :8010]
    end

    subgraph Storage Tier
        DB1[(SQLite / PG Schema 1)]
        DB2[(SQLite / PG Schema 2)]
        DB3[(SQLite / PG Schema 3)]
        Redis[(Redis Cache)]
    end

    UI --> GW
    GW --> M1 & M2 & M3 & M4 & M5 & M6 & M7
    M1 --> DB1
    M2 --> DB2
    M4 & M5 --> DB3
    GW -.-> Redis
```

---

## 21. Implemented vs Planned Comparison

| Capability | Implemented State | Planned / Stub State |
| :--- | :--- | :--- |
| **Relational Storage** | Fully implemented via SQLAlchemy async models & SQLite/PostgreSQL. | Unified global PostgreSQL cluster with cross-schema FKs. |
| **Migrations** | Custom Alembic runner and migration scripts. | Automated CI/CD database migration pipelines. |
| **Caching & Pub/Sub** | Redis hooks and ephemeral caching. | Distributed multi-region Redis cluster. |

---

## 22. Prioritized Problems & Risks

| Finding ID | Severity | Affected Service | Description & Consequence | Recommended Direction |
| :--- | :--- | :--- | :--- | :--- |
| **DB-01** | MEDIUM | All Services | Decentralized databases lack cross-service foreign keys, relying entirely on application-level UUID validation. | Introduce logical schema governance or planned unified PostgreSQL foreign keys. |
| **DB-02** | LOW | Local Dev | Dual SQLite initialization (`create_all` vs Alembic migrations) can cause schema drift if not synchronized. | Standardize startup initialization to use Alembic migrations exclusively in production. |

---

## 23. Future Unified Database Requirements

A future unified database architecture must support:
- Multi-tenant workspace isolation (`tenants`, `tenant_memberships`).
- Complete hierarchical resource mapping (Account → Projects → Environments → Connections → Architectures → Validations → IaC Plans → Deployments → Audit History).
- High availability, ACID compliance, and relational integrity via PostgreSQL.

---

## 24. Architectural Recommendations

1. **Retain Async SQLAlchemy 2.0**: The existing async pattern (`AsyncSession`, `async_sessionmaker`) provides robust performance and clean dependency injection.
2. **Standardize on PostgreSQL for Production**: Ensure production deployments uniformly configure PostgreSQL with dedicated logical schemas per domain service.
3. **Centralize Migration Management**: Unify migration execution under a single Alembic root to manage all service domains cohesively.

---

## 25. Questions Requiring Human Decisions

1. Should production environments migrate from isolated microservice database files/schemas to a single centralized PostgreSQL database with explicit foreign key relationships across domains?
2. Should Redis be adopted as the mandatory caching and session store across all multi-tenant deployments?

---

## 26. Final Audit Conclusion

The existing AetherOps database architecture is well-structured around asynchronous SQLAlchemy 2.0 models, offering flexible deployment across local SQLite files and production PostgreSQL schemas. Cross-service data separation is cleanly maintained via UUIDs and REST APIs. The repository is fully prepared for higher-level architectural consolidation when required.
