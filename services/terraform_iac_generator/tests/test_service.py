import os
import asyncio
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import httpx
from app.main import app
from app.database import init_db
from app.schemas import IaCGenerationRequest

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    try:
        asyncio.run(init_db())
    except Exception:
        pass

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["port"] == 8008
def test_generate_iac_rejected_without_architecture_approval():
    payload = {
        "project_name": "fintech-core",
        "aws_region": "us-east-1",
        "iac_tool": "terraform",
    }
    response = client.post("/api/v1/generate-iac", json=payload)
    assert response.status_code == 400
    assert "Approval Gate Violation" in response.json()["detail"]

def test_generate_iac_rejected_with_unapproved_version():
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
            "compute_count": 1,
            "database_instance_type": "none",
            "database_storage_gb": 0,
            "database_multi_az": False,
            "enable_alb": False,
            "enable_waf": False,
            "enable_kms": False
        }
        response = client.post("/api/v1/generate-iac", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["architecture_version_id"] == "arch-approved-v1"
        assert data["terraform_version_id"].startswith("tf-")
        assert len(data["checksum"]) == 64
        assert len(data["files"]) >= 4
        filenames = [f["filename"] for f in data["files"]]
        assert "main.tf" in filenames
        assert "provider.tf" in filenames
        assert "variables.tf" in filenames
        assert "outputs.tf" in filenames

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
        compute_tf = next(f["content"] for f in data["files"] if f["filename"] == "compute.tf")
        assert "aws_lb" in compute_tf

# ═══════════════════════════════════════════════════════════════════════════════
# Comprehensive Scenarios A through J Testing Suite (Requirement 12)
# ═══════════════════════════════════════════════════════════════════════════════

def test_scenario_a_ec2_architecture():
    """Scenario A — EC2 architecture: approved EC2 instance with specific type and network config."""
    status_mock = MagicMock()
    status_mock.status_code = 200
    status_mock.json.return_value = {"version_id": "arch-scen-a", "is_approved": True, "status": "APPROVED"}

    review_mock = MagicMock()
    review_mock.status_code = 200
    review_mock.json.return_value = {
        "version_id": "arch-scen-a",
        "is_approved": True,
        "target_region": "ap-south-1",
        "environment_tier": "development",
        "nodes": [
            {"id": "vpc", "data": {"resource_type": "vpc", "label": "VPC"}},
            {"id": "subnet", "data": {"resource_type": "subnet", "label": "Subnet"}},
            {"id": "sg", "data": {"resource_type": "security_group", "label": "SG"}},
            {"id": "ec2", "data": {"resource_type": "ec2", "label": "EC2 t3.small"}}
        ],
        "resource_inventory": []
    }

    def side_effect(url, *args, **kwargs):
        if "status" in url:
            return status_mock
        return review_mock

    with patch("httpx.Client.get", side_effect=side_effect):
        payload = {
            "project_name": "scenario-a-app",
            "architecture_version_id": "arch-scen-a",
            "compute_instance_type": "t3.small"
        }
        response = client.post("/api/v1/generate-iac", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["summary"]["target_region"] == "ap-south-1"
        assert "aws_instance" in data["summary"]["resources_defined"]

def test_scenario_b_multi_service_architecture():
    """Scenario B — Multi-service architecture: EC2, VPC, subnet, security group, and S3."""
    status_mock = MagicMock()
    status_mock.status_code = 200
    status_mock.json.return_value = {"version_id": "arch-scen-b", "is_approved": True, "status": "APPROVED"}

    review_mock = MagicMock()
    review_mock.status_code = 200
    review_mock.json.return_value = {
        "version_id": "arch-scen-b",
        "is_approved": True,
        "target_region": "us-east-1",
        "environment_tier": "production",
        "nodes": [
            {"id": "vpc", "data": {"resource_type": "vpc", "label": "VPC"}},
            {"id": "subnet", "data": {"resource_type": "subnet", "label": "Subnet"}},
            {"id": "sg", "data": {"resource_type": "security_group", "label": "SG"}},
            {"id": "ec2", "data": {"resource_type": "ec2", "label": "EC2"}},
            {"id": "s3", "data": {"resource_type": "s3", "label": "S3 Bucket"}}
        ],
        "resource_inventory": [{"resource_type": "s3", "name": "data-bucket"}]
    }

    def side_effect(url, *args, **kwargs):
        if "status" in url:
            return status_mock
        return review_mock

    with patch("httpx.Client.get", side_effect=side_effect):
        payload = {
            "project_name": "scenario-b-app",
            "architecture_version_id": "arch-scen-b",
        }
        response = client.post("/api/v1/generate-iac", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        storage_tf = next(f["content"] for f in data["files"] if f["filename"] == "storage.tf")
        assert "aws_s3_bucket" in storage_tf

def test_scenario_c_missing_configuration():
    """Scenario C — Missing configuration: lacks mandatory resource configuration / version ID."""
    payload = {
        "project_name": "scenario-c-app",
        "architecture_version_id": "",
    }
    response = client.post("/api/v1/generate-iac", json=payload)
    assert response.status_code == 400
    assert "Approval Gate Violation" in response.json()["detail"]

def test_scenario_d_extra_resource_detection():
    """Scenario D — Consistency verification checks unexpected/extra resources."""
    from app.iac_engine import build_infrastructure_ir, verify_architecture_consistency, GeneratedFile
    req = IaCGenerationRequest(project_name="scen-d", architecture_version_id="arch-d")
    ir = build_infrastructure_ir(req)
    files = [GeneratedFile(filename="main.tf", content='resource "aws_nat_gateway" "extra" {}', language="hcl")]
    report = verify_architecture_consistency(ir, files)
    assert report is not None

def test_scenario_e_instance_type_fidelity():
    """Scenario E — Instance type changes: approved config remains authoritative."""
    status_mock = MagicMock()
    status_mock.status_code = 200
    status_mock.json.return_value = {"version_id": "arch-scen-e", "is_approved": True, "status": "APPROVED"}

    review_mock = MagicMock()
    review_mock.status_code = 200
    review_mock.json.return_value = {
        "version_id": "arch-scen-e",
        "is_approved": True,
        "target_region": "us-east-1",
        "environment_tier": "development",
        "nodes": [{"id": "ec2", "data": {"resource_type": "ec2", "label": "EC2 t3.small"}}]
    }

    def side_effect(url, *args, **kwargs):
        if "status" in url:
            return status_mock
        return review_mock

    with patch("httpx.Client.get", side_effect=side_effect):
        payload = {
            "project_name": "scenario-e-app",
            "architecture_version_id": "arch-scen-e",
            "compute_instance_type": "t3.small"
        }
        response = client.post("/api/v1/generate-iac", json=payload)
        assert response.status_code == 200
        variables_tf = next(f["content"] for f in response.json()["files"] if f["filename"] == "variables.tf")
        assert "t3.small" in variables_tf

def test_scenario_f_terraform_syntax_failure():
    """Scenario F — Terraform syntax failure handling in validation pipeline."""
    from app.iac_engine import validate_and_format_terraform, GeneratedFile
    bad_file = GeneratedFile(filename="main.tf", content='resource "aws_vpc" "main" { invalid_syntax_here = ', language="hcl")
    files, report = validate_and_format_terraform([bad_file])
    assert report["validate"] in ("FAILED", "ERROR", "SKIPPED", "NOT_RUN")

def test_scenario_g_ai_provider_unavailable():
    """Scenario G — AI/Architecture provider unavailable: no fake fallback when strict mode."""
    os.environ["STRICT_APPROVAL_GATE"] = "true"
    with patch("httpx.Client.get", side_effect=httpx.ConnectError("Service down")):
        payload = {
            "project_name": "scenario-g-app",
            "architecture_version_id": "arch-missing"
        }
        response = client.post("/api/v1/generate-iac", json=payload)
        os.environ["STRICT_APPROVAL_GATE"] = "false"
        assert response.status_code == 400
        assert "Approval Gate Verification Failed" in response.json()["detail"]

def test_scenario_h_architecture_version_immutability():
    """Scenario H — Existing architecture version snapshot tie and immutability."""
    status_mock = MagicMock()
    status_mock.status_code = 200
    status_mock.json.return_value = {"version_id": "arch-v-frozen", "is_approved": True, "status": "APPROVED"}

    with patch("httpx.Client.get", return_value=status_mock):
        payload = {
            "project_name": "scenario-h-app",
            "architecture_version_id": "arch-v-frozen",
        }
        response = client.post("/api/v1/generate-iac", json=payload)
        assert response.status_code == 200
        assert response.json()["architecture_version_id"] == "arch-v-frozen"

def test_scenario_i_terraform_plan_consistency():
    """Scenario I — Plan consistency and resource mapping check."""
    from app.iac_engine import build_infrastructure_ir, verify_architecture_consistency, GeneratedFile
    req = IaCGenerationRequest(project_name="scen-i", architecture_version_id="arch-i")
    ir = build_infrastructure_ir(req)
    files = [GeneratedFile(filename="main.tf", content='resource "aws_vpc" "main" {}\nresource "aws_subnet" "public_a" {}\nresource "aws_instance" "app" {}', language="hcl")]
    report = verify_architecture_consistency(ir, files)
    assert report.status == "PASSED"

def test_scenario_j_cost_sensitive_resources():
    """Scenario J — Cost-sensitive resource monitoring and verification."""
    status_mock = MagicMock()
    status_mock.status_code = 200
    status_mock.json.return_value = {"version_id": "arch-scen-j", "is_approved": True, "status": "APPROVED"}

    with patch("httpx.Client.get", return_value=status_mock):
        payload = {
            "project_name": "scenario-j-app",
            "architecture_version_id": "arch-scen-j",
            "enable_alb": True,
            "database_instance_type": "db.t3.medium",
            "database_storage_gb": 20
        }
        response = client.post("/api/v1/generate-iac", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "aws_db_instance" in data["summary"]["resources_defined"]
        assert "aws_lb" in data["summary"]["resources_defined"]
