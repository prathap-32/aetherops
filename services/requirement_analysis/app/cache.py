# services/requirement_analysis/app/cache.py
import os
import logging
import json
from typing import Optional, Any
import redis.asyncio as aioredis

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
        Sets a key-value pair in Redis with an optional TTL (defaults to 1 hour).
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
