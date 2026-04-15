"""Application entry: FastAPI app factory, public shell, auth, RBAC, and health route."""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates

from examai.bootstrap import ensure_roles, maybe_seed_demo_user
from examai.config import Settings, get_settings
from examai.csrf import get_or_create_csrf, validate_csrf
from examai.database import create_schema, get_db, get_session_factory, configure_engine
from examai.http.security_middleware import SESSION_USER_KEY, SecurityMiddleware
from examai.security import verify_password
from examai.admin_routes import router as admin_router
from examai.coordinator_routes import router as coordinator_router
from examai.intern_routes import router as intern_router
from examai.mentor_workspace_routes import router as mentor_workspace_router
from examai.tasks_routes import router as tasks_router
from examai.users_repo import get_user_by_email, get_user_by_id


def _package_dir() -> Path:
    return Path(__file__).resolve().parent


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    settings = settings or get_settings()
    configure_engine(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        create_schema()
        db = get_session_factory()()
        try:
            ensure_roles(db)
            maybe_seed_demo_user(db, settings)
        finally:
            db.close()
        yield

    app = FastAPI(
        title="Examinai",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
    )
    app.include_router(tasks_router)
    app.include_router(intern_router)
    app.include_router(mentor_workspace_router)
    app.include_router(coordinator_router)
    app.include_router(admin_router)

    root = _package_dir()
    static_root = root / "static"
    templates = Jinja2Templates(directory=str(root / "templates"))

    _HEALTH_BODY: Dict[str, str] = {"status": "UP"}

    app.add_middleware(SecurityMiddleware, settings=settings)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie=settings.session_cookie_name,
        max_age=settings.session_max_age,
        same_site="lax",
        https_only=False,
    )

    @app.get("/actuator/health")
    def actuator_health() -> Dict[str, str]:
        """Spring Boot Actuator-compatible liveness JSON; public (no auth)."""
        return _HEALTH_BODY

    @app.get("/actuator/health/{subpath:path}")
    def actuator_health_subpath(subpath: str) -> Dict[str, str]:
        """Subpaths under /actuator/health/ (e.g. liveness) — same contract as root."""
        return _HEALTH_BODY

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "index.html")

    @app.get("/login", response_class=HTMLResponse)
    def login_get(request: Request) -> HTMLResponse:
        if request.session.get(SESSION_USER_KEY):
            return RedirectResponse(url="/home", status_code=303)
        flash = request.session.pop("_flash", None)
        csrf_token = get_or_create_csrf(request.session)
        return templates.TemplateResponse(
            request,
            "login.html",
            {"csrf_token": csrf_token, "flash": flash},
        )

    @app.post("/login")
    def login_post(
        request: Request,
        db: Session = Depends(get_db),
        username: str = Form(...),
        password: str = Form(...),
        csrf_token: str = Form(...),
    ) -> RedirectResponse:
        if not validate_csrf(request.session, csrf_token):
            request.session["_flash"] = "Invalid or missing security token. Try again."
            return RedirectResponse(url="/login", status_code=303)
        user = get_user_by_email(db, username)
        if user is None or not user.enabled:
            request.session["_flash"] = "Invalid email or password."
            return RedirectResponse(url="/login", status_code=303)
        if not verify_password(password, user.password_hash):
            request.session["_flash"] = "Invalid email or password."
            return RedirectResponse(url="/login", status_code=303)
        request.session[SESSION_USER_KEY] = str(user.id)
        get_or_create_csrf(request.session)
        return RedirectResponse(url="/home", status_code=303)

    @app.post("/logout")
    def logout_post(
        request: Request,
        csrf_token: str = Form(...),
    ) -> RedirectResponse:
        if not validate_csrf(request.session, csrf_token):
            request.session["_flash"] = "Invalid or missing security token."
            return RedirectResponse(url="/login", status_code=303)
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)

    @app.get("/home", response_class=HTMLResponse)
    def home(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
        uid = request.session.get(SESSION_USER_KEY)
        user = get_user_by_id(db, uuid.UUID(str(uid))) if uid else None
        csrf_token = get_or_create_csrf(request.session)
        return templates.TemplateResponse(
            request,
            "home.html",
            {
                "user": user,
                "csrf_token": csrf_token,
            },
        )

    @app.get("/app/secure", response_class=HTMLResponse)
    def secure_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
        uid = request.session.get(SESSION_USER_KEY)
        user = get_user_by_id(db, uuid.UUID(str(uid))) if uid else None
        csrf_token = get_or_create_csrf(request.session)
        return templates.TemplateResponse(
            request,
            "secure.html",
            {"user": user, "csrf_token": csrf_token},
        )

    # Role-space smoke routes (Story 1.4) — minimal placeholders until epics 2–7 flesh them out.
    @app.get("/review/queue", response_class=HTMLResponse)
    def review_queue_placeholder(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "spaces/review-queue.html")

    @app.get("/error", response_class=HTMLResponse)
    def error_page(
        request: Request,
        message: Optional[str] = None,
    ) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "error.html",
            {"message": message or "An unexpected error occurred."},
        )

    app.mount(
        "/css",
        StaticFiles(directory=str(static_root / "css")),
        name="css",
    )
    app.mount(
        "/js",
        StaticFiles(directory=str(static_root / "js")),
        name="js",
    )
    app.mount(
        "/webjars",
        StaticFiles(directory=str(static_root / "webjars")),
        name="webjars",
    )

    return app


_lazy_app: Optional[FastAPI] = None


def __getattr__(name: str) -> Any:
    """Lazy `app` so `uvicorn examai.main:app` works without forcing import-time DB setup."""
    global _lazy_app
    if name == "app":
        if _lazy_app is None:
            _lazy_app = create_app()
        return _lazy_app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
