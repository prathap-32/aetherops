# services/requirement_analysis/tests/test_requirements_service.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)


def test_requirements_ui_renders():
    """Verify that Module 1 interactive Web Console renders with 200 OK."""
    response = client.get("/app")
    assert response.status_code == 200
    assert "AetherOps Cloud - Module 1: Requirement Analysis & Sizing" in response.text
    assert "Workload Parameters" in response.text
    assert "fintech-payment-engine" in response.text


def test_requirements_analyze_endpoint():
    """Verify that analyzing requirements returns sizing, rationales, and FinOps optimizations."""
    payload = {
        "project_name": "test-analytics-pipeline",
        "stream": "web_application",
        "technology": {
            "frontend": "react_vue_angular",
            "backend": "python_fastapi_django",
            "database": "postgresql"
        },
        "operations": {
            "container_orchestration": "kubernetes",
            "infrastructure_as_code": "terraform",
            "configuration_management": "none",
            "ci_cd_pipeline": "github_actions"
        },
        "monitoring": {
            "level": "advanced",
            "alerting_channel": "slack_webhook"
        },
        "traffic_scale": "growth",
        "reliability": "production_safe",
        "data_storage_gb": 50.0,
        "security_need": "payment_processing",
        "monthly_budget": 500.0
    }
    response = client.post("/api/v1/requirements/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "data" in data
    res = data["data"]
    assert "service_rationales" in res
    assert "cost_optimizations" in res
    assert "cost_breakdown" in res
    assert "ai_advice" in res
    ai_advice = res["ai_advice"]
    assert "scorecard" in ai_advice
    assert "synthesis" in ai_advice
    scorecard = ai_advice["scorecard"]
    assert "security" in scorecard
    assert "reliability" in scorecard
    assert "performance" in scorecard
    assert "cost_optimization" in scorecard
    assert "operational_excellence" in scorecard
    assert "sustainability" in scorecard
    assert 0 <= scorecard["overall_score"] <= 100
    assert "compute" in res["service_rationales"]
    assert "database" in res["service_rationales"]
    assert len(res["cost_optimizations"]) > 0
    assert res["architecture_tier"] == "Production-Standard"



def test_requirements_crud_lifecycle():
    """Verify complete CRUD lifecycle for requirement projects in SQLite requirements.db."""
    payload = {
        "project_name": "test-crud-service",
        "stream": "dev_sandbox",
        "technology": {
            "frontend": "simple_html_css",
            "backend": "nodejs_express",
            "database": "postgresql"
        },
        "operations": {
            "container_orchestration": "docker_compose",
            "infrastructure_as_code": "terraform",
            "configuration_management": "none",
            "ci_cd_pipeline": "github_actions"
        },
        "monitoring": {
            "level": "basic",
            "alerting_channel": "email"
        },
        "traffic_scale": "hobby_dev",
        "reliability": "dev_testing",
        "data_storage_gb": 10.0,
        "security_need": "standard",
        "monthly_budget": 150.0
    }

    # 1. Create Project
    create_res = client.post("/api/v1/requirements?description=Integration+Test+Project", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["status"] == "CREATED"
    project_id = created_data["project"]["id"]
    assert project_id is not None
    assert created_data["project"]["project_name"] == "test-crud-service"

    # 2. Get Project by ID
    get_res = client.get(f"/api/v1/requirements/{project_id}")
    assert get_res.status_code == 200
    proj_data = get_res.json()["project"]
    assert proj_data["id"] == project_id
    assert proj_data["stream"] == "dev_sandbox"
    assert "service_rationales" in proj_data
    assert "cost_optimizations" in proj_data

    # 3. List Projects
    list_res = client.get("/api/v1/requirements?limit=10")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["status"] == "SUCCESS"
    assert list_data["count"] >= 1
    found = any(p["id"] == project_id for p in list_data["projects"])
    assert found is True

    # 4. Update Project
    payload["monthly_budget"] = 250.0
    payload["traffic_scale"] = "growth"
    update_res = client.put(f"/api/v1/requirements/{project_id}", json=payload)
    assert update_res.status_code == 200
    updated_data = update_res.json()["project"]
    assert updated_data["monthly_budget"] == 250.0
    assert updated_data["traffic_scale"] == "growth"

    # 5. Delete Project
    del_res = client.delete(f"/api/v1/requirements/{project_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "DELETED"

    # 6. Verify 404 on deleted project
    not_found_res = client.get(f"/api/v1/requirements/{project_id}")
    assert not_found_res.status_code == 404


def test_requirements_dispatch_to_module2_mocked():
    """Verify dispatching a project to Module 2 updates state and stores graph summary."""
    payload = {
        "project_name": "test-dispatch-project",
        "stream": "web_application",
        "technology": {
            "frontend": "react_vue_angular",
            "backend": "python_fastapi_django",
            "database": "postgresql"
        },
        "operations": {
            "container_orchestration": "kubernetes",
            "infrastructure_as_code": "terraform",
            "configuration_management": "none",
            "ci_cd_pipeline": "github_actions"
        },
        "monitoring": {
            "level": "basic",
            "alerting_channel": "email"
        },
        "traffic_scale": "growth",
        "reliability": "production_safe",
        "data_storage_gb": 30.0,
        "security_need": "standard",
        "monthly_budget": 300.0
    }

    create_res = client.post("/api/v1/requirements", json=payload)
    project_id = create_res.json()["project"]["id"]

    mock_graph = {
        "nodes": [
            {"id": "node-vpc", "type": "vpc", "data": {"label": "Amazon VPC"}},
            {"id": "node-ec2", "type": "compute", "data": {"label": "EC2 Fleet"}},
            {"id": "node-rds", "type": "database", "data": {"label": "PostgreSQL RDS"}}
        ],
        "edges": [
            {"id": "edge-1", "source": "node-vpc", "target": "node-ec2"},
            {"id": "edge-2", "source": "node-ec2", "target": "node-rds"}
        ]
    }

    from unittest.mock import MagicMock
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_graph

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        dispatch_res = client.post(f"/api/v1/requirements/{project_id}/dispatch")
        assert dispatch_res.status_code == 200
        data = dispatch_res.json()
        assert data["status"] == "DISPATCHED_SUCCESSFULLY"
        assert data["graph_nodes"] == 3
        assert data["graph_edges"] == 2
        assert data["project"]["dispatched_to_m2"] is True
        assert data["project"]["status"] == "DISPATCHED_TO_M2"

    # Cleanup
    client.delete(f"/api/v1/requirements/{project_id}")


def test_natural_language_parser_offline():
    """Verify that offline deterministic semantic parser accurately extracts requirements with $0 cost."""
    from app.ai_advisor import parse_natural_language_requirements

    # Case 1: Healthcare HIPAA scenario
    prompt1 = "We are deploying a healthcare patient portal called care-sync-api using Python FastAPI and PostgreSQL. Requires HIPAA compliance, 50 GB storage, high traffic 250 RPS, under $350/mo."
    res1 = parse_natural_language_requirements(prompt1)
    assert res1.project_name == "care-sync-api"
    assert res1.technology.backend == "python_fastapi_django"
    assert res1.technology.database == "postgresql"
    assert res1.security_need.value == "healthcare"
    assert res1.traffic_scale.value == "production"
    assert res1.data_storage_gb == 50.0
    assert res1.monthly_budget == 350.0

    # Case 2: Fintech PCI-DSS scenario
    prompt2 = "A payment processing engine named fintech-core on Node.js and MySQL, PCI-DSS compliance, mission-critical zero downtime, with Terraform and Slack alerts."
    res2 = parse_natural_language_requirements(prompt2)
    assert res2.project_name == "fintech-core"
    assert res2.technology.backend == "nodejs_express"
    assert res2.technology.database == "mysql"
    assert res2.security_need.value == "payment_processing"
    assert res2.reliability.value == "mission_critical"
    assert res2.monitoring.alerting_channel == "slack_webhook"

    # Case 3: Developer sandbox
    prompt3 = "Lightweight internal dev sandbox for testing prototypes on React and Express, budget under $40."
    res3 = parse_natural_language_requirements(prompt3)
    assert res3.stream.value == "dev_sandbox"
    assert res3.technology.frontend == "react_vue_angular"
    assert res3.technology.backend == "nodejs_express"
    assert res3.monthly_budget == 40.0
    assert res3.traffic_scale.value == "hobby_dev"


def test_ai_parse_prompt_endpoint():
    """Verify POST /api/v1/requirements/parse-prompt returns structured parameters with high confidence."""
    payload = {
        "prompt": "Build an AI model inference pipeline using Python FastAPI and PostgreSQL under $300 budget."
    }
    response = client.post("/api/v1/requirements/parse-prompt", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "engine_used" in data
    assert data["confidence_score"] >= 95.0
    parsed = data["parsed_input"]
    assert parsed["technology"]["backend"] == "python_fastapi_django"
    assert parsed["technology"]["database"] == "postgresql"
    assert parsed["monthly_budget"] == 300.0


def test_ai_analyze_endpoint_and_well_architected_evaluation():
    """Verify POST /api/v1/requirements/ai-analyze generates full architecture, 'Why That Service', and 6-pillar scorecard."""
    payload = {
        "prompt": "Need an enterprise healthcare web application with Python FastAPI, PostgreSQL, HIPAA security, multi-AZ high availability, and 100 GB storage under $500/mo.",
        "target_region": "us-east-1",
        "auto_save": True
    }
    response = client.post("/api/v1/requirements/ai-analyze", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "SUCCESS"
    assert "data" in res
    data = res["data"]
    
    # 1. Architecture Sizing
    assert "profile" in data
    assert "architecture_tier" in data
    assert "total_estimated_cost" in data

    # 2. 'Why That Service' Rationales
    assert "service_rationales" in data
    rationales = data["service_rationales"]
    assert "compute" in rationales
    assert "database" in rationales
    assert "security" in rationales
    assert "why" in rationales["compute"]
    assert "Amazon EC2" in rationales["compute"]["service_name"]

    # 3. FinOps Cost Optimizations
    assert "cost_optimizations" in data
    opts = data["cost_optimizations"]
    assert len(opts) > 0
    assert any("Savings Plan" in o["title"] for o in opts)

    # 4. AWS Well-Architected 6-Pillar Scorecard
    assert "ai_advice" in data
    ai_advice = data["ai_advice"]
    assert "scorecard" in ai_advice
    assert "synthesis" in ai_advice
    scorecard = ai_advice["scorecard"]
    assert 0 <= scorecard["overall_score"] <= 100
    assert scorecard["security"]["status"] in ["OPTIMAL", "ACCEPTABLE", "NEEDS_ATTENTION"]

    # 5. Data Provenance from SQLite & Redis
    assert "data_source" in res
    assert "catalog_us-east-1.db" in res["data_source"]["sqlite_catalog_partition"]
    assert res["data_source"]["redis_cache"] == "aether_redis"

    # 6. Auto-Save Verification
    project_id = res["project_id"]
    assert project_id is not None
    get_proj = client.get(f"/api/v1/requirements/{project_id}")
    assert get_proj.status_code == 200
    assert get_proj.json()["project"]["security_need"] == "healthcare"

    # Cleanup
    client.delete(f"/api/v1/requirements/{project_id}")

