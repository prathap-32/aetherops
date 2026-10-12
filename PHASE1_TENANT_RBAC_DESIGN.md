# AetherOps — Phase 1 Design Specification
# Multi-Tenant Identity, Role-Based Access Control (RBAC), and Cloud Credential Security Envelope
**Document:** `PHASE1_TENANT_RBAC_DESIGN.md`  
**Execution Mode:** Checkpoint 1 (Design Only — Strictly Non-Mutating)  
**Date:** October 12, 2026  
**Status:** Design Proposal — Awaiting Human Approval Before Implementation  

---

## 1. Executive Summary & Design Scope

This specification establishes the architectural, data-model, cryptographic, and operational design for **Phase 1** of AetherOps:
- **Multi-Tenant Identity & Workspaces**
- **Explicit Role-Based Access Control (RBAC)**
- **Reversible AES-256-GCM Cloud Credential Security Envelope**
- **GitHub Credential Vaulting & OAuth State Hardening**
- **Versioned Database Migrations (Alembic)**
- **Tamper-Evident Security Audit & Cross-Cutting Evidence Integration**

This design preserves all established Phase 0 security containment fixes, maintains strict backward compatibility with existing API contracts, protects deterministic sizing algorithms across all 39 SQLite-supported AWS regions, preserves architecture DAG layout generation, and guarantees zero unapproved cloud mutations.

---

## 2. Multi-Tenant Identity & Data Models

### 2.1 Entity Design: `Tenant` & `TenantMembership`

To transition from single-user string ownership (`owner = "username"`) to an enterprise multi-tenant model without breaking existing workflows, we introduce two primary entities in the core data layer:

```text
┌────────────────────────────────────────────────────────┐
│                        Tenant                          │
├────────────────────────────────────────────────────────┤
│ id: String(36) [UUIDv4 PK]                             │
│ name: String(100)                                      │
│ slug: String(100) [Unique Index]                       │
│ tenant_type: String(20) [PERSONAL | ORGANIZATION]      │
│ status: String(20) [ACTIVE | SUSPENDED | ARCHIVED]     │
│ created_at: DateTime [UTC]                             │
│ updated_at: DateTime [UTC]                             │
└──────────────────────────┬─────────────────────────────┘
                           │ 1
                           │
                           │ *
┌──────────────────────────┴─────────────────────────────┐
│                   TenantMembership                     │
├────────────────────────────────────────────────────────┤
│ id: String(36) [UUIDv4 PK]                             │
│ tenant_id: String(36) [FK -> Tenant.id, Index]         │
│ user_id: String(36) [FK -> AdminUser.uuid, Index]      │
│ role: String(30) [OWNER | ADMIN | MEMBER | VIEWER]     │
│ status: String(20) [ACTIVE | INVITED | SUSPENDED]      │
│ created_at: DateTime [UTC]                             │
│ updated_at: DateTime [UTC]                             │
│ UNIQUE(tenant_id, user_id)                             │
└────────────────────────────────────────────────────────┘
```

#### SQLAlchemy Model Definitions

```python
class Tenant(Base):
    __tablename__ = "aether_tenants"

    id          = Column(String(36),  primary_key=True, index=True) # UUID v4
    name        = Column(String(100), nullable=False)
    slug        = Column(String(100), nullable=False, unique=True, index=True)
    tenant_type = Column(String(20),  nullable=False, default="ORGANIZATION") # PERSONAL | ORGANIZATION
    status      = Column(String(20),  nullable=False, default="ACTIVE")       # ACTIVE | SUSPENDED | ARCHIVED
    created_at  = Column(DateTime,    nullable=False, default=datetime.datetime.utcnow)
    updated_at  = Column(DateTime,    nullable=False, default=datetime.datetime.utcnow,
                         onupdate=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "tenant_type": self.tenant_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TenantMembership(Base):
    __tablename__ = "aether_tenant_memberships"

    id         = Column(String(36), primary_key=True, index=True) # UUID v4
    tenant_id  = Column(String(36), nullable=False, index=True)
    user_id    = Column(String(36), nullable=False, index=True)   # Stable User UUID
    role       = Column(String(30), nullable=False, default="MEMBER") # OWNER | ADMIN | MEMBER | VIEWER
    status     = Column(String(20), nullable=False, default="ACTIVE") # ACTIVE | INVITED | SUSPENDED
    created_at = Column(DateTime,   nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime,   nullable=False, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", name="_uq_tenant_user_membership"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "role": self.role,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
```

