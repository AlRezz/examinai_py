"""Intern task list and detail (Story 3.1, docs/api-contracts.md)."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from examai.csrf import get_or_create_csrf, validate_csrf
from examai.database import get_db
from examai.http.security_middleware import SESSION_USER_KEY
from examai.intern_tasks_repo import (
    get_published_feedback_for_intern_submission,
    get_submission_for_intern_pair,
    get_task_for_intern_if_assigned,
    list_assigned_tasks_for_intern,
    upsert_intern_submission_coordinates,
)
from examai.submission_lifecycle import intern_submission_lifecycle_badge
from examai.users_repo import get_user_by_id

_ROOT = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(_ROOT / "templates"))

router = APIRouter()


def _current_user(request: Request, db: Session):
    uid = request.session.get(SESSION_USER_KEY)
    if not uid or not isinstance(uid, str):
        raise HTTPException(status_code=401)
    return get_user_by_id(db, uuid.UUID(uid))


@router.get("/intern/tasks", response_class=HTMLResponse)
def intern_task_list(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    user = _current_user(request, db)
    csrf_token = get_or_create_csrf(request.session)
    flash = request.session.pop("_flash", None)
    tasks = list_assigned_tasks_for_intern(db, user.id)
    return templates.TemplateResponse(
        request,
        "intern/tasks/list.html",
        {
            "user": user,
            "csrf_token": csrf_token,
            "tasks": tasks,
            "flash": flash,
        },
    )


@router.get("/intern/tasks/{task_id}", response_class=HTMLResponse)
def intern_task_detail(
    request: Request,
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    user = _current_user(request, db)
    csrf_token = get_or_create_csrf(request.session)
    flash = request.session.pop("_flash", None)
    task = get_task_for_intern_if_assigned(db, user.id, task_id)
    # Product policy: respond with 404 for missing tasks and for tasks the intern is not
    # assigned to, so callers cannot distinguish "does not exist" from "not yours".
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    submission = get_submission_for_intern_pair(db, user.id, task_id)
    published_feedback = None
    if submission is not None:
        published_feedback = get_published_feedback_for_intern_submission(db, user.id, submission.id)
    submission_lifecycle = intern_submission_lifecycle_badge(
        submission=submission,
        has_published_feedback=published_feedback is not None,
    )
    return templates.TemplateResponse(
        request,
        "intern/tasks/detail.html",
        {
            "user": user,
            "csrf_token": csrf_token,
            "task": task,
            "submission": submission,
            "published_feedback": published_feedback,
            "submission_lifecycle": submission_lifecycle,
            "flash": flash,
        },
    )


@router.get("/intern/submissions/{submission_id}/feedback", response_class=HTMLResponse)
def intern_submission_feedback(
    request: Request,
    submission_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """GET /intern/submissions/{submissionId}/feedback — published outcome for own submission (FR10)."""
    user = _current_user(request, db)
    csrf_token = get_or_create_csrf(request.session)
    flash = request.session.pop("_flash", None)
    published = get_published_feedback_for_intern_submission(db, user.id, submission_id)
    if published is None:
        raise HTTPException(status_code=404, detail="Feedback not found.")
    task = get_task_for_intern_if_assigned(db, user.id, published.submission.task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Feedback not found.")
    submission_lifecycle = intern_submission_lifecycle_badge(
        submission=published.submission,
        has_published_feedback=True,
    )
    return templates.TemplateResponse(
        request,
        "intern/submissions/feedback.html",
        {
            "user": user,
            "csrf_token": csrf_token,
            "task": task,
            "published": published,
            "submission_lifecycle": submission_lifecycle,
            "flash": flash,
        },
    )


@router.post("/intern/tasks/{task_id}/submission")
def intern_post_submission(
    request: Request,
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
    repo_identifier: str = Form(""),
    commit_sha: str = Form(""),
    path_scope: str = Form(""),
) -> RedirectResponse:
    """Submit or update version-control coordinates (POST /intern/tasks/{taskId}/submission, FR9)."""
    user = _current_user(request, db)
    if not validate_csrf(request.session, csrf_token):
        request.session["_flash"] = "Invalid or missing security token. Try again."
        return RedirectResponse(url=f"/intern/tasks/{task_id}", status_code=303)
    task = get_task_for_intern_if_assigned(db, user.id, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    repo = repo_identifier.strip()
    if not repo:
        request.session["_flash"] = "Repository is required."
        return RedirectResponse(url=f"/intern/tasks/{task_id}", status_code=303)
    if len(repo) > 500:
        request.session["_flash"] = "Repository must be at most 500 characters."
        return RedirectResponse(url=f"/intern/tasks/{task_id}", status_code=303)

    csha = commit_sha.strip() or None
    if csha is not None and len(csha) > 64:
        request.session["_flash"] = "Commit SHA must be at most 64 characters."
        return RedirectResponse(url=f"/intern/tasks/{task_id}", status_code=303)

    pscope = path_scope.strip() or None
    if pscope is not None and len(pscope) > 2000:
        request.session["_flash"] = "Path scope must be at most 2000 characters."
        return RedirectResponse(url=f"/intern/tasks/{task_id}", status_code=303)

    upsert_intern_submission_coordinates(db, task_id, user.id, repo, csha, pscope)
    request.session["_flash"] = "Your submission coordinates were saved."
    return RedirectResponse(url=f"/intern/tasks/{task_id}", status_code=303)
