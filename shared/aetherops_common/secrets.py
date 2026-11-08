# shared/aetherops_common/secrets.py
"""
AetherOps Centralized Application Secrets Manager.

Retrieves application-level configuration directly from AWS Secrets Manager at runtime.
Parses plaintext dotenv SecretString, enforces explicit environment variable precedence,
and caches loaded credentials in-process to avoid redundant AWS API requests.

Security invariants:
- Never prints or logs sensitive credential values or SecretString.
- Never writes retrieved secrets to disk.
- Preserves explicit process environment variables over retrieved values.
- Uses AWS SDK default credential provider chain (AWS SSO locally, IAM role on EC2).
"""

import os
import sys
import io
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("aetherops.secrets")

# Protected non-sensitive bootstrap variables that should never be overridden by secret contents
BOOTSTRAP_PROTECTED_VARS = {
    "AWS_REGION",
    "AWS_DEFAULT_REGION",
    "AWS_SECRET_ID",
    "AETHER_SECRET_ID",
    "AWS_PROFILE",
    "AWS_CONFIG_FILE",
    "AWS_SHARED_CREDENTIALS_FILE",
}

# In-memory in-process secrets cache
_CACHED_SECRETS: Dict[str, str] = {}
_INITIAL_PROCESS_ENV: Optional[Dict[str, str]] = None
_LOADED_STATUS: Dict[str, Any] = {
    "connected": False,
    "provider": "uninitialized",
    "secret_id": None,
    "region": None,
    "variables_count": 0,
    "last_loaded_at": None,
    "source": None,
}


class SecretsManagerError(RuntimeError):
    """Raised when application secrets cannot be retrieved or parsed from AWS Secrets Manager."""
    pass


def _safe_parse_dotenv(content: str) -> Dict[str, str]:
    """
    Parses dotenv string content into a dictionary.
    Prefers python-dotenv's dotenv_values; falls back to an embedded parser.
    """
    if not content or not content.strip():
        return {}

    try:
        from dotenv import dotenv_values
        raw_parsed = dotenv_values(stream=io.StringIO(content))
        parsed = {k: v for k, v in raw_parsed.items() if k and v is not None}
    except ImportError:
        # Fallback safe dotenv parser if python-dotenv is not yet available in current scope
        parsed: Dict[str, str] = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key:
                    parsed[key] = val

    # Sanitize any accidental space after protocol separator (e.g., "http: //" -> "http://")
    cleaned = {}
    for k, v in parsed.items():
        v_str = str(v).strip()
        if ": //" in v_str:
            v_str = v_str.replace(": //", "://")
        cleaned[k] = v_str
    return cleaned


