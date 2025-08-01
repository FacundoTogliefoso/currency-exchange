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
        if settings.BANXICO_TOKEN:
            params["token"] = settings.BANXICO_TOKEN

        headers = {
            "Accept": "application/json",
            "User-Agent": "RatesService/1.0",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Making request to Banxico API: {endpoint}")
                response = await client.get(endpoint, params=params, headers=headers)
                response.raise_for_status()

                raw_data = response.json()
                logger.info(f"Banxico API response: {raw_data}")

                if not raw_data.get("bmx") or not raw_data["bmx"].get("series"):
                    logger.error(f"Invalid Banxico response structure: {raw_data}")
                    raise HTTPException(
                        status_code=502,
                        detail="Invalid response format from Banxico API",
                    )

                series = raw_data["bmx"]["series"][0]
                if not series.get("datos"):
                    logger.warning(f"No data in Banxico response for {endpoint}")
                    if "oportuno" in endpoint:
                        logger.info(
                            "Trying with recent date range instead of /oportuno"
                        )
                        from datetime import date, timedelta

                        end_date = date.today()
                        start_date = end_date - timedelta(days=5)
                        return await self.fetch_series(
                            start_date=start_date.strftime("%d-%m-%Y"),
                            end_date=end_date.strftime("%d-%m-%Y"),
                        )

                    raise HTTPException(
                        status_code=404,
                        detail="No exchange rate data available from Banxico",
                    )

                return BanxicoResponse.model_validate(raw_data)

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

        except HTTPException:
            # Re-raise HTTP exceptions (our custom ones)
            raise

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(
                status_code=502, detail="Banxico service unavailable"
            ) from e


# Singleton
banxico_api = BanxicoAPI()
