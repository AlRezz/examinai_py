"""User and role lookups."""

from __future__ import annotations

import uuid
from typing import FrozenSet

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from examai.models import Role, User, user_roles
from examai.security import hash_password


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


def list_roles_ordered(session: Session) -> list[Role]:
    """All roles for admin assignment UI, ordered by name."""
    stmt = select(Role).order_by(Role.name)
    return list(session.scalars(stmt).all())


def create_user_with_roles(
    session: Session,
    *,
    email: str,
    password_plain: str,
    enabled: bool,
    role_names: list[str],
) -> tuple[User | None, str | None]:
    """
    Create a user and assign roles. Normalizes email; hashes password.
    Returns (user, None) on success, or (None, error_message) on validation / conflict.
    """
    email_norm = email.strip().lower()
    if not email_norm:
        return None, "Email is required."
    pw = password_plain.strip()
    if not pw:
        return None, "Password is required."
    if len(pw) > 72:
        return None, "Password must be at most 72 bytes."
    unique_names = sorted({n.strip() for n in role_names if n and str(n).strip()})
    if not unique_names:
        return None, "Select at least one role."
    if get_user_by_email(session, email_norm) is not None:
        return None, "A user with that email already exists."

    roles: list[Role] = []
    for name in unique_names:
        role = session.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
        if role is None:
            return None, f"Unknown role: {name}."
        roles.append(role)

    user = User(
        id=uuid.uuid4(),
        email=email_norm,
        password_hash=hash_password(pw),
        enabled=enabled,
    )
    for r in roles:
        user.roles.append(r)
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        return None, "A user with that email already exists."
    session.refresh(user)
    return user, None


def update_user_with_roles(
    session: Session,
    *,
    user_id: uuid.UUID,
    actor_user_id: uuid.UUID | None,
    email: str,
    password_plain: str | None,
    enabled: bool,
    role_names: list[str],
) -> tuple[User | None, str | None]:
    """
    Update user email, enabled, optional password (non-empty => rehash), and replace role assignments.
    Normalizes email. Returns (user, None) on success, or (None, error_message).
    """
    user = get_user_by_id(session, user_id)
    if user is None:
        return None, "User not found."

    email_norm = email.strip().lower()
    if not email_norm:
        return None, "Email is required."

    unique_names = sorted({n.strip() for n in role_names if n and str(n).strip()})
    if not unique_names:
        return None, "Select at least one role."

    if actor_user_id is not None and user_id == actor_user_id:
        if not enabled:
            return None, "You cannot disable your own account."
        if "administrator" not in unique_names:
            return None, "You cannot remove your own administrator role."

    other = get_user_by_email(session, email_norm)
    if other is not None and other.id != user_id:
        return None, "A user with that email already exists."

    roles: list[Role] = []
    for name in unique_names:
        role = session.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
        if role is None:
            return None, f"Unknown role: {name}."
        roles.append(role)

    pw_change = (password_plain or "").strip()
    if pw_change:
        if len(pw_change) > 72:
            return None, "Password must be at most 72 bytes."
        user.password_hash = hash_password(pw_change)

    user.email = email_norm
    user.enabled = enabled
    user.roles.clear()
    for r in roles:
        user.roles.append(r)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        return None, "A user with that email already exists."
    session.refresh(user)
    return user, None
