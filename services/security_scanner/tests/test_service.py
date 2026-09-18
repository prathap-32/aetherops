# services/security_scanner/tests/test_service.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["port"] == 8005

def test_security_scan_pass():
    payload = {
        "project_name": "secure-banking-api",
        "target_frameworks": ["CIS-AWS-1.5", "PCI-DSS"],
        "open_ingress_ports": [443],
        "kms_encryption_enabled": True,
        "waf_enabled": True,
        "iam_wildcard_permissions": False,
        "public_s3_buckets": False
    }
    response = client.post("/api/v1/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["security_posture_score"] == 100
    assert data["failed_count"] == 0
    assert data["compliance_status"]["CIS-AWS-1.5"] == "COMPLIANT"

def test_security_scan_violations():
    payload = {
        "project_name": "vulnerable-app",
        "target_frameworks": ["CIS-AWS-1.5"],
        "open_ingress_ports": [22, 5432],
        "kms_encryption_enabled": False,
        "waf_enabled": False,
        "iam_wildcard_permissions": True,
        "public_s3_buckets": True
    }
    response = client.post("/api/v1/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["security_posture_score"] < 50
    assert data["failed_count"] >= 4
    assert data["compliance_status"]["CIS-AWS-1.5"] == "NON_COMPLIANT"
