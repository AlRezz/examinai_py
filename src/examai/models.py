"""SQLAlchemy ORM models aligned with docs/data-models.md."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Optional
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Table, Column, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        Uuid(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    roles: Mapped[list["Role"]] = relationship(
        secondary=user_roles,
        back_populates="users",
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    users: Mapped[list[User]] = relationship(
        secondary=user_roles,
        back_populates="roles",
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )


class TaskAssignment(Base):
    __tablename__ = "task_assignments"

    task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    intern_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Submission(Base):
    """One row per (task, intern) pair — docs/data-models.md."""

    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint("task_id", "intern_user_id", name="uq_submissions_task_intern"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    intern_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    repo_identifier: Mapped[str] = mapped_column(String(500), nullable=False)
    commit_sha: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    path_scope: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    model_invocations: Mapped[list["ModelInvocation"]] = relationship(
        back_populates="submission",
    )


class ModelInvocation(Base):
    """Successful LLM inference audit row (docs/data-models.md)."""

    __tablename__ = "model_invocations"
    __table_args__ = (Index("ix_model_invocations_submission_invoked", "submission_id", "invoked_at"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    invoked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    model_version: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    prompt_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    submission: Mapped["Submission"] = relationship(back_populates="model_invocations")
    ai_draft: Mapped[Optional["AiDraft"]] = relationship(back_populates="model_invocation", uselist=False)


class AiDraft(Base):
    """AI-generated assessment text linked to one invocation."""

    __tablename__ = "ai_drafts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_invocation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("model_invocations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    assessment_text: Mapped[str] = mapped_column(Text, nullable=False)

    model_invocation: Mapped["ModelInvocation"] = relationship(back_populates="ai_draft")


class MentorReviewDraft(Base):
    """Mentor WIP rubric per submission."""

    __tablename__ = "mentor_review_drafts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    quality_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    readability_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    correctness_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    narrative_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mentor_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False
    )

    submission: Mapped["Submission"] = relationship()
    mentor: Mapped["User"] = relationship()


class PublishedReview(Base):
    """Published mentor outcome per submission."""

    __tablename__ = "published_reviews"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    quality_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    readability_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    correctness_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    narrative: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    publishing_mentor_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False)
    snapshot_commit_sha: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    snapshot_git_fetch_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    snapshot_path_scope: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)

    submission: Mapped["Submission"] = relationship()


__all__ = [
    "Base",
    "User",
    "Role",
    "user_roles",
    "Task",
    "TaskAssignment",
    "Submission",
    "ModelInvocation",
    "AiDraft",
    "MentorReviewDraft",
    "PublishedReview",
]
