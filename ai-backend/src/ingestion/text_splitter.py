from typing import List, Dict, Optional
from loguru import logger
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import hashlib


class AstrologyTextSplitterService:
    """astrolura-ai text splitter for chunking astrology documents."""

    def __init__(
        self,
        chunk_size: int = 1024,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        if separators is None:
            separators = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=separators,
            keep_separator=True,
        )

        logger.info(
            f"Initialized TextSplitterService with chunk_size={chunk_size}, "
            f"chunk_overlap={chunk_overlap}"
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        logger.info(f"Splitting {len(documents)} documents into chunks...")
        chunks = self.splitter.split_documents(documents)

        enriched_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_id = self._generate_chunk_id(chunk, i)
            chunk.metadata.update({
                "chunk_id": chunk_id,
                "chunk_index": i,
                "chunk_size": len(chunk.page_content),
                "chunk_overlap": self.chunk_overlap,
            })
            enriched_chunks.append(chunk)

        logger.info(f"Split {len(documents)} documents into {len(enriched_chunks)} chunks")
        return enriched_chunks

    def _generate_chunk_id(self, chunk: Document, index: int) -> str:
        source_file = chunk.metadata.get("source_file", "unknown")
        page_number = chunk.metadata.get("page_number", 0)
        content_preview = chunk.page_content[:100]
        unique_string = f"{source_file}_{page_number}_{index}_{content_preview}"
        chunk_hash = hashlib.md5(unique_string.encode()).hexdigest()[:12]
        return f"{source_file.replace('.pdf', '')}_{page_number}_{chunk_hash}"

    def get_chunk_statistics(self, chunks: List[Document]) -> Dict:
        if not chunks:
            return {
                "total_chunks": 0,
                "total_characters": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
                "chunks_by_source": {},
            }

        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        total_chars = sum(chunk_sizes)

        chunks_by_source = {}
        for chunk in chunks:
            source = chunk.metadata.get("source_file", "unknown")
            chunks_by_source[source] = chunks_by_source.get(source, 0) + 1

        return {
            "total_chunks": len(chunks),
            "total_characters": total_chars,
            "avg_chunk_size": round(total_chars / len(chunks), 2),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "chunks_by_source": chunks_by_source,
            "configured_chunk_size": self.chunk_size,
            "configured_overlap": self.chunk_overlap,
        }


def get_astrology_text_splitter(
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
) -> AstrologyTextSplitterService:
    return AstrologyTextSplitterService(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
