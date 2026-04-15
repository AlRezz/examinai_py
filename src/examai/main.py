"""Application entry: FastAPI app factory, public shell, and health route."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates


def _package_dir() -> Path:
    return Path(__file__).resolve().parent


def create_app() -> FastAPI:
    app = FastAPI(
        title="Examinai",
        # OpenAPI UI disabled by default (server-rendered product, not JSON API-first).
        docs_url=None,
        redoc_url=None,
    )

    root = _package_dir()
    static_root = root / "static"
    templates = Jinja2Templates(directory=str(root / "templates"))

    @app.get("/actuator/health")
    def actuator_health() -> Dict[str, str]:
        """Compatible with Spring Boot Actuator health path used in runbooks."""
        return {"status": "UP"}

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "index.html")

    @app.get("/login", response_class=HTMLResponse)
    def login(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "login.html")

    @app.get("/error", response_class=HTMLResponse)
    def error_page(
        request: Request,
        message: Optional[str] = None,
    ) -> HTMLResponse:
        # Optional query param for user-visible copy only (no stack traces; Story 1-1).
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


app = create_app()
