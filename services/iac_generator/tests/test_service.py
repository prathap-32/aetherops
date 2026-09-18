# services/iac_generator/tests/test_service.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["port"] == 8003

def test_generate_iac():
    payload = {
        "project_name": "fintech-core",
        "aws_region": "us-east-1",
        "iac_tool": "terraform",
        "compute_instance_type": "m5.large",
        "compute_count": 3,
        "database_instance_type": "db.m5.large",
        "database_storage_gb": 100,
        "database_multi_az": True,
        "enable_alb": True,
        "enable_waf": True,
        "enable_kms": True
    }
    response = client.post("/api/v1/generate-iac", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert len(data["files"]) >= 4
    filenames = [f["filename"] for f in data["files"]]
    assert "main.tf" in filenames
    assert "provider.tf" in filenames
    assert "variables.tf" in filenames
    assert "outputs.tf" in filenames
