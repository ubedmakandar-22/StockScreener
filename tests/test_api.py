"""Tests for API endpoints."""

import pytest
from unittest.mock import patch, MagicMock


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test GET /api/v1/health."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "UP"
        assert "timestamp" in data


class TestScanEndpoints:
    """Test scanner endpoints."""

    @patch("api.routes.scanner_engine")
    def test_daily_scan_endpoint(self, mock_engine, client):
        """Test GET /api/v1/scan/daily."""
        mock_engine.scan_all.return_value = []

        response = client.get("/api/v1/scan/daily")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["count"] == 0

    @patch("api.routes.scanner_engine")
    def test_weekly_scan_endpoint(self, mock_engine, client):
        """Test GET /api/v1/scan/weekly."""
        mock_engine.scan_all.return_value = []

        response = client.get("/api/v1/scan/weekly")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["count"] == 0

    @patch("api.routes.scanner_engine")
    def test_monthly_scan_endpoint(self, mock_engine, client):
        """Test GET /api/v1/scan/monthly."""
        mock_engine.scan_all.return_value = []

        response = client.get("/api/v1/scan/monthly")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["count"] == 0

    @patch("api.routes.scanner_engine")
    def test_all_scan_endpoint(self, mock_engine, client):
        """Test GET /api/v1/scan/all."""
        mock_engine.scan_all.return_value = []

        response = client.get("/api/v1/scan/all")

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
