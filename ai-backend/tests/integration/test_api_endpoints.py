"""
Integration tests for API endpoints.
Tests the FastAPI endpoints with mock services.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client with mocked RAG services."""
        with patch('app.rag.service_manager.get_rag_service_manager') as mock_manager:
            manager = MagicMock()
            manager.is_connected = True
            manager.initialize = AsyncMock(return_value=True)
            manager.shutdown = AsyncMock()
            mock_manager.return_value = manager

            from main import app
            with TestClient(app) as client:
                yield client

    def test_health_check_returns_ok(self, client):
        """Test that health check returns ok status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "environment" in data

    def test_health_check_includes_rag_status(self, client):
        """Test that health check includes RAG status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "rag_status" in data


class TestRootEndpoint:
    """Tests for root endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        with patch('app.rag.service_manager.get_rag_service_manager') as mock_manager:
            manager = MagicMock()
            manager.is_connected = True
            manager.initialize = AsyncMock(return_value=True)
            manager.shutdown = AsyncMock()
            mock_manager.return_value = manager

            from main import app
            with TestClient(app) as client:
                yield client

    def test_root_returns_welcome(self, client):
        """Test that root endpoint returns welcome message."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Welcome" in data["message"]


class TestBirthChartEndpoints:
    """Tests for birth chart endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client with mocked services."""
        with patch('app.rag.service_manager.get_rag_service_manager') as mock_manager:
            manager = MagicMock()
            manager.is_connected = True
            manager.initialize = AsyncMock(return_value=True)
            manager.shutdown = AsyncMock()
            mock_manager.return_value = manager

            from main import app
            with TestClient(app) as client:
                yield client

    def test_calculate_birth_chart_validation_error(self, client):
        """Test that invalid data returns validation error."""
        # Missing required fields
        response = client.post("/api/v1/birth-chart/calculate", json={})

        assert response.status_code == 422

    def test_interpret_chart_not_found(self, client):
        """Test that non-existent chart returns 404."""
        response = client.post(
            "/api/v1/birth-chart/interpret",
            json={
                "chart_id": "non-existent-id",
                "interpretation_style": "detailed",
                "language": "tr"
            }
        )

        assert response.status_code == 404

    def test_get_chart_not_found(self, client):
        """Test that getting non-existent chart returns 404."""
        response = client.get("/api/v1/birth-chart/non-existent-id")

        assert response.status_code == 404


class TestBirthChartCalculation:
    """Tests for birth chart calculation with mocked calculator."""

    @pytest.fixture
    def client(self):
        """Create test client with mocked services."""
        with patch('app.rag.service_manager.get_rag_service_manager') as mock_manager, \
             patch('app.api.v1.endpoints.birth_chart.get_calculator') as mock_calc:

            # Mock RAG manager
            manager = MagicMock()
            manager.is_connected = True
            manager.initialize = AsyncMock(return_value=True)
            manager.shutdown = AsyncMock()
            mock_manager.return_value = manager

            # Mock calculator
            calculator = MagicMock()

            # Create mock chart data
            mock_chart_data = MagicMock()
            mock_chart_data.model_dump.return_value = {
                "chart_info": {
                    "name": "Test",
                    "birth_date": "1990-01-15",
                    "birth_time": "14:30",
                    "location": {"city": "Istanbul", "country": "Turkey"}
                },
                "planets": [],
                "houses": [],
                "aspects": [],
                "ascendant": {"sign": "Aries", "sign_en": "Aries"},
                "elements": {"fire": 25, "earth": 25, "air": 25, "water": 25},
                "qualities": {"cardinal": 33, "fixed": 33, "mutable": 34}
            }

            calculator.calculate_birth_chart.return_value = ("test-chart-id", mock_chart_data)
            mock_calc.return_value = calculator

            from main import app
            with TestClient(app) as client:
                yield client, calculator

    def test_calculate_birth_chart_success(self, client):
        """Test successful birth chart calculation."""
        test_client, calculator = client

        response = test_client.post(
            "/api/v1/birth-chart/calculate",
            json={
                "name": "Test User",
                "birth_date": "1990-01-15",
                "birth_time": "14:30",
                "birth_place": "Istanbul, Turkey"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "chart_id" in data


class TestInterpretationEndpoint:
    """Tests for interpretation endpoint with mocked RAG."""

    @pytest.fixture
    def client_with_chart(self):
        """Create test client with pre-cached chart."""
        with patch('app.rag.service_manager.get_rag_service_manager') as mock_manager:

            # Mock RAG manager
            manager = MagicMock()
            manager.is_connected = True
            manager.initialize = AsyncMock(return_value=True)
            manager.shutdown = AsyncMock()

            # Mock retrieval service
            retrieval = MagicMock()
            retrieval.retrieve_context.return_value = [
                {"id": "1", "score": 0.5, "text": "Test content", "source_file": "test.pdf", "category": "general", "page_number": 1}
            ]
            retrieval.format_context.return_value = "Test context"
            manager.get_retrieval_service.return_value = retrieval

            # Mock generation service
            gen_service = MagicMock()
            gen_service.generate_interpretation.return_value = "# Test Interpretation\n\nThis is a test."
            manager.generation_service = gen_service

            mock_manager.return_value = manager

            from main import app
            from app.api.v1.endpoints.birth_chart import chart_cache

            # Pre-populate chart cache
            chart_cache["test-chart-id"] = {
                "chart_info": {
                    "name": "Test User",
                    "birth_date": "1990-01-15",
                    "birth_time": "14:30",
                    "location": {"city": "Istanbul", "country": "Turkey"}
                },
                "planets": [
                    {"name_en": "Sun", "sign_en": "Capricorn", "house": 10},
                    {"name_en": "Moon", "sign_en": "Leo", "house": 5}
                ],
                "houses": [],
                "aspects": [],
                "ascendant": {"sign_en": "Taurus"},
                "elements": {"fire": 25, "earth": 25, "air": 25, "water": 25},
                "qualities": {"cardinal": 33, "fixed": 33, "mutable": 34}
            }

            with TestClient(app) as client:
                yield client, manager

    def test_interpret_chart_success(self, client_with_chart):
        """Test successful chart interpretation."""
        test_client, manager = client_with_chart

        response = test_client.post(
            "/api/v1/birth-chart/interpret",
            json={
                "chart_id": "test-chart-id",
                "interpretation_style": "detailed",
                "language": "tr"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "interpretation" in data
