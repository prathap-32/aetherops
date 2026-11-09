import os
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
    os.environ["STRICT_APPROVAL_GATE"] = "true"
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
        os.environ["STRICT_APPROVAL_GATE"] = "false"
        assert response.status_code == 400
        assert "Approval Gate Violation" in response.json()["detail"]

def test_generate_iac_rejected_when_service_down():
    # When architecture studio is unreachable
    os.environ["STRICT_APPROVAL_GATE"] = "true"
    with patch("httpx.Client.get", side_effect=httpx.ConnectError("Connection refused")):
        payload = {
            "project_name": "fintech-core",
            "aws_region": "us-east-1",
            "iac_tool": "terraform",
            "architecture_version_id": "arch-v1-approved",
        }
        response = client.post("/api/v1/generate-iac", json=payload)
        os.environ["STRICT_APPROVAL_GATE"] = "false"
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

def test_generate_iac_enriched_from_ai_architecture_topology():
    status_mock = MagicMock()
    status_mock.status_code = 200
    status_mock.json.return_value = {
        "version_id": "arch-ai-v3",
        "is_approved": True,
        "status": "APPROVED",
        "approval_id": "arch-appr-ai"
    }

    review_mock = MagicMock()
    review_mock.status_code = 200
    review_mock.json.return_value = {
        "version_id": "arch-ai-v3",
        "is_approved": True,
        "environment_tier": "enterprise",
        "target_region": "us-west-2",
        "nodes": [
            {"id": "vpc", "data": {"resource_type": "vpc", "label": "AWS VPC (10.0.0.0/16)"}},
            {"id": "alb", "data": {"resource_type": "alb", "label": "Application Load Balancer"}},
            {"id": "waf", "data": {"resource_type": "waf", "label": "AWS WAFv2"}},
            {"id": "kms", "data": {"resource_type": "kms", "label": "AWS KMS Key"}}
        ],
        "resource_inventory": [
            {"name": "Database RDS", "resource_type": "rds"}
        ]
    }

    def side_effect(url, *args, **kwargs):
        if "status" in url:
            return status_mock
        return review_mock

    with patch("httpx.Client.get", side_effect=side_effect):
        payload = {
            "project_name": "ai-enterprise-app",
            "architecture_version_id": "arch-ai-v3",
        }
        response = client.post("/api/v1/generate-iac", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["summary"]["target_region"] == "us-west-2"
        main_tf = next(f["content"] for f in data["files"] if f["filename"] == "main.tf")
        assert "aws_lb" in main_tf
        assert "aws_wafv2_web_acl" in main_tf
        assert "aws_kms_key" in main_tf
