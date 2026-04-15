"""User and role lookups."""

from __future__ import annotations

import uuid
from typing import FrozenSet

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from examai.models import Role, User, user_roles


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


def list_users_with_role(session: Session, role_name: str) -> list[User]:
    """Users that have the given role name, ordered by email."""
    stmt = (
        select(User)
        .join(user_roles, User.id == user_roles.c.user_id)
        .join(Role, Role.id == user_roles.c.role_id)
        .where(Role.name == role_name)
        .order_by(User.email)
    )
    return list(session.scalars(stmt).unique().all())


def list_users_with_roles(session: Session) -> list[User]:
    """All users with roles loaded, ordered by email (admin list; do not expose password_hash in templates)."""
    stmt = select(User).options(selectinload(User.roles)).order_by(User.email)
    return list(session.scalars(stmt).unique().all())
