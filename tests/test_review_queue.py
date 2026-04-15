"""Story 4.6: GET /review/queue mentor review queue (FR24)."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from examai.bootstrap import ensure_roles
from examai.database import get_session_factory
from examai.models import PublishedReview, Submission, Task, TaskAssignment, User
from examai.security import hash_password

from tests.conftest import login_with_password, trigger_lifespan


def _seed_role_user(email: str, password: str, role_name: str) -> User:
    from sqlalchemy import select

    from examai.models import Role

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


def test_review_queue_ok_for_mentor_shows_outstanding(client: TestClient) -> None:
    trigger_lifespan(client)
    mentor = _seed_role_user("rq-mentor@example.com", "secret", "mentor")
    intern = _seed_role_user("rq-intern@example.com", "secret", "intern")
    db = get_session_factory()()
    try:
        task = Task(title="Queue Task Alpha", description=None, due_date=None)
        db.add(task)
        db.commit()
        db.refresh(task)
        task_id = task.id
        intern_id = intern.id
        db.add(TaskAssignment(task_id=task_id, intern_user_id=intern_id))
        sub = Submission(
            task_id=task_id,
            intern_user_id=intern_id,
            repo_identifier="org/rq",
            commit_sha="deadbeef",
            path_scope="/",
            status="in_progress",
        )
        db.add(sub)
        db.commit()
    finally:
        db.close()

    login_with_password(client, mentor.email, "secret")
    r = client.get("/review/queue")
    assert r.status_code == 200
    assert "Review queue" in r.text
    assert "Queue Task Alpha" in r.text
    assert "rq-intern@example.com" in r.text
    assert "in_progress" in r.text
    assert f"/tasks/{task_id}/submissions/{intern_id}" in r.text


def test_review_queue_excludes_published(client: TestClient) -> None:
    trigger_lifespan(client)
    mentor = _seed_role_user("rq-mentor-pub@example.com", "secret", "mentor")
    intern = _seed_role_user("rq-intern-pub@example.com", "secret", "intern")
    db = get_session_factory()()
    try:
        task = Task(title="Published Task", description=None, due_date=None)
        db.add(task)
        db.commit()
        db.refresh(task)
        db.add(TaskAssignment(task_id=task.id, intern_user_id=intern.id))
        sub = Submission(
            task_id=task.id,
            intern_user_id=intern.id,
            repo_identifier="org/pub",
            commit_sha="abc",
            path_scope="/",
            status="done",
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        db.add(
            PublishedReview(
                submission_id=sub.id,
                quality_score=3,
                readability_score=3,
                correctness_score=3,
                narrative="ok",
                publishing_mentor_user_id=mentor.id,
                snapshot_commit_sha=sub.commit_sha,
                snapshot_git_fetch_version=sub.git_fetch_version,
                snapshot_path_scope=sub.path_scope,
            )
        )
        db.commit()
    finally:
        db.close()

    login_with_password(client, mentor.email, "secret")
    r = client.get("/review/queue")
    assert r.status_code == 200
    assert "Published Task" not in r.text


def test_review_queue_shows_awaiting_submission(client: TestClient) -> None:
    trigger_lifespan(client)
    mentor = _seed_role_user("rq-mentor-await@example.com", "secret", "mentor")
    intern = _seed_role_user("rq-intern-await@example.com", "secret", "intern")
    db = get_session_factory()()
    try:
        task = Task(title="No Sub Yet", description=None, due_date=None)
        db.add(task)
        db.commit()
        db.refresh(task)
        db.add(TaskAssignment(task_id=task.id, intern_user_id=intern.id))
        db.commit()
    finally:
        db.close()

    login_with_password(client, mentor.email, "secret")
    r = client.get("/review/queue")
    assert r.status_code == 200
    assert "Awaiting submission" in r.text
    assert "No Sub Yet" in r.text


def test_intern_forbidden_on_review_queue(client: TestClient) -> None:
    trigger_lifespan(client)
    _seed_role_user("rq-intern-only@example.com", "secret", "intern")
    login_with_password(client, "rq-intern-only@example.com", "secret")
    r = client.get("/review/queue")
    assert r.status_code == 403
