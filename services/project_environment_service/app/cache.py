# services/project_and_environment_management/app/cache.py
import os
import json
import logging
from typing import Optional, Any
import redis.asyncio as aioredis

logger = logging.getLogger("project-manager-cache")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Cache key patterns
# projects:list:{owner}       → list of all projects for an owner   (TTL 60s)
# project:detail:{project_id} → project + its environments          (TTL 30s)


class ProjectCacheManager:
    def __init__(self):
        self._client: Optional[aioredis.Redis] = None
        self._connected = False

    async def connect(self):
        try:
            self._client = aioredis.from_url(
                REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
            )
            await self._client.ping()
            self._connected = True
            logger.info("Project Manager: Redis connected.")
        except Exception as exc:
            self._connected = False
            self._client = None
            logger.warning(f"Project Manager: Redis unavailable ({exc}). Running cache-less.")

    async def disconnect(self):
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass
            finally:
                self._client = None
                self._connected = False

    # ── Low-level ─────────────────────────────────────────────────────────────

    async def _get(self, key: str) -> Optional[str]:
        if not self._connected or not self._client:
            return None
        try:
            return await self._client.get(key)
        except Exception:
            return None

    async def _set(self, key: str, value: str, ttl: int) -> bool:
        if not self._connected or not self._client:
            return False
        try:
            await self._client.set(key, value, ex=ttl)
            return True
        except Exception:
            return False

    async def _delete(self, key: str):
        if not self._connected or not self._client:
            return
        try:
            await self._client.delete(key)
        except Exception:
            pass

    # ── Project list cache ────────────────────────────────────────────────────

    async def get_projects_list(self, owner: str) -> Optional[Any]:
        raw = await self._get(f"projects:list:{owner}")
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                pass
        return None

    async def set_projects_list(self, owner: str, data: Any):
        await self._set(f"projects:list:{owner}", json.dumps(data), ttl=60)

    async def invalidate_projects_list(self, owner: str):
        await self._delete(f"projects:list:{owner}")

    # ── Project detail cache ──────────────────────────────────────────────────

    async def get_project_detail(self, project_id: str) -> Optional[Any]:
        raw = await self._get(f"project:detail:{project_id}")
        if raw:
            try:
                return json.loads(raw)
            except Exception:
                pass
        return None

    async def set_project_detail(self, project_id: str, data: Any):
        await self._set(f"project:detail:{project_id}", json.dumps(data), ttl=30)

    async def invalidate_project_detail(self, project_id: str):
        await self._delete(f"project:detail:{project_id}")

    # ── Bulk invalidation ─────────────────────────────────────────────────────

    async def invalidate_all_for_owner(self, owner: str, project_id: Optional[str] = None):
        await self.invalidate_projects_list(owner)
        if project_id:
            await self.invalidate_project_detail(project_id)

    @property
    def is_connected(self) -> bool:
        return self._connected


# Global singleton
cache_manager = ProjectCacheManager()
