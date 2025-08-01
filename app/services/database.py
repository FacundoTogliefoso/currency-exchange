import logging
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError

from app.core.database import ExchangeRate, db_manager
from app.schemas.rates import ExchangeRateData

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations"""

    async def save_exchange_rate(self, rate_data: ExchangeRateData) -> bool:
        """Save exchange rate to database"""
        try:
            async with db_manager.get_session() as session:
                existing = await session.execute(
                    select(ExchangeRate).where(ExchangeRate.date == rate_data.date)
                )
                existing_rate = existing.scalar_one_or_none()

                if existing_rate:
                    existing_rate.rate = rate_data.rate
                    existing_rate.source = rate_data.source
                    existing_rate.updated_at = datetime.now(timezone.utc)
                    logger.debug(
                        f"Updated exchange rate for {rate_data.date}: {rate_data.rate}"
                    )
                else:
                    new_rate = ExchangeRate(
                        date=datetime.combine(rate_data.date, datetime.min.time()),
                        rate=rate_data.rate,
                        source=rate_data.source,
                    )
                    session.add(new_rate)
                    logger.debug(
                        f"Inserted new exchange rate for {rate_data.date}: {rate_data.rate}"
                    )

                return True

        except IntegrityError as e:
            logger.warning(f"Exchange rate already exists for {rate_data.date}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to save exchange rate: {e}")
            return False

    async def get_latest_exchange_rate(self) -> Optional[ExchangeRateData]:
        """Get the most recent exchange rate from database"""
        try:
            async with db_manager.get_session() as session:
                result = await session.execute(
                    select(ExchangeRate).order_by(ExchangeRate.date.desc()).limit(1)
                )
                rate_record = result.scalar_one_or_none()

                if rate_record:
                    return ExchangeRateData(
                        date=rate_record.date.date(),
                        rate=rate_record.rate,
                        source=rate_record.source,
                    )
                return None

        except Exception as e:
            logger.error(f"Failed to get latest exchange rate: {e}")
            return None

    async def get_historical_rates(self, days: int = 10) -> List[ExchangeRateData]:
        """Get historical exchange rates from database"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days + 10)

            async with db_manager.get_session() as session:
                result = await session.execute(
                    select(ExchangeRate)
                    .where(
                        and_(
                            ExchangeRate.date
                            >= datetime.combine(start_date, datetime.min.time()),
                            ExchangeRate.date
                            <= datetime.combine(end_date, datetime.max.time()),
                        )
                    )
                    .order_by(ExchangeRate.date.desc())
                    .limit(days)
                )
                rate_records = result.scalars().all()

                return [
                    ExchangeRateData(
                        date=record.date.date(), rate=record.rate, source=record.source
                    )
                    for record in rate_records
                ]

        except Exception as e:
            logger.error(f"Failed to get historical rates: {e}")
            return []

    async def get_average_rate(self, days: int = 15) -> Optional[float]:
        """Calculate average rate from database"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            async with db_manager.get_session() as session:
                result = await session.execute(
                    select(func.avg(ExchangeRate.rate)).where(
                        and_(
                            ExchangeRate.date
                            >= datetime.combine(start_date, datetime.min.time()),
                            ExchangeRate.date
                            <= datetime.combine(end_date, datetime.max.time()),
                        )
                    )
                )
                avg_rate = result.scalar()

                return float(avg_rate) if avg_rate else None

        except Exception as e:
            logger.error(f"Failed to calculate average rate: {e}")
            return None

    async def get_rate_count(self) -> int:
        """Get total number of rates in database"""
        try:
            async with db_manager.get_session() as session:
                result = await session.execute(select(func.count(ExchangeRate.id)))
                return result.scalar() or 0
        except Exception as e:
            logger.error(f"Failed to get rate count: {e}")
            return 0


database_service = DatabaseService()
