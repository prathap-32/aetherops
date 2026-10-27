# AetherOps Authentication Architecture

## 1. Overview and Topology

AetherOps implements a **Gateway-Centric Zero-Trust Architecture**. All external browser traffic is terminated exclusively by the central API Gateway running on port `8000`. Direct ingress from external clients to downstream microservices (Auth Service on `7999`, Project & Environment Management on `8001`, Source & Cloud Connection on `8002`, Repo Analyzer on `8003`, Cloud Architecture Studio on `8004`, etc.) is strictly forbidden in production network topologies.

```
+-----------------------------------------------------------------------+
|                            Browser / Client                           |
+-----------------------------------------------------------------------+
                                   |
                                   | (Port 8000 only)
                                   v
+-----------------------------------------------------------------------+
|                        API Gateway (Port 8000)                        |
| - Strips untrusted identity headers (X-Tenant-ID, X-User-ID, etc.)    |
| - Validates cryptographic HS256 JWT signature and expiration          |
| - Injects trusted verified headers:                                   |
|     X-User-ID, X-Authenticated-User, X-User-Role, X-Tenant-ID, etc.   |
| - Public whitelist: /api/v1/auth/login, /api/v1/meta, health probes   |
+-----------------------------------------------------------------------+
         |                 |                     |                 |
         | (Port 7999)     | (Port 8001)         | (Port 8002)     | (Ports 8003-8012)
         v                 v                     v                 v
+----------------+ +----------------+ +----------------+ +----------------+
|  Auth Service  | | Project & Env  | | Source & Cloud | | Analysis,      |
|  (Bcrypt, JWT  | | Manager        | | Connection     | | Architecture,  |
|   minting,     | | (Tenant RBAC,  | | (Vault/KMS     | | Deployer,      |
|   OAuth state) | |  CRUD, Quotas) | |  Cred storage) | |  Studio)       |
+----------------+ +----------------+ +----------------+ +----------------+
```

---

## 2. Authentication Flow

### 2.1 Password-Based Authentication
1. **Frontend Request**: The client issues `POST /api/v1/auth/login` with JSON payload `{"username": "...", "password": "..."}` to the Gateway on Port 8000.
2. **Reverse Proxy Dispatch**: Gateway matches the path as public and forwards the request to Auth Service (Port 7999).
3. **Cryptographic Password Verification**: Auth Service queries the persistent credentials store (`auth.db` / PostgreSQL). Plaintext fallback is strictly rejected. Passwords are salted and hashed using `bcrypt` (10-12 rounds) and verified using `bcrypt.checkpw()`.
4. **JWT Minting**:
   - Algorithm: `HS256` (HMAC with SHA-256).
   - Payload:
     ```json
     {
       "sub": "<username>",
       "uuid": "<user_uuid>",
       "email": "<email>",
       "role": "<ROLE>",
       "account_id": "<account_id>",
       "tenant_id": "<tenant_id>",
       "iat": 1792900000,
       "exp": 1792928800,
       "jti": "<secure_random_uuid>"
     }
     ```
   - Signed using `JWT_SECRET_KEY` (fail-closed in production if unconfigured or default).
5. **Token Delivery**: The signed JWT is returned in the JSON response payload (`{"token": "<jwt>", ...}`).

### 2.2 Subsequent Protected Requests
1. **Header Transmission**: Client sends `Authorization: Bearer <jwt>` to the Gateway on Port 8000.
2. **Gateway Stripping**: Gateway strips any client-supplied identity headers:
   `x-account-id`, `x-tenant-id`, `x-user-id`, `x-user-role`, `x-auth-type`, `x-user-email`, `x-authenticated-user`.
3. **Cryptographic Verification**:
   - Gateway decodes the JWT using `jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])`.
   - Rejects mock tokens (e.g. `mock_token_*`), expired tokens, tampered signatures, and invalid algorithms with `HTTP 401 Unauthorized`.
4. **Header Injection**:
   - Gateway injects verified identity claims:
     - `x-authenticated-user`: `payload["sub"]`
     - `x-user-id`: `payload["uuid"]`
     - `x-user-role`: `payload["role"]`
     - `x-tenant-id`: `payload["tenant_id"]`
     - `x-account-id`: `payload["account_id"]`
5. **Downstream Dispatch**: Downstream services receive trusted, sanitized headers and execute domain logic within verified tenant boundaries.

---

## 3. OAuth 2.0 & Social Identity Architecture

AetherOps supports OAuth 2.0 authentication via Google and GitHub.

### 3.1 State and CSRF Defense
1. **State Generation**: On `/api/v1/auth/google` or `/api/v1/auth/github`, Auth Service generates a cryptographically random 32-byte state: `secrets.token_urlsafe(32)`.
2. **Double-Submit State Cookie**:
   - Stored in an `HttpOnly`, `SameSite=Lax`, `Secure` cookie: `oauth_state_<provider>`.
   - Passed in the provider redirect authorization URL: `&state=<random_state>`.
3. **Callback Validation**:
   - Provider redirects user to `/api/v1/auth/<provider>/callback?code=...&state=...`.
   - Auth Service retrieves the `oauth_state_<provider>` cookie and validates `secrets.compare_digest(cookie_state, query_state)`.
   - Missing or mismatched states return `HTTP 400 Bad Request` immediately. The state cookie is deleted upon verification.

### 3.2 Secure Token Delivery
- Tokens are **never** appended to redirection URL query parameters.
- Browser popups communicate token credentials back to the main window via `postMessage`.
- Target origin is strictly restricted to `window.location.origin` (or verified application URL); the previous wildcard target (`"*"`) has been removed.
- The receiving page (`LoginPage.jsx`) explicitly verifies `event.origin === window.location.origin` before processing the token.

---

## 4. Session Termination & Revocation

1. **Client Logout**: Client invokes `POST /api/v1/auth/logout` via Gateway.
2. **Cookie Clearance**: Gateway and Auth Service expire any ambient session cookies with `Max-Age=0; Path=/; HttpOnly; SameSite=Lax`.
3. **Client Storage Clearance**: Frontend client discards the in-memory/storage token reference.
4. **Stateless JWT Lifespan Notice**: In V1, tokens are stateless HMAC-SHA256 JWTs. They remain mathematically valid until their expiration timestamp (`exp`, default 8 hours). Logout removes client-side state and cookies; server-side immediate revocation via a shared Redis denylist is planned for V2.

---

## 5. Fail-Closed Security Configuration

- **`JWT_SECRET_KEY`**: If `AETHER_ENV=production` or `ENVIRONMENT=production`, application startup verifies that `JWT_SECRET_KEY` is not empty and not the default development passphrase. Insecure configurations fail closed with `RuntimeError` or `logger.critical`.
- **`ADMIN_API_KEY`**: Development fallback keys (`aetherops-secret-admin-key`) are disabled in production mode.
- **CORS Configuration**: Wildcard origins (`*`) combined with credential allowances (`allow_credentials=True`) are prohibited. Gateway explicitly configures authorized origins (`http://localhost:8000`, `http://127.0.0.1:8000`, production frontend domains).
