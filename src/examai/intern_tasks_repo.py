"""Intern-scoped task reads via task_assignments (Story 3.1, docs/data-models.md)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from examai.models import PublishedReview, Submission, Task, TaskAssignment


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


def get_submission_for_intern_pair(
    session: Session, intern_user_id: uuid.UUID, task_id: uuid.UUID
) -> Submission | None:
    """Existing submission row for this intern on this task, if any (FR9, FR28)."""
    stmt = select(Submission).where(
        Submission.task_id == task_id,
        Submission.intern_user_id == intern_user_id,
    )
    return session.scalar(stmt)


def get_published_feedback_for_intern_submission(
    session: Session, intern_user_id: uuid.UUID, submission_id: uuid.UUID
) -> PublishedReview | None:
    """Published review for `submission_id` only if that submission belongs to the intern (FR10)."""
    stmt = (
        select(PublishedReview)
        .join(Submission, Submission.id == PublishedReview.submission_id)
        .where(
            PublishedReview.submission_id == submission_id,
            Submission.intern_user_id == intern_user_id,
        )
    )
    return session.scalar(stmt)


def upsert_intern_submission_coordinates(
    session: Session,
    task_id: uuid.UUID,
    intern_user_id: uuid.UUID,
    repo_identifier: str,
    commit_sha: str | None,
    path_scope: str | None,
) -> Submission:
    """Create or update coordinates for the (task, intern) pair (FR9)."""
    existing = get_submission_for_intern_pair(session, intern_user_id, task_id)
    if existing is not None:
        existing.repo_identifier = repo_identifier
        existing.commit_sha = commit_sha
        existing.path_scope = path_scope
        session.commit()
        session.refresh(existing)
        return existing
    sub = Submission(
        task_id=task_id,
        intern_user_id=intern_user_id,
        repo_identifier=repo_identifier,
        commit_sha=commit_sha,
        path_scope=path_scope,
        status="pending",
    )
    session.add(sub)
    session.commit()
    session.refresh(sub)
    return sub
