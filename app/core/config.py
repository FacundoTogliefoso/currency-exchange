# app/core/config.py
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    BANXICO_API_BASE_URL: str = os.getenv(
        "BANXICO_API_BASE_URL", "https://www.banxico.org.mx/SieAPIRest/service/v1"
    )
    BANXICO_SERIES_ID: str = os.getenv("BANXICO_SERIES_ID", "SF43718")
    BANXICO_TOKEN: str = os.getenv(
        "BANXICO_TOKEN",
        "df74d3cc6606b977710db7b12feae415afac4cb863229e872ec5f593a843e5c8",
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")


settings = Settings()