---

## 3. Stable User Identity & Migration from String Ownership

### 3.1 Deficiency in Current Baseline
Currently, `AdminUser.id` is an autoincrement integer, but all domain tables (`AetherProject`, `GitConnection`, `CloudConnection`) link ownership via `owner = Column(String(100))` populated from the mutable username (`sub` claim). If a user edits their username or email via `PUT /api/v1/auth/profile`, their historical project linkage breaks.

### 3.2 Stable Identity Solution
1. **Add Immutable UUID to `AdminUser`:**
   Add `uuid = Column(String(36), unique=True, index=True, nullable=False)` to `AdminUser`.
   For existing accounts, `uuid` is backfilled deterministically:
   `uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"aetherops.user.{user.username}"))`.
2. **JWT Claims Enhancement:**
   ```json
   {
     "sub": "<user_uuid>",
     "username": "prathap",
     "email": "prathap@example.com",
     "role": "USER",
     "active_tenant_id": "<tenant_uuid>",
     "iat": 1776000000,
     "exp": 1776028800
   }
   ```
   `sub` holds the immutable UUID. The human username remains in `username` for display.

### 3.3 Personal Workspace Auto-Mapping Strategy
To ensure that existing projects remain accessible without manual data entry:
1. For every distinct user existing in `pm_admin_users` or historical `owner` string:
   - Create a personal workspace `Tenant`:
     - `id`: `str(uuid.uuid5(uuid.NAMESPACE_DNS, f"aetherops.personal_tenant.{username}"))`
     - `name`: `f"{username}'s Personal Workspace"`
     - `slug`: `f"personal-{username.lower()}"`
     - `tenant_type`: `"PERSONAL"`
     - `status`: `"ACTIVE"`
   - Create `TenantMembership`:
     - `user_id`: `user.uuid`
     - `tenant_id`: `personal_tenant.id`
     - `role`: `"OWNER"`
     - `status`: `"ACTIVE"`
2. **Schema Extension on Resource Tables:**
   Add `tenant_id = Column(String(36), nullable=True, index=True)` and `created_by_user_id = Column(String(36), nullable=True)` to:
   - `aether_projects`
   - `aether_environments`
   - `sc_git_connections`
   - `sc_cloud_connections`
3. **Data Backfill:**
   Execute SQL migration:
   ```sql
   UPDATE aether_projects p
   SET tenant_id = t.id,
       created_by_user_id = u.uuid
   FROM aether_tenants t
   JOIN aether_tenant_memberships tm ON tm.tenant_id = t.id
   JOIN pm_admin_users u ON u.uuid = tm.user_id
   WHERE p.owner = u.username AND t.tenant_type = 'PERSONAL';
   ```
4. **Preservation Guarantee:** The legacy `owner` column is preserved and retained as a secondary index during Phase 1. Existing queries referencing `owner` continue functioning seamlessly.

---

## 4. Role-Based Access Control (RBAC) Architecture

### 4.1 Role Hierarchy & Scopes

AetherOps establishes a clear division between **Platform Administrative Roles** and **Tenant Roles**:

```text
PLATFORM SCOPE:
  └── PLATFORM_SUPER_ADMIN (System maintenance, tenant lifecycle, platform audits)

TENANT SCOPE:
  └── TENANT_OWNER    (Complete control over tenant, billing, membership, all resources)
       └── TENANT_ADMIN   (Manage projects, environments, connections, credentials, members)
            └── TENANT_MEMBER  (Create & modify projects/environments, run dry-runs, view credentials metadata)
                 └── TENANT_VIEWER  (Read-only inspection of architectures, risks, and deployment statuses)
```

