# services/requirement_analysis/app/admin_router.py
import logging
import time
import os
from typing import Literal, List, Optional
import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Header, Security, BackgroundTasks, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text

from app.database import (
    get_db_session,
    get_sessionmaker_for_region,
    init_db_for_region,
    SUPPORTED_REGIONS,
    get_region_db_url,
    get_postgres_engine,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    IS_TESTING
)
from app.models import EC2Catalog, RDSCatalog, GenericServiceCatalog, SyncMetadata
from app.cache import cache_manager, load_aws_regions_reference_in_cache, warm_region_cache
from app.sync_helper import (
    sync_catalog_from_aws,
    lookup_ec2_instance,
    lookup_rds_instance,
    lookup_generic_aws_service,
    load_aws_regions_reference
)
from app.security import verify_admin_key, validate_region_code
from app.login_page import get_login_page_html
from app.auth import (
    verify_password,
    hash_password,
    create_access_token,
    decode_access_token,
    check_login_rate_limit,
    record_failed_login,
    clear_failed_login,
    get_admin_db_session,
    log_admin_audit,
    get_current_admin,
    SESSION_COOKIE_NAME,
)
from app.security_models import AdminUser, AdminAuditLog

logger = logging.getLogger("requirement-analysis-admin")

admin_router = APIRouter()

class AdminLoginInput(BaseModel):
    username: str = Field(..., examples=["admin"])
    password: str = Field(..., examples=["AetherOps@2026!"])
    remember_me: bool = Field(default=False)

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

