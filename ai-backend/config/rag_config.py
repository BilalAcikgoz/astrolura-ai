from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RAGSettings(BaseSettings):
    """astrolura-ai RAG pipeline settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    search_top_k: int = Field(alias="SEARCH_TOP_K")
    similarity_threshold: float = Field(alias="SIMILARITY_THRESHOLD")
    max_context_chunks: int = Field(alias="MAX_CONTEXT_CHUNKS")
    max_queries: int = Field(alias="MAX_QUERIES")
