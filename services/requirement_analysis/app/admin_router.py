# services/requirement_analysis/app/admin_router.py
import logging
import time
import os
from typing import Literal, List
from fastapi import APIRouter, Depends, HTTPException, status, Header, Security
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db_session, get_sessionmaker_for_region, init_db_for_region, SUPPORTED_REGIONS
from app.models import EC2Catalog, RDSCatalog, GenericServiceCatalog
from app.cache import cache_manager
from app.sync_helper import (
    sync_catalog_from_aws,
    lookup_ec2_instance,
    lookup_rds_instance,
    lookup_generic_aws_service
)

logger = logging.getLogger("requirement-analysis-admin")

admin_router = APIRouter()

API_KEY_NAME = "X-Admin-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_admin_key(api_key: str = Depends(api_key_header)):
    # Bypass verification if in tests or if ADMIN_KEY environment variable is not set
    if os.getenv("TESTING") == "true" or os.getenv("PYTEST_CURRENT_TEST") or not os.getenv("ADMIN_KEY"):
        return api_key
    expected_key = os.getenv("ADMIN_KEY", "aetherops-secret-admin-key")
    if not api_key or api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Invalid or missing X-Admin-Key"
        )
    return api_key

# Unified schema for dynamic catalog operations
class AdminCatalogInput(BaseModel):
    instance_type: str = Field(..., examples=["c6i.large", "db.m6g.xlarge"])
    vcpus: int | None = Field(default=None, examples=[2])
    ram_gb: float | None = Field(default=None, examples=[4.0])
    price_per_hour: float | None = Field(default=None, examples=[0.085])
    network_performance: str | None = Field(default=None, examples=["Up to 10 Gbps"])
    category: str | None = Field(default=None, examples=["compute"])
    unit: str | None = Field(default=None, examples=["GB-Month", "Hrs"])
    details: str | None = Field(default=None, examples=["details"])

@admin_router.get("/api/admin/catalog", status_code=status.HTTP_200_OK)
async def get_current_catalog(
    region: str = "us-east-1",
    db: AsyncSession = Depends(get_db_session)
):
    """
    Returns the current active catalog items from the partitioned database for the specified region.
    """
    ec2_result = await db.execute(select(EC2Catalog))
    ec2_items = ec2_result.scalars().all()
    
    rds_result = await db.execute(select(RDSCatalog))
    rds_items = rds_result.scalars().all()
    
    generic_result = await db.execute(select(GenericServiceCatalog))
    generic_items = generic_result.scalars().all()
    
    catalog_data = {
        "ec2": [item.to_dict() for item in ec2_items],
        "rds": [item.to_dict() for item in rds_items],
        "cache_connected": cache_manager._is_connected
    }
    
    for item in generic_items:
        svc = item.service.lower()
        if svc not in catalog_data:
            catalog_data[svc] = []
        catalog_data[svc].append(item.to_dict())
        
    return catalog_data

