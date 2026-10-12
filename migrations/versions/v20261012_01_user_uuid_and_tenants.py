"""
Migration 20261012_01_user_uuid_and_tenants
Applies Phase 1 Multi-Tenant Identity, RBAC, and Personal Workspace Schema & Backfill.

Targets:
- Project Manager Schema / SQLite Database (`project_manager` schema in PG or `projects.db` in SQLite)
- Source Connection Schema / SQLite Database (`source_connection` schema in PG or `source_connections.db` in SQLite)

Actions:
1. Adds `uuid VARCHAR(36)` to `pm_admin_users` and `sc_admin_users` if missing.
2. Backfills stable immutable UUIDs for all historical users:
   - admin: 00000000-0000-0000-0000-000000000002
   - root_admin: 00000000-0000-0000-0000-000000000001
   - others: uuid5(NAMESPACE_DNS, f"{username}.aetherops.local")
3. Creates `pm_tenants` table with unique constraint on `slug`.
4. Creates `pm_tenant_memberships` table with unique constraint on `(tenant_id, user_id)`.
5. Adds `tenant_id` and `created_by_user_id` to `aether_projects` and `aether_environments`.
6. Backfills personal workspaces (`pm_tenants`) and `OWNER` memberships (`pm_tenant_memberships`) for all users.
7. Reconciles existing `aether_projects` to their owners' personal workspaces and creator UUIDs.
8. Reconciles `aether_environments` to their project's tenant.
9. Synchronizes `sc_admin_users` to match `pm_admin_users` identity mapping.
10. Adds `tenant_id` and `created_by_user_id` to `sc_git_connections` and `sc_cloud_connections`.
11. Reconciles `sc_git_connections` and `sc_cloud_connections` to verified project tenants and user UUIDs.
12. Marks bcrypt-only AWS credentials in `sc_cloud_connections` as `NEEDS_REAUTHENTICATION`.
13. Quarantines ambiguous or orphaned records without assigning arbitrary tenants.
"""
import uuid
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("migration-01")

REVISION = "20261012_01"
NAME = "user_uuid_and_tenants"
DESCRIPTION = "Phase 1: User UUID backfill, Tenants, RBAC memberships, Connection reconciliation, and Quarantine"

ADMIN_UUID = "00000000-0000-0000-0000-000000000002"
ROOT_ADMIN_UUID = "00000000-0000-0000-0000-000000000001"


def derive_user_uuid(username: str) -> str:
    """Deterministic, immutable UUID generation for users."""
    u_lower = username.lower().strip()
    if u_lower == "root_admin":
        return ROOT_ADMIN_UUID
    if u_lower == "admin":
        return ADMIN_UUID
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{u_lower}.aetherops.local"))


