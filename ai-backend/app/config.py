from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application Settings
    app_name: str = Field(default="Astro-Fala AI Backend", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Server Settings
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    workers: int = Field(default=4, alias="WORKERS")

    # Geocoding Configuration
    geocoding_provider: str = Field(default="nominatim", alias="GEOCODING_PROVIDER")
    google_maps_api_key: Optional[str] = Field(default=None, alias="GOOGLE_MAPS_API_KEY")
    mapbox_api_key: Optional[str] = Field(default=None, alias="MAPBOX_API_KEY")

    # Swiss Ephemeris Configuration
    ephe_path: str = Field(default="./ephe", alias="EPHE_PATH")

    # Milvus Vector Database Configuration
    milvus_host: str = Field(default="localhost", alias="MILVUS_HOST")
    milvus_port: int = Field(default=19530, alias="MILVUS_PORT")
    milvus_collection_name: str = Field(default="astrology_knowledge", alias="MILVUS_COLLECTION_NAME")
    milvus_index_type: str = Field(default="IVF_FLAT", alias="MILVUS_INDEX_TYPE")
    milvus_metric_type: str = Field(default="L2", alias="MILVUS_METRIC_TYPE")
    milvus_nlist: int = Field(default=128, alias="MILVUS_NLIST")
    milvus_nprobe: int = Field(default=10, alias="MILVUS_NPROBE")

    # OpenAI Configuration
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, alias="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(default=2000, alias="OPENAI_MAX_TOKENS")
    openai_top_p: float = Field(default=0.9, alias="OPENAI_TOP_P")
    openai_frequency_penalty: float = Field(default=0.0, alias="OPENAI_FREQUENCY_PENALTY")
    openai_presence_penalty: float = Field(default=0.0, alias="OPENAI_PRESENCE_PENALTY")

    # Embedding Configuration
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    embedding_dimension: int = Field(default=1536, alias="EMBEDDING_DIMENSION")

    # Local Embeddings (Alternative)
    use_local_embeddings: bool = Field(default=False, alias="USE_LOCAL_EMBEDDINGS")
    local_embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        alias="LOCAL_EMBEDDING_MODEL"
    )
    local_embedding_dimension: int = Field(default=384, alias="LOCAL_EMBEDDING_DIMENSION")

    # Cache Settings
    cache_dir: str = Field(default="./cache", alias="CACHE_DIR")
    cache_ttl_seconds: int = Field(default=3600, alias="CACHE_TTL_SECONDS")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests_per_minute: int = Field(default=60, alias="RATE_LIMIT_REQUESTS_PER_MINUTE")
    rate_limit_requests_per_day: int = Field(default=1000, alias="RATE_LIMIT_REQUESTS_PER_DAY")

    # Security
    secret_key: str = Field(alias="SECRET_KEY")
    allowed_origins: str = Field(default="http://localhost:3000", alias="ALLOWED_ORIGINS")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Logging
    log_file: str = Field(default="logs/app.log", alias="LOG_FILE")
    log_rotation: str = Field(default="10 MB", alias="LOG_ROTATION")
    log_retention: str = Field(default="30 days", alias="LOG_RETENTION")

    @field_validator("allowed_origins")
    def parse_allowed_origins(cls, v):
        # Parse comma-separated origins into a list
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("ephe_path", "cache_dir")
    def ensure_path_exists(cls, v):
        # Ensure directory paths exist
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path.absolute())

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    @property
    def active_embedding_dimension(self) -> int:
        return self.local_embedding_dimension if self.use_local_embeddings else self.embedding_dimension

    @property
    def active_embedding_model(self) -> str:
        return self.local_embedding_model if self.use_local_embeddings else self.embedding_model

# Global settings instance
settings = Settings()


# Convenience function to get settings
def get_settings() -> Settings:
    return settings
