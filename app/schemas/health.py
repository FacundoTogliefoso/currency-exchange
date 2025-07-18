# app/schemas/health.py
import datetime
from typing import Any

from pydantic import BaseModel, Field


def get_timestamp():
    """Get current UTC timestamp"""
    return datetime.datetime.now(datetime.UTC)


class HealthStatus(BaseModel):
    status: str
    timestamp: datetime.datetime = Field(default_factory=get_timestamp)
    version: str
    uptime_seconds: int


class DependencyStatus(BaseModel):
    name: str
    status: str
    response_time_ms: float | None = None
    last_check: datetime.datetime = Field(default_factory=get_timestamp)
    details: str | None = None


class DetailedHealthResponse(BaseModel):
    status: str
    timestamp: datetime.datetime = Field(default_factory=get_timestamp)
    version: str
    uptime_seconds: int
    dependencies: list[DependencyStatus]
    performance: dict[str, Any] = Field(default_factory=dict)
