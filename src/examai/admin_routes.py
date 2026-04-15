"""Administrator user management (Story 6.1, docs/api-contracts.md)."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from examai.csrf import get_or_create_csrf
from examai.database import get_db
from examai.http.security_middleware import SESSION_USER_KEY
from examai.users_repo import get_user_by_id, list_users_with_roles

_ROOT = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(_ROOT / "templates"))

router = APIRouter()


@router.get("/admin/users", response_class=HTMLResponse)
def admin_user_list(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    uid = request.session.get(SESSION_USER_KEY)
    user = get_user_by_id(db, uuid.UUID(str(uid))) if uid else None
    csrf_token = get_or_create_csrf(request.session)
    flash = request.session.pop("_flash", None)
    users = list_users_with_roles(db)
    return templates.TemplateResponse(
        request,
        "admin/users/list.html",
        {
            "user": user,
            "csrf_token": csrf_token,
            "flash": flash,
            "users": users,
        },
    )
