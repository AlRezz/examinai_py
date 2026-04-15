"""Story 7.1: coordinator index, case record, RBAC."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from examai.bootstrap import ensure_roles
from examai.database import get_session_factory
from examai.models import Role, Submission, Task, User
from examai.security import hash_password

from tests.conftest import login_with_password, trigger_lifespan


def _seed_user(email: str, password: str, role_name: str) -> User:
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
        db.refresh(user)
        return user
    finally:
        db.close()


def _seed_task_and_submission(
    *,
    title: str = "Sample task",
    intern: User,
    repo: str = "org/candidate-repo",
) -> tuple[Task, Submission]:
    db = get_session_factory()()
    try:
        task = Task(title=title, description="Desc", due_date=None)
        db.add(task)
        db.commit()
        db.refresh(task)
        sub = Submission(
            id=uuid.uuid4(),
            task_id=task.id,
            intern_user_id=intern.id,
            repo_identifier=repo,
            commit_sha=None,
            path_scope="/",
            status="in_progress",
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        return task, sub
    finally:
        db.close()


def test_coordinator_sees_index_and_case(client: TestClient) -> None:
    trigger_lifespan(client)
    coord = _seed_user("coord7@example.com", "p", "coordinator")
    intern_u = _seed_user("intern7@example.com", "p", "intern")
    _task, sub = _seed_task_and_submission(intern=intern_u)

    login_with_password(client, coord.email, "p")

    idx = client.get("/coordinator")
    assert idx.status_code == 200
    assert "Sample task" in idx.text
    assert "intern7@example.com" in idx.text
    assert str(sub.id) in idx.text

    case = client.get(f"/coordinator/cases/{sub.id}")
    assert case.status_code == 200
    assert "Case record" in case.text
    assert "Sample task" in case.text
    assert "read-only" in case.text.lower()


def test_non_coordinator_denied_coordinator_routes(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("mentor7@example.com", "p", "mentor")
    _seed_user("intern7b@example.com", "p", "intern")
    _seed_user("admin7@example.com", "p", "administrator")

    login_with_password(client, "mentor7@example.com", "p")
    assert client.get("/coordinator").status_code == 403
    assert client.get(f"/coordinator/cases/{uuid.uuid4()}").status_code == 403

    login_with_password(client, "intern7b@example.com", "p")
    assert client.get("/coordinator").status_code == 403

    login_with_password(client, "admin7@example.com", "p")
    assert client.get("/coordinator").status_code == 403
    assert client.get(f"/coordinator/cases/{uuid.uuid4()}").status_code == 403


def test_case_not_found_returns_404(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("coord7c@example.com", "p", "coordinator")
    login_with_password(client, "coord7c@example.com", "p")
    missing = uuid.uuid4()
    r = client.get(f"/coordinator/cases/{missing}")
    assert r.status_code == 404
    assert "not found" in r.text.lower()


def test_invalid_submission_uuid_is_not_server_error(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_user("coord7d@example.com", "p", "coordinator")
    login_with_password(client, "coord7d@example.com", "p")
    r = client.get("/coordinator/cases/not-a-uuid")
    assert r.status_code == 422
