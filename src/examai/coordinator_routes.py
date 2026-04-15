"""Coordinator index and case record (Story 7.1, docs/api-contracts.md)."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from examai.coordinator_repo import get_case_record, list_submission_summaries
from examai.csrf import get_or_create_csrf
from examai.database import get_db
from examai.http.security_middleware import SESSION_USER_KEY
from examai.users_repo import get_user_by_id

_ROOT = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(_ROOT / "templates"))

router = APIRouter()


@router.get("/coordinator", response_class=HTMLResponse)
def coordinator_index(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    uid = request.session.get(SESSION_USER_KEY)
    user = get_user_by_id(db, uuid.UUID(str(uid))) if uid else None
    csrf_token = get_or_create_csrf(request.session)
    flash = request.session.pop("_flash", None)
    rows = list_submission_summaries(db)
    return templates.TemplateResponse(
        request,
        "coordinator/index.html",
        {
            "user": user,
            "csrf_token": csrf_token,
            "flash": flash,
            "submissions": rows,
        },
    )


@router.get("/coordinator/cases/{submission_id}", response_class=HTMLResponse)
def coordinator_case_record(
    request: Request,
    submission_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    uid = request.session.get(SESSION_USER_KEY)
    user = get_user_by_id(db, uuid.UUID(str(uid))) if uid else None
    csrf_token = get_or_create_csrf(request.session)
    case = get_case_record(db, submission_id)
    if case is None:
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": "That case was not found."},
            status_code=404,
        )
    return templates.TemplateResponse(
        request,
        "coordinator/case-record.html",
        {
            "user": user,
            "csrf_token": csrf_token,
            "submission": case.submission,
            "task": case.task,
            "intern": case.intern,
        },
    )
