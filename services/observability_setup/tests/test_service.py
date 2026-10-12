# services/observability_setup/tests/test_service.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["port"] == 8010

def test_generate_observability():
    payload = {
        "project_name": "payments-gateway",
        "environment": "production",
        "alert_channel": "slack_webhook",
        "enable_otel": True,
        "enable_cloudwatch_alarms": True,
        "target_cpu_alarm_threshold": 75,
        "target_error_rate_threshold": 2.0
    }
    response = client.post("/api/v1/generate-observability", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert len(data["artifacts"]) >= 3
    filenames = [a["filename"] for a in data["artifacts"]]
    assert "cloudwatch-alarms.tf" in filenames
    assert "otel-collector-config.yaml" in filenames
    assert "grafana-dashboard.json" in filenames
