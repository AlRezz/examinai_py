"""Mentor submission workspace queries (docs/data-models.md)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from examai.models import (
    AiDraft,
    MentorReviewDraft,
    ModelInvocation,
    PublishedReview,
    Submission,
    TaskAssignment,
    User,
)


@dataclass(frozen=True)
class InternSubmissionRow:
    intern: User
    submission: Submission | None


def list_intern_submissions_for_task(session: Session, task_id: uuid.UUID) -> list[InternSubmissionRow]:
    """Assigned interns with optional submission row (left join)."""
    stmt = (
        select(User, Submission)
        .join(TaskAssignment, TaskAssignment.intern_user_id == User.id)
        .where(TaskAssignment.task_id == task_id)
        .outerjoin(
            Submission,
            (Submission.task_id == TaskAssignment.task_id)
            & (Submission.intern_user_id == TaskAssignment.intern_user_id),
        )
        .order_by(User.email.asc())
    )
    rows: list[InternSubmissionRow] = []
    for user, sub in session.execute(stmt).all():
        rows.append(InternSubmissionRow(intern=user, submission=sub))
    return rows


def get_submission_for_pair(
    session: Session,
    task_id: uuid.UUID,
    intern_user_id: uuid.UUID,
) -> Submission | None:
    stmt = select(Submission).where(
        Submission.task_id == task_id,
        Submission.intern_user_id == intern_user_id,
    )
    return session.scalars(stmt).first()


def intern_assigned_to_task(session: Session, task_id: uuid.UUID, intern_user_id: uuid.UUID) -> bool:
    stmt = select(TaskAssignment).where(
        TaskAssignment.task_id == task_id,
        TaskAssignment.intern_user_id == intern_user_id,
    )
    return session.scalars(stmt).first() is not None


def get_latest_ai_draft(session: Session, submission_id: uuid.UUID) -> tuple[ModelInvocation, AiDraft] | None:
    stmt = (
        select(ModelInvocation, AiDraft)
        .join(AiDraft, AiDraft.model_invocation_id == ModelInvocation.id)
        .where(ModelInvocation.submission_id == submission_id)
        .order_by(ModelInvocation.invoked_at.desc())
        .limit(1)
    )
    row = session.execute(stmt).first()
    if row is None:
        return None
    inv, draft = row[0], row[1]
    return inv, draft


def get_mentor_review_draft(session: Session, submission_id: uuid.UUID) -> MentorReviewDraft | None:
    stmt = select(MentorReviewDraft).where(MentorReviewDraft.submission_id == submission_id)
    return session.scalars(stmt).first()


def get_published_review(session: Session, submission_id: uuid.UUID) -> PublishedReview | None:
    stmt = select(PublishedReview).where(PublishedReview.submission_id == submission_id)
    return session.scalars(stmt).first()


def upsert_mentor_review_draft(
    session: Session,
    *,
    submission_id: uuid.UUID,
    mentor_user_id: uuid.UUID,
    quality_score: Optional[int],
    readability_score: Optional[int],
    correctness_score: Optional[int],
    narrative_feedback: Optional[str],
) -> MentorReviewDraft:
    existing = get_mentor_review_draft(session, submission_id)
    if existing is None:
        row = MentorReviewDraft(
            submission_id=submission_id,
            mentor_user_id=mentor_user_id,
            quality_score=quality_score,
            readability_score=readability_score,
            correctness_score=correctness_score,
            narrative_feedback=narrative_feedback,
        )
        session.add(row)
    else:
        existing.mentor_user_id = mentor_user_id
        existing.quality_score = quality_score
        existing.readability_score = readability_score
        existing.correctness_score = correctness_score
        existing.narrative_feedback = narrative_feedback
        row = existing
    session.commit()
    session.refresh(row)
    return row


def upsert_published_review(
    session: Session,
    *,
    submission: Submission,
    mentor_user_id: uuid.UUID,
    quality_score: Optional[int],
    readability_score: Optional[int],
    correctness_score: Optional[int],
    narrative: Optional[str],
) -> PublishedReview:
    existing = get_published_review(session, submission.id)
    snap_sha = submission.commit_sha
    snap_path = submission.path_scope
    snap_ver = submission.git_fetch_version
    if existing is None:
        row = PublishedReview(
            submission_id=submission.id,
            quality_score=quality_score,
            readability_score=readability_score,
            correctness_score=correctness_score,
            narrative=narrative,
            publishing_mentor_user_id=mentor_user_id,
            snapshot_commit_sha=snap_sha,
            snapshot_git_fetch_version=snap_ver,
            snapshot_path_scope=snap_path,
        )
        session.add(row)
    else:
        existing.quality_score = quality_score
        existing.readability_score = readability_score
        existing.correctness_score = correctness_score
        existing.narrative = narrative
        existing.publishing_mentor_user_id = mentor_user_id
        existing.snapshot_commit_sha = snap_sha
        existing.snapshot_git_fetch_version = snap_ver
        existing.snapshot_path_scope = snap_path
        row = existing
    session.commit()
    session.refresh(row)
    return row
