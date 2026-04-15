"""Intern-scoped task reads via task_assignments (Story 3.1, docs/data-models.md)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from examai.models import Task, TaskAssignment


def list_assigned_tasks_for_intern(session: Session, intern_user_id: uuid.UUID) -> list[Task]:
    """Tasks linked to the intern through task_assignments (FR7)."""
    stmt = (
        select(Task)
        .join(TaskAssignment, TaskAssignment.task_id == Task.id)
        .where(TaskAssignment.intern_user_id == intern_user_id)
        .order_by(Task.created_at.desc())
    )
    return list(session.scalars(stmt).unique().all())


def get_task_for_intern_if_assigned(
    session: Session, intern_user_id: uuid.UUID, task_id: uuid.UUID
) -> Task | None:
    """Task detail only when an assignment row exists for this intern (FR8)."""
    stmt = (
        select(Task)
        .join(TaskAssignment, TaskAssignment.task_id == Task.id)
        .where(
            TaskAssignment.intern_user_id == intern_user_id,
            Task.id == task_id,
        )
    )
    return session.scalar(stmt)
