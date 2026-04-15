"""Shared test fixtures (isolated in-memory DB)."""

from __future__ import annotations

import re
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from examai.config import Settings
from examai.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        secret_key="test-secret-key-unit-tests-only",
        database_url="sqlite+pysqlite:///:memory:",
        bootstrap_demo_user=False,
    )


@pytest.fixture
def app(test_settings: Settings):
    return create_app(test_settings)


@pytest.fixture
def client(app) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


def trigger_lifespan(client: TestClient) -> None:
    """First request starts lifespan (schema + roles)."""
    client.get("/actuator/health")


def extract_csrf(html: str) -> str:
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
    assert m is not None, "csrf_token field not found in HTML"
    return m.group(1)


def login_with_password(client: TestClient, email: str, password: str) -> TestClient:
    r = client.get("/login")
    token = extract_csrf(r.text)
    client.post(
        "/login",
        data={
            "username": email,
            "password": password,
            "csrf_token": token,
        },
    )
    return client
