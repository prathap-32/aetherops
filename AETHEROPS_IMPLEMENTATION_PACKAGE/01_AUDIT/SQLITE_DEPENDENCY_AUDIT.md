# AetherOps SQLite Dependency Audit

## Findings
- Legacy microservices utilized localized SQLite database files (`auth.db`, `projects.db`, `source_connections.db`, `architecture.db`, `admin_security.db`).
- **Removal Plan:** All production runtime persistence is transitioning to centralized PostgreSQL (`aetherops_platform`), eliminating production SQLite fallback. SQLite is retained exclusively for isolated testing fixtures.
