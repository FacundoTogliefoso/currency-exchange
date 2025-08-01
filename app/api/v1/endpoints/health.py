from fastapi import APIRouter

from app.services.health import full_health_check

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/",
    summary="Application health check",
    description="Returns comprehensive health status including all service dependencies (Banxico API and Redis cache).",
)
async def health_check():
    """
    Perform health check for the service and all dependencies.

    Returns:
        dict: Health status information including:
            - status: Overall health ("healthy" or "unhealthy")
            - services: List of individual service health statuses
            - checked_at: Timestamp of health check

    Response Examples:
        Healthy:
        {
            "status": "healthy",
            "services": [
                {"status": "healthy", "source": "banxico", "timestamp": "..."},
                {"status": "healthy", "source": "redis", "timestamp": "..."}
            ],
            "checked_at": "2025-07-18T15:30:00Z"
        }

        Unhealthy:
        {
            "status": "unhealthy",
            "services": [
                {"status": "unhealthy", "source": "banxico", "error": "...", "timestamp": "..."},
                {"status": "healthy", "source": "redis", "timestamp": "..."}
            ],
            "checked_at": "2025-07-18T15:30:00Z"
        }
    """
    return await full_health_check()