### 4.2 Comprehensive RBAC Permission Matrix

| Operation / Capability | PLATFORM_SUPER_ADMIN | TENANT_OWNER | TENANT_ADMIN | TENANT_MEMBER | TENANT_VIEWER |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Tenant Lifecycle** | | | | | |
| Create new Organization Tenant | ✅ | ✅ | ❌ | ❌ | ❌ |
| Suspend / Archive Tenant | ✅ | ✅ (Own) | ❌ | ❌ | ❌ |
| Update Tenant Name / Settings | ❌ (Unless break-glass) | ✅ | ✅ | ❌ | ❌ |
| Transfer Tenant Ownership | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Membership Management** | | | | | |
| Invite Members / Viewers | ❌ | ✅ | ✅ | ❌ | ❌ |
| Promote to TENANT_ADMIN | ❌ | ✅ | ❌ | ❌ | ❌ |
| Remove Member | ❌ | ✅ | ✅ (Members only) | ❌ | ❌ |
| View Member List | ✅ (Audit) | ✅ | ✅ | ✅ | ✅ |
| **Project & Environment Management** | | | | | |
| List Projects in Tenant | ✅ (All tenants) | ✅ | ✅ | ✅ | ✅ |
| Create Project / Environment | ❌ | ✅ | ✅ | ✅ | ❌ |
| Update Project / Environment | ❌ | ✅ | ✅ | ✅ (Owned/Assigned) | ❌ |
| Delete Project / Environment | ❌ | ✅ | ✅ | ❌ | ❌ |
| Advance Environment Lifecycle Status | ❌ | ✅ | ✅ | ✅ | ❌ |
| **Source & Cloud Connections** | | | | | |
| Connect GitHub (OAuth / PAT) | ❌ | ✅ | ✅ | ❌ | ❌ |
| Register AWS IAM Role / Account | ❌ | ✅ | ✅ | ❌ | ❌ |
| View Masked Connection Metadata | ✅ (Audit) | ✅ | ✅ | ✅ | ✅ |
| Revalidate Cloud Connection | ❌ | ✅ | ✅ | ✅ | ❌ |
| Delete Connection | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Credential Security Envelope** | | | | | |
| Store Cloud Credentials (AES-GCM) | ❌ | ✅ | ✅ | ❌ | ❌ |
| Rotate Vaulted Credentials | ❌ | ✅ | ✅ | ❌ | ❌ |
| Export Decrypted Credentials | ❌ (Strict Deny) | ❌ (Strict Deny) | ❌ (Strict Deny) | ❌ (Strict Deny) | ❌ (Strict Deny) |
| Ephemeral Decrypt for Deployment Runner | ❌ | ✅ (Via Worker) | ✅ (Via Worker) | ✅ (Via Worker) | ❌ |
| **Planning, IaC & Execution** | | | | | |
| Run Requirement Sizing & Analysis | ✅ | ✅ | ✅ | ✅ | ✅ |
| Generate Architecture Graph (DAG) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Generate Terraform Code | ✅ | ✅ | ✅ | ✅ | ❌ |
| Approve Infrastructure Mutation Plan | ❌ | ✅ | ✅ | ❌ | ❌ |
| Trigger Application Deployment | ❌ | ✅ | ✅ | ✅ | ❌ |
| **Audit & Documentation Engine** | | | | | |
| View Tenant Security Audit Logs | ✅ (System-wide) | ✅ | ✅ | ❌ | ❌ |
| Generate Signed Evidence Document | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 5. Authorization Enforcement & Middleware Across Microservices

### 5.1 Context-Aware Tenant Dependency

All tenant-scoped endpoints enforce authorization through a reusable FastAPI dependency: `get_current_tenant_context`.

