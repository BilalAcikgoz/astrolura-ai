"""
Unit tests for query generation in retrieval service.
These tests don't require external services.
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.rag.service_manager import ManagedRetrievalService


class MockEmbeddingService:
    """Mock embedding service for testing."""
    def embed_text(self, text: str):
        return [0.1] * 1536


class MockVectorStore:
    """Mock vector store for testing."""
    def search(self, query_embedding, top_k=5):
        return []


class TestQueryGeneration:
    """Tests for query generation from birth chart data."""

    @pytest.fixture
    def retrieval_service(self):
        """Create a retrieval service with mocks."""
        return ManagedRetrievalService(
            embedding_service=MockEmbeddingService(),
            vector_store=MockVectorStore(),
            top_k=5,
            similarity_threshold=0.8
        )

    def test_generate_sun_queries(self, retrieval_service, sample_chart_data):
        """Test Sun sign query generation."""
        queries = retrieval_service.generate_queries_from_chart(sample_chart_data)

        # Should have Sun queries
        sun_queries = [q for q in queries if "Sun" in q]
        assert len(sun_queries) >= 2
        assert any("Capricorn" in q for q in sun_queries)

    def test_generate_moon_queries(self, retrieval_service, sample_chart_data):
        """Test Moon sign query generation."""
        queries = retrieval_service.generate_queries_from_chart(sample_chart_data)

        # Should have Moon queries
        moon_queries = [q for q in queries if "Moon" in q]
        assert len(moon_queries) >= 2
        assert any("Leo" in q for q in moon_queries)

    def test_generate_ascendant_queries(self, retrieval_service, sample_chart_data):
        """Test Ascendant query generation."""
        queries = retrieval_service.generate_queries_from_chart(sample_chart_data)

        # Should have Ascendant queries
        asc_queries = [q for q in queries if "Ascendant" in q or "rising" in q.lower()]
        assert len(asc_queries) >= 1
        assert any("Taurus" in q for q in asc_queries)

    def test_generate_planet_queries(self, retrieval_service, sample_chart_data):
        """Test planet query generation."""
        queries = retrieval_service.generate_queries_from_chart(sample_chart_data)

        # Should have queries for major planets
        planet_names = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        for planet in planet_names:
            planet_queries = [q for q in queries if planet in q]
            assert len(planet_queries) >= 1, f"Missing query for {planet}"

    def test_generate_house_queries(self, retrieval_service, sample_chart_data):
        """Test house cusp query generation."""
        queries = retrieval_service.generate_queries_from_chart(sample_chart_data)

        # Should have house queries
        house_queries = [q for q in queries if "house" in q.lower() and "cusp" in q.lower()]
        assert len(house_queries) >= 1

    def test_generate_aspect_queries(self, retrieval_service, sample_chart_data):
        """Test aspect query generation."""
        queries = retrieval_service.generate_queries_from_chart(sample_chart_data)

        # Should have aspect queries
        aspect_types = ['Conjunction', 'Opposition', 'Trine', 'Square', 'Sextile']
        aspect_queries = [q for q in queries if any(a in q for a in aspect_types)]
        assert len(aspect_queries) >= 1

    def test_generate_element_queries(self, retrieval_service, sample_chart_data):
        """Test element balance query generation."""
        queries = retrieval_service.generate_queries_from_chart(sample_chart_data)

        # Should have element query - earth is dominant in sample data
        element_queries = [q for q in queries if "element" in q.lower()]
        assert len(element_queries) >= 1
        # Earth should be dominant (45%)
        assert any("earth" in q.lower() for q in element_queries)

    def test_generate_quality_queries(self, retrieval_service, sample_chart_data):
        """Test quality/modality query generation."""
        queries = retrieval_service.generate_queries_from_chart(sample_chart_data)

        # Should have quality query - mutable is dominant in sample data
        quality_queries = [q for q in queries if "quality" in q.lower() or "modality" in q.lower()]
        assert len(quality_queries) >= 1
        # Mutable should be dominant (40%)
        assert any("mutable" in q.lower() for q in quality_queries)

    def test_query_count(self, retrieval_service, sample_chart_data):
        """Test that a reasonable number of queries are generated."""
        queries = retrieval_service.generate_queries_from_chart(sample_chart_data)

        # Should generate multiple queries but not too many
        assert len(queries) >= 10
        assert len(queries) <= 50

    def test_empty_chart_data(self, retrieval_service):
        """Test handling of empty chart data."""
        queries = retrieval_service.generate_queries_from_chart({})
        assert isinstance(queries, list)
        assert len(queries) == 0

    def test_partial_chart_data(self, retrieval_service):
        """Test handling of partial chart data."""
        partial_data = {
            "planets": [
                {
                    "name_en": "Sun",
                    "sign_en": "Aries",
                    "house": 1
                }
            ]
        }
        queries = retrieval_service.generate_queries_from_chart(partial_data)

        assert len(queries) >= 2  # Should still generate Sun queries


class TestContextFormatting:
    """Tests for context formatting."""

    @pytest.fixture
    def retrieval_service(self):
        """Create a retrieval service with mocks."""
        return ManagedRetrievalService(
            embedding_service=MockEmbeddingService(),
            vector_store=MockVectorStore(),
            top_k=5,
            similarity_threshold=0.8
        )

    def test_format_empty_results(self, retrieval_service):
        """Test formatting empty results."""
        context = retrieval_service.format_context([])
        assert "No relevant" in context or context == ""

    def test_format_single_result(self, retrieval_service):
        """Test formatting single result."""
        results = [{
            "id": "test_1",
            "score": 0.5,
            "text": "This is test content about astrology.",
            "source_file": "test.pdf",
            "category": "general_astrology",
            "page_number": 1
        }]

        context = retrieval_service.format_context(results)

        assert "test content" in context.lower()
        assert "Source 1" in context

    def test_format_multiple_results(self, retrieval_service):
        """Test formatting multiple results."""
        results = [
            {
                "id": "test_1",
                "score": 0.3,
                "text": "First result about Sun signs.",
                "source_file": "sun.pdf",
                "category": "planets",
                "page_number": 1
            },
            {
                "id": "test_2",
                "score": 0.5,
                "text": "Second result about Moon signs.",
                "source_file": "moon.pdf",
                "category": "planets",
                "page_number": 5
            }
        ]

        context = retrieval_service.format_context(results)

        assert "Source 1" in context
        assert "Source 2" in context
        assert "Sun" in context
        assert "Moon" in context

    def test_format_max_chunks_limit(self, retrieval_service):
        """Test that max_chunks limit is respected."""
        results = [
            {
                "id": f"test_{i}",
                "score": 0.1 * i,
                "text": f"Content {i}",
                "source_file": "test.pdf",
                "category": "general",
                "page_number": i
            }
            for i in range(20)
        ]

        context = retrieval_service.format_context(results, max_chunks=5)

        # Should only have 5 sources
        assert context.count("[Source") == 5
