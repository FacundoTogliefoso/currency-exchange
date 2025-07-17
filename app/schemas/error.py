import datetime

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail structure"""

    code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    correlation_id: str = Field(..., description="Request correlation ID")
    timestamp: float = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC).timestamp()
    )
    details: str | None = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Standard error response"""

    error: ErrorDetail = Field(
        ...,
        example={
            "code": 502,
            "message": "External API unavailable",
            "correlation_id": "req-1642345678000",
            "timestamp": 1642345678.123,
            "details": "Circuit breaker is open",
        },
    )
