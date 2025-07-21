from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings"""

    APP_NAME: str = "Currency Exchange API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["*"]
    LOG_LEVEL: str = "INFO"

    BANXICO_API_BASE_URL: str = (
        "https://www.banxico.org.mx/SieAPIRest/service/v1/series"
    )
    BANXICO_SERIES_ID: str = "SF43718"  # USD/MXN exchange rate
    BANXICO_TOKEN: str = ""
    BANXICO_TIMEOUT: int = 10

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DECODE_RESPONSES: bool = True
    REDIS_MAX_CONNECTIONS: int = 20

    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_NAME: str = "currency_exchange"
    DATABASE_USERNAME: str = "admin"
    DATABASE_PASSWORD: str = ""
    DATABASE_MAX_CONNECTIONS: int = 20
    DATABASE_MIN_CONNECTIONS: int = 5

    AWS_REGION: str = "us-west-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    DATABASE_SECRET_ARN: Optional[str] = None
    BANXICO_SECRET_ARN: Optional[str] = None

    CACHE_CURRENT_RATE_TTL: int = 300  # 5 minutes
    CACHE_HISTORICAL_RATE_TTL: int = 3600  # 1 hour
    CACHE_AVERAGE_RATE_TTL: int = 1800  # 30 minutes

    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 3
    CIRCUIT_BREAKER_TIMEOUT_DURATION: int = 30

    HEALTH_CHECK_TIMEOUT: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        """Construct database URL"""
        return f"mysql+aiomysql://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    @property
    def redis_url(self) -> str:
        """Construct Redis URL"""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT.lower() == "development"


settings = Settings()
