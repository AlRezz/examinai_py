"""Mentor submission workspace: coordinates (Epic 4), AI draft audit, degraded LLM UX (Epic 5)."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from examai.ai_assessment_parsing import parse_ai_assessment_output
from examai.config import get_settings
from examai.csrf import get_or_create_csrf, validate_csrf
from examai.database import get_db
from examai.http.security_middleware import SESSION_USER_KEY
from examai.integration.ai import OllamaClientError, ollama_generate
from examai.integration.git_provider import fetch_repository_contents, parse_repo_identifier
from examai.intern_tasks_repo import upsert_intern_submission_coordinates
from examai.models import AiDraft, ModelInvocation, Task
from examai.mentor_workspace_repo import (
    get_latest_ai_draft,
    get_mentor_review_draft,
    get_published_review,
    get_submission_for_pair,
    intern_assigned_to_task,
    list_intern_submissions_for_task,
    list_outstanding_review_queue,
    upsert_mentor_review_draft,
    upsert_published_review,
)
from examai.submission_lifecycle import mentor_submission_lifecycle_badge
from examai.tasks_repo import get_task_by_id
from examai.users_repo import get_user_by_id

_ROOT = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(_ROOT / "templates"))

router = APIRouter()

_AI_RETRIEVED_CODE_MAX_CHARS = 12000


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
        "You are assisting a mentor with a draft assessment of an intern's submission.",
        "Base your scores (1–5) and written feedback on the retrieved source code when it is present; otherwise use the task and coordinate context only.",
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
        ]
    )
    raw_code = (getattr(submission, "git_retrieved_text", None) or "").strip()
    if raw_code:
        if len(raw_code) > _AI_RETRIEVED_CODE_MAX_CHARS:
            raw_code = raw_code[:_AI_RETRIEVED_CODE_MAX_CHARS] + "\n…"
        parts.extend(
            [
                "",
                "Retrieved source (for review; may be truncated):",
                "```",
                raw_code,
                "```",
            ]
        )
    else:
        parts.extend(
            [
                "",
                "Retrieved source: (none yet — run Git fetch in the workspace when configured so code can inform scores.)",
            ]
        )
    parts.extend(
        [
            "",
            "Respond using EXACTLY this structure. First three lines must be scores (integers 1–5):",
            "",
            "Quality: <1-5>",
            "Readability: <1-5>",
            "Correctness: <1-5>",
            "",
            "### Feedback on the code",
            "<your feedback>",
            "",
            "### Suggestions to improve",
            "<your suggestions>",
            "",
            "Do not request or assume access to secrets, tokens, or environment variables.",
        ]
    )
    return "\n".join(parts)


def _prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


_AI_FLASH_DETAIL_MAX = 320
_GIT_FLASH_DETAIL_MAX = 320


def _shorten_for_flash(msg: str, *, max_len: int = _AI_FLASH_DETAIL_MAX) -> str:
    s = msg.strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


def _git_fetch_version_token(normalized_text: str) -> str:
    digest = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{digest}"


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


@router.get("/review/queue", response_class=HTMLResponse)
def review_queue(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    """GET /review/queue — FR24, UX-DR1 (`review/queue.html`)."""
    user = _current_user(request, db)
    csrf_token = get_or_create_csrf(request.session)
    flash = request.session.pop("_flash", None)
    rows = list_outstanding_review_queue(db)
    return templates.TemplateResponse(
        request,
        "review/queue.html",
        {
            "user": user,
            "csrf_token": csrf_token,
            "flash": flash,
            "rows": rows,
        },
    )


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

    submission_lifecycle = mentor_submission_lifecycle_badge(
        submission=submission,
        has_published=published is not None,
        has_mentor_draft=mentor_draft is not None,
    )

    csrf_token = get_or_create_csrf(request.session)
    flash = request.session.pop("_flash", None)

    ollama_configured = bool(settings.ollama_base_url)
    git_provider_configured = bool(settings.git_provider_base_url)
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
            "git_provider_configured": git_provider_configured,
            "degraded_inference": degraded_inference,
            "submission_lifecycle": submission_lifecycle,
        },
    )


@router.post("/tasks/{task_id}/submissions/{intern_id}/coordinates")
def post_submission_coordinates(
    request: Request,
    task_id: uuid.UUID,
    intern_id: uuid.UUID,
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
    repo_identifier: str = Form(""),
    commit_sha: str = Form(""),
    path_scope: str = Form(""),
) -> RedirectResponse:
    """POST /tasks/{taskId}/submissions/{internId}/coordinates — FR19, docs/api-contracts.md."""
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

    repo = repo_identifier.strip()
    if not repo:
        request.session["_flash"] = "Repository is required."
        return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)
    if len(repo) > 500:
        request.session["_flash"] = "Repository must be at most 500 characters."
        return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)

    csha = commit_sha.strip() or None
    if csha is not None and len(csha) > 64:
        request.session["_flash"] = "Commit SHA must be at most 64 characters."
        return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)

    pscope = path_scope.strip() or None
    if pscope is not None and len(pscope) > 2000:
        request.session["_flash"] = "Path scope must be at most 2000 characters."
        return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)

    upsert_intern_submission_coordinates(db, task_id, intern_id, repo, csha, pscope)
    request.session["_flash"] = "Submission coordinates saved."
    return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)


@router.post("/tasks/{task_id}/submissions/{intern_id}/fetch")
def post_submission_fetch(
    request: Request,
    task_id: uuid.UUID,
    intern_id: uuid.UUID,
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
) -> RedirectResponse:
    """POST /tasks/{taskId}/submissions/{internId}/fetch — FR20, FR29, FR31."""
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
        request.session["_flash"] = "No submission record exists yet. Save coordinates first."
        return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)

    settings = get_settings()
    now = datetime.now(timezone.utc)

    def _persist_failure(code: str, flash: str) -> RedirectResponse:
        submission.git_retrieval_state = "failed"
        submission.git_retrieval_error_code = code
        submission.git_retrieved_text = None
        submission.git_retrieved_source = None
        submission.git_last_attempt_at = now
        submission.updated_at = now
        db.commit()
        request.session["_flash"] = flash
        return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)

    if not settings.git_provider_base_url:
        return _persist_failure(
            "GIT_NOT_CONFIGURED",
            "Git fetch unavailable: set GIT_PROVIDER_BASE_URL (and optional GIT_PROVIDER_TOKEN).",
        )

    csha = (submission.commit_sha or "").strip()
    if not csha:
        return _persist_failure(
            "COMMIT_SHA_REQUIRED",
            "Git fetch needs a commit SHA. Enter one under repository coordinates, save, then fetch again.",
        )

    try:
        owner, repo = parse_repo_identifier(submission.repo_identifier)
    except ValueError as e:
        detail = _shorten_for_flash(str(e), max_len=_GIT_FLASH_DETAIL_MAX)
        return _persist_failure("INVALID_REPO", f"Git fetch failed: {detail}")

    submission.git_retrieval_state = "fetching"
    submission.git_retrieval_error_code = None
    submission.git_last_attempt_at = now
    submission.updated_at = now
    db.commit()

    result = fetch_repository_contents(
        api_base=settings.git_provider_base_url,
        token=settings.git_provider_token,
        owner=owner,
        repo=repo,
        ref=csha,
        path_scope=submission.path_scope,
        timeout_seconds=settings.git_provider_timeout_seconds,
    )

    now2 = datetime.now(timezone.utc)
    submission = get_submission_for_pair(db, task_id, intern_id)
    if submission is None:
        request.session["_flash"] = "Submission disappeared during Git fetch. Try again."
        return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)

    submission.updated_at = now2
    submission.git_last_attempt_at = now2

    if result.ok and result.normalized_text is not None:
        submission.git_retrieval_state = "success"
        submission.git_retrieval_error_code = None
        submission.git_retrieved_text = result.normalized_text
        submission.git_retrieved_source = result.source_kind
        submission.git_last_success_at = now2
        submission.git_fetch_version = _git_fetch_version_token(result.normalized_text)
        db.commit()
        request.session["_flash"] = "Git source retrieved successfully."
        return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)

    code = result.error_code or "UNKNOWN"
    submission.git_retrieval_state = "failed"
    submission.git_retrieval_error_code = code
    submission.git_retrieved_text = None
    submission.git_retrieved_source = None
    db.commit()
    request.session["_flash"] = (
        f"Git fetch failed ({code}). "
        "Check coordinates, token, and provider access — you can adjust coordinates and retry."
    )
    return RedirectResponse(url=_redirect_workspace(task_id, intern_id), status_code=303)


@router.post("/tasks/{task_id}/submissions/{intern_id}/ai-draft-assessment")
def post_ai_draft_assessment(
    request: Request,
    task_id: uuid.UUID,
    intern_id: uuid.UUID,
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
) -> RedirectResponse:
    user = _current_user(request, db)
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
        detail = _shorten_for_flash(str(e))
        request.session["_flash"] = (
            f"AI draft could not be generated: {detail}. "
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
    db.flush()
    parsed = parse_ai_assessment_output(result.text)
    upsert_mentor_review_draft(
        db,
        submission_id=submission.id,
        mentor_user_id=user.id,
        quality_score=parsed.quality_score,
        readability_score=parsed.readability_score,
        correctness_score=parsed.correctness_score,
        narrative_feedback=parsed.narrative_feedback,
    )
    request.session["_flash"] = (
        "AI draft assessment was generated and recorded; mentor review draft was updated from the model output."
    )
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

    draft = get_mentor_review_draft(db, submission.id)
    q = _parse_score(quality_score)
    r = _parse_score(readability_score)
    c = _parse_score(correctness_score)
    narrative_clean = narrative.strip() or narrative_feedback.strip() or None

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
