# AetherOps Database Setup Guide

## PostgreSQL 15 Centralized Setup
1. Deploy PostgreSQL container via Docker Compose using `aetherops_platform` database name.
2. Execute schema bootstrap scripts to create the 19 logical schemas and assign roles (`aetherops_migrator`, `aetherops_app`, `aetherops_readonly`).
3. Run Alembic migrations.