def slugify(text_val: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", text_val).strip().lower()
    return re.sub(r"[-\s]+", "-", cleaned) or "workspace"


async def upgrade(session: AsyncSession, dialect: str, target: str = "project_manager"):
    """
    Execute upgrade migration.
    target: 'project_manager' or 'source_connection'
    """
    logger.info(f"Running upgrade {REVISION} ({NAME}) on {dialect} target '{target}'")

    if target == "project_manager":
        await _upgrade_project_manager(session, dialect)
    elif target == "source_connection":
        await _upgrade_source_connection(session, dialect)
    else:
        raise ValueError(f"Unknown target: {target}")


async def _upgrade_project_manager(session: AsyncSession, dialect: str):
    schema_prefix = '"project_manager".' if dialect == "postgresql" else ""
    
    # 1. Add uuid column to pm_admin_users if not present
    if dialect == "postgresql":
        await session.execute(text(f"""
        ALTER TABLE {schema_prefix}"pm_admin_users" 
        ADD COLUMN IF NOT EXISTS "uuid" VARCHAR(36);
        """))
    else:
        # SQLite
        try:
            await session.execute(text('ALTER TABLE "pm_admin_users" ADD COLUMN "uuid" VARCHAR(36);'))
        except Exception:
            pass  # column already exists

    # 2. Backfill UUIDs for all users in pm_admin_users
    res = await session.execute(text(f'SELECT id, username, uuid FROM {schema_prefix}"pm_admin_users";'))
    users = res.fetchall()
    user_map = {}  # username -> uuid
    for row in users:
        u_id, uname, existing_uuid = row[0], row[1], row[2]
        canonical_uuid = existing_uuid if (existing_uuid and existing_uuid != "None") else derive_user_uuid(uname)
        user_map[uname] = canonical_uuid
        await session.execute(text(f"""
        UPDATE {schema_prefix}"pm_admin_users"
        SET "uuid" = :canonical_uuid
        WHERE id = :u_id;
        """), {"canonical_uuid": canonical_uuid, "u_id": u_id})

    # Add unique index on uuid for pm_admin_users
    await session.execute(text(f"""
    CREATE UNIQUE INDEX IF NOT EXISTS "idx_pm_admin_users_uuid" 
    ON {schema_prefix}"pm_admin_users" ("uuid");
    """))

    # 3. Create pm_tenants table
    if dialect == "postgresql":
        await session.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {schema_prefix}"pm_tenants" (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(120) NOT NULL,
            slug VARCHAR(140) NOT NULL,
            tenant_type VARCHAR(30) NOT NULL DEFAULT 'ORGANIZATION',
            status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            CONSTRAINT "uq_pm_tenants_slug" UNIQUE ("slug")
        );
        """))
    else:
        await session.execute(text("""
        CREATE TABLE IF NOT EXISTS "pm_tenants" (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(120) NOT NULL,
            slug VARCHAR(140) NOT NULL UNIQUE,
            tenant_type VARCHAR(30) NOT NULL DEFAULT 'ORGANIZATION',
            status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        );
        """))

    # 4. Create pm_tenant_memberships table
    if dialect == "postgresql":
        await session.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {schema_prefix}"pm_tenant_memberships" (
            id VARCHAR(36) PRIMARY KEY,
            tenant_id VARCHAR(36) NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            role VARCHAR(30) NOT NULL DEFAULT 'MEMBER',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            CONSTRAINT "uq_pm_tenant_membership" UNIQUE ("tenant_id", "user_id")
        );
        """))
    else:
        await session.execute(text("""
        CREATE TABLE IF NOT EXISTS "pm_tenant_memberships" (
            id VARCHAR(36) PRIMARY KEY,
            tenant_id VARCHAR(36) NOT NULL,
            user_id VARCHAR(36) NOT NULL,
            role VARCHAR(30) NOT NULL DEFAULT 'MEMBER',
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            UNIQUE ("tenant_id", "user_id")
        );
        """))

    # 5. Add tenant_id & created_by_user_id to aether_projects
    if dialect == "postgresql":
        await session.execute(text(f"""
        ALTER TABLE {schema_prefix}"aether_projects" 
        ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR(36),
        ADD COLUMN IF NOT EXISTS "created_by_user_id" VARCHAR(36);
        """))
    else:
        try:
            await session.execute(text('ALTER TABLE "aether_projects" ADD COLUMN "tenant_id" VARCHAR(36);'))
        except Exception:
            pass
        try:
            await session.execute(text('ALTER TABLE "aether_projects" ADD COLUMN "created_by_user_id" VARCHAR(36);'))
        except Exception:
            pass

    # 6. Add tenant_id to aether_environments
    if dialect == "postgresql":
        await session.execute(text(f"""
        ALTER TABLE {schema_prefix}"aether_environments" 
        ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR(36);
        """))
    else:
        try:
            await session.execute(text('ALTER TABLE "aether_environments" ADD COLUMN "tenant_id" VARCHAR(36);'))
        except Exception:
            pass

    # 7. Provision personal workspaces and memberships for all users
    user_tenant_map = {}  # user_uuid -> tenant_id
    now = datetime.utcnow()
    for uname, u_uuid in user_map.items():
        # Check if personal workspace already exists
        clean_name = uname.strip() or "User"
        slug = f"personal-{slugify(clean_name)}-{u_uuid[:8].lower()}"
        
        t_res = await session.execute(text(f"""
        SELECT id FROM {schema_prefix}"pm_tenants" WHERE slug = :slug;
        """), {"slug": slug})
        existing_t = t_res.scalar_one_or_none()
        
        if existing_t:
            t_id = existing_t
        else:
            t_id = str(uuid.uuid4())
            t_name = f"{clean_name}'s Workspace"
            await session.execute(text(f"""
            INSERT INTO {schema_prefix}"pm_tenants" (id, name, slug, tenant_type, status, created_at, updated_at)
            VALUES (:id, :name, :slug, 'PERSONAL', 'ACTIVE', :created_at, :updated_at);
            """), {"id": t_id, "name": t_name, "slug": slug, "created_at": now, "updated_at": now})

        user_tenant_map[u_uuid] = t_id

        # Ensure OWNER membership exists
        m_res = await session.execute(text(f"""
        SELECT id FROM {schema_prefix}"pm_tenant_memberships" 
        WHERE tenant_id = :tenant_id AND user_id = :user_id;
        """), {"tenant_id": t_id, "user_id": u_uuid})
        if not m_res.scalar_one_or_none():
            m_id = str(uuid.uuid4())
            await session.execute(text(f"""
            INSERT INTO {schema_prefix}"pm_tenant_memberships" (id, tenant_id, user_id, role, is_active, created_at, updated_at)
            VALUES (:id, :tenant_id, :user_id, 'OWNER', TRUE, :created_at, :updated_at);
            """), {"id": m_id, "tenant_id": t_id, "user_id": u_uuid, "created_at": now, "updated_at": now})

    # 8. Reconcile aether_projects: map to owner's personal workspace
    p_res = await session.execute(text(f'SELECT id, owner FROM {schema_prefix}"aether_projects";'))
    projects = p_res.fetchall()
    for p_id, p_owner in projects:
        u_uuid = user_map.get(p_owner)
        if u_uuid and u_uuid in user_tenant_map:
            t_id = user_tenant_map[u_uuid]
            await session.execute(text(f"""
            UPDATE {schema_prefix}"aether_projects"
            SET "tenant_id" = :t_id, "created_by_user_id" = :u_uuid
            WHERE id = :p_id;
            """), {"t_id": t_id, "u_uuid": u_uuid, "p_id": p_id})
        else:
            logger.warning(f"Project '{p_id}' has unmapped owner '{p_owner}' -> QUARANTINED (no tenant assigned)")

    # 9. Reconcile aether_environments: map to project's tenant_id
    await session.execute(text(f"""
    UPDATE {schema_prefix}"aether_environments" e
    SET "tenant_id" = p."tenant_id"
    FROM {schema_prefix}"aether_projects" p
    WHERE e."project_id" = p."id" AND p."tenant_id" IS NOT NULL;
    """ if dialect == "postgresql" else f"""
    UPDATE "aether_environments"
    SET "tenant_id" = (SELECT p."tenant_id" FROM "aether_projects" p WHERE p."id" = "aether_environments"."project_id")
    WHERE "project_id" IN (SELECT id FROM "aether_projects" WHERE "tenant_id" IS NOT NULL);
    """))

    # 10. Add indexes
    for idx_sql in [
        f'CREATE INDEX IF NOT EXISTS "idx_pm_projects_tenant" ON {schema_prefix}"aether_projects" ("tenant_id");',
        f'CREATE INDEX IF NOT EXISTS "idx_pm_projects_creator" ON {schema_prefix}"aether_projects" ("created_by_user_id");',
        f'CREATE INDEX IF NOT EXISTS "idx_pm_env_tenant" ON {schema_prefix}"aether_environments" ("tenant_id");',
        f'CREATE INDEX IF NOT EXISTS "idx_pm_memberships_tenant" ON {schema_prefix}"pm_tenant_memberships" ("tenant_id");',
        f'CREATE INDEX IF NOT EXISTS "idx_pm_memberships_user" ON {schema_prefix}"pm_tenant_memberships" ("user_id");',
    ]:
        await session.execute(text(idx_sql))

    await session.commit()
    logger.info("Project Manager migration complete.")


