"""
Integration tests for the RAG pipeline.
These tests require external services (Milvus, OpenAI) to be running.
Mark with @pytest.mark.integration to skip in CI without services.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Skip all tests in this module if services are not available
pytestmark = pytest.mark.integration


class TestRAGPipelineIntegration:
    """Integration tests for the complete RAG pipeline."""

    @pytest.fixture
    def mock_services(self):
        """Set up mock services for integration testing without real connections."""
        with patch('app.rag.service_manager.get_embedding_service') as mock_embed, \
             patch('app.rag.service_manager.get_vector_store') as mock_vector, \
             patch('app.rag.service_manager.get_generation_service') as mock_gen:

            # Mock embedding service
            embed_service = MagicMock()
            embed_service.embed_text.return_value = [0.1] * 1536
            mock_embed.return_value = embed_service

            # Mock vector store
            vector_store = MagicMock()
            vector_store.connect.return_value = True
            vector_store.load_collection.return_value = None
            vector_store.search.return_value = [
                {
                    "id": "test_1",
                    "score": 0.5,
                    "distance": 0.5,
                    "text": "Sun in Capricorn represents ambition and discipline.",
                    "source_file": "astrology.pdf",
                    "category": "planets",
                    "page_number": 1,
                    "chunk_index": 0,
                    "metadata": {}
                }
            ]
            mock_vector.return_value = vector_store

            # Mock generation service
            gen_service = MagicMock()
            gen_service.generate_interpretation.return_value = "# Test Interpretation\n\nThis is a test."
            mock_gen.return_value = gen_service

            yield {
                "embedding": embed_service,
                "vector_store": vector_store,
                "generation": gen_service
            }

    @pytest.mark.asyncio
    async def test_rag_manager_initialization(self, mock_services):
        """Test RAG service manager initialization."""
        from app.rag.service_manager import RAGServiceManager

        # Reset singleton for testing
        RAGServiceManager._instance = None
        RAGServiceManager._initialized = False

        manager = RAGServiceManager()
        result = await manager.initialize()

        assert result is True
        assert manager.is_connected is True

    @pytest.mark.asyncio
    async def test_rag_manager_shutdown(self, mock_services):
        """Test RAG service manager shutdown."""
        from app.rag.service_manager import RAGServiceManager

        # Reset singleton for testing
        RAGServiceManager._instance = None
        RAGServiceManager._initialized = False

        manager = RAGServiceManager()
        await manager.initialize()
        await manager.shutdown()

        assert manager.is_connected is False

    def test_retrieval_service_creation(self, mock_services):
        """Test retrieval service creation from manager."""
        from app.rag.service_manager import RAGServiceManager

        # Reset singleton for testing
        RAGServiceManager._instance = None
        RAGServiceManager._initialized = False

        manager = RAGServiceManager()
        manager._embedding_service = mock_services["embedding"]
        manager._vector_store = mock_services["vector_store"]
        manager._generation_service = mock_services["generation"]
        manager._connected = True

        retrieval = manager.get_retrieval_service(top_k=5, similarity_threshold=0.8)

        assert retrieval is not None
        assert retrieval.top_k == 5
        assert retrieval.similarity_threshold == 0.8

    def test_full_retrieval_flow(self, mock_services, sample_chart_data):
        """Test complete retrieval flow."""
        from app.rag.service_manager import ManagedRetrievalService

        retrieval = ManagedRetrievalService(
            embedding_service=mock_services["embedding"],
            vector_store=mock_services["vector_store"],
            top_k=5,
            similarity_threshold=1.0
        )

        # Generate queries
        queries = retrieval.generate_queries_from_chart(sample_chart_data)
        assert len(queries) > 0

        # Retrieve context
        results = retrieval.retrieve_context(sample_chart_data, max_queries=5)
        assert isinstance(results, list)

        # Format context
        context = retrieval.format_context(results, max_chunks=10)
        assert isinstance(context, str)

    def test_generation_with_context(self, mock_services, sample_chart_data):
        """Test interpretation generation with retrieved context."""
        gen_service = mock_services["generation"]

        context = "Sample astrological context about Sun in Capricorn."
        interpretation = gen_service.generate_interpretation(
            chart_data=sample_chart_data,
            context=context,
            language="tr"
        )

        gen_service.generate_interpretation.assert_called_once()
        assert interpretation is not None


class TestServiceManagerSingleton:
    """Tests for singleton behavior of RAG service manager."""

    def test_singleton_instance(self):
        """Test that manager is a singleton."""
        from app.rag.service_manager import RAGServiceManager

        # Reset singleton for testing
        RAGServiceManager._instance = None
        RAGServiceManager._initialized = False

        manager1 = RAGServiceManager()
        manager2 = RAGServiceManager()

        assert manager1 is manager2

    def test_get_rag_service_manager_returns_same_instance(self):
        """Test that get_rag_service_manager returns same instance."""
        from app.rag.service_manager import get_rag_service_manager, RAGServiceManager

        # Reset singleton for testing
        RAGServiceManager._instance = None
        RAGServiceManager._initialized = False

        manager1 = get_rag_service_manager()
        manager2 = get_rag_service_manager()

        assert manager1 is manager2


class TestErrorHandling:
    """Tests for error handling in RAG pipeline."""

    @pytest.mark.asyncio
    async def test_initialization_failure_handling(self):
        """Test handling of initialization failures."""
        from app.rag.service_manager import RAGServiceManager

        # Reset singleton for testing
        RAGServiceManager._instance = None
        RAGServiceManager._initialized = False

        with patch('app.rag.service_manager.get_embedding_service') as mock:
            mock.side_effect = Exception("Connection failed")

            manager = RAGServiceManager()
            result = await manager.initialize()

            assert result is False
            assert manager.is_connected is False

    def test_retrieval_service_without_initialization(self):
        """Test that getting retrieval service fails without initialization."""
        from app.rag.service_manager import RAGServiceManager

        # Reset singleton for testing
        RAGServiceManager._instance = None
        RAGServiceManager._initialized = False

        manager = RAGServiceManager()

        with pytest.raises(RuntimeError):
            manager.get_retrieval_service()
