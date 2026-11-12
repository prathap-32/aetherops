# AetherOps Permission Matrix

| Role | Schemas | Allowed Operations |
|---|---|---|
| `aetherops_migrator` | All 19 schemas | DDL (`CREATE`, `ALTER`, `DROP`, `GRANT`) |
| `aetherops_app` | Domain-specific schemas | DML (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) |
| `aetherops_readonly` | All 19 schemas | `SELECT` only |