async def _upgrade_source_connection(session: AsyncSession, dialect: str):
    schema_prefix = '"source_connection".' if dialect == "postgresql" else ""
    pm_schema_prefix = '"project_manager".' if dialect == "postgresql" else ""

    # 1. Add uuid column to sc_admin_users if missing
    if dialect == "postgresql":
        await session.execute(text(f"""
        ALTER TABLE {schema_prefix}"sc_admin_users" 
        ADD COLUMN IF NOT EXISTS "uuid" VARCHAR(36);
        """))
    else:
        try:
            await session.execute(text('ALTER TABLE "sc_admin_users" ADD COLUMN "uuid" VARCHAR(36);'))
        except Exception:
            pass

    # 2. Synchronize sc_admin_users with canonical UUIDs
    res = await session.execute(text(f'SELECT id, username, uuid FROM {schema_prefix}"sc_admin_users";'))
    for row in res.fetchall():
        u_id, uname, existing_uuid = row[0], row[1], row[2]
        canonical_uuid = existing_uuid if (existing_uuid and existing_uuid != "None") else derive_user_uuid(uname)
        await session.execute(text(f"""
        UPDATE {schema_prefix}"sc_admin_users"
        SET "uuid" = :canonical_uuid
        WHERE id = :u_id;
        """), {"canonical_uuid": canonical_uuid, "u_id": u_id})

    # 3. Add tenant_id & created_by_user_id to sc_git_connections
    if dialect == "postgresql":
        await session.execute(text(f"""
        ALTER TABLE {schema_prefix}"sc_git_connections" 
        ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR(36),
        ADD COLUMN IF NOT EXISTS "created_by_user_id" VARCHAR(36);
        """))
    else:
        try:
            await session.execute(text('ALTER TABLE "sc_git_connections" ADD COLUMN "tenant_id" VARCHAR(36);'))
        except Exception:
            pass
        try:
            await session.execute(text('ALTER TABLE "sc_git_connections" ADD COLUMN "created_by_user_id" VARCHAR(36);'))
        except Exception:
            pass

    # 4. Add tenant_id & created_by_user_id to sc_cloud_connections
    if dialect == "postgresql":
        await session.execute(text(f"""
        ALTER TABLE {schema_prefix}"sc_cloud_connections" 
        ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR(36),
        ADD COLUMN IF NOT EXISTS "created_by_user_id" VARCHAR(36);
        """))
    else:
        try:
            await session.execute(text('ALTER TABLE "sc_cloud_connections" ADD COLUMN "tenant_id" VARCHAR(36);'))
        except Exception:
            pass
        try:
            await session.execute(text('ALTER TABLE "sc_cloud_connections" ADD COLUMN "created_by_user_id" VARCHAR(36);'))
        except Exception:
            pass

    # 5. Reconcile sc_git_connections to project's tenant_id and owner's UUID
    if dialect == "postgresql":
        # Project table in project_manager schema
        await session.execute(text(f"""
        UPDATE {schema_prefix}"sc_git_connections" g
        SET "tenant_id" = p."tenant_id",
            "created_by_user_id" = p."created_by_user_id"
        FROM {pm_schema_prefix}"aether_projects" p
        WHERE g."project_id" = p."id" AND p."tenant_id" IS NOT NULL;
        """))
    else:
        # SQLite (if sharing DB or attached)
        try:
            await session.execute(text("""
            UPDATE "sc_git_connections"
            SET "tenant_id" = (SELECT p."tenant_id" FROM "aether_projects" p WHERE p."id" = "sc_git_connections"."project_id"),
                "created_by_user_id" = (SELECT p."created_by_user_id" FROM "aether_projects" p WHERE p."id" = "sc_git_connections"."project_id")
            WHERE "project_id" IN (SELECT id FROM "aether_projects" WHERE "tenant_id" IS NOT NULL);
            """))
        except Exception:
            pass

    # 6. Reconcile sc_cloud_connections to project's tenant_id and owner's UUID
    if dialect == "postgresql":
        await session.execute(text(f"""
        UPDATE {schema_prefix}"sc_cloud_connections" c
        SET "tenant_id" = p."tenant_id",
            "created_by_user_id" = p."created_by_user_id"
        FROM {pm_schema_prefix}"aether_projects" p
        WHERE c."project_id" = p."id" AND p."tenant_id" IS NOT NULL;
        """))
    else:
        try:
            await session.execute(text("""
            UPDATE "sc_cloud_connections"
            SET "tenant_id" = (SELECT p."tenant_id" FROM "aether_projects" p WHERE p."id" = "sc_cloud_connections"."project_id"),
                "created_by_user_id" = (SELECT p."created_by_user_id" FROM "aether_projects" p WHERE p."id" = "sc_cloud_connections"."project_id")
            WHERE "project_id" IN (SELECT id FROM "aether_projects" WHERE "tenant_id" IS NOT NULL);
            """))
        except Exception:
            pass

    # 7. Transition legacy bcrypt-hashed AWS credentials to NEEDS_REAUTHENTICATION
    # Condition: secret_key_hash starts with '$2b$' or is bcrypt formatted
    await session.execute(text(f"""
    UPDATE {schema_prefix}"sc_cloud_connections"
    SET "status" = 'NEEDS_REAUTHENTICATION'
    WHERE "secret_key_hash" IS NOT NULL 
      AND ("secret_key_hash" LIKE '$2b$%' OR "secret_key_hash" LIKE '$2a$%')
      AND "status" = 'CONNECTED';
    """))

    # 8. Add indexes
    for idx_sql in [
        f'CREATE INDEX IF NOT EXISTS "idx_sc_git_tenant" ON {schema_prefix}"sc_git_connections" ("tenant_id");',
        f'CREATE INDEX IF NOT EXISTS "idx_sc_git_creator" ON {schema_prefix}"sc_git_connections" ("created_by_user_id");',
        f'CREATE INDEX IF NOT EXISTS "idx_sc_cloud_tenant" ON {schema_prefix}"sc_cloud_connections" ("tenant_id");',
        f'CREATE INDEX IF NOT EXISTS "idx_sc_cloud_creator" ON {schema_prefix}"sc_cloud_connections" ("created_by_user_id");',
    ]:
        await session.execute(text(idx_sql))

    await session.commit()
    logger.info("Source Connection migration complete.")


