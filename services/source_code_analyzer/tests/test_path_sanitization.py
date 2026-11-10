# services/repo_analyzer_service/tests/test_path_sanitization.py
"""
Tests for repository path sanitization and directory traversal prevention.
"""
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app, validate_safe_repo_path
from fastapi import HTTPException


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.parametrize("bad_path,expected_status", [
    ("/", 400),
    ("/etc", 403),
    ("/etc/passwd", 403),
    ("/proc", 403),
    ("/sys", 403),
    ("/root", 403),
    ("/var/log", 403),
    ("~/.ssh", 403),
    ("~/.aws", 403),
])
def test_validate_safe_repo_path_blocks_system_and_credentials(bad_path, expected_status):
    with pytest.raises(HTTPException) as excinfo:
        validate_safe_repo_path(bad_path)
    assert excinfo.value.status_code == expected_status


@pytest.mark.anyio
async def test_scan_endpoint_rejects_sensitive_paths(client):
    res = await client.post("/api/v1/repo/scan", json={"repo_path": "/etc"})
    assert res.status_code == 403
    assert "Access to system path" in res.json()["detail"]

    res_root = await client.post("/api/v1/repo/scan", json={"repo_path": "/"})
    assert res_root.status_code == 400

    res_ssh = await client.post("/api/v1/repo/scan", json={"repo_path": "~/.ssh"})
    assert res_ssh.status_code == 403
    assert "credential directory" in res_ssh.json()["detail"]


@pytest.mark.anyio
async def test_scan_endpoint_accepts_valid_directory(client):
    # Scan current repo workspace or temporary directory
    cwd = os.getcwd()
    res = await client.post("/api/v1/repo/scan", json={"repo_path": cwd, "include_findings": False})
    assert res.status_code == 200
    data = res.json()
    assert "components" in data or "languages" in data
