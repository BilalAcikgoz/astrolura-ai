from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class VectorDBSettings(BaseSettings):
    """astrolura-ai Milvus vector database settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    milvus_host: str = Field(alias="MILVUS_HOST")
    milvus_port: int = Field(alias="MILVUS_PORT")
    milvus_database: str = Field(alias="MILVUS_DATABASE")
    milvus_birth_chart_collection: str = Field(alias="MILVUS_BIRTH_CHART_COLLECTION")
    milvus_transit_chart_collection: str = Field(alias="MILVUS_TRANSIT_CHART_COLLECTION")
    milvus_index_type: str = Field(alias="MILVUS_INDEX_TYPE")
    milvus_metric_type: str = Field(alias="MILVUS_METRIC_TYPE")
    milvus_hnsw_m: int = Field(alias="MILVUS_HNSW_M")
    milvus_hnsw_ef_construction: int = Field(alias="MILVUS_HNSW_EF_CONSTRUCTION")
    milvus_hnsw_ef_search: int = Field(alias="MILVUS_HNSW_EF_SEARCH")