async def downgrade(session: AsyncSession, dialect: str, target: str = "project_manager"):
    """
    Rollback migration.
    Reverts added columns / tables if supported safely.
    """
    logger.info(f"Running downgrade {REVISION} on {dialect} target '{target}'")
    schema_prefix = f'"{target}".' if dialect == "postgresql" else ""

    if target == "project_manager":
        if dialect == "postgresql":
            await session.execute(text(f'DROP TABLE IF EXISTS {schema_prefix}"pm_tenant_memberships" CASCADE;'))
            await session.execute(text(f'DROP TABLE IF EXISTS {schema_prefix}"pm_tenants" CASCADE;'))
            await session.execute(text(f'ALTER TABLE {schema_prefix}"aether_projects" DROP COLUMN IF EXISTS "tenant_id", DROP COLUMN IF EXISTS "created_by_user_id";'))
            await session.execute(text(f'ALTER TABLE {schema_prefix}"aether_environments" DROP COLUMN IF EXISTS "tenant_id";'))
            await session.execute(text(f'ALTER TABLE {schema_prefix}"pm_admin_users" DROP COLUMN IF EXISTS "uuid";'))
        else:
            await session.execute(text('DROP TABLE IF EXISTS "pm_tenant_memberships";'))
            await session.execute(text('DROP TABLE IF EXISTS "pm_tenants";'))
            # SQLite does not drop columns in older engines, but table drops revert schema
    elif target == "source_connection":
        if dialect == "postgresql":
            await session.execute(text(f'ALTER TABLE {schema_prefix}"sc_git_connections" DROP COLUMN IF EXISTS "tenant_id", DROP COLUMN IF EXISTS "created_by_user_id";'))
            await session.execute(text(f'ALTER TABLE {schema_prefix}"sc_cloud_connections" DROP COLUMN IF EXISTS "tenant_id", DROP COLUMN IF EXISTS "created_by_user_id";'))
            await session.execute(text(f'ALTER TABLE {schema_prefix}"sc_admin_users" DROP COLUMN IF EXISTS "uuid";'))

    await session.commit()
    logger.info(f"Downgrade {REVISION} complete on {target}.")
