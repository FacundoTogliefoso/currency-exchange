from functools import lru_cache

import aioredis

from app.core.config import settings


@lru_cache
def get_redis_client():
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


redis_client = get_redis_client()
