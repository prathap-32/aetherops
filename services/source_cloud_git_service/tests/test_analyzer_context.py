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

def test_manifest_redaction_preserves_dependency_fields_and_removes_json_tokens():
    content = '{"dependencies":{"fastapi":"==0.115.0"},"token":"ghp_sensitive"}'
    redacted = router_module._redact_analysis_manifest_content("package.json", content)
    assert '"fastapi":"==0.115.0"' in redacted
    assert "ghp_sensitive" not in redacted
    assert "[REDACTED]" in redacted


def test_manifest_redaction_removes_yaml_and_xml_secret_values():
    yaml_content = """environment:
  PASSWORD: super-secret
  API_TOKEN=ghp_sensitive"""
    redacted_yaml = router_module._redact_analysis_manifest_content("compose.yaml", yaml_content)
    assert "super-secret" not in redacted_yaml
    assert "ghp_sensitive" not in redacted_yaml
    xml_content = "<settings><password>super-secret</password></settings>"
    redacted_xml = router_module._redact_analysis_manifest_content("pom.xml", xml_content)
    assert "super-secret" not in redacted_xml
    assert "[REDACTED]" in redacted_xml
