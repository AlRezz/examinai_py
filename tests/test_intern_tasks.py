"""Story 3.1: intern task list and detail via task_assignments."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from examai.bootstrap import ensure_roles
from examai.database import get_session_factory
from examai.models import PublishedReview, Role, Submission, Task, TaskAssignment, User
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
    assert "No submission yet" in ok.text

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


def test_intern_post_submission_creates_and_updates_row(client: TestClient) -> None:
    trigger_lifespan(client)
    intern_id = _seed_user("intern-sub@example.com", "secret", "intern")
    task_id = _seed_task("Coord task")
    _assign(task_id, intern_id)
    login_with_password(client, "intern-sub@example.com", "secret")
    page = client.get(f"/intern/tasks/{task_id}")
    token = extract_csrf(page.text)
    r = client.post(
        f"/intern/tasks/{task_id}/submission",
        data={
            "csrf_token": token,
            "repo_identifier": "org/hello",
            "commit_sha": "deadbeef",
            "path_scope": "/pkg",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    assert r.headers.get("location", "").endswith(f"/intern/tasks/{task_id}")

    db = get_session_factory()()
    try:
        sub = db.execute(
            select(Submission).where(
                Submission.task_id == task_id,
                Submission.intern_user_id == intern_id,
            )
        ).scalar_one()
        assert sub.repo_identifier == "org/hello"
        assert sub.commit_sha == "deadbeef"
        assert sub.path_scope == "/pkg"
        assert sub.status == "pending"
    finally:
        db.close()

    page2 = client.get(f"/intern/tasks/{task_id}")
    assert "Coordinates saved" in page2.text
    token2 = extract_csrf(page2.text)
    client.post(
        f"/intern/tasks/{task_id}/submission",
        data={
            "csrf_token": token2,
            "repo_identifier": "org/hello",
            "commit_sha": "updated99",
            "path_scope": "",
        },
        follow_redirects=False,
    )
    db = get_session_factory()()
    try:
        sub = db.execute(
            select(Submission).where(
                Submission.task_id == task_id,
                Submission.intern_user_id == intern_id,
            )
        ).scalar_one()
        assert sub.commit_sha == "updated99"
        assert sub.path_scope is None
    finally:
        db.close()


def test_intern_post_submission_unassigned_task_404(client: TestClient) -> None:
    trigger_lifespan(client)
    intern_id = _seed_user("intern-post-404@example.com", "secret", "intern")
    task_ok = _seed_task("Mine for csrf")
    task_not_mine = _seed_task("Not mine")
    _assign(task_ok, intern_id)
    _assign(task_not_mine, _seed_user("intern-other-post@example.com", "secret", "intern"))

    login_with_password(client, "intern-post-404@example.com", "secret")
    page = client.get(f"/intern/tasks/{task_ok}")
    token = extract_csrf(page.text)
    r = client.post(
        f"/intern/tasks/{task_not_mine}/submission",
        data={
            "csrf_token": token,
            "repo_identifier": "org/x",
            "commit_sha": "",
            "path_scope": "",
        },
        follow_redirects=False,
    )
    assert r.status_code == 404


def test_intern_post_submission_invalid_csrf_redirects(client: TestClient) -> None:
    trigger_lifespan(client)
    intern_id = _seed_user("intern-csrf@example.com", "secret", "intern")
    task_id = _seed_task("Csrf task")
    _assign(task_id, intern_id)
    login_with_password(client, "intern-csrf@example.com", "secret")
    r = client.post(
        f"/intern/tasks/{task_id}/submission",
        data={
            "csrf_token": "not-the-token",
            "repo_identifier": "org/x",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    after = client.get(f"/intern/tasks/{task_id}")
    assert "Invalid or missing security token" in after.text


def _seed_mentor(email: str) -> uuid.UUID:
    return _seed_user(email, "secret", "mentor")


def test_intern_feedback_page_shows_published_review(client: TestClient) -> None:
    trigger_lifespan(client)
    intern_id = _seed_user("intern-fb@example.com", "secret", "intern")
    mentor_id = _seed_mentor("mentor-fb@example.com")
    task_id = _seed_task("Feedback task")
    _assign(task_id, intern_id)
    db = get_session_factory()()
    try:
        sub = Submission(
            task_id=task_id,
            intern_user_id=intern_id,
            repo_identifier="org/r",
            commit_sha="cafef00d",
            path_scope="/app",
            status="pending",
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        sub_id = sub.id
        db.add(
            PublishedReview(
                submission_id=sub_id,
                quality_score=4,
                readability_score=5,
                correctness_score=3,
                narrative="Solid submission.",
                publishing_mentor_user_id=mentor_id,
                snapshot_commit_sha="cafef00d",
                snapshot_path_scope="/app",
            )
        )
        db.commit()
    finally:
        db.close()

    login_with_password(client, "intern-fb@example.com", "secret")
    r = client.get(f"/intern/submissions/{sub_id}/feedback")
    assert r.status_code == 200
    assert "Published feedback" in r.text
    assert "Feedback published" in r.text
    assert "Solid submission." in r.text
    assert "4" in r.text
    assert "Evidence snapshot" in r.text
    assert "cafef00d" in r.text

    detail = client.get(f"/intern/tasks/{task_id}")
    assert detail.status_code == 200
    assert "Feedback published" in detail.text
    assert f'href="/intern/submissions/{sub_id}/feedback"' in detail.text


def test_intern_feedback_404_other_intern_submission(client: TestClient) -> None:
    trigger_lifespan(client)
    mine = _seed_user("intern-mine@example.com", "secret", "intern")
    theirs = _seed_user("intern-theirs@example.com", "secret", "intern")
    mentor_id = _seed_mentor("mentor-404@example.com")
    task_a = _seed_task("A")
    task_b = _seed_task("B")
    _assign(task_a, mine)
    _assign(task_b, theirs)
    db = get_session_factory()()
    try:
        sub = Submission(
            task_id=task_b,
            intern_user_id=theirs,
            repo_identifier="org/x",
            commit_sha=None,
            path_scope=None,
            status="pending",
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        sid = sub.id
        db.add(
            PublishedReview(
                submission_id=sid,
                quality_score=2,
                readability_score=2,
                correctness_score=2,
                narrative="Other",
                publishing_mentor_user_id=mentor_id,
            )
        )
        db.commit()
    finally:
        db.close()

    login_with_password(client, "intern-mine@example.com", "secret")
    assert client.get(f"/intern/submissions/{sid}/feedback").status_code == 404


def test_intern_feedback_404_when_not_published(client: TestClient) -> None:
    trigger_lifespan(client)
    intern_id = _seed_user("intern-nopub@example.com", "secret", "intern")
    task_id = _seed_task("No pub")
    _assign(task_id, intern_id)
    db = get_session_factory()()
    try:
        sub = Submission(
            task_id=task_id,
            intern_user_id=intern_id,
            repo_identifier="org/r",
            commit_sha=None,
            path_scope=None,
            status="pending",
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        sid = sub.id
    finally:
        db.close()

    login_with_password(client, "intern-nopub@example.com", "secret")
    assert client.get(f"/intern/submissions/{sid}/feedback").status_code == 404


def test_non_intern_forbidden_on_intern_feedback_get(client: TestClient) -> None:
    trigger_lifespan(client)
    intern_id = _seed_user("intern-fb403@example.com", "secret", "intern")
    mentor_id = _seed_mentor("mentor-fb403@example.com")
    task_id = _seed_task("Fb403")
    _assign(task_id, intern_id)
    db = get_session_factory()()
    try:
        sub = Submission(
            task_id=task_id,
            intern_user_id=intern_id,
            repo_identifier="org/r",
            commit_sha=None,
            path_scope=None,
            status="pending",
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        sid = sub.id
        db.add(
            PublishedReview(
                submission_id=sid,
                narrative="Hi",
                publishing_mentor_user_id=mentor_id,
            )
        )
        db.commit()
    finally:
        db.close()

    _seed_user("mentor-fb403b@example.com", "secret", "mentor")
    login_with_password(client, "mentor-fb403b@example.com", "secret")
    assert client.get(f"/intern/submissions/{sid}/feedback").status_code == 403


def test_non_intern_forbidden_on_intern_submission_post(client: TestClient) -> None:
    trigger_lifespan(client)
    intern_id = _seed_user("intern-target@example.com", "secret", "intern")
    task_id = _seed_task("Task for mentor post test")
    _assign(task_id, intern_id)
    _seed_user("mentor-post@example.com", "secret", "mentor")
    login_with_password(client, "mentor-post@example.com", "secret")
    page = client.get("/home")
    token = extract_csrf(page.text)
    r = client.post(
        f"/intern/tasks/{task_id}/submission",
        data={"csrf_token": token, "repo_identifier": "org/x"},
    )
    assert r.status_code == 403
