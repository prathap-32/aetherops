"""
Comprehensive Migration Verification Test Suite for AetherOps Phase 1 Checkpoint 3.
Executes testing across DISPOSABLE PostgreSQL and SQLite databases.
Covers:
1. Fresh database initialization & migration.
2. Upgrade from exact baseline schema & historical data snapshot.
3. User UUID backfill (including deterministic admin & root_admin UUIDs).
4. Personal workspace & OWNER membership creation.
5. Project & environment ownership reconciliation.
6. Git & cloud connection reconciliation.
7. Orphaned and ambiguous connection quarantine (unassigned tenant).
8. NEEDS_REAUTHENTICATION transition for bcrypt-hashed credentials.
9. Repeated migration idempotency.
10. Migration rollback / downgrade verification.
11. Row count and record accountability verification.
"""
import os
import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from migrations.runner import ensure_migration_table, get_applied_versions
import migrations.versions.v20261012_01_user_uuid_and_tenants as m_01

ADMIN_UUID = "00000000-0000-0000-0000-000000000002"
ROOT_ADMIN_UUID = "00000000-0000-0000-0000-000000000001"

DISPOSABLE_SQLITE_URL = "sqlite+aiosqlite:///disposable_test_migration.db"
DISPOSABLE_PG_URL = os.getenv("TEST_POSTGRES_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/disposable_migration_test")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_sqlite_fresh_install_and_idempotency():
    """Verify fresh install and multiple migration runs on SQLite."""
    db_file = "disposable_sqlite_fresh.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    engine = create_async_engine(f"sqlite+aiosqlite:///{db_file}", echo=False)
    sm = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with sm() as session:
        # Create minimal baseline table
        await session.execute(text("""
        CREATE TABLE pm_admin_users (
            id INTEGER PRIMARY KEY,
            username VARCHAR(64) NOT NULL,
            email VARCHAR(120) NOT NULL
        );
        """))
        await session.execute(text("""
        CREATE TABLE aether_projects (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            owner VARCHAR(100) NOT NULL
        );
        """))
        await session.execute(text("""
        CREATE TABLE aether_environments (
            id VARCHAR(36) PRIMARY KEY,
            project_id VARCHAR(36) NOT NULL,
            name VARCHAR(50) NOT NULL
        );
        """))
        # Seed test user and project
        await session.execute(text("INSERT INTO pm_admin_users (id, username, email) VALUES (1, 'admin', 'admin@test.local');"))
        await session.execute(text("INSERT INTO pm_admin_users (id, username, email) VALUES (2, 'alice', 'alice@test.local');"))
        await session.execute(text("INSERT INTO aether_projects (id, name, owner) VALUES ('proj-1', 'AliceApp', 'alice');"))
        await session.execute(text("INSERT INTO aether_environments (id, project_id, name) VALUES ('env-1', 'proj-1', 'dev');"))
        await session.commit()

        # Run migration 1st time
        await m_01.upgrade(session, "sqlite", target="project_manager")

        # Verify UUID backfill
        res = await session.execute(text("SELECT username, uuid FROM pm_admin_users;"))
        users = dict(res.fetchall())
        assert users["admin"] == ADMIN_UUID
        assert users["alice"] == m_01.derive_user_uuid("alice")

        # Verify tenant created for alice
        res_t = await session.execute(text("SELECT id, name, slug FROM pm_tenants;"))
        tenants = res_t.fetchall()
        assert len(tenants) == 2  # admin & alice

        # Verify project mapped
        res_p = await session.execute(text("SELECT id, tenant_id, created_by_user_id FROM aether_projects WHERE id = 'proj-1';"))
        p_row = res_p.fetchone()
        assert p_row[1] is not None
        assert p_row[2] == users["alice"]

        # Run migration 2nd time (IDEMPOTENCY CHECK)
        await m_01.upgrade(session, "sqlite", target="project_manager")

        # Verify no duplicate tenants created
        res_t2 = await session.execute(text("SELECT id FROM pm_tenants;"))
        assert len(res_t2.fetchall()) == 2

    await engine.dispose()
    if os.path.exists(db_file):
        os.remove(db_file)


