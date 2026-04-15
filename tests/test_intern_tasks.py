"""Story 3.1: intern task list and detail via task_assignments."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from examai.bootstrap import ensure_roles
from examai.database import get_session_factory
from examai.models import Role, Task, TaskAssignment, User
from examai.security import hash_password

from tests.conftest import login_with_password, trigger_lifespan


def _seed_user(email: str, password: str, role_name: str) -> uuid.UUID:
    db = get_session_factory()()
    try:
        ensure_roles(db)
        role = db.execute(select(Role).where(Role.name == role_name)).scalar_one()
        uid = uuid.uuid4()
        user = User(
            id=uid,
            email=email,
            password_hash=hash_password(password),
            enabled=True,
        )
        user.roles.append(role)
        db.add(user)
        db.commit()
        return uid
    finally:
        db.close()


def _seed_task(title: str) -> uuid.UUID:
    db = get_session_factory()()
    try:
        task = Task(title=title, description="Desc", due_date=None)
        db.add(task)
        db.commit()
        return task.id
    finally:
        db.close()


def _assign(task_id: uuid.UUID, intern_user_id: uuid.UUID) -> None:
    db = get_session_factory()()
    try:
        db.add(TaskAssignment(task_id=task_id, intern_user_id=intern_user_id))
        db.commit()
    finally:
        db.close()


def test_intern_list_shows_only_assigned_tasks(client: TestClient) -> None:
    trigger_lifespan(client)
    intern_a = _seed_user("intern-list-a@example.com", "secret", "intern")
    intern_b = _seed_user("intern-list-b@example.com", "secret", "intern")
    task_mine = _seed_task("Mine")
    task_other = _seed_task("Other intern only")
    _assign(task_mine, intern_a)
    _assign(task_other, intern_b)

    login_with_password(client, "intern-list-a@example.com", "secret")
    r = client.get("/intern/tasks")
    assert r.status_code == 200
    assert "Mine" in r.text
    assert "Other intern only" not in r.text
    assert 'href="/intern/tasks/' in r.text


def test_intern_task_detail_and_unassigned_is_404(client: TestClient) -> None:
    trigger_lifespan(client)
    intern_id = _seed_user("intern-detail@example.com", "secret", "intern")
    task_ok = _seed_task("Assigned detail")
    task_not_mine = _seed_task("Not assigned to me")
    _assign(task_ok, intern_id)
    _assign(task_not_mine, _seed_user("intern-other@example.com", "secret", "intern"))

    login_with_password(client, "intern-detail@example.com", "secret")

    ok = client.get(f"/intern/tasks/{task_ok}")
    assert ok.status_code == 200
    assert "Assigned detail" in ok.text
    assert "Desc" in ok.text

    missing = uuid.uuid4()
    assert client.get(f"/intern/tasks/{missing}").status_code == 404

    nope = client.get(f"/intern/tasks/{task_not_mine}")
    assert nope.status_code == 404


def test_non_intern_forbidden_on_intern_tasks(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor-intern-space@example.com", "secret", "mentor")
    login_with_password(client, "mentor-intern-space@example.com", "secret")
    assert client.get("/intern/tasks").status_code == 403


def test_intern_tasks_requires_login(client: TestClient) -> None:
    trigger_lifespan(client)
    r = client.get("/intern/tasks", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers.get("location") == "/login"
