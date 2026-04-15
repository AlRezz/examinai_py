"""Coordinator oversight queries (Story 7.1, docs/data-models.md)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from examai.models import Submission, Task, User


@dataclass(frozen=True)
class CoordinatorSubmissionSummary:
    submission_id: uuid.UUID
    task_id: uuid.UUID
    task_title: str
    intern_email: str
    status: str
    repo_identifier: str
    updated_at: datetime


@dataclass(frozen=True)
class CoordinatorCaseRecord:
    submission: Submission
    task: Task
    intern: User


def list_submission_summaries(session: Session) -> list[CoordinatorSubmissionSummary]:
    """All submissions with task title and intern email for the coordinator index."""
    stmt = (
        select(Submission, Task.title, User.email)
        .join(Task, Submission.task_id == Task.id)
        .join(User, Submission.intern_user_id == User.id)
        .order_by(Submission.updated_at.desc())
    )
    rows = session.execute(stmt).all()
    out: list[CoordinatorSubmissionSummary] = []
    for sub, task_title, intern_email in rows:
        out.append(
            CoordinatorSubmissionSummary(
                submission_id=sub.id,
                task_id=sub.task_id,
                task_title=task_title,
                intern_email=intern_email,
                status=sub.status,
                repo_identifier=sub.repo_identifier,
                updated_at=sub.updated_at,
            )
        )
    return out


def get_case_record(session: Session, submission_id: uuid.UUID) -> CoordinatorCaseRecord | None:
    stmt = (
        select(Submission, Task, User)
        .join(Task, Submission.task_id == Task.id)
        .join(User, Submission.intern_user_id == User.id)
        .where(Submission.id == submission_id)
    )
    row = session.execute(stmt).one_or_none()
    if row is None:
        return None
    sub, task, intern = row
    return CoordinatorCaseRecord(submission=sub, task=task, intern=intern)