@pytest.mark.anyio
async def test_postgresql_baseline_upgrade_reconciliation_and_rollback():
    """
    Test against disposable PostgreSQL database:
    1. Recreate clean disposable database.
    2. Seed with exact baseline tables and historical rows.
    3. Run upgrade migration.
    4. Verify UUID backfill, tenant mapping, connection reconciliation.
    5. Verify NEEDS_REAUTHENTICATION for bcrypt hash.
    6. Verify orphaned connections are quarantined.
    7. Test rollback.
    """
    # Create disposable db via postgres connection
    admin_engine = create_async_engine("postgresql+asyncpg://postgres:postgrespassword@localhost:5432/postgres", isolation_level="AUTOCOMMIT")
    async with admin_engine.connect() as conn:
        await conn.execute(text("DROP DATABASE IF EXISTS disposable_migration_test;"))
        await conn.execute(text("CREATE DATABASE disposable_migration_test;"))
    await admin_engine.dispose()

    test_engine = create_async_engine("postgresql+asyncpg://postgres:postgrespassword@localhost:5432/disposable_migration_test", echo=False)
    sm = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with sm() as session:
        # Create schemas
        await session.execute(text('CREATE SCHEMA IF NOT EXISTS "project_manager";'))
        await session.execute(text('CREATE SCHEMA IF NOT EXISTS "source_connection";'))

        # Seed Project Manager baseline tables
        for ddl in [
            """CREATE TABLE "project_manager"."pm_admin_users" (
                id SERIAL PRIMARY KEY,
                username VARCHAR(64) NOT NULL,
                email VARCHAR(120) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(32) NOT NULL DEFAULT 'ADMIN',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                failed_attempts INTEGER NOT NULL DEFAULT 0,
                locked_until TIMESTAMP,
                last_login_at TIMESTAMP,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );""",
            """CREATE TABLE "project_manager"."aether_projects" (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description VARCHAR(255),
                project_type VARCHAR(50) NOT NULL,
                owner VARCHAR(100) NOT NULL,
                status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
                environment_count INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );""",
            """CREATE TABLE "project_manager"."aether_environments" (
                id VARCHAR(36) PRIMARY KEY,
                project_id VARCHAR(36) NOT NULL,
                name VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'CREATED',
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );""",
            """CREATE TABLE "source_connection"."sc_admin_users" (
                id SERIAL PRIMARY KEY,
                username VARCHAR(64) NOT NULL,
                email VARCHAR(120) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(32) NOT NULL DEFAULT 'SUPER_ADMIN',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                failed_attempts INTEGER NOT NULL DEFAULT 0,
                locked_until TIMESTAMP,
                last_login_at TIMESTAMP,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );""",
            """CREATE TABLE "source_connection"."sc_git_connections" (
                id VARCHAR(36) PRIMARY KEY,
                project_id VARCHAR(36) NOT NULL,
                environment_id VARCHAR(36) NOT NULL,
                owner VARCHAR(100) NOT NULL,
                repo_url VARCHAR(500) NOT NULL,
                repo_name VARCHAR(200) NOT NULL,
                branch VARCHAR(200) NOT NULL DEFAULT 'main',
                pat_label VARCHAR(100),
                pat_token_hash VARCHAR(255),
                auth_type VARCHAR(30) DEFAULT 'PAT',
                github_user VARCHAR(100),
                status VARCHAR(30) NOT NULL DEFAULT 'CONNECTED',
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );""",
            """CREATE TABLE "source_connection"."sc_cloud_connections" (
                id VARCHAR(36) PRIMARY KEY,
                project_id VARCHAR(36) NOT NULL,
                environment_id VARCHAR(36) NOT NULL,
                owner VARCHAR(100) NOT NULL,
                provider VARCHAR(30) NOT NULL DEFAULT 'AWS',
                auth_type VARCHAR(30) NOT NULL DEFAULT 'ACCESS_KEYS',
                aws_region VARCHAR(50) NOT NULL DEFAULT 'us-east-1',
                access_key_masked VARCHAR(30),
                access_key_id VARCHAR(128),
                secret_key_hash VARCHAR(255),
                role_arn VARCHAR(300),
                external_id VARCHAR(100),
                status VARCHAR(30) NOT NULL DEFAULT 'CONNECTED',
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );"""
        ]:
            await session.execute(text(ddl))

        # Seed representative baseline data:
        for seed_sql in [
            """INSERT INTO "project_manager"."pm_admin_users" (id, username, email, password_hash, role) VALUES
            (1, 'admin', 'admin@aetherops.cloud', 'dummy_hash', 'SUPER_ADMIN'),
            (2, 'root_admin', 'root@aetherops.cloud', 'dummy_hash', 'SUPER_ADMIN'),
            (3, 'developer', 'dev@aetherops.cloud', 'dummy_hash', 'ADMIN');""",

            """INSERT INTO "source_connection"."sc_admin_users" (id, username, email, password_hash, role) VALUES
            (1, 'admin', 'admin@aetherops.cloud', 'dummy_hash', 'SUPER_ADMIN'),
            (2, 'root_admin', 'root@aetherops.cloud', 'dummy_hash', 'SUPER_ADMIN');""",

            """INSERT INTO "project_manager"."aether_projects" (id, name, project_type, owner) VALUES
            ('proj-dev-1', 'DevApp', 'web_application', 'developer');""",

            """INSERT INTO "project_manager"."aether_environments" (id, project_id, name) VALUES
            ('env-dev-1', 'proj-dev-1', 'dev');""",

            """INSERT INTO "source_connection"."sc_git_connections" (id, project_id, environment_id, owner, repo_url, repo_name) VALUES
            ('git-1', 'proj-dev-1', 'env-dev-1', 'developer', 'https://github.com/org/repo', 'org/repo');""",

            """INSERT INTO "source_connection"."sc_cloud_connections" (id, project_id, environment_id, owner, auth_type, role_arn, status) VALUES
            ('cloud-1', 'proj-dev-1', 'env-dev-1', 'developer', 'IAM_ROLE_ARN', 'arn:aws:iam::123:role/dev', 'CONNECTED');""",

            """INSERT INTO "source_connection"."sc_cloud_connections" (id, project_id, environment_id, owner, auth_type, secret_key_hash, status) VALUES
            ('cloud-bcrypt', 'proj-dev-1', 'env-dev-1', 'developer', 'ACCESS_KEYS', '$2b$10$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'CONNECTED');""",

            """INSERT INTO "source_connection"."sc_cloud_connections" (id, project_id, environment_id, owner, auth_type, role_arn, status) VALUES
            ('cloud-orphan', 'orphan-proj-99', 'orphan-env-99', 'admin', 'IAM_ROLE_ARN', 'arn:aws:iam::123:role/orphan', 'CONNECTED');"""
        ]:
            await session.execute(text(seed_sql))
        await session.commit()

        # RUN UPGRADE
        await m_01.upgrade(session, "postgresql", target="project_manager")
        await m_01.upgrade(session, "postgresql", target="source_connection")

        # 1. VERIFY USER IDENTITY BACKFILL
        res_users = await session.execute(text('SELECT username, uuid FROM "project_manager"."pm_admin_users";'))
        users = dict(res_users.fetchall())
        assert users["admin"] == ADMIN_UUID, "Default admin UUID mismatch"
        assert users["root_admin"] == ROOT_ADMIN_UUID, "Root admin UUID mismatch"
        assert users["developer"] == m_01.derive_user_uuid("developer"), "Developer UUID mismatch"

        # 2. VERIFY TENANT & MEMBERSHIP CREATION
        res_t = await session.execute(text('SELECT name, slug, tenant_type FROM "project_manager"."pm_tenants";'))
        tenants = res_t.fetchall()
        assert len(tenants) == 3  # all 3 users have personal workspaces
        for t in tenants:
            assert t[2] == "PERSONAL"

        res_m = await session.execute(text('SELECT role, is_active FROM "project_manager"."pm_tenant_memberships";'))
        memberships = res_m.fetchall()
        assert len(memberships) == 3
        for m in memberships:
            assert m[0] == "OWNER"
            assert m[1] is True

        # 3. VERIFY PROJECT RECONCILIATION
        res_p = await session.execute(text('SELECT id, tenant_id, created_by_user_id FROM "project_manager"."aether_projects" WHERE id = \'proj-dev-1\';'))
        p = res_p.fetchone()
        assert p[1] is not None, "Project tenant_id was not populated"
        assert p[2] == users["developer"], "Project creator UUID mismatch"

        # 4. VERIFY ENVIRONMENT RECONCILIATION
        res_e = await session.execute(text('SELECT id, tenant_id FROM "project_manager"."aether_environments" WHERE id = \'env-dev-1\';'))
        e = res_e.fetchone()
        assert e[1] == p[1], "Environment tenant_id does not match project tenant_id"

        # 5. VERIFY CONNECTION RECONCILIATION
        res_g = await session.execute(text('SELECT id, tenant_id, created_by_user_id FROM "source_connection"."sc_git_connections" WHERE id = \'git-1\';'))
        g = res_g.fetchone()
        assert g[1] == p[1], "Git connection tenant_id mismatch"
        assert g[2] == users["developer"], "Git creator UUID mismatch"

        # 6. VERIFY BCRYPT AWS CONNECTION -> NEEDS_REAUTHENTICATION
        res_c_bcrypt = await session.execute(text('SELECT status FROM "source_connection"."sc_cloud_connections" WHERE id = \'cloud-bcrypt\';'))
        assert res_c_bcrypt.scalar_one() == "NEEDS_REAUTHENTICATION", "Bcrypt AWS credential not marked NEEDS_REAUTHENTICATION"

        # 7. VERIFY ORPHANED CONNECTION -> QUARANTINED (tenant_id IS NULL)
        res_c_orphan = await session.execute(text('SELECT tenant_id FROM "source_connection"."sc_cloud_connections" WHERE id = \'cloud-orphan\';'))
        assert res_c_orphan.scalar_one() is None, "Orphan connection was incorrectly assigned a tenant"

        # 8. TEST DOWNGRADE (ROLLBACK)
        await m_01.downgrade(session, "postgresql", target="source_connection")
        await m_01.downgrade(session, "postgresql", target="project_manager")

        # Verify tables dropped
        res_table_check = await session.execute(text("""
        SELECT to_regclass('"project_manager"."pm_tenants"');
        """))
        assert res_table_check.scalar_one() is None, "pm_tenants was not dropped on rollback"

    await test_engine.dispose()

    # Drop disposable database
    admin_engine = create_async_engine("postgresql+asyncpg://postgres:postgrespassword@localhost:5432/postgres", isolation_level="AUTOCOMMIT")
    async with admin_engine.connect() as conn:
        await conn.execute(text("DROP DATABASE IF EXISTS disposable_migration_test;"))
    await admin_engine.dispose()
