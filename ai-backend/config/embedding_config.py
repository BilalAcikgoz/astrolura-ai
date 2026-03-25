from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingSettings(BaseSettings):
    """astrolura-ai embedding model settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    openrouter_api_key: str = Field(alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(alias="OPENROUTER_BASE_URL")
    embedding_model: str = Field(alias="EMBEDDING_MODEL")
    embedding_dimension: int = Field(alias="EMBEDDING_DIMENSION")
    embedding_batch_size: int = Field(alias="EMBEDDING_BATCH_SIZE")
    embedding_max_tokens: int = Field(alias="EMBEDDING_MAX_TOKENS")
    embedding_rate_limit_pause: float = Field(alias="EMBEDDING_RATE_LIMIT_PAUSE")
