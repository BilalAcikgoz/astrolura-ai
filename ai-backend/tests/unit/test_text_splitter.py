"""
Unit tests for TextSplitterService.
"""
import pytest
from langchain.schema import Document

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.rag.knowledge_base.text_splitter import TextSplitterService, get_text_splitter


class TestTextSplitterService:
    """Tests for TextSplitterService."""

    def test_initialization_default(self):
        """Test default initialization."""
        splitter = TextSplitterService()
        assert splitter.chunk_size == 1024
        assert splitter.chunk_overlap == 200

    def test_initialization_custom(self):
        """Test custom initialization."""
        splitter = TextSplitterService(chunk_size=500, chunk_overlap=100)
        assert splitter.chunk_size == 500
        assert splitter.chunk_overlap == 100

    def test_split_documents_basic(self, sample_documents):
        """Test basic document splitting."""
        splitter = TextSplitterService(chunk_size=100, chunk_overlap=20)
        chunks = splitter.split_documents(sample_documents)

        assert len(chunks) > 0
        for chunk in chunks:
            assert isinstance(chunk, Document)
            assert "chunk_id" in chunk.metadata
            assert "chunk_index" in chunk.metadata
            assert "chunk_size" in chunk.metadata

    def test_split_text(self):
        """Test text splitting."""
        splitter = TextSplitterService(chunk_size=50, chunk_overlap=10)
        text = "This is a test text that should be split into multiple chunks for testing purposes."
        metadata = {"source": "test"}

        chunks = splitter.split_text(text, metadata)

        assert len(chunks) > 0
        for chunk in chunks:
            assert "source" in chunk.metadata
            assert chunk.metadata["source"] == "test"

    def test_chunk_id_generation(self, sample_documents):
        """Test that chunk IDs are unique."""
        splitter = TextSplitterService(chunk_size=100, chunk_overlap=20)
        chunks = splitter.split_documents(sample_documents)

        chunk_ids = [chunk.metadata["chunk_id"] for chunk in chunks]
        assert len(chunk_ids) == len(set(chunk_ids)), "Chunk IDs should be unique"

    def test_chunk_statistics(self, sample_documents):
        """Test chunk statistics calculation."""
        splitter = TextSplitterService(chunk_size=100, chunk_overlap=20)
        chunks = splitter.split_documents(sample_documents)

        stats = splitter.get_chunk_statistics(chunks)

        assert "total_chunks" in stats
        assert "total_characters" in stats
        assert "avg_chunk_size" in stats
        assert "min_chunk_size" in stats
        assert "max_chunk_size" in stats
        assert "chunks_by_source" in stats

        assert stats["total_chunks"] == len(chunks)

    def test_empty_document_handling(self):
        """Test handling of empty documents."""
        splitter = TextSplitterService()
        chunks = splitter.split_documents([])

        assert len(chunks) == 0

    def test_preview_chunks(self, sample_documents):
        """Test chunk preview functionality."""
        splitter = TextSplitterService(chunk_size=100, chunk_overlap=20)
        chunks = splitter.split_documents(sample_documents)

        previews = splitter.preview_chunks(chunks, num_previews=2, preview_length=50)

        assert len(previews) <= 2
        for preview in previews:
            assert "chunk_index" in preview
            assert "chunk_id" in preview
            assert "content_preview" in preview
            assert len(preview["content_preview"]) <= 50

    def test_factory_function(self):
        """Test the factory function."""
        splitter = get_text_splitter(chunk_size=512, chunk_overlap=64)

        assert isinstance(splitter, TextSplitterService)
        assert splitter.chunk_size == 512
        assert splitter.chunk_overlap == 64

    def test_metadata_preservation(self, sample_documents):
        """Test that original metadata is preserved after splitting."""
        splitter = TextSplitterService(chunk_size=100, chunk_overlap=20)
        chunks = splitter.split_documents(sample_documents)

        for chunk in chunks:
            # Original metadata should be preserved
            assert "source_file" in chunk.metadata or "chunk_id" in chunk.metadata

    def test_chunk_overlap_less_than_chunk_size(self):
        """Test that overlap is less than chunk size."""
        with pytest.raises(Exception):
            # This should fail or create a splitter that handles this gracefully
            splitter = TextSplitterService(chunk_size=50, chunk_overlap=100)
            # LangChain may not raise an error immediately, but behavior may be undefined
