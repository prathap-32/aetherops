# services/project_and_environment_management/app/seed.py
import logging
import uuid
import datetime

from sqlalchemy import select

from app.database import init_projects_db, get_sqlite_sessionmaker
from app.models import AetherProject, AetherEnvironment

logger = logging.getLogger("project-manager-seeder")


async def seed_initial_data():
    """
    Seeds two sample projects with environments into projects.db if empty.
    Skips seeding if data already exists.
    """
    await init_projects_db()
    sf = get_sqlite_sessionmaker()

    async with sf() as session:
        try:
            res = await session.execute(select(AetherProject).limit(1))
            if res.scalar_one_or_none() is not None:
                logger.info("projects.db already has data — skipping seed.")
                return

            # Sample project 1
            proj1_id = str(uuid.uuid4())
            proj1 = AetherProject(
                id=proj1_id,
                name="AetherShop",
                description="E-commerce application with microservices architecture and AWS RDS backend.",
                project_type="web_application",
                owner="admin",
                status="ACTIVE",
                environment_count=2,
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
            )
            session.add(proj1)

            session.add(AetherEnvironment(
                id=str(uuid.uuid4()),
                project_id=proj1_id,
                name="Development",
                env_type="development",
                aws_region="ap-south-1",
                description="Local dev environment with t3.micro instances.",
                status="CONFIGURED",
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
            ))
            session.add(AetherEnvironment(
                id=str(uuid.uuid4()),
                project_id=proj1_id,
                name="Production",
                env_type="production",
                aws_region="us-east-1",
                description="Production environment with Multi-AZ RDS and CloudFront CDN.",
                status="ARCHITECTURE_READY",
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
            ))

            # Sample project 2
            proj2_id = str(uuid.uuid4())
            proj2 = AetherProject(
                id=proj2_id,
                name="DataStream API",
                description="Real-time data ingestion and processing API service on ECS.",
                project_type="api_service",
                owner="admin",
                status="CREATED",
                environment_count=1,
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
            )
            session.add(proj2)

            session.add(AetherEnvironment(
                id=str(uuid.uuid4()),
                project_id=proj2_id,
                name="Staging",
                env_type="staging",
                aws_region="eu-west-1",
                description="Staging environment for integration testing.",
                status="CREATED",
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
            ))

            await session.commit()
            logger.info("Seeded 2 sample projects and 3 environments into projects.db.")

        except Exception as exc:
            logger.warning(f"Sample data seed skipped: {exc}", exc_info=True)
