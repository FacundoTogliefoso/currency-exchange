import logging

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Async Redis client wrapper with logging and error handling."""

    def __init__(self):
        self._client: redis.Redis | None = None

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD or None,
                decode_responses=settings.REDIS_DECODE_RESPONSES,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
        return self._client

    async def ping(self) -> bool:
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    async def get(self, key: str) -> str | None:
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return None

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        try:
            return await self.client.set(key, value, ex=ex)
        except Exception as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False

    async def setex(self, key: str, time: int, value: str) -> bool:
        try:
            return await self.client.setex(key, time, value)
        except Exception as e:
            logger.error(f"Redis SETEX error for key '{key}': {e}")
            return False

    async def delete(self, *keys: str) -> int:
        try:
            return await self.client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE error for keys {keys}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        try:
            return bool(await self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key '{key}': {e}")
            return False

    async def close(self):
        """Close Redis connection"""
        if self._client:
            await self._client.close()
            self._client = None


# Global Redis client singleton
redis_client = RedisClient()