```python
class TenantContext:
    def __init__(self, tenant: Tenant, user: AdminUser, role: str):
        self.tenant = tenant
        self.user = user
        self.role = role

    def require_role(self, *allowed_roles: str):
        if self.user.role == "SUPER_ADMIN":
            return  # Platform superadmin bypass for administrative oversight
        if self.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action requires one of roles: {', '.join(allowed_roles)}. Current role: '{self.role}'."
            )

async def get_current_tenant_context(
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: Dict[str, Any] = Depends(get_current_admin),
) -> TenantContext:
    user_uuid = admin.get("uuid") or admin.get("sub")
    platform_role = admin.get("role", "USER")

    # 1. Resolve requested tenant: Header -> Query Param -> Personal Tenant Fallback
    tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get("tenant_id")
    
    if not tenant_id:
        # Default to user's personal tenant
        personal_res = await db.execute(
            select(Tenant).join(TenantMembership, TenantMembership.tenant_id == Tenant.id)
            .where(TenantMembership.user_id == user_uuid, Tenant.tenant_type == "PERSONAL")
        )
        tenant = personal_res.scalar_one_or_none()
        if not tenant:
            raise HTTPException(status_code=400, detail="No active tenant context provided and no personal workspace found.")
        tenant_id = tenant.id
        membership_role = "OWNER"
    else:
        # 2. Verify Tenant exists and is active
        t_res = await db.execute(select(Tenant).where(Tenant.id == tenant_id, Tenant.status == "ACTIVE"))
        tenant = t_res.scalar_one_or_none()
        if not tenant:
            raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' not found or suspended.")

        # 3. Verify Membership and Active Status
        if platform_role == "SUPER_ADMIN":
            membership_role = "OWNER"  # Superadmin treated as owner for inspection
        else:
            m_res = await db.execute(
                select(TenantMembership).where(
                    TenantMembership.tenant_id == tenant_id,
                    TenantMembership.user_id == user_uuid,
                    TenantMembership.status == "ACTIVE"
                )
            )
            membership = m_res.scalar_one_or_none()
            if not membership:
                raise HTTPException(status_code=403, detail="Unauthorized: You are not an active member of this tenant.")
            membership_role = membership.role

    return TenantContext(tenant=tenant, user=admin, role=membership_role)
```

### 5.2 Microservice Cross-Boundary Context Passing
Downstream services (e.g., `requirement_analysis` on port 8001, `architecture_generator` on port 8002) receive tenant context via standardized internal HTTP headers forwarded by reverse proxy gateways:
- `X-Aether-Tenant-ID`: `<tenant_uuid>`
- `X-Aether-User-ID`: `<user_uuid>`
- `X-Aether-Tenant-Role`: `TENANT_ADMIN`

Each microservice binds its persistent records (e.g., `requirements.db` entries) to `tenant_id`, guaranteeing cross-service tenant isolation.

---

## 6. Authentication Architecture (JWT, Cookies, API Keys)

To ensure consistency across the 12 microservices:
1. **Explicit Precedence Order (Established in Phase 0):**
   - Channel 1: `Authorization: Bearer <JWT>` takes highest priority.
   - Channel 2: HttpOnly Session Cookie `aether_session` used for web browser UI interactions.
   - Channel 3: `X-Admin-Key` for automation/CI/CD pipelines (strictly disallowing hardcoded default keys in production).
2. **Session Security Standards:**
   - Cookie Flags: `HttpOnly=True`, `SameSite=Lax`, `Path=/`, `Max-Age=28800` (8 hours).
   - In production (`ENVIRONMENT=production`): `Secure=True` enforced.
3. **JWT Configuration:**
   - Algorithm: `HS256` with minimum 256-bit cryptographic secret (`JWT_SECRET_KEY`).
   - Token payload includes `jti` (unique token identifier) for replay detection and revocation blacklisting in Redis.

---

## 7. Cache Isolation & Authorization Enforcement

### 7.1 Namespace Partitioning in Redis
The baseline vulnerability where keys were globally shared across tenants (e.g., `project:detail:{id}`) is replaced with strict multi-tenant namespace partitioning:

| Cache Key Pattern | Data Stored | TTL | Invalidation Trigger |
| :--- | :--- | :--- | :--- |
| `t:{tenant_id}:projects:list` | Serialized ProjectListOut | 60s | Project Create/Update/Delete |
| `t:{tenant_id}:project:{project_id}` | Project + Environments Detail | 30s | Project/Environment Update/Delete |
| `t:{tenant_id}:cloud:connections` | Serialized CloudConnectionList | 60s | Connection Create/Update/Delete |
| `t:{tenant_id}:cloud:conn:{cloud_id}` | Cloud Connection Detail | 60s | Connection Update/Revalidate |
| `t:{tenant_id}:git:conn:{conn_id}` | Git Connection Detail | 60s | Git Connection Update/Validation |
| `t:{tenant_id}:user:{user_id}:role` | Cached Role for User in Tenant | 300s | Membership Role Change / Removal |

### 7.2 Inviolable Authorization-Before-Cache Rule
In every cached endpoint:
```python
# 1. ALWAYS perform database or context membership verification FIRST
ctx.require_role("OWNER", "ADMIN", "MEMBER", "VIEWER")

# 2. Only check cache within the verified tenant namespace
cached = await cache_manager.get(f"t:{ctx.tenant.id}:project:{project_id}")
if cached:
    return ProjectOut(**cached)

# 3. Query DB scoped to tenant_id
project = await db.scalar(select(AetherProject).where(
    AetherProject.id == project_id,
    AetherProject.tenant_id == ctx.tenant.id
))
if not project:
    raise HTTPException(status_code=404, detail="Project not found.")
```

---

## 8. Database Topology & Versioned Migration Strategy

### 8.1 Dual-Database Topology Realities
AetherOps runs with:
- **Primary Runtime:** PostgreSQL container (`aether_postgres`, database `aether_catalog`).
- **Failover / Hermetic Testing:** SQLite with WAL mode (`test_projects.db`, `test_source_connections.db`).

The migration strategy must support both PostgreSQL (with schemas `project_manager`, `source_connection`) and SQLite.

### 8.2 Alembic Migration Architecture
We introduce versioned migrations using **Alembic**:
```text
migrations/
├── alembic.ini
├── env.py              # Detects PostgreSQL vs SQLite dialects dynamically
├── script.py.mako
└── versions/
    ├── 0001_baseline_tables.py
    ├── 0002_add_tenant_and_membership_tables.py
    ├── 0003_add_tenant_id_to_projects_and_connections.py
    ├── 0004_backfill_personal_workspaces.py
    └── 0005_add_secret_vault_table.py
```

#### Multi-Engine `env.py` Handling
```python
def run_migrations_online():
    # If URL is postgresql+asyncpg, use sync wrapper or async engine for migrations
    # Support search_path: "project_manager, public"
    connectable = context.config.attributes.get("connection", None)
    if connectable is None:
        connectable = engine_from_config(
            context.config.get_section(context.config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    with connectable.connect() as connection:
        if connection.dialect.name == "postgresql":
            connection.execute(text('CREATE SCHEMA IF NOT EXISTS "project_manager"'))
            connection.execute(text('SET search_path TO "project_manager", public'))
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

### 8.3 Safe Data Migration & Recovery Prerequisite
- **Step 1:** Backup database prior to migration execution (`pg_dump` for PostgreSQL; `.backup` for SQLite).
- **Step 2:** Execute additive migrations (create `aether_tenants`, `aether_tenant_memberships`, add nullable `tenant_id`).
- **Step 3:** Run data backfill script inside a single atomic transaction.
- **Rollback Limitations:** Downward migrations drop tenant tables; existing projects retain legacy `owner` column so that rolling back does not destroy project data.

---

## 9. Backward Compatibility & API Preservation

### 9.1 Zero Breaking Changes to Public Contracts
All existing API response schemas retain existing fields:

```python
class ProjectOut(BaseModel):
    id:                str
    name:              str
    description:       str | None
    project_type:      str
    owner:             str                       # RETAINED: Legacy username string
    tenant_id:         str | None = None         # NEW: Populated tenant context
    status:            str
    environment_count: int
    environments:      list[EnvironmentOut] = []
    created_at:        str
    updated_at:        str
