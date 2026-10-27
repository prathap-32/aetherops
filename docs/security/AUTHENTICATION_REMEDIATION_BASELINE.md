# AetherOps Authentication & Security Remediation Baseline

**Document:** `docs/security/AUTHENTICATION_REMEDIATION_BASELINE.md`  
**Date:** October 25, 2026  
**Status:** Baseline Established  

---

## 1. Runtime Architecture and Service Inventory

The AetherOps system comprises 14 microservices and a React Vite frontend:

| # | Service Directory | Port | Browser-Facing? | Authentication Mechanism | Authorization Mechanism | Tenant Checks | Direct-Access Risk |
|---|---|:---:|:---:|---|---|---|---|
| 1 | `services/auth_service` | 7999 | Direct (frontend bypass) | JWT (HS256) + bcrypt; mock token backdoor | Role claim | Account / Tenant ID in token | High (`0.0.0.0` exposure) |
| 2 | `services/gateway` | 8000 | Yes (Primary entry point) | None enforced (Reverse proxy) | None | Checks X-Account-ID against token | Medium (Reverse proxy) |
| 3 | `services/project_and_environment_management` | 8001 | Direct (tested direct) | Bearer JWT / Cookie / Mock token / API key | TenantContext (RBAC) | Yes, but bypassed by admin username | High (`0.0.0.0` exposure) |
| 4 | `services/source_and_cloud_connection` | 8002 | Direct | Bearer JWT / Cookie / Master API key | Owner string matching | Partial | High (`0.0.0.0` exposure) |
| 5 | `services/repo_analyzer_service` | 8003 | Direct / Gateway | **None** | **None** | None | High (`0.0.0.0` exposure) |
| 6 | `services/requirement_analysis` | 8004 | Direct / Gateway | None on core / API Key on admin | None | None | High (`0.0.0.0` exposure) |
| 7 | `services/architecture_generator` | 8004 / 8005 | Direct / Gateway | **None** | **None** | None | High (`0.0.0.0` exposure) |
| 8 | `services/iac_generator` | 8006 | Direct / Gateway | **None** | **None** | None | High (`0.0.0.0` exposure) |
| 9 | `services/finops_optimizer` | 8007 | Direct / Gateway | **None** | **None** | None | High (`0.0.0.0` exposure) |
| 10 | `services/security_scanner` | 8008 | Direct / Gateway | **None** | **None** | None | High (`0.0.0.0` exposure) |
| 11 | `services/cicd_pipeline` | 8009 | Direct / Gateway | **None** | **None** | None | High (`0.0.0.0` exposure) |
| 12 | `services/observability_setup` | 8010 | Direct / Gateway | **None** | **None** | None | High (`0.0.0.0` exposure) |
| 13 | `services/cloud_deployer` | 8011 | Direct / Gateway | **None** | **None** | None | Low (Simulated execution) |
| 14 | `services/admin_console` | 8012 | Direct / Gateway | Bearer JWT / Cookie / Master API key | Role check | None | High (`0.0.0.0` exposure) |

---

## 2. Verified Vulnerabilities Targeted for Remediation

1. **Mock Token Backdoor**: `mock_token_*` prefix accepted in `auth_service` and `project_and_environment_management`.
2. **Platform Super Admin Privilege Escalation**: Literal username matching `"admin"` or `"root_admin"` in `tenant_context.py` granting platform-wide super admin rights.
3. **Gateway Bypass**: Frontend calls `http://localhost:7999` directly for auth rather than `http://localhost:8000/api/v1/auth`.
4. **Gateway Insecure Header Forwarding**: Gateway forwards arbitrary incoming `x-user-*` and `x-tenant-*` headers when unauthenticated.
5. **Gateway Missing Auth Enforcement**: Gateway proxies to downstream microservices without requiring valid tokens.
6. **Unprotected Microservices**: 8 downstream microservices enforce zero authentication.
7. **OAuth CSRF**: Google and GitHub OAuth callbacks accept `state` but never validate it against stored session state.
8. **Insecure PostMessage & Query String Token Exposure**: PostMessage uses target origin `'*'`, frontend listener lacks origin validation, fallback redirect leaks JWT in URL query parameters.
9. **Insecure Plaintext Password Comparison Fallback**: `_verify_password` in `auth_service` allows plaintext password match.
10. **Permissive CORS & Host Binding**: Services bind to `0.0.0.0` with `allow_origins=["*"]` and `allow_credentials=True`.
