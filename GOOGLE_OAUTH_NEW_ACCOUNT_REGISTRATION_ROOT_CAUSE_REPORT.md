# GOOGLE OAUTH NEW ACCOUNT REGISTRATION ROOT-CAUSE REPORT

## 1. Investigation Findings & Root Cause
- **Root Cause**: The `/api/v1/auth/me` endpoint in `auth_service` queried the `users` database record successfully upon OAuth login, but omitted `has_seen_welcome` from its returned JSON dictionary.
- **Impact**: On the frontend, `user.has_seen_welcome` evaluated to `undefined`, which caused `user && user.has_seen_welcome === 0` to fail. As a result, newly registered Google OAuth users incorrectly received the returning-user greeting ("Welcome back") instead of "Welcome to AetherOps".

## 2. Affected Files & Functions
- **File**: `services/auth_service/app/main.py`
- **Function**: `get_me(request: Request)`

## 3. Proposed Correction
- Include `"has_seen_welcome": user["has_seen_welcome"]` in the profile dictionary returned by `/api/v1/auth/me`.
