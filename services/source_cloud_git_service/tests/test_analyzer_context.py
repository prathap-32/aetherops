from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request

import app.router as router_module


def make_request(headers: list[tuple[bytes, bytes]]) -> Request:
    return Request({
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/api/v1/connections/conn-1/analyzer-context",
        "raw_path": b"/api/v1/connections/conn-1/analyzer-context",
        "query_string": b"",
        "headers": headers,
        "server": ("testserver", 80),
        "client": ("127.0.0.1", 12345),
    })


@pytest.mark.asyncio
async def test_analyzer_context_rejects_tenant_header_not_matching_jwt(monkeypatch):
    monkeypatch.setattr(
        router_module,
        "decode_access_token",
        lambda token: {"uuid": "user-1", "tenant_id": "tenant-a"},
    )
    request = make_request([
        (b"authorization", b"Bearer signed-token"),
        (b"x-tenant-id", b"tenant-b"),
    ])
    with pytest.raises(HTTPException) as error:
        await router_module.get_analyzer_source_context(
            "conn-1", request, db=object(), admin={"username": "alice"}
        )
    assert error.value.status_code == 403


@pytest.mark.asyncio
async def test_analyzer_context_requires_tenant_claim(monkeypatch):
    monkeypatch.setattr(router_module, "decode_access_token", lambda token: {"uuid": "user-1"})
    request = make_request([(b"authorization", b"Bearer signed-token")])
    with pytest.raises(HTTPException) as error:
        await router_module.get_analyzer_source_context(
            "conn-1", request, db=object(), admin={"username": "alice"}
        )
    assert error.value.status_code == 403


@pytest.mark.asyncio
async def test_analyzer_context_requires_encrypted_pat(monkeypatch):
    monkeypatch.setattr(
        router_module,
        "decode_access_token",
        lambda token: {"uuid": "user-1", "tenant_id": "tenant-a"},
    )

    async def fake_get_connection(*args, **kwargs):
        return SimpleNamespace(
            id="conn-1",
            tenant_id="tenant-a",
            encrypted_pat=None,
            pat_nonce=None,
            pat_tag=None,
        )

    monkeypatch.setattr(router_module, "_get_conn_or_404", fake_get_connection)
    request = make_request([(b"authorization", b"Bearer signed-token")])
    with pytest.raises(HTTPException) as error:
        await router_module.get_analyzer_source_context(
            "conn-1", request, db=object(), admin={"username": "alice"}
        )
    assert error.value.status_code == 409
