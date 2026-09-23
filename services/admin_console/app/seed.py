import os
import json
import logging
import datetime
import uuid
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import (
    Base, engine, get_sqlite_sessionmaker,
    get_requirements_sessionmaker, init_requirements_db
)
from app.models import EC2Catalog, RDSCatalog, GenericServiceCatalog, SyncMetadata, RequirementProject
from app.schemas import (
    RequirementInput, TechnologyStack, OperationsPreference,
    MonitoringPreference, CloudStream, TrafficScale, ReliabilityLevel, SecurityNeed
)
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
        
    multiplier = 1.0
    if region_data and "pricing_tier_multiplier" in region_data:
        try:
            multiplier = float(region_data["pricing_tier_multiplier"])
        except Exception:
            multiplier = 1.0

    for item in EC2_CATALOG:
        price = round(item.price_per_hour * multiplier, 4)
        session.add(EC2Catalog(
            instance_type=item.instance_type,
            vcpus=item.vcpus,
            ram_gb=item.ram_gb,
            price_per_hour=price,
            network_performance=item.network_performance,
            category=item.category
        ))

    for item in RDS_CATALOG:
        price = round(item.price_per_hour * multiplier, 4)
        session.add(RDSCatalog(
            instance_type=item.instance_type,
            vcpus=item.vcpus,
            ram_gb=item.ram_gb,
            price_per_hour=price,
            category=item.category
        ))
            
    from app.sync_helper import GENERIC_SERVICES_ITEMS, get_generic_fallback_pricing
    for service_name, item_types in GENERIC_SERVICES_ITEMS.items():
        for item_type in item_types:
            fallback = get_generic_fallback_pricing(service_name, item_type, region=region)
            price = round(fallback["price_per_hour"] * multiplier, 4)
            session.add(GenericServiceCatalog(
                service=service_name,
                instance_type=fallback["instance_type"],
                vcpus=fallback["vcpus"],
                ram_gb=fallback["ram_gb"],
                price_per_hour=price,
                unit=fallback["unit"],
                category=fallback["category"],
                region=fallback["region"],
                details=fallback["details"]
            ))

    meta_res = await session.execute(select(SyncMetadata).where(SyncMetadata.region_code == region))
    meta_row = meta_res.scalar_one_or_none()
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


async def seed_sample_requirements():
    """
    Seeds initial sample workload requirement profiles in SQLite requirements.db if empty.
    """
    await init_requirements_db()
    sf = get_requirements_sessionmaker()
    async with sf() as session:
        try:
            existing = await session.execute(select(RequirementProject).limit(1))
            if existing.scalar_one_or_none() is not None:
                logger.info("requirements.db already contains projects. Skipping sample seeding.")
                return

            from app.engine import analyze_and_explain_requirements

            sample_1 = RequirementInput(
                project_name="fintech-payment-engine",
                stream=CloudStream.web_application,
                technology=TechnologyStack(
                    frontend="react_vue_angular",
                    backend="python_fastapi_django",
                    database="postgresql"
                ),
                operations=OperationsPreference(
                    container_orchestration="kubernetes",
                    infrastructure_as_code="terraform",
                    ci_cd_pipeline="github_actions"
                ),
                monitoring=MonitoringPreference(
                    level="advanced",
                    alerting_channel="slack_webhook"
                ),
                traffic_scale=TrafficScale.growth,
                reliability=ReliabilityLevel.production_safe,
                data_storage_gb=80.0,
                security_need=SecurityNeed.payment_processing,
                monthly_budget=600.0
            )

            sample_2 = RequirementInput(
                project_name="cloud-saas-starter",
                stream=CloudStream.web_application,
                technology=TechnologyStack(
                    frontend="simple_html_css",
                    backend="nodejs_express",
                    database="postgresql"
                ),
                operations=OperationsPreference(
                    container_orchestration="docker_compose",
                    infrastructure_as_code="terraform",
                    ci_cd_pipeline="github_actions"
                ),
                monitoring=MonitoringPreference(
                    level="basic",
                    alerting_channel="email"
                ),
                traffic_scale=TrafficScale.hobby_dev,
                reliability=ReliabilityLevel.dev_testing,
                data_storage_gb=15.0,
                security_need=SecurityNeed.standard,
                monthly_budget=100.0
            )

            # Analyze using default session (us-east-1)
            default_sf = get_sqlite_sessionmaker("us-east-1")
            async with default_sf() as cat_session:
                res1 = await analyze_and_explain_requirements(sample_1, cat_session)
                res2 = await analyze_and_explain_requirements(sample_2, cat_session)

            proj1 = RequirementProject(
                id=str(uuid.uuid4()),
                project_name=sample_1.project_name,
                description="High-throughput payment gateway with PCI-DSS compliance and Multi-AZ PostgreSQL failover.",
                stream=sample_1.stream.value,
                target_region="us-east-1",
                traffic_scale=sample_1.traffic_scale.value,
                reliability=sample_1.reliability.value,
                security_need=sample_1.security_need.value,
                data_storage_gb=sample_1.data_storage_gb,
                monthly_budget=sample_1.monthly_budget,
                tech_stack=json.dumps(sample_1.technology.model_dump()),
                operations=json.dumps(sample_1.operations.model_dump()),
                monitoring=json.dumps(sample_1.monitoring.model_dump()),
                architecture_tier=res1["architecture_tier"],
                estimated_monthly_cost=res1["total_estimated_cost"],
                cost_breakdown=json.dumps(res1["cost_breakdown"]),
                service_rationales=json.dumps(res1["service_rationales"]),
                cost_optimizations=json.dumps(res1["cost_optimizations"]),
                profile_output=json.dumps(res1["profile"]),
                status="ANALYZED"
            )

            proj2 = RequirementProject(
                id=str(uuid.uuid4()),
                project_name=sample_2.project_name,
                description="Developer prototype environment with Docker Compose and single-instance burstable compute.",
                stream=sample_2.stream.value,
                target_region="us-east-1",
                traffic_scale=sample_2.traffic_scale.value,
                reliability=sample_2.reliability.value,
                security_need=sample_2.security_need.value,
                data_storage_gb=sample_2.data_storage_gb,
                monthly_budget=sample_2.monthly_budget,
                tech_stack=json.dumps(sample_2.technology.model_dump()),
                operations=json.dumps(sample_2.operations.model_dump()),
                monitoring=json.dumps(sample_2.monitoring.model_dump()),
                architecture_tier=res2["architecture_tier"],
                estimated_monthly_cost=res2["total_estimated_cost"],
                cost_breakdown=json.dumps(res2["cost_breakdown"]),
                service_rationales=json.dumps(res2["service_rationales"]),
                cost_optimizations=json.dumps(res2["cost_optimizations"]),
                profile_output=json.dumps(res2["profile"]),
                status="ANALYZED"
            )

            session.add(proj1)
            session.add(proj2)
            await session.commit()
            logger.info("Successfully seeded initial sample projects into requirements.db.")
        except Exception as e:
            logger.warning(f"Seeding sample requirements skipped: {e}", exc_info=True)

