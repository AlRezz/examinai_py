"""Story 6.2: admin create user with roles."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from examai.bootstrap import ensure_roles
from examai.database import get_session_factory
from examai.models import Role, User
from examai.security import hash_password

from tests.conftest import extract_csrf, login_with_password, trigger_lifespan


def _user_id_by_email(email: str) -> uuid.UUID:
    db = get_session_factory()()
    try:
        u = db.execute(select(User).where(User.email == email)).scalar_one()
        return u.id
    finally:
        db.close()


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


def test_admin_new_user_form_lists_roles(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("admin-nu@example.com", "p", "administrator")
    login_with_password(client, "admin-nu@example.com", "p")
    r = client.get("/admin/users/new")
    assert r.status_code == 200
    assert "New user" in r.text
    assert 'name="role_name"' in r.text
    assert "intern" in r.text
    assert "administrator" in r.text
    assert "$2b$" not in r.text


def test_admin_creates_user_with_roles(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("admin-cr@example.com", "p", "administrator")
    login_with_password(client, "admin-cr@example.com", "p")
    r = client.get("/admin/users/new")
    csrf = extract_csrf(r.text)
    r2 = client.post(
        "/admin/users/new",
        data={
            "csrf_token": csrf,
            "email": "newbie@example.com",
            "password": "secret123",
            "enabled": "on",
            "role_name": ["intern", "mentor"],
        },
        follow_redirects=False,
    )
    assert r2.status_code == 303
    assert r2.headers.get("location") == "/admin/users"

    db = get_session_factory()()
    try:
        u = db.execute(select(User).where(User.email == "newbie@example.com")).scalar_one_or_none()
        assert u is not None
        assert u.enabled is True
        names = {r.name for r in u.roles}
        assert names == {"intern", "mentor"}
    finally:
        db.close()

    listing = client.get("/admin/users")
    assert listing.status_code == 200
    assert "newbie@example.com" in listing.text


def test_new_user_can_sign_in(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("admin-si@example.com", "p", "administrator")
    login_with_password(client, "admin-si@example.com", "p")
    r = client.get("/admin/users/new")
    csrf = extract_csrf(r.text)
    client.post(
        "/admin/users/new",
        data={
            "csrf_token": csrf,
            "email": "signin@example.com",
            "password": "their-password",
            "enabled": "on",
            "role_name": ["intern"],
        },
        follow_redirects=False,
    )
    client.get("/actuator/health")
    lr = client.get("/login")
    csrf_login = extract_csrf(lr.text)
    ok = client.post(
        "/login",
        data={
            "username": "signin@example.com",
            "password": "their-password",
            "csrf_token": csrf_login,
        },
        follow_redirects=False,
    )
    assert ok.status_code == 303
    assert ok.headers.get("location") == "/home"


def test_non_admin_forbidden_from_new_user(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor-nu@example.com", "p", "mentor")
    login_with_password(client, "mentor-nu@example.com", "p")
    assert client.get("/admin/users/new").status_code == 403


def test_create_user_rejects_bad_csrf(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("admin-csrf@example.com", "p", "administrator")
    login_with_password(client, "admin-csrf@example.com", "p")
    r = client.post(
        "/admin/users/new",
        data={
            "csrf_token": "nope",
            "email": "x@example.com",
            "password": "x",
            "role_name": ["intern"],
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers.get("location") == "/admin/users/new"
    r2 = client.get("/admin/users/new")
    assert "Invalid or missing security token" in r2.text


def test_create_user_duplicate_email(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("admin-dup@example.com", "p", "administrator")
    _seed_user("exists@example.com", "p", "intern")
    login_with_password(client, "admin-dup@example.com", "p")
    r = client.get("/admin/users/new")
    csrf = extract_csrf(r.text)
    r2 = client.post(
        "/admin/users/new",
        data={
            "csrf_token": csrf,
            "email": "exists@example.com",
            "password": "another",
            "enabled": "on",
            "role_name": ["mentor"],
        },
        follow_redirects=False,
    )
    assert r2.status_code == 303
    r3 = client.get("/admin/users/new")
    assert "already exists" in r3.text.lower()


def test_create_user_requires_role(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("admin-roles@example.com", "p", "administrator")
    login_with_password(client, "admin-roles@example.com", "p")
    r = client.get("/admin/users/new")
    csrf = extract_csrf(r.text)
    r2 = client.post(
        "/admin/users/new",
        data={
            "csrf_token": csrf,
            "email": "noroles@example.com",
            "password": "secret123",
            "enabled": "on",
        },
        follow_redirects=False,
    )
    assert r2.status_code == 303
    r3 = client.get("/admin/users/new")
    assert "at least one role" in r3.text.lower()
