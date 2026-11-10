import pytest
from starlette.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["port"] == 8009

def test_approval_and_execution_flow(client):
    plan_id = "test-plan-999"
    plan_hash = "hash-999-secure"

    # Try execution before approval -> Should be rejected 400
    exec_res = client.post("/api/v1/deployments/execute", json={"plan_id": plan_id})
    assert exec_res.status_code == 400
    assert "Approval Gate Violation" in exec_res.json()["detail"]

    # Approve plan
    appr_res = client.post("/api/v1/deployments/approve", json={
        "plan_id": plan_id,
        "plan_hash": plan_hash,
        "approver": "lead-architect"
    })
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "APPROVED"

    # Now execute -> Should succeed
    exec_res2 = client.post("/api/v1/deployments/execute", json={"plan_id": plan_id})
    assert exec_res2.status_code == 200
    data = exec_res2.json()
    assert data["status"] == "COMPLETED"
    dep_id = data["deployment_id"]

    # Get logs
    log_res = client.get(f"/api/v1/deployments/{dep_id}/logs")
    assert log_res.status_code == 200
    assert len(log_res.json()["logs"]) > 0
