# services/requirement_analysis/app/admin_router.py
import logging
import time
from typing import Literal, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db_session
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

# Mock AWS Pricing & Documentation API response
MOCK_AWS_DOCS_API_DATA = {
    "ec2": [
        {"instance_type": "c6i.large", "vcpus": 2, "ram_gb": 4.0, "price_per_hour": 0.085, "network_performance": "Up to 12.5 Gbps", "category": "compute_optimized"},
        {"instance_type": "c6i.xlarge", "vcpus": 4, "ram_gb": 8.0, "price_per_hour": 0.17, "network_performance": "Up to 12.5 Gbps", "category": "compute_optimized"},
        {"instance_type": "g5.xlarge", "vcpus": 4, "ram_gb": 16.0, "price_per_hour": 1.006, "network_performance": "Up to 10 Gbps", "category": "gpu_instance"},
        {"instance_type": "r6g.large", "vcpus": 2, "ram_gb": 16.0, "price_per_hour": 0.1008, "network_performance": "Up to 10 Gbps", "category": "memory_optimized"},
        {"instance_type": "t3.medium", "vcpus": 2, "ram_gb": 4.0, "price_per_hour": 0.0416, "network_performance": "Up to 5 Gbps", "category": "burstable"}
    ],
    "rds": [
        {"instance_type": "db.m6g.xlarge", "vcpus": 4, "ram_gb": 16.0, "price_per_hour": 0.28, "category": "standard"},
        {"instance_type": "db.r6g.large", "vcpus": 2, "ram_gb": 16.0, "price_per_hour": 0.24, "category": "memory"},
        {"instance_type": "db.t4g.small", "vcpus": 2, "ram_gb": 2.0, "price_per_hour": 0.032, "category": "burstable"}
    ]
}

# Unified schema for dynamic catalog operations
class AdminCatalogInput(BaseModel):
    instance_type: str = Field(..., examples=["c6i.large", "db.m6g.xlarge"])
    region: str | None = Field(default=None, examples=["us-east-1", "us-west-2"])
    az: str | None = Field(default=None, examples=["us-east-1a", "us-east-1b"])
    # Optional manual overrides — if omitted, specs are fetched live from AWS APIs
    vcpus: int | None = Field(default=None, examples=[2])
    ram_gb: float | None = Field(default=None, examples=[4.0])
    price_per_hour: float | None = Field(default=None, examples=[0.085])
    network_performance: str | None = Field(default=None, examples=["Up to 10 Gbps"])
    category: str | None = Field(default=None, examples=["compute"])

# Service-to-model/lookup mapping
CATALOG_SERVICES = {
    "ec2": {
        "model": EC2Catalog,
        "lookup": lookup_ec2_instance,
        "source_name": "ec2.shop",
        "has_network": True,
    },
    "rds": {
        "model": RDSCatalog,
        "lookup": lookup_rds_instance,
        "source_name": "aws_pricing_api",
        "has_network": False,
    },
}

DYNAMIC_SERVICES = [
    "iam", "vpc", "s3", "route53", "route 53", "ebs", "efs",
    "ecs", "ecr", "eks", "waf", "cloudwatch", "cloudfront", "cloudtrail"
]

def get_service_config(service: str):
    service_lower = service.lower()
    if service_lower in CATALOG_SERVICES:
        return CATALOG_SERVICES[service_lower]
    if service_lower in DYNAMIC_SERVICES:
        return {
            "model": GenericServiceCatalog,
            "lookup": lambda instance_type, region="us-east-1", az=None: lookup_generic_aws_service(service_lower, instance_type, region),
            "source_name": "aws_pricing_api",
            "has_network": False,
        }
    return None

@admin_router.get("/api/admin/catalog", status_code=status.HTTP_200_OK)
async def get_current_catalog(region: str = "us-east-1", db: AsyncSession = Depends(get_db_session)):
    """
    Returns the current active catalog items from the database.
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
    Dynamically resolves and returns specs/pricing for a specific instance type, region, and AZ from AWS pricing.
    """
    svc = get_service_config(service)
    if not svc:
        raise HTTPException(status_code=400, detail=f"Invalid service '{service}'. Must be one of: {', '.join(list(CATALOG_SERVICES.keys()) + DYNAMIC_SERVICES)}")
    
    try:
        if service.lower() == "ec2":
            specs = await lookup_ec2_instance(instance_type, region=region, az=az)
        elif service.lower() == "rds":
            specs = await lookup_rds_instance(instance_type, region=region, az=az)
        else:
            specs = await lookup_generic_aws_service(service, instance_type, region=region)
        return {
            "status": "success",
            "service": service.lower(),
            "region": region,
            "az": az,
            "specs": specs
        }
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=404, detail=str(e))