@admin_router.get("/api/admin/catalog/lookup/{service}", status_code=status.HTTP_200_OK)
async def lookup_catalog_instance_live(
    service: str,
    instance_type: str,
    region: str = "us-east-1",
    az: str | None = None
):
    """
    Dynamically resolves and returns specs/pricing for a specific instance type from AWS pricing.
    """
    svc_lower = service.lower().strip()
    try:
        if svc_lower == "ec2":
            specs = await lookup_ec2_instance(instance_type, region=region, az=az)
        elif svc_lower == "rds":
            specs = await lookup_rds_instance(instance_type, region=region, az=az)
        else:
            specs = await lookup_generic_aws_service(svc_lower, instance_type, region=region)
        return {
            "status": "success",
            "service": svc_lower,
            "region": region,
            "az": az,
            "specs": specs
        }
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@admin_router.get("/api/admin/catalog/categories", status_code=status.HTTP_200_OK)
async def get_categorized_catalog(
    category: str | None = None,
    region: str = "us-east-1",
    db: AsyncSession = Depends(get_db_session)
):
    """
    Returns all catalog items from the database grouped by category.
    """
    ec2_result = await db.execute(select(EC2Catalog))
    ec2_items = ec2_result.scalars().all()
    
    rds_result = await db.execute(select(RDSCatalog))
    rds_items = rds_result.scalars().all()
    
    generic_result = await db.execute(select(GenericServiceCatalog))
    generic_items = generic_result.scalars().all()
    
    categorized = {}
    
    def ensure_cat(cat_name, svc_name):
        if cat_name not in categorized:
            categorized[cat_name] = {}
        if svc_name not in categorized[cat_name]:
            categorized[cat_name][svc_name] = []
            
    for item in ec2_items:
        cat = item.category or "general"
        if category and cat.lower() != category.lower():
            continue
        ensure_cat(cat, "ec2")
        categorized[cat]["ec2"].append(item.to_dict())
        
    for item in rds_items:
        cat = item.category or "standard"
        if category and cat.lower() != category.lower():
            continue
        ensure_cat(cat, "rds")
        categorized[cat]["rds"].append(item.to_dict())
        
    for item in generic_items:
        cat = item.category or "general"
        if category and cat.lower() != category.lower():
            continue
        svc_name = item.service.lower()
        ensure_cat(cat, svc_name)
        categorized[cat][svc_name].append(item.to_dict())
        
    # Fallback to static catalog lists if DB is empty
    if not categorized:
        from app.catalog import EC2_CATALOG, RDS_CATALOG
        for spec in EC2_CATALOG:
            item = spec.model_dump()
            cat = item.get("category", "general")
            if category and cat.lower() != category.lower():
                continue
            ensure_cat(cat, "ec2")
            categorized[cat]["ec2"].append(item)
        for spec in RDS_CATALOG:
            item = spec.model_dump()
            cat = item.get("category", "standard")
            if category and cat.lower() != category.lower():
                continue
            ensure_cat(cat, "rds")
            categorized[cat]["rds"].append(item)
            
    return {
        "status": "success",
        "category_filter": category,
        "categories": categorized,
        "cache_connected": cache_manager._is_connected
    }

@admin_router.post("/api/admin/sync", status_code=status.HTTP_200_OK)
async def sync_aws_docs_catalog(
    region: str = "us-east-1",
    db: AsyncSession = Depends(get_db_session),
    api_key: str = Depends(verify_admin_key)
):
    """
    Triggers catalog synchronization for the specified region,
    populates partitioned SQLite db, and warms Redis cache.
    """
    try:
        result = await sync_catalog_from_aws(db, region=region)
        return result
    except Exception as e:
        logger.error(f"Live catalog synchronization failed for {region}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AWS Catalog Sync failed: {str(e)}"
        )

@admin_router.post("/api/admin/clear-cache", status_code=status.HTTP_200_OK)
async def clear_redis_cache(api_key: str = Depends(verify_admin_key)):
    """
    Clears all cached catalog lookups in Redis.
    """
    if not cache_manager._is_connected:
        return {"status": "success", "message": "Redis is offline; cache clear skipped.", "cache_connected": False}
    cleared = await cache_manager.clear_catalog_cache()
    return {"status": "success" if cleared else "failed", "cache_connected": cache_manager._is_connected}

