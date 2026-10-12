# services/cicd_pipeline/tests/test_service.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["port"] == 8009

def test_generate_github_actions_pipeline():
    payload = {
        "project_name": "ecommerce-frontend",
        "platform": "github_actions",
        "iac_tool": "terraform",
        "enable_security_scan": True,
        "enable_cost_budget_gate": True,
        "auto_apply_on_main": False,
        "target_branch": "main"
    }
    response = client.post("/api/v1/generate-pipeline", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["platform"] == "github_actions"
    assert len(data["files"]) >= 1
    assert ".github/workflows/aether-deploy.yml" in data["files"][0]["filepath"]
    assert "trivy-action" in data["files"][0]["content"]

def test_generate_gitlab_pipeline():
    payload = {
        "project_name": "ai-model-serving",
        "platform": "gitlab_ci",
        "iac_tool": "terraform",
        "enable_security_scan": True,
        "enable_cost_budget_gate": False,
        "auto_apply_on_main": True,
        "target_branch": "main"
    }
    response = client.post("/api/v1/generate-pipeline", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["platform"] == "gitlab_ci"
    assert ".gitlab-ci.yml" in data["files"][0]["filepath"]
