# services/requirement_analysis/app/cache.py
import os
import logging
import json
import datetime
from typing import Optional, Any
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("requirement-analysis-cache")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class CacheManager:
    """
    Asynchronous Redis Cache Manager with graceful DB fallback on connection failure.
    """
    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self._is_connected = False

    async def connect(self):
        """
        Initializes the async Redis client pool.
        """
        try:
            self.redis_client = aioredis.from_url(
                REDIS_URL, 
                encoding="utf-8", 
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0
            )
            # Ping to verify active connection
            await self.redis_client.ping()
            self._is_connected = True
            logger.info("Successfully connected to Redis cache.")
        except Exception as e:
            self._is_connected = False
            self.redis_client = None
            logger.warning(f"Redis connection failed: {e}. Falling back to DB-only operations.")

    async def get(self, key: str) -> Optional[str]:
        """
        Gets a value from Redis by key. Returns None on cache miss or connection error.
        """
        if not self._is_connected or not self.redis_client:
            return None
        try:
            return await self.redis_client.get(key)
        except Exception as e:
            logger.warning(f"Error fetching from Redis cache for key '{key}': {e}")
            return None

    async def get_json(self, key: str) -> Optional[Any]:
        """
        Gets and parses JSON value from Redis by key.
        """
        val = await self.get(key)
        if val:
            try:
                return json.loads(val)
            except Exception:
                return None
        return None

    async def set(self, key: str, value: str, expire_seconds: int = 3600) -> bool:
        """
        Sets a key-value pair in Redis with an optional TTL.
        """
        if not self._is_connected or not self.redis_client:
            return False
        try:
            await self.redis_client.set(key, value, ex=expire_seconds)
            return True
        except Exception as e:
            logger.warning(f"Error setting key '{key}' in Redis cache: {e}")
            return False

    async def set_json(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """
        Serializes and sets an object as JSON in Redis.
        """
        try:
            return await self.set(key, json.dumps(value), expire_seconds)
        except Exception as e:
            logger.warning(f"Failed to serialize JSON for key '{key}': {e}")
            return False

    async def invalidate(self, key: str) -> bool:
        """
        Removes a key from the cache.
        """
        if not self._is_connected or not self.redis_client:
            return False
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Error invalidating key '{key}' in Redis: {e}")
            return False

    async def clear_catalog_cache(self) -> bool:
        """
        Invalidates all keys prefixed with 'catalog:'.
        """
        if not self._is_connected or not self.redis_client:
            return False
        try:
            keys = await self.redis_client.keys("catalog:*")
            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} catalog cache entries.")
            return True
        except Exception as e:
            logger.warning(f"Error clearing catalog cache prefix: {e}")
            return False

    async def disconnect(self):
        """
        Closes the Redis connection pool.
        """
        if self.redis_client:
            try:
                await self.redis_client.aclose()
                logger.info("Closed Redis connection.")
            except Exception:
                pass
            finally:
                self.redis_client = None
                self._is_connected = False

# Global Cache Manager instance
cache_manager = CacheManager()

def load_aws_regions_reference_in_cache():
    paths_to_check = [
        "aws_regions_reference.json",
        "scratch/aws_regions_reference.json",
        "../aws_regions_reference.json",
        "/home/prathap32/GP/devops-lab/projects/aether-cloud/services/requirement_analysis/aws_regions_reference.json"
    ]
    for path in paths_to_check:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    raise FileNotFoundError("aws_regions_reference.json could not be found.")

