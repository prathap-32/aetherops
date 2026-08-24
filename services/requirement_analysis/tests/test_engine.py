# services/requirement_analysis/tests/test_engine.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.engine import calculate_compute_needs, analyze_requirements
from app.schemas import RequirementInput
from app.database import Base, engine, AsyncSessionLocal
from app.seed import init_db, seed_catalog

client = TestClient(app)

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="module")
async def db_session():
    # Setup database schema and seed data
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        await seed_catalog(session)
        
    async with AsyncSessionLocal() as session:
        yield session

def test_calculate_compute_needs():
    vcpus, ram = calculate_compute_needs(rps=150, peak_multiplier=2.0, workload_type="api")
    assert vcpus == 2
    assert ram == 4.0

    vcpus, ram = calculate_compute_needs(rps=10, peak_multiplier=1.5, workload_type="batch")
    assert vcpus == 2
    assert ram == 8.0

@pytest.mark.anyio
async def test_analyze_requirements_developer(db_session):
    inputs = RequirementInput(
        project_name="dev-proj",
        stream="web_application",
        technology={
            "frontend": "react_vue_angular",
            "backend": "python_fastapi_django",
            "database": "postgresql"
        },
        operations={
            "container_orchestration": "docker_compose",
            "infrastructure_as_code": "terraform"
        },
        monitoring={
            "level": "basic",
            "alerting_channel": "email"
        },
        traffic_scale="hobby_dev",
        reliability="dev_testing",
        data_storage_gb=10.0,
        security_need="standard",
        monthly_budget=100.0
    )
    result = await analyze_requirements(inputs, db_session)
    
    assert result.architecture_tier == "Developer"
    assert result.high_availability_mode == "none"
    assert result.components.compute.min_instances == 1
    assert result.components.networking.has_alb is False
    assert result.components.networking.nat_gateway_count == 0
    assert result.components.database.multi_az is False
    assert result.components.security.encryption_enabled is False
    assert result.components.operations.orchestration_tool == "docker_compose"
    assert "docker-compose.yml" in result.components.operations.files_to_generate

@pytest.mark.anyio
async def test_analyze_requirements_production(db_session):
    inputs = RequirementInput(
        project_name="prod-proj",
        stream="web_application",
        technology={
            "frontend": "react_vue_angular",
            "backend": "python_fastapi_django",
            "database": "postgresql"
        },
        operations={
            "container_orchestration": "kubernetes",
            "infrastructure_as_code": "terraform",
            "ci_cd_pipeline": "github_actions"
        },
        monitoring={
            "level": "advanced",
            "alerting_channel": "slack_webhook"
        },
        traffic_scale="growth",
        reliability="production_safe",
        data_storage_gb=100.0,
        security_need="healthcare",
        monthly_budget=2000.0
    )
    result = await analyze_requirements(inputs, db_session)
    
    assert result.architecture_tier == "Production-Standard"
    assert result.high_availability_mode == "multi-az"
    assert result.components.compute.min_instances == 2
    assert result.components.networking.has_alb is True
    assert result.components.networking.nat_gateway_count == 1
    assert result.components.database.multi_az is True
    assert result.components.security.encryption_enabled is True
    assert "HIPAA" in result.compliance_applied
    assert "deployment.yaml" in result.components.operations.files_to_generate
    assert "Prometheus Server" in result.components.monitoring.tools_to_deploy

@pytest.mark.anyio
async def test_analyze_requirements_enterprise_ai(db_session):
    inputs = RequirementInput(
        project_name="ai-enterprise",
        stream="ai_ml",
        technology={
            "frontend": "react_vue_angular",
            "backend": "python_fastapi_django",
            "database": "postgresql"
        },
        operations={
            "container_orchestration": "kubernetes",
            "infrastructure_as_code": "terraform"
        },
        monitoring={
            "level": "advanced",
            "alerting_channel": "slack_webhook"
        },
        traffic_scale="production",
        reliability="mission_critical",
        data_storage_gb=500.0,
        security_need="payment_processing",
        monthly_budget=10000.0
    )
    result = await analyze_requirements(inputs, db_session)
    
    assert result.architecture_tier == "Enterprise-HA"
    assert result.high_availability_mode == "multi-region"
    assert result.components.compute.min_instances == 4
    assert result.components.compute.instance_type == "g4dn.xlarge"  # GPU-accelerated selection
    assert result.components.networking.has_alb is True
    assert result.components.networking.nat_gateway_count == 2
    assert result.components.database.multi_az is True
    assert result.components.database.replica_count == 1
    assert result.components.security.waf_enabled is True
    assert result.components.security.encryption_enabled is True

