from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.security import verify_request_identity


def make_request(headers: list[tuple[bytes, bytes]]) -> Request:
    return Request({
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/api/v1/repo/scan",
        "raw_path": b"/api/v1/repo/scan",
        "query_string": b"",
        "headers": headers,
        "server": ("testserver", 80),
        "client": ("127.0.0.1", 12345),
    })


def test_production_api_requires_bearer_token(monkeypatch):
    monkeypatch.setenv("AETHER_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "unit-test-secret-with-sufficient-entropy")
    with pytest.raises(HTTPException) as error:
        verify_request_identity(make_request([]))
    assert error.value.status_code == 401


def test_production_api_verifies_tenant_claim(monkeypatch):
    secret = "unit-test-secret-with-sufficient-entropy"
    monkeypatch.setenv("AETHER_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", secret)
    token = jwt.encode(
        {
            "sub": "test-user",
            "uuid": "user-123",
            "tenant_id": "tenant-123",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        secret,
        algorithm="HS256",
    )
    request = make_request([
        (b"authorization", f"Bearer {token}".encode()),
        (b"x-tenant-id", b"tenant-other"),
    ])
    with pytest.raises(HTTPException) as error:
        verify_request_identity(request)
    assert error.value.status_code == 403

def test_development_api_validates_present_bearer_token(monkeypatch):
    secret = "aetherops-super-secure-production-cryptographic-jwt-token-signing-key-2026-cloudops-master"
    monkeypatch.setenv("AETHER_ENV", "development")
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    token = jwt.encode(
        {
            "sub": "test-user",
            "uuid": "user-123",
            "tenant_id": "tenant-123",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        secret,
        algorithm="HS256",
    )
    identity = verify_request_identity(
        make_request([(b"authorization", f"Bearer {token}".encode())])
    )
    assert identity["tenant_id"] == "tenant-123"


def test_development_api_does_not_accept_unverified_tenant_header(monkeypatch):
    monkeypatch.setenv("AETHER_ENV", "development")
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    assert verify_request_identity(make_request([(b"x-tenant-id", b"tenant-forged")])) is None