def load_application_secrets(
    secret_id: Optional[str] = None,
    region_name: Optional[str] = None,
    refresh: bool = False,
    fail_fast: bool = True,
    allow_local_fallback: Optional[bool] = None,
) -> Dict[str, str]:
    """
    Loads application credentials from AWS Secrets Manager into process environment.

    Precedence Policy:
    1. Explicitly provided process environment variables have the highest priority.
    2. Retrieved Secrets Manager values fill variables that are not already defined.
    3. Missing/unreachable Secrets Manager in production/cloud fails fast with a clear error.

    Args:
        secret_id: The AWS Secrets Manager SecretId (defaults to AWS_SECRET_ID, AETHER_SECRET_ID, or 'aetherops/platform').
        region_name: AWS region (defaults to AWS_REGION, AWS_DEFAULT_REGION, or 'ap-south-1').
        refresh: Force re-fetching secrets from AWS Secrets Manager even if already cached.
        fail_fast: If True, raises SecretsManagerError on connection/retrieval failure.
        allow_local_fallback: If True, falls back to local .env if Secrets Manager is unreachable.
                              Defaults to checking AETHER_ALLOW_LOCAL_ENV_FALLBACK env var.

    Returns:
        Dict[str, str] containing the loaded configuration (for programmatic inspection if needed).
    """
    global _CACHED_SECRETS, _LOADED_STATUS, _INITIAL_PROCESS_ENV

    # Record snapshot of original environment prior to any secret injection to preserve precedence
    if _INITIAL_PROCESS_ENV is None:
        _INITIAL_PROCESS_ENV = dict(os.environ)

    # Return cached secrets immediately if already loaded and refresh not requested
    if _CACHED_SECRETS and not refresh:
        return _CACHED_SECRETS

    # Resolve bootstrap configuration
    target_region = (
        region_name
        or os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or "ap-south-1"
    )
    target_secret_id = (
        secret_id
        or os.getenv("AWS_SECRET_ID")
        or os.getenv("AETHER_SECRET_ID")
        or "aetherops/platform"
    )

    if allow_local_fallback is None:
        env_val = os.getenv("AETHER_ALLOW_LOCAL_ENV_FALLBACK")
        if env_val is not None:
            allow_local_fallback = env_val.lower() in ("true", "1", "yes")
        else:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            allow_local_fallback = os.path.exists(os.path.join(root_dir, ".env"))

    # Attempt retrieval from AWS Secrets Manager
    secret_string: Optional[str] = None
    retrieval_error: Optional[Exception] = None
    max_retries = 3
    base_backoff = 0.5

    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
    except ImportError as e:
        logger.warning("Boto3 is not installed or available: %s", e)
        if fail_fast and not allow_local_fallback:
            raise SecretsManagerError(
                f"Cannot load AWS Secrets Manager: boto3 package is not installed. {e}"
            ) from e
        retrieval_error = e

    if retrieval_error is None:
        for attempt in range(1, max_retries + 1):
            try:
                client = boto3.client("secretsmanager", region_name=target_region)
                response = client.get_secret_value(SecretId=target_secret_id)
                secret_string = response.get("SecretString")
                if not secret_string:
                    raise SecretsManagerError(
                        f"Secret '{target_secret_id}' in region '{target_region}' has no SecretString content."
                    )
                retrieval_error = None
                break
            except (NoCredentialsError, ClientError, EndpointConnectionError) as exc:
                retrieval_error = exc
                # Only retry transient connection or throttling errors
                is_throttled = False
                if hasattr(exc, "response") and isinstance(exc.response, dict):
                    err_code = exc.response.get("Error", {}).get("Code", "")
                    if err_code in ("ThrottlingException", "RequestLimitExceeded", "InternalServiceError"):
                        is_throttled = True

                if (isinstance(exc, EndpointConnectionError) or is_throttled) and attempt < max_retries:
                    sleep_time = base_backoff * (2 ** (attempt - 1))
                    logger.warning(
                        "Transient error contacting AWS Secrets Manager (attempt %d/%d). Retrying in %.2fs...",
                        attempt,
                        max_retries,
                        sleep_time,
                    )
                    time.sleep(sleep_time)
                else:
                    break
            except Exception as exc:
                retrieval_error = exc
                break

    # Handle success or fallback
    if secret_string:
        parsed = _safe_parse_dotenv(secret_string)
        if not parsed:
            raise SecretsManagerError(
                f"Retrieved SecretString for '{target_secret_id}' is empty or could not be parsed as dotenv format."
            )

        # Apply precedence: only set values that were NOT explicitly provided in the initial process environment
        injected_count = 0
        newly_cached: Dict[str, str] = {}
        for k, v in parsed.items():
            if not k or k in BOOTSTRAP_PROTECTED_VARS:
                continue
            if k not in _INITIAL_PROCESS_ENV:
                os.environ[k] = str(v)
                injected_count += 1
            newly_cached[k] = os.environ[k]

        _CACHED_SECRETS = newly_cached
        _LOADED_STATUS = {
            "connected": True,
            "provider": "aws_secrets_manager",
            "secret_id": target_secret_id,
            "region": target_region,
            "variables_count": len(parsed),
            "injected_count": injected_count,
            "last_loaded_at": time.time(),
            "source": f"aws_secrets_manager://{target_region}/{target_secret_id}",
        }

        logger.info(
            "AWS Secrets Manager: Connected. Loaded %d configuration variables from '%s' (%s). Redacted.",
            len(parsed),
            target_secret_id,
            target_region,
        )
        return _CACHED_SECRETS

    # If AWS Secrets Manager retrieval failed, evaluate fallback or fail fast
    if allow_local_fallback:
        logger.warning(
            "AWS Secrets Manager retrieval failed (%s). Attempting local .env fallback as configured by AETHER_ALLOW_LOCAL_ENV_FALLBACK.",
            retrieval_error,
        )
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        local_env = os.path.join(root_dir, ".env")
        if os.path.exists(local_env):
            try:
                with open(local_env, "r", encoding="utf-8") as f:
                    content = f.read()
                parsed = _safe_parse_dotenv(content)
                for k, v in parsed.items():
                    if k not in BOOTSTRAP_PROTECTED_VARS and k not in _INITIAL_PROCESS_ENV:
                        os.environ[k] = str(v)
                    _CACHED_SECRETS[k] = os.environ.get(k, str(v))

                _LOADED_STATUS = {
                    "connected": False,
                    "provider": "local_dotenv_fallback",
                    "secret_id": None,
                    "region": target_region,
                    "variables_count": len(parsed),
                    "last_loaded_at": time.time(),
                    "source": "local_dotenv",
                    "error": str(retrieval_error) if retrieval_error else "fallback",
                }
                logger.warning(
                    "Loaded %d variables from local .env fallback. Note: AWS Secrets Manager should be used in production.",
                    len(parsed),
                )
                return _CACHED_SECRETS
            except Exception as e:
                logger.error("Failed to read local fallback .env: %s", e)

    # Fail fast
    err_msg = (
        f"Failed to retrieve application secrets from AWS Secrets Manager for secret '{target_secret_id}' "
        f"in region '{target_region}'. Error: {retrieval_error}"
    )
    logger.error("AWS Secrets Manager Error: %s", err_msg)
    _LOADED_STATUS = {
        "connected": False,
        "provider": "failed",
        "secret_id": target_secret_id,
        "region": target_region,
        "variables_count": 0,
        "last_loaded_at": time.time(),
        "source": None,
        "error": str(retrieval_error) if retrieval_error else "unreachable",
    }
    if fail_fast:
        raise SecretsManagerError(err_msg) from retrieval_error

    return {}


def get_application_setting(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieves an application configuration value, ensuring secrets have been initialized.
    """
    if not _CACHED_SECRETS:
        try:
            load_application_secrets(fail_fast=False)
        except Exception:
            pass
    return os.environ.get(name, _CACHED_SECRETS.get(name, default))


def get_application_secrets_status() -> Dict[str, Any]:
    """
    Returns non-sensitive connectivity and cache metadata for diagnostics and health checks.
    NEVER returns credential values or SecretString content.
    """
    status_copy = dict(_LOADED_STATUS)
    status_copy["cached"] = bool(_CACHED_SECRETS)
    status_copy["credentials"] = "REDACTED"
    return status_copy
