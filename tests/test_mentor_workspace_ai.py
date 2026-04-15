"""Epic 5: mentor workspace, AI draft audit, degraded LLM messaging."""

from __future__ import annotations

import uuid
from dataclasses import replace
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import select

from examai.bootstrap import ensure_roles
from examai.database import get_session_factory
from examai.models import AiDraft, ModelInvocation, Submission, Task, User
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