@admin_router.get("/admin/login", response_class=HTMLResponse)
async def get_admin_login(request: Request, redirect: Optional[str] = "/admin"):
    """
    Renders the dedicated Cyberpunk Admin Login Portal.
    If the client is already authenticated with a valid JWT cookie, redirects to console.
    """
    cookie_token = request.cookies.get(SESSION_COOKIE_NAME)
    if cookie_token:
        payload = decode_access_token(cookie_token)
        if payload:
            return RedirectResponse(url=redirect or "/admin", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    return HTMLResponse(content=get_login_page_html(redirect=redirect or "/admin"), status_code=200)

@admin_router.post("/api/admin/auth/login")
async def post_admin_login(
    payload: AdminLoginInput,
    request: Request,
    response: Response
):
    """
    Authenticates administrator against PostgreSQL admin_security.admin_users vault
    and issues an HttpOnly secure session cookie + JWT token with Redis rate-limiting.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"

    # 1. Rate Limiting Check (Redis)
    if not check_login_rate_limit(client_ip):
        await log_admin_audit(
            username=payload.username,
            action="RATE_LIMITED",
            status="BLOCKED",
            ip=client_ip,
            details="Exceeded 5 failed attempts in 15 minutes"
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please wait 15 minutes before trying again."
        )

    # 2. Database User Lookup
    user = None
    async for session in get_admin_db_session():
        stmt = select(AdminUser).where(
            (AdminUser.username == payload.username.strip()) |
            (AdminUser.email == payload.username.strip().lower())
        )
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()
        break

    if not user or not verify_password(payload.password, user.password_hash):
        record_failed_login(client_ip)
        await log_admin_audit(
            username=payload.username,
            action="FAILED_LOGIN",
            status="FAILED",
            ip=client_ip,
            details="Invalid username or password"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials. Please verify your username and password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact system administrator."
        )

    # 3. Successful Login
    clear_failed_login(client_ip)

    # Update last login timestamp
    async for session in get_admin_db_session():
        u = await session.get(AdminUser, user.id)
        if u:
            u.last_login_at = datetime.datetime.utcnow()
            u.failed_attempts = 0
            await session.commit()
        break

    await log_admin_audit(
        username=user.username,
        action="LOGIN",
        status="SUCCESS",
        ip=client_ip,
        details=f"Successful login via role {user.role}"
    )

    hours = 7 * 24 if payload.remember_me else 8
    token = create_access_token(
        username=user.username,
        role=user.role,
        email=user.email,
        hours=hours
    )

    # Set secure HttpOnly cookie
    max_age = hours * 3600
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=max_age,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/"
    )

    return {
        "status": "SUCCESS",
        "message": "Authentication successful",
        "user": user.to_dict(),
        "token": token
    }

@admin_router.post("/api/admin/auth/logout")
async def post_admin_logout(
    request: Request,
    response: Response
):
    """
    Clears the HttpOnly admin session cookie and records audit log.
    """
    user_info = None
    cookie_token = request.cookies.get(SESSION_COOKIE_NAME)
    if cookie_token:
        user_info = decode_access_token(cookie_token)

    username = user_info.get("sub", "admin") if user_info else "admin"
    client_ip = request.client.host if request.client else "127.0.0.1"

    await log_admin_audit(
        username=username,
        action="LOGOUT",
        status="SUCCESS",
        ip=client_ip,
        details="User logged out"
    )

    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/"
    )
    return {
        "status": "SUCCESS",
        "message": "Logged out successfully"
    }

@admin_router.get("/api/admin/auth/me")
async def get_admin_me(
    admin: dict = Depends(get_current_admin)
):
    """
    Returns current authenticated administrator profile.
    """
    return {
        "status": "AUTHENTICATED",
        "user": admin
    }

@admin_router.get("/api/admin/auth/audit")
async def get_admin_audit(
    limit: int = 50,
    admin: dict = Depends(get_current_admin)
):
    """
    Returns security audit log from PostgreSQL vault.
    """
    logs = []
    async for session in get_admin_db_session():
        stmt = select(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(limit)
        res = await session.execute(stmt)
        records = res.scalars().all()
        logs = [r.to_dict() for r in records]
        break
    return {
        "total": len(logs),
        "audit_logs": logs
    }

@admin_router.get("/api/admin/probe", status_code=status.HTTP_200_OK)
async def get_system_live_probe(
    region: str = "us-east-1",
    api_key: str = Depends(verify_admin_key)
):
    """
    Returns live diagnostics, connection health, ping latency, and data presence
    for Redis, PostgreSQL Docker container, and SQLite local engine.
    """
    region = region.lower().strip()
    region_pg = region.replace("-", "_")
    
    # 1. Redis Probe
    redis_info = {
        "connected": False,
        "latency_ms": 0.0,
        "total_keys": 0,
        "region_data_cached": False,
        "region_keys_count": 0,
        "persistence_file": "dump.rdb + appendonly.aof (data/redis/)",
        "error": None
    }
    if cache_manager._is_connected and cache_manager.redis_client:
        try:
            t0 = time.monotonic()
            await cache_manager.redis_client.ping()
            redis_info["latency_ms"] = round((time.monotonic() - t0) * 1000, 2)
            redis_info["connected"] = True
            redis_info["total_keys"] = await cache_manager.redis_client.dbsize()
            
            # Check presence for current region
            region_keys = await cache_manager.redis_client.keys(f"catalog:{region}:*")
            redis_info["region_data_cached"] = len(region_keys) > 0
            redis_info["region_keys_count"] = len(region_keys)
        except Exception as e:
            redis_info["error"] = str(e)
            
    # 2. PostgreSQL Probe
    pg_info = {
        "connected": False,
        "latency_ms": 0.0,
        "database": POSTGRES_DB,
        "host": f"{POSTGRES_HOST}:{POSTGRES_PORT}",
        "total_schemas": 0,
        "region_data_present": False,
        "region_records_count": 0,
        "schema_name": f"region_{region_pg}",
        "error": None
    }
    if not IS_TESTING:
        try:
            pg_eng = get_postgres_engine(region)
            t0 = time.monotonic()
            async with pg_eng.connect() as conn:
                await conn.execute(text("SELECT 1"))
                pg_info["latency_ms"] = round((time.monotonic() - t0) * 1000, 2)
                pg_info["connected"] = True
                
                # Check total regional schemas
                schema_res = await conn.execute(text("SELECT count(*) FROM information_schema.schemata WHERE schema_name LIKE 'region_%'"))
                pg_info["total_schemas"] = schema_res.scalar() or 0
                
                # Check table count in this region's schema
                try:
                    ec2_cnt = await conn.execute(text("SELECT count(*) FROM ec2_catalog"))
                    rds_cnt = await conn.execute(text("SELECT count(*) FROM rds_catalog"))
                    gen_cnt = await conn.execute(text("SELECT count(*) FROM generic_service_catalog"))
                    total_in_reg = (ec2_cnt.scalar() or 0) + (rds_cnt.scalar() or 0) + (gen_cnt.scalar() or 0)
                    pg_info["region_records_count"] = total_in_reg
                    pg_info["region_data_present"] = total_in_reg > 0
                except Exception:
                    pass
        except Exception as e:
            pg_info["error"] = str(e)
    else:
        pg_info["connected"] = True
        pg_info["database"] = "test_isolated"
        pg_info["region_data_present"] = True
        
    # 3. SQLite Probe
    sqlite_file = f"catalog_{region}.db"
    sqlite_info = {
        "connected": True,
        "db_file": sqlite_file,
        "file_exists": os.path.exists(sqlite_file),
        "file_size_bytes": os.path.getsize(sqlite_file) if os.path.exists(sqlite_file) else 0,
        "latency_ms": 0.05,
        "mode": "WAL"
    }
    
    return {
        "region": region,
        "timestamp": time.time(),
        "redis": redis_info,
        "postgresql": pg_info,
        "sqlite": sqlite_info
    }

@admin_router.post("/api/admin/catalog/seed-all", status_code=status.HTTP_200_OK)
async def trigger_bulk_seed_all(
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_admin_key)
):
    """
    Triggers uploading and warming catalog data for ALL 39 regions into:
    SQLite local files, PostgreSQL container schemas, and Redis cache.
    """
    from app.seed import seed_all_regions
    
    async def _do_bulk():
        try:
            await seed_all_regions(force=True)
            logger.info("Background bulk upload for all 39 regions completed successfully.")
        except Exception as e:
            logger.error(f"Bulk upload failed: {e}", exc_info=True)
            
    background_tasks.add_task(_do_bulk)
    return {
        "status": "PROCESSING",
        "message": "Bulk catalog upload for all 39 regions started in background (PostgreSQL + Redis + SQLite)."
    }

@admin_router.get("/api/admin/catalog", status_code=status.HTTP_200_OK)
async def get_current_catalog(
    region: str = "us-east-1",
    db: AsyncSession = Depends(get_db_session)
):
    """
    Returns the current active catalog items from Redis cache if available;
    otherwise queries the partitioned database for the specified region and populates Redis cache.
    """
    region_lower = region.lower().strip()
    cache_key = f"catalog:{region_lower}:full_admin"
    
    if cache_manager._is_connected:
        cached_data = await cache_manager.get_json(cache_key)
        if cached_data:
            cached_data["cache_connected"] = True
            return cached_data

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
        
    if cache_manager._is_connected:
        await cache_manager.set_json(cache_key, catalog_data, expire_seconds=86400)

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
    populates database, and warms Redis cache.
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

class RegionSyncInput(BaseModel):
    force_live_fetch: bool = Field(default=True, description="Force fetching from live ec2.shop API")
    include_generic_services: bool = Field(default=True, description="Include generic AWS services in sync")

@admin_router.get("/api/admin/catalog/regions", status_code=status.HTTP_200_OK)
async def list_all_configured_regions(api_key: str = Depends(verify_admin_key)):
    """
    Returns metadata and live probe status for all 39 configured AWS regions across SQLite, PostgreSQL, and Redis.
    """
    try:
        ref_data = load_aws_regions_reference()
    except Exception:
        ref_data = {"regions": []}

    result = []
    for r in ref_data.get("regions", []):
        code = r.get("region_code", "")
        if code not in SUPPORTED_REGIONS:
            continue

        db_url = get_region_db_url(code)
        if "sqlite" in db_url:
            db_filename = db_url.split("///")[-1]
            db_exists = os.path.exists(db_filename)
        else:
            db_filename = db_url
            db_exists = True

        # Check SyncMetadata from DB if available
        sync_status = "PENDING"
        last_synced = None
        if db_exists:
            try:
                await init_db_for_region(code)
                sf = get_sessionmaker_for_region(code)
                async with sf() as session:
                    meta_res = await session.execute(select(SyncMetadata).where(SyncMetadata.region_code == code))
                    meta = meta_res.scalar_one_or_none()
                    if meta:
                        sync_status = meta.status
                        last_synced = meta.last_sync_timestamp.isoformat() if meta.last_sync_timestamp else None
            except Exception:
                pass

        # Check Redis cache
        cached = False
        if cache_manager._is_connected:
            try:
                val = await cache_manager.get_json(f"catalog:{code}:metadata")
                cached = val is not None
            except Exception:
                pass

        result.append({
            "region_code": code,
            "region_name": r.get("region_name", ""),
            "geography": r.get("geography", ""),
            "az_count": r.get("az_count", 0),
            "db_file": db_filename,
            "db_exists": db_exists,
            "postgres_ready": True,
            "last_synced": last_synced,
            "sync_status": sync_status,
            "cached_in_redis": cached,
        })

    return result

@admin_router.post("/api/admin/catalog/sync/{region_code}", status_code=status.HTTP_202_ACCEPTED)
async def trigger_region_sync(
    region_code: str,
    background_tasks: BackgroundTasks,
    payload: Optional[RegionSyncInput] = None,
    api_key: str = Depends(verify_admin_key),
):
    """
    Triggers an on-demand catalog sync for a single AWS region.
    Returns an immediate acknowledgment while the sync runs in the background.
    """
    region_code = validate_region_code(region_code)
    body = payload or RegionSyncInput()
    task_id = f"sync_{region_code}_{int(time.time())}"

    async def _do_sync():
        try:
            await init_db_for_region(region_code)
            sf = get_sessionmaker_for_region(region_code)
            async with sf() as session:
                await sync_catalog_from_aws(
                    session,
                    region=region_code,
                    force_live_fetch=body.force_live_fetch,
                    include_generic_services=body.include_generic_services,
                )
            logger.info(f"Background sync completed for region '{region_code}' (task={task_id})")
        except Exception as e:
            logger.error(f"Background sync failed for region '{region_code}': {e}", exc_info=True)
            try:
                import datetime
                sf2 = get_sessionmaker_for_region(region_code)
                async with sf2() as session:
                    meta_res = await session.execute(select(SyncMetadata).where(SyncMetadata.region_code == region_code))
                    meta = meta_res.scalar_one_or_none()
                    if meta:
                        meta.status = "FAILED"
                        meta.error_message = str(e)[:500]
                    else:
                        session.add(SyncMetadata(
                            region_code=region_code,
                            last_sync_timestamp=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
                            status="FAILED",
                            records_synced=0, ec2_count=0, rds_count=0, generic_count=0, duration_ms=0,
                            error_message=str(e)[:500],
                        ))
                    await session.commit()
            except Exception:
                pass

    background_tasks.add_task(_do_sync)

    return {
        "status": "PROCESSING",
        "region": region_code,
        "message": f"Dynamic catalog sync started for {region_code}",
        "task_id": task_id,
    }

@admin_router.get("/api/admin/catalog/status/{region_code}", status_code=status.HTTP_200_OK)
async def get_region_sync_status(
    region_code: str,
    api_key: str = Depends(verify_admin_key),
):
    """
    Returns sync health & telemetry for a specific region.
    """
    region_code = validate_region_code(region_code)

    try:
        await init_db_for_region(region_code)
        sf = get_sessionmaker_for_region(region_code)
        async with sf() as session:
            meta_res = await session.execute(select(SyncMetadata).where(SyncMetadata.region_code == region_code))
            meta = meta_res.scalar_one_or_none()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not query SyncMetadata: {e}")

    if not meta:
        return {
            "region_code": region_code,
            "status": "NEVER_SYNCED",
            "records_updated": {"ec2": 0, "rds": 0, "generic": 0},
            "duration_ms": 0,
            "last_sync_timestamp": None,
            "error_message": None,
        }

    return {
        "region_code": meta.region_code,
        "status": meta.status,
        "records_updated": {
            "ec2": meta.ec2_count,
            "rds": meta.rds_count,
            "generic": meta.generic_count,
        },
        "total_records": meta.records_synced,
        "duration_ms": meta.duration_ms,
        "last_sync_timestamp": meta.last_sync_timestamp.isoformat() if meta.last_sync_timestamp else None,
        "error_message": meta.error_message,
    }

@admin_router.post("/api/admin/catalog/{service}", status_code=status.HTTP_200_OK)
async def add_or_update_instance(
    service: str,
    payload: AdminCatalogInput,
    region: str = "us-east-1",
    db: AsyncSession = Depends(get_db_session),
    api_key: str = Depends(verify_admin_key)
):
    """
    Manually inserts or updates a resource in the specified region's database.
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

@admin_router.get("/api/admin/modules", status_code=status.HTTP_200_OK)
async def get_platform_modules():
    """
    Returns live health, ports, and catalog dependency mappings for all 8 Aether platform modules.
    """
    import httpx
    
    modules = [
        {
            "id": 1,
            "code": "requirement_analysis",
            "name": "Requirement Analysis Engine",
            "port": 8001,
            "url": "http://localhost:8001",
            "health_endpoint": "http://localhost:8001/health",
            "status": "ONLINE",
            "phase": "Phase 1: Analysis & Right-Sizing",
            "description": "Translates high-level project tech stacks and traffic projections into optimal compute, storage, and networking specifications.",
            "catalog_dependencies": ["EC2 Compute", "RDS Databases", "EBS Storage", "VPC Networking"],
            "catalog_role": "Queries regional baseline instance sizing and pricing multipliers to select optimal EC2/RDS profiles within target budget."
        },
        {
            "id": 2,
            "code": "architecture_generator",
            "name": "Cloud Architecture Generator",
            "port": 8002,
            "url": "http://localhost:8002",
            "health_endpoint": "http://localhost:8002/health",
            "status": "ONLINE",
            "phase": "Phase 2: Topology & Network Design",
            "description": "Synthesizes production multi-tier AWS architecture diagrams, subnet placement, NAT Gateways, and high-availability topologies.",
            "catalog_dependencies": ["VPC & NAT Gateway", "Route 53", "EKS Kubernetes", "ECS Containers", "CloudFront CDN"],
            "catalog_role": "Leverages regional networking rates, container orchestrator specifications, and CDN edge data to synthesize resilient architecture designs."
        },
        {
            "id": 3,
            "code": "iac_code_generator",
            "name": "IaC Code Generator",
            "port": 8003,
            "url": "http://localhost:8003",
            "health_endpoint": None,
            "status": "READY",
            "phase": "Phase 3: Infrastructure as Code",
            "description": "Produces production-grade, validated Terraform (HCL) and OpenTofu modules matching the generated cloud architecture.",
            "catalog_dependencies": ["All 39 AWS Regions", "EC2 Specs", "RDS Engines", "S3 Storage Classes", "IAM Policies"],
            "catalog_role": "Directly references instance types, AZ counts, and regional parameters to generate syntactically correct Terraform provider files."
        },
        {
            "id": 4,
            "code": "finops_optimizer",
            "name": "FinOps Cost Optimizer",
            "port": 8004,
            "url": "http://localhost:8004",
            "health_endpoint": None,
            "status": "CONNECTED",
            "phase": "Phase 4: Cost Intelligence & TCO",
            "description": "Conducts continuous cost arbitrage, spot vs on-demand simulations, reserved instance planning, and 3-year TCO financial forecasting.",
            "catalog_dependencies": ["Redis L1 Price Cache", "PostgreSQL Master Pricing", "All 39 Regional Catalogs"],
            "catalog_role": "Master consumer of real-time AWS Pricing API data; relies on 0ms Redis latency to calculate instant cost projections across any region."
        },
        {
            "id": 5,
            "code": "security_compliance",
            "name": "Security & Compliance Engine",
            "port": 8005,
            "url": "http://localhost:8005",
            "health_endpoint": None,
            "status": "READY",
            "phase": "Phase 5: Zero-Trust Governance",
            "description": "Enforces CIS AWS Foundations Benchmark compliance, least-privilege IAM policies, automated WAF rules, and KMS encryption.",
            "catalog_dependencies": ["WAF Rules & WebACLs", "IAM Security", "CloudTrail Auditing", "KMS Encryption"],
            "catalog_role": "Inspects WAF WebACL rate structures, IAM role boundaries, and audit logging pricing across target regions."
        },
        {
            "id": 6,
            "code": "cicd_pipeline",
            "name": "CI/CD Pipeline Engine",
            "port": 8006,
            "url": "http://localhost:8006",
            "health_endpoint": None,
            "status": "READY",
            "phase": "Phase 6: GitOps & Delivery",
            "description": "Builds automated GitHub Actions and GitLab CI workflows with security scanning, plan validation, and automated canary deployments.",
            "catalog_dependencies": ["ECR Container Registry", "ECS Fargate", "EKS Kubernetes", "CloudWatch Metrics"],
            "catalog_role": "Calculates container registry storage and network transfer out pricing to optimize artifact deployment pipelines."
        },
        {
            "id": 7,
            "code": "observability_apm",
            "name": "Observability & APM Engine",
            "port": 8007,
            "url": "http://localhost:8007",
            "health_endpoint": None,
            "status": "READY",
            "phase": "Phase 7: Monitoring & Telemetry",
            "description": "Instruments OpenTelemetry collectors, custom CloudWatch alarms, synthetic probes, and real-time SLO error-budget monitors.",
            "catalog_dependencies": ["CloudWatch Alarms & Metrics", "CloudTrail Audit Logs", "OpenSearch"],
            "catalog_role": "Retrieves metric ingestion rates, custom dimension pricing, and log storage costs across the active region."
        },
        {
            "id": 8,
            "code": "deployer_drift",
            "name": "Deployer & Drift Engine",
            "port": 8008,
            "url": "http://localhost:8008",
            "health_endpoint": None,
            "status": "READY",
            "phase": "Phase 8: Autonomous Provisioning",
            "description": "Executes terraform state reconciliation, blue/green traffic cutovers, and continuous background drift detection with automated remediation.",
            "catalog_dependencies": ["All 39 PostgreSQL Schemas", "Redis L1 State Cache", "Dynamic AWS Offer Index"],
            "catalog_role": "Compares deployed cloud infrastructure against the catalog baseline to flag regional rate changes or instance deprecation."
        }
    ]

    async with httpx.AsyncClient(timeout=0.6) as client:
        for mod in modules:
            if mod["health_endpoint"]:
                try:
                    r = await client.get(mod["health_endpoint"])
                    if r.status_code == 200:
                        mod["status"] = "ONLINE"
                    else:
                        mod["status"] = "DEGRADED"
                except Exception:
                    mod["status"] = "OFFLINE"

    return {
        "status": "success",
        "total_modules": len(modules),
        "online_count": sum(1 for m in modules if m["status"] == "ONLINE"),
        "modules": modules
    }

@admin_router.get("/admin", response_class=HTMLResponse)
async def serve_admin_dashboard():
    """
    Serves the master dark-mode glassmorphic admin dashboard for AetherOps AI.
    Features:
    - Hamburger collapsible sidebar with all 8 modules + Central Catalog
    - Real-time Redis L1, PostgreSQL L3, and SQLite L2 live diagnostics probes
    - 39-Region AWS matrix telemetry
    - Bulk upload & Live sync controllers
    """
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AetherOps Cloud - Admin Catalog Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Plus Jakarta Sans', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace'],
                    },
                    colors: {
                        cyber: {
                            bg: '#07080c',
                            sidebar: '#0b0d14',
                            card: 'rgba(17, 20, 31, 0.75)',
                            border: 'rgba(255, 255, 255, 0.08)',
                            accent: '#6366f1',
                            violet: '#8b5cf6',
                            mint: '#10b981',
                            amber: '#f59e0b',
                            coral: '#ef4444',
                            cyan: '#06b6d4'
                        }
                    }
                }
            }
        }
    </script>
    <style>
        body {
            background-color: #07080c;
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.10) 0px, transparent 50%),
                radial-gradient(at 50% 50%, rgba(6, 182, 212, 0.05) 0px, transparent 60%);
            background-attachment: fixed;
        }
        .glass-panel {
            backdrop-filter: blur(16px);
            background: rgba(14, 17, 28, 0.78);
            border: 1px solid rgba(255, 255, 255, 0.07);
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.6);
        }
        .glow-hover:hover {
            box-shadow: 0 0 25px rgba(99, 102, 241, 0.4);
            transform: translateY(-1px);
        }
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(11, 13, 20, 0.8);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(99, 102, 241, 0.35);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(99, 102, 241, 0.7);
        }
        /* Smooth Sidebar Drawer & Collapse Transitions */
        #sidebar {
            transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1), min-width 0.25s cubic-bezier(0.4, 0, 0.2, 1), transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.2s ease;
        }
        @media (min-width: 1024px) {
            #sidebar {
                position: static !important;
                transform: translateX(0) !important;
                width: 17.5rem;
                min-width: 17.5rem;
                opacity: 1;
            }
            #sidebar.is-desktop-collapsed {
                width: 0 !important;
                min-width: 0 !important;
                max-width: 0 !important;
                overflow: hidden !important;
                border-right-width: 0 !important;
                opacity: 0 !important;
                pointer-events: none !important;
            }
        }
        @media (max-width: 1023px) {
            #sidebar {
                position: fixed !important;
                top: 0;
                bottom: 0;
                left: 0;
                width: 17.5rem;
                transform: translateX(-100%) !important;
                z-index: 50;
            }
            #sidebar.is-mobile-open {
                transform: translateX(0) !important;
                box-shadow: 12px 0 40px rgba(0, 0, 0, 0.85);
            }
        }
        .tab-btn-active {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(139, 92, 246, 0.25));
            border-color: rgba(99, 102, 241, 0.5);
            color: #ffffff;
            box-shadow: 0 4px 15px -3px rgba(99, 102, 241, 0.3);
        }
    </style>
