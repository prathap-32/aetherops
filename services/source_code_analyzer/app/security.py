"""Production request authentication for the Module 3 service boundary.

The API gateway validates tokens before proxying. Module 3 independently verifies
the same bearer JWT so direct service access cannot bypass that boundary.
"""
from __future__ import annotations

import os
from typing import Any

import jwt
from fastapi import HTTPException, Request, status

DEV_DEFAULT_JWT_SECRET = "aetherops-super-secure-production-cryptographic-jwt-token-signing-key-2026-cloudops-master"

INSECURE_SECRETS = {
    "", "secret", "changeme", "admin", "default", "test", "dev",
    "aetherops-super-secure-production-cryptographic-jwt-token-signing-key-2026-cloudops-master",
}


def verify_request_identity(request: Request) -> dict[str, Any] | None:
    environment = os.getenv("AETHER_ENV", os.getenv("ENVIRONMENT", "development")).lower()
    is_production = environment == "production"

    authorization = request.headers.get("authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        if is_production:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="A valid bearer token is required.",
            )
        return None

    configured_secret = os.getenv("JWT_SECRET_KEY")
    secret = configured_secret if configured_secret else (
        None if is_production else DEV_DEFAULT_JWT_SECRET
    )
    if not secret or (is_production and secret in INSECURE_SECRETS):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Module 3 authentication is not securely configured.",
        )

    try:
        claims = jwt.decode(
            token.strip(),
            secret,
            algorithms=["HS256"],
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The bearer token is invalid or expired.",
        ) from exc

    if not claims.get("uuid") or not claims.get("sub") or not claims.get("tenant_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The authenticated token is missing required user or tenant identity claims.",
        )

    header_tenant = request.headers.get("x-tenant-id")
    token_tenant = claims["tenant_id"]
    if header_tenant and header_tenant != token_tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant identity does not match the authenticated token.",
        )

    return claims