```

### 9.2 Preservation of Deterministic Algorithms
The following components remain completely untouched:
1. `services/requirement_analysis/app/engine.py` (deterministic sizing algorithms).
2. All 39 regional SQLite pricing catalogs (`data/catalogs/catalog_*.db`).
3. `services/architecture_generator/app/generator.py` (DAG coordinate generation and React Flow layouts).

---

## 10. AES-256-GCM Credential Security Envelope Architecture

### 10.1 Addressing the Baseline bcrypt Deficiency
Phase 0 confirmed that AWS `secret_access_key` is currently hashed with bcrypt, making it permanently unrecoverable for deployment operations. 

We replace this with an authenticated, reversible **AES-256-GCM Security Envelope**.

```text
┌────────────────────────────────────────────────────────┐
│              User Input Secret Material                │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│      Generate 96-bit Cryptographically Secure Nonce    │
│              secrets.token_bytes(12)                   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│      Construct Associated Authenticated Data (AAD)     │
│   "tenant:{tenant_id}|resource:{id}|type:{type}|v1"    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│             AES-256-GCM AEAD Encryption                │
│       (Plaintext, Key=256-bit DEK, Nonce=96-bit, AAD)  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                 Output Ciphertext + Tag                │
│           (Stored in sc_secret_vault table)            │
└────────────────────────────────────────────────────────┘
```

### 10.2 Cryptographic Envelope Specifications
- **Cipher:** AES-256-GCM (`cryptography.hazmat.primitives.ciphers.aead.AESGCM`).
- **Data Encryption Key (DEK):** 256 bits (32 bytes), unique per tenant or credential record.
- **Nonce:** 96 bits (12 bytes), cryptographically random via `secrets.token_bytes(12)`.
  > [!IMPORTANT]
  > **Zero Nonce Reuse:** Every encryption invocation generates a fresh random nonce. A nonce is never reused with the same DEK.
- **Authentication Tag:** 128 bits (16 bytes), verified by the hardware-accelerated GCM implementation before releasing plaintext.
- **Associated Authenticated Data (AAD):**
  `AAD = f"tenant:{tenant_id}|res_type:{resource_type}|res_id:{resource_id}|v1".encode("utf-8")`
  **Anti-Swapping Guarantee:** If an attacker attempts to copy ciphertext from Tenant A's row into Tenant B's row, decryption immediately fails with authentication failure because the tenant ID in AAD does not match.

### 10.3 Key Provider Abstraction (`KeyProvider`)

```python
class KeyProvider(ABC):
    @abstractmethod
    async def get_or_create_data_key(self, tenant_id: str) -> bytes:
        """Return 256-bit DEK."""
        pass

class DevelopmentKeyProvider(KeyProvider):
    """
    Secure development provider deriving DEK from environment secret.
    Requires AETHER_MASTER_ENCRYPTION_KEY (64-character hex or base64).
    Fails closed if key is missing or invalid.
    """
    def __init__(self):
        raw_key = os.getenv("AETHER_MASTER_ENCRYPTION_KEY")
        if not raw_key:
            raise RuntimeError("CRITICAL: AETHER_MASTER_ENCRYPTION_KEY environment variable is not configured.")
        self.master_key = hashlib.sha256(raw_key.encode()).digest()

    async def get_or_create_data_key(self, tenant_id: str) -> bytes:
        # HKDF / HMAC-based tenant DEK derivation
        import hmac
        return hmac.new(self.master_key, f"tenant_dek:{tenant_id}".encode(), hashlib.sha256).digest()

class AwsKmsKeyProvider(KeyProvider):
    """
    Production KMS Envelope provider.
    Calls KMS GenerateDataKey using Customer-Managed Key (CMK) ARN.
    """
    def __init__(self, kms_key_arn: str):
        self.kms_key_arn = kms_key_arn

    async def get_or_create_data_key(self, tenant_id: str) -> bytes:
        # Calls boto3 / aioboto3 kms.generate_data_key
        # Returns plaintext DEK, stores encrypted DEK in vault
        pass