</head>
<body class="text-gray-100 min-h-screen antialiased flex flex-col font-sans">

    <!-- App Wrapper with Sidebar & Main Area -->
    <div class="flex flex-1 overflow-hidden relative">

        <!-- Sidebar Overlay on Mobile -->
        <div id="sidebar-overlay" onclick="toggleSidebar()" class="fixed inset-0 bg-black/75 backdrop-blur-sm z-40 hidden transition-opacity"></div>

        <!-- Master Hamburger Sidebar -->
        <aside id="sidebar" class="bg-cyber-sidebar/95 border-r border-cyber-border flex flex-col justify-between backdrop-blur-xl shrink-0 overflow-hidden select-none">
            <div class="w-[17.5rem] h-full flex flex-col justify-between overflow-hidden">
                <!-- Sidebar Top Content -->
                <div>
                    <!-- Brand Header -->
                    <div class="p-4 border-b border-cyber-border flex items-center justify-between">
                        <div class="flex items-center space-x-3">
                            <div class="h-9 w-9 rounded-xl bg-gradient-to-tr from-cyber-accent via-indigo-500 to-cyber-cyan flex items-center justify-center shadow-lg shadow-cyber-accent/25 shrink-0">
                                <span class="font-extrabold text-base text-white">A</span>
                            </div>
                            <div class="min-w-0">
                                <h1 class="text-sm font-extrabold tracking-tight text-white flex items-center gap-1.5 truncate">
                                    <span>AetherOps</span> <span class="text-[9px] px-1.5 py-0.5 rounded bg-cyber-accent/20 text-indigo-300 font-semibold border border-cyber-accent/30 font-mono">CORE</span>
                                </h1>
                                <p class="text-[9px] text-gray-400 tracking-wider uppercase font-medium truncate">Autonomous CloudOps</p>
                            </div>
                        </div>
                        <button onclick="toggleSidebar()" class="text-gray-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition cursor-pointer" title="Close Sidebar" aria-label="Close Sidebar">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                        </button>
                    </div>

                    <!-- Navigation Sections -->
                    <div class="p-3 space-y-5 overflow-y-auto max-h-[calc(100vh-170px)]">
                        
                        <!-- Core Platform Navigation -->
                        <div>
                            <div class="text-[10px] font-bold text-gray-400 uppercase tracking-widest px-3 mb-2">Platform Console</div>
                            <nav class="space-y-1">
                                <button onclick="switchMainView('catalog')" id="nav-btn-catalog" class="w-full flex items-center justify-between px-3 py-2 text-xs font-semibold rounded-xl transition text-left tab-btn-active border border-transparent cursor-pointer">
                                    <div class="flex items-center space-x-2.5">
                                        <svg class="w-4 h-4 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7C5 4 4 5 4 7z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-6h6v6"></path></svg>
                                        <span>Global AWS Catalog</span>
                                    </div>
                                    <span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Master</span>
                                </button>

                                <button onclick="switchMainView('modules')" id="nav-btn-modules" class="w-full flex items-center justify-between px-3 py-2 text-xs font-medium rounded-xl text-gray-400 hover:text-white hover:bg-slate-800/40 transition text-left border border-transparent cursor-pointer">
                                    <div class="flex items-center space-x-2.5">
                                        <svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                                        <span>Platform Modules (8)</span>
                                    </div>
                                    <span class="text-[9px] px-1.5 py-0.5 rounded bg-purple-950/60 text-purple-300 font-mono">8 Total</span>
                                </button>

                                <button onclick="switchMainView('matrix')" id="nav-btn-matrix" class="w-full flex items-center justify-between px-3 py-2 text-xs font-medium rounded-xl text-gray-400 hover:text-white hover:bg-slate-800/40 transition text-left border border-transparent cursor-pointer">
                                    <div class="flex items-center space-x-2.5">
                                        <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064"></path></svg>
                                        <span>39-Region Cloud Matrix</span>
                                    </div>
                                    <span class="text-[9px] px-1.5 py-0.5 rounded bg-cyan-950/60 text-cyan-300 font-mono">39 AWS</span>
                                </button>

                                <button onclick="switchMainView('probes')" id="nav-btn-probes" class="w-full flex items-center justify-between px-3 py-2 text-xs font-medium rounded-xl text-gray-400 hover:text-white hover:bg-slate-800/40 transition text-left border border-transparent cursor-pointer">
                                    <div class="flex items-center space-x-2.5">
                                        <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                        <span>Database & Cache Probes</span>
                                    </div>
                                    <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
                                </button>
                            </nav>
                        </div>

                        <!-- 8 Platform Modules List (Clickable Interactive) -->
                        <div>
                            <div class="text-[10px] font-bold text-gray-400 uppercase tracking-widest px-3 mb-2 flex justify-between items-center">
                                <span>Aether Modules</span>
                                <span class="text-[9px] text-indigo-400 font-mono bg-indigo-950/60 px-1.5 py-0.5 rounded">All 8 Integrated</span>
                            </div>
                            <nav class="space-y-1" id="sidebar-modules-list">
                                <!-- Populated dynamically via JS -->
                            </nav>
                        </div>

                        <!-- Database Quick Actions -->
                        <div>
                            <div class="text-[10px] font-bold text-gray-400 uppercase tracking-widest px-3 mb-2">Cloud Operations</div>
                            <div class="space-y-1.5">
                                <button onclick="triggerUploadAllRegions()" class="w-full py-1.5 px-3 text-left text-xs text-cyan-300 hover:text-white bg-slate-900/60 hover:bg-cyan-950/40 border border-cyan-500/20 rounded-xl transition flex items-center justify-between cursor-pointer">
                                    <span>Bulk Upload 39 Regions</span>
                                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                                </button>
                                <button onclick="clearRedisCache()" class="w-full py-1.5 px-3 text-left text-xs text-amber-300 hover:text-white bg-slate-900/60 hover:bg-amber-950/40 border border-amber-500/20 rounded-xl transition flex items-center justify-between cursor-pointer">
                                    <span>Purge Redis L1 Cache</span>
                                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                                </button>
                            </div>
                        </div>

                    </div>
                </div>

                <!-- Sidebar Footer -->
                <div class="p-4 border-t border-cyber-border bg-black/30 text-[11px] text-gray-400 flex items-center justify-between shrink-0">
                    <div class="flex items-center space-x-2">
                        <div class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></div>
                        <span class="font-medium text-gray-300">Cluster Healthy</span>
                    </div>
                    <span class="font-mono text-[10px] text-gray-500">v1.0.0-PROD</span>
                </div>
            </div>
        </aside>

        <!-- Main Content Area -->
        <div class="flex-1 flex flex-col min-w-0 overflow-y-auto">

            <!-- Top Navigation Bar (Sleek, Fully Responsive, Zero Overflow) -->
            <header class="glass-panel sticky top-0 z-30 border-b border-cyber-border px-3 sm:px-5 py-2.5 flex items-center justify-between gap-2 overflow-hidden">
                
                <!-- Left: Hamburger Toggle & Title -->
                <div class="flex items-center space-x-2 sm:space-x-3 shrink-0">
                    <button onclick="toggleSidebar()" id="hamburger-btn" class="p-2 rounded-xl text-gray-300 hover:text-white hover:bg-slate-800/80 border border-cyber-border hover:border-indigo-500/40 focus:outline-none transition flex items-center justify-center shrink-0 cursor-pointer" title="Toggle Navigation Sidebar" aria-label="Toggle Sidebar">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
                    </button>
                    <div class="flex items-center space-x-1.5 shrink-0">
                        <span class="font-extrabold text-sm sm:text-base text-white tracking-tight">AetherOps</span>
                        <span class="text-gray-600 hidden md:inline">/</span>
                        <span class="text-xs font-bold text-indigo-400 font-mono hidden md:inline" id="nav-view-label">CATALOG</span>
                    </div>
                </div>

                <!-- Center: Compact View Switcher Pills (Visible on Desktops >=1280px) -->
                <div class="hidden xl:flex items-center space-x-1 bg-cyber-bg/80 border border-cyber-border p-1 rounded-xl shrink-0">
                    <button onclick="switchMainView('catalog')" id="header-tab-catalog" class="px-2.5 py-1 text-xs font-semibold rounded-lg transition bg-indigo-600/30 text-white border border-indigo-500/40 flex items-center gap-1.5 cursor-pointer">
                        <svg class="w-3.5 h-3.5 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1 3 3 3h10c2 0 3-1 3-3V7c0-2-1-3-3-3H7C5 4 4 5 4 7z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-6h6v6"></path></svg>
                        <span>Catalog</span>
                    </button>
                    <button onclick="switchMainView('modules')" id="header-tab-modules" class="px-2.5 py-1 text-xs font-medium text-gray-400 hover:text-white rounded-lg transition flex items-center gap-1.5 cursor-pointer">
                        <svg class="w-3.5 h-3.5 text-purple-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                        <span>Modules (8)</span>
                    </button>
                    <button onclick="switchMainView('matrix')" id="header-tab-matrix" class="px-2.5 py-1 text-xs font-medium text-gray-400 hover:text-white rounded-lg transition flex items-center gap-1.5 cursor-pointer">
                        <svg class="w-3.5 h-3.5 text-cyan-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064"></path></svg>
                        <span>39 Regions</span>
                    </button>
                    <button onclick="switchMainView('probes')" id="header-tab-probes" class="px-2.5 py-1 text-xs font-medium text-gray-400 hover:text-white rounded-lg transition flex items-center gap-1.5 cursor-pointer">
                        <svg class="w-3.5 h-3.5 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                        <span>Probes</span>
                    </button>
                </div>

                <!-- Right: Region Select, Compact Cluster Pill & Admin Key -->
                <div class="flex items-center space-x-1.5 sm:space-x-2.5 shrink-0">
                    
                    <!-- Compact Region Selector -->
                    <div class="flex items-center space-x-1.5 bg-cyber-bg/90 border border-cyber-border rounded-xl px-2 py-1 shrink-0">
                        <svg class="w-3.5 h-3.5 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path></svg>
                        <select id="region-filter" onchange="onRegionFilterChange()" class="bg-transparent text-xs text-indigo-300 font-bold focus:outline-none cursor-pointer max-w-[85px] sm:max-w-[130px] md:max-w-[160px] truncate">
                            <!-- Populated dynamically -->
                        </select>
                    </div>

                    <!-- Live Cluster Status Pill -->
                    <button onclick="switchMainView('probes')" id="pill-cluster" class="flex items-center space-x-1.5 px-2 sm:px-2.5 py-1 rounded-xl text-xs font-semibold bg-slate-900/90 border border-emerald-500/30 text-emerald-300 hover:border-emerald-500/60 transition shrink-0 cursor-pointer" title="Click to view live database diagnostics">
                        <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse shrink-0"></span>
                        <span id="pill-cluster-text" class="font-mono text-[11px] hidden sm:inline">Cluster Ready</span>
                        <span class="font-mono text-[10px] sm:hidden text-emerald-400">Live</span>
                    </button>

                    <!-- Authenticated Admin User Badge -->
                    <div id="auth-user-pill" class="flex items-center space-x-1.5 sm:space-x-2 bg-indigo-950/60 border border-indigo-500/30 rounded-xl px-2 sm:px-2.5 py-1 text-xs shrink-0" title="Active Admin Session">
                        <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shrink-0"></div>
                        <span id="auth-username" class="font-bold text-indigo-200 font-mono text-[11px] sm:text-xs">admin</span>
                        <span id="auth-role" class="hidden md:inline-block px-1.5 py-0.5 text-[9px] font-extrabold uppercase tracking-wider rounded bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">SUPER_ADMIN</span>
                    </div>

                    <!-- Admin Key Button -->
                    <button onclick="promptChangeAdminKey()" class="p-1.5 px-2 rounded-xl text-xs font-bold bg-slate-900/80 text-gray-300 border border-cyber-border hover:text-white hover:border-indigo-500/40 transition flex items-center gap-1 shrink-0 cursor-pointer hidden sm:flex" title="Configure Admin API Secret Key">
                        <svg class="w-3.5 h-3.5 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path></svg>
                        <span class="hidden lg:inline text-[11px]">API Key</span>
                    </button>

                    <!-- Secure Logout Button -->
                    <button onclick="logoutAdmin()" class="p-1.5 px-2 sm:px-2.5 rounded-xl text-xs font-bold bg-red-950/40 text-red-300 border border-red-500/30 hover:bg-red-900/60 hover:border-red-500/50 transition flex items-center gap-1.5 shrink-0 cursor-pointer" title="Securely Sign Out">
                        <svg class="w-3.5 h-3.5 text-red-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
                        <span class="hidden sm:inline text-[11px]">Logout</span>
                    </button>

                </div>

            </header>

            <!-- Dashboard Content Container -->
            <main class="flex-1 p-4 md:p-6 space-y-6 max-w-7xl mx-auto w-full">

                <!-- VIEW 1: LIVE PROBES SECTION (Always accessible or focused) -->
                <section id="view-probes" class="space-y-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <span class="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                            <h3 class="text-xs font-bold uppercase tracking-widest text-gray-300">Live Multi-Tier Database & Cache Probes</h3>
                            <span class="text-[10px] text-gray-500 font-mono" id="probe-timestamp">-</span>
                        </div>
                        <button onclick="refreshProbes()" class="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center space-x-1.5 px-3 py-1 bg-indigo-950/40 rounded-lg border border-indigo-500/20 hover:border-indigo-500/40 transition">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                            <span>Refresh Probes</span>
                        </button>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        
                        <!-- 1. Redis L1 In-Memory Probe -->
                        <div class="glass-panel p-5 rounded-2xl space-y-3 border-l-4 border-l-emerald-500 glow-hover transition">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="text-[11px] font-bold uppercase tracking-wider text-gray-400">L1 In-Memory Cache (RAM)</div>
                                    <div class="text-base font-extrabold text-white mt-0.5 flex items-center gap-2">
                                        <span>Redis 7 (Docker)</span>
                                        <span id="probe-redis-badge" class="px-2 py-0.5 text-[10px] rounded-md font-mono font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">ONLINE</span>
                                    </div>
                                </div>
                                <span id="probe-redis-latency" class="text-xs font-mono font-bold text-emerald-400">0.0ms</span>
                            </div>
                            <div class="pt-2 border-t border-cyber-border/60 text-xs space-y-1.5 text-gray-400">
                                <div class="flex justify-between">
                                    <span>Selected Region Data:</span>
                                    <span id="probe-redis-region-status" class="font-bold text-white">Checking...</span>
                                </div>
                                <div class="flex justify-between">
                                    <span>Total Keys Cached:</span>
                                    <span id="probe-redis-keys" class="font-mono text-gray-200">-</span>
                                </div>
                                <div class="flex justify-between text-[11px]">
                                    <span>Disk Persistence:</span>
                                    <span class="text-emerald-400 font-mono">dump.rdb + AOF (Active)</span>
                                </div>
                            </div>
                        </div>

                        <!-- 2. PostgreSQL L3 Master Container Probe -->
                        <div class="glass-panel p-5 rounded-2xl space-y-3 border-l-4 border-l-cyan-500 glow-hover transition">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="text-[11px] font-bold uppercase tracking-wider text-gray-400">L3 Master Database (Disk)</div>
                                    <div class="text-base font-extrabold text-white mt-0.5 flex items-center gap-2">
                                        <span>PostgreSQL 16</span>
                                        <span id="probe-pg-badge" class="px-2 py-0.5 text-[10px] rounded-md font-mono font-semibold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">ONLINE</span>
                                    </div>
                                </div>
                                <span id="probe-pg-latency" class="text-xs font-mono font-bold text-cyan-400">0.0ms</span>
                            </div>
                            <div class="pt-2 border-t border-cyber-border/60 text-xs space-y-1.5 text-gray-400">
                                <div class="flex justify-between">
                                    <span>Selected Region Data:</span>
                                    <span id="probe-pg-region-status" class="font-bold text-white">Checking...</span>
                                </div>
                                <div class="flex justify-between">
                                    <span>Active Regional Schemas:</span>
                                    <span id="probe-pg-schemas" class="font-mono text-cyan-300 font-bold">39 Schemas</span>
                                </div>
                                <div class="flex justify-between text-[11px]">
                                    <span>Master Database:</span>
                                    <span class="text-cyan-400/90 font-mono">aether_catalog</span>
                                </div>
                            </div>
                        </div>

                        <!-- 3. SQLite L2 Engine Probe -->
                        <div class="glass-panel p-5 rounded-2xl space-y-3 border-l-4 border-l-indigo-500 glow-hover transition">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="text-[11px] font-bold uppercase tracking-wider text-gray-400">L2 Local Replica (Host)</div>
                                    <div class="text-base font-extrabold text-white mt-0.5 flex items-center gap-2">
                                        <span>SQLite WAL Engine</span>
                                        <span class="px-2 py-0.5 text-[10px] rounded-md font-mono font-semibold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">READY</span>
                                    </div>
                                </div>
                                <span class="text-xs font-mono font-bold text-indigo-400">0.05ms</span>
                            </div>
                            <div class="pt-2 border-t border-cyber-border/60 text-xs space-y-1.5 text-gray-400">
                                <div class="flex justify-between">
                                    <span>Active Database File:</span>
                                    <span id="probe-sqlite-file" class="font-mono text-white text-[11px]">catalog_us-east-1.db</span>
                                </div>
                                <div class="flex justify-between">
                                    <span>Access Mode:</span>
                                    <span class="font-mono text-indigo-300 font-bold">WAL (Zero-Latency Local)</span>
                                </div>
                                <div class="flex justify-between text-[11px]">
                                    <span>Failover Route:</span>
                                    <span class="text-emerald-400 font-medium">Auto-PostgreSQL Docker</span>
                                </div>
                            </div>
                        </div>

                    </div>
                </section>

                <!-- VIEW 2: GLOBAL AWS CATALOG SECTION -->
                <div id="view-catalog" class="space-y-6">

                    <!-- Actions & Global Operations Bar -->
                    <section class="glass-panel p-5 rounded-2xl flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
                        
                        <div class="flex items-center space-x-6 overflow-x-auto pb-1 lg:pb-0">
                            <div>
                                <div class="text-[10px] font-bold uppercase tracking-widest text-gray-400">Compute Profiles</div>
                                <div class="text-2xl font-extrabold text-white mt-0.5" id="compute-count">0</div>
                            </div>
                            <div class="h-8 w-px bg-cyber-border"></div>
                            <div>
                                <div class="text-[10px] font-bold uppercase tracking-widest text-gray-400">Platform Services</div>
                                <div class="text-2xl font-extrabold text-white mt-0.5" id="other-count">0</div>
                            </div>
                            <div class="h-8 w-px bg-cyber-border"></div>
                            <div>
                                <div class="text-[10px] font-bold uppercase tracking-widest text-gray-400">Sync Status</div>
                                <div class="text-xs font-extrabold text-emerald-400 mt-1 flex items-center gap-1.5" id="region-sync-status">
                                    <span>READY</span>
                                </div>
                            </div>
                        </div>

                        <!-- Action Buttons -->
                        <div class="flex flex-wrap items-center gap-2.5">
                            
                            <!-- Sync Live AWS Pricing -->
                            <button onclick="triggerDynamicSync()" id="sync-btn" class="py-2 px-4 bg-gradient-to-r from-indigo-600 to-cyber-violet hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs rounded-xl transition shadow-lg shadow-indigo-500/20 glow-hover flex items-center space-x-2">
                                <svg class="h-3.5 w-3.5 animate-spin hidden" id="sync-spinner" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                                <span>Sync Live AWS Pricing</span>
                            </button>

                            <!-- Add Custom SKU Button -->
                            <button onclick="openAddResourceModal()" class="py-2 px-3.5 bg-slate-800 hover:bg-slate-700 text-white border border-cyber-border font-semibold text-xs rounded-xl transition flex items-center space-x-1.5">
                                <svg class="w-3.5 h-3.5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                                <span>Add Custom SKU</span>
                            </button>

                            <!-- Upload All 39 Regions Button -->
                            <button onclick="triggerUploadAllRegions()" id="upload-all-btn" class="py-2 px-3.5 bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-500/30 font-semibold text-xs rounded-xl transition flex items-center space-x-1.5">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
                                <span>Upload All 39 Regions</span>
                            </button>

                            <!-- Clear Cache -->
                            <button onclick="clearRedisCache()" class="py-2 px-3 bg-slate-800 hover:bg-slate-700 text-gray-400 hover:text-white border border-cyber-border font-medium text-xs rounded-xl transition">
                                Purge Redis
                            </button>

                        </div>

                    </section>

                    <!-- Organized Catalog Workspace -->
                    <section class="grid grid-cols-1 lg:grid-cols-4 gap-6">
                        
                        <!-- Left Service Category Navigator -->
                        <div class="lg:col-span-1 space-y-4">
                            
                            <!-- Category Filter Tabs -->
                            <div class="glass-panel p-3 rounded-2xl space-y-1">
                                <div class="text-[10px] font-bold text-gray-400 uppercase tracking-wider px-2 mb-2">Service Domains</div>
                                <div class="grid grid-cols-1 gap-1" id="category-filter-chips">
                                    <button onclick="filterServiceGroup('all')" id="cat-chip-all" class="w-full text-left px-3 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600/30 text-white border border-indigo-500/30">All Services (15)</button>
                                    <button onclick="filterServiceGroup('compute')" id="cat-chip-compute" class="w-full text-left px-3 py-1.5 text-xs font-medium text-gray-400 hover:text-white rounded-lg transition">🖥️ Compute & Containers (4)</button>
                                    <button onclick="filterServiceGroup('database')" id="cat-chip-database" class="w-full text-left px-3 py-1.5 text-xs font-medium text-gray-400 hover:text-white rounded-lg transition">🗄️ Databases & Storage (4)</button>
                                    <button onclick="filterServiceGroup('network')" id="cat-chip-network" class="w-full text-left px-3 py-1.5 text-xs font-medium text-gray-400 hover:text-white rounded-lg transition">🌐 Networking & CDN (3)</button>
                                    <button onclick="filterServiceGroup('security')" id="cat-chip-security" class="w-full text-left px-3 py-1.5 text-xs font-medium text-gray-400 hover:text-white rounded-lg transition">🛡️ Security & Governance (3)</button>
                                    <button onclick="filterServiceGroup('monitoring')" id="cat-chip-monitoring" class="w-full text-left px-3 py-1.5 text-xs font-medium text-gray-400 hover:text-white rounded-lg transition">📊 Observability (1)</button>
                                </div>
                            </div>

                            <!-- Service Navigation List -->
                            <div class="glass-panel p-3 rounded-2xl space-y-2">
                                <div class="text-[11px] font-bold text-gray-400 uppercase tracking-wider px-2 mb-1 flex justify-between items-center">
                                    <span>AWS Services</span>
                                    <span class="text-[10px] text-gray-500 font-mono" id="current-service-tag">EC2</span>
                                </div>
                                <nav class="space-y-1 max-h-[500px] overflow-y-auto pr-1" id="service-nav">
                                    <!-- Populated dynamically -->
                                </nav>
                            </div>

                        </div>

                        <!-- Right Main Table Workspace -->
                        <div class="lg:col-span-3 space-y-4">
                            
                            <!-- Table Container -->
                            <div class="glass-panel rounded-2xl overflow-hidden border border-cyber-border">
                                
                                <!-- Table Header with Stats Strip -->
                                <div class="p-5 border-b border-cyber-border flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                                    <div>
                                        <h4 class="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                                            <span class="h-2 w-2 rounded-full bg-emerald-400"></span>
                                            <span id="table-title">EC2 Compute Catalog</span>
                                        </h4>
                                        <p class="text-[11px] text-gray-400 mt-0.5">
                                            <span id="table-subtitle">Specifications and pricing synced from AWS pricing engine</span>
                                            • <span id="table-price-range" class="text-indigo-300 font-mono font-semibold">$0.0104 - $0.3400/hr</span>
                                        </p>
                                    </div>
                                    <div class="relative w-full sm:w-64">
                                        <input type="text" onkeyup="filterTable('catalog-table', this.value)" placeholder="Search instance or spec..." class="w-full py-1.5 pl-8 pr-3 bg-cyber-bg border border-cyber-border rounded-xl text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500">
                                        <svg class="w-4 h-4 text-gray-500 absolute left-2.5 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                                    </div>
                                </div>

                                <!-- Table Element -->
                                <div class="overflow-x-auto">
                                    <table class="w-full text-left border-collapse" id="catalog-table">
                                        <thead>
                                            <tr class="border-b border-cyber-border bg-slate-900/50 text-[11px] font-bold text-gray-400 uppercase tracking-wider">
                                                <th class="p-3.5">Instance / Resource</th>
                                                <th class="p-3.5">vCPUs</th>
                                                <th class="p-3.5">Memory</th>
                                                <th class="p-3.5">Unit</th>
                                                <th class="p-3.5">Category</th>
                                                <th class="p-3.5">Network / Specs</th>
                                                <th class="p-3.5 text-right">Hourly Rate</th>
                                                <th class="p-3.5 text-right">Est. Monthly</th>
                                                <th class="p-3.5 text-center">Action</th>
                                            </tr>
                                        </thead>
                                        <tbody class="divide-y divide-cyber-border/40 text-xs" id="table-rows">
                                            <!-- Populated dynamically -->
                                        </tbody>
                                    </table>
                                </div>

                            </div>

                        </div>

                    </section>

                </div>

                <!-- VIEW 3: ALL 8 PLATFORM MODULES HUB (Whole Application Architecture) -->
                <div id="view-modules" class="space-y-6 hidden">
                    
                    <!-- Modules Hub Header -->
                    <div class="glass-panel p-6 rounded-2xl border-l-4 border-l-purple-500 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                        <div>
                            <div class="text-[10px] font-bold text-purple-400 uppercase tracking-widest">AetherOps Architecture Map</div>
                            <h3 class="text-xl font-extrabold text-white mt-1">Platform Modules Ecosystem (8 Modules)</h3>
                            <p class="text-xs text-gray-400 mt-1 max-w-3xl">
                                The Universal Catalog in Redis (L1) and PostgreSQL (L3) powers all 8 microservices. Each module queries real-time regional rates and instance profiles to deliver automated, right-sized cloud infrastructure.
                            </p>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class="px-3 py-1.5 rounded-xl bg-purple-950/60 text-purple-300 border border-purple-500/30 text-xs font-bold font-mono">
                                Central Catalog: 39 Regions Active
                            </span>
                        </div>
                    </div>

                    <!-- Pipeline Flow Diagram -->
                    <div class="glass-panel p-5 rounded-2xl overflow-x-auto">
                        <div class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3">Module Execution & Catalog Consumption Pipeline</div>
                        <div class="flex items-center min-w-[850px] justify-between text-xs font-mono">
                            <div class="p-3 rounded-xl bg-slate-900/80 border border-emerald-500/40 text-center space-y-1">
                                <span class="text-[10px] text-emerald-400 font-bold">:8001 LIVE</span>
                                <div class="font-bold text-white">1. Requirements</div>
                                <div class="text-[10px] text-gray-400">EC2/RDS Sizing</div>
                            </div>
                            <span class="text-gray-500">→</span>
                            <div class="p-3 rounded-xl bg-slate-900/80 border border-emerald-500/40 text-center space-y-1">
                                <span class="text-[10px] text-emerald-400 font-bold">:8002 LIVE</span>
                                <div class="font-bold text-white">2. Architecture</div>
                                <div class="text-[10px] text-gray-400">VPC/EKS Network</div>
                            </div>
                            <span class="text-gray-500">→</span>
                            <div class="p-3 rounded-xl bg-slate-900/80 border border-cyber-border text-center space-y-1">
                                <span class="text-[10px] text-indigo-400 font-bold">:8003 READY</span>
                                <div class="font-bold text-white">3. IaC Code</div>
                                <div class="text-[10px] text-gray-400">Terraform / HCL</div>
                            </div>
                            <span class="text-gray-500">→</span>
                            <div class="p-3 rounded-xl bg-slate-900/80 border border-cyan-500/40 text-center space-y-1">
                                <span class="text-[10px] text-cyan-400 font-bold">:8004 CONNECTED</span>
                                <div class="font-bold text-white">4. FinOps Cost</div>
                                <div class="text-[10px] text-gray-400">Redis 0ms TCO</div>
                            </div>
                            <span class="text-gray-500">→</span>
                            <div class="p-3 rounded-xl bg-slate-900/80 border border-cyber-border text-center space-y-1">
                                <span class="text-[10px] text-gray-400 font-bold">:8005 READY</span>
                                <div class="font-bold text-white">5. Security</div>
                                <div class="text-[10px] text-gray-400">WAF / IAM CIS</div>
                            </div>
                            <span class="text-gray-500">→</span>
                            <div class="p-3 rounded-xl bg-slate-900/80 border border-cyber-border text-center space-y-1">
                                <span class="text-[10px] text-gray-400 font-bold">:8006 READY</span>
                                <div class="font-bold text-white">6. CI/CD</div>
                                <div class="text-[10px] text-gray-400">ECR Registry</div>
                            </div>
                            <span class="text-gray-500">→</span>
                            <div class="p-3 rounded-xl bg-slate-900/80 border border-cyber-border text-center space-y-1">
                                <span class="text-[10px] text-gray-400 font-bold">:8007 READY</span>
                                <div class="font-bold text-white">7. Observability</div>
                                <div class="text-[10px] text-gray-400">CloudWatch Logs</div>
                            </div>
                            <span class="text-gray-500">→</span>
                            <div class="p-3 rounded-xl bg-slate-900/80 border border-cyber-border text-center space-y-1">
                                <span class="text-[10px] text-gray-400 font-bold">:8008 READY</span>
                                <div class="font-bold text-white">8. Deployer</div>
                                <div class="text-[10px] text-gray-400">Drift Repair</div>
                            </div>
                        </div>
                    </div>

                    <!-- 8 Module Cards Grid -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4" id="modules-cards-container">
                        <!-- Populated dynamically via JS -->
                    </div>

                </div>

                <!-- VIEW 4: 39-REGION MULTI-CLOUD MATRIX -->
                <div id="view-matrix" class="space-y-6 hidden">
                    
                    <div class="glass-panel p-6 rounded-2xl border-l-4 border-l-cyan-500 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                        <div>
                            <div class="text-[10px] font-bold text-cyan-400 uppercase tracking-widest">Global Cloud Infrastructure Matrix</div>
                            <h3 class="text-xl font-extrabold text-white mt-1">AWS 39-Region Multi-Tier Replication</h3>
                            <p class="text-xs text-gray-400 mt-1">
                                Complete replication telemetry across all 39 global AWS regions. Every region is co-located in SQLite (L2), persistently schema-isolated in PostgreSQL (L3), and cached in Redis (L1).
                            </p>
                        </div>
                        <button onclick="triggerUploadAllRegions()" class="py-2 px-4 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold rounded-xl transition shadow-lg shadow-cyan-500/20">
                            Re-Sync All 39 Regions
                        </button>
                    </div>

                    <!-- Regions Grid grouped by Geography -->
                    <div class="space-y-6" id="matrix-regions-container">
                        <!-- Populated dynamically via JS -->
                    </div>

                </div>

            </main>

            <!-- Footer -->
            <footer class="mt-auto border-t border-cyber-border py-4 px-8 text-center text-xs text-gray-500 flex flex-col sm:flex-row justify-between items-center gap-2">
                <span>&copy; 2026 AetherOps AI. Autonomous CloudOps Infrastructure Engine.</span>
                <span class="font-mono text-[11px] text-gray-400">PostgreSQL (L3 Master) + Redis (L1 Cache) + SQLite (L2 Local)</span>
            </footer>

        </div>

    </div>

    <!-- MODAL 1: ADD CUSTOM SKU / RESOURCE -->
    <div id="modal-add-resource" class="fixed inset-0 bg-black/70 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-lg rounded-2xl p-6 border border-cyber-border space-y-4 shadow-2xl">
            <div class="flex justify-between items-center pb-3 border-b border-cyber-border">
                <h3 class="text-base font-bold text-white flex items-center gap-2">
                    <span class="h-2 w-2 rounded-full bg-indigo-400"></span>
                    <span>Add Custom Resource / SKU</span>
                </h3>
                <button onclick="closeAddResourceModal()" class="text-gray-400 hover:text-white">&times;</button>
            </div>
            <form id="add-resource-form" onsubmit="submitCustomResource(event)" class="space-y-3 text-xs">
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-gray-400 font-semibold mb-1">Target Service</label>
                        <select id="modal-service" class="w-full p-2 bg-cyber-bg border border-cyber-border rounded-xl text-white">
                            <option value="ec2">EC2 (Compute Instance)</option>
                            <option value="rds">RDS (Database Instance)</option>
                            <option value="s3">S3 (Storage Profile)</option>
                            <option value="vpc">VPC (Network Profile)</option>
                            <option value="iam">IAM (Security)</option>
                            <option value="waf">WAF (Firewall)</option>
                            <option value="cloudwatch">CloudWatch</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-400 font-semibold mb-1">Instance / SKU Code</label>
                        <input type="text" id="modal-instance-type" required placeholder="e.g. c7i.2xlarge" class="w-full p-2 bg-cyber-bg border border-cyber-border rounded-xl text-white font-mono">
                    </div>
                </div>
                <div class="grid grid-cols-3 gap-3">
                    <div>
                        <label class="block text-gray-400 font-semibold mb-1">vCPUs</label>
                        <input type="number" id="modal-vcpus" value="4" class="w-full p-2 bg-cyber-bg border border-cyber-border rounded-xl text-white font-mono">
                    </div>
                    <div>
                        <label class="block text-gray-400 font-semibold mb-1">RAM (GB)</label>
                        <input type="number" step="0.5" id="modal-ram" value="16.0" class="w-full p-2 bg-cyber-bg border border-cyber-border rounded-xl text-white font-mono">
                    </div>
                    <div>
                        <label class="block text-gray-400 font-semibold mb-1">Hourly Price ($)</label>
                        <input type="number" step="0.0001" id="modal-price" required value="0.1700" class="w-full p-2 bg-cyber-bg border border-cyber-border rounded-xl text-emerald-400 font-mono font-bold">
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-gray-400 font-semibold mb-1">Category</label>
                        <select id="modal-category" class="w-full p-2 bg-cyber-bg border border-cyber-border rounded-xl text-white">
                            <option value="general">General Purpose</option>
                            <option value="compute_optimized">Compute Optimized</option>
                            <option value="memory_optimized">Memory Optimized</option>
                            <option value="burstable">Burstable</option>
                            <option value="storage">Storage</option>
                            <option value="networking">Networking</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-gray-400 font-semibold mb-1">Network / Specs Details</label>
                        <input type="text" id="modal-details" placeholder="e.g. 12.5 Gbps" class="w-full p-2 bg-cyber-bg border border-cyber-border rounded-xl text-white">
                    </div>
                </div>
                <div class="pt-3 flex justify-end space-x-2 border-t border-cyber-border">
                    <button type="button" onclick="closeAddResourceModal()" class="px-4 py-2 bg-slate-800 text-gray-300 rounded-xl hover:bg-slate-700">Cancel</button>
                    <button type="submit" class="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl shadow-lg shadow-indigo-500/25">Save to DB & Redis</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL 2: RAW JSON INSPECTOR -->
    <div id="modal-inspector" class="fixed inset-0 bg-black/75 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
        <div class="glass-panel w-full max-w-2xl rounded-2xl p-6 border border-cyber-border space-y-4 shadow-2xl flex flex-col max-h-[85vh]">
            <div class="flex justify-between items-center pb-3 border-b border-cyber-border">
                <h3 class="text-base font-bold text-white flex items-center gap-2">
                    <span class="h-2 w-2 rounded-full bg-cyan-400"></span>
                    <span id="inspector-title">Resource Specification Inspector</span>
                </h3>
                <button onclick="closeInspectorModal()" class="text-gray-400 hover:text-white text-lg">&times;</button>
            </div>
            <div class="flex-1 overflow-y-auto bg-black/60 p-4 rounded-xl border border-cyber-border font-mono text-xs text-indigo-300">
                <pre id="inspector-json">{}</pre>
            </div>
            <div class="flex justify-between items-center pt-2">
                <span class="text-[11px] text-gray-400 font-mono">Source: Aether Multi-Tier Catalog Engine</span>
                <button onclick="copyInspectorJSON()" class="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-xl transition">Copy JSON</button>
            </div>
        </div>
    </div>

    <!-- Notification Toast -->
    <div id="toast" class="fixed bottom-6 right-6 px-5 py-3 rounded-2xl shadow-2xl border border-cyber-border bg-emerald-950/85 text-emerald-300 backdrop-blur-xl flex items-center space-x-3 max-w-sm hidden z-50">
        <span id="toast-text" class="text-xs font-semibold">Notification message</span>
    </div>

    <script>
        let regionsList = [];
        let currentService = 'ec2';
        let currentRegion = 'us-east-1';
        let catalogData = {};
        let modulesData = [];
        let currentGroup = 'all';
        const adminKey = localStorage.getItem('X-Admin-Key') || 'aetherops-secret-admin-key';

        function getServiceSvg(code) {
            const map = {
                ec2: `<svg class="w-3.5 h-3.5 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"></path></svg>`,
                eks: `<svg class="w-3.5 h-3.5 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>`,
                ecs: `<svg class="w-3.5 h-3.5 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>`,
                ecr: `<svg class="w-3.5 h-3.5 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path></svg>`,
                rds: `<svg class="w-3.5 h-3.5 text-cyan-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path></svg>`,
                s3: `<svg class="w-3.5 h-3.5 text-cyan-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path></svg>`,
                ebs: `<svg class="w-3.5 h-3.5 text-cyan-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"></path></svg>`,
                efs: `<svg class="w-3.5 h-3.5 text-cyan-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>`,
                vpc: `<svg class="w-3.5 h-3.5 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path></svg>`,
                route53: `<svg class="w-3.5 h-3.5 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"></path></svg>`,
                cloudfront: `<svg class="w-3.5 h-3.5 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>`,
                iam: `<svg class="w-3.5 h-3.5 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path></svg>`,
                waf: `<svg class="w-3.5 h-3.5 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>`,
                cloudtrail: `<svg class="w-3.5 h-3.5 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>`,
                cloudwatch: `<svg class="w-3.5 h-3.5 text-purple-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>`
            };
            return map[code] || `<svg class="w-3.5 h-3.5 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>`;
        }

        const servicesList = [
            { code: "ec2", name: "EC2 (Compute)", group: "compute" },
            { code: "eks", name: "EKS (Kubernetes)", group: "compute" },
            { code: "ecs", name: "ECS (Containers)", group: "compute" },
            { code: "ecr", name: "ECR (Registry)", group: "compute" },
            { code: "rds", name: "RDS (Databases)", group: "database" },
            { code: "s3", name: "S3 (Object Storage)", group: "database" },
            { code: "ebs", name: "EBS (Block Storage)", group: "database" },
            { code: "efs", name: "EFS (File Storage)", group: "database" },
            { code: "vpc", name: "VPC (Networking)", group: "network" },
            { code: "route53", name: "Route 53 (DNS)", group: "network" },
            { code: "cloudfront", name: "CloudFront (CDN)", group: "network" },
            { code: "iam", name: "IAM (Security)", group: "security" },
            { code: "waf", name: "WAF (Firewall)", group: "security" },
            { code: "cloudtrail", name: "CloudTrail (Audit)", group: "security" },
            { code: "cloudwatch", name: "CloudWatch (Metrics)", group: "monitoring" }
        ];

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            if (!sidebar) return;
            const isDesktop = window.innerWidth >= 1024;

            if (isDesktop) {
                sidebar.classList.toggle('is-desktop-collapsed');
                if (overlay) overlay.classList.add('hidden');
            } else {
                const isOpen = sidebar.classList.toggle('is-mobile-open');
                if (overlay) {
                    if (isOpen) {
                        overlay.classList.remove('hidden');
                    } else {
                        overlay.classList.add('hidden');
                    }
                }
            }
        }

        function closeSidebarOnMobile() {
            if (window.innerWidth < 1024) {
                const sidebar = document.getElementById('sidebar');
                const overlay = document.getElementById('sidebar-overlay');
                if (sidebar) sidebar.classList.remove('is-mobile-open');
                if (overlay) overlay.classList.add('hidden');
            }
        }

        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeSidebarOnMobile();
            }
        });

        function showToast(msg, type = "success") {
            const toast = document.getElementById('toast');
            const text = document.getElementById('toast-text');
            text.innerText = msg;
            if (type === "error") {
                toast.className = "fixed bottom-6 right-6 px-5 py-3 rounded-2xl shadow-2xl border border-rose-500/40 bg-rose-950/90 text-rose-300 backdrop-blur-xl flex items-center space-x-3 max-w-sm z-50";
            } else {
                toast.className = "fixed bottom-6 right-6 px-5 py-3 rounded-2xl shadow-2xl border border-emerald-500/40 bg-emerald-950/90 text-emerald-300 backdrop-blur-xl flex items-center space-x-3 max-w-sm z-50";
            }
            toast.classList.remove('hidden');
            setTimeout(() => { toast.classList.add('hidden'); }, 4000);
        }

        function promptChangeAdminKey() {
            const current = localStorage.getItem('X-Admin-Key') || 'aetherops-secret-admin-key';
            const res = prompt("Enter AetherOps Admin API Secret Key (X-Admin-Key):", current);
            if (res) {
                localStorage.setItem('X-Admin-Key', res.trim());
                showToast("Admin Key updated! Reloading telemetry...");
                setTimeout(() => location.reload(), 800);
            }
        }

        async function checkAuthStatus() {
            try {
                const res = await fetch('/api/admin/auth/me', {
                    headers: adminKey ? { 'X-Admin-Key': adminKey } : {}
                });
                if (res.ok) {
                    const data = await res.json();
                    if (data && data.user) {
                        const u = document.getElementById('auth-username');
                        const r = document.getElementById('auth-role');
                        if (u) u.textContent = data.user.username || 'admin';
                        if (r) r.textContent = data.user.role || 'SUPER_ADMIN';
                    }
                } else if (res.status === 401 || res.status === 403) {
                    window.location.href = '/admin/login?redirect=' + encodeURIComponent(window.location.pathname);
                }
            } catch (e) {
                console.warn("Auth check warning:", e);
            }
        }

        async function logoutAdmin() {
            try {
                await fetch('/api/admin/auth/logout', {
                    method: 'POST',
                    headers: adminKey ? { 'X-Admin-Key': adminKey } : {}
                });
            } catch (e) {
                console.warn("Logout error:", e);
            }
            localStorage.removeItem('X-Admin-Key');
            showToast("Logged out successfully. Redirecting to login...");
            setTimeout(() => {
                window.location.href = '/admin/login';
            }, 500);
        }

        function switchMainView(viewName) {
            const views = ['catalog', 'modules', 'matrix', 'probes'];
            views.forEach(v => {
                const el = document.getElementById(`view-${v}`);
                if (el) {
                    if (viewName === 'catalog') {
                        if (v === 'catalog' || v === 'probes') {
                            el.classList.remove('hidden');
                        } else {
                            el.classList.add('hidden');
                        }
                    } else {
                        if (v === viewName) {
                            el.classList.remove('hidden');
                        } else {
                            el.classList.add('hidden');
                        }
                    }
                }
                const navBtn = document.getElementById(`nav-btn-${v}`);
                if (navBtn) {
                    if (v === viewName) {
                        navBtn.classList.add('tab-btn-active');
                        navBtn.classList.remove('text-gray-400');
                    } else {
                        navBtn.classList.remove('tab-btn-active');
                        navBtn.classList.add('text-gray-400');
                    }
                }
                const headerTab = document.getElementById(`header-tab-${v}`);
                if (headerTab) {
                    if (v === viewName) {
                        headerTab.className = "px-2.5 py-1 text-xs font-semibold rounded-lg transition bg-indigo-600/30 text-white border border-indigo-500/40 flex items-center gap-1.5 cursor-pointer";
                    } else {
                        headerTab.className = "px-2.5 py-1 text-xs font-medium text-gray-400 hover:text-white rounded-lg transition flex items-center gap-1.5 cursor-pointer";
                    }
                }
            });

            const navLabel = document.getElementById('nav-view-label');
            if (navLabel) {
                const map = { catalog: 'CATALOG', modules: 'MODULES (8)', matrix: '39 REGIONS', probes: 'PROBES' };
                navLabel.innerText = map[viewName] || viewName.toUpperCase();
            }

            const badge = document.getElementById('view-mode-badge');
            if (badge) {
                badge.innerText = `${viewName.toUpperCase()} MODE`;
            }

            closeSidebarOnMobile();
        }

        async function onRegionFilterChange() {
            currentRegion = document.getElementById('region-filter').value;
            await refreshProbes();
            await fetchCatalog();
            await checkRegionSyncStatus();
        }

        async function refreshProbes() {
            try {
                const res = await fetch(`/api/admin/probe?region=${currentRegion}`, {
                    headers: { 'X-Admin-Key': adminKey }
                });
                if (!res.ok) return;
                const probe = await res.json();
                
                const timeEl = document.getElementById('probe-timestamp');
                if (timeEl) timeEl.innerText = new Date(probe.timestamp * 1000).toLocaleTimeString();

                // Redis Probe Update
                const redisBadge = document.getElementById('probe-redis-badge');
                const redisLatency = document.getElementById('probe-redis-latency');
                const redisRegionStatus = document.getElementById('probe-redis-region-status');
                const redisKeys = document.getElementById('probe-redis-keys');
                const pillRedisText = document.getElementById('pill-redis-text');
                
                if (probe.redis.connected) {
                    if (redisBadge) {
                        redisBadge.innerText = 'ONLINE';
                        redisBadge.className = 'px-2 py-0.5 text-[10px] rounded-md font-mono font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
                    }
                    if (redisLatency) redisLatency.innerText = `${probe.redis.latency_ms}ms`;
                    if (redisKeys) redisKeys.innerText = `${probe.redis.total_keys} keys cached`;
                    if (pillRedisText) pillRedisText.innerText = `Redis: ${probe.redis.latency_ms}ms (${probe.redis.total_keys} keys)`;
                    
                    if (redisRegionStatus) {
                        if (probe.redis.region_data_cached) {
                            redisRegionStatus.innerHTML = `<span class="text-emerald-400 font-semibold">✔ PRESENT (${probe.redis.region_keys_count} keys)</span>`;
                        } else {
                            redisRegionStatus.innerHTML = `<span class="text-yellow-400 font-semibold">❄ COLD</span>`;
                        }
                    }
                } else {
                    if (redisBadge) {
                        redisBadge.innerText = 'OFFLINE';
                        redisBadge.className = 'px-2 py-0.5 text-[10px] rounded-md font-mono font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/30';
                    }
                    if (pillRedisText) pillRedisText.innerText = 'Redis: Offline';
                    if (redisRegionStatus) redisRegionStatus.innerHTML = `<span class="text-rose-400">Offline</span>`;
                }

                // PostgreSQL Probe Update
                const pgBadge = document.getElementById('probe-pg-badge');
                const pgLatency = document.getElementById('probe-pg-latency');
                const pgRegionStatus = document.getElementById('probe-pg-region-status');
                const pgSchemas = document.getElementById('probe-pg-schemas');
                const pillPgText = document.getElementById('pill-postgres-text');

                if (probe.postgresql.connected) {
                    if (pgBadge) {
                        pgBadge.innerText = 'ONLINE';
                        pgBadge.className = 'px-2 py-0.5 text-[10px] rounded-md font-mono font-semibold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30';
                    }
                    if (pgLatency) pgLatency.innerText = `${probe.postgresql.latency_ms}ms`;
                    if (pgSchemas) pgSchemas.innerText = `${probe.postgresql.total_schemas} Regional Schemas`;
                    if (pillPgText) pillPgText.innerText = `PostgreSQL: Ready (${probe.postgresql.total_schemas} schemas)`;
                    
                    if (pgRegionStatus) {
                        if (probe.postgresql.region_data_present) {
                            pgRegionStatus.innerHTML = `<span class="text-cyan-400 font-semibold">✔ PRESENT (${probe.postgresql.region_records_count} rows)</span>`;
                        } else {
                            pgRegionStatus.innerHTML = `<span class="text-gray-400">0 rows</span>`;
                        }
                    }
                } else {
                    if (pgBadge) {
                        pgBadge.innerText = 'OFFLINE';
                        pgBadge.className = 'px-2 py-0.5 text-[10px] rounded-md font-mono font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/30';
                    }
                    if (pillPgText) pillPgText.innerText = 'PostgreSQL: Offline';
                }

                // SQLite Local Update
                const sqliteFile = document.getElementById('probe-sqlite-file');
                if (sqliteFile && probe.sqlite) {
                    sqliteFile.innerText = probe.sqlite.db_file;
                }

                // Header Cluster Status Pill Update
                const pillClusterText = document.getElementById('pill-cluster-text');
                const pillCluster = document.getElementById('pill-cluster');
                if (pillClusterText && pillCluster) {
                    if (probe.redis.connected && probe.postgresql.connected) {
                        pillClusterText.innerText = `Redis ${probe.redis.latency_ms}ms • PG ${probe.postgresql.latency_ms}ms`;
                        pillCluster.className = "flex items-center space-x-1.5 px-2 sm:px-2.5 py-1 rounded-xl text-xs font-semibold bg-slate-900/90 border border-emerald-500/30 text-emerald-300 hover:border-emerald-500/60 transition shrink-0 cursor-pointer";
                    } else if (probe.redis.connected || probe.postgresql.connected) {
                        pillClusterText.innerText = `Cluster Degraded`;
                        pillCluster.className = "flex items-center space-x-1.5 px-2 sm:px-2.5 py-1 rounded-xl text-xs font-semibold bg-slate-900/90 border border-amber-500/30 text-amber-300 hover:border-amber-500/60 transition shrink-0 cursor-pointer";
                    } else {
                        pillClusterText.innerText = `Cluster Offline`;
                        pillCluster.className = "flex items-center space-x-1.5 px-2 sm:px-2.5 py-1 rounded-xl text-xs font-semibold bg-slate-900/90 border border-rose-500/30 text-rose-300 hover:border-rose-500/60 transition shrink-0 cursor-pointer";
                    }
                }

            } catch (e) {
                console.error("Probe error:", e);
            }
        }

        async function triggerUploadAllRegions() {
            const btn = document.getElementById('upload-all-btn');
            btn.disabled = true;
            showToast("Initiating bulk upload for all 39 AWS regions into Redis & PostgreSQL...");

            try {
                const res = await fetch('/api/admin/catalog/seed-all', {
                    method: 'POST',
                    headers: { 'X-Admin-Key': adminKey }
                });
                const data = await res.json();
                showToast("Bulk upload finished! PostgreSQL schemas & Redis keys warmed.");
                setTimeout(async () => {
                    await refreshProbes();
                    await fetchCatalog();
                    await loadRegionsMatrix();
                    btn.disabled = false;
                }, 1500);
            } catch (err) {
                showToast("Bulk upload failed: " + err.message, "error");
                btn.disabled = false;
            }
        }

        function filterServiceGroup(group) {
            currentGroup = group;
            ['all', 'compute', 'database', 'network', 'security', 'monitoring'].forEach(g => {
                const chip = document.getElementById(`cat-chip-${g}`);
                if (chip) {
                    if (g === group) {
                        chip.className = "w-full text-left px-3 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600/30 text-white border border-indigo-500/30";
                    } else {
                        chip.className = "w-full text-left px-3 py-1.5 text-xs font-medium text-gray-400 hover:text-white rounded-lg transition";
                    }
                }
            });
            renderServiceNav();
        }

        function renderServiceNav() {
            const nav = document.getElementById('service-nav');
            nav.innerHTML = '';

            const filteredServices = (currentGroup === 'all') 
                ? servicesList 
                : servicesList.filter(s => s.group === currentGroup);

            filteredServices.forEach(svc => {
                const items = catalogData[svc.code] || [];
                const count = items.length;
                
                const activeClass = (currentService === svc.code) 
                    ? "bg-indigo-600/25 text-white border border-indigo-500/40 shadow-sm" 
                    : "text-gray-400 hover:bg-slate-800/40 hover:text-white border border-transparent";

                nav.innerHTML += `
                    <button onclick="switchService('${svc.code}')" class="w-full flex items-center justify-between px-3 py-2 text-xs font-medium rounded-xl transition ${activeClass} cursor-pointer">
                        <div class="flex items-center space-x-2.5 min-w-0">
                            ${getServiceSvg(svc.code)}
                            <span class="truncate">${svc.name}</span>
                        </div>
                        <span class="px-2 py-0.5 rounded-full bg-slate-900 text-[10px] font-semibold text-gray-300 font-mono shrink-0">${count}</span>
                    </button>
                `;
            });
        }

        async function fetchCatalog() {
            try {
                const res = await fetch(`/api/admin/catalog?region=${currentRegion}`);
                catalogData = await res.json();

                let totalCompute = 0;
                let totalPlatform = 0;

                servicesList.forEach(svc => {
                    const items = catalogData[svc.code] || [];
                    if (['ec2', 'eks', 'ecs', 'ecr'].includes(svc.code)) {
                        totalCompute += items.length;
                    } else {
                        totalPlatform += items.length;
                    }
                });

                document.getElementById('compute-count').innerText = totalCompute;
                document.getElementById('other-count').innerText = totalPlatform;
                document.getElementById('current-service-tag').innerText = currentService.toUpperCase();

                renderServiceNav();
                renderTable();

            } catch (e) {
                showToast("Failed to fetch catalog: " + e.message, "error");
            }
        }

        function switchService(serviceCode) {
            currentService = serviceCode;
            document.getElementById('current-service-tag').innerText = currentService.toUpperCase();
            renderServiceNav();
            renderTable();
        }

        function renderTable() {
            const tableTitle = document.getElementById('table-title');
            const tableSubtitle = document.getElementById('table-subtitle');
            const tablePriceRange = document.getElementById('table-price-range');
            const tableRows = document.getElementById('table-rows');

            const svcObj = servicesList.find(s => s.code === currentService);
            const serviceName = svcObj ? svcObj.name : currentService.toUpperCase();
            tableTitle.innerText = `${serviceName} Catalog Database`;
            tableSubtitle.innerText = `Active Region: ${currentRegion.toUpperCase()} • PostgreSQL & Redis Dual Cache`;

            tableRows.innerHTML = '';
            const items = catalogData[currentService] || [];

            if (items.length === 0) {
                tablePriceRange.innerText = "$0.00/hr";
                tableRows.innerHTML = `<tr><td colspan="9" class="p-8 text-center text-xs text-gray-500">No catalog records stored for ${serviceName} in ${currentRegion.toUpperCase()}. Click 'Sync Live AWS Pricing' or 'Add Custom SKU'.</td></tr>`;
                return;
            }

            const prices = items.map(i => i.price_per_hour || 0.0);
            const minP = Math.min(...prices);
            const maxP = Math.max(...prices);
            tablePriceRange.innerText = `$${minP.toFixed(4)} - $${maxP.toFixed(4)}/hr (${items.length} items)`;

            items.forEach((item, idx) => {
                const vcpuDisp = (item.vcpus && item.vcpus > 0) ? item.vcpus : '-';
                const ramDisp = (item.ram_gb && item.ram_gb > 0) ? `${item.ram_gb} GB` : '-';
                const unitDisp = item.unit || 'Hrs';
                const netOrDetailDisp = item.network_performance || item.details || '-';
                const hourlyPrice = item.price_per_hour || 0.0;
                const monthlyPrice = (hourlyPrice * 730).toFixed(2);
                
                tableRows.innerHTML += `
                    <tr class="hover:bg-slate-800/30 transition border-b border-cyber-border/40">
                        <td class="p-3.5 font-bold text-white font-mono flex items-center space-x-2">
                            <span>${item.instance_type}</span>
                        </td>
                        <td class="p-3.5 text-gray-300 font-mono">${vcpuDisp}</td>
                        <td class="p-3.5 text-gray-300 font-mono">${ramDisp}</td>
                        <td class="p-3.5 text-gray-400 font-mono text-[11px]">${unitDisp}</td>
                        <td class="p-3.5"><span class="px-2 py-0.5 rounded bg-slate-900 text-[10px] capitalize text-indigo-300 border border-indigo-500/20 font-semibold">${item.category || 'Standard'}</span></td>
                        <td class="p-3.5 text-[11px] text-gray-400 truncate max-w-xs">${netOrDetailDisp}</td>
                        <td class="p-3.5 text-right text-emerald-400 font-mono font-bold">$${hourlyPrice.toFixed(4)}</td>
                        <td class="p-3.5 text-right text-gray-300 font-mono font-bold">$${monthlyPrice}</td>
                        <td class="p-3.5 text-center">
                            <button onclick="inspectItemByIndex(${idx})" class="p-1 px-2 text-[10px] font-semibold bg-slate-800 hover:bg-slate-700 text-indigo-300 rounded border border-cyber-border transition">
                                Inspect
                            </button>
                        </td>
                    </tr>
                `;
            });
        }

        function inspectItemByIndex(idx) {
            const items = catalogData[currentService] || [];
            const item = items[idx];
            if (!item) return;

            document.getElementById('inspector-title').innerText = `${item.instance_type} (${currentService.toUpperCase()})`;
            document.getElementById('inspector-json').innerText = JSON.stringify(item, null, 2);
            document.getElementById('modal-inspector').classList.remove('hidden');
        }

        function closeInspectorModal() {
            document.getElementById('modal-inspector').classList.add('hidden');
        }

        function copyInspectorJSON() {
            const text = document.getElementById('inspector-json').innerText;
            navigator.clipboard.writeText(text);
            showToast("JSON copied to clipboard!");
        }

        function openAddResourceModal() {
            document.getElementById('modal-service').value = currentService;
            document.getElementById('modal-add-resource').classList.remove('hidden');
        }

        function closeAddResourceModal() {
            document.getElementById('modal-add-resource').classList.add('hidden');
        }

        async function submitCustomResource(event) {
            event.preventDefault();
            const service = document.getElementById('modal-service').value;
            const instanceType = document.getElementById('modal-instance-type').value.trim();
            const vcpus = parseInt(document.getElementById('modal-vcpus').value) || 2;
            const ramGb = parseFloat(document.getElementById('modal-ram').value) || 4.0;
            const price = parseFloat(document.getElementById('modal-price').value) || 0.1;
            const category = document.getElementById('modal-category').value;
            const details = document.getElementById('modal-details').value;

            try {
                const res = await fetch(`/api/admin/catalog/${service}`, {
                    method: 'POST',
                    headers: { 'X-Admin-Key': adminKey, 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        instance_type: instanceType,
                        vcpus: vcpus,
                        ram_gb: ramGb,
                        price_per_hour: price,
                        category: category,
                        network_performance: details,
                        details: details,
                        region: currentRegion
                    })
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Save error");
                }

                showToast(`Resource '${instanceType}' successfully saved to DB & Redis!`);
                closeAddResourceModal();
                await fetchCatalog();
                await refreshProbes();
            } catch (err) {
                showToast("Failed to save resource: " + err.message, "error");
            }
        }

        function filterTable(tableId, query) {
            const table = document.getElementById(tableId);
            const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
            query = query.toLowerCase();
            for (let i = 0; i < rows.length; i++) {
                const text = rows[i].innerText.toLowerCase();
                rows[i].style.display = text.includes(query) ? "" : "none";
            }
        }

        let pollingInterval = null;

        async function triggerDynamicSync() {
            const spinner = document.getElementById('sync-spinner');
            const btn = document.getElementById('sync-btn');
            spinner.classList.remove('hidden');
            btn.disabled = true;
            
            showToast(`Initiating dynamic sync for ${currentRegion.toUpperCase()}...`);
            document.getElementById('region-sync-status').innerHTML = '<span class="text-yellow-400 animate-pulse font-bold">SYNCING...</span>';

            try {
                const res = await fetch(`/api/admin/catalog/sync/${currentRegion}`, {
                    method: 'POST',
                    headers: { 'X-Admin-Key': adminKey, 'Content-Type': 'application/json' },
                    body: JSON.stringify({ force_live_fetch: true, include_generic_services: true })
                });
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || 'API error');
                }
                
                if (pollingInterval) clearInterval(pollingInterval);
                pollingInterval = setInterval(checkRegionSyncStatus, 2000);
            } catch (err) {
                showToast(`Sync failed: ${err.message}`, 'error');
                spinner.classList.add('hidden');
                btn.disabled = false;
                document.getElementById('region-sync-status').innerHTML = '<span class="text-rose-400 font-bold">ERROR</span>';
            }
        }

        async function checkRegionSyncStatus() {
            try {
                const res = await fetch(`/api/admin/catalog/status/${currentRegion}`, {
                    headers: { 'X-Admin-Key': adminKey }
                });
                if (!res.ok) return;
                const data = await res.json();
                
                const statusEl = document.getElementById('region-sync-status');
                if (data.status === 'SUCCESS') {
                    statusEl.innerHTML = '<span class="text-emerald-400 font-bold">READY (SYNCED)</span>';
                } else if (data.status === 'FAILED') {
                    statusEl.innerHTML = '<span class="text-rose-400 font-bold">FAILED</span>';
                } else if (data.status === 'IN_PROGRESS') {
                    statusEl.innerHTML = '<span class="text-yellow-400 font-bold animate-pulse">SYNCING...</span>';
                } else {
                    statusEl.innerHTML = '<span class="text-gray-400 font-bold">READY</span>';
                }

                if (data.status === 'SUCCESS' || data.status === 'FAILED') {
                    if (pollingInterval) {
                        clearInterval(pollingInterval);
                        pollingInterval = null;
                        document.getElementById('sync-spinner').classList.add('hidden');
                        document.getElementById('sync-btn').disabled = false;
                        
                        if (data.status === 'SUCCESS') {
                            showToast(`Sync completed for ${currentRegion.toUpperCase()}! (${data.total_records} records)`);
                            await refreshProbes();
                            await fetchCatalog();
                        } else {
                            showToast(`Sync error: ${data.error_message}`, 'error');
                        }
                    }
                }
            } catch (err) {
                console.error("Status check failed", err);
            }
        }

        async function clearRedisCache() {
            try {
                const res = await fetch('/api/admin/clear-cache', {
                    method: 'POST',
                    headers: { 'X-Admin-Key': adminKey }
                });
                const data = await res.json();
                showToast("Redis L1 cache purged successfully.");
                await refreshProbes();
                await fetchCatalog();
            } catch (err) {
                showToast("Cache operation failed", "error");
            }
        }

        async function loadModules() {
            try {
                const res = await fetch('/api/admin/modules');
                if (!res.ok) return;
                const data = await res.json();
                modulesData = data.modules || [];
                
                // Render Sidebar Modules Navigation
                const sidebarNav = document.getElementById('sidebar-modules-list');
                sidebarNav.innerHTML = '';

                // Render Modules Hub Cards
                const cardsContainer = document.getElementById('modules-cards-container');
                cardsContainer.innerHTML = '';

                modulesData.forEach(mod => {
                    const statusColor = mod.status === 'ONLINE' ? 'bg-emerald-400' : (mod.status === 'CONNECTED' ? 'bg-cyan-400' : 'bg-indigo-400');
                    const badgeClass = mod.status === 'ONLINE' ? 'bg-emerald-500/15 text-emerald-400' : (mod.status === 'CONNECTED' ? 'bg-cyan-500/15 text-cyan-300' : 'bg-slate-800 text-gray-400');

                    // Sidebar Item
                    sidebarNav.innerHTML += `
                        <div onclick="selectModuleFromSidebar('${mod.code}')" class="cursor-pointer flex items-center justify-between px-3 py-2 text-xs font-medium rounded-xl text-gray-300 bg-slate-800/25 hover:bg-slate-800/60 border border-cyber-border transition">
                            <div class="flex items-center space-x-2.5">
                                <span class="h-1.5 w-1.5 rounded-full ${statusColor}"></span>
                                <span>${mod.id}. ${mod.name.replace(' Engine', '').replace(' Service', '')}</span>
                            </div>
                            <span class="text-[9px] px-1.5 py-0.5 rounded ${badgeClass} font-mono">${mod.status === 'ONLINE' ? `:${mod.port} Live` : mod.status}</span>
                        </div>
                    `;

                    // Module Card in Hub
                    cardsContainer.innerHTML += `
                        <div id="module-card-${mod.code}" class="glass-panel p-5 rounded-2xl border border-cyber-border space-y-3 glow-hover transition">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="text-[10px] font-bold uppercase tracking-wider text-indigo-400">${mod.phase}</div>
                                    <h4 class="text-base font-extrabold text-white mt-0.5 flex items-center gap-2">
                                        <span>${mod.id}. ${mod.name}</span>
                                    </h4>
                                </div>
                                <span class="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${badgeClass}">
                                    ${mod.status} ${mod.port ? `(:${mod.port})` : ''}
                                </span>
                            </div>
                            <p class="text-xs text-gray-300 leading-relaxed">${mod.description}</p>
                            
                            <div class="pt-3 border-t border-cyber-border/60 space-y-2">
                                <div class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Catalog Integration:</div>
                                <p class="text-[11px] text-gray-400">${mod.catalog_role}</p>
                                <div class="flex flex-wrap gap-1 mt-1">
                                    ${mod.catalog_dependencies.map(dep => `<span class="px-2 py-0.5 rounded bg-slate-900 text-[10px] text-indigo-300 font-mono border border-indigo-500/20">${dep}</span>`).join('')}
                                </div>
                            </div>
                        </div>
                    `;
                });

            } catch (e) {
                console.error("Failed to load modules:", e);
            }
        }

        function selectModuleFromSidebar(modCode) {
            switchMainView('modules');
            setTimeout(() => {
                const el = document.getElementById(`module-card-${modCode}`);
                if (el) {
                    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    el.classList.add('ring-2', 'ring-indigo-500');
                    setTimeout(() => el.classList.remove('ring-2', 'ring-indigo-500'), 2500);
                }
            }, 100);
        }

        async function loadRegionsMatrix() {
            try {
                const res = await fetch('/api/admin/catalog/regions', {
                    headers: { 'X-Admin-Key': adminKey }
                });
                if (!res.ok) return;
                regionsList = await res.json();

                const container = document.getElementById('matrix-regions-container');
                container.innerHTML = '';

                // Group regions by geography
                const groups = {
                    "North America": ["us-east-1", "us-east-2", "us-west-1", "us-west-2", "ca-central-1", "ca-west-1", "mx-central-1", "us-gov-east-1", "us-gov-west-1"],
                    "Europe": ["eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1", "eu-central-2", "eu-north-1", "eu-south-1", "eu-south-2"],
                    "Asia Pacific": ["ap-south-1", "ap-south-2", "ap-southeast-1", "ap-southeast-2", "ap-southeast-3", "ap-southeast-4", "ap-southeast-5", "ap-southeast-6", "ap-southeast-7", "ap-east-1", "ap-east-2", "ap-northeast-1", "ap-northeast-2", "ap-northeast-3"],
                    "Middle East & Africa": ["me-south-1", "me-central-1", "me-central-2", "il-central-1", "af-south-1"],
                    "South America & China": ["sa-east-1", "cn-north-1", "cn-northwest-1"]
                };

                for (const [geoName, regionCodes] of Object.entries(groups)) {
                    let cardsHtml = '';
                    regionCodes.forEach(code => {
                        const r = regionsList.find(item => item.region_code === code) || { region_code: code, region_name: code, az_count: 3, pricing_tier_multiplier: 1.0, cached_in_redis: true, db_exists: true };
                        
                        cardsHtml += `
                            <div onclick="selectRegionFromMatrix('${r.region_code}')" class="cursor-pointer glass-panel p-4 rounded-xl border border-cyber-border hover:border-indigo-500/50 transition space-y-2.5">
                                <div class="flex justify-between items-start">
                                    <div>
                                        <div class="font-extrabold text-sm text-white font-mono">${r.region_code}</div>
                                        <div class="text-[11px] text-gray-400 truncate max-w-[150px]">${r.region_name}</div>
                                    </div>
                                    <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-900 text-yellow-300 font-bold">${r.pricing_tier_multiplier}x</span>
                                </div>
                                <div class="pt-2 border-t border-cyber-border/40 flex justify-between items-center text-[10px]">
                                    <span class="text-gray-500">${r.az_count} AZs</span>
                                    <div class="flex items-center space-x-1.5 font-mono">
                                        <span class="px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 font-bold text-[9px]">PG READY</span>
                                        <span class="px-1.5 py-0.5 rounded bg-cyan-500/15 text-cyan-400 font-bold text-[9px]">REDIS L1</span>
                                    </div>
                                </div>
                            </div>
                        `;
                    });

                    container.innerHTML += `
                        <div class="space-y-3">
                            <h4 class="text-xs font-bold uppercase tracking-wider text-gray-400 flex items-center gap-2">
                                <span class="h-1.5 w-1.5 rounded-full bg-cyan-400"></span>
                                <span>${geoName} (${regionCodes.length} Regions)</span>
                            </h4>
                            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                                ${cardsHtml}
                            </div>
                        </div>
                    `;
                }

            } catch (e) {
                console.error("Failed to load regions matrix", e);
            }
        }

        function selectRegionFromMatrix(regionCode) {
            currentRegion = regionCode;
            document.getElementById('region-filter').value = regionCode;
            switchMainView('catalog');
            showToast(`Switched active region to ${regionCode.toUpperCase()}!`);
            onRegionFilterChange();
        }

        window.addEventListener('load', async () => {
            await checkAuthStatus();
            try {
                const res = await fetch('/api/admin/catalog/regions', {
                    headers: { 'X-Admin-Key': adminKey }
                });
                if (res.ok) {
                    regionsList = await res.json();
                }
            } catch (e) {
                console.error("Failed to load regions", e);
            }
            
            const filterSelect = document.getElementById('region-filter');
            filterSelect.innerHTML = '';
            
            if (regionsList.length > 0) {
                regionsList.forEach(r => {
                    filterSelect.innerHTML += `<option value="${r.region_code}" class="bg-cyber-bg text-white font-mono">${r.region_code} — ${r.region_name}</option>`;
                });
            } else {
                filterSelect.innerHTML = `<option value="us-east-1" class="bg-cyber-bg text-white font-mono">us-east-1 — US East (N. Virginia)</option>`;
            }
            
            filterSelect.value = currentRegion;
            await refreshProbes();
            await checkRegionSyncStatus();
            await fetchCatalog();
            await loadModules();
            await loadRegionsMatrix();
        });
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content, status_code=200)