async def warm_region_cache(region: str, ec2_items: list, rds_items: list, generic_items: list, metadata: dict):
    """
    Warms the Redis cache for a specific region's catalog data.
    """
    region = region.lower().strip()
    
    # 1. Top 50 burstable & compute instances
    burstable_and_compute = [
        item for item in ec2_items 
        if item.get("category") in ["burstable", "compute"]
    ]
    sorted_ec2 = sorted(burstable_and_compute, key=lambda x: x.get("price_per_hour", 0.0))[:50]
    await cache_manager.set_json(f"catalog:{region}:ec2:summary", sorted_ec2, expire_seconds=86400)
    
    # 2. Standard DB tiers & costs
    standard_db = [
        item for item in rds_items
        if item.get("category") in ["standard", "burstable", "memory"]
    ]
    sorted_rds = sorted(standard_db, key=lambda x: x.get("price_per_hour", 0.0))
    await cache_manager.set_json(f"catalog:{region}:rds:summary", sorted_rds, expire_seconds=86400)
    
    # 3. Storage, WAF, NAT, CloudWatch rates
    await cache_manager.set_json(f"catalog:{region}:generic:all", generic_items, expire_seconds=86400)
    
    # 4. Metadata
    meta_payload = {
        "region_code": region,
        "last_sync_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "SUCCESS",
        "az_count": metadata.get("az_count", 3),
        "launch_year": metadata.get("launch_year", 2016),
        "pricing_tier_multiplier": metadata.get("pricing_tier_multiplier", 1.0),
        "records_synced": metadata.get("records_count", len(ec2_items) + len(rds_items) + len(generic_items))
    }
    await cache_manager.set_json(f"catalog:{region}:metadata", meta_payload, expire_seconds=86400)

async def get_region_catalog(region: str, db: AsyncSession) -> dict:
    """
    Cache-Aside retrieval: check Redis first; if cache miss, query regional SQLite and write back.
    """
    region = region.lower().strip()
    
    ec2_key = f"catalog:{region}:ec2:summary"
    rds_key = f"catalog:{region}:rds:summary"
    generic_key = f"catalog:{region}:generic:all"
    meta_key = f"catalog:{region}:metadata"
    
    ec2_summary = await cache_manager.get_json(ec2_key)
    rds_summary = await cache_manager.get_json(rds_key)
    generic_all = await cache_manager.get_json(generic_key)
    meta = await cache_manager.get_json(meta_key)
    
    if ec2_summary is not None and rds_summary is not None and generic_all is not None:
        return {
            "region": region,
            "ec2": ec2_summary,
            "rds": rds_summary,
            "generic": generic_all,
            "metadata": meta
        }
        
    logger.info(f"Cache miss for region catalog {region}. Querying database...")
    from app.models import EC2Catalog, RDSCatalog, GenericServiceCatalog, SyncMetadata
    from sqlalchemy.future import select
    
    ec2_res = await db.execute(select(EC2Catalog))
    ec2_items = [item.to_dict() for item in ec2_res.scalars().all()]
    
    rds_res = await db.execute(select(RDSCatalog))
    rds_items = [item.to_dict() for item in rds_res.scalars().all()]
    
    generic_res = await db.execute(select(GenericServiceCatalog))
    generic_items = [item.to_dict() for item in generic_res.scalars().all()]
    
    meta_res = await db.execute(select(SyncMetadata).where(SyncMetadata.region_code == region))
    meta_db = meta_res.scalar_one_or_none()
    
    try:
        ref_data = load_aws_regions_reference_in_cache()
        region_data = next((r for r in ref_data["regions"] if r["region_code"] == region), {})
    except Exception:
        region_data = {}
    
    meta_payload = {
        "region_code": region,
        "last_sync_timestamp": meta_db.last_sync_timestamp.isoformat() if meta_db and meta_db.last_sync_timestamp else None,
        "status": meta_db.status if meta_db else "PENDING",
        "az_count": region_data.get("az_count", 3),
        "launch_year": region_data.get("launch_year", 2016),
        "pricing_tier_multiplier": region_data.get("pricing_tier_multiplier", 1.0),
        "records_synced": meta_db.records_synced if meta_db else 0
    }
    
    # Warm the cache
    await warm_region_cache(region, ec2_items, rds_items, generic_items, {
        "az_count": meta_payload["az_count"],
        "launch_year": meta_payload["launch_year"],
        "pricing_tier_multiplier": meta_payload["pricing_tier_multiplier"],
        "records_count": len(ec2_items) + len(rds_items) + len(generic_items)
    })
    
    return {
        "region": region,
        "ec2": ec2_items,
        "rds": rds_items,
        "generic": generic_items,
        "metadata": meta_payload
    }
