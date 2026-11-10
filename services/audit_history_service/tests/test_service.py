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
    assert data["port"] == 8012

def test_record_and_list_audit_events(client):
    payload = {
        "event_type": "PROJECT_CREATED",
        "module_key": "MOD-PM",
        "project_id": "proj-alpha",
        "actor": "admin",
        "details": {"name": "Alpha Project", "region": "us-east-1"}
    }
    create_res = client.post("/api/v1/audit/record", json=payload)
    assert create_res.status_code == 201
    evt = create_res.json()
    assert evt["event_type"] == "PROJECT_CREATED"
    assert evt["project_id"] == "proj-alpha"

    # Query events
    list_res = client.get("/api/v1/audit/events?project_id=proj-alpha")
    assert list_res.status_code == 200
    events = list_res.json()["events"]
    assert len(events) >= 1
    assert any(e["event_type"] == "PROJECT_CREATED" for e in events)
