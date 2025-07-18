from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings"""

    # Application
    APP_NAME: str = "Currency Exchange API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Banxico API
    BANXICO_API_BASE_URL: str = (
        "https://www.banxico.org.mx/SieAPIRest/service/v1/series"
    )
    BANXICO_SERIES_ID: str = "SF43718"  # USD/MXN exchange rate
    BANXICO_TOKEN: str = ""

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_DECODE_RESPONSES: bool = True

    # Cache TTLs (seconds)
    CACHE_CURRENT_RATE_TTL: int = 300  # 5 minutes
    CACHE_HISTORICAL_RATE_TTL: int = 3600  # 1 hour
    CACHE_AVERAGE_RATE_TTL: int = 1800  # 30 minutes

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["*"]

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
