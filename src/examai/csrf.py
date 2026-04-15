"""CSRF token helpers (session-bound, double-submit style)."""

from __future__ import annotations

import secrets
from typing import Any, Mapping, MutableMapping

SESSION_CSRF_KEY = "_csrf_token"


def get_or_create_csrf(session: MutableMapping[str, Any]) -> str:
    existing = session.get(SESSION_CSRF_KEY)
    if isinstance(existing, str) and len(existing) >= 16:
        return existing
    token = secrets.token_urlsafe(32)
    session[SESSION_CSRF_KEY] = token
    return token


def validate_csrf(session: Mapping[str, Any], submitted: str | None) -> bool:
    if not submitted:
        return False
    expected = session.get(SESSION_CSRF_KEY)
    if not isinstance(expected, str):
        return False
    return secrets.compare_digest(expected, submitted)
