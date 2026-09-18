# services/finops_optimizer/tests/test_service.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["port"] == 8004

def test_optimize_costs():
    payload = {
        "project_name": "prod-ecommerce",
        "monthly_on_demand_compute": 150.0,
        "monthly_on_demand_rds": 120.0,
        "monthly_storage_and_network": 45.0,
        "current_instance_family": "m5",
        "is_development": False
    }
    response = client.post("/api/v1/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["baseline_monthly_spend"] == 315.0
    assert data["total_monthly_savings"] > 0
    assert len(data["savings_opportunities"]) >= 2
    assert data["tco_projection"]["net_1_year_savings"] > 0
