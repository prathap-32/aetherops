# AetherOps Admin Panel — User Analytics & OAuth Provider Breakdown

## Overview
The Admin Console features an integrated **User Analytics & Authentication Breakdown** card reflecting real-time backend database statistics across all registered users and authentication providers.

## Authentication Provider Tracking
- **Credentials:** Email/password registered accounts (`auth_provider = 'credentials'`).
- **Google OAuth:** Google sign-in accounts (`auth_provider = 'google'`).
- **GitHub OAuth:** GitHub sign-in accounts (`auth_provider = 'github'`).

## Counting Rules & API Structure
- **Endpoint:** `GET /api/v1/admin/users/statistics` (proxied via Admin Console at `/api/admin/users/statistics`).
- **Response Schema:**
  ```json
  {
    "total_users": 11,
    "google_users": 0,
    "github_users": 0,
    "credentials_users": 11,
    "providers": {
      "google": 0,
      "github": 0,
      "credentials": 11
    },
    "users": [...],
    "updated_at": "2026-11-10T16:59:08Z"
  }
  ```
- **Uniqueness:** All Users counts distinct internal user IDs. Provider categories count users linked to each authentication method.
