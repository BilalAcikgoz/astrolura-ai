from typing import List, Dict, Optional
from loguru import logger
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import numpy as np
from langchain_core.documents import Document
import hashlib
import json
from pathlib import Path

from config import embedding_settings, app_settings


class EmbeddingService:
    """astrolura-ai embedding service using OpenRouter API."""

    def __init__(self, batch_size: Optional[int] = None):
        self.model = embedding_settings.embedding_model
        self.batch_size = batch_size or embedding_settings.embedding_batch_size
        self.dimension = embedding_settings.embedding_dimension

        self.client = OpenAI(
            api_key=embedding_settings.openrouter_api_key,
            base_url=embedding_settings.openrouter_base_url,
        )

        self.cache_dir = Path(app_settings.cache_dir) / "embeddings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"Initialized EmbeddingService with model={self.model}, "
            f"dimension={self.dimension}, batch_size={self.batch_size}"
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call_embedding_api(self, texts: List[str]) -> List[List[float]]:
        try:
            response = self.client.embeddings.create(model=self.model, input=texts)
            embeddings = [item.embedding for item in response.data]

            if hasattr(response, "usage") and response.usage:
                total_tokens = response.usage.total_tokens
                logger.debug(
                    f"Embedding API Call: model={response.model}, "
                    f"texts={len(texts)}, tokens={total_tokens:,}"
                )

            return embeddings
        except Exception as e:
            logger.error(f"Error calling embedding API: {str(e)}")
            raise

    def embed_text(self, text: str, use_cache: bool = True) -> List[float]:
        if use_cache:
            cached_embedding = self._get_cached_embedding(text)
            if cached_embedding is not None:
                return cached_embedding

        embeddings = self._call_embedding_api([text])
        embedding = embeddings[0]

        if use_cache:
            self._cache_embedding(text, embedding)

        return embedding

    def embed_texts(
        self, texts: List[str], use_cache: bool = True, show_progress: bool = True
    ) -> List[List[float]]:
        all_embeddings = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size
        total_cached = 0
        total_new = 0

        logger.info(f"Embedding {len(texts)} texts in {total_batches} batches...")

        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i : i + self.batch_size]
            batch_num = (i // self.batch_size) + 1

            if show_progress:
                logger.info(f"Processing batch {batch_num}/{total_batches}")

            batch_embeddings = []
            texts_to_embed = []
            text_indices = []

            for idx, text in enumerate(batch_texts):
                if use_cache:
                    cached = self._get_cached_embedding(text)
                    if cached is not None:
                        batch_embeddings.append(cached)
                        total_cached += 1
                        continue

                texts_to_embed.append(text)
                text_indices.append(idx)

            if texts_to_embed:
                new_embeddings = self._call_embedding_api(texts_to_embed)
                total_new += len(texts_to_embed)

                if use_cache:
                    for text, embedding in zip(texts_to_embed, new_embeddings):
                        self._cache_embedding(text, embedding)

                for idx, embedding in zip(text_indices, new_embeddings):
                    batch_embeddings.insert(idx, embedding)

            all_embeddings.extend(batch_embeddings)

        logger.info(
            f"Embedding complete: {len(all_embeddings)} total "
            f"({total_cached} cached, {total_new} new)"
        )
        return all_embeddings

    def embed_documents(
        self, documents: List[Document], use_cache: bool = True, show_progress: bool = True
    ) -> List[Dict]:
        logger.info(f"Embedding {len(documents)} documents...")
        texts = [doc.page_content for doc in documents]
        embeddings = self.embed_texts(texts, use_cache=use_cache, show_progress=show_progress)

        embedded_docs = []
        for doc, embedding in zip(documents, embeddings):
            embedded_docs.append({
                "text": doc.page_content,
                "embedding": embedding,
                "metadata": doc.metadata,
            })
        return embedded_docs

    def _get_cache_key(self, text: str) -> str:
        text_hash = hashlib.sha256(f"{self.model}:{text}".encode()).hexdigest()
        return text_hash

    def _get_cached_embedding(self, text: str) -> Optional[List[float]]:
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    cached_data = json.load(f)
                return cached_data["embedding"]
            except Exception as e:
                logger.warning(f"Error reading cache: {str(e)}")
                return None
        return None

    def _cache_embedding(self, text: str, embedding: List[float]):
        try:
            cache_key = self._get_cache_key(text)
            cache_file = self.cache_dir / f"{cache_key}.json"
            cache_data = {
                "model": self.model,
                "text_preview": text[:200],
                "embedding": embedding,
            }
            with open(cache_file, "w") as f:
                json.dump(cache_data, f)
        except Exception as e:
            logger.warning(f"Error caching embedding: {str(e)}")

    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return float(dot_product / (norm1 * norm2))

    def get_embedding_stats(self) -> Dict:
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        return {
            "cached_embeddings": len(cache_files),
            "cache_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_directory": str(self.cache_dir),
            "model": self.model,
            "dimension": self.dimension,
        }

    def clear_cache(self):
        cache_files = list(self.cache_dir.glob("*.json"))
        for cache_file in cache_files:
            cache_file.unlink()
        logger.info(f"Cleared {len(cache_files)} cached embeddings")


def get_embedding_service(batch_size: Optional[int] = None) -> EmbeddingService:
    return EmbeddingService(batch_size=batch_size)
