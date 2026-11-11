from app.universal_scanner import run_universal_scan


def test_empty_repository_does_not_receive_fabricated_ports(tmp_path):
    report = run_universal_scan(tmp_path)
    assert report["ports"] == []
    assert report["workload_type"] == "UNKNOWN / INSUFFICIENT_EVIDENCE"

def test_local_monorepo_dependency_inventory_is_bounded_and_scoped(tmp_path):
    from app.universal_scanner import run_universal_scan

    api = tmp_path / "apps" / "api"
    web = tmp_path / "apps" / "web"
    api.mkdir(parents=True)
    web.mkdir(parents=True)
    (api / "pyproject.toml").write_text(
        '[project]\ndependencies = ["fastapi==0.115.0"]\n',
        encoding="utf-8",
    )
    (web / "package.json").write_text(
        '{"dependencies":{"react":"18.2.0"}}',
        encoding="utf-8",
    )

    report = run_universal_scan(tmp_path)
    assert report["is_monorepo"] is True
    assert set(report["application_roots"]) == {"apps/api", "apps/web"}
    assert {item["package_name"] for item in report["dependencies_detected"]} == {
        "fastapi", "react"
    }
    assert report["dependency_count"] == 2


import pytest
from app import universal_scanner


@pytest.mark.anyio
async def test_connection_context_requires_verified_tenant_identity():
    with pytest.raises(ValueError):
        await universal_scanner.fetch_connection_analysis_context(
            connection_id="connection-1",
            authorization="",
            tenant_id="",
        )


@pytest.mark.anyio
async def test_connection_context_rejects_cross_tenant_response(monkeypatch):
    context = {
        "connection_id": "connection-1",
        "tenant_id": "tenant-other",
        "project_id": "project-1",
        "environment_id": "environment-1",
        "commit_sha": "a" * 40,
        "tree": [],
        "manifest_contents": {},
    }

    class FakeResponse:
        status_code = 200
        def json(self):
            return context

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return False
        async def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(universal_scanner.httpx, "AsyncClient", FakeClient)
    with pytest.raises(PermissionError):
        await universal_scanner.fetch_connection_analysis_context(
            connection_id="connection-1",
            authorization="Bearer verified-token",
            tenant_id="tenant-a",
            project_id="project-1",
            environment_id="environment-1",
        )
