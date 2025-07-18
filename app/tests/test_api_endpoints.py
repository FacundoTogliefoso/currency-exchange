from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.schemas.rates import ExchangeRateData
from main import app


class TestRatesAPI:

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_current_rate_success(self, client):
        """Test successful current rate retrieval"""
        mock_rate = ExchangeRateData(date="2025-07-18", rate=18.7200, source="banxico")

        with patch(
            "app.services.rates.get_current_exchange_rate", return_value=mock_rate
        ):
            response = client.get("/api/v1/rates/current")
            assert response.status_code == 200
            data = response.json()
            assert data["rate"] == 18.7200
            assert data["source"] == "banxico"

    def test_current_rate_not_found(self, client):
        """Test current rate when no data available"""
        with patch("app.services.rates.get_current_exchange_rate", return_value=None):
            response = client.get("/api/v1/rates/current")
            assert response.status_code == 404
            assert "No current rate available" in response.json()["detail"]

    def test_historical_rates_success(self, client):
        """Test successful historical rates retrieval"""
        mock_rates = [
            ExchangeRateData(date="2025-07-18", rate=18.7200, source="banxico"),
            ExchangeRateData(date="2025-07-17", rate=18.6800, source="banxico"),
        ]

        with patch("app.services.rates.get_historical_rates", return_value=mock_rates):
            response = client.get("/api/v1/rates/historical?days=2")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["rate"] == 18.7200

    def test_historical_rates_invalid_days(self, client):
        """Test historical rates with invalid parameters"""
        response = client.get("/api/v1/rates/historical?days=0")
        assert response.status_code == 422

        response = client.get("/api/v1/rates/historical?days=100")
        assert response.status_code == 422

    def test_average_rate_success(self, client):
        """Test successful average rate calculation"""
        with patch("app.services.rates.get_average_rate", return_value=18.6733):
            response = client.get("/api/v1/rates/average?days=15")
            assert response.status_code == 200
            assert response.json() == 18.6733

    def test_average_rate_no_data(self, client):
        """Test average rate when no data available"""
        with patch("app.services.rates.get_average_rate", return_value=None):
            response = client.get("/api/v1/rates/average")
            assert response.status_code == 404


class TestHealthAPI:

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_health_endpoint_healthy(self, client):
        """Test health endpoint when all services are healthy"""
        mock_response = {
            "status": "healthy",
            "services": [
                {"status": "healthy", "source": "banxico"},
                {"status": "healthy", "source": "redis"},
            ],
            "checked_at": "2025-07-18T20:00:00Z",
        }

        with patch("app.services.health.full_health_check", return_value=mock_response):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert len(data["services"]) == 2

    def test_health_endpoint_unhealthy(self, client):
        """Test health endpoint when services are unhealthy"""
        mock_response = {
            "status": "unhealthy",
            "services": [
                {"status": "unhealthy", "source": "banxico", "error": "API error"},
                {"status": "healthy", "source": "redis"},
            ],
            "checked_at": "2025-07-18T20:00:00Z",
        }

        with patch("app.services.health.full_health_check", return_value=mock_response):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
