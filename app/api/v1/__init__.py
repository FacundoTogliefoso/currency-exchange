from fastapi import APIRouter

from app.api.v1.endpoints import health, rates

api_router = APIRouter()

api_router.include_router(rates.router)
api_router.include_router(health.router)