@admin_router.get("/api/admin/catalog/categories", status_code=status.HTTP_200_OK)
async def get_categorized_catalog(
    category: str | None = None,
    region: str = "us-east-1",
    db: AsyncSession = Depends(get_db_session)
):
    """
    Returns all catalog items from the database grouped by category and nested by service type.
    Optionally filters to only return details for a specific category.
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
        
    # If DB is empty, use the default static catalog as fallback
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
            
        from app.sync_helper import get_generic_fallback_pricing
        fallback_items = [
            ("iam", "IAM User/Role/Policy"),
            ("vpc", "NAT Gateway"),
            ("vpc", "VPN Connection"),
            ("s3", "Standard Storage"),
            ("s3", "Glacier Storage"),
            ("route53", "Hosted Zone"),
            ("ebs", "gp3"),
            ("efs", "Standard Storage"),
            ("eks", "Cluster"),
            ("ecs", "Fargate"),
            ("ecr", "Storage"),
            ("waf", "Rule"),
            ("cloudwatch", "Metric"),
            ("cloudfront", "Data Transfer Out"),
            ("cloudtrail", "Paid Events"),
        ]
        for svc, item_t in fallback_items:
            item = get_generic_fallback_pricing(svc, item_t, region=region)
            cat = item.get("category", "general")
            if category and cat.lower() != category.lower():
                continue
            ensure_cat(cat, svc)
            categorized[cat][svc].append(item)
            
    return {
        "status": "success",
        "category_filter": category,
        "categories": categorized,
        "cache_connected": cache_manager._is_connected
    }

@admin_router.post("/api/admin/sync", status_code=status.HTTP_200_OK)
async def sync_aws_docs_catalog(region: str = "us-east-1", db: AsyncSession = Depends(get_db_session)):
    """
    Calls AWS Pricing API to fetch updated instances, inserts them,
    and invalidates the Redis Cache-Aside layer.
    """
    try:
        result = await sync_catalog_from_aws(db, region=region)
        return result
    except Exception as e:
        logger.error(f"Live catalog synchronization failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AWS Catalog Sync failed: {str(e)}"
        )

@admin_router.post("/api/admin/clear-cache", status_code=status.HTTP_200_OK)
async def clear_redis_cache():
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
    db: AsyncSession = Depends(get_db_session)
):
    """
    Dynamically adds or updates an instance/item in the catalog.
    Service can be 'ec2', 'rds', or any other dynamic AWS service.
    """
    svc = get_service_config(service)
    if not svc:
        raise HTTPException(status_code=400, detail=f"Invalid service '{service}'. Must be one of: {', '.join(list(CATALOG_SERVICES.keys()) + DYNAMIC_SERVICES)}")

    Model = svc["model"]
    has_manual = payload.price_per_hour is not None

    if has_manual:
        specs = {
            "instance_type": payload.instance_type,
            "vcpus": payload.vcpus or 0,
            "ram_gb": payload.ram_gb or 0.0,
            "price_per_hour": payload.price_per_hour,
            "category": payload.category or "general",
        }
        if svc.get("has_network"):
            specs["network_performance"] = payload.network_performance or "Up to 10 Gbps"
        if Model == GenericServiceCatalog:
            specs["service"] = service.lower()
            specs["region"] = payload.region or region
        source = "manual"
    else:
        try:
            if service.lower() == "ec2":
                specs = await lookup_ec2_instance(
                    payload.instance_type,
                    region=payload.region or region,
                    az=payload.az
                )
            elif service.lower() == "rds":
                specs = await lookup_rds_instance(
                    payload.instance_type,
                    region=payload.region or region,
                    az=payload.az
                )
            else:
                specs = await lookup_generic_aws_service(
                    service,
                    payload.instance_type,
                    region=payload.region or region
                )
            source = svc["source_name"]
        except (ValueError, RuntimeError) as e:
            raise HTTPException(status_code=404, detail=str(e))

    if Model == GenericServiceCatalog:
        query = select(Model).where((Model.instance_type == specs["instance_type"]) & (Model.service == service.lower()))
    else:
        query = select(Model).where(Model.instance_type == specs["instance_type"])
        
    res = await db.execute(query)
    existing = res.scalar_one_or_none()

    if existing:
        existing.vcpus = specs.get("vcpus", existing.vcpus)
        existing.ram_gb = specs.get("ram_gb", existing.ram_gb)
        existing.price_per_hour = specs["price_per_hour"]
        existing.category = specs.get("category", existing.category)
        if svc.get("has_network") and "network_performance" in specs:
            existing.network_performance = specs["network_performance"]
        if Model == GenericServiceCatalog:
            existing.unit = specs.get("unit", existing.unit)
            existing.region = specs.get("region", existing.region)
            existing.details = specs.get("details", existing.details)
        msg = f"Updated {service.upper()} item {specs['instance_type']} (source: {source})"
    else:
        db_item = Model(**specs)
        db.add(db_item)
        msg = f"Created {service.upper()} item {specs['instance_type']} (source: {source})"

    await db.commit()
    await cache_manager.clear_catalog_cache()
    return {"status": "success", "message": msg, "specs": specs, "source": source, "service": service.lower()}

@admin_router.delete("/api/admin/catalog/{service}/{instance_type}", status_code=status.HTTP_200_OK)
async def delete_instance(service: str, instance_type: str, region: str = "us-east-1", db: AsyncSession = Depends(get_db_session)):
    """
    Deletes an instance/item from the catalog.
    """
    svc = get_service_config(service)
    if not svc:
        raise HTTPException(status_code=400, detail=f"Invalid service '{service}'. Must be one of: {', '.join(list(CATALOG_SERVICES.keys()) + DYNAMIC_SERVICES)}")

    Model = svc["model"]
    if Model == GenericServiceCatalog:
        query = select(Model).where((Model.instance_type == instance_type) & (Model.service == service.lower()))
    else:
        query = select(Model).where(Model.instance_type == instance_type)
        
    res = await db.execute(query)
    existing = res.scalar_one_or_none()

    if not existing:
        raise HTTPException(status_code=404, detail=f"{service.upper()} item '{instance_type}' not found")

    await db.delete(existing)
    await db.commit()
    await cache_manager.clear_catalog_cache()
    return {"status": "success", "message": f"Deleted {service.upper()} {instance_type}", "service": service.lower()}

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
        /* Custom scrollbar */
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
        
        <div class="flex items-center space-x-4">
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

            <!-- Right Workspace: Form & Datatable -->
            <div class="lg:col-span-3 space-y-8">
                
                <!-- Unified Catalog Item Form -->
                <div class="glass-panel p-6 rounded-2xl">
                    <h2 class="text-md font-bold text-white mb-1 flex items-center">
                        <span class="h-4 w-1 bg-cyber-violet mr-2 rounded font-semibold" id="form-color-bar"></span>
                        <span id="form-title">Add Infrastructure Catalog Item</span>
                    </h2>
                    <p class="text-xs text-gray-500 mb-4">Specs are fetched dynamically from <span class="text-cyber-violet font-semibold">AWS bulk price lists</span>. Set manual overrides if desired.</p>
                    
                    <form id="unified-form" onsubmit="submitCatalogItem(event)" class="space-y-4">
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label class="block text-xs font-semibold text-gray-400 mb-1">Target Service <span class="text-red-400">*</span></label>
                                <select id="item-service" onchange="onServiceChange()" class="w-full py-2.5 px-3 bg-cyber-bg border border-cyber-border rounded-xl text-sm focus:outline-none focus:border-cyber-violet focus:ring-1 focus:ring-cyber-violet/30">
                                    <option value="ec2">EC2 (Compute Instances)</option>
                                    <option value="rds">RDS (Database Engines)</option>
                                    <option value="s3">S3 (Simple Storage Service)</option>
                                    <option value="vpc">VPC (Virtual Private Cloud)</option>
                                    <option value="iam">IAM (Identity &amp; Access)</option>
                                    <option value="route53">Route 53 (DNS Service)</option>
                                    <option value="ebs">EBS (Elastic Block Store)</option>
                                    <option value="efs">EFS (Elastic File System)</option>
                                    <option value="eks">EKS (Elastic Kubernetes)</option>
                                    <option value="ecs">ECS (Elastic Container Service)</option>
                                    <option value="ecr">ECR (Container Registry)</option>
                                    <option value="waf">WAF (Web Application Firewall)</option>
                                    <option value="cloudwatch">CloudWatch (Monitoring)</option>
                                    <option value="cloudfront">CloudFront (CDN)</option>
                                    <option value="cloudtrail">CloudTrail (Auditing)</option>
                                </select>
                            </div>
                            
                            <div>
                                <label class="block text-xs font-semibold text-gray-400 mb-1">Resource Name / Type <span class="text-red-400">*</span></label>
                                <input type="text" id="item-type" required placeholder="e.g. c6i.large, Standard Storage, NAT Gateway" class="w-full py-2.5 px-3 bg-cyber-bg border border-cyber-border rounded-xl text-sm focus:outline-none focus:border-cyber-violet">
                            </div>

                            <div>
                                <label class="block text-xs font-semibold text-gray-400 mb-1">AWS Region</label>
                                <input type="text" id="item-region" placeholder="us-east-1" class="w-full py-2.5 px-3 bg-cyber-bg border border-cyber-border rounded-xl text-sm focus:outline-none focus:border-cyber-violet">
                            </div>
                        </div>

                        <!-- Resolved specs details panel -->
                        <div id="resolved-preview" class="hidden bg-slate-900/60 rounded-xl p-3 border border-cyber-border/50 text-xs text-gray-300 space-y-1">
                            <span class="text-cyber-mint font-bold flex items-center mb-1">
                                <svg class="w-3.5 h-3.5 mr-1 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                                Resolved AWS Specs
                            </span>
                            <div id="resolved-preview-content"></div>
                        </div>

                        <!-- Advanced manual overrides -->
                        <details class="group">
                            <summary class="cursor-pointer text-xs text-gray-500 hover:text-gray-300 transition flex items-center">
                                <svg class="w-3.5 h-3.5 mr-1.5 transition-transform group-open:rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                                Manual Specification Overrides
                            </summary>
                            <div class="mt-3 space-y-3 pl-1 border-l-2 border-cyber-border/30 ml-2">
                                <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                                    <div id="form-vcpu-ram-group" class="col-span-2 grid grid-cols-2 gap-3">
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-500 mb-1">vCPUs</label>
                                            <input type="number" id="item-vcpus" placeholder="auto" class="w-full py-2 px-3 bg-cyber-bg border border-cyber-border rounded-xl text-xs focus:outline-none focus:border-cyber-violet">
                                        </div>
                                        <div>
                                            <label class="block text-xs font-semibold text-gray-500 mb-1">RAM (GB)</label>
                                            <input type="number" id="item-ram" step="0.5" placeholder="auto" class="w-full py-2 px-3 bg-cyber-bg border border-cyber-border rounded-xl text-xs focus:outline-none focus:border-cyber-violet">
                                        </div>
                                    </div>
                                    <div>
                                        <label class="block text-xs font-semibold text-gray-500 mb-1">Price per Hour / Unit</label>
                                        <input type="number" id="item-price" step="0.00001" placeholder="auto" class="w-full py-2 px-3 bg-cyber-bg border border-cyber-border rounded-xl text-xs focus:outline-none focus:border-cyber-violet">
                                    </div>
                                    <div>
                                        <label class="block text-xs font-semibold text-gray-500 mb-1">Category Class</label>
                                        <input type="text" id="item-cat" placeholder="e.g. compute, storage" class="w-full py-2 px-3 bg-cyber-bg border border-cyber-border rounded-xl text-xs focus:outline-none focus:border-cyber-violet">
                                    </div>
                                </div>
                                <div class="grid grid-cols-2 gap-3">
                                    <div id="form-network-group">
                                        <label class="block text-xs font-semibold text-gray-500 mb-1">Network Performance</label>
                                        <input type="text" id="item-network" placeholder="e.g. Up to 10 Gbps" class="w-full py-2 px-3 bg-cyber-bg border border-cyber-border rounded-xl text-xs focus:outline-none focus:border-cyber-violet">
                                    </div>
                                    <div id="form-unit-group" class="hidden">
                                        <label class="block text-xs font-semibold text-gray-500 mb-1">Billing Unit</label>
                                        <input type="text" id="item-unit" placeholder="e.g. GB-Month, HostedZone-Month" class="w-full py-2 px-3 bg-cyber-bg border border-cyber-border rounded-xl text-xs focus:outline-none focus:border-cyber-violet">
                                    </div>
                                </div>
                            </div>
                        </details>

                        <button type="submit" id="submit-btn" class="w-full py-2.5 bg-gradient-to-r from-cyber-violet to-purple-600 hover:from-purple-600 hover:to-cyber-violet text-white font-semibold text-sm rounded-xl transition duration-200 flex justify-center items-center">
                            <svg class="h-4 w-4 mr-2 animate-spin hidden" id="form-spinner" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            <span id="submit-text">Lookup &amp; Ingest Item</span>
                        </button>
                    </form>
                </div>

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
                            <!-- Region Filter -->
                            <div class="flex items-center space-x-2 bg-cyber-bg border border-cyber-border rounded-xl px-2.5 py-1">
                                <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">Region:</span>
                                <select id="region-filter" onchange="onRegionFilterChange()" class="bg-transparent text-xs text-cyber-lightViolet focus:outline-none cursor-pointer font-bold">
                                    <option value="us-east-1" class="bg-cyber-bg text-white">US East (N. Virginia)</option>
                                    <option value="us-west-2" class="bg-cyber-bg text-white">US West (Oregon)</option>
                                    <option value="eu-west-1" class="bg-cyber-bg text-white">Europe (Ireland)</option>
                                    <option value="ap-southeast-1" class="bg-cyber-bg text-white">Asia Pacific (Singapore)</option>
                                    <option value="ap-south-1" class="bg-cyber-bg text-white">Asia Pacific (Mumbai)</option>
                                </select>
                            </div>

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

        function onServiceChange() {
            const service = document.getElementById('item-service').value;
            const vcpuRamGroup = document.getElementById('form-vcpu-ram-group');
            const netGroup = document.getElementById('form-network-group');
            const unitGroup = document.getElementById('form-unit-group');
            const colorBar = document.getElementById('form-color-bar');

            if (service === 'ec2') {
                vcpuRamGroup.classList.remove('hidden');
                netGroup.classList.remove('hidden');
                unitGroup.classList.add('hidden');
                colorBar.className = "h-4 w-1 bg-cyber-violet mr-2 rounded font-semibold";
            } else if (service === 'rds') {
                vcpuRamGroup.classList.remove('hidden');
                netGroup.classList.add('hidden');
                unitGroup.classList.add('hidden');
                colorBar.className = "h-4 w-1 bg-cyber-mint mr-2 rounded font-semibold";
            } else {
                vcpuRamGroup.classList.add('hidden');
                netGroup.classList.add('hidden');
                unitGroup.classList.remove('hidden');
                colorBar.className = "h-4 w-1 bg-purple-500 mr-2 rounded font-semibold";
            }
            
            // Auto update placeholder based on service
            const itemInput = document.getElementById('item-type');
            if (service === 's3') itemInput.placeholder = "e.g. Standard Storage, Glacier Storage";
            else if (service === 'vpc') itemInput.placeholder = "e.g. NAT Gateway, VPN Connection";
            else if (service === 'ebs') itemInput.placeholder = "e.g. gp3, gp2";
            else if (service === 'iam') itemInput.placeholder = "e.g. IAM User/Role/Policy";
            else itemInput.placeholder = "e.g. c6i.large, db.t4g.small, Hosted Zone, Cluster";
        }

        async function onRegionFilterChange() {
            currentRegion = document.getElementById('region-filter').value;
            // Auto update form region to match
            document.getElementById('item-region').value = currentRegion;
            await fetchCatalog();
        }

        async function syncAWSDocs() {
            const spinner = document.getElementById('sync-spinner');
            spinner.classList.remove('hidden');
            showToast(`Ingesting AWS dynamic prices for region ${currentRegion.toUpperCase()}... This may take up to 30-45 seconds.`);
            try {
                const res = await fetch(`/api/admin/sync?region=${currentRegion}`, { method: 'POST' });
                if (!res.ok) {
                    const err = await res.json();
                    showToast(`Sync failed: ${err.detail || 'API timeout'}`, 'error');
                    return;
                }
                const data = await res.json();
                showToast(`AWS Price List Sync completed successfully for ${currentRegion.toUpperCase()}! ${data.added_ec2} EC2 + ${data.added_rds} RDS ingested.`);
                await fetchCatalog();
            } catch (err) {
                showToast('Sync server timeout/error', 'error');
            } finally {
                spinner.classList.add('hidden');
            }
        }

        async function clearRedisCache() {
            try {
                const res = await fetch('/api/admin/clear-cache', { method: 'POST' });
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
            document.getElementById('item-service').value = serviceCode;
            onServiceChange();
            fetchCatalog();
        }

        function renderTable() {
            const tableTitle = document.getElementById('table-title');
            const tableHeaders = document.getElementById('table-headers');
            const tableRows = document.getElementById('table-rows');

            const serviceName = servicesList.find(s => s.code === currentService)?.name || currentService.toUpperCase();
            tableTitle.innerText = `${serviceName} Catalog Database`;

            tableRows.innerHTML = '';
            const items = catalogData[currentService] || [];

            tableHeaders.innerHTML = `
                <th class="p-4">Resource Type / Name</th>
                <th class="p-4">vCPUs</th>
                <th class="p-4">RAM / Size</th>
                <th class="p-4">Price / Rate</th>
                <th class="p-4">Billing Unit</th>
                <th class="p-4">AWS Region</th>
                <th class="p-4">Category</th>
                <th class="p-4">Network / Details</th>
            `;

            if (items.length === 0) {
                tableRows.innerHTML = `<tr><td colspan="8" class="p-8 text-center text-xs text-gray-500">No specifications stored for this service. Click Sync.</td></tr>`;
                return;
            }

            items.forEach(item => {
                const vcpuDisp = (item.vcpus && item.vcpus > 0) ? item.vcpus : '-';
                const ramDisp = (item.ram_gb && item.ram_gb > 0) ? `${item.ram_gb} GB` : '-';
                const unitDisp = item.unit || 'Hrs';
                const regionDisp = (item.region || 'us-east-1').toUpperCase();
                const netOrDetailDisp = item.network_performance || item.details || '-';
                
                tableRows.innerHTML += `
                    <tr class="hover:bg-slate-800/20 transition border-b border-cyber-border/40">
                        <td class="p-4 font-semibold text-white">${item.instance_type}</td>
                        <td class="p-4 text-gray-400 font-mono">${vcpuDisp}</td>
                        <td class="p-4 text-gray-400 font-mono">${ramDisp}</td>
                        <td class="p-4 text-cyber-lightViolet font-mono font-bold">$${item.price_per_hour.toFixed(4)}</td>
                        <td class="p-4 text-gray-400 font-mono">${unitDisp}</td>
                        <td class="p-4 text-gray-400 uppercase">${regionDisp}</td>
                        <td class="p-4"><span class="px-2 py-0.5 rounded bg-slate-900 text-xs capitalize text-gray-400 border border-cyber-border">${item.category}</span></td>
                        <td class="p-4 text-xs text-gray-500 truncate max-w-xs">${netOrDetailDisp}</td>
                    </tr>
                `;
            });
        }

        async function submitCatalogItem(e) {
            e.preventDefault();
            const spinner = document.getElementById('form-spinner');
            const btnText = document.getElementById('submit-text');
            spinner.classList.remove('hidden');
            btnText.textContent = 'Resolving Spec...';

            const service = document.getElementById('item-service').value;
            const type = document.getElementById('item-type').value;
            const region = document.getElementById('item-region').value || 'us-east-1';

            const payload = {
                instance_type: type,
                region: region
            };

            const priceVal = document.getElementById('item-price').value;
            if (priceVal !== '') {
                payload.price_per_hour = parseFloat(priceVal);
                payload.vcpus = parseInt(document.getElementById('item-vcpus').value || '0');
                payload.ram_gb = parseFloat(document.getElementById('item-ram').value || '0.0');
                
                const cat = document.getElementById('item-cat').value;
                if (cat) payload.category = cat;
                
                const net = document.getElementById('item-network').value;
                if (net) payload.network_performance = net;
                
                const unit = document.getElementById('item-unit').value;
                if (unit) payload.unit = unit;
            }

            try {
                const res = await fetch(`/api/admin/catalog/${service}?region=${region}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (!res.ok) {
                    const err = await res.json();
                    showToast(err.detail || 'Resolution/addition failed', 'error');
                    return;
                }

                const data = await res.json();
                showToast(data.message);

                if (data.specs) {
                    const preview = document.getElementById('resolved-preview');
                    const previewContent = document.getElementById('resolved-preview-content');
                    preview.classList.remove('hidden');
                    
                    let html = `<div>Resource: <strong>${data.specs.instance_type}</strong></div>`;
                    html += `<div>Hourly Cost: <strong class="text-cyber-mint">$${data.specs.price_per_hour.toFixed(5)}</strong></div>`;
                    if (service === 'ec2' || service === 'rds') {
                        html += `<div>vCPUs: <strong>${data.specs.vcpus}</strong> | RAM: <strong>${data.specs.ram_gb} GB</strong></div>`;
                    }
                    if (data.specs.unit) html += `<div>Billing Unit: <strong>${data.specs.unit}</strong></div>`;
                    if (data.specs.details) html += `<div class="italic text-[10px] text-gray-500 mt-1">${data.specs.details}</div>`;
                    
                    previewContent.innerHTML = html;
                }

                document.getElementById('unified-form').reset();
                document.getElementById('item-service').value = service;
                onServiceChange();
                
                currentService = service;
                await fetchCatalog();

            } catch (err) {
                showToast('Failed to add catalog item', 'error');
            } finally {
                spinner.classList.add('hidden');
                btnText.textContent = 'Lookup & Ingest Item';
            }
        }

        async function deleteCatalogItem(service, instanceType) {
            if (!confirm(`Are you sure you want to delete ${instanceType} from the ${service.toUpperCase()} catalog database?`)) return;
            try {
                const res = await fetch(`/api/admin/catalog/${service}/${instanceType}?region=${currentRegion}`, { method: 'DELETE' });
                if (!res.ok) {
                    const err = await res.json();
                    showToast(err.detail || 'Delete failed', 'error');
                    return;
                }
                const data = await res.json();
                showToast(data.message);
                await fetchCatalog();
            } catch (err) {
                showToast("Server call failed during deletion", "error");
            }
        }

        function populateFormEC2(type, vcpus, ram, price, cat, net) {
            document.getElementById('item-service').value = 'ec2';
            onServiceChange();
            document.getElementById('item-type').value = type;
            document.getElementById('item-vcpus').value = vcpus;
            document.getElementById('item-ram').value = ram;
            document.getElementById('item-price').value = price;
            document.getElementById('item-cat').value = cat;
            document.getElementById('item-network').value = net;
            document.querySelector('#unified-form details').open = true;
            document.getElementById('item-type').focus();
        }

        function populateFormRDS(type, vcpus, ram, price, cat) {
            document.getElementById('item-service').value = 'rds';
            onServiceChange();
            document.getElementById('item-type').value = type;
            document.getElementById('item-vcpus').value = vcpus;
            document.getElementById('item-ram').value = ram;
            document.getElementById('item-price').value = price;
            document.getElementById('item-cat').value = cat;
            document.querySelector('#unified-form details').open = true;
            document.getElementById('item-type').focus();
        }

        function populateFormGeneric(service, type, price, cat, unit, region) {
            document.getElementById('item-service').value = service;
            onServiceChange();
            document.getElementById('item-type').value = type;
            document.getElementById('item-price').value = price;
            document.getElementById('item-cat').value = cat;
            document.getElementById('item-unit').value = unit;
            document.getElementById('item-region').value = region;
            document.querySelector('#unified-form details').open = true;
            document.getElementById('item-type').focus();
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
            onServiceChange();
            fetchCatalog();
        });
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content, status_code=200)
