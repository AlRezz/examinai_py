"""Stories 6.2–6.3: admin create and edit users with roles."""

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


def test_admin_edit_user_form(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("admin-ed@example.com", "p", "administrator")
    _seed_user("subject@example.com", "pw", "intern")
    login_with_password(client, "admin-ed@example.com", "p")
    uid = _user_id_by_email("subject@example.com")
    r = client.get(f"/admin/users/{uid}/edit")
    assert r.status_code == 200
    assert "Edit user" in r.text
    assert "subject@example.com" in r.text
    assert 'name="role_name"' in r.text
    assert "$2b$" not in r.text


def test_admin_edits_user_roles_and_email(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("admin-e2@example.com", "p", "administrator")
    _seed_user("editable@example.com", "pw", "intern")
    login_with_password(client, "admin-e2@example.com", "p")
    uid = _user_id_by_email("editable@example.com")
    r = client.get(f"/admin/users/{uid}/edit")
    csrf = extract_csrf(r.text)
    r2 = client.post(
        f"/admin/users/{uid}/edit",
        data={
            "csrf_token": csrf,
            "email": "updated@example.com",
            "password": "",
            "enabled": "on",
            "role_name": ["mentor"],
        },
        follow_redirects=False,
    )
    assert r2.status_code == 303
    assert r2.headers.get("location") == "/admin/users"

    db = get_session_factory()()
    try:
        u = db.execute(select(User).where(User.email == "updated@example.com")).scalar_one_or_none()
        assert u is not None
        assert {role.name for role in u.roles} == {"mentor"}
    finally:
        db.close()


def test_edit_password_optional_preserves_hash(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("admin-ph@example.com", "p", "administrator")
    _seed_user("keeppw@example.com", "secret99", "intern")
    uid = _user_id_by_email("keeppw@example.com")
    db = get_session_factory()()
    try:
        before = db.execute(select(User).where(User.id == uid)).scalar_one()
        h1 = before.password_hash
    finally:
        db.close()

    login_with_password(client, "admin-ph@example.com", "p")
    r = client.get(f"/admin/users/{uid}/edit")
    csrf = extract_csrf(r.text)
    client.post(
        f"/admin/users/{uid}/edit",
        data={
            "csrf_token": csrf,
            "email": "keeppw@example.com",
            "password": "",
            "enabled": "on",
            "role_name": ["intern"],
        },
        follow_redirects=False,
    )
    db = get_session_factory()()
    try:
        after = db.execute(select(User).where(User.id == uid)).scalar_one()
        assert after.password_hash == h1
    finally:
        db.close()


def test_non_admin_forbidden_from_edit(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor-ed@example.com", "p", "mentor")
    _seed_user("victim@example.com", "x", "intern")
    uid = _user_id_by_email("victim@example.com")
    login_with_password(client, "mentor-ed@example.com", "p")
    assert client.get(f"/admin/users/{uid}/edit").status_code == 403


def test_edit_unknown_user_404(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("admin-404@example.com", "p", "administrator")
    login_with_password(client, "admin-404@example.com", "p")
    missing = uuid.uuid4()
    assert client.get(f"/admin/users/{missing}/edit").status_code == 404


def test_edit_user_rejects_bad_csrf(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("admin-ec@example.com", "p", "administrator")
    _seed_user("csrf-t@example.com", "x", "intern")
    uid = _user_id_by_email("csrf-t@example.com")
    login_with_password(client, "admin-ec@example.com", "p")
    r = client.post(
        f"/admin/users/{uid}/edit",
        data={
            "csrf_token": "nope",
            "email": "csrf-t@example.com",
            "role_name": ["intern"],
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers.get("location") == f"/admin/users/{uid}/edit"
    r2 = client.get(f"/admin/users/{uid}/edit")
    assert "Invalid or missing security token" in r2.text


def test_edit_user_duplicate_email(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("admin-dp2@example.com", "p", "administrator")
    _seed_user("a@example.com", "p", "intern")
    _seed_user("b@example.com", "p", "intern")
    login_with_password(client, "admin-dp2@example.com", "p")
    bid = _user_id_by_email("b@example.com")
    r = client.get(f"/admin/users/{bid}/edit")
    csrf = extract_csrf(r.text)
    r2 = client.post(
        f"/admin/users/{bid}/edit",
        data={
            "csrf_token": csrf,
            "email": "a@example.com",
            "password": "",
            "enabled": "on",
            "role_name": ["intern"],
        },
        follow_redirects=False,
    )
    assert r2.status_code == 303
    r3 = client.get(f"/admin/users/{bid}/edit")
    assert "already exists" in r3.text.lower()


def test_admin_cannot_strip_own_admin_role(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("self-ad@example.com", "p", "administrator")
    login_with_password(client, "self-ad@example.com", "p")
    uid = _user_id_by_email("self-ad@example.com")
    r = client.get(f"/admin/users/{uid}/edit")
    csrf = extract_csrf(r.text)
    r2 = client.post(
        f"/admin/users/{uid}/edit",
        data={
            "csrf_token": csrf,
            "email": "self-ad@example.com",
            "password": "",
            "enabled": "on",
            "role_name": ["intern"],
        },
        follow_redirects=False,
    )
    assert r2.status_code == 303
    r3 = client.get(f"/admin/users/{uid}/edit")
    assert "cannot remove your own administrator" in r3.text.lower()


def test_admin_cannot_disable_self(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("self-dis@example.com", "p", "administrator")
    login_with_password(client, "self-dis@example.com", "p")
    uid = _user_id_by_email("self-dis@example.com")
    r = client.get(f"/admin/users/{uid}/edit")
    csrf = extract_csrf(r.text)
    r2 = client.post(
        f"/admin/users/{uid}/edit",
        data={
            "csrf_token": csrf,
            "email": "self-dis@example.com",
            "password": "",
            "enabled": "",
            "role_name": ["administrator"],
        },
        follow_redirects=False,
    )
    assert r2.status_code == 303
    r3 = client.get(f"/admin/users/{uid}/edit")
    assert "cannot disable your own account" in r3.text.lower()
