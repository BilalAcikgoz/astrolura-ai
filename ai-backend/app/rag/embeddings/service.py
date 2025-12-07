from typing import List, Dict, Optional, Union
from loguru import logger
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import numpy as np
from langchain.schema import Document
import hashlib
import json
from pathlib import Path

from app.config import get_settings

class EmbeddingService:
    # Service for generating embeddings using OpenAI's embedding models.
    # Supports batch processing, caching, and retry logic.
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        batch_size: int = 100
    ):
        # Initialize embedding service.
        settings = get_settings()

        self.model = model or settings.embedding_model
        self.api_key = api_key or settings.openai_api_key
        self.batch_size = batch_size
        self.dimension = settings.embedding_dimension

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)

        # Setup cache
        self.cache_dir = Path(cache_dir or settings.cache_dir) / "embeddings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"Initialized EmbeddingService with model={self.model}, "
            f"dimension={self.dimension}, batch_size={self.batch_size}"
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _call_embedding_api(self, texts: List[str]) -> List[List[float]]:
        # Call OpenAI embedding API with retry logic.
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )

            embeddings = [item.embedding for item in response.data]
            return embeddings

        except Exception as e:
            logger.error(f"Error calling embedding API: {str(e)}")
            raise

    def embed_text(self, text: str, use_cache: bool = True) -> List[float]:
        # Generate embedding for a single text.
        # Check cache first
        if use_cache:
            cached_embedding = self._get_cached_embedding(text)
            if cached_embedding is not None:
                return cached_embedding

        # Generate embedding
        embeddings = self._call_embedding_api([text])
        embedding = embeddings[0]

        # Cache the result
        if use_cache:
            self._cache_embedding(text, embedding)

        return embedding

    def embed_texts(
        self,
        texts: List[str],
        use_cache: bool = True,
        show_progress: bool = True
    ) -> List[List[float]]:
        # Generate embeddings for multiple texts in batches.
        all_embeddings = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size

        logger.info(f"Embedding {len(texts)} texts in {total_batches} batches...")

        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1

            if show_progress:
                logger.info(f"Processing batch {batch_num}/{total_batches}")

            # Check cache for each text in batch
            batch_embeddings = []
            texts_to_embed = []
            text_indices = []

            for idx, text in enumerate(batch_texts):
                if use_cache:
                    cached = self._get_cached_embedding(text)
                    if cached is not None:
                        batch_embeddings.append(cached)
                        continue

                # Need to embed this text
                texts_to_embed.append(text)
                text_indices.append(idx)

            # Embed texts that weren't cached
            if texts_to_embed:
                new_embeddings = self._call_embedding_api(texts_to_embed)

                # Cache new embeddings
                if use_cache:
                    for text, embedding in zip(texts_to_embed, new_embeddings):
                        self._cache_embedding(text, embedding)

                # Insert new embeddings at correct positions
                for idx, embedding in zip(text_indices, new_embeddings):
                    batch_embeddings.insert(idx, embedding)

            all_embeddings.extend(batch_embeddings)

        logger.info(f"Successfully generated {len(all_embeddings)} embeddings")
        return all_embeddings

    def embed_documents(
        self,
        documents: List[Document],
        use_cache: bool = True,
        show_progress: bool = True
    ) -> List[Dict]:
        # Generate embeddings for documents and return with metadata.
        logger.info(f"Embedding {len(documents)} documents...")

        # Extract texts from documents
        texts = [doc.page_content for doc in documents]

        # Generate embeddings
        embeddings = self.embed_texts(
            texts,
            use_cache=use_cache,
            show_progress=show_progress
        )

        # Combine with metadata
        embedded_docs = []
        for doc, embedding in zip(documents, embeddings):
            embedded_docs.append({
                "text": doc.page_content,
                "embedding": embedding,
                "metadata": doc.metadata
            })

        return embedded_docs

    def _get_cache_key(self, text: str) -> str:
        # Generate cache key for a text.
        # Create hash of text and model
        text_hash = hashlib.sha256(f"{self.model}:{text}".encode()).hexdigest()
        return text_hash

    def _get_cached_embedding(self, text: str) -> Optional[List[float]]:
        # Get cached embedding for a text.
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                return cached_data['embedding']
            except Exception as e:
                logger.warning(f"Error reading cache: {str(e)}")
                return None

        return None

    def _cache_embedding(self, text: str, embedding: List[float]):
        # Cache an embedding.
        try:
            cache_key = self._get_cache_key(text)
            cache_file = self.cache_dir / f"{cache_key}.json"

            cache_data = {
                "model": self.model,
                "text_preview": text[:200],  # Store preview for debugging
                "embedding": embedding
            }

            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)

        except Exception as e:
            logger.warning(f"Error caching embedding: {str(e)}")

    def cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        # Calculate cosine similarity between two embeddings.
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        similarity = dot_product / (norm1 * norm2)
        return float(similarity)

    def get_embedding_stats(self) -> Dict:
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)

        stats = {
            "cached_embeddings": len(cache_files),
            "cache_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_directory": str(self.cache_dir),
            "model": self.model,
            "dimension": self.dimension
        }

        return stats

    def clear_cache(self):
        cache_files = list(self.cache_dir.glob("*.json"))
        for cache_file in cache_files:
            cache_file.unlink()

        logger.info(f"Cleared {len(cache_files)} cached embeddings")

# Factory function to get an EmbeddingService instance.
def get_embedding_service(
    model: Optional[str] = None,
    batch_size: int = 100
) -> EmbeddingService:
    
    return EmbeddingService(model=model, batch_size=batch_size)