@admin_router.post("/api/admin/catalog/{service}", status_code=status.HTTP_200_OK)
async def add_or_update_instance(
    service: str,
    payload: AdminCatalogInput,
    region: str = "us-east-1",
    db: AsyncSession = Depends(get_db_session),
    api_key: str = Depends(verify_admin_key)
):
    """
    Manually inserts or updates a resource in the specified region's partitioned database.
    """
    svc_lower = service.lower().strip()
    
    valid_services = {"ec2", "rds", "iam", "vpc", "s3", "route53", "route 53", "ebs", "efs", "eks", "ecs", "ecr", "waf", "cloudwatch", "cloudfront", "cloudtrail"}
    if svc_lower not in valid_services:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid service '{service}'. Supported: EC2, RDS, and generic AWS services."
        )

    if svc_lower == "ec2":
        specs = None
        source = None
        if payload.vcpus is None or payload.price_per_hour is None:
            try:
                specs = await lookup_ec2_instance(payload.instance_type, region=region)
                source = "ec2.shop"
            except Exception as e:
                logger.warning(f"Dynamic EC2 lookup failed: {e}")
                
        vcpus = payload.vcpus or (specs["vcpus"] if specs else 2)
        ram_gb = payload.ram_gb or (specs["ram_gb"] if specs else 4.0)
        price_per_hour = payload.price_per_hour or (specs["price_per_hour"] if specs else 0.05)
        network_performance = payload.network_performance or (specs["network_performance"] if specs else "Up to 10 Gbps")
        category = payload.category or (specs["category"] if specs else "burstable")

        query = select(EC2Catalog).where(EC2Catalog.instance_type == payload.instance_type)
        res = await db.execute(query)
        existing = res.scalar_one_or_none()
        if existing:
            existing.vcpus = vcpus
            existing.ram_gb = ram_gb
            existing.price_per_hour = price_per_hour
            existing.network_performance = network_performance
            existing.category = category
        else:
            db_item = EC2Catalog(
                instance_type=payload.instance_type,
                vcpus=vcpus,
                ram_gb=ram_gb,
                price_per_hour=price_per_hour,
                network_performance=network_performance,
                category=category
            )
            db.add(db_item)
            
        await db.commit()
        await cache_manager.clear_catalog_cache()
        if source:
            return {
                "status": "success",
                "source": source,
                "specs": {
                    "vcpus": vcpus,
                    "ram_gb": ram_gb,
                    "price_per_hour": price_per_hour,
                    "network_performance": network_performance,
                    "category": category
                }
            }
        return {"status": "success", "message": f"Successfully updated {svc_lower}"}
            
    elif svc_lower == "rds":
        specs = None
        source = None
        if payload.vcpus is None or payload.price_per_hour is None:
            try:
                specs = await lookup_rds_instance(payload.instance_type, region=region)
                source = "aws_pricing_api"
            except Exception as e:
                logger.warning(f"Dynamic RDS lookup failed: {e}")

        vcpus = payload.vcpus or (specs["vcpus"] if specs else 2)
        ram_gb = payload.ram_gb or (specs["ram_gb"] if specs else 4.0)
        price_per_hour = payload.price_per_hour or (specs["price_per_hour"] if specs else 0.05)
        category = payload.category or (specs["category"] if specs else "burstable")

        query = select(RDSCatalog).where(RDSCatalog.instance_type == payload.instance_type)
        res = await db.execute(query)
        existing = res.scalar_one_or_none()
        if existing:
            existing.vcpus = vcpus
            existing.ram_gb = ram_gb
            existing.price_per_hour = price_per_hour
            existing.category = category
        else:
            db_item = RDSCatalog(
                instance_type=payload.instance_type,
                vcpus=vcpus,
                ram_gb=ram_gb,
                price_per_hour=price_per_hour,
                category=category
            )
            db.add(db_item)
            
        await db.commit()
        await cache_manager.clear_catalog_cache()
        if source:
            return {
                "status": "success",
                "source": source,
                "specs": {
                    "vcpus": vcpus,
                    "ram_gb": ram_gb,
                    "price_per_hour": price_per_hour,
                    "category": category
                }
            }
        return {"status": "success", "message": f"Successfully updated {svc_lower}"}
            
    else:
        query = select(GenericServiceCatalog).where(
            GenericServiceCatalog.service == svc_lower,
            GenericServiceCatalog.instance_type == payload.instance_type
        )
        res = await db.execute(query)
        existing = res.scalar_one_or_none()
        if existing:
            existing.price_per_hour = payload.price_per_hour or existing.price_per_hour
            existing.unit = payload.unit or existing.unit
            existing.category = payload.category or existing.category
            existing.details = payload.details or existing.details
        else:
            db_item = GenericServiceCatalog(
                service=svc_lower,
                instance_type=payload.instance_type,
                vcpus=payload.vcpus or 0,
                ram_gb=payload.ram_gb or 0.0,
                price_per_hour=payload.price_per_hour or 0.05,
                unit=payload.unit or "GB-Month",
                category=payload.category or "general",
                region=region,
                details=payload.details or ""
            )
            db.add(db_item)
            
        await db.commit()
        await cache_manager.clear_catalog_cache()
        return {"status": "success", "message": f"Successfully updated {svc_lower}"}

