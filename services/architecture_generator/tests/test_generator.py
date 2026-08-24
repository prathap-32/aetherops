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
