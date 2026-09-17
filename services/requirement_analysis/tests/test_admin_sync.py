# services/requirement_analysis/tests/test_admin_sync.py
"""
Tests for the region-targeted admin sync endpoints.
Uses the same TestClient(app) pattern as the existing test_engine.py.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# --- Test 1: GET /api/admin/catalog/regions returns all configured regions ---
def test_list_all_configured_regions():
    res = client.get("/api/admin/catalog/regions")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 30
    codes = [r["region_code"] for r in data]
    assert "us-east-1" in codes
    assert "ap-south-1" in codes
    assert "eu-west-1" in codes
    sample = data[0]
    for key in ("region_code", "region_name", "geography", "az_count", "db_file", "sync_status", "cached_in_redis"):
        assert key in sample


# --- Test 2: POST /api/admin/catalog/sync/ap-south-1 triggers sync ---
def test_trigger_region_sync_ap_south_1():
    res = client.post("/api/admin/catalog/sync/ap-south-1")
    assert res.status_code == 202
    data = res.json()
    assert data["status"] == "PROCESSING"
    assert data["region"] == "ap-south-1"
    assert "task_id" in data
    assert data["task_id"].startswith("sync_ap-south-1_")


# --- Test 3: GET /api/admin/catalog/status/us-east-1 returns telemetry ---
def test_get_region_sync_status():
    res = client.get("/api/admin/catalog/status/us-east-1")
    assert res.status_code == 200
    data = res.json()
    assert data["region_code"] == "us-east-1"
    assert "status" in data
    assert "records_updated" in data
    assert "duration_ms" in data
    assert "error_message" in data


# --- Test 4: Invalid region returns 400 ---
def test_sync_invalid_region_format():
    res = client.post("/api/admin/catalog/sync/invalid")
    assert res.status_code in (400, 422)


def test_sync_unknown_region():
    res = client.post("/api/admin/catalog/sync/xx-invalid-9")
    assert res.status_code == 400


def test_status_invalid_region():
    res = client.get("/api/admin/catalog/status/invalid")
    assert res.status_code in (400, 422)


# --- Test 5: Sync with explicit JSON body ---
def test_trigger_sync_with_body():
    res = client.post(
        "/api/admin/catalog/sync/us-west-2",
        json={"force_live_fetch": False, "include_generic_services": True},
    )
    assert res.status_code == 202
    data = res.json()
    assert data["region"] == "us-west-2"
    assert data["status"] == "PROCESSING"
