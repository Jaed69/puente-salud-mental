"""Application settings loaded from environment variables (prefix ``PUENTE_``)."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_embedding_cache_dir() -> str:
    cache_home = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return str(Path(cache_home) / "fastembed")


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
    database_connect_timeout: float = Field(default=10.0, gt=0)
    # Chosen by eval/reports/retrieval-2026-11-24.md (best MRR and Hit@k in hybrid mode).
    embedding_model: str = "jinaai/jina-embeddings-v2-base-es"
    # fastembed's own default is the system temp dir, which is often RAM-backed (tmpfs): keep the
    # models on disk instead.
    embedding_cache_dir: str = Field(default_factory=_default_embedding_cache_dir)
    retrieval_mode: Literal["dense", "lexical", "hybrid"] = "hybrid"
    retrieval_k: int = Field(default=4, ge=1, le=10)
    retrieval_timeout_seconds: float = Field(default=5.0, gt=0)


@lru_cache
def get_settings() -> Settings:
    return Settings()
