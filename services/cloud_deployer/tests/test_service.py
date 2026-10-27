# services/cloud_deployer/tests/test_service.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["port"] == 8011

def test_deploy_infrastructure_backwards_compatible():
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
    assert data["mode"] == "TEST_SANDBOX"

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

def test_deployment_planning_and_risk_evaluation():
    payload = {
        "project_name": "ecommerce-platform",
        "environment_tier": "production",
        "target_region": "us-east-1",
        "architecture_version_id": "arch-prod-v1",
        "terraform_version_id": "tf-prod-v1"
    }
    response = client.post("/api/v1/deployments/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PLANNED"
    assert data["plan_id"].startswith("pln-2026-")
    assert len(data["plan_digest"]) == 64
    assert len(data["resource_changes"]) >= 8
    assert data["summary"]["create"] >= 8
    assert "risk_assessment" in data
    assert data["risk_assessment"]["status"] in ("PASS", "WARNING", "BLOCKED")
    assert data["can_approve"] is True

def test_unapproved_deployment_execution_blocked():
    # 1. Create plan
    plan_resp = client.post("/api/v1/deployments/plan", json={
        "project_name": "secure-app",
        "environment_tier": "staging",
        "target_region": "us-east-1"
    })
    plan_id = plan_resp.json()["plan_id"]

    # 2. Attempt to execute immediately without approval -> must fail with 400
    exec_resp = client.post("/api/v1/deployments/execute", json={"plan_id": plan_id})
    assert exec_resp.status_code == 400
    assert "Approval Gate Violation" in exec_resp.json()["detail"]

def test_digest_tampering_blocked():
    # 1. Create plan
    plan_resp = client.post("/api/v1/deployments/plan", json={
        "project_name": "vault-app",
        "environment_tier": "development",
        "target_region": "us-west-2"
    })
    plan_id = plan_resp.json()["plan_id"]

    # 2. Attempt approval with invalid digest -> must fail with 400
    tampered_digest = "0000000000000000000000000000000000000000000000000000000000000000"
    appr_resp = client.post("/api/v1/deployments/approve", json={
        "plan_id": plan_id,
        "plan_digest": tampered_digest
    })
    assert appr_resp.status_code == 400
    assert "digest mismatch" in appr_resp.json()["detail"].lower()

def test_complete_deployment_lifecycle():
    # 1. Plan
    plan_res = client.post("/api/v1/deployments/plan", json={
        "project_name": "alpha-service",
        "environment_tier": "production",
        "target_region": "us-east-1"
    })
    assert plan_res.status_code == 200
    p_data = plan_res.json()
    plan_id = p_data["plan_id"]
    plan_digest = p_data["plan_digest"]

    # 2. Approve
    headers = {
        "x-authenticated-user": "lead_architect",
        "x-user-uuid": "usr_998877",
        "x-tenant-id": "ten_alpha"
    }
    appr_res = client.post(
        "/api/v1/deployments/approve",
        json={"plan_id": plan_id, "plan_digest": plan_digest, "comments": "Approved for sprint 42 release"},
        headers=headers
    )
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "APPROVED"
    assert appr_res.json()["approved_by"] == "lead_architect"

    # 3. Execute
    exec_res = client.post("/api/v1/deployments/execute", json={"plan_id": plan_id}, headers=headers)
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    dep_id = exec_data["deployment_id"]
    assert exec_data["status"] == "SUCCESS"
    assert exec_data["state_lock_acquired"] is True
    assert exec_data["mode"] == "TEST_SANDBOX"

    # 4. Fetch Logs
    logs_res = client.get(f"/api/v1/deployments/{dep_id}/logs")
    assert logs_res.status_code == 200
    logs_data = logs_res.json()
    assert len(logs_data["logs"]) >= 5
    assert any("Acquired distributed" in l for l in logs_data["logs"])
    assert any("Apply complete" in l for l in logs_data["logs"])

    # 5. Fetch Resources
    res_res = client.get(f"/api/v1/deployments/{dep_id}/resources")
    assert res_res.status_code == 200
    assert res_res.json()["count"] >= 5

    # 6. List Deployments
    list_res = client.get("/api/v1/deployments?project_id=alpha-service")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1


def test_dynamic_terraform_files_parsing_in_plan():
    """Verify that custom generated Terraform files are parsed into exact resource changes."""
    custom_hcl = """
resource "aws_vpc" "custom_net" {
  cidr_block = "172.16.0.0/16"
}

resource "aws_subnet" "custom_sub" {
  cidr_block = "172.16.1.0/24"
}

resource "aws_instance" "worker" {
  instance_type = "c6i.xlarge"
}
"""
    payload = {
        "project_name": "custom-hcl-app",
        "environment_tier": "development",
        "target_region": "us-west-2",
        "terraform_files": [
            {"filename": "main.tf", "content": custom_hcl}
        ]
    }
    response = client.post("/api/v1/deployments/plan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["resource_changes"]) == 3
    rtypes = [r["resource_type"] for r in data["resource_changes"]]
    assert "aws_vpc" in rtypes
    assert "aws_subnet" in rtypes
    assert "aws_instance" in rtypes
    assert data["summary"]["create"] == 3


def test_honest_aws_account_id_and_sandbox_verification_status():
    """Verify that execution stamps real AWS account ID or unverified-sandbox, without hardcoded fakes."""
    # 1. Plan with explicit AWS account ID
    plan_resp = client.post("/api/v1/deployments/plan", json={
        "project_name": "real-acc-proj",
        "environment_tier": "development",
        "target_region": "eu-central-1",
        "aws_account_id": "987654321098"
    })
    assert plan_resp.status_code == 200
    p = plan_resp.json()

    # 2. Approve
    appr_resp = client.post("/api/v1/deployments/approve", json={
        "plan_id": p["plan_id"],
        "plan_digest": p["plan_digest"]
    })
    assert appr_resp.status_code == 200

    # 3. Execute
    exec_resp = client.post("/api/v1/deployments/execute", json={"plan_id": p["plan_id"]})
    assert exec_resp.status_code == 200
    dep_id = exec_resp.json()["deployment_id"]

    # 4. Resources
    res_resp = client.get(f"/api/v1/deployments/{dep_id}/resources")
    assert res_resp.status_code == 200
    resources = res_resp.json()["resources"]
    assert len(resources) > 0
    # Every resource should have the target account in ARN and explicit sandbox verification status
    for r in resources:
        assert "987654321098" in r["arn"]
        assert r["verification_status"] == "UNVERIFIED_LOCAL_SANDBOX"
        assert r["is_verified_aws"] is False
