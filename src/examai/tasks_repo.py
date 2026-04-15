"""Task persistence (docs/data-models.md — tasks)."""

from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from examai.models import Task


def list_tasks(session: Session) -> list[Task]:
    stmt = select(Task).order_by(Task.created_at.desc())
    return list(session.scalars(stmt).all())


def get_task_by_id(session: Session, task_id: uuid.UUID) -> Task | None:
    return session.get(Task, task_id)


def create_task(
    session: Session,
    *,
    title: str,
    description: Optional[str],
    due_date: Optional[date],
) -> Task:
    task = Task(title=title, description=description, due_date=due_date)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def update_task(
    session: Session,
    task: Task,
    *,
    title: str,
    description: Optional[str],
    due_date: Optional[date],
) -> Task:
    task.title = title
    task.description = description
    task.due_date = due_date
    session.commit()
    session.refresh(task)
    return task
