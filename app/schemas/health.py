import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

DATETIME_NOW = datetime.datetime.now(datetime.timezone.utc)


class HealthStatus(BaseModel):
    status: str
    timestamp: datetime = Field(default_factory=DATETIME_NOW)
    version: str
    uptime_seconds: int


class DependencyStatus(BaseModel):
    name: str
    status: str
    response_time_ms: Optional[float] = None
    last_check: datetime = Field(default_factory=DATETIME_NOW)
    details: Optional[str] = None


class DetailedHealthResponse(BaseModel):
    status: str
    timestamp: datetime = Field(default_factory=DATETIME_NOW)
    version: str
    uptime_seconds: int
    dependencies: List[DependencyStatus]
    performance: Dict[str, Any] = Field(default_factory=dict)
