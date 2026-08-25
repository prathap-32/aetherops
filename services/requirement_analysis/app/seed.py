# services/requirement_analysis/app/seed.py
import logging
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base, engine
from app.models import EC2Catalog, RDSCatalog, GenericServiceCatalog
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

async def seed_catalog(session: AsyncSession, region: str = "us-east-1"):
    """
    Seeds catalog entries into database if empty.
    """
    logger.info(f"Checking database catalog status for region '{region}'...")
    
    # 1. Seed EC2 catalog
    ec2_count_query = await session.execute(select(EC2Catalog))
    existing_ec2s = ec2_count_query.scalars().all()
    
    if not existing_ec2s:
        logger.info(f"Seeding {len(EC2_CATALOG)} EC2 instances to database...")
        for spec in EC2_CATALOG:
            db_spec = EC2Catalog(
                instance_type=spec.instance_type,
                vcpus=spec.vcpus,
                ram_gb=spec.ram_gb,
                price_per_hour=spec.price_per_hour,
                network_performance=spec.network_performance,
                category=spec.category
            )
            session.add(db_spec)
        await session.flush()
        logger.info("EC2 catalog seeded successfully.")
    else:
        logger.info("EC2 catalog database is already populated.")

    # 2. Seed RDS catalog
    rds_count_query = await session.execute(select(RDSCatalog))
    existing_rds = rds_count_query.scalars().all()
    
    if not existing_rds:
        logger.info(f"Seeding {len(RDS_CATALOG)} RDS instances to database...")
        for spec in RDS_CATALOG:
            db_spec = RDSCatalog(
                instance_type=spec.instance_type,
                vcpus=spec.vcpus,
                ram_gb=spec.ram_gb,
                price_per_hour=spec.price_per_hour,
                category=spec.category
            )
            session.add(db_spec)
        await session.flush()
        logger.info("RDS catalog seeded successfully.")
    else:
        logger.info("RDS catalog database is already populated.")
    
    # 3. Seed Generic catalog
    generic_count_query = await session.execute(select(GenericServiceCatalog))
    existing_generic = generic_count_query.scalars().all()
    
    if not existing_generic:
        from app.sync_helper import get_generic_fallback_pricing, GENERIC_SERVICES_ITEMS
        
        fallback_items = []
        for svc, item_types in GENERIC_SERVICES_ITEMS.items():
            for item_t in item_types:
                fallback_items.append((svc, item_t))
                
        logger.info(f"Seeding {len(fallback_items)} generic service entries to database...")
        for svc, item_t in fallback_items:
            item = get_generic_fallback_pricing(svc, item_t, region=region)
            db_item = GenericServiceCatalog(
                service=item["service"],
                instance_type=item["instance_type"],
                vcpus=item["vcpus"],
                ram_gb=item["ram_gb"],
                price_per_hour=item["price_per_hour"],
                unit=item["unit"],
                category=item["category"],
                region=item["region"],
                details=item["details"]
            )
            session.add(db_item)
        await session.flush()
        logger.info("Generic service catalog seeded successfully.")
    else:
        logger.info("Generic service catalog database is already populated.")
        
    await session.commit()
