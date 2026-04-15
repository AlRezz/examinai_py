"""Administrator user management (Story 6.1, docs/api-contracts.md)."""

from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from examai.csrf import get_or_create_csrf, validate_csrf
from examai.database import get_db
from examai.http.security_middleware import SESSION_USER_KEY
from examai.users_repo import (
    create_user_with_roles,
    get_user_by_id,
    list_roles_ordered,
    list_users_with_roles,
    update_user_with_roles,
)

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


@router.get("/admin/users/new", response_class=HTMLResponse)
def admin_user_new_get(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    uid = request.session.get(SESSION_USER_KEY)
    user = get_user_by_id(db, uuid.UUID(str(uid))) if uid else None
    csrf_token = get_or_create_csrf(request.session)
    flash = request.session.pop("_flash", None)
    roles = list_roles_ordered(db)
    return templates.TemplateResponse(
        request,
        "admin/user-form.html",
        {
            "user": user,
            "csrf_token": csrf_token,
            "flash": flash,
            "all_roles": roles,
            "form_action": "/admin/users/new",
            "is_edit": False,
            "edit_user": None,
            "selected_role_names": [],
        },
    )


@router.post("/admin/users/new")
async def admin_user_new_post(request: Request, db: Session = Depends(get_db)) -> RedirectResponse:
    form = await request.form()
    csrf_raw = form.get("csrf_token")
    csrf_token = csrf_raw if isinstance(csrf_raw, str) else None
    if not csrf_token or not validate_csrf(request.session, csrf_token):
        request.session["_flash"] = "Invalid or missing security token. Try again."
        return RedirectResponse(url="/admin/users/new", status_code=303)

    email_raw = form.get("email")
    email = email_raw.strip() if isinstance(email_raw, str) else ""
    password_raw = form.get("password")
    password = password_raw if isinstance(password_raw, str) else ""
    enabled_raw = form.get("enabled")
    enabled = isinstance(enabled_raw, str) and enabled_raw in ("on", "true", "1")

    raw_roles = form.getlist("role_name")
    role_names: list[str] = []
    for item in raw_roles:
        if isinstance(item, str) and item.strip():
            role_names.append(item.strip())

    _user, err = create_user_with_roles(
        db,
        email=email,
        password_plain=password,
        enabled=enabled,
        role_names=role_names,
    )
    if err:
        request.session["_flash"] = err
        return RedirectResponse(url="/admin/users/new", status_code=303)

    request.session["_flash"] = "User created."
    return RedirectResponse(url="/admin/users", status_code=303)


@router.get("/admin/users/{user_id}/edit", response_class=HTMLResponse)
def admin_user_edit_get(
    request: Request, user_id: uuid.UUID, db: Session = Depends(get_db)
) -> HTMLResponse:
    uid = request.session.get(SESSION_USER_KEY)
    user = get_user_by_id(db, uuid.UUID(str(uid))) if uid else None
    target = get_user_by_id(db, user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="User not found.")
    csrf_token = get_or_create_csrf(request.session)
    flash = request.session.pop("_flash", None)
    roles = list_roles_ordered(db)
    selected = sorted({r.name for r in target.roles})
    return templates.TemplateResponse(
        request,
        "admin/user-form.html",
        {
            "user": user,
            "csrf_token": csrf_token,
            "flash": flash,
            "all_roles": roles,
            "form_action": f"/admin/users/{user_id}/edit",
            "is_edit": True,
            "edit_user": target,
            "selected_role_names": selected,
        },
    )


@router.post("/admin/users/{user_id}/edit")
async def admin_user_edit_post(
    request: Request, user_id: uuid.UUID, db: Session = Depends(get_db)
) -> RedirectResponse:
    form = await request.form()
    csrf_raw = form.get("csrf_token")
    csrf_token = csrf_raw if isinstance(csrf_raw, str) else None
    if not csrf_token or not validate_csrf(request.session, csrf_token):
        request.session["_flash"] = "Invalid or missing security token. Try again."
        return RedirectResponse(url=f"/admin/users/{user_id}/edit", status_code=303)

    actor_raw = request.session.get(SESSION_USER_KEY)
    actor_id = uuid.UUID(str(actor_raw)) if actor_raw else None

    email_raw = form.get("email")
    email = email_raw.strip() if isinstance(email_raw, str) else ""
    password_raw = form.get("password")
    password = password_raw if isinstance(password_raw, str) else None
    enabled_raw = form.get("enabled")
    enabled = isinstance(enabled_raw, str) and enabled_raw in ("on", "true", "1")

    raw_roles = form.getlist("role_name")
    role_names: list[str] = []
    for item in raw_roles:
        if isinstance(item, str) and item.strip():
            role_names.append(item.strip())

    _user, err = update_user_with_roles(
        db,
        user_id=user_id,
        actor_user_id=actor_id,
        email=email,
        password_plain=password,
        enabled=enabled,
        role_names=role_names,
    )
    if err:
        request.session["_flash"] = err
        return RedirectResponse(url=f"/admin/users/{user_id}/edit", status_code=303)

    request.session["_flash"] = "User updated."
    return RedirectResponse(url="/admin/users", status_code=303)
