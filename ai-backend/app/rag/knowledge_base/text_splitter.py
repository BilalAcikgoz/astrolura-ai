from typing import List, Dict, Optional
from loguru import logger
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import hashlib

class TextSplitterService:
    # Service for splitting documents into chunks for vector storage.
    # Uses RecursiveCharacterTextSplitter to maintain semantic coherence.
    def __init__(
        self,
        chunk_size: int = 1024,
        chunk_overlap: int = 200,
        length_function: callable = len,
        separators: Optional[List[str]] = None
    ):
        # Initialize text splitter service.
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Default separators optimized for astrology texts
        if separators is None:
            separators = [
                "\n\n",  # Paragraph breaks
                "\n",    # Line breaks
                ". ",    # Sentence endings
                "! ",    # Exclamations
                "? ",    # Questions
                "; ",    # Semicolons
                ", ",    # Commas
                " ",     # Spaces
                ""       # Characters
            ]

        # Initialize LangChain's RecursiveCharacterTextSplitter
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=length_function,
            separators=separators,
            keep_separator=True
        )

        logger.info(
            f"Initialized TextSplitterService with chunk_size={chunk_size}, "
            f"chunk_overlap={chunk_overlap}"
        )

    def split_documents(
        self,
        documents: List[Document]
    ) -> List[Document]:
        # Split a list of documents into chunks.
        logger.info(f"Splitting {len(documents)} documents into chunks...")

        # Split documents
        chunks = self.splitter.split_documents(documents)

        # Enrich metadata for each chunk
        enriched_chunks = []
        for i, chunk in enumerate(chunks):
            # Generate unique chunk ID
            chunk_id = self._generate_chunk_id(chunk, i)

            # Enrich metadata
            chunk.metadata.update({
                "chunk_id": chunk_id,
                "chunk_index": i,
                "chunk_size": len(chunk.page_content),
                "chunk_overlap": self.chunk_overlap
            })

            enriched_chunks.append(chunk)

        logger.info(
            f"Split {len(documents)} documents into {len(enriched_chunks)} chunks"
        )

        return enriched_chunks

    def split_text(
        self,
        text: str,
        metadata: Optional[Dict] = None
    ) -> List[Document]:
        # Split a raw text string into chunks.
        if metadata is None:
            metadata = {}

        # Create a temporary document
        doc = Document(page_content=text, metadata=metadata)

        # Split using split_documents
        return self.split_documents([doc])

    # Generate a unique ID for a chunk.
    def _generate_chunk_id(self, chunk: Document, index: int) -> str:
        # Create a hash based on source file, page number, and content
        source_file = chunk.metadata.get("source_file", "unknown")
        page_number = chunk.metadata.get("page_number", 0)
        content_preview = chunk.page_content[:100]

        # Combine into a unique string
        unique_string = f"{source_file}_{page_number}_{index}_{content_preview}"

        # Generate hash
        chunk_hash = hashlib.md5(unique_string.encode()).hexdigest()[:12]

        # Create readable ID
        chunk_id = f"{source_file.replace('.pdf', '')}_{page_number}_{chunk_hash}"

        return chunk_id

    def get_chunk_statistics(self, chunks: List[Document]) -> Dict:
        # Get statistics about chunks.
        if not chunks:
            return {
                "total_chunks": 0,
                "total_characters": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
                "chunks_by_source": {}
            }

        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        total_chars = sum(chunk_sizes)

        # Count by source file
        chunks_by_source = {}
        for chunk in chunks:
            source = chunk.metadata.get("source_file", "unknown")
            chunks_by_source[source] = chunks_by_source.get(source, 0) + 1

        stats = {
            "total_chunks": len(chunks),
            "total_characters": total_chars,
            "avg_chunk_size": round(total_chars / len(chunks), 2),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "chunks_by_source": chunks_by_source,
            "configured_chunk_size": self.chunk_size,
            "configured_overlap": self.chunk_overlap
        }

        logger.info(f"Chunk statistics: {stats}")
        return stats

    def preview_chunks(
        self,
        chunks: List[Document],
        num_previews: int = 3,
        preview_length: int = 200
    ) -> List[Dict]:
        # Get preview of chunks for inspection.
        previews = []

        for i, chunk in enumerate(chunks[:num_previews]):
            preview = {
                "chunk_index": i,
                "chunk_id": chunk.metadata.get("chunk_id", "unknown"),
                "source_file": chunk.metadata.get("source_file", "unknown"),
                "page_number": chunk.metadata.get("page_number", "unknown"),
                "chunk_size": len(chunk.page_content),
                "content_preview": chunk.page_content[:preview_length].replace('\n', ' '),
                "metadata": chunk.metadata
            }
            previews.append(preview)

        return previews

# Factory function to get a TextSplitterService instance.
def get_text_splitter(
    chunk_size: int = 1024,
    chunk_overlap: int = 200
) -> TextSplitterService:
    
    return TextSplitterService(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
