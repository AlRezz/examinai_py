"""Story 2.2: assign interns to a task."""

from __future__ import annotations

import uuid
from urllib.parse import urlencode

from fastapi.testclient import TestClient
from sqlalchemy import select

from examai.bootstrap import ensure_roles
from examai.database import get_session_factory
from examai.models import Role, Task, TaskAssignment, User
from examai.security import hash_password

from tests.conftest import extract_csrf, login_with_password, trigger_lifespan


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
        task = Task(title=title, description=None, due_date=None)
        db.add(task)
        db.commit()
        tid = task.id
        return tid
    finally:
        db.close()


def test_assignments_save_and_persist(client: TestClient) -> None:
    trigger_lifespan(client)
    mentor_id = _seed_user("mentor-assign@example.com", "secret", "mentor")
    intern_a = _seed_user("intern-a@example.com", "secret", "intern")
    intern_b = _seed_user("intern-b@example.com", "secret", "intern")
    _ = mentor_id
    task_id = _seed_task("Group project")

    login_with_password(client, "mentor-assign@example.com", "secret")

    r_get = client.get(f"/tasks/{task_id}/assignments")
    assert r_get.status_code == 200
    assert "intern-a@example.com" in r_get.text
    assert "intern-b@example.com" in r_get.text
    csrf = extract_csrf(r_get.text)

    body = urlencode(
        [
            ("csrf_token", csrf),
            ("intern_id", str(intern_a)),
            ("intern_id", str(intern_b)),
        ]
    )
    r_post = client.post(
        f"/tasks/{task_id}/assignments",
        content=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        follow_redirects=False,
    )
    assert r_post.status_code == 303
    assert r_post.headers.get("location") == f"/tasks/{task_id}/assignments"

    db = get_session_factory()()
    try:
        rows = db.execute(
            select(TaskAssignment).where(TaskAssignment.task_id == task_id)
        ).scalars().all()
        assigned = {r.intern_user_id for r in rows}
        assert assigned == {intern_a, intern_b}
    finally:
        db.close()

    r_after = client.get(f"/tasks/{task_id}/assignments")
    assert r_after.status_code == 200
    assert 'name="intern_id"' in r_after.text
    assert f'value="{intern_a}"' in r_after.text


def test_assignments_clear_all(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor-clear@example.com", "secret", "mentor")
    intern_a = _seed_user("intern-clear@example.com", "secret", "intern")
    task_id = _seed_task("Solo optional")

    login_with_password(client, "mentor-clear@example.com", "secret")

    r0 = client.get(f"/tasks/{task_id}/assignments")
    csrf0 = extract_csrf(r0.text)
    body0 = urlencode([("csrf_token", csrf0), ("intern_id", str(intern_a))])
    client.post(
        f"/tasks/{task_id}/assignments",
        content=body0,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        follow_redirects=False,
    )

    r1 = client.get(f"/tasks/{task_id}/assignments")
    csrf1 = extract_csrf(r1.text)
    body_clear = urlencode([("csrf_token", csrf1)])
    r_clear = client.post(
        f"/tasks/{task_id}/assignments",
        content=body_clear,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        follow_redirects=False,
    )
    assert r_clear.status_code == 303

    db = get_session_factory()()
    try:
        n = db.execute(
            select(TaskAssignment).where(TaskAssignment.task_id == task_id)
        ).scalars().all()
        assert len(n) == 0
    finally:
        db.close()


def test_assignments_intern_forbidden(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("intern-forbid@example.com", "secret", "intern")
    task_id = _seed_task("No access")

    login_with_password(client, "intern-forbid@example.com", "secret")
    assert client.get(f"/tasks/{task_id}/assignments").status_code == 403


def test_assignments_admin_can_save(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("admin-assign@example.com", "secret", "administrator")
    intern_id = _seed_user("intern-admin@example.com", "secret", "intern")
    task_id = _seed_task("Admin assigns")

    login_with_password(client, "admin-assign@example.com", "secret")
    r_get = client.get(f"/tasks/{task_id}/assignments")
    assert r_get.status_code == 200
    csrf = extract_csrf(r_get.text)
    body = urlencode([("csrf_token", csrf), ("intern_id", str(intern_id))])
    r_post = client.post(
        f"/tasks/{task_id}/assignments",
        content=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        follow_redirects=False,
    )
    assert r_post.status_code == 303
    db = get_session_factory()()
    try:
        rows = db.execute(
            select(TaskAssignment).where(TaskAssignment.task_id == task_id)
        ).scalars().all()
        assert len(rows) == 1
        assert rows[0].intern_user_id == intern_id
    finally:
        db.close()


def test_assignments_rejects_malformed_intern_id(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor-malform@example.com", "secret", "mentor")
    task_id = _seed_task("Tamper")

    login_with_password(client, "mentor-malform@example.com", "secret")
    r = client.get(f"/tasks/{task_id}/assignments")
    csrf = extract_csrf(r.text)
    body = urlencode([("csrf_token", csrf), ("intern_id", "not-a-uuid")])
    r_post = client.post(
        f"/tasks/{task_id}/assignments",
        content=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        follow_redirects=False,
    )
    assert r_post.status_code == 303
    r2 = client.get(f"/tasks/{task_id}/assignments")
    assert "Invalid selection" in r2.text
    db = get_session_factory()()
    try:
        rows = db.execute(
            select(TaskAssignment).where(TaskAssignment.task_id == task_id)
        ).scalars().all()
        assert len(rows) == 0
    finally:
        db.close()


def test_assignments_rejects_non_intern_id(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor-bad@example.com", "secret", "mentor")
    mentor_other = _seed_user("mentor-other@example.com", "secret", "mentor")
    task_id = _seed_task("Bad pick")

    login_with_password(client, "mentor-bad@example.com", "secret")
    r = client.get(f"/tasks/{task_id}/assignments")
    csrf = extract_csrf(r.text)
    body = urlencode([("csrf_token", csrf), ("intern_id", str(mentor_other))])
    r_post = client.post(
        f"/tasks/{task_id}/assignments",
        content=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        follow_redirects=False,
    )
    assert r_post.status_code == 303
    r2 = client.get(f"/tasks/{task_id}/assignments")
    assert "not interns" in r2.text

    db = get_session_factory()()
    try:
        rows = db.execute(
            select(TaskAssignment).where(TaskAssignment.task_id == task_id)
        ).scalars().all()
        assert len(rows) == 0
    finally:
        db.close()


def test_assignments_get_not_found(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor-404a@example.com", "secret", "mentor")
    login_with_password(client, "mentor-404a@example.com", "secret")
    missing = uuid.uuid4()
    r = client.get(f"/tasks/{missing}/assignments")
    assert r.status_code == 404


def test_task_list_has_assign_link(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor-link@example.com", "secret", "mentor")
    task_id = _seed_task("Linked task")

    login_with_password(client, "mentor-link@example.com", "secret")
    r = client.get("/tasks")
    assert r.status_code == 200
    assert f'href="/tasks/{task_id}/assignments"' in r.text
