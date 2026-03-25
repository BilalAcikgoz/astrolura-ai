from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """astrolura-ai application, server, logging and geocoding settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(alias="APP_NAME")
    app_version: str = Field(alias="APP_VERSION")
    debug: bool = Field(alias="DEBUG")
    environment: str = Field(alias="ENVIRONMENT")
    log_level: str = Field(alias="LOG_LEVEL")

    # Server
    host: str = Field(alias="HOST")
    port: int = Field(alias="PORT")
    workers: int = Field(alias="WORKERS")

    # CORS
    allowed_origins: str = Field(alias="ALLOWED_ORIGINS")

    # Geocoding & Ephemeris
    geocoding_provider: str = Field(alias="GEOCODING_PROVIDER")
    ephe_path: str = Field(alias="EPHE_PATH")

    # Cache
    cache_dir: str = Field(alias="CACHE_DIR")
    cache_ttl_seconds: int = Field(alias="CACHE_TTL_SECONDS")

    # Rate Limiting
    rate_limit_enabled: bool = Field(alias="RATE_LIMIT_ENABLED")
    rate_limit_requests_per_minute: int = Field(alias="RATE_LIMIT_REQUESTS_PER_MINUTE")
    rate_limit_requests_per_day: int = Field(alias="RATE_LIMIT_REQUESTS_PER_DAY")

    # Logging
    log_file: str = Field(alias="LOG_FILE")
    log_rotation: str = Field(alias="LOG_ROTATION")
    log_retention: str = Field(alias="LOG_RETENTION")

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"
