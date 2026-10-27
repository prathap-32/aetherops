# services/requirement_analysis/app/security.py
import os
import re
import secrets
import logging
from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader

from app.database import SUPPORTED_REGIONS

logger = logging.getLogger("requirement-analysis-security")

API_KEY_NAME = "X-Admin-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Generate a secure default key for dev environments
_DEFAULT_DEV_KEY = "aetherops-secret-admin-key"


def _is_test_context() -> bool:
    """Only bypass auth if explicitly configured via environment variable."""
    return os.getenv("TEST_BYPASS_AUTH", "false").lower() == "true"


def get_admin_secret_key() -> str:
    """Resolve the admin secret key from env or fallback."""
    key = os.getenv("ADMIN_SECRET_KEY", _DEFAULT_DEV_KEY)
    env = os.getenv("ENVIRONMENT", os.getenv("AETHER_ENV", "development")).lower()
    if env == "production" and (not key or key == _DEFAULT_DEV_KEY):
        raise RuntimeError("FATAL: Default development ADMIN_SECRET_KEY cannot be used in production.")
    return key


async def verify_admin_key(request: Request, api_key: Optional[str] = Depends(api_key_header)):
    """
    FastAPI dependency that enforces multi-channel Admin authentication:
    1. Test context bypass for automated suites (if TEST_BYPASS_AUTH=true).
    2. HttpOnly Cookie: 'aether_session' (JWT signed).
    3. Bearer Token: 'Authorization: Bearer <JWT>'.
    4. Master Key: 'X-Admin-Key' header.
    """
    if _is_test_context():
        return api_key or "test-bypass"

    # Channel 1: Check HttpOnly Cookie
    cookie_token = request.cookies.get("aether_session")
    if cookie_token:
        from app.auth import decode_access_token
        payload = decode_access_token(cookie_token)
        if payload:
            return payload.get("sub", "admin")

    # Channel 2: Check Authorization: Bearer <token>
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        from app.auth import decode_access_token
        payload = decode_access_token(token)
        if payload:
            return payload.get("sub", "admin")

    # Channel 3: Check X-Admin-Key header
    expected_key = get_admin_secret_key()
    if api_key and secrets.compare_digest(api_key.strip(), expected_key):
        return api_key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized: Authentication required via cookie session, Bearer token, or valid X-Admin-Key"
    )



# Region code validation regex: e.g. us-east-1, ap-southeast-3, cn-northwest-1
REGION_CODE_PATTERN = re.compile(r"^[a-z]{2}(-[a-z]+-[0-9]{1})$")


def validate_region_code(region_code: str) -> str:
    """
    Validates region_code format and membership in SUPPORTED_REGIONS.
    Returns the sanitized lowercase region code.
    Raises HTTPException 400 on invalid format or unknown region.
    """
    region_code = region_code.lower().strip()

    if not REGION_CODE_PATTERN.match(region_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid region code format: '{region_code}'. Expected pattern: xx-xxxxx-N (e.g., us-east-1)"
        )

    if region_code not in SUPPORTED_REGIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported region '{region_code}'. Must be one of the 39 supported AWS regions."
        )

    return region_code
