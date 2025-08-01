import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


def get_timestamp():
    """Get current UTC timestamp"""
    return datetime.datetime.now(datetime.timezone.utc)


class ExchangeRateData(BaseModel):
    date: datetime.date
    rate: float = Field(..., gt=0)
    source: str = Field(default="banxico")


class CurrentRateResponse(BaseModel):
    data: ExchangeRateData
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime.datetime = Field(default_factory=get_timestamp)
    cache_hit: bool = Field(default=False)


class AverageRateData(BaseModel):
    period: str
    average_rate: float = Field(..., gt=0)
    data_points: int = Field(..., gt=0)
    start_date: datetime.date
    end_date: datetime.date

    @field_validator("period")
    @classmethod
    def validate_period(cls, v):
        if v not in ["15d", "30d"]:
            raise ValueError("Period must be either 15d or 30d")
        return v


class AverageRateResponse(BaseModel):
    data: AverageRateData
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime.datetime = Field(default_factory=get_timestamp)
    cache_hit: bool = Field(default=False)


class HistoricalRateResponse(BaseModel):
    data: list[ExchangeRateData]
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime.datetime = Field(default_factory=get_timestamp)
    cache_hit: bool = Field(default=False)

    @field_validator("data")
    @classmethod
    def validate_data_not_empty(cls, v):
        if not v:
            raise ValueError("Historical data cannot be empty")
        return v
