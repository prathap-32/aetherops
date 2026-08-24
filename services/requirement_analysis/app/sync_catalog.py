# services/requirement_analysis/app/sync_catalog.py
import asyncio
import logging
import sys

from app.database import AsyncSessionLocal, engine
from app.cache import cache_manager
from app.sync_helper import sync_catalog_from_aws

# Setup logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("requirement-analysis-cli-sync")

async def main():
    logger.info("Initializing automated AWS catalog sync script...")
    await cache_manager.connect()
    
    try:
        async with AsyncSessionLocal() as session:
            logger.info("Starting synchronization with AWS Price List / docs APIs...")
            result = await sync_catalog_from_aws(session)
            logger.info(f"Sync complete! Result: {result}")
    except Exception as e:
        logger.error(f"Failed to synchronize catalog: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await cache_manager.disconnect()
        await engine.dispose()
        logger.info("Script finished execution.")

if __name__ == "__main__":
    asyncio.run(main())
