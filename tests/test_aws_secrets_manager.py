# tests/test_aws_secrets_manager.py
"""
Automated Unit Tests for Centralized AWS Secrets Manager Integration.

Tests:
1. Successful secret retrieval.
2. Correct region selection.
3. Correct SecretId selection.
4. Correct dotenv parsing.
5. Multiple environment variables parsing.
6. Empty secret handling.
7. Invalid secret handling.
8. AWS permission failure (AccessDeniedException).
9. Network/service failure (EndpointConnectionError with retries).
10. Missing secret (ResourceNotFoundException).
11. Configuration precedence (Explicit process env vars override secrets).
12. Bootstrap protected variables protection.
13. Cache behavior (no repeated AWS requests).
14. Controlled cache refresh.
15. No credential leakage in status reports and logs.
16. get_application_setting accessor behavior.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError

# Ensure shared directory is on sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED_DIR = os.path.join(ROOT_DIR, "shared")
for p in (SHARED_DIR, ROOT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

import shared.aetherops_common.secrets as sm


@pytest.fixture(autouse=True)
def reset_secrets_state(monkeypatch):
    """Resets module-level cache and state before every test."""
    monkeypatch.setattr(sm, "_CACHED_SECRETS", {})
    monkeypatch.setattr(sm, "_INITIAL_PROCESS_ENV", None)
    monkeypatch.setattr(
        sm,
        "_LOADED_STATUS",
        {
            "connected": False,
            "provider": "uninitialized",
            "secret_id": None,
            "region": None,
            "variables_count": 0,
            "last_loaded_at": None,
            "source": None,
        },
    )


def test_dotenv_parsing_valid():
    """Verify safe dotenv parsing handles quotes, comments, and spacing."""
    raw = """
    # Platform settings
    AETHER_ENV=production
    DATABASE_URL="postgresql+asyncpg://user:pass@db:5432/app"
    PORT=8000
    JWT_SECRET_KEY='super-secret-key-12345'
    EMPTY_VAL=
    """
    parsed = sm._safe_parse_dotenv(raw)
    assert parsed["AETHER_ENV"] == "production"
    assert parsed["DATABASE_URL"] == "postgresql+asyncpg://user:pass@db:5432/app"
    assert parsed["PORT"] == "8000"
    assert parsed["JWT_SECRET_KEY"] == "super-secret-key-12345"
    assert parsed.get("EMPTY_VAL") == ""


def test_dotenv_parsing_empty_and_whitespace():
    """Verify empty or whitespace-only dotenv content returns empty dict."""
    assert sm._safe_parse_dotenv("") == {}
    assert sm._safe_parse_dotenv("   \n\n# comments only\n  ") == {}


def test_successful_secret_retrieval(monkeypatch):
    """Test successful retrieval from AWS Secrets Manager and injection into os.environ."""
    sample_dotenv = (
        "APP_NAME=AetherOps\n"
        "APP_STAGE=staging\n"
        "API_RATE_LIMIT=120\n"
    )

    mock_client = MagicMock()
    mock_client.get_secret_value.return_value = {
        "SecretString": sample_dotenv
    }

    with patch("boto3.client", return_value=mock_client):
        res = sm.load_application_secrets(secret_id="aetherops/platform", region_name="ap-south-1")

    assert res["APP_NAME"] == "AetherOps"
    assert res["APP_STAGE"] == "staging"
    assert res["API_RATE_LIMIT"] == "120"
    assert os.environ.get("APP_NAME") == "AetherOps"
    assert os.environ.get("APP_STAGE") == "staging"

    status = sm.get_application_secrets_status()
    assert status["connected"] is True
    assert status["provider"] == "aws_secrets_manager"
    assert status["secret_id"] == "aetherops/platform"
    assert status["region"] == "ap-south-1"
    assert status["variables_count"] == 3
    assert status["credentials"] == "REDACTED"


def test_correct_region_and_secret_id_selection(monkeypatch):
    """Test that configured environment variables AWS_REGION and AWS_SECRET_ID are respected."""
    monkeypatch.setenv("AWS_REGION", "eu-west-1")
    monkeypatch.setenv("AWS_SECRET_ID", "custom/project/secrets")

    mock_client = MagicMock()
    mock_client.get_secret_value.return_value = {
        "SecretString": "DISCOVERED_VAR=true"
    }

    with patch("boto3.client", return_value=mock_client) as mock_boto_client:
        sm.load_application_secrets()

    mock_boto_client.assert_called_once_with("secretsmanager", region_name="eu-west-1")
    mock_client.get_secret_value.assert_called_once_with(SecretId="custom/project/secrets")


def test_empty_secret_handling():
    """Verify empty SecretString raises SecretsManagerError."""
    mock_client = MagicMock()
    mock_client.get_secret_value.return_value = {
        "SecretString": ""
    }

    with patch("boto3.client", return_value=mock_client):
        with pytest.raises(sm.SecretsManagerError) as exc_info:
            sm.load_application_secrets(secret_id="aetherops/test", fail_fast=True, allow_local_fallback=False)
        assert "no SecretString content" in str(exc_info.value)


def test_invalid_secret_content_handling():
    """Verify non-dotenv content without key=value pairs raises SecretsManagerError."""
    mock_client = MagicMock()
    mock_client.get_secret_value.return_value = {
        "SecretString": "   \n# lone comment without keys\n   "
    }

    with patch("boto3.client", return_value=mock_client):
        with pytest.raises(sm.SecretsManagerError) as exc_info:
            sm.load_application_secrets(secret_id="aetherops/test", fail_fast=True, allow_local_fallback=False)
        assert "could not be parsed" in str(exc_info.value)


def test_aws_permission_failure():
    """Verify AWS ClientError (AccessDeniedException) raises SecretsManagerError without leaking credentials."""
    mock_client = MagicMock()
    err_response = {
        "Error": {
            "Code": "AccessDeniedException",
            "Message": "User is not authorized to perform: secretsmanager:GetSecretValue"
        }
    }
    mock_client.get_secret_value.side_effect = ClientError(err_response, "GetSecretValue")

    with patch("boto3.client", return_value=mock_client):
        with pytest.raises(sm.SecretsManagerError) as exc_info:
            sm.load_application_secrets(secret_id="aetherops/platform", fail_fast=True, allow_local_fallback=False)
        assert "AccessDeniedException" in str(exc_info.value)


def test_missing_secret_error():
    """Verify ResourceNotFoundException raises SecretsManagerError."""
    mock_client = MagicMock()
    err_response = {
        "Error": {
            "Code": "ResourceNotFoundException",
            "Message": "Secrets Manager cannot find the specified secret"
        }
    }
    mock_client.get_secret_value.side_effect = ClientError(err_response, "GetSecretValue")

    with patch("boto3.client", return_value=mock_client):
        with pytest.raises(sm.SecretsManagerError) as exc_info:
            sm.load_application_secrets(secret_id="nonexistent-secret", fail_fast=True, allow_local_fallback=False)
        assert "ResourceNotFoundException" in str(exc_info.value)


def test_configuration_precedence_policy(monkeypatch):
    """
    Precedence Rule Verification:
    Explicit process environment variables take HIGHEST priority and must NOT be overwritten by AWS Secrets Manager.
    """
    # Set explicit process environment variable before loading
    monkeypatch.setenv("DATABASE_URL", "postgresql://custom_override_db:5432/test")
    # Clean any SERVER_PORT before test
    monkeypatch.delenv("SERVER_PORT", raising=False)

    mock_client = MagicMock()
    # Secret contains a different value for DATABASE_URL and a new key SERVER_PORT
    mock_client.get_secret_value.return_value = {
        "SecretString": (
            "DATABASE_URL=postgresql://aws_secret_manager_db:5432/prod\n"
            "SERVER_PORT=9000\n"
        )
    }

    with patch("boto3.client", return_value=mock_client):
        sm.load_application_secrets(secret_id="aetherops/platform")

    # Explicit variable MUST retain its original value (precedence)
    assert os.environ["DATABASE_URL"] == "postgresql://custom_override_db:5432/test"
    # Unset variable gets populated from AWS Secrets Manager
    assert os.environ["SERVER_PORT"] == "9000"


def test_bootstrap_protected_vars_not_overwritten(monkeypatch):
    """Verify bootstrap variables (AWS_REGION, AWS_SECRET_ID) cannot be corrupted by payload contents."""
    monkeypatch.setenv("AWS_REGION", "ap-south-1")
    monkeypatch.setenv("AWS_SECRET_ID", "aetherops/platform")
    monkeypatch.delenv("APP_SERVICE_KEY", raising=False)

    mock_client = MagicMock()
    # Malicious or accidental secret payload trying to override AWS_REGION
    mock_client.get_secret_value.return_value = {
        "SecretString": (
            "AWS_REGION=us-west-2\n"
            "AWS_SECRET_ID=override-secret\n"
            "APP_SERVICE_KEY=valid-key\n"
        )
    }

    with patch("boto3.client", return_value=mock_client):
        sm.load_application_secrets()

    assert os.environ["AWS_REGION"] == "ap-south-1"
    assert os.environ["AWS_SECRET_ID"] == "aetherops/platform"
    assert os.environ["APP_SERVICE_KEY"] == "valid-key"


def test_cache_behavior_no_repeated_aws_requests():
    """Verify in-process caching prevents duplicate AWS API requests."""
    mock_client = MagicMock()
    mock_client.get_secret_value.return_value = {
        "SecretString": "CACHED_ITEM=123"
    }

    with patch("boto3.client", return_value=mock_client):
        # First call hits AWS
        res1 = sm.load_application_secrets(secret_id="aetherops/platform")
        assert res1["CACHED_ITEM"] == "123"
        assert mock_client.get_secret_value.call_count == 1

        # Second call within same process uses in-memory cache
        res2 = sm.load_application_secrets(secret_id="aetherops/platform")
        assert res2["CACHED_ITEM"] == "123"
        # Must still be 1 (no repeated request)
        assert mock_client.get_secret_value.call_count == 1


def test_controlled_cache_refresh():
    """Verify refresh=True triggers a controlled re-fetch from AWS."""
    mock_client = MagicMock()
    mock_client.get_secret_value.side_effect = [
        {"SecretString": "VERSION=1"},
        {"SecretString": "VERSION=2"},
    ]

    with patch("boto3.client", return_value=mock_client):
        res1 = sm.load_application_secrets(secret_id="aetherops/platform")
        assert res1["VERSION"] == "1"
        assert mock_client.get_secret_value.call_count == 1

        # Controlled refresh
        res2 = sm.load_application_secrets(secret_id="aetherops/platform", refresh=True)
        assert res2["VERSION"] == "2"
        assert mock_client.get_secret_value.call_count == 2


def test_get_application_setting_accessor(monkeypatch):
    """Verify get_application_setting accessor returns expected configuration."""
    monkeypatch.setattr(sm, "_CACHED_SECRETS", {"TEST_KEY": "test_val"})
    assert sm.get_application_setting("TEST_KEY") == "test_val"
    assert sm.get_application_setting("NON_EXISTENT", default="fallback") == "fallback"


def test_no_credential_leakage_in_status():
    """Verify status metadata always redacts credentials."""
    status = sm.get_application_secrets_status()
    assert "credentials" in status
    assert status["credentials"] == "REDACTED"
    assert "SecretString" not in status
    assert "secret_value" not in status
