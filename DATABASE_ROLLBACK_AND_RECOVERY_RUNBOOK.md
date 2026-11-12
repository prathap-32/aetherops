# Database Rollback and Recovery Runbook

**Date:** November 11, 2026  

---

## 1. Backup Location & Retention
- **PostgreSQL Backups:** Stored securely at `backups/pre_migration/postgres/` (e.g., `aether_postgres_backup.sql`).
- **SQLite Backups:** Stored at `backups/pre_migration/sqlite/`.

## 2. Recovery Procedure
1. Stop affected microservices.
2. Restore PostgreSQL database using `psql`:
   ```bash
   sudo docker exec -i aether_postgres psql -U postgres -d aether_catalog < backups/pre_migration/postgres/aether_postgres_backup.sql
   ```
3. Restart microservices and verify health endpoints.
