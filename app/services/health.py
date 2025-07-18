import datetime
import logging

from app.core.redis import redis_client
from app.services.banxico import banxico_api

logger = logging.getLogger(__name__)


def get_timestamp():
    """Get current UTC timestamp"""
    return datetime.datetime.now(datetime.UTC).isoformat()


async def check_banxico_status() -> dict:
    """Checks whether Banxico API is healthy."""
    try:
        response = await banxico_api.fetch_series()
        if (
            not response.bmx
            or not hasattr(response.bmx, "series")
            or not response.bmx.series
        ):
            raise ValueError("Unexpected Banxico response format")

        return {"status": "healthy", "source": "banxico", "timestamp": get_timestamp()}
    except Exception as e:
        logger.error(f"Banxico health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "source": "banxico",
            "error": str(e),
            "timestamp": get_timestamp(),
        }


async def check_redis_status() -> dict:
    """Checks whether Redis is reachable."""
    try:
        pong = await redis_client.ping()
        return {
            "status": "healthy" if pong else "unhealthy",
            "source": "redis",
            "timestamp": get_timestamp(),
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "source": "redis",
            "error": str(e),
            "timestamp": get_timestamp(),
        }


async def full_health_check() -> dict:
    """Performs full system health check."""
    banxico = await check_banxico_status()
    redis = await check_redis_status()

    healthy = all(s["status"] == "healthy" for s in [banxico, redis])

    return {
        "status": "healthy" if healthy else "unhealthy",
        "services": [banxico, redis],
        "checked_at": get_timestamp(),
    }
