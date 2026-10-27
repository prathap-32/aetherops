# AetherOps Authorization and Tenant Isolation Architecture

## 1. Multi-Tenant Domain Model

AetherOps models tenancy through a hierarchical four-tier structure:

```
+--------------------------------------------------------------+
|                         Account                              |
|  - Root billing and organizational unit (e.g. 109283746519)  |
+--------------------------------------------------------------+
                               |
                               v
+--------------------------------------------------------------+
|                         Tenant                               |
|  - Workspace boundary (PERSONAL or ORGANIZATION)             |
|  - Deterministic unique slug & UUID v4 identifier            |
+--------------------------------------------------------------+
                               |
                               v
+--------------------------------------------------------------+
|                         Project                              |
|  - Isolated system containing architecture & environments    |
|  - Strictly bound to a single tenant_id                      |
+--------------------------------------------------------------+
                               |
                               v
+--------------------------------------------------------------+
|                       Environment                            |
|  - Deployment tiers: development, staging, production, etc.  |
|  - Bound to project_id and tenant_id                         |
+--------------------------------------------------------------+
```

---

## 2. Role-Based Access Control (RBAC) Matrix

### 2.1 Tenant-Level Roles
- **OWNER**: Full administrative control over the tenant workspace, project lifecycle, cloud connections, and membership.
- **ADMIN**: Management of projects, environments, and deployments; restricted from deleting the workspace.
- **MEMBER**: Creation and management of assigned projects and environments.
- **VIEWER**: Read-only inspection of architectures, telemetry, and project metadata.

### 2.2 Platform Administration vs. Tenant Scope
- Platform administrative privileges (`SUPER_ADMIN`, `PLATFORM_ADMIN`) are evaluated strictly based on the cryptographically verified role in the user's session (`admin.get("role") in PLATFORM_SUPER_ADMIN_ROLES`).
- **No Username Escalation**: Checks evaluating `user_name in ("admin", "root_admin")` have been completely eradicated. A user named `"admin"` with role `"USER"` is strictly treated as an unprivileged user.

---

## 3. Enforcement Points & Boundary Protection

### 3.1 Gateway-Level Account & Tenant Consistency Check
When requests enter the API Gateway:
1. Client headers `X-Account-ID` and `X-Tenant-ID` are sanitized and stripped.
2. Verified claims `account_id` and `tenant_id` from the decoded JWT payload are evaluated.
3. If a client attempts to override the tenant header to an unauthorized tenant ID, the Gateway halts execution with `HTTP 403 Forbidden` (`Tenant isolation violation`).

### 3.2 Service-Level `TenantContext` Dependency
All protected endpoints in `project_and_environment_management` require the `get_tenant_context` dependency:
1. Resolves requested tenant boundary from `X-Tenant-ID` header or defaults to user's personal workspace.
2. Queries the database to verify active tenant membership and status (`TenantMembership.status == "ACTIVE"`).
3. Evaluates tenant suspension: Suspended tenants reject access with `HTTP 403 Forbidden`.
4. Downstream operations filter database queries explicitly by `tenant_id`:
   ```python
   query = select(AetherProject).where(
       (AetherProject.tenant_id == ctx.tenant.id)
       | ((AetherProject.tenant_id.is_(None)) & (AetherProject.owner == owner))
       | (AetherProject.owner == owner)
   )
   ```

### 3.3 Direct Object Reference (IDOR) Protections
- Accessing a project (`GET /api/v1/projects/{project_id}`) requires that `project.tenant_id == ctx.tenant.id` or that the requesting user is the creator.
- Unauthorized foreign-tenant project queries return `HTTP 404 Not Found` (rather than 403) to prevent resource enumeration.

---

## 4. Database-Level Isolation & Migrations

- **Dual-Engine Architecture**:
  - Primary Engine: PostgreSQL (`aether_catalog` / schema `project_manager`).
  - Fallback/Local Engine: SQLite with Write-Ahead Logging (`WAL` mode).
- **Schema Columns**:
  - `aether_tenants`: `id`, `name`, `slug`, `tenant_type`, `status`.
  - `aether_tenant_memberships`: `id`, `tenant_id`, `user_id`, `role`, `status`.
  - `aether_projects`: `id`, `tenant_id`, `created_by_user_id`, `owner`, ...
  - `aether_environments`: `id`, `project_id`, `tenant_id`, `created_by_user_id`, ...
- **Hermetic Test Isolation**: Tests execute against clean isolated SQLite instances (`test_projects.db`, in-memory sessions) ensuring zero cross-test leakage.
