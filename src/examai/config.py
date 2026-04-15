"""Application settings from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    """Runtime configuration (secrets and URLs from env only in real deployments)."""

    secret_key: str
    database_url: str
    session_cookie_name: str = "examai_session"
    session_max_age: int = 60 * 60 * 8  # 8 hours
    bootstrap_demo_user: bool = False
    ollama_base_url: str = ""
    ollama_model: str = "llama3.2"
    ollama_timeout_seconds: float = 120.0
    ollama_max_retries: int = 2
    git_provider_base_url: str = ""
    git_provider_token: str = ""
    git_provider_timeout_seconds: float = 45.0


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


@lru_cache
def get_settings() -> Settings:
    secret_key = os.environ.get("EXAMINAI_SECRET_KEY", "").strip()
    if not secret_key:
        secret_key = "dev-insecure-change-me"

    database_url = os.environ.get(
        "EXAMINAI_DATABASE_URL",
        "sqlite+pysqlite:///./examai.local.db",
    ).strip()

    ollama_base = (os.environ.get("OLLAMA_BASE_URL") or "").strip().rstrip("/")
    ollama_model = (os.environ.get("OLLAMA_MODEL") or "llama3.2").strip() or "llama3.2"
    ollama_timeout_raw = os.environ.get("OLLAMA_TIMEOUT_SECONDS")
    try:
        ollama_timeout = float(ollama_timeout_raw) if ollama_timeout_raw else 120.0
    except ValueError:
        ollama_timeout = 120.0
    ollama_retries_raw = os.environ.get("OLLAMA_MAX_RETRIES")
    try:
        ollama_retries = int(ollama_retries_raw) if ollama_retries_raw else 2
    except ValueError:
        ollama_retries = 2
    ollama_retries = max(1, min(ollama_retries, 5))

    git_base = (os.environ.get("GIT_PROVIDER_BASE_URL") or "").strip().rstrip("/")
    git_token = (os.environ.get("GIT_PROVIDER_TOKEN") or "").strip()
    git_timeout_raw = os.environ.get("GIT_PROVIDER_TIMEOUT_SECONDS")
    try:
        git_timeout = float(git_timeout_raw) if git_timeout_raw else 45.0
    except ValueError:
        git_timeout = 45.0
    git_timeout = max(5.0, min(git_timeout, 120.0))

    return Settings(
        secret_key=secret_key,
        database_url=database_url,
        bootstrap_demo_user=_env_bool("EXAMINAI_BOOTSTRAP_DEMO", False),
        ollama_base_url=ollama_base,
        ollama_model=ollama_model,
        ollama_timeout_seconds=ollama_timeout,
        ollama_max_retries=ollama_retries,
        git_provider_base_url=git_base,
        git_provider_token=git_token,
        git_provider_timeout_seconds=git_timeout,
    )


def clear_settings_cache() -> None:
    get_settings.cache_clear()
