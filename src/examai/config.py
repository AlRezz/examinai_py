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

    return Settings(
        secret_key=secret_key,
        database_url=database_url,
        bootstrap_demo_user=_env_bool("EXAMINAI_BOOTSTRAP_DEMO", False),
    )


def clear_settings_cache() -> None:
    get_settings.cache_clear()
