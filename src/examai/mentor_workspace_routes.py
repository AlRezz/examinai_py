"""Mentor submission workspace, AI draft audit, degraded LLM UX (Epic 5)."""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from examai.config import get_settings
from examai.csrf import get_or_create_csrf, validate_csrf
from examai.database import get_db
from examai.http.security_middleware import SESSION_USER_KEY
from examai.integration.ai import OllamaClientError, ollama_generate
from examai.models import AiDraft, ModelInvocation, Task
from examai.mentor_workspace_repo import (
    get_latest_ai_draft,
    get_mentor_review_draft,
    get_published_review,
    get_submission_for_pair,
    intern_assigned_to_task,
    list_intern_submissions_for_task,
    upsert_mentor_review_draft,
    upsert_published_review,
)
from examai.tasks_repo import get_task_by_id
from examai.users_repo import get_user_by_id

_ROOT = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(_ROOT / "templates"))

router = APIRouter()


def _current_user(request: Request, db: Session):
    uid = request.session.get(SESSION_USER_KEY)
    if not uid or not isinstance(uid, str):
        raise HTTPException(status_code=401)
    return get_user_by_id(db, uuid.UUID(uid))


def _build_ai_prompt(task: Task, submission) -> str:
    desc = (task.description or "").strip()
    if len(desc) > 8000:
        desc = desc[:8000] + "\n…"
    parts = [
        "You are assisting a mentor with a concise draft assessment of an intern's submission.",
        "",
        f"Task title: {task.title}",
    ]
    if desc:
        parts.extend(["", "Task description:", desc])
    parts.extend(
        [
            "",
            f"Repository identifier: {submission.repo_identifier}",
            f"Commit SHA: {submission.commit_sha or '(not set)'}",
            f"Path scope: {submission.path_scope or '(not set)'}",
            f"Submission status: {submission.status}",
            "",
            "Provide a short, professional assessment draft. Do not request or assume access to secrets, tokens, or environment variables.",
        ]
    )
    return "\n".join(parts)


def _prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _parse_score(raw: str) -> Optional[int]:
    s = raw.strip()
    if not s:
        return None
    try:
        v = int(s)
    except ValueError:
        return None
    if 1 <= v <= 5:
        return v
    return None


def _redirect_workspace(task_id: uuid.UUID, intern_id: uuid.UUID) -> str:
    return f"/tasks/{task_id}/submissions/{intern_id}"


@router.get("/tasks/{task_id}/submissions", response_class=HTMLResponse)
def submissions_list(
    request: Request,
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    user = _current_user(request, db)
    task = get_task_by_id(db, task_id)
    if task is None:
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "That task was not found."},
            status_code=404,
        )
    csrf_token = get_or_create_csrf(request.session)
    flash = request.session.pop("_flash", None)
    rows = list_intern_submissions_for_task(db, task_id)
    return templates.TemplateResponse(
        request,
        "tasks/submissions.html",
        {
            "user": user,
            "csrf_token": csrf_token,
            "flash": flash,
            "task": task,
            "rows": rows,
        },
    )


@router.get("/tasks/{task_id}/submissions/{intern_id}", response_class=HTMLResponse)
def submission_workspace(
    request: Request,
    task_id: uuid.UUID,
    intern_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    user = _current_user(request, db)
    task = get_task_by_id(db, task_id)
    if task is None:
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "That task was not found."},
            status_code=404,
        )
    if not intern_assigned_to_task(db, task_id, intern_id):
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "That intern is not assigned to this task."},
            status_code=404,
        )
    intern = get_user_by_id(db, intern_id)
    if intern is None:
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "User not found."},
            status_code=404,
        )

    settings = get_settings()
    submission = get_submission_for_pair(db, task_id, intern_id)
    ai_pair = get_latest_ai_draft(db, submission.id) if submission else None
    mentor_draft = get_mentor_review_draft(db, submission.id) if submission else None
    published = get_published_review(db, submission.id) if submission else None

    csrf_token = get_or_create_csrf(request.session)
    flash = request.session.pop("_flash", None)

    ollama_configured = bool(settings.ollama_base_url)
    flash_lower = (flash or "").lower()
    degraded_inference = (not ollama_configured) or (
        flash is not None
        and (
            "could not" in flash_lower
            or "not configured" in flash_lower
            or ("unavailable" in flash_lower and "was generated" not in flash_lower)
        )
    )

    return templates.TemplateResponse(
        request,
        "tasks/submission-detail.html",
        {
            "user": user,
            "csrf_token": csrf_token,
            "flash": flash,
            "task": task,
            "intern": intern,
            "submission": submission,
            "ai_invocation": ai_pair[0] if ai_pair else None,
            "ai_draft": ai_pair[1] if ai_pair else None,
            "mentor_draft": mentor_draft,
            "published": published,
            "ollama_configured": ollama_configured,
            "degraded_inference": degraded_inference,
        },
    )


