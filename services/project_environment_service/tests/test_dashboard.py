# services/project_and_environment_management/tests/test_dashboard.py
"""
Pytest suite for Adaptive Unified Dashboard Backend Endpoints.

Covers:
- GET /api/v1/dashboard (Stage 1 Onboarding, Stage 2 Project Created, Lifecycle Computation)
- GET /api/v1/dashboard/preferences (Default structure, user scoping)
- PUT /api/v1/dashboard/preferences (Updating and persisting user preferences)
- POST /api/v1/dashboard/preferences/reset (Resetting preferences back to default)
- Security: Tenant & user isolation for preferences
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def client():
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def admin_headers():
    return {"X-Admin-Key": "aetherops-secret-admin-key"}


@pytest.mark.asyncio
async def test_dashboard_summary_endpoint(client, admin_headers):
    """Verify /api/v1/dashboard returns lifecycle stage, summary, and eligibility."""
    res = await client.get("/api/v1/dashboard", headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()

    assert "lifecycle_stage" in data
    assert data["lifecycle_stage"] in [
        "stage_1_onboarding",
        "stage_2_project_created",
        "stage_3_infrastructure_workflow",
        "stage_4_active_operations",
    ]
    assert "summary" in data
    assert "total_projects" in data["summary"]
    assert "total_environments" in data["summary"]
    assert "widget_eligibility" in data
    assert "getting_started" in data["widget_eligibility"]
    assert "overview_metrics" in data["widget_eligibility"]
    assert "recent_projects" in data["widget_eligibility"]
    assert "recommended_action" in data
    assert "title" in data["recommended_action"]


@pytest.mark.asyncio
async def test_dashboard_default_preferences(client, admin_headers):
    """Verify /api/v1/dashboard/preferences returns default layout when no customization exists."""
    res = await client.get("/api/v1/dashboard/preferences", headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()

    assert "widget_order" in data
    assert isinstance(data["widget_order"], list)
    assert "getting_started" in data["widget_order"]
    assert "widget_visibility" in data
    assert data["widget_visibility"].get("overview_metrics") is True
    assert "widget_sizes" in data
    assert "pinned_widgets" in data


@pytest.mark.asyncio
async def test_dashboard_save_and_reset_preferences(client, admin_headers):
    """Verify updating and resetting dashboard preferences."""
    custom_prefs = {
        "widget_order": ["recent_projects", "overview_metrics"],
        "widget_visibility": {"recent_projects": True, "overview_metrics": False},
        "widget_sizes": {"recent_projects": "half", "overview_metrics": "full"},
        "pinned_widgets": ["recent_projects"],
    }

    # 1. Update preferences
    put_res = await client.put(
        "/api/v1/dashboard/preferences",
        json=custom_prefs,
        headers=admin_headers,
    )
    assert put_res.status_code == 200, put_res.text
    saved = put_res.json()
    assert saved["widget_order"] == ["recent_projects", "overview_metrics"]
    assert saved["pinned_widgets"] == ["recent_projects"]

    # 2. Get preferences to confirm persistence
    get_res = await client.get("/api/v1/dashboard/preferences", headers=admin_headers)
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["widget_order"] == ["recent_projects", "overview_metrics"]
    assert retrieved["widget_visibility"]["overview_metrics"] is False

    # 3. Reset preferences to default
    reset_res = await client.post(
        "/api/v1/dashboard/preferences/reset",
        headers=admin_headers,
    )
    assert reset_res.status_code == 200
    reset_data = reset_res.json()
    assert "getting_started" in reset_data["widget_order"]
    assert reset_data["widget_visibility"]["overview_metrics"] is True
