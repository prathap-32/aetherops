# services/source_and_cloud_connection/app/seed.py
import uuid, json, datetime, logging
from sqlalchemy import select
from app.database import init_source_db, get_sqlite_sessionmaker
from app.models import GitConnection, SourceSnapshot

logger = logging.getLogger("source-connection-seeder")


async def seed_initial_data():
    await init_source_db()
    sf = get_sqlite_sessionmaker()
    async with sf() as session:
        try:
            res = await session.execute(select(GitConnection).limit(1))
            if res.scalar_one_or_none():
                return

            # Sample connection 1
            conn1_id = str(uuid.uuid4())
            proj1_id = "sample-project-001"
            env1_id  = "sample-env-001"

            conn1 = GitConnection(
                id=conn1_id, project_id=proj1_id, environment_id=env1_id,
                owner="admin", repo_url="https://github.com/aetherops/aethershop",
                repo_name="aetherops/aethershop", branch="main",
                pat_label="github-pat-dev", default_branch="main",
                last_commit_sha="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
                last_commit_msg="feat: add checkout flow with Stripe integration",
                last_commit_author="dev@aetherops.cloud",
                last_commit_at=datetime.datetime(2026, 10, 10, 8, 30, 0),
                is_private=True, stars="128", language="Python",
                status="CONNECTED",
                created_at=datetime.datetime.utcnow(), updated_at=datetime.datetime.utcnow(),
            )
            session.add(conn1)

            snap1_tree = [
                {"path": "README.md",          "type": "file", "size": 1240},
                {"path": "requirements.txt",    "type": "file", "size": 312},
                {"path": "Dockerfile",          "type": "file", "size": 890},
                {"path": "app/",                "type": "dir",  "size": 0},
                {"path": "app/main.py",         "type": "file", "size": 3400},
                {"path": "app/models.py",       "type": "file", "size": 2100},
                {"path": "app/routes/",         "type": "dir",  "size": 0},
                {"path": "app/routes/cart.py",  "type": "file", "size": 1800},
                {"path": "app/routes/checkout.py","type":"file","size": 2200},
                {"path": ".github/",            "type": "dir",  "size": 0},
                {"path": ".github/workflows/ci.yml","type":"file","size":980},
            ]
            snap1 = SourceSnapshot(
                id=str(uuid.uuid4()), connection_id=conn1_id,
                project_id=proj1_id, environment_id=env1_id,
                commit_sha="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2", branch="main",
                file_tree=json.dumps(snap1_tree),
                detected_files=json.dumps({"dockerfile": True, "requirements_txt": True,
                                           "github_actions": True, "docker_compose": False}),
                language_hints=json.dumps({"primary": "Python", "others": ["HTML", "CSS"]}),
                total_files="11", total_size_kb="12",
                created_at=datetime.datetime.utcnow(),
            )
            session.add(snap1)

            # Sample cloud connection 1 — Access Keys
            cloud1 = CloudConnection(
                id=str(uuid.uuid4()), project_id=proj1_id, environment_id=env1_id, owner="admin",
                provider="AWS", auth_type="ACCESS_KEYS", aws_region="ap-south-1",
                access_key_masked="AKIA••••••••7890", access_key_id="AKIAIOSFODNN7EXAMPLE",
                account_id="123456789012", caller_arn="arn:aws:iam::123456789012:user/aether-deployer",
                caller_user_id="AIDAIEXAMPLE12345", status="CONNECTED",
                last_validated_at=datetime.datetime.utcnow(),
                created_at=datetime.datetime.utcnow(), updated_at=datetime.datetime.utcnow(),
            )
            session.add(cloud1)

            # Sample connection 2 — pending
            conn2 = GitConnection(
                id=str(uuid.uuid4()), project_id="sample-project-002",
                environment_id="sample-env-002", owner="admin",
                repo_url="https://github.com/aetherops/datastream-api",
                repo_name="aetherops/datastream-api", branch="develop",
                pat_label=None, status="PENDING",
                created_at=datetime.datetime.utcnow(), updated_at=datetime.datetime.utcnow(),
            )
            session.add(conn2)

            cloud2 = CloudConnection(
                id=str(uuid.uuid4()), project_id="sample-project-002", environment_id="sample-env-002", owner="admin",
                provider="AWS", auth_type="IAM_ROLE_ARN", aws_region="us-east-1",
                role_arn="arn:aws:iam::987654321098:role/AetherOpsCrossAccountRole",
                account_id="987654321098", caller_arn="arn:aws:iam::987654321098:role/AetherOpsCrossAccountRole",
                status="CONNECTED", last_validated_at=datetime.datetime.utcnow(),
                created_at=datetime.datetime.utcnow(), updated_at=datetime.datetime.utcnow(),
            )
            session.add(cloud2)

            await session.commit()
            logger.info("Seeded sample git and cloud connections.")
        except Exception as exc:
            logger.warning(f"Seed skipped: {exc}", exc_info=True)