def test_api_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_analyze():
    payload = {
        "project_name": "api-test",
        "stream": "web_application",
        "technology": {
            "frontend": "react_vue_angular",
            "backend": "python_fastapi_django",
            "database": "postgresql"
        },
        "operations": {
            "container_orchestration": "docker_compose",
            "infrastructure_as_code": "terraform"
        },
        "monitoring": {
            "level": "basic",
            "alerting_channel": "email"
        },
        "traffic_scale": "growth",
        "reliability": "production_safe",
        "data_storage_gb": 30.0,
        "security_need": "healthcare",
        "monthly_budget": 500.0
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["architecture_tier"] == "Production-Standard"
    assert data["components"]["compute"]["min_instances"] >= 1
    assert data["components"]["database"]["storage_gb"] >= 30
    assert "HIPAA" in data["compliance_applied"]
    assert "docker-compose.yml" in data["components"]["operations"]["files_to_generate"]

def test_admin_dashboard_response():
    response = client.get("/admin")
    assert response.status_code == 200
    assert "AetherOps Cloud - Admin Catalog Dashboard" in response.text

def test_admin_get_catalog():
    response = client.get("/api/admin/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "ec2" in data
    assert "rds" in data
    assert "cache_connected" in data

def test_admin_sync():
    from unittest.mock import AsyncMock, patch
    mock_result = {
        "status": "success",
        "added_ec2": 10,
        "updated_ec2": 0,
        "added_rds": 5,
        "updated_rds": 0,
        "cache_cleared": True
    }
    with patch("app.admin_router.sync_catalog_from_aws", new_callable=AsyncMock, return_value=mock_result):
        response = client.post("/api/admin/sync")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "added_ec2" in data
        assert "updated_ec2" in data
        assert "added_rds" in data

def test_admin_clear_cache():
    response = client.post("/api/admin/clear-cache")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_admin_crud_ec2():
    # 1. Create/Update instance
    payload = {
        "instance_type": "c6i.testlarge",
        "vcpus": 2,
        "ram_gb": 4.0,
        "price_per_hour": 0.085,
        "network_performance": "10 Gbps",
        "category": "compute_optimized"
    }
    response = client.post("/api/admin/catalog/ec2", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify presence in catalog
    res_cat = client.get("/api/admin/catalog")
    ec2_types = [item["instance_type"] for item in res_cat.json()["ec2"]]
    assert "c6i.testlarge" in ec2_types

    # 2. Delete instance
    response = client.delete("/api/admin/catalog/ec2/c6i.testlarge")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify removal
    res_cat2 = client.get("/api/admin/catalog")
    ec2_types2 = [item["instance_type"] for item in res_cat2.json()["ec2"]]
    assert "c6i.testlarge" not in ec2_types2

def test_admin_dynamic_ec2_lookup():
    """Test dynamic EC2 add — only instance_type provided, specs resolved from API."""
    from unittest.mock import AsyncMock, patch
    mock_specs = {
        "instance_type": "m5.xlarge",
        "vcpus": 4,
        "ram_gb": 16.0,
        "price_per_hour": 0.192,
        "network_performance": "Up to 10 Gbps",
        "category": "general"
    }
    with patch("app.admin_router.lookup_ec2_instance", new_callable=AsyncMock, return_value=mock_specs):
        # Send only instance_type — no manual overrides
        response = client.post("/api/admin/catalog/ec2", json={"instance_type": "m5.xlarge"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["source"] == "ec2.shop"
        assert data["specs"]["vcpus"] == 4
        assert data["specs"]["ram_gb"] == 16.0

    # Verify in catalog
    res_cat = client.get("/api/admin/catalog")
    ec2_types = [item["instance_type"] for item in res_cat.json()["ec2"]]
    assert "m5.xlarge" in ec2_types

    # Cleanup
    client.delete("/api/admin/catalog/ec2/m5.xlarge")

def test_admin_dynamic_rds_lookup():
    """Test dynamic RDS add — only instance_type provided, specs resolved from API."""
    from unittest.mock import AsyncMock, patch
    mock_specs = {
        "instance_type": "db.r6g.large",
        "vcpus": 2,
        "ram_gb": 16.0,
        "price_per_hour": 0.24,
        "category": "memory"
    }
    with patch("app.admin_router.lookup_rds_instance", new_callable=AsyncMock, return_value=mock_specs):
        response = client.post("/api/admin/catalog/rds", json={"instance_type": "db.r6g.large"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["source"] == "aws_pricing_api"
        assert data["specs"]["vcpus"] == 2

    # Cleanup
    client.delete("/api/admin/catalog/rds/db.r6g.large")

def test_admin_invalid_service():
    """Test that an invalid service name returns 400."""
    response = client.post("/api/admin/catalog/sqs", json={"instance_type": "queue.large"})
    assert response.status_code == 400
    assert "Invalid service" in response.json()["detail"]

    response = client.delete("/api/admin/catalog/lambda/some.type")
    assert response.status_code == 400
    assert "Invalid service" in response.json()["detail"]

def test_admin_dynamic_lookup_endpoint():
    """Test dynamic live lookup endpoint with region and AZ parameters."""
    from unittest.mock import AsyncMock, patch
    mock_specs = {
        "instance_type": "c6i.xlarge",
        "vcpus": 4,
        "ram_gb": 8.0,
        "price_per_hour": 0.17,
        "network_performance": "12.5 Gbps",
        "category": "compute"
    }
    with patch("app.admin_router.lookup_ec2_instance", new_callable=AsyncMock, return_value=mock_specs) as mock_lookup:
        response = client.get(
            "/api/admin/catalog/lookup/ec2",
            params={"instance_type": "c6i.xlarge", "region": "us-west-2", "az": "us-west-2a"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["service"] == "ec2"
        assert data["region"] == "us-west-2"
        assert data["az"] == "us-west-2a"
        assert data["specs"]["instance_type"] == "c6i.xlarge"
        mock_lookup.assert_called_once_with("c6i.xlarge", region="us-west-2", az="us-west-2a")

def test_admin_categorized_catalog():
    """Test retrieving catalog grouped by category."""
    response = client.get("/api/admin/catalog/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "categories" in data
    
    # Check category grouping structure
    categories = data["categories"]
    assert any(cat in categories for cat in ["burstable", "general", "standard"])

    # Test filtering by a specific category
    response_filtered = client.get("/api/admin/catalog/categories", params={"category": "burstable"})
    assert response_filtered.status_code == 200
    filtered_data = response_filtered.json()
    assert filtered_data["category_filter"] == "burstable"
    for cat in filtered_data["categories"]:
        assert cat.lower() == "burstable"

def test_admin_categorized_catalog_fallback():
    """Test retrieving categorized catalog fallback when database is empty."""
    from unittest.mock import AsyncMock, MagicMock
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    
    from app.admin_router import get_categorized_catalog
    import asyncio
    
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(get_categorized_catalog(db=mock_db))
    
    assert result["status"] == "success"
    assert "categories" in result
    categories = result["categories"]
    # Check that static catalog falls back successfully
    assert "burstable" in categories
    assert len(categories["burstable"]["ec2"]) > 0

def test_admin_crud_generic():
    # 1. Create/Update a generic service (e.g., S3 storage profile)
    payload = {
        "instance_type": "Standard Storage",
        "price_per_hour": 0.023,
        "unit": "GB-Month",
        "category": "storage",
        "region": "us-east-1",
        "details": "Custom standard storage pricing"
    }
    response = client.post("/api/admin/catalog/s3", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify presence in catalog
    res_cat = client.get("/api/admin/catalog")
    s3_types = [item["instance_type"] for item in res_cat.json()["s3"]]
    assert "Standard Storage" in s3_types

    # 2. Delete the service
    response = client.delete("/api/admin/catalog/s3/Standard Storage")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify removal
    res_cat2 = client.get("/api/admin/catalog")
    s3_types2 = [item["instance_type"] for item in res_cat2.json().get("s3", [])]
    assert "Standard Storage" not in s3_types2

def test_admin_dynamic_generic_lookup():
    """Test dynamic lookups for a generic service via the lookup endpoint."""
    from unittest.mock import AsyncMock, patch
    mock_specs = {
        "instance_type": "NAT Gateway",
        "price_per_hour": 0.045,
        "unit": "Hrs",
        "category": "networking",
        "region": "us-west-2",
        "details": "Mocked NAT Gateway specs"
    }
    with patch("app.admin_router.lookup_generic_aws_service", new_callable=AsyncMock, return_value=mock_specs) as mock_lookup:
        response = client.get(
            "/api/admin/catalog/lookup/vpc",
            params={"instance_type": "NAT Gateway", "region": "us-west-2"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["service"] == "vpc"
        assert data["region"] == "us-west-2"
        assert data["specs"]["instance_type"] == "NAT Gateway"
        assert data["specs"]["price_per_hour"] == 0.045
        mock_lookup.assert_called_once_with("vpc", "NAT Gateway", region="us-west-2")

@pytest.mark.anyio
async def test_sync_catalog_from_aws_integration(db_session):
    from unittest.mock import AsyncMock, patch
    from app.sync_helper import sync_catalog_from_aws
    from app.models import EC2Catalog, RDSCatalog, GenericServiceCatalog
    from sqlalchemy import select

    mock_ec2 = [
        {"InstanceType": "t3.micro", "Memory": "1 GiB", "VCPUS": "2", "Cost": "0.0104", "Network": "Up to 5 Gbps"}
    ]
    mock_rds = {
        "products": {
            "sku123": {
                "productFamily": "Database Instance",
                "attributes": {
                    "deploymentOption": "Single-AZ",
                    "databaseEngine": "PostgreSQL",
                    "instanceType": "db.t3.micro",
                    "vcpu": "2",
                    "memory": "1 GiB"
                }
            }
        },
        "terms": {
            "OnDemand": {
                "sku123": {
                    "sku123.term1": {
                        "priceDimensions": {
                            "sku123.term1.rate": {
                                "unit": "Hrs",
                                "pricePerUnit": {"USD": "0.018"}
                            }
                        }
                    }
                }
            }
        }
    }

    # Mock the external httpx calls
    async def mock_get(url, *args, **kwargs):
        class MockResponse:
            def __init__(self, json_data):
                self.json_data = json_data
            def raise_for_status(self):
                pass
            def json(self):
                return self.json_data
        if "ec2.shop" in url:
            return MockResponse(mock_ec2)
        elif "AmazonRDS" in url:
            return MockResponse(mock_rds)
        # return fallback index for AWS offer queries (e.g. S3, VPC)
        return MockResponse({"products": {}, "terms": {}})

    with patch("httpx.AsyncClient.get", side_effect=mock_get):
        result = await sync_catalog_from_aws(db_session)
        assert result["status"] == "success"
        assert result["added_ec2"] == 1
        assert result["added_rds"] == 1
        assert result["added_generic"] > 10

        # Verify they are in db
        ec2_res = await db_session.execute(select(EC2Catalog))
        assert len(ec2_res.scalars().all()) == 1

        rds_res = await db_session.execute(select(RDSCatalog))
        assert len(rds_res.scalars().all()) == 1

        generic_res = await db_session.execute(select(GenericServiceCatalog))
        assert len(generic_res.scalars().all()) > 10




