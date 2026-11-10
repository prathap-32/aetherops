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
    assert data["port"] == 8007

def test_create_plan_and_risk(client):
    payload = {
        "project_name": "ecommerce-api",
        "target_region": "us-east-1",
        "environment_tier": "development"
    }
    res = client.post("/api/v1/deployments/plan", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "plan_id" in data
    assert "plan_hash" in data
    assert "changes" in data
    assert "risk_assessment" in data
    assert "cost_summary" in data
    assert "complexity_assessment" in data

    plan_id = data["plan_id"]
    get_res = client.get(f"/api/v1/deployments/plan/{plan_id}")
    assert get_res.status_code == 200
    assert get_res.json()["plan_id"] == plan_id
