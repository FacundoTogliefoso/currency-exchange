import datetime
import logging
from contextlib import asynccontextmanager

from sqlalchemy import Column, DateTime, Float, Index, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_timestamp():
    """Get current UTC timestamp"""
    return datetime.datetime.now(datetime.timezone.utc)


class Base(DeclarativeBase):
    pass


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, unique=True)
    rate = Column(Float, nullable=False)
    source = Column(String(50), nullable=False, default="banxico")
    created_at = Column(DateTime, default=get_timestamp())
    updated_at = Column(DateTime, default=get_timestamp(), onupdate=get_timestamp())

    __table_args__ = (
        Index("idx_date", "date"),
        Index("idx_date_source", "date", "source"),
        Index("idx_created_at", "created_at"),
    )


class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.session_maker = None

    async def init_db(self):
        """Initialize database connection"""
        try:
            self.engine = create_async_engine(
                settings.database_url,
                echo=settings.DEBUG,
                pool_size=settings.DATABASE_MAX_CONNECTIONS,
                max_overflow=0,
                pool_pre_ping=True,
                pool_recycle=3600,
            )

            self.session_maker = async_sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )

            logger.info(
                f"Database connected: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}"
            )

        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    async def create_tables(self):
        """Create database tables"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            raise

    async def close_db(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")

    @asynccontextmanager
    async def get_session(self):
        """Get database session with automatic cleanup"""
        async with self.session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def health_check(self) -> bool:
        """Check database health"""
        try:
            async with self.get_session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


db_manager = DatabaseManager()
