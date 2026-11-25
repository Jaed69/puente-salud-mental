"""Application settings loaded from environment variables (prefix ``PUENTE_``)."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PUENTE_", env_file=".env", extra="ignore")

    environment: Literal["development", "test", "production"] = "development"
    app_name: str = "Puente"

    # OpenAI-compatible chat model. Without a base URL and a model the companion serves a fixed
    # fallback reply. The API key is optional for local endpoints.
    llm_base_url: str | None = None
    llm_api_key: SecretStr | None = None
    llm_model: str | None = None
    llm_timeout_seconds: float = Field(default=20.0, gt=0)
    llm_max_output_tokens: int = Field(default=300, gt=0)

    # Knowledge base (PostgreSQL + pgvector). Without a database URL the companion answers without
    # reference material. Embeddings always run locally (see puente.knowledge.embeddings).
    database_url: SecretStr | None = None
    embedding_model: str = "intfloat/multilingual-e5-large"
    embedding_cache_dir: str | None = None
    retrieval_mode: Literal["dense", "lexical", "hybrid"] = "hybrid"
    retrieval_k: int = Field(default=4, ge=1, le=10)
    retrieval_timeout_seconds: float = Field(default=5.0, gt=0)


@lru_cache
def get_settings() -> Settings:
    return Settings()
