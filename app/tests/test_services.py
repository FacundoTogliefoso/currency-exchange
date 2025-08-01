from datetime import date
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi import HTTPException

from app.schemas.banxico import BanxicoResponse
from app.schemas.rates import ExchangeRateData
from app.services import health, rates
from app.services.banxico import BanxicoAPI


class TestBanxicoService:

    @pytest.fixture
    def banxico_service(self):
        return BanxicoAPI()

    @pytest.mark.asyncio
    async def test_fetch_series_success(self):
        """Test successful series fetch from Banxico API"""
        mock_response_data = {
            "bmx": {
                "series": [
                    {
                        "idSerie": "SF43718",
                        "titulo": "Tipo de cambio Pesos por dólar E.U.A.",
                        "datos": [{"fecha": "18/07/2025", "dato": "18.7200"}],
                    }
                ]
            }
        }

        banxico_service = BanxicoAPI()

        with patch.object(banxico_service, "fetch_series") as mock_fetch:
            mock_fetch.return_value = BanxicoResponse.model_validate(mock_response_data)

            result = await banxico_service.fetch_series()

            assert result.bmx.series[0].idSerie == "SF43718"
            assert len(result.bmx.series[0].datos) == 1
            assert result.bmx.series[0].datos[0].dato == "18.7200"

    @pytest.mark.asyncio
    async def test_fetch_series_timeout(self, banxico_service):
        """Test timeout handling"""
        with patch(
            "httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Timeout")
        ):
            with pytest.raises(HTTPException) as exc_info:
                await banxico_service.fetch_series()

            assert exc_info.value.status_code == 504

    @pytest.mark.asyncio
    async def test_fetch_series_http_error(self, banxico_service):
        """Test HTTP error handling"""
        mock_response = AsyncMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        with patch(
            "httpx.AsyncClient.get",
            side_effect=httpx.HTTPStatusError(
                "400 Bad Request", request=None, response=mock_response
            ),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await banxico_service.fetch_series()

            assert exc_info.value.status_code == 502


class TestRatesService:

    @pytest.mark.asyncio
    async def test_get_current_exchange_rate_cache_miss(self):
        """Test current rate with cache miss"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        mock_banxico = AsyncMock()
        mock_banxico.fetch_series.return_value.bmx.series = [
            type(
                "obj",
                (object,),
                {
                    "datos": [
                        type(
                            "obj", (object,), {"fecha": "18/07/2025", "dato": "18.7200"}
                        )
                    ]
                },
            )
        ]

        with (
            patch("app.services.rates.redis_client", mock_redis),
            patch("app.services.rates.banxico_api", mock_banxico),
        ):

            result = await rates.get_current_exchange_rate()

            assert isinstance(result, ExchangeRateData)
            assert result.rate == 18.7200
            mock_banxico.fetch_series.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_current_exchange_rate_no_data(self):
        """Test current rate when Banxico returns no data"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        mock_banxico = AsyncMock()
        mock_banxico.fetch_series.return_value.bmx = None

        with (
            patch("app.services.rates.redis_client", mock_redis),
            patch("app.services.rates.banxico_api", mock_banxico),
        ):

            result = await rates.get_current_exchange_rate()
            assert result is None

    @pytest.mark.asyncio
    async def test_get_historical_rates_success(self):
        """Test successful historical rates retrieval"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None

        mock_banxico = AsyncMock()
        mock_banxico.fetch_series.return_value.bmx.series = [
            type(
                "obj",
                (object,),
                {
                    "datos": [
                        type(
                            "obj", (object,), {"fecha": "18/07/2025", "dato": "18.7200"}
                        ),
                        type(
                            "obj", (object,), {"fecha": "17/07/2025", "dato": "18.6800"}
                        ),
                    ]
                },
            )
        ]

        with (
            patch("app.services.rates.redis_client", mock_redis),
            patch("app.services.rates.banxico_api", mock_banxico),
        ):

            result = await rates.get_historical_rates(days=2)

            assert len(result) <= 2
            assert all(isinstance(rate, ExchangeRateData) for rate in result)

    @pytest.mark.asyncio
    async def test_get_average_rate_success(self):
        """Test successful average rate calculation"""
        mock_rates = [
            ExchangeRateData(date=date(2025, 7, 18), rate=18.70, source="banxico"),
            ExchangeRateData(date=date(2025, 7, 17), rate=18.80, source="banxico"),
        ]

        with patch("app.services.rates.get_historical_rates", return_value=mock_rates):
            result = await rates.get_average_rate(days=2)

            expected_average = (18.70 + 18.80) / 2
            assert abs(result - expected_average) < 0.01

    @pytest.mark.asyncio
    async def test_get_average_rate_no_data(self):
        """Test average rate when no historical data available"""
        with patch("app.services.rates.get_historical_rates", return_value=[]):
            result = await rates.get_average_rate(days=15)
            assert result is None

    def test_parse_date_function(self):
        """Test date parsing utility function"""
        result = rates._parse_date("18/07/2025")
        expected = date(2025, 7, 18)
        assert result == expected


class TestHealthService:

    @pytest.mark.asyncio
    async def test_check_banxico_status_healthy(self):
        """Test Banxico health check success"""
        mock_banxico = AsyncMock()
        mock_banxico.fetch_series.return_value.bmx.series = [{"datos": []}]

        with patch("app.services.health.banxico_api", mock_banxico):
            result = await health.check_banxico_status()

            assert result["status"] == "healthy"
            assert result["source"] == "banxico"

    @pytest.mark.asyncio
    async def test_check_banxico_status_unhealthy(self):
        """Test Banxico health check failure"""
        mock_banxico = AsyncMock()
        mock_banxico.fetch_series.side_effect = Exception("API Error")

        with patch("app.services.health.banxico_api", mock_banxico):
            result = await health.check_banxico_status()

            assert result["status"] == "unhealthy"
            assert "error" in result

    @pytest.mark.asyncio
    async def test_check_redis_status_healthy(self):
        """Test Redis health check success"""
        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True

        with patch("app.services.health.redis_client", mock_redis):
            result = await health.check_redis_status()

            assert result["status"] == "healthy"
            assert result["source"] == "redis"

    @pytest.mark.asyncio
    async def test_check_redis_status_unhealthy(self):
        """Test Redis health check failure"""
        mock_redis = AsyncMock()
        mock_redis.ping.side_effect = Exception("Connection failed")

        with patch("app.services.health.redis_client", mock_redis):
            result = await health.check_redis_status()

            assert result["status"] == "unhealthy"
            assert "error" in result

    @pytest.mark.asyncio
    async def test_full_health_check(self):
        """Test full health check combining all services"""
        mock_banxico_result = {"status": "healthy", "source": "banxico"}
        mock_redis_result = {"status": "healthy", "source": "redis"}

        with (
            patch(
                "app.services.health.check_banxico_status",
                return_value=mock_banxico_result,
            ),
            patch(
                "app.services.health.check_redis_status", return_value=mock_redis_result
            ),
        ):

            result = await health.full_health_check()

            assert result["status"] == "healthy"
            assert len(result["services"]) == 2
            assert "checked_at" in result