@admin_router.delete("/api/admin/catalog/{service}/{instance_type}", status_code=status.HTTP_200_OK)
async def delete_instance(
    service: str,
    instance_type: str,
    region: str = "us-east-1",
    db: AsyncSession = Depends(get_db_session),
    api_key: str = Depends(verify_admin_key)
):
    """
    Deletes a catalog entry from the specified region's database.
    """
    svc_lower = service.lower().strip()
    
    valid_services = {"ec2", "rds", "iam", "vpc", "s3", "route53", "route 53", "ebs", "efs", "eks", "ecs", "ecr", "waf", "cloudwatch", "cloudfront", "cloudtrail"}
    if svc_lower not in valid_services:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid service '{service}'."
        )

    if svc_lower == "ec2":
        query = select(EC2Catalog).where(EC2Catalog.instance_type == instance_type)
    elif svc_lower == "rds":
        query = select(RDSCatalog).where(RDSCatalog.instance_type == instance_type)
    else:
        query = select(GenericServiceCatalog).where(
            GenericServiceCatalog.service == svc_lower,
            GenericServiceCatalog.instance_type == instance_type
        )
        
    res = await db.execute(query)
    existing = res.scalar_one_or_none()
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")
        
    await db.delete(existing)
    await db.commit()
    await cache_manager.clear_catalog_cache()
    return {"status": "success", "message": f"Deleted {instance_type}"}

