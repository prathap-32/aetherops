# services/iac_generator/tests/test_service.py
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import httpx
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["port"] == 8006

def test_generate_iac_rejected_without_architecture_approval():
    # Attempting generation without architecture_version_id must be rejected with 400
    payload = {
        "project_name": "fintech-core",
        "aws_region": "us-east-1",
        "iac_tool": "terraform",
    }
    response = client.post("/api/v1/generate-iac", json=payload)
    assert response.status_code == 400
    assert "Approval Gate Violation" in response.json()["detail"]

def test_generate_iac_rejected_with_unapproved_version():
    # When architecture studio reports is_approved=False
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "version_id": "arch-v1-draft",
        "is_approved": False,
        "status": "DRAFT"
    }

    with patch("httpx.Client.get", return_value=mock_resp):
        payload = {
            "project_name": "fintech-core",
            "aws_region": "us-east-1",
            "iac_tool": "terraform",
            "architecture_version_id": "arch-v1-draft",
        }
        response = client.post("/api/v1/generate-iac", json=payload)
        assert response.status_code == 400
        assert "Approval Gate Violation" in response.json()["detail"]

def test_generate_iac_rejected_when_service_down():
    # When architecture studio is unreachable
    with patch("httpx.Client.get", side_effect=httpx.ConnectError("Connection refused")):
        payload = {
            "project_name": "fintech-core",
            "aws_region": "us-east-1",
            "iac_tool": "terraform",
            "architecture_version_id": "arch-v1-approved",
        }
        response = client.post("/api/v1/generate-iac", json=payload)
        assert response.status_code == 400
        assert "Approval Gate Verification Failed" in response.json()["detail"]

def test_generate_iac_success_with_approved_version():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "version_id": "arch-approved-v1",
        "is_approved": True,
        "status": "APPROVED",
        "approval_id": "arch-appr-abc12345"
    }

    with patch("httpx.Client.get", return_value=mock_resp):
        payload = {
            "project_name": "fintech-core",
            "aws_region": "us-east-1",
            "iac_tool": "terraform",
            "architecture_version_id": "arch-approved-v1",
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
        assert data["architecture_version_id"] == "arch-approved-v1"
        assert data["terraform_version_id"].startswith("tf-")
        assert len(data["checksum"]) == 64  # SHA256 length
        assert len(data["files"]) >= 4
        filenames = [f["filename"] for f in data["files"]]
        assert "main.tf" in filenames
        assert "provider.tf" in filenames
        assert "variables.tf" in filenames
        assert "outputs.tf" in filenames
        # Validation report check
        assert data["validation"].get("fmt") in ("PASS", "NOT_RUN", "SKIPPED")

def test_generate_iac_alternate_endpoint():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "version_id": "arch-approved-v2",
        "is_approved": True,
        "status": "APPROVED",
        "approval_id": "arch-appr-xyz987"
    }

    with patch("httpx.Client.get", return_value=mock_resp):
        payload = {
            "project_name": "fintech-core",
            "aws_region": "us-east-1",
            "architecture_version_id": "arch-approved-v2",
        }
        response = client.post("/api/v1/iac/generate", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "SUCCESS"

