# SQLite to PostgreSQL Migration Plan

**Date:** November 11, 2026  

---

## 1. Migration Strategy
1. **Preservation:** Retain all source SQLite database files as read-only migration sources and archival backups (`backups/pre_migration/`).
2. **Schema Mapping:** Map SQLite tables (`users`, `tenants`, `aether_projects`, `aether_environments`, etc.) to canonical PostgreSQL schemas (`identity`, `workspace`, etc.).
3. **Data Transformation:** Handle SQLite integer/boolean differences, timestamp normalization, and UUID consistency.
4. **Validation:** Execute record reconciliation comparing source row counts with target PostgreSQL counts.
5. **Cutover:** Update microservice connection strings to point exclusively to PostgreSQL.
