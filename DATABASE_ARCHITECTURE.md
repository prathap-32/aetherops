# AetherOps Central Database Architecture

## Overview
AetherOps utilizes a hybrid persistence architecture combining PostgreSQL as the central persistent database and service-level persistent SQLite databases for microservice isolation.

## User & Authentication Schema (`auth.db`)
- **Users Table:** Stores `id`, `uuid`, `username`, `email`, `password_hash`, `role`, `account_id`, `tenant_id`, `created_at`, `last_login_at`, `email_verified`, and `auth_provider`.
- **Auth Provider Tracking:** Explicitly records `credentials`, `google`, or `github` upon registration and updates during login callbacks.
- **Admin Analytics Aggregation:** Grouped SQL count queries efficiently compute statistics per provider without loading unnecessary records into memory.
