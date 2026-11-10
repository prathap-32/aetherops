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
    assert data["port"] == 8004

def test_catalog(client):
    res = client.get("/api/v1/catalog")
    assert res.status_code == 200
    data = res.json()
    assert "ec2" in data
    assert "rds" in data

def test_recommendation_dev(client):
    payload = {
        "project_id": "proj-123",
        "environment_id": "env-dev",
        "environment_tier": "development",
        "target_region": "us-east-1",
        "workload_type": "web_app"
    }
    res = client.post("/api/v1/recommendation", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "profile" in data
    assert data["profile"]["architecture_tier"] == "Developer"

def test_recommendation_prod(client):
    payload = {
        "project_id": "proj-123",
        "environment_id": "env-prod",
        "environment_tier": "production",
        "target_region": "us-east-1",
        "workload_type": "web_app"
    }
    res = client.post("/api/v1/recommendation", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["profile"]["architecture_tier"] == "Production-Standard"
    assert data["profile"]["high_availability_mode"] == "multi-az"
