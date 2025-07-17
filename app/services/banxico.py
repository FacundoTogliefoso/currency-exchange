import logging

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.banxico import BanxicoResponse

logger = logging.getLogger(__name__)


class BanxicoAPI:
    def __init__(self):
        self.base_url = settings.BANXICO_API_BASE_URL
        self.series_id = settings.BANXICO_SERIES_ID
        self.timeout = 10.0

    async def fetch_series(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> BanxicoResponse:
        """
        Fetches exchange rate data from Banxico for a given date range
        or the latest available value if no range is provided.
        """
        endpoint = f"{self.base_url}/{self.series_id}/datos"
        if start_date and end_date:
            endpoint += f"/{start_date}/{end_date}"
        else:
            endpoint += "/oportuno"

        params = {"mediaType": "json"}
        headers = {
            "token": settings.BANXICO_TOKEN,
            "Accept": "application/json",
            "User-Agent": "RatesService/1.0",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, params=params, headers=headers)
                response.raise_for_status()
                return BanxicoResponse.model_validate(response.json())

        except httpx.TimeoutException as e:
            logger.error(f"Timeout calling Banxico API: {endpoint}")
            raise HTTPException(status_code=504, detail="Banxico API timeout") from e

        except httpx.HTTPStatusError as e:
            error_text = e.response.text
            logger.error(
                f"HTTP error {e.response.status_code} from Banxico: {error_text}"
            )
            raise HTTPException(
                status_code=502, detail="Banxico API returned an error"
            ) from e

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(
                status_code=502, detail="Banxico service unavailable"
            ) from e


# Singleton
banxico_api = BanxicoAPI()
