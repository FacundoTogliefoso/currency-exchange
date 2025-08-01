import json
import logging
from datetime import date, timedelta

from app.core.redis import redis_client
from app.schemas.rates import ExchangeRateData
from app.services.banxico import banxico_api

logger = logging.getLogger(__name__)

# Cache TTLs
CURRENT_RATE_TTL = 300  # 5 minutes
HISTORICAL_RATE_TTL = 3600  # 1 hour
AVERAGE_RATE_TTL = 1800  # 30 minutes


def _parse_date(date_str: str) -> date:
    """Parse '16/07/2025' → date(2025, 7, 16)"""
    day, month, year = map(int, date_str.split("/"))
    return date(year, month, day)


async def get_current_exchange_rate() -> ExchangeRateData | None:
    """Return the most recent exchange rate, using cache if available."""
    cache_key = "rates:current"

    try:
        cached = await redis_client.get(cache_key)
        if cached:
            logger.debug("Cache hit for current rate")
            data = json.loads(cached)
            return ExchangeRateData(
                date=date.fromisoformat(data["date"]),
                rate=data["rate"],
                source=data["source"],
            )
    except Exception as e:
        logger.warning(f"Cache error for current rate: {e}")

    logger.debug("Cache miss for current rate — calling Banxico API")
    response = await banxico_api.fetch_series()

    if (
        not response.bmx
        or not hasattr(response.bmx, "series")
        or not response.bmx.series
    ):
        logger.error("No series data in Banxico response")
        return None

    series = response.bmx.series[0]
    if not hasattr(series, "datos") or not series.datos:
        logger.error("No datos in series")
        return None

    latest = series.datos[0]
    rate_data = ExchangeRateData(
        date=_parse_date(latest.fecha), rate=float(latest.dato), source="banxico"
    )

    try:
        cache_data = {
            "date": rate_data.date.isoformat(),
            "rate": rate_data.rate,
            "source": rate_data.source,
        }
        await redis_client.setex(cache_key, CURRENT_RATE_TTL, json.dumps(cache_data))
    except Exception as e:
        logger.warning(f"Failed to cache current rate: {e}")

    return rate_data


async def get_historical_rates(days: int = 10) -> list[ExchangeRateData]:
    """Return exchange rates for the last N business days"""
    cache_key = f"rates:historical:{days}"

    try:
        cached = await redis_client.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for historical {days}d")
            data = json.loads(cached)
            return [
                ExchangeRateData(
                    date=date.fromisoformat(item["date"]),
                    rate=item["rate"],
                    source=item["source"],
                )
                for item in data
            ]
    except Exception as e:
        logger.warning(f"Cache error for historical {days}d: {e}")

    logger.debug(f"Cache miss for historical {days}d — calling Banxico API")
    end = date.today()
    start = end - timedelta(days=days + 10)

    response = await banxico_api.fetch_series(
        start_date=start.strftime("%Y-%m-%d"), end_date=end.strftime("%Y-%m-%d")
    )

    if (
        not response.bmx
        or not hasattr(response.bmx, "series")
        or not response.bmx.series
    ):
        return []

    series = response.bmx.series[0]
    if not hasattr(series, "datos") or not series.datos:
        return []

    rates = []
    for item in series.datos:
        if item.dato == "N/E":
            continue
        parsed_date = _parse_date(item.fecha)
        if parsed_date.weekday() < 5:
            rates.append(
                ExchangeRateData(
                    date=parsed_date, rate=float(item.dato), source="banxico"
                )
            )

    result = sorted(rates, key=lambda x: x.date, reverse=True)[:days]

    try:
        cache_data = [
            {"date": rate.date.isoformat(), "rate": rate.rate, "source": rate.source}
            for rate in result
        ]
        await redis_client.setex(cache_key, HISTORICAL_RATE_TTL, json.dumps(cache_data))
    except Exception as e:
        logger.warning(f"Failed to cache historical {days}d: {e}")

    return result


async def get_average_rate(days: int = 15) -> float | None:
    """Calculate the average exchange rate over last N business days"""
    rates = await get_historical_rates(days=days)
    if not rates:
        return None
    return sum(r.rate for r in rates) / len(rates)
