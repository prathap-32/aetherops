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
    assert data["port"] == 8006

def test_validation_rules(client):
    res = client.get("/api/v1/validation/rules")
    assert res.status_code == 200
    data = res.json()
    assert "rules" in data
    assert "supported_resource_types" in data

def test_validation_pass(client):
    payload = {
        "project_id": "proj-1",
        "environment_tier": "development",
        "nodes": [
            {"id": "alb-1", "resource_type": "alb"},
            {"id": "ec2-1", "resource_type": "ec2"},
            {"id": "rds-1", "resource_type": "rds"}
        ],
        "edges": [
            {"id": "e1", "source": "alb-1", "target": "ec2-1"},
            {"id": "e2", "source": "ec2-1", "target": "rds-1"}
        ]
    }
    res = client.post("/api/v1/architecture/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "PASS"
    assert data["can_proceed_to_iac"] is True
    assert data["blocking_count"] == 0

def test_validation_blocked_missing_ingress(client):
    payload = {
        "project_id": "proj-1",
        "environment_tier": "development",
        "nodes": [
            {"id": "ec2-1", "resource_type": "ec2"}
        ],
        "edges": []
    }
    res = client.post("/api/v1/architecture/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "BLOCKED"
    assert data["can_proceed_to_iac"] is False
    assert data["blocking_count"] > 0
