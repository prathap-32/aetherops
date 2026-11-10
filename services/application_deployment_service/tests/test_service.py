import pytest
from starlette.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["port"] == 8010

def test_deploy_application_flow(client):
    payload = {
        "service_name": "frontend-spa",
        "target_region": "us-east-1",
        "commit_sha": "a1b2c3d4",
        "container_port": 3000
    }
    res = client.post("/api/v1/deploy", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "DEPLOYED"
    assert data["service_name"] == "frontend-spa"
    assert "image_digest" in data
    assert "release_id" in data

    rel_id = data["release_id"]
    get_res = client.get(f"/api/v1/deployments/releases/{rel_id}")
    assert get_res.status_code == 200
    assert get_res.json()["release_id"] == rel_id
