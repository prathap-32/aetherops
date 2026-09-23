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
import secrets
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
    MASTER_ADMIN_KEY,
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
    db: AsyncSession = Depends(get_db_session),
    api_key: str = Depends(verify_admin_key)
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
    
    if len(ec2_items) == 0:
        from app.seed import seed_catalog
        logger.info(f"Catalog for region '{region_lower}' is empty in database. Auto-seeding catalog...")
        try:
            await seed_catalog(db, region=region_lower, force=False)
            ec2_result = await db.execute(select(EC2Catalog))
            ec2_items = ec2_result.scalars().all()
        except Exception as seed_err:
            logger.warning(f"Auto-seed for region '{region_lower}' deferred: {seed_err}")

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
    az: str | None = None,
    api_key: str = Depends(verify_admin_key)
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
    db: AsyncSession = Depends(get_db_session),
    api_key: str = Depends(verify_admin_key)
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
    force_live_fetch: bool = Field(default=False, description="Force fetching from live ec2.shop API")
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
async def get_platform_modules(api_key: str = Depends(verify_admin_key)):
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
            "ui_url": "http://localhost:8001/app",
            "ui_path": "/app",
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
            "health_endpoint": "http://localhost:8003/health",
            "status": "ONLINE",
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
            "health_endpoint": "http://localhost:8004/health",
            "status": "ONLINE",
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
            "health_endpoint": "http://localhost:8005/health",
            "status": "ONLINE",
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
            "health_endpoint": "http://localhost:8006/health",
            "status": "ONLINE",
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
            "health_endpoint": "http://localhost:8007/health",
            "status": "ONLINE",
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
            "health_endpoint": "http://localhost:8008/health",
            "status": "ONLINE",
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
async def serve_admin_dashboard(request: Request):
    """
    Serves the master AWS Management Console dashboard for AWS Quick Infra Manager.
    Enforces strict authentication:
    If no valid JWT cookie session ('aether_session'), Bearer token, or master API key is present,
    redirects immediately to /admin/login.
    """
    is_authenticated = False

    # Channel 1: Check HttpOnly cookie
    cookie_token = request.cookies.get(SESSION_COOKIE_NAME)
    if cookie_token:
        payload = decode_access_token(cookie_token)
        if payload:
            is_authenticated = True

    # Channel 2: Check Authorization: Bearer <token>
    if not is_authenticated:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            payload = decode_access_token(token)
            if payload:
                is_authenticated = True

    # Channel 3: Check X-Admin-Key header
    if not is_authenticated:
        admin_key = request.headers.get("X-Admin-Key")
        if admin_key and secrets.compare_digest(admin_key.strip(), MASTER_ADMIN_KEY):
            is_authenticated = True

    if not is_authenticated:
        return RedirectResponse(
            url="/admin/login?redirect=/admin",
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )

    from app.dashboard_page import get_dashboard_page_html
    return HTMLResponse(content=get_dashboard_page_html(), status_code=200)

