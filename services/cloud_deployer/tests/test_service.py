# services/cloud_deployer/tests/test_service.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["port"] == 8008

def test_deploy_infrastructure():
    payload = {
        "project_name": "prod-workload",
        "target_region": "us-east-1",
        "dry_run": False
    }
    response = client.post("/api/v1/deploy", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert len(data["resources_applied"]) >= 3
    assert data["state_lock_acquired"] is True

def test_drift_detection():
    payload = {
        "project_name": "prod-workload",
        "target_region": "us-east-1"
    }
    response = client.post("/api/v1/drift-detection", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["is_in_sync"] is True
    assert data["total_drift_items"] == 0
