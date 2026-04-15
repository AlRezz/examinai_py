"""Epic 5: mentor workspace, AI draft audit, degraded LLM messaging."""

from __future__ import annotations

import uuid
from dataclasses import replace
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import select

from examai.bootstrap import ensure_roles
from examai.database import get_session_factory
from examai.integration.ai import OllamaClientError
from examai.integration.git_provider import GitFetchResult
from examai.models import AiDraft, MentorReviewDraft, ModelInvocation, PublishedReview, Submission, Task, User
from examai.security import hash_password

from tests.conftest import extract_csrf, login_with_password, trigger_lifespan


def _seed_user(email: str, password: str, role_name: str) -> User:
    from sqlalchemy import select as sa_select
    from examai.models import Role

    db = get_session_factory()()
    try:
        ensure_roles(db)
        role = db.execute(sa_select(Role).where(Role.name == role_name)).scalar_one()
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


def _seed_task_with_submission(
    *,
    mentor_email: str = "mw-mentor@example.com",
    intern_email: str = "mw-intern@example.com",
) -> tuple[User, User, uuid.UUID, uuid.UUID, uuid.UUID]:
    mentor = _seed_user(mentor_email, "secret", "mentor")
    intern = _seed_user(intern_email, "secret", "intern")
    db = get_session_factory()()
    try:
        from examai.models import TaskAssignment

        task = Task(title="AI task", description="Task body for prompt.", due_date=None)
        db.add(task)
        db.commit()
        db.refresh(task)
        task_id = task.id
        intern_id = intern.id
        db.add(TaskAssignment(task_id=task_id, intern_user_id=intern_id))
        sub = Submission(
            task_id=task_id,
            intern_user_id=intern_id,
            repo_identifier="org/repo",
            commit_sha="abc123",
            path_scope="/src",
            status="in_progress",
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
        sub_id = sub.id
        return mentor, intern, task_id, intern_id, sub_id
    finally:
        db.close()


def test_submissions_list_and_workspace_renders(client: TestClient) -> None:
    trigger_lifespan(client)
    mentor, intern, task_id, intern_id, _sub_id = _seed_task_with_submission()
    login_with_password(client, mentor.email, "secret")

    lst = client.get(f"/tasks/{task_id}/submissions")
    assert lst.status_code == 200
    assert intern.email in lst.text

    ws = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
    assert ws.status_code == 200
    assert "Mentor workspace" in ws.text
    assert "AI draft" in ws.text


def test_intern_forbidden_on_mentor_submissions_routes(client: TestClient) -> None:
    """Story 4.1 AC4: /tasks/** is mentor or administrator only (FR5)."""
    trigger_lifespan(client)
    _seed_user("mw-intern-rbac@example.com", "secret", "intern")
    login_with_password(client, "mw-intern-rbac@example.com", "secret")
    tid, iid = uuid.uuid4(), uuid.uuid4()
    assert client.get(f"/tasks/{tid}/submissions").status_code == 403
    assert client.get(f"/tasks/{tid}/submissions/{iid}").status_code == 403


def test_administrator_can_open_submissions_list_and_workspace(client: TestClient) -> None:
    """Story 4.1 AC4: administrators share mentor task/submission space."""
    trigger_lifespan(client)
    from examai.models import TaskAssignment

    admin = _seed_user("mw-admin-sub@example.com", "secret", "administrator")
    intern = _seed_user("mw-intern-admin@example.com", "secret", "intern")
    db = get_session_factory()()
    try:
        task = Task(title="Admin submissions task", description="x", due_date=None)
        db.add(task)
        db.commit()
        db.refresh(task)
        task_id = task.id
        db.add(TaskAssignment(task_id=task_id, intern_user_id=intern.id))
        db.commit()
    finally:
        db.close()

    login_with_password(client, admin.email, "secret")
    lst = client.get(f"/tasks/{task_id}/submissions")
    assert lst.status_code == 200
    assert intern.email in lst.text
    ws = client.get(f"/tasks/{task_id}/submissions/{intern.id}")
    assert ws.status_code == 200
    assert "Mentor workspace" in ws.text


def test_ai_draft_post_persists_audit_rows(client: TestClient, test_settings) -> None:
    trigger_lifespan(client)
    mentor, intern, task_id, intern_id, sub_id = _seed_task_with_submission()
    login_with_password(client, mentor.email, "secret")

    class _FakeClient:
        def __init__(self, *a, **k) -> None:
            pass

        def __enter__(self) -> "_FakeClient":
            return self

        def __exit__(self, *a) -> None:
            pass

        def post(self, url: str, json=None):
            class R:
                status_code = 200

                def raise_for_status(self) -> None:
                    pass

                def json(self):
                    return {"model": "m1", "response": "Assessment draft body.", "done": True}

            return R()

    patched_settings = replace(
        test_settings,
        ollama_base_url="http://127.0.0.1:11434",
        ollama_model="test-model",
    )

    with patch("examai.mentor_workspace_routes.get_settings", lambda: patched_settings):
        with patch("examai.integration.ai.httpx.Client", _FakeClient):
            page = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
            csrf = extract_csrf(page.text)
            r = client.post(
                f"/tasks/{task_id}/submissions/{intern_id}/ai-draft-assessment",
                data={"csrf_token": csrf},
                follow_redirects=False,
            )
            assert r.status_code == 303

    db = get_session_factory()()
    try:
        inv = db.execute(select(ModelInvocation).where(ModelInvocation.submission_id == sub_id)).scalar_one()
        assert inv.prompt_hash
        assert inv.model_name
        draft = db.execute(select(AiDraft).where(AiDraft.model_invocation_id == inv.id)).scalar_one()
        assert "Assessment draft" in draft.assessment_text
    finally:
        db.close()

    after = client.get(f"/tasks/{task_id}/submissions/{intern_id}", follow_redirects=False)
    assert after.status_code == 200
    assert "Assessment draft body" in after.text


def test_ai_unconfigured_shows_degraded_and_skips_llm(client: TestClient, test_settings) -> None:
    trigger_lifespan(client)
    mentor, intern, task_id, intern_id, sub_id = _seed_task_with_submission(
        mentor_email="mw-mentor2@example.com",
        intern_email="mw-intern2@example.com",
    )
    login_with_password(client, mentor.email, "secret")

    patched = replace(test_settings, ollama_base_url="")
    with patch("examai.mentor_workspace_routes.get_settings", lambda: patched):
        page = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
        assert "AI draft limited" in page.text or "not configured" in page.text.lower()

        csrf = extract_csrf(page.text)
        with patch("examai.integration.ai.httpx.Client") as mock_client:
            client.post(
                f"/tasks/{task_id}/submissions/{intern_id}/ai-draft-assessment",
                data={"csrf_token": csrf},
                follow_redirects=False,
            )
            mock_client.assert_not_called()

    db = get_session_factory()()
    try:
        n = db.execute(select(ModelInvocation).where(ModelInvocation.submission_id == sub_id)).all()
        assert len(n) == 0
    finally:
        db.close()


def test_manual_review_save_works_without_ai(client: TestClient, test_settings) -> None:
    trigger_lifespan(client)
    mentor, intern, task_id, intern_id, _sub_id = _seed_task_with_submission(
        mentor_email="mw-mentor3@example.com",
        intern_email="mw-intern3@example.com",
    )
    login_with_password(client, mentor.email, "secret")

    patched = replace(test_settings, ollama_base_url="")
    with patch("examai.mentor_workspace_routes.get_settings", lambda: patched):
        page = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
        csrf = extract_csrf(page.text)
        r = client.post(
            f"/tasks/{task_id}/submissions/{intern_id}/review-draft",
            data={
                "csrf_token": csrf,
                "quality_score": "4",
                "readability_score": "",
                "correctness_score": "",
                "narrative_feedback": "Good work on structure.",
            },
            follow_redirects=False,
        )
        assert r.status_code == 303

    page2 = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
    assert "Good work on structure." in page2.text


def test_review_draft_post_persists_mentor_review_drafts_row(client: TestClient, test_settings) -> None:
    """Story 4.4: POST .../review-draft persists mentor_review_drafts per data-models."""
    trigger_lifespan(client)
    mentor, intern, task_id, intern_id, sub_id = _seed_task_with_submission(
        mentor_email="mw-mentor44@example.com",
        intern_email="mw-intern44@example.com",
    )
    login_with_password(client, mentor.email, "secret")

    patched = replace(test_settings, ollama_base_url="")
    with patch("examai.mentor_workspace_routes.get_settings", lambda: patched):
        page = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
        csrf = extract_csrf(page.text)
        r = client.post(
            f"/tasks/{task_id}/submissions/{intern_id}/review-draft",
            data={
                "csrf_token": csrf,
                "quality_score": "4",
                "readability_score": "3",
                "correctness_score": "5",
                "narrative_feedback": "Iterate before publish.",
            },
            follow_redirects=False,
        )
        assert r.status_code == 303

    db = get_session_factory()()
    try:
        row = db.execute(select(MentorReviewDraft).where(MentorReviewDraft.submission_id == sub_id)).scalar_one()
        assert row.quality_score == 4
        assert row.readability_score == 3
        assert row.correctness_score == 5
        assert row.narrative_feedback == "Iterate before publish."
        assert row.mentor_user_id == mentor.id
    finally:
        db.close()


def test_ai_draft_post_ollama_error_no_audit_rows_and_banner(client: TestClient, test_settings) -> None:
    trigger_lifespan(client)
    mentor, intern, task_id, intern_id, sub_id = _seed_task_with_submission(
        mentor_email="mw-mentor-fail@example.com",
        intern_email="mw-intern-fail@example.com",
    )
    login_with_password(client, mentor.email, "secret")

    patched_settings = replace(
        test_settings,
        ollama_base_url="http://127.0.0.1:11434",
        ollama_model="test-model",
    )

    def _fail_ollama(**_kwargs) -> None:
        raise OllamaClientError("upstream timed out")

    with patch("examai.mentor_workspace_routes.get_settings", lambda: patched_settings):
        with patch("examai.mentor_workspace_routes.ollama_generate", _fail_ollama):
            page = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
            csrf = extract_csrf(page.text)
            r = client.post(
                f"/tasks/{task_id}/submissions/{intern_id}/ai-draft-assessment",
                data={"csrf_token": csrf},
                follow_redirects=False,
            )
            assert r.status_code == 303

    db = get_session_factory()()
    try:
        rows = db.execute(select(ModelInvocation).where(ModelInvocation.submission_id == sub_id)).all()
        assert len(rows) == 0
    finally:
        db.close()

    after = client.get(f"/tasks/{task_id}/submissions/{intern_id}", follow_redirects=False)
    assert after.status_code == 200
    assert "could not" in after.text.lower()
    assert "AI draft limited" in after.text or "unavailable" in after.text.lower()


def test_ai_draft_error_flash_truncates_long_upstream_message(client: TestClient, test_settings) -> None:
    trigger_lifespan(client)
    mentor, intern, task_id, intern_id, _sub_id = _seed_task_with_submission(
        mentor_email="mw-mentor-longerr@example.com",
        intern_email="mw-intern-longerr@example.com",
    )
    login_with_password(client, mentor.email, "secret")
    long_err = "Z" * 600

    patched_settings = replace(
        test_settings,
        ollama_base_url="http://127.0.0.1:11434",
        ollama_model="test-model",
    )

    def _fail_long(**_kwargs) -> None:
        raise OllamaClientError(long_err)

    with patch("examai.mentor_workspace_routes.get_settings", lambda: patched_settings):
        with patch("examai.mentor_workspace_routes.ollama_generate", _fail_long):
            page = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
            csrf = extract_csrf(page.text)
            client.post(
                f"/tasks/{task_id}/submissions/{intern_id}/ai-draft-assessment",
                data={"csrf_token": csrf},
                follow_redirects=False,
            )

    after = client.get(f"/tasks/{task_id}/submissions/{intern_id}", follow_redirects=False)
    assert after.status_code == 200
    assert long_err not in after.text
    assert "…" in after.text or "could not" in after.text.lower()


def test_publish_review_persists_and_shows_flash(client: TestClient, test_settings) -> None:
    trigger_lifespan(client)
    mentor, intern, task_id, intern_id, sub_id = _seed_task_with_submission(
        mentor_email="mw-mentor-pub@example.com",
        intern_email="mw-intern-pub@example.com",
    )
    login_with_password(client, mentor.email, "secret")

    patched = replace(test_settings, ollama_base_url="")
    with patch("examai.mentor_workspace_routes.get_settings", lambda: patched):
        page = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
        csrf = extract_csrf(page.text)
        r = client.post(
            f"/tasks/{task_id}/submissions/{intern_id}/publish-review",
            data={
                "csrf_token": csrf,
                "quality_score": "5",
                "readability_score": "4",
                "correctness_score": "3",
                "narrative": "Ship it with notes.",
            },
            follow_redirects=False,
        )
        assert r.status_code == 303

    db = get_session_factory()()
    try:
        pub = db.execute(
            select(PublishedReview).where(PublishedReview.submission_id == sub_id)
        ).scalar_one()
        assert pub.quality_score == 5
        assert pub.readability_score == 4
        assert pub.correctness_score == 3
        assert pub.narrative == "Ship it with notes."
        assert pub.publishing_mentor_user_id == mentor.id
        assert pub.snapshot_commit_sha == "abc123"
    finally:
        db.close()

    page2 = client.get(f"/tasks/{task_id}/submissions/{intern_id}", follow_redirects=False)
    assert page2.status_code == 200
    assert "Review published" in page2.text
    assert "Last published" in page2.text


def _seed_task_assignment_only(
    *,
    mentor_email: str = "mw-mentor-coords@example.com",
    intern_email: str = "mw-intern-coords@example.com",
) -> tuple[User, User, uuid.UUID, uuid.UUID]:
    """Task with intern assignment but no submission row (Story 4.2)."""
    mentor = _seed_user(mentor_email, "secret", "mentor")
    intern = _seed_user(intern_email, "secret", "intern")
    db = get_session_factory()()
    try:
        from examai.models import TaskAssignment

        task = Task(title="Coords task", description="x", due_date=None)
        db.add(task)
        db.commit()
        db.refresh(task)
        db.add(TaskAssignment(task_id=task.id, intern_user_id=intern.id))
        db.commit()
        return mentor, intern, task.id, intern.id
    finally:
        db.close()


def test_mentor_post_coordinates_creates_submission(client: TestClient) -> None:
    """Story 4.2: POST .../coordinates upserts when no row exists (FR19)."""
    trigger_lifespan(client)
    mentor, intern, task_id, intern_id = _seed_task_assignment_only()
    login_with_password(client, mentor.email, "secret")

    page = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
    assert page.status_code == 200
    assert "Repository coordinates" in page.text
    csrf = extract_csrf(page.text)
    r = client.post(
        f"/tasks/{task_id}/submissions/{intern_id}/coordinates",
        data={
            "csrf_token": csrf,
            "repo_identifier": "mentor-org/mentor-repo",
            "commit_sha": "deadbeef",
            "path_scope": "/lib",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303

    db = get_session_factory()()
    try:
        sub = db.execute(
            select(Submission).where(
                Submission.task_id == task_id,
                Submission.intern_user_id == intern_id,
            )
        ).scalar_one()
        assert sub.repo_identifier == "mentor-org/mentor-repo"
        assert sub.commit_sha == "deadbeef"
        assert sub.path_scope == "/lib"
    finally:
        db.close()

    page2 = client.get(f"/tasks/{task_id}/submissions/{intern_id}", follow_redirects=False)
    assert page2.status_code == 200
    assert "Submission coordinates saved" in page2.text
    assert "mentor-org/mentor-repo" in page2.text


def test_mentor_post_coordinates_updates_existing(client: TestClient) -> None:
    trigger_lifespan(client)
    mentor, intern, task_id, intern_id, _sub_id = _seed_task_with_submission(
        mentor_email="mw-mentor-upd@example.com",
        intern_email="mw-intern-upd@example.com",
    )
    login_with_password(client, mentor.email, "secret")
    page = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
    csrf = extract_csrf(page.text)
    r = client.post(
        f"/tasks/{task_id}/submissions/{intern_id}/coordinates",
        data={
            "csrf_token": csrf,
            "repo_identifier": "fixed/org-repo",
            "commit_sha": "",
            "path_scope": "",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303

    db = get_session_factory()()
    try:
        sub = db.execute(
            select(Submission).where(
                Submission.task_id == task_id,
                Submission.intern_user_id == intern_id,
            )
        ).scalar_one()
        assert sub.repo_identifier == "fixed/org-repo"
        assert sub.commit_sha is None
    finally:
        db.close()


def test_mentor_post_coordinates_empty_repo_flash(client: TestClient) -> None:
    trigger_lifespan(client)
    mentor, intern, task_id, intern_id = _seed_task_assignment_only(
        mentor_email="mw-mentor-val@example.com",
        intern_email="mw-intern-val@example.com",
    )
    login_with_password(client, mentor.email, "secret")
    page = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
    csrf = extract_csrf(page.text)
    r = client.post(
        f"/tasks/{task_id}/submissions/{intern_id}/coordinates",
        data={
            "csrf_token": csrf,
            "repo_identifier": "   ",
            "commit_sha": "",
            "path_scope": "",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    page2 = client.get(f"/tasks/{task_id}/submissions/{intern_id}", follow_redirects=False)
    assert page2.status_code == 200
    assert "Repository is required" in page2.text


def test_intern_forbidden_post_coordinates(client: TestClient) -> None:
    """POST /tasks/.../coordinates is mentor or administrator only (FR5)."""
    trigger_lifespan(client)
    _seed_user("mw-intern-postc@example.com", "secret", "intern")
    login_with_password(client, "mw-intern-postc@example.com", "secret")
    tid, iid = uuid.uuid4(), uuid.uuid4()
    assert (
        client.post(
            f"/tasks/{tid}/submissions/{iid}/coordinates",
            data={
                "csrf_token": "x",
                "repo_identifier": "a/b",
            },
        ).status_code
        == 403
    )


def test_intern_forbidden_post_fetch(client: TestClient) -> None:
    """POST /tasks/.../fetch is mentor or administrator only (FR5)."""
    trigger_lifespan(client)
    _seed_user("mw-intern-fetch@example.com", "secret", "intern")
    login_with_password(client, "mw-intern-fetch@example.com", "secret")
    tid, iid = uuid.uuid4(), uuid.uuid4()
    assert (
        client.post(
            f"/tasks/{tid}/submissions/{iid}/fetch",
            data={"csrf_token": "x"},
        ).status_code
        == 403
    )


def test_git_fetch_success_persists_state(client: TestClient, test_settings) -> None:
    """Story 4.3: POST .../fetch updates git_retrieval_* when provider returns content."""
    trigger_lifespan(client)
    mentor, intern, task_id, intern_id, sub_id = _seed_task_with_submission(
        mentor_email="gf-mentor@example.com",
        intern_email="gf-intern@example.com",
    )
    login_with_password(client, mentor.email, "secret")

    patched = replace(
        test_settings,
        git_provider_base_url="https://api.github.com",
        git_provider_token="",
    )

    def _fake_fetch(**_kwargs: object) -> GitFetchResult:
        return GitFetchResult(ok=True, normalized_text="alpha\nbravo")

    with patch("examai.mentor_workspace_routes.get_settings", lambda: patched):
        with patch("examai.mentor_workspace_routes.fetch_repository_contents", _fake_fetch):
            page = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
            csrf = extract_csrf(page.text)
            r = client.post(
                f"/tasks/{task_id}/submissions/{intern_id}/fetch",
                data={"csrf_token": csrf},
                follow_redirects=False,
            )
            assert r.status_code == 303

    db = get_session_factory()()
    try:
        sub = db.execute(select(Submission).where(Submission.id == sub_id)).scalar_one()
        assert sub.git_retrieval_state == "success"
        assert sub.git_retrieved_text and "alpha" in sub.git_retrieved_text
        assert sub.git_fetch_version
        assert sub.git_retrieval_error_code is None
    finally:
        db.close()

    page2 = client.get(f"/tasks/{task_id}/submissions/{intern_id}", follow_redirects=False)
    assert page2.status_code == 200
    assert "Git source retrieved successfully" in page2.text


def test_git_fetch_not_configured_sets_failure(client: TestClient, test_settings) -> None:
    trigger_lifespan(client)
    mentor, intern, task_id, intern_id, sub_id = _seed_task_with_submission(
        mentor_email="gf-mentor-nc@example.com",
        intern_email="gf-intern-nc@example.com",
    )
    login_with_password(client, mentor.email, "secret")

    patched = replace(test_settings, git_provider_base_url="")
    with patch("examai.mentor_workspace_routes.get_settings", lambda: patched):
        page = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
        csrf = extract_csrf(page.text)
        r = client.post(
            f"/tasks/{task_id}/submissions/{intern_id}/fetch",
            data={"csrf_token": csrf},
            follow_redirects=False,
        )
        assert r.status_code == 303

    db = get_session_factory()()
    try:
        sub = db.execute(select(Submission).where(Submission.id == sub_id)).scalar_one()
        assert sub.git_retrieval_state == "failed"
        assert sub.git_retrieval_error_code == "GIT_NOT_CONFIGURED"
    finally:
        db.close()


def test_git_fetch_requires_commit_sha(client: TestClient, test_settings) -> None:
    trigger_lifespan(client)
    mentor, intern, task_id, intern_id, sub_id = _seed_task_with_submission(
        mentor_email="gf-mentor-sha@example.com",
        intern_email="gf-intern-sha@example.com",
    )
    db = get_session_factory()()
    try:
        sub = db.execute(select(Submission).where(Submission.id == sub_id)).scalar_one()
        sub.commit_sha = None
        db.commit()
    finally:
        db.close()

    login_with_password(client, mentor.email, "secret")
    patched = replace(
        test_settings,
        git_provider_base_url="https://api.github.com",
    )
    with patch("examai.mentor_workspace_routes.get_settings", lambda: patched):
        with patch("examai.mentor_workspace_routes.fetch_repository_contents") as mock_fetch:
            page = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
            csrf = extract_csrf(page.text)
            r = client.post(
                f"/tasks/{task_id}/submissions/{intern_id}/fetch",
                data={"csrf_token": csrf},
                follow_redirects=False,
            )
            assert r.status_code == 303
            mock_fetch.assert_not_called()

    db = get_session_factory()()
    try:
        sub = db.execute(select(Submission).where(Submission.id == sub_id)).scalar_one()
        assert sub.git_retrieval_error_code == "COMMIT_SHA_REQUIRED"
    finally:
        db.close()


def test_git_fetch_provider_error_sets_code(client: TestClient, test_settings) -> None:
    trigger_lifespan(client)
    mentor, intern, task_id, intern_id, sub_id = _seed_task_with_submission(
        mentor_email="gf-mentor-err@example.com",
        intern_email="gf-intern-err@example.com",
    )
    login_with_password(client, mentor.email, "secret")

    patched = replace(
        test_settings,
        git_provider_base_url="https://api.github.com",
    )

    def _fail(**_kwargs: object) -> GitFetchResult:
        return GitFetchResult(ok=False, error_code="NOT_FOUND")

    with patch("examai.mentor_workspace_routes.get_settings", lambda: patched):
        with patch("examai.mentor_workspace_routes.fetch_repository_contents", _fail):
            page = client.get(f"/tasks/{task_id}/submissions/{intern_id}")
            csrf = extract_csrf(page.text)
            r = client.post(
                f"/tasks/{task_id}/submissions/{intern_id}/fetch",
                data={"csrf_token": csrf},
                follow_redirects=False,
            )
            assert r.status_code == 303

    db = get_session_factory()()
    try:
        sub = db.execute(select(Submission).where(Submission.id == sub_id)).scalar_one()
        assert sub.git_retrieval_state == "failed"
        assert sub.git_retrieval_error_code == "NOT_FOUND"
        assert sub.git_retrieved_text is None
    finally:
        db.close()

