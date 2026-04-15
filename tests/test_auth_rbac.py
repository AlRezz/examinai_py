"""Stories 1.3–1.5: session auth, RBAC, CSRF on mutating forms."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from examai.bootstrap import ensure_roles
from examai.config import Settings
from examai.database import get_session_factory
from examai.http.security_middleware import SESSION_USER_KEY
from examai.models import Role, User
from examai.security import hash_password

from tests.conftest import (
    extract_csrf,
    login_with_password,
    signed_session_cookies,
    trigger_lifespan,
)


def _seed_user(email: str, password: str, role_name: str) -> None:
    db = get_session_factory()()
    try:
        ensure_roles(db)
        role = db.execute(select(Role).where(Role.name == role_name)).scalar_one()
        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=hash_password(password),
            enabled=True,
        )
        user.roles.append(role)
        db.add(user)
        db.commit()
    finally:
        db.close()


def test_home_redirects_when_unauthenticated(client: TestClient) -> None:
    trigger_lifespan(client)
    r = client.get("/home", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers.get("location") == "/login"


def test_malformed_session_uid_redirects_to_login(
    client: TestClient, test_settings: Settings
) -> None:
    trigger_lifespan(client)
    for name, value in signed_session_cookies(
        test_settings, {SESSION_USER_KEY: "not-a-uuid"}
    ).items():
        client.cookies.set(name, value)
    r = client.get("/home", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers.get("location") == "/login"


def test_malformed_session_uid_blocked_on_rbac_route(
    client: TestClient, test_settings: Settings
) -> None:
    trigger_lifespan(client)
    for name, value in signed_session_cookies(
        test_settings, {SESSION_USER_KEY: "bogus-id"}
    ).items():
        client.cookies.set(name, value)
    r = client.get("/tasks", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers.get("location") == "/login"


def test_login_logout_and_secure_pages(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("u@example.com", "secret", "intern")

    r = client.get("/login")
    assert r.status_code == 200
    csrf = extract_csrf(r.text)

    bad = client.post(
        "/login",
        data={"username": "u@example.com", "password": "wrong", "csrf_token": csrf},
        follow_redirects=False,
    )
    assert bad.status_code == 303
    assert bad.headers.get("location") == "/login"

    r2 = client.get("/login")
    csrf2 = extract_csrf(r2.text)
    ok = client.post(
        "/login",
        data={"username": "u@example.com", "password": "secret", "csrf_token": csrf2},
        follow_redirects=False,
    )
    assert ok.status_code == 303
    assert ok.headers.get("location") == "/home"

    home = client.get("/home")
    assert home.status_code == 200
    assert "Home" in home.text

    secure = client.get("/app/secure")
    assert secure.status_code == 200
    assert "Secure" in secure.text

    logout_page = client.get("/home")
    logout_csrf = extract_csrf(logout_page.text)
    out = client.post(
        "/logout",
        data={"csrf_token": logout_csrf},
        follow_redirects=False,
    )
    assert out.status_code == 303
    assert out.headers.get("location") == "/login"

    blocked = client.get("/home", follow_redirects=False)
    assert blocked.status_code == 303
    assert blocked.headers.get("location") == "/login"


def test_login_rejects_bad_csrf(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("csrf@example.com", "x", "intern")
    client.post(
        "/login",
        data={
            "username": "csrf@example.com",
            "password": "x",
            "csrf_token": "invalid",
        },
        follow_redirects=False,
    )
    r = client.get("/home", follow_redirects=False)
    assert r.status_code == 303


def test_rbac_intern_blocked_from_tasks(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("intern-only@example.com", "p", "intern")
    login_with_password(client, "intern-only@example.com", "p")
    r = client.get("/tasks")
    assert r.status_code == 403


def test_rbac_mentor_reaches_tasks(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor@example.com", "p", "mentor")
    login_with_password(client, "mentor@example.com", "p")
    r = client.get("/tasks")
    assert r.status_code == 200
    assert "Tasks" in r.text


def test_rbac_admin_reaches_admin_users(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("admin@example.com", "p", "administrator")
    _seed_user("listed@example.com", "p", "intern")
    login_with_password(client, "admin@example.com", "p")
    r = client.get("/admin/users")
    assert r.status_code == 200
    assert "Users" in r.text
    assert "admin@example.com" in r.text
    assert "listed@example.com" in r.text
    assert "$2b$" not in r.text


def test_rbac_mentor_blocked_from_admin_users(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor-admin@example.com", "p", "mentor")
    login_with_password(client, "mentor-admin@example.com", "p")
    assert client.get("/admin/users").status_code == 403


def test_rbac_intern_blocked_from_admin_users(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("intern-admin@example.com", "p", "intern")
    login_with_password(client, "intern-admin@example.com", "p")
    assert client.get("/admin/users").status_code == 403


def test_rbac_coordinator_reaches_coordinator(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("coord@example.com", "p", "coordinator")
    login_with_password(client, "coord@example.com", "p")
    r = client.get("/coordinator")
    assert r.status_code == 200


def test_login_form_includes_csrf_field(client: TestClient) -> None:
    trigger_lifespan(client)
    r = client.get("/login")
    assert 'name="csrf_token"' in r.text
