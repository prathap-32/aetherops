# AetherOps User Data & Credential Security Audit

## Security Policies & Implementation

### 1. Password Hashing
- **Algorithm:** bcrypt with salted key derivation.
- **Rule:** Plaintext passwords are **never** stored in the database or exposed via API responses.

### 2. OAuth Credentials & Tokens
- **Protection:** OAuth access tokens, refresh tokens, client secrets, and session cookies are stored securely using HttpOnly, Secure, and SameSite cookie policies.
- **Exposure Prevention:** Credentials are never exposed to the frontend or included in logs/error traces.

### 3. Authentication Provider Tracking
- Normalized provider identifiers:
  - `credentials` (Email/password registration)
  - `google` (Google OAuth 2.0 login)
  - `github` (GitHub OAuth login)
- Tracked per user account in persistent database records.

### 4. Tenant & User Isolation
- Strict server-side verification extracts user ID and tenant ID from cryptographically signed JWT session tokens.
- Cross-tenant data access attempts are blocked with HTTP 403 / 404 responses.
