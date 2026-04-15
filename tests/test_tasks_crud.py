"""Story 2.1: mentor/admin task list, create, edit."""

from __future__ import annotations

import re
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from examai.bootstrap import ensure_roles
from examai.database import get_session_factory
from examai.models import Role, Task, User
from examai.security import hash_password

from tests.conftest import extract_csrf, login_with_password, trigger_lifespan


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


def test_tasks_list_create_edit_happy_path_mentor(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor-crud@example.com", "secret", "mentor")
    login_with_password(client, "mentor-crud@example.com", "secret")

    r_list = client.get("/tasks")
    assert r_list.status_code == 200
    assert "Tasks" in r_list.text
    assert "No tasks yet" in r_list.text

    r_new = client.get("/tasks/new")
    assert r_new.status_code == 200
    csrf = extract_csrf(r_new.text)

    r_post = client.post(
        "/tasks/new",
        data={
            "csrf_token": csrf,
            "title": "  Alpha task  ",
            "description": "Desc line",
            "due_date": "2026-05-01",
        },
        follow_redirects=False,
    )
    assert r_post.status_code == 303
    assert r_post.headers.get("location") == "/tasks"

    after = client.get("/tasks")
    assert after.status_code == 200
    assert "Alpha task" in after.text
    assert "2026-05-01" in after.text

    m = re.search(r'href="/tasks/([0-9a-f-]{36})/edit"', after.text)
    assert m is not None
    task_id = m.group(1)

    r_edit = client.get(f"/tasks/{task_id}/edit")
    assert r_edit.status_code == 200
    assert "Edit task" in r_edit.text
    assert "Alpha task" in r_edit.text
    csrf2 = extract_csrf(r_edit.text)

    r_save = client.post(
        f"/tasks/{task_id}/edit",
        data={
            "csrf_token": csrf2,
            "title": "Alpha task (updated)",
            "description": "",
            "due_date": "",
        },
        follow_redirects=False,
    )
    assert r_save.status_code == 303
    assert r_save.headers.get("location") == "/tasks"

    final = client.get("/tasks")
    assert "Alpha task (updated)" in final.text


def test_tasks_admin_can_mutate(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("admin-crud@example.com", "secret", "administrator")
    login_with_password(client, "admin-crud@example.com", "secret")

    r_new = client.get("/tasks/new")
    csrf = extract_csrf(r_new.text)
    client.post(
        "/tasks/new",
        data={
            "csrf_token": csrf,
            "title": "Admin task",
            "description": "",
            "due_date": "",
        },
        follow_redirects=False,
    )
    home = client.get("/tasks")
    assert "Admin task" in home.text


def test_tasks_intern_forbidden(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("intern-crud@example.com", "secret", "intern")
    login_with_password(client, "intern-crud@example.com", "secret")

    assert client.get("/tasks").status_code == 403
    assert client.get("/tasks/new").status_code == 403
    assert client.post("/tasks/new", data={"csrf_token": "x", "title": "x"}).status_code == 403


def test_tasks_post_rejects_bad_csrf(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor-csrf@example.com", "secret", "mentor")
    login_with_password(client, "mentor-csrf@example.com", "secret")

    r = client.post(
        "/tasks/new",
        data={
            "csrf_token": "not-the-token",
            "title": "Nope",
            "description": "",
            "due_date": "",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers.get("location") == "/tasks/new"

    listed = client.get("/tasks")
    assert "Nope" not in listed.text


def test_tasks_edit_not_found(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor-404@example.com", "secret", "mentor")
    login_with_password(client, "mentor-404@example.com", "secret")

    missing = uuid.uuid4()
    r = client.get(f"/tasks/{missing}/edit")
    assert r.status_code == 404


def test_tasks_validation_title_too_long(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor-long@example.com", "secret", "mentor")
    login_with_password(client, "mentor-long@example.com", "secret")

    r_new = client.get("/tasks/new")
    csrf = extract_csrf(r_new.text)
    long_title = "x" * 501
    r = client.post(
        "/tasks/new",
        data={
            "csrf_token": csrf,
            "title": long_title,
            "description": "",
            "due_date": "",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers.get("location") == "/tasks/new"
    r_form = client.get("/tasks/new")
    assert r_form.status_code == 200
    assert "500 characters" in r_form.text
    listed = client.get("/tasks")
    assert long_title not in listed.text


def test_tasks_validation_empty_title(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor-val@example.com", "secret", "mentor")
    login_with_password(client, "mentor-val@example.com", "secret")

    r_new = client.get("/tasks/new")
    csrf = extract_csrf(r_new.text)
    r = client.post(
        "/tasks/new",
        data={
            "csrf_token": csrf,
            "title": "   ",
            "description": "",
            "due_date": "",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers.get("location") == "/tasks/new"


def test_tasks_persisted_row(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor-db@example.com", "secret", "mentor")
    login_with_password(client, "mentor-db@example.com", "secret")

    r_new = client.get("/tasks/new")
    csrf = extract_csrf(r_new.text)
    client.post(
        "/tasks/new",
        data={
            "csrf_token": csrf,
            "title": "DB check",
            "description": "hello",
            "due_date": "2026-06-15",
        },
        follow_redirects=False,
    )
    db = get_session_factory()()
    try:
        row = db.execute(select(Task).where(Task.title == "DB check")).scalar_one()
        assert row.description == "hello"
        assert row.due_date is not None
        assert row.due_date.isoformat() == "2026-06-15"
    finally:
        db.close()
