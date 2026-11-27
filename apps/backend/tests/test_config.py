from pathlib import Path

import pytest

from puente.config import Settings


def test_embedding_cache_defaults_to_xdg_cache_home(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("PUENTE_EMBEDDING_CACHE_DIR", raising=False)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))

    settings = Settings(_env_file=None)

    assert settings.embedding_cache_dir == str(tmp_path / "fastembed")


def test_embedding_cache_falls_back_to_home_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("PUENTE_EMBEDDING_CACHE_DIR", raising=False)
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))

    settings = Settings(_env_file=None)

    assert settings.embedding_cache_dir == str(tmp_path / ".cache" / "fastembed")


def test_embedding_cache_env_var_overrides_default(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("PUENTE_EMBEDDING_CACHE_DIR", "/models")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))

    settings = Settings(_env_file=None)

    assert settings.embedding_cache_dir == "/models"
