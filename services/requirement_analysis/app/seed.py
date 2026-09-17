import os
import json
import logging
import datetime
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base, engine
from app.models import EC2Catalog, RDSCatalog, GenericServiceCatalog, SyncMetadata
from app.catalog import EC2_CATALOG, RDS_CATALOG

logger = logging.getLogger("requirement-analysis-seeder")

async def init_db():
    """
    Creates all database tables defined in the metadata.
    """
    logger.info("Initializing database schemas...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schemas initialized.")

async def seed_catalog(session: AsyncSession, region: str = "us-east-1", force: bool = False):
    """
    Seeds catalog entries into database by executing a local seed script.
    If force=False and the database already contains data for the region, seeding is skipped to preserve stored synced values.
    """
    region = region.lower().strip()
    
    if not force:
        existing = await session.execute(select(EC2Catalog).limit(1))
        if existing.scalar_one_or_none() is not None:
            logger.info(f"Database for region '{region}' already contains catalog data. Preserving stored DB values.")
            return

    logger.info(f"Seeding catalog entries for region '{region}'...")
    
    await session.execute(delete(EC2Catalog))
    await session.execute(delete(RDSCatalog))
    await session.execute(delete(GenericServiceCatalog))
    
    ref_data = None
    paths_to_check = [
        "aws_regions_reference.json",
        "scratch/aws_regions_reference.json",
        "../aws_regions_reference.json",
        "/home/prathap32/GP/devops-lab/projects/aether-cloud/services/requirement_analysis/aws_regions_reference.json"
    ]
    for path in paths_to_check:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    ref_data = json.load(f)
                break
            except Exception:
                pass
                
    region_data = None
    if ref_data:
        region_data = next((r for r in ref_data["regions"] if r["region_code"] == region), None)
        
    if region_data:
        compute_catalog = region_data["service_catalog"].get("compute_baseline_hourly", {})
        for inst_type, price in compute_catalog.items():
            spec = next((item for item in EC2_CATALOG if item.instance_type == inst_type), None)
            session.add(EC2Catalog(
                instance_type=inst_type,
                vcpus=spec.vcpus if spec else 2,
                ram_gb=spec.ram_gb if spec else 4.0,
                price_per_hour=float(price),
                network_performance=spec.network_performance if spec else "Up to 5 Gbps",
                category=spec.category if spec else "burstable"
            ))
            
        rds_catalog = region_data["service_catalog"].get("database_baseline_hourly", {})
        for inst_type, price in rds_catalog.items():
            spec = next((item for item in RDS_CATALOG if item.instance_type == inst_type), None)
            session.add(RDSCatalog(
                instance_type=inst_type,
                vcpus=spec.vcpus if spec else 2,
                ram_gb=spec.ram_gb if spec else 4.0,
                price_per_hour=float(price),
                category=spec.category if spec else "burstable"
            ))
    else:
        for item in EC2_CATALOG:
            session.add(EC2Catalog(
                instance_type=item.instance_type,
                vcpus=item.vcpus,
                ram_gb=item.ram_gb,
                price_per_hour=item.price_per_hour,
                network_performance=item.network_performance,
                category=item.category
            ))
        for item in RDS_CATALOG:
            session.add(RDSCatalog(
                instance_type=item.instance_type,
                vcpus=item.vcpus,
                ram_gb=item.ram_gb,
                price_per_hour=item.price_per_hour,
                category=item.category
            ))
            
    from app.sync_helper import GENERIC_SERVICES_ITEMS, get_generic_fallback_pricing
    for service_name, item_types in GENERIC_SERVICES_ITEMS.items():
        for item_type in item_types:
            fallback = get_generic_fallback_pricing(service_name, item_type, region=region)
            session.add(GenericServiceCatalog(
                service=service_name,
                instance_type=fallback["instance_type"],
                vcpus=fallback["vcpus"],
                ram_gb=fallback["ram_gb"],
                price_per_hour=fallback["price_per_hour"],
                unit=fallback["unit"],
                category=fallback["category"],
                region=fallback["region"],
                details=fallback["details"]
            ))

    meta_res = await session.execute(select(SyncMetadata).where(SyncMetadata.region_code == region))
    meta_row = meta_res.scalar_one_or_none()
    if region_data:
        ec2_cnt = len(region_data["service_catalog"].get("compute_baseline_hourly", {}))
        rds_cnt = len(region_data["service_catalog"].get("database_baseline_hourly", {}))
    else:
        ec2_cnt = len(EC2_CATALOG)
        rds_cnt = len(RDS_CATALOG)
    gen_cnt = sum(len(items) for items in GENERIC_SERVICES_ITEMS.values())
    tot_cnt = ec2_cnt + rds_cnt + gen_cnt
    if meta_row:
        meta_row.status = "SUCCESS"
        meta_row.last_sync_timestamp = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        meta_row.records_synced = tot_cnt
        meta_row.ec2_count = ec2_cnt
        meta_row.rds_count = rds_cnt
        meta_row.generic_count = gen_cnt
        meta_row.duration_ms = 120
        meta_row.error_message = None
    else:
        session.add(SyncMetadata(
            region_code=region,
            last_sync_timestamp=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
            status="SUCCESS",
            records_synced=tot_cnt,
            ec2_count=ec2_cnt,
            rds_count=rds_cnt,
            generic_count=gen_cnt,
            duration_ms=120,
        ))
            
    await session.commit()
    logger.info(f"Catalog for region '{region}' seeded successfully.")

async def seed_all_regions(force: bool = True):
    """
    Seeds catalog entries for all 39 regions into:
    1. Local SQLite partitions (catalog_{region}.db)
    2. PostgreSQL container schemas (region_{region_pg})
    3. Redis in-memory cache
    """
    import asyncio
    from app.database import (
        SUPPORTED_REGIONS,
        init_db_for_region,
        get_sqlite_sessionmaker,
        get_postgres_sessionmaker,
        IS_TESTING
    )
    from app.cache import cache_manager, get_region_catalog
    
    logger.info(f"Starting bulk catalog upload for all {len(SUPPORTED_REGIONS)} regions...")
    sem = asyncio.Semaphore(10)
    
    async def upload_one(region):
        async with sem:
            try:
                await init_db_for_region(region)
                
                # 1. Seed SQLite
                sq_sf = get_sqlite_sessionmaker(region)
                async with sq_sf() as sq_sess:
                    await seed_catalog(sq_sess, region, force=force)
                    await get_region_catalog(region, sq_sess)
                    
                # 2. Seed PostgreSQL
                if not IS_TESTING:
                    try:
                        pg_sf = get_postgres_sessionmaker(region)
                        async with pg_sf() as pg_sess:
                            await seed_catalog(pg_sess, region, force=force)
                    except Exception as pg_err:
                        logger.warning(f"PostgreSQL seed deferred for {region}: {pg_err}")
                        
                logger.info(f"Catalog uploaded for region '{region}'.")
            except Exception as e:
                logger.error(f"Error seeding region '{region}': {e}")

    await asyncio.gather(*(upload_one(r) for r in SUPPORTED_REGIONS))
    
    if cache_manager._is_connected and cache_manager.redis_client:
        try:
            await cache_manager.redis_client.bgsave()
        except Exception:
            pass
            
    logger.info("Bulk catalog upload for all 39 regions completed.")
