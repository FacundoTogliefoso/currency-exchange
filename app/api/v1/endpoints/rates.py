from fastapi import APIRouter, HTTPException, Query

from app.schemas.rates import ExchangeRateData
from app.services import rates as rate_service

router = APIRouter(prefix="/rates", tags=["Rates"])


@router.get(
    "/current",
    response_model=ExchangeRateData,
    summary="Get current USD/MXN exchange rate",
    description="Returns the most recent USD/MXN exchange rate from Banxico with 5-minute caching.",
)
async def get_current_rate():
    """
    Get the latest USD/MXN exchange rate.

    Returns:
        ExchangeRateData: Current exchange rate with date and source information
    """
    rate = await rate_service.get_current_exchange_rate()
    if not rate:
        raise HTTPException(status_code=404, detail="No current rate available")
    return rate


@router.get(
    "/historical",
    response_model=list[ExchangeRateData],
    summary="Get historical USD/MXN exchange rates",
    description="Returns historical USD/MXN exchange rates for the specified number of business days (excludes weekends).",
)
async def get_historical_rates(
    days: int = Query(
        default=10,
        ge=1,
        le=90,
        description="Number of business days to retrieve (1-90)",
    )
):
    """
    Get historical exchange rates for the last N business days (Monday-Friday).
    Weekends are automatically filtered out.

    Args:
        days: Number of business days to retrieve (1-90). Default is 10.

    Returns:
        List[ExchangeRateData]: List of exchange rates sorted by date (most recent first)
    """
    return await rate_service.get_historical_rates(days=days)


@router.get(
    "/average",
    response_model=float,
    summary="Get average USD/MXN exchange rate",
    description="Returns the arithmetic mean of USD/MXN exchange rates over the specified number of business days.",
)
async def get_average_rate(
    days: int = Query(
        default=15,
        ge=1,
        le=90,
        description="Number of business days for average calculation (1-90)",
    )
):
    """
    Get the average exchange rate for the last N business days.

    Args:
        days: Number of business days for calculation (1-90). Default is 15.

    Returns:
        float: Average exchange rate rounded to 4 decimal places
    """
    rate = await rate_service.get_average_rate(days=days)
    if rate is None:
        raise HTTPException(status_code=404, detail="No data to calculate average")
    return round(rate, 4)