```

### 10.4 Vault Storage Schema: `sc_secret_vault`

```python
class SecretVault(Base):
    __tablename__ = "sc_secret_vault"

    id            = Column(String(36),  primary_key=True, index=True) # UUID v4
    tenant_id     = Column(String(36),  nullable=False, index=True)
    resource_type = Column(String(50),  nullable=False) # AWS_CREDENTIALS | GITHUB_PAT | GITHUB_OAUTH
    resource_id   = Column(String(36),  nullable=False, index=True) # FK to CloudConnection or GitConnection
    ciphertext    = Column(LargeBinary, nullable=False)
    nonce         = Column(LargeBinary, nullable=False) # 12 bytes
    key_id        = Column(String(200), nullable=False) # Provider identifier / KMS ARN
    version       = Column(Integer,     nullable=False, default=1)
    created_at    = Column(DateTime,    nullable=False, default=datetime.datetime.utcnow)
    rotated_at    = Column(DateTime,    nullable=True)
```

---

## 11. GitHub Credential Vault & OAuth Security

### 11.1 Vaulting Personal Access Tokens (PATs) & OAuth Secrets
1. `GitConnection` records store only metadata (`repo_name`, `branch`, `pat_label`, `github_user`).
2. Plaintext PATs and OAuth Access Tokens are encrypted with AES-256-GCM and stored in `sc_secret_vault` linked to `connection_id`.
3. Plaintext tokens are **never** echoed in `GitConnectionOut` or API responses.

### 11.2 Hardening OAuth Flow Against CSRF & State Tampering
1. **OAuth State Generation:**
   ```python
   state = secrets.token_urlsafe(32)
   ```
2. **State Context Storage in Redis:**
   Key: `gh_state:{state}` (TTL: 600s / 10 minutes)
   Value: `json.dumps({"user_id": user_uuid, "tenant_id": tenant_id, "timestamp": time.time()})`
3. **Callback Validation:**
   In `GET /api/v1/auth/github/callback`:
   - Fetch `gh_state:{state}` from Redis and immediately delete it (single-use token).
   - If missing, expired, or user mismatch: reject with `HTTP 400 Bad Request: Invalid or expired OAuth state`.
4. **Open Redirect Prevention:**
   Callback redirect destinations are restricted strictly to relative paths (`/app/source`, `/source-connection`) or pre-approved domain allowlists.

---

## 12. Security Audit & Evidence Engine Integration

### 12.1 Cross-Cutting Nature
The **Documentation & Evidence Engine** is confirmed as a cross-cutting background service observing Modules 1–14, rather than a standalone isolated feature.

### 12.2 Security Audit Events
Every security-sensitive event emits a structured, immutable audit log:

```python
class SecurityAuditEvent(Base):
    __tablename__ = "aether_security_audit_events"

    id          = Column(String(36), primary_key=True, index=True) # UUID v4
    tenant_id   = Column(String(36), nullable=True, index=True)
    actor_id    = Column(String(36), nullable=False, index=True)   # User UUID
    actor_email = Column(String(120), nullable=True)
    action      = Column(String(64), nullable=False, index=True)   # e.g., CREDENTIAL_VAULT_ENCRYPT
    resource    = Column(String(120), nullable=True)
    status      = Column(String(20), nullable=False)               # SUCCESS | DENIED | ERROR
    ip_address  = Column(String(64), nullable=True)
    details     = Column(Text, nullable=True)                      # Sanitized JSON metadata
    created_at  = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
```

### 12.3 Strict Secret Sanitization Filter
Before writing to `details` or evidence stores:
```python
FORBIDDEN_AUDIT_KEYS = {
    "secret_access_key", "access_key_id", "session_token",
    "password", "token", "pat_token", "pat_token_hash",
    "jwt", "api_key", "X-Admin-Key", "Authorization", "private_key"
}

