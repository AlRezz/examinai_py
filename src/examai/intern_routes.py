"""Intern task list and detail (Story 3.1, docs/api-contracts.md)."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from examai.csrf import get_or_create_csrf
from examai.database import get_db
from examai.http.security_middleware import SESSION_USER_KEY
from examai.intern_tasks_repo import get_task_for_intern_if_assigned, list_assigned_tasks_for_intern
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
    return templates.TemplateResponse(
        request,
        "intern/tasks/detail.html",
        {
            "user": user,
            "csrf_token": csrf_token,
            "task": task,
            "flash": flash,
        },
    )
