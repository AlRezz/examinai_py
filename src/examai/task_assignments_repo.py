"""Task ↔ intern assignments (docs/data-models.md — task_assignments)."""

from __future__ import annotations

import uuid
from typing import Iterable

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from examai.models import TaskAssignment


def assigned_intern_ids_for_task(session: Session, task_id: uuid.UUID) -> set[uuid.UUID]:
    stmt = select(TaskAssignment.intern_user_id).where(TaskAssignment.task_id == task_id)
    return set(session.scalars(stmt).all())


def replace_task_assignments(
    session: Session,
    task_id: uuid.UUID,
    intern_user_ids: Iterable[uuid.UUID],
) -> None:
    """Replace all assignments for the task with the given intern user ids (deduplicated, order preserved)."""
    seen: set[uuid.UUID] = set()
    ordered: list[uuid.UUID] = []
    for iid in intern_user_ids:
        if iid not in seen:
            seen.add(iid)
            ordered.append(iid)
    session.execute(delete(TaskAssignment).where(TaskAssignment.task_id == task_id))
    for iid in ordered:
        session.add(TaskAssignment(task_id=task_id, intern_user_id=iid))
    session.commit()
