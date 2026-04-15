"""Mentor/admin task list and CRUD (Story 2.1, docs/api-contracts.md)."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Tuple

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from examai.csrf import get_or_create_csrf, validate_csrf
from examai.database import get_db
from examai.http.security_middleware import SESSION_USER_KEY
from examai.tasks_repo import create_task, get_task_by_id, list_tasks, update_task
from examai.users_repo import get_user_by_id

_ROOT = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(_ROOT / "templates"))

router = APIRouter()


def _parse_optional_date(raw: Optional[str]) -> Tuple[Optional[date], Optional[str]]:
    """Return (date or None, error message or None)."""
    if raw is None:
        return None, None
    s = raw.strip()
    if not s:
        return None, None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date(), None
    except ValueError:
        return None, "Due date must be YYYY-MM-DD."


def _current_user(request: Request, db: Session):
    uid = request.session.get(SESSION_USER_KEY)
    assert uid
    return get_user_by_id(db, uuid.UUID(str(uid)))


@router.get("/tasks", response_class=HTMLResponse)
def task_list(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    user = _current_user(request, db)
    csrf_token = get_or_create_csrf(request.session)
    flash = request.session.pop("_flash", None)
    tasks = list_tasks(db)
    return templates.TemplateResponse(
        request,
        "tasks/list.html",
        {
            "user": user,
            "csrf_token": csrf_token,
            "tasks": tasks,
            "flash": flash,
        },
    )


@router.get("/tasks/new", response_class=HTMLResponse)
def task_new_get(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    user = _current_user(request, db)
    csrf_token = get_or_create_csrf(request.session)
    flash = request.session.pop("_flash", None)
    return templates.TemplateResponse(
        request,
        "tasks/form.html",
        {
            "user": user,
            "csrf_token": csrf_token,
            "flash": flash,
            "heading": "New task",
            "form_action": "/tasks/new",
            "task": None,
            "title_value": "",
            "description_value": "",
            "due_date_value": "",
        },
    )


@router.post("/tasks/new")
def task_new_post(
    request: Request,
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
    title: str = Form(""),
    description: str = Form(""),
    due_date: str = Form(""),
) -> RedirectResponse:
    if not validate_csrf(request.session, csrf_token):
        request.session["_flash"] = "Invalid or missing security token. Try again."
        return RedirectResponse(url="/tasks/new", status_code=303)
    title_clean = title.strip()
    if not title_clean:
        request.session["_flash"] = "Title is required."
        return RedirectResponse(url="/tasks/new", status_code=303)
    due_parsed, err = _parse_optional_date(due_date)
    if err:
        request.session["_flash"] = err
        return RedirectResponse(url="/tasks/new", status_code=303)
    desc_clean = description.strip() or None
    create_task(db, title=title_clean, description=desc_clean, due_date=due_parsed)
    request.session["_flash"] = "Task created."
    return RedirectResponse(url="/tasks", status_code=303)


@router.get("/tasks/{task_id}/edit", response_class=HTMLResponse)
def task_edit_get(
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
    due_str = task.due_date.isoformat() if task.due_date else ""
    return templates.TemplateResponse(
        request,
        "tasks/form.html",
        {
            "user": user,
            "csrf_token": csrf_token,
            "flash": flash,
            "heading": "Edit task",
            "form_action": f"/tasks/{task.id}/edit",
            "task": task,
            "title_value": task.title,
            "description_value": task.description or "",
            "due_date_value": due_str,
        },
    )


@router.post("/tasks/{task_id}/edit")
def task_edit_post(
    request: Request,
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
    title: str = Form(""),
    description: str = Form(""),
    due_date: str = Form(""),
) -> RedirectResponse:
    if not validate_csrf(request.session, csrf_token):
        request.session["_flash"] = "Invalid or missing security token. Try again."
        return RedirectResponse(url=f"/tasks/{task_id}/edit", status_code=303)
    task = get_task_by_id(db, task_id)
    if task is None:
        request.session["_flash"] = "That task was not found."
        return RedirectResponse(url="/tasks", status_code=303)
    title_clean = title.strip()
    if not title_clean:
        request.session["_flash"] = "Title is required."
        return RedirectResponse(url=f"/tasks/{task_id}/edit", status_code=303)
    due_parsed, err = _parse_optional_date(due_date)
    if err:
        request.session["_flash"] = err
        return RedirectResponse(url=f"/tasks/{task_id}/edit", status_code=303)
    desc_clean = description.strip() or None
    update_task(db, task, title=title_clean, description=desc_clean, due_date=due_parsed)
    request.session["_flash"] = "Task updated."
    return RedirectResponse(url="/tasks", status_code=303)
