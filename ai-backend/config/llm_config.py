from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """astrolura-ai OpenRouter LLM generation settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    openrouter_api_key: str = Field(alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(alias="OPENROUTER_BASE_URL")
    llm_model: str = Field(alias="LLM_MODEL")
    llm_max_completion_tokens: int = Field(alias="LLM_MAX_COMPLETION_TOKENS")
    llm_timeout: int = Field(alias="LLM_TIMEOUT")
    llm_max_retries: int = Field(alias="LLM_MAX_RETRIES")
    llm_temperature: float = Field(alias="LLM_TEMPERATURE")
    llm_top_p: float = Field(alias="LLM_TOP_P")
    llm_frequency_penalty: float = Field(alias="LLM_FREQUENCY_PENALTY")
    llm_presence_penalty: float = Field(alias="LLM_PRESENCE_PENALTY")
