# AetherOps Canonical Database Architecture

**Target Database:** PostgreSQL 15 (`aetherops` / `aether_catalog`)  

---

## 1. Domain-Oriented Logical Schemas
To ensure clean separation of concerns and enterprise maintainability, the single PostgreSQL database is organized into domain schemas:

| Schema | Responsibility |
|---|---|
| `identity` | Users, authentication identities, sessions, audit logs |
| `workspace` | Accounts, projects, environments, dashboard preferences |
| `source_control` | GitHub connections, repositories, branches, snapshots |
| `cloud` | AWS accounts, IAM role associations, regions, connection metadata |
| `architecture` | Architecture versions, graph topologies, studio sessions |
| `infrastructure` | Generated Terraform IaC bundles |
| `execution` | Approvals, execution history, deployment operations |
| `audit` | Immutable operation logs and evidence event ledgers |

---

## 2. Constraints & Standards
- **Identifiers:** Primary UUIDs with surrogate auto-incrementing IDs where appropriate.
- **Timestamps:** Timezone-aware PostgreSQL timestamps (`TIMESTAMPTZ`).
- **Referential Integrity:** Enforced foreign key constraints with explicit cascade/restrict policies.
- **Security:** Connection pooling, least-privilege roles, and encrypted credential storage.
