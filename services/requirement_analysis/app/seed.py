import os
import json
import logging
from sqlalchemy import delete
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
    Seeds catalog entries into database by executing a local seed script.
    """
    region = region.lower().strip()
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
            
    await session.commit()
    logger.info(f"Catalog for region '{region}' seeded successfully.")
