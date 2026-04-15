"""Session auth + RBAC for HTML routes (stories 1.3–1.4)."""

from __future__ import annotations

import uuid
from typing import Callable

from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response

from examai.config import Settings
from examai.database import get_session_factory
from examai.rbac import required_roles_for_path, roles_allow_path
from examai.users_repo import role_names_for_user

SESSION_USER_KEY = "uid"


def is_public_route(path: str, method: str) -> bool:
    if path in ("/", "/error"):
        return True
    if path == "/login":
        return True
    if path.startswith("/css/") or path.startswith("/js/") or path.startswith("/webjars/"):
        return True
    if path.startswith("/actuator/health"):
        return True
    if path == "/favicon.ico":
        return True
    return False


def _load_roles(uid: str) -> frozenset[str]:
    db = get_session_factory()()
    try:
        return role_names_for_user(db, uuid.UUID(uid))
    finally:
        db.close()


class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable, settings: Settings) -> None:
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        method = request.method

        if is_public_route(path, method):
            return await call_next(request)

        uid = request.session.get(SESSION_USER_KEY)
        if not uid or not isinstance(uid, str):
            if method in ("GET", "HEAD"):
                return RedirectResponse(url="/login", status_code=303)
            return Response("Authentication required", status_code=401)

        required = required_roles_for_path(path)
        if required is not None:
            roles = await run_in_threadpool(_load_roles, uid)
            if not roles_allow_path(path, roles):
                body = (
                    "<!DOCTYPE html><html><head><title>Forbidden</title></head>"
                    '<body><h1>Forbidden</h1><p>You do not have access to this area.</p>'
                    '<p><a href="/home">Home</a></p></body></html>'
                )
                return HTMLResponse(body, status_code=403)

        return await call_next(request)
