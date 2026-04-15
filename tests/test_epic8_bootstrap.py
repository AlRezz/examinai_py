"""Epic 8: Liquibase CLI guardrails and initial administrator seed."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from examai.config import Settings
from examai.main import create_app

from tests.conftest import login_with_password, trigger_lifespan


def test_liquibase_cli_skips_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EXAMINAI_USE_LIQUIBASE", raising=False)
    from examai import liquibase_cli

    assert liquibase_cli.main() == 0


def test_liquibase_cli_errors_when_postgres_expected_but_url_is_sqlite(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EXAMINAI_USE_LIQUIBASE", "1")
    monkeypatch.setenv("EXAMINAI_DATABASE_URL", "sqlite+pysqlite:///:memory:")
    from examai import liquibase_cli

    assert liquibase_cli.main() == 1


def test_initial_admin_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EXAMINAI_ADMIN_INITIAL_PASSWORD", "SeedPass!234")
    settings = Settings(
        secret_key="test-secret-key-unit-tests-only",
        database_url="sqlite+pysqlite:///:memory:",
        bootstrap_demo_user=False,
    )
    app = create_app(settings)
    with TestClient(app) as client:
        trigger_lifespan(client)
        login_with_password(client, "admin@examinai.local", "SeedPass!234")
        r = client.get("/admin/users", follow_redirects=False)
        assert r.status_code == 200
