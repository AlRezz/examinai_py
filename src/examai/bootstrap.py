"""Schema creation and reference data (roles, optional demo user)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from examai.config import Settings
from examai.models import Role, User
from examai.security import hash_password
from examai.users_repo import get_user_by_email

SEEDED_ROLE_NAMES = (
    "intern",
    "mentor",
    "administrator",
    "coordinator",
)


def ensure_roles(session: Session) -> None:
    for name in SEEDED_ROLE_NAMES:
        existing = session.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
        if existing is None:
            session.add(Role(id=uuid.uuid4(), name=name))
    session.commit()


def _role_by_name(session: Session, name: str) -> Role | None:
    return session.execute(select(Role).where(Role.name == name)).scalar_one_or_none()


def maybe_seed_demo_user(session: Session, settings: Settings) -> None:
    if not settings.bootstrap_demo_user:
        return
    email = "demo@examinai.local"
    if get_user_by_email(session, email) is not None:
        return
    pw = hash_password("demo")
    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash=pw,
        enabled=True,
    )
    intern = _role_by_name(session, "intern")
    if intern is None:
        return
    user.roles.append(intern)
    session.add(user)
    session.commit()