def sanitize_audit_metadata(data: dict) -> dict:
    sanitized = {}
    for k, v in data.items():
        if any(bad in k.lower() for bad in ("secret", "pass", "token", "key", "auth", "cred")):
            sanitized[k] = "[REDACTED]"
        elif isinstance(v, dict):
            sanitized[k] = sanitize_audit_metadata(v)
        else:
            sanitized[k] = v
    return sanitized
```

---

## 13. Threat Model, Edge Cases & Automated Test Plan

### 13.1 Threat Matrix & Countermeasures

| Threat Vector | Attack Scenario | Architectural Countermeasure |
| :--- | :--- | :--- |
| **T1: Horizontal Tenant Hopping** | Tenant A attempts `GET /api/v1/projects/{tenant_b_proj_id}` | `TenantContext` queries `where tenant_id == ctx.tenant.id`. Non-matching IDs return `HTTP 404` without leaking object existence. |
| **T2: Vertical Privilege Escalation** | `TENANT_VIEWER` attempts `POST /api/v1/projects` | `ctx.require_role("OWNER", "ADMIN", "MEMBER")` throws `HTTP 403 Forbidden`. |
| **T3: Ciphertext Swapping / Hijacking** | Attacker moves Tenant A's ciphertext into Tenant B's database record | AES-256-GCM verification fails closed because Tenant B's AAD does not match Tenant A's AAD. |
| **T4: Cache-Aside Tenant Bypass** | User requests cached detail of another tenant's project | All cache keys are tenant-prefixed (`t:{tenant_id}:...`) AND `get_current_tenant_context` executes before returning cached results. |
| **T5: OAuth State Forgery / CSRF** | Attacker intercepts callback or initiates forged OAuth flow | State tokens are cryptographically generated, single-use, bound to user ID in Redis, and expire in 10 minutes. |
| **T6: Plaintext Credential Leakage** | API response serializes secret keys or PATs to JSON | Output schemas (`CloudConnectionOut`, `GitConnectionOut`) strictly omit secret fields. Vault queries require purpose-built internal runner interfaces. |

### 13.2 Automated Test Plan for Phase 1 Verification

```text
tests/phase1/
├── test_tenant_identity.py        # Personal workspace auto-creation, tenant CRUD
├── test_rbac_matrix.py             # Verify all 5 roles against every permission boundary
├── test_migrations.py              # Alembic upgrade & downgrade on disposable DBs
├── test_credential_envelope.py    # AES-256-GCM encryption, decryption, AAD mismatch, nonce uniqueness
├── test_github_vault.py           # Vaulted token storage, OAuth state validation
└── test_audit_sanitization.py     # Verify zero secrets leaked in audit logs & evidence
```

---

## 14. Unresolved Decisions Requiring Human Approval

Before proceeding to Checkpoint 2 and Checkpoint 3 implementation, the following decisions are submitted for human review:

1. **Default Signup Behavior:**
   - *Option A (Recommended):* Every new registrant automatically receives an active Personal Workspace with role `OWNER`, allowing immediate single-user exploration while enabling future multi-tenant invitations.
   - *Option B:* New registrants receive no workspace by default and must be explicitly invited to an existing Organization Tenant.
2. **Existing AWS Secret Keys Handling:**
   - *Fact:* Existing AWS secret keys in the database were irreversibly hashed with bcrypt in prior iterations.
   - *Proposal:* Existing connections will be flagged with `status = "NEEDS_REAUTHENTICATION"`. A notice will prompt the user to re-save credentials so they can be vaulted into the new AES-256-GCM envelope.
3. **Key Management Provider Configuration:**
   - *Local/Dev Default:* `DevelopmentKeyProvider` using `AETHER_MASTER_ENCRYPTION_KEY` from `.env`.
   - *Production Option:* AWS KMS Customer-Managed Key ARN via `AETHER_KMS_KEY_ARN` when deploying to AWS.

---

## 15. Checkpoint 1 Conclusion

Checkpoint 1 design specification is complete. 

**Execution is STOPPED. Awaiting human review and explicit approval of `PHASE1_TENANT_RBAC_DESIGN.md` before implementing Checkpoint 2.**