@router.post("/tasks/{task_id}/submissions/{intern_id}/ai-draft-assessment")
def post_ai_draft_assessment(
    request: Request,
    task_id: uuid.UUID,
    intern_id: uuid.UUID,
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
) -> RedirectResponse:
    if not validate_csrf(request.session, csrf_token):
        request.session["_flash"] = "Invalid or missing security token. Try again."
        return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)
    task = get_task_by_id(db, task_id)
    if task is None:
        request.session["_flash"] = "That task was not found."
        return RedirectResponse(url="/tasks", status_code=303)
    if not intern_assigned_to_task(db, task_id, intern_id):
        request.session["_flash"] = "That intern is not assigned to this task."
        return RedirectResponse(url=f"/tasks/{task_id}/submissions", status_code=303)
    submission = get_submission_for_pair(db, task_id, intern_id)
    if submission is None:
        request.session["_flash"] = (
            "No submission record exists yet for this intern. The intern must submit coordinates first."
        )
        return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)

    settings = get_settings()
    if not settings.ollama_base_url:
        request.session["_flash"] = (
            "AI draft is unavailable: Ollama is not configured (set OLLAMA_BASE_URL). "
            "You can still save a manual review and publish below."
        )
        return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)

    prompt = _build_ai_prompt(task, submission)
    phash = _prompt_hash(prompt)
    try:
        result = ollama_generate(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            prompt=prompt,
            timeout_seconds=settings.ollama_timeout_seconds,
            max_retries=settings.ollama_max_retries,
        )
    except OllamaClientError as e:
        request.session["_flash"] = (
            f"AI draft could not be generated: {e}. "
            "You can still save a manual review and publish without waiting for AI."
        )
        return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)

    inv = ModelInvocation(
        submission_id=submission.id,
        model_name=result.model_name,
        model_version=result.model_version,
        prompt_hash=phash,
    )
    db.add(inv)
    db.flush()
    db.add(
        AiDraft(
            model_invocation_id=inv.id,
            assessment_text=result.text,
        )
    )
    db.commit()
    request.session["_flash"] = "AI draft assessment was generated and recorded."
    return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)


@router.post("/tasks/{task_id}/submissions/{intern_id}/review-draft")
def post_review_draft(
    request: Request,
    task_id: uuid.UUID,
    intern_id: uuid.UUID,
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
    quality_score: str = Form(""),
    readability_score: str = Form(""),
    correctness_score: str = Form(""),
    narrative_feedback: str = Form(""),
) -> RedirectResponse:
    user = _current_user(request, db)
    if not validate_csrf(request.session, csrf_token):
        request.session["_flash"] = "Invalid or missing security token. Try again."
        return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)
    submission = get_submission_for_pair(db, task_id, intern_id)
    if submission is None or not intern_assigned_to_task(db, task_id, intern_id):
        request.session["_flash"] = "Submission not found for this workspace."
        return RedirectResponse(url=f"/tasks/{task_id}/submissions", status_code=303)
    q = _parse_score(quality_score)
    r = _parse_score(readability_score)
    c = _parse_score(correctness_score)
    narrative = narrative_feedback.strip() or None
    upsert_mentor_review_draft(
        db,
        submission_id=submission.id,
        mentor_user_id=user.id,
        quality_score=q,
        readability_score=r,
        correctness_score=c,
        narrative_feedback=narrative,
    )
    request.session["_flash"] = "Mentor review draft saved."
    return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)


@router.post("/tasks/{task_id}/submissions/{intern_id}/publish-review")
def post_publish_review(
    request: Request,
    task_id: uuid.UUID,
    intern_id: uuid.UUID,
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
    quality_score: str = Form(""),
    readability_score: str = Form(""),
    correctness_score: str = Form(""),
    narrative: str = Form(""),
) -> RedirectResponse:
    user = _current_user(request, db)
    if not validate_csrf(request.session, csrf_token):
        request.session["_flash"] = "Invalid or missing security token. Try again."
        return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)
    submission = get_submission_for_pair(db, task_id, intern_id)
    if submission is None or not intern_assigned_to_task(db, task_id, intern_id):
        request.session["_flash"] = "Submission not found for this workspace."
        return RedirectResponse(url=f"/tasks/{task_id}/submissions", status_code=303)

    draft = get_mentor_review_draft(db, submission.id)
    q = _parse_score(quality_score)
    r = _parse_score(readability_score)
    c = _parse_score(correctness_score)
    narrative_clean = narrative.strip() or None

    q = q if q is not None else (draft.quality_score if draft else None)
    r = r if r is not None else (draft.readability_score if draft else None)
    c = c if c is not None else (draft.correctness_score if draft else None)
    narrative_clean = narrative_clean or (draft.narrative_feedback if draft else None)

    if narrative_clean is None and q is None and r is None and c is None:
        request.session["_flash"] = "Add mentor feedback (narrative and/or scores) before publishing."
        return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)

    upsert_published_review(
        db,
        submission=submission,
        mentor_user_id=user.id,
        quality_score=q,
        readability_score=r,
        correctness_score=c,
        narrative=narrative_clean,
    )
    request.session["_flash"] = "Review published."
    return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)
