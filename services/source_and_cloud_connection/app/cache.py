# services/source_and_cloud_connection/app/cache.py
import os, json, logging
from typing import Optional, Any
import redis.asyncio as aioredis

logger = logging.getLogger("source-connection-cache")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Cache key patterns:
#   sc:list:{owner}               → all connections for user  (TTL 60s)
#   sc:connection:{connection_id} → single connection detail  (TTL 30s)
#   sc:snapshot:{connection_id}   → latest source snapshot    (TTL 120s)


class SourceCacheManager:
    def __init__(self):
        self._client: Optional[aioredis.Redis] = None
        self._connected = False

    async def connect(self):
        try:
            self._client = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True,
                                             socket_timeout=2.0, socket_connect_timeout=2.0)
            await self._client.ping()
            self._connected = True
        except Exception as exc:
            self._connected = False
            self._client = None
            logger.warning(f"Redis unavailable: {exc}")

    async def disconnect(self):
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass
            finally:
                self._client = None
                self._connected = False

    async def _get(self, key: str) -> Optional[str]:
        if not self._connected or not self._client:
            return None
        try:
            return await self._client.get(key)
        except Exception:
            return None

    async def _set(self, key: str, value: str, ttl: int):
        if not self._connected or not self._client:
            return
        try:
            await self._client.set(key, value, ex=ttl)
        except Exception:
            pass

    async def _del(self, key: str):
        if not self._connected or not self._client:
            return
        try:
            await self._client.delete(key)
        except Exception:
            pass

    async def get_json(self, key: str) -> Optional[Any]:
        raw = await self._get(key)
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                pass
        return None

    async def set_json(self, key: str, value: Any, ttl: int = 60):
        await self._set(key, json.dumps(value), ttl)

    # ── Convenience methods ───────────────────────────────────────────────────

    # Git connection caching
    async def get_list(self, owner: str):       return await self.get_json(f"sc:list:{owner}")
    async def set_list(self, owner: str, d: Any): await self.set_json(f"sc:list:{owner}", d, 60)
    async def del_list(self, owner: str):       await self._del(f"sc:list:{owner}")

    async def get_conn(self, cid: str):          return await self.get_json(f"sc:connection:{cid}")
    async def set_conn(self, cid: str, d: Any):  await self.set_json(f"sc:connection:{cid}", d, 30)
    async def del_conn(self, cid: str):          await self._del(f"sc:connection:{cid}")

    async def get_snapshot(self, cid: str):      return await self.get_json(f"sc:snapshot:{cid}")
    async def set_snapshot(self, cid: str, d: Any): await self.set_json(f"sc:snapshot:{cid}", d, 120)
    async def del_snapshot(self, cid: str):      await self._del(f"sc:snapshot:{cid}")

    # Cloud connection caching
    async def get_cloud_list(self, owner: str): return await self.get_json(f"sc:cloud:list:{owner}")
    async def set_cloud_list(self, owner: str, d: Any): await self.set_json(f"sc:cloud:list:{owner}", d, 60)
    async def del_cloud_list(self, owner: str): await self._del(f"sc:cloud:list:{owner}")

    async def get_cloud_conn(self, cid: str): return await self.get_json(f"sc:cloud:conn:{cid}")
    async def set_cloud_conn(self, cid: str, d: Any): await self.set_json(f"sc:cloud:conn:{cid}", d, 30)
    async def del_cloud_conn(self, cid: str): await self._del(f"sc:cloud:conn:{cid}")

    async def invalidate_all(self, owner: str, cid: Optional[str] = None):
        await self.del_list(owner)
        await self.del_cloud_list(owner)
        if cid:
            await self.del_conn(cid)
            await self.del_snapshot(cid)
            await self.del_cloud_conn(cid)

    @property
    def is_connected(self) -> bool:
        return self._connected


cache_manager = SourceCacheManager()
