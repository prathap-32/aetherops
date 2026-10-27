# services/architecture_generator/tests/test_generator.py
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.generator import generate_architecture_graph
from app.schemas import RequirementProfileOutput

client = TestClient(app)

# Sample valid profile data for testing
sample_profile_payload = {
    "architecture_tier": "Production-Standard",
    "high_availability_mode": "multi-az",
    "compliance_applied": ["HIPAA"],
    "monthly_budget_limit": 2000.0,
    "total_estimated_cost": 420.50,
    "cost_exceeds_budget": False,
    "components": {
        "compute": {
            "instance_type": "m6i.large",
            "vcpus": 2,
            "ram_gb": 8.0,
            "min_instances": 2,
            "max_instances": 6,
            "target_cpu_utilization": 70,
            "has_autoscaling": True,
            "monthly_cost": 140.16
        },
        "database": {
            "instance_type": "db.m6g.large",
            "vcpus": 2,
            "ram_gb": 8.0,
            "storage_gb": 150,
            "storage_type": "gp3",
            "multi_az": True,
            "replica_count": 0,
            "backup_retention_days": 7,
            "monthly_cost": 210.00
        },
        "networking": {
            "has_alb": True,
            "nat_gateway_count": 1,
            "has_cloudfront": True,
            "monthly_cost": 50.00
        },
        "storage": {
            "s3_gb": 200,
            "s3_class": "STANDARD",
            "ebs_gb_per_instance": 50,
            "monthly_cost": 20.34
        },
        "security": {
            "encryption_enabled": True,
            "iam_audit_required": True,
            "waf_enabled": True,
            "kms_key_rotation": True
        },
        "operations": {
            "orchestration_tool": "docker_compose",
            "iac_tool": "terraform",
            "config_tool": "none",
            "ci_cd_tool": "github_actions",
            "files_to_generate": ["docker-compose.yml", "main.tf"]
        },
        "monitoring": {
            "level": "basic",
            "alerting_channel": "email",
            "tools_to_deploy": ["CloudWatch"]
        }
    },
    "educational_notes": ["Mock note"],
    "remediation_steps": ["Mock step"]
}

def test_generate_architecture_graph():
    profile = RequirementProfileOutput(**sample_profile_payload)
    graph = generate_architecture_graph(profile)
    
    node_ids = [node.id for node in graph.nodes]
    assert "internet" in node_ids
    assert "cloudfront" in node_ids
    assert "vpc-1" in node_ids
    assert "subnet-public-a" in node_ids
    assert "subnet-private-a" in node_ids
    assert "ec2-a" in node_ids
    assert "rds-master" in node_ids
    assert "ec2-b" in node_ids
    assert "rds-replica" in node_ids

    # Check edges
    edge_ids = [edge.id for edge in graph.edges]
    assert "edge-internet-cf" in edge_ids
    assert "edge-db-replication" in edge_ids

def test_api_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_generate_graph():
    response = client.post("/api/v1/generate-graph", json=sample_profile_payload)
    assert response.status_code == 200
    
    graph_data = response.json()
    assert "nodes" in graph_data
    assert "edges" in graph_data
    node_ids = [node["id"] for node in graph_data["nodes"]]
    assert "vpc-1" in node_ids
    assert "rds-master" in node_ids


def test_ai_architecture_analysis_stage_a():
    """Verify Stage A AI Architecture Analysis identifies completeness and security posture."""
    valid_payload = {
        "environment_tier": "production",
        "target_region": "us-east-1",
        "nodes": [
            {"id": "node-client", "data": {"label": "Client Ingress", "resource_type": "internet"}},
            {"id": "node-alb", "data": {"label": "ALB", "resource_type": "alb"}},
            {"id": "node-compute", "data": {"label": "EC2 ASG", "resource_type": "ec2"}},
            {"id": "node-db", "data": {"label": "RDS Postgres", "resource_type": "rds", "details": {"multi_az": True}}},
        ],
        "edges": [
            {"id": "e1", "source": "node-client", "target": "node-alb"},
            {"id": "e2", "source": "node-alb", "target": "node-compute"},
            {"id": "e3", "source": "node-compute", "target": "node-db"},
        ]
    }
    response = client.post("/api/v1/architecture/analyze", json=valid_payload)
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert "overall_score" in data
    assert "findings" in data
    assert data["has_blocking_findings"] is False


def test_deterministic_validation_stage_b_blocking_policy():
    """Verify Stage B deterministic validation blocks direct internet-to-database connections."""
    insecure_payload = {
        "environment_tier": "production",
        "nodes": [
            {"id": "node-client", "data": {"label": "Client Ingress", "resource_type": "internet"}},
            {"id": "node-db", "data": {"label": "RDS Postgres", "resource_type": "rds"}},
        ],
        "edges": [
            {"id": "e-bad", "source": "node-client", "target": "node-db"},
        ]
    }
    response = client.post("/api/v1/architecture/validate", json=insecure_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "BLOCKED"
    assert data["can_approve"] is False
    assert any("Security Policy Violation" in err for err in data["blocking_errors"])


def test_architecture_version_save_and_approval_gate_stage_c():
    """Verify Stage C version save, approval recording, and approval gating."""
    save_payload = {
        "project_id": "proj-test-1",
        "environment_id": "env-prod-1",
        "version_id": "arch-v1.0.0-test",
        "environment_tier": "production",
        "nodes": [
            {"id": "node-client", "data": {"label": "Client", "resource_type": "internet"}},
            {"id": "node-alb", "data": {"label": "ALB", "resource_type": "alb"}},
            {"id": "node-compute", "data": {"label": "EC2", "resource_type": "ec2"}},
            {"id": "node-db", "data": {"label": "RDS", "resource_type": "rds", "details": {"multi_az": True}}},
        ],
        "edges": [
            {"id": "e1", "source": "node-client", "target": "node-alb"},
            {"id": "e2", "source": "node-alb", "target": "node-compute"},
            {"id": "e3", "source": "node-compute", "target": "node-db"},
        ]
    }
    save_resp = client.post("/api/v1/architecture/studio/save", json=save_payload)
    assert save_resp.status_code == 200
    assert save_resp.json()["is_approved"] is False

    # Check status before approval
    status_resp = client.get("/api/v1/architecture/versions/arch-v1.0.0-test/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["can_generate_terraform"] is False

    # Review bundle
    review_resp = client.get("/api/v1/architecture/review/arch-v1.0.0-test")
    assert review_resp.status_code == 200
    review_data = review_resp.json()
    assert review_data["can_approve"] is True
    assert len(review_data["resource_inventory"]) == 4

    # Explicit Approve
    appr_resp = client.post(
        "/api/v1/architecture/approve",
        json={"version_id": "arch-v1.0.0-test", "project_id": "proj-test-1", "environment_id": "env-prod-1"},
        headers={"x-authenticated-user": "alice", "x-user-uuid": "uuid-alice"}
    )
    assert appr_resp.status_code == 200
    appr_data = appr_resp.json()
    assert appr_data["status"] == "APPROVED"
    assert "approval_id" in appr_data

    # Check status after approval
    status_resp2 = client.get("/api/v1/architecture/versions/arch-v1.0.0-test/status")
    assert status_resp2.status_code == 200
    assert status_resp2.json()["can_generate_terraform"] is True
    assert status_resp2.json()["is_approved"] is True

    # Modifying architecture invalidates approval
    save_resp2 = client.post("/api/v1/architecture/studio/save", json={**save_payload, "version_id": "arch-v1.0.1-test"})
    assert save_resp2.status_code == 200
    assert save_resp2.json()["is_approved"] is False
