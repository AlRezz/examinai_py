"""URL-space access rules (docs/api-contracts.md, architecture RBAC)."""

from __future__ import annotations

from typing import FrozenSet

# Role names match seeded `roles.name` (data-models.md).
ROLE_INTERN = "intern"
ROLE_MENTOR = "mentor"
ROLE_ADMINISTRATOR = "administrator"
ROLE_COORDINATOR = "coordinator"


def required_roles_for_path(path: str) -> FrozenSet[str] | None:
    """Return roles that may access this path (any one is enough), or None if not RBAC-guarded here."""
    if path.startswith("/admin/"):
        return frozenset({ROLE_ADMINISTRATOR})
    if path.startswith("/intern/"):
        return frozenset({ROLE_INTERN})
    if path.startswith("/coordinator"):
        return frozenset({ROLE_COORDINATOR})
    if path.startswith("/tasks") or path.startswith("/review/"):
        return frozenset({ROLE_MENTOR, ROLE_ADMINISTRATOR})
    return None


def roles_allow_path(path: str, user_roles: FrozenSet[str]) -> bool:
    required = required_roles_for_path(path)
    if required is None:
        return True
    return bool(user_roles & required)