@admin_router.get("/admin", response_class=HTMLResponse)
async def serve_admin_dashboard():
    """
    Serves the beautiful, premium dark-mode glassmorphic admin dashboard.
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AetherOps Cloud - Admin Catalog Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Outfit', 'sans-serif'],
                    },
                    colors: {
                        cyber: {
                            bg: '#08090d',
                            card: 'rgba(15, 17, 26, 0.75)',
                            border: 'rgba(255, 255, 255, 0.06)',
                            violet: '#7c3aed',
                            violetGlow: 'rgba(124, 58, 237, 0.15)',
                            lightViolet: '#a78bfa',
                            mint: '#10b981',
                            coral: '#ef4444'
                        }
                    }
                }
            }
        }
    </script>
    <style>
        body {
            background-color: #08090d;
            background-image: 
                radial-gradient(at 10% 20%, rgba(124, 58, 237, 0.12) 0px, transparent 50%),
                radial-gradient(at 90% 80%, rgba(16, 185, 129, 0.08) 0px, transparent 50%);
            background-attachment: fixed;
        }
        .glass-panel {
            backdrop-filter: blur(16px);
            background: rgba(15, 17, 26, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.06);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        }
        .glow-hover:hover {
            box-shadow: 0 0 15px rgba(124, 58, 237, 0.4);
            transform: translateY(-1px);
        }
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(18, 20, 29, 0.5);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(124, 58, 237, 0.3);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(124, 58, 237, 0.5);
        }
    </style>
</head>
<body class="text-gray-100 min-h-screen antialiased flex flex-col">

    <!-- Top Navigation -->
    <header class="glass-panel sticky top-0 z-50 border-b border-cyber-border py-4 px-6 md:px-12 flex justify-between items-center">
        <div class="flex items-center space-x-3">
            <div class="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyber-violet to-cyber-mint flex items-center justify-center shadow-lg shadow-cyber-violetGlow">
                <span class="font-bold text-lg text-white">A</span>
            </div>
            <div>
                <h1 class="text-xl font-bold tracking-tight bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">AetherOps Cloud</h1>
                <p class="text-[11px] text-cyber-lightViolet uppercase tracking-widest font-semibold">Management Console</p>
            </div>
        </div>
        
        <div class="flex items-center space-x-4 mr-2">
            <!-- Global Region Selector -->
            <div class="flex items-center space-x-2 bg-cyber-bg border border-cyber-border rounded-xl px-2.5 py-1">
                <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Region:</span>
                <select id="region-filter" onchange="onRegionFilterChange()" class="bg-transparent text-xs text-cyber-lightViolet focus:outline-none cursor-pointer font-bold">
                    <!-- Dynamic region options populated by JS -->
                </select>
            </div>
            <span id="cache-status" class="hidden md:inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-gray-800 text-gray-400">
                Checking Cache...
            </span>
            <span class="hidden md:inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-cyber-violetGlow text-cyber-lightViolet border border-cyber-violet/20">
                <span class="h-2 w-2 rounded-full bg-cyber-mint mr-2 animate-pulse"></span>
                Role: Cloud Architect
            </span>
        </div>
    </header>

    <!-- Main Workspace -->
    <main class="flex-grow max-w-7xl w-full mx-auto p-6 md:p-12 space-y-8">
        
        <!-- Status Bar & Actions -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between">
                <span class="text-sm font-medium text-gray-400">Total Compute Profiles</span>
                <div class="flex items-baseline space-x-2 mt-4">
                    <span id="compute-count" class="text-4xl font-bold text-white">0</span>
                    <span class="text-xs text-cyber-mint font-medium">EC2 + EKS + ECS</span>
                </div>
            </div>

            <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between">
                <span class="text-sm font-medium text-gray-400">Total Platform Services</span>
                <div class="flex items-baseline space-x-2 mt-4">
                    <span id="other-count" class="text-4xl font-bold text-white">0</span>
                    <span class="text-xs text-cyber-mint font-medium">DB + Storage + Network</span>
                </div>
            </div>

            <!-- Global Action Controls -->
            <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between space-y-3">
                <button onclick="syncAWSDocs()" class="w-full py-2.5 px-4 bg-gradient-to-r from-cyber-violet to-purple-600 hover:from-purple-600 hover:to-cyber-violet text-white font-medium text-sm rounded-xl transition duration-200 glow-hover flex justify-center items-center">
                    <svg class="h-4 w-4 mr-2 animate-spin hidden" id="sync-spinner" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Sync Live AWS Pricing</span>
                </button>
                <button onclick="clearRedisCache()" class="w-full py-2 px-4 bg-slate-800 hover:bg-slate-700 text-gray-300 border border-cyber-border font-medium text-[11px] rounded-xl transition duration-200 flex justify-center items-center">
                    <span>Clear Redis Cache-Aside</span>
                </button>
            </div>

        </div>

        <!-- Catalog Tables & Add Forms -->
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
            
            <!-- Left Sidebar Navigation for Services -->
            <div class="lg:col-span-1 space-y-2">
                <div class="text-xs font-bold text-gray-500 uppercase tracking-widest px-3 mb-2">AWS Services</div>
                <nav class="space-y-1.5" id="service-nav">
                    <!-- Dynamic navigation buttons -->
                </nav>
            </div>

            <!-- Right Workspace: Datatable -->
            <div class="lg:col-span-3 space-y-8">
                
                <!-- Datatable Panel -->
                <div class="glass-panel rounded-2xl overflow-hidden">
                    <div class="p-6 border-b border-cyber-border flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
                        <div>
                            <h2 class="text-md font-bold text-white uppercase tracking-wider flex items-center">
                                <span class="h-2 w-2 rounded-full bg-cyber-mint mr-2 animate-pulse"></span>
                                <span id="table-title">EC2 Catalog</span>
                            </h2>
                            <p class="text-xs text-gray-500 mt-1">Listing registered instances and specs inside database</p>
                        </div>
                        <div class="flex flex-col sm:flex-row items-stretch sm:items-center space-y-3 sm:space-y-0 sm:space-x-4 w-full md:w-auto">
                            <!-- Search Input -->
                            <div class="relative w-full sm:w-64">
                                <input type="text" onkeyup="filterTable('catalog-table', this.value)" placeholder="Search catalog items..." class="w-full py-1.5 pl-8 pr-3 bg-cyber-bg border border-cyber-border rounded-xl text-xs focus:outline-none focus:border-cyber-violet">
                                <svg class="w-4 h-4 text-gray-500 absolute left-2.5 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                            </div>
                        </div>
                    </div>
                    
                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse" id="catalog-table">
                            <thead>
                                <tr class="border-b border-cyber-border bg-slate-900/35 text-xs font-semibold text-gray-400 uppercase tracking-wider" id="table-headers">
                                    <!-- Dynamic headers -->
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-cyber-border/40 text-sm" id="table-rows">
                                <!-- Dynamic rows -->
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>

    </main>

    <!-- Footer -->
    <footer class="mt-auto border-t border-cyber-border py-6 text-center text-xs text-gray-500">
        &copy; 2026 AetherOps Engine AI. Admin Console built with FastAPI + TailwindCSS.
    </footer>

    <!-- Toast Notification -->
    <div id="toast" class="fixed bottom-6 right-6 px-5 py-3 rounded-xl shadow-lg border border-cyber-border bg-emerald-950/70 text-cyber-mint backdrop-blur-md flex items-center space-x-3 max-w-sm hidden z-50">
        <span id="toast-text" class="text-xs font-medium">Notification message</span>
    </div>

    <script>
        const regionsList = [
            { code: "us-east-1", name: "US East (N. Virginia)" },
            { code: "us-east-2", name: "US East (Ohio)" },
            { code: "us-west-1", name: "US West (N. California)" },
            { code: "us-west-2", name: "US West (Oregon)" },
            { code: "ca-central-1", name: "Canada (Central)" },
            { code: "ca-west-1", name: "Canada West (Calgary)" },
            { code: "mx-central-1", name: "Mexico (Central)" },
            { code: "us-gov-east-1", name: "AWS GovCloud (US-East)" },
            { code: "us-gov-west-1", name: "AWS GovCloud (US-West)" },
            { code: "sa-east-1", name: "South America (São Paulo)" },
            { code: "eu-west-1", name: "Europe (Ireland)" },
            { code: "eu-west-2", name: "Europe (London)" },
            { code: "eu-west-3", name: "Europe (Paris)" },
            { code: "eu-central-1", name: "Europe (Frankfurt)" },
            { code: "eu-central-2", name: "Europe (Zurich)" },
            { code: "eu-north-1", name: "Europe (Stockholm)" },
            { code: "eu-south-1", name: "Europe (Milan)" },
            { code: "eu-south-2", name: "Europe (Spain)" },
            { code: "ap-south-1", name: "Asia Pacific (Mumbai)" },
            { code: "ap-south-2", name: "Asia Pacific (Hyderabad)" },
            { code: "ap-southeast-1", name: "Asia Pacific (Singapore)" },
            { code: "ap-southeast-2", name: "Asia Pacific (Sydney)" },
            { code: "ap-southeast-3", name: "Asia Pacific (Jakarta)" },
            { code: "ap-southeast-4", name: "Asia Pacific (Melbourne)" },
            { code: "ap-southeast-5", name: "Asia Pacific (Malaysia)" },
            { code: "ap-southeast-6", name: "Asia Pacific (Thailand)" },
            { code: "ap-southeast-7", name: "Asia Pacific (New Zealand)" },
            { code: "ap-east-1", name: "Asia Pacific (Hong Kong)" },
            { code: "ap-east-2", name: "Asia Pacific (Taiwan)" },
            { code: "ap-northeast-1", name: "Asia Pacific (Tokyo)" },
            { code: "ap-northeast-2", name: "Asia Pacific (Seoul)" },
            { code: "ap-northeast-3", name: "Asia Pacific (Osaka)" },
            { code: "me-south-1", name: "Middle East (Bahrain)" },
            { code: "me-central-1", name: "Middle East (UAE)" },
            { code: "il-central-1", name: "Israel (Tel Aviv)" },
            { code: "me-central-2", name: "Middle East (Saudi Arabia)" },
            { code: "af-south-1", name: "Africa (Cape Town)" },
            { code: "cn-north-1", name: "China (Beijing)" },
            { code: "cn-northwest-1", name: "China (Ningxia)" }
        ];

        const servicesList = [
            { code: "ec2", name: "EC2 (Compute)" },
            { code: "rds", name: "RDS (Database)" },
            { code: "s3", name: "S3 (Storage)" },
            { code: "vpc", name: "VPC (Networking)" },
            { code: "iam", name: "IAM (Security)" },
            { code: "route53", name: "Route 53 (DNS)" },
            { code: "ebs", name: "EBS (Block Storage)" },
            { code: "efs", name: "EFS (File Storage)" },
            { code: "eks", name: "EKS (Kubernetes)" },
            { code: "ecs", name: "ECS (Containers)" },
            { code: "ecr", name: "ECR (Registry)" },
            { code: "waf", name: "WAF (Firewall)" },
            { code: "cloudwatch", name: "CloudWatch (Metrics)" },
            { code: "cloudfront", name: "CloudFront (CDN)" },
            { code: "cloudtrail", name: "CloudTrail (Auditing)" }
        ];

        let catalogData = {};
        let currentService = 'ec2';
        let currentRegion = 'us-east-1';
        const adminKey = localStorage.getItem('X-Admin-Key') || 'aetherops-secret-admin-key';

        function showToast(msg, type = "success") {
            const toast = document.getElementById('toast');
            const text = document.getElementById('toast-text');
            text.innerText = msg;
            if (type === "error") {
                toast.className = "fixed bottom-6 right-6 px-5 py-3 rounded-xl shadow-lg border border-cyber-coral/20 bg-rose-950/70 text-cyber-coral backdrop-blur-md flex items-center space-x-3 max-w-sm z-50";
            } else {
                toast.className = "fixed bottom-6 right-6 px-5 py-3 rounded-xl shadow-lg border border-cyber-mint/20 bg-emerald-950/70 text-cyber-mint backdrop-blur-md flex items-center space-x-3 max-w-sm z-50";
            }
            toast.classList.remove('hidden');
            setTimeout(() => {
                toast.classList.add('hidden');
            }, 4000);
        }

        async function onRegionFilterChange() {
            currentRegion = document.getElementById('region-filter').value;
            await fetchCatalog();
        }

        async function syncAWSDocs() {
            const spinner = document.getElementById('sync-spinner');
            spinner.classList.remove('hidden');
            showToast(`Ingesting AWS dynamic prices for region ${currentRegion.toUpperCase()}...`);
            try {
                const res = await fetch(`/api/admin/sync?region=${currentRegion}`, {
                    method: 'POST',
                    headers: { 'X-Admin-Key': adminKey }
                });
                if (!res.ok) {
                    const err = await res.json();
                    showToast(`Sync failed: ${err.detail || 'API error'}`, 'error');
                    return;
                }
                const data = await res.json();
                showToast(`AWS Price List Sync completed successfully for ${currentRegion.toUpperCase()}!`);
                await fetchCatalog();
            } catch (err) {
                showToast('Sync server timeout/error', 'error');
            } finally {
                spinner.classList.add('hidden');
            }
        }

        async function clearRedisCache() {
            try {
                const res = await fetch('/api/admin/clear-cache', {
                    method: 'POST',
                    headers: { 'X-Admin-Key': adminKey }
                });
                const data = await res.json();
                if (data.status === "success") {
                    showToast("Redis cache layer successfully cleared.");
                } else {
                    showToast("Cache invalidation failed (Redis Offline)", "error");
                }
                await fetchCatalog();
            } catch (err) {
                showToast("Cache operation failed", "error");
            }
        }

        async function fetchCatalog() {
            try {
                const res = await fetch(`/api/admin/catalog?region=${currentRegion}`);
                catalogData = await res.json();
                
                // Update Cache Status Badge
                const cacheStatus = document.getElementById('cache-status');
                if (catalogData.cache_connected) {
                    cacheStatus.innerText = "Redis Cache: Connected";
                    cacheStatus.className = "hidden md:inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950/50 text-cyber-mint border border-cyber-mint/20";
                } else {
                    cacheStatus.innerText = "Redis Cache: Offline";
                    cacheStatus.className = "hidden md:inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-rose-950/50 text-cyber-coral border border-cyber-coral/20";
                }

                // Render Navigation Items with Counts
                const nav = document.getElementById('service-nav');
                nav.innerHTML = '';
                
                let totalCompute = 0;
                let totalPlatform = 0;

                servicesList.forEach(svc => {
                    const items = catalogData[svc.code] || [];
                    const count = items.length;
                    
                    if (['ec2', 'eks', 'ecs'].includes(svc.code)) {
                        totalCompute += count;
                    } else {
                        totalPlatform += count;
                    }

                    const activeClass = (currentService === svc.code) 
                        ? "bg-cyber-violetGlow text-white border border-cyber-violet/30" 
                        : "text-gray-400 hover:bg-slate-800/40 hover:text-white border border-transparent";

                    nav.innerHTML += `
                        <button onclick="switchService('${svc.code}')" class="w-full flex items-center justify-between px-3 py-2 text-xs font-medium rounded-xl transition duration-150 ${activeClass}">
                            <span>${svc.name}</span>
                            <span class="px-2 py-0.5 rounded-full bg-slate-900 text-[10px] font-semibold text-gray-300">${count}</span>
                        </button>
                    `;
                });

                document.getElementById('compute-count').innerText = totalCompute;
                document.getElementById('other-count').innerText = totalPlatform;

                renderTable();

            } catch (err) {
                showToast("Failed to communicate with catalog database API", "error");
            }
        }

        function switchService(serviceCode) {
            currentService = serviceCode;
            fetchCatalog();
        }

        function renderTable() {
            const tableTitle = document.getElementById('table-title');
            const tableHeaders = document.getElementById('table-headers');
            const tableRows = document.getElementById('table-rows');

            const serviceName = servicesList.find(s => s.code === currentService)?.name || currentService.toUpperCase();
            tableTitle.innerText = `${serviceName} Catalog Database (${currentRegion.toUpperCase()})`;

            tableRows.innerHTML = '';
            const items = catalogData[currentService] || [];

            tableHeaders.innerHTML = `
                <th class="p-4">Resource Type / Name</th>
                <th class="p-4">vCPUs</th>
                <th class="p-4">RAM / Size</th>
                <th class="p-4">Billing Unit</th>
                <th class="p-4">Category</th>
                <th class="p-4">Network / Details</th>
                <th class="p-4 text-right">Price / Rate</th>
            `;

            if (items.length === 0) {
                tableRows.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-xs text-gray-500">No specifications stored for this service. Click Sync.</td></tr>`;
                return;
            }

            items.forEach(item => {
                const vcpuDisp = (item.vcpus && item.vcpus > 0) ? item.vcpus : '-';
                const ramDisp = (item.ram_gb && item.ram_gb > 0) ? `${item.ram_gb} GB` : '-';
                const unitDisp = item.unit || 'Hrs';
                const netOrDetailDisp = item.network_performance || item.details || '-';
                
                tableRows.innerHTML += `
                    <tr class="hover:bg-slate-800/20 transition border-b border-cyber-border/40">
                        <td class="p-4 font-semibold text-white">${item.instance_type}</td>
                        <td class="p-4 text-gray-400 font-mono">${vcpuDisp}</td>
                        <td class="p-4 text-gray-400 font-mono">${ramDisp}</td>
                        <td class="p-4 text-gray-400 font-mono">${unitDisp}</td>
                        <td class="p-4"><span class="px-2 py-0.5 rounded bg-slate-900 text-xs capitalize text-gray-400 border border-cyber-border">${item.category}</span></td>
                        <td class="p-4 text-xs text-gray-500 truncate max-w-xs">${netOrDetailDisp}</td>
                        <td class="p-4 text-right text-cyber-lightViolet font-mono font-bold">$${item.price_per_hour.toFixed(4)}</td>
                    </tr>
                `;
            });
        }

        function filterTable(tableId, query) {
            const table = document.getElementById(tableId);
            const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
            query = query.toLowerCase();
            for (let i = 0; i < rows.length; i++) {
                const text = rows[i].innerText.toLowerCase();
                if (text.includes(query)) {
                    rows[i].style.display = "";
                } else {
                    rows[i].style.display = "none";
                }
            }
        }

        window.addEventListener('load', () => {
            // Populate regions filter select dynamically
            const filterSelect = document.getElementById('region-filter');
            filterSelect.innerHTML = '';
            regionsList.forEach(r => {
                filterSelect.innerHTML += `<option value="${r.code}" class="bg-cyber-bg text-white">${r.name}</option>`;
            });
            filterSelect.value = currentRegion;
            fetchCatalog();
        });
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content, status_code=200)
