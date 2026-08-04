"""
Cache abstraction used by read-heavy endpoints (skills/roles list, analytics,
job listings). Defaults to an in-process TTL cache so the app runs with zero
extra infra; switches to Redis transparently when REDIS_URL is configured.
"""
from __future__ import annotations

import json
from typing import Any

from cachetools import TTLCache

from app.core.config import get_settings

settings = get_settings()
_memory_cache: TTLCache = TTLCache(maxsize=2048, ttl=settings.CACHE_TTL_SECONDS)

_redis_client = None
if settings.REDIS_URL:
    import redis.asyncio as redis
    _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class Cache:
    """Unified async-friendly cache interface (works with or without Redis)."""

    @staticmethod
    async def get(key: str) -> Any | None:
        if _redis_client:
            raw = await _redis_client.get(key)
            return json.loads(raw) if raw else None
        return _memory_cache.get(key)

    @staticmethod
    async def set(key: str, value: Any, ttl: int | None = None) -> None:
        if _redis_client:
            await _redis_client.set(key, json.dumps(value), ex=ttl or settings.CACHE_TTL_SECONDS)
        else:
            _memory_cache[key] = value

    @staticmethod
    async def delete(key: str) -> None:
        if _redis_client:
            await _redis_client.delete(key)
        else:
            _memory_cache.pop(key, None)


cache = Cache()
