"""Shared test fixtures (isolated in-memory DB)."""

from __future__ import annotations

import json
import re
from base64 import b64encode
from typing import Any, Generator

import itsdangerous
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


def signed_session_cookies(
    settings: Settings,
    session_data: dict[str, Any],
) -> dict[str, str]:
    """Cookies dict for Starlette SessionMiddleware (matches starlette.middleware.sessions encoding)."""
    signer = itsdangerous.TimestampSigner(str(settings.secret_key))
    payload = b64encode(json.dumps(session_data).encode("utf-8"))
    signed = signer.sign(payload)
    return {settings.session_cookie_name: signed.decode("utf-8")}


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
