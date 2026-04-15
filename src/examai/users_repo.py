"""User and role lookups."""

from __future__ import annotations

import uuid
from typing import FrozenSet

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from examai.models import Role, User


def get_user_by_email(session: Session, email: str) -> User | None:
    normalized = email.strip().lower()
    stmt = select(User).where(func.lower(User.email) == normalized)
    return session.execute(stmt).scalar_one_or_none()


def get_user_by_id(session: Session, user_id: uuid.UUID) -> User | None:
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.roles))
    )
    return session.execute(stmt).scalar_one_or_none()


def role_names_for_user(session: Session, user_id: uuid.UUID) -> FrozenSet[str]:
    user = get_user_by_id(session, user_id)
    if user is None:
        return frozenset()
    return frozenset(r.name for r in user.roles)
