"""Application entry: FastAPI app factory and minimal health route."""

from __future__ import annotations

from typing import Dict

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(
        title="Examinai",
        # OpenAPI UI disabled by default (server-rendered product, not JSON API-first).
        docs_url=None,
        redoc_url=None,
    )

    @app.get("/actuator/health")
    def actuator_health() -> Dict[str, str]:
        """Compatible with Spring Boot Actuator health path used in runbooks."""
        return {"status": "UP"}

    return app


app = create_app()
