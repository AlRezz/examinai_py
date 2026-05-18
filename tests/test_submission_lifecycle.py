"""Unit tests for intern submission lifecycle badge mapping."""

from __future__ import annotations

import uuid

from examai.models import Submission
from examai.submission_lifecycle import (
    intern_submission_lifecycle_badge,
    mentor_submission_lifecycle_badge,
)


def _sub(**kwargs: object) -> Submission:
    base = dict(
        task_id=uuid.uuid4(),
        intern_user_id=uuid.uuid4(),
        repo_identifier="org/x",
        status="pending",
    )
    base.update(kwargs)
    return Submission(**base)


def test_no_submission() -> None:
    b = intern_submission_lifecycle_badge(submission=None, has_published_feedback=False)
    assert b.label == "No submission yet"
    assert "secondary" in b.css_class


def test_published_wins_over_git_state() -> None:
    s = _sub(git_retrieval_state="failed", git_retrieval_error_code="x")
    b = intern_submission_lifecycle_badge(submission=s, has_published_feedback=True)
    assert b.label == "Feedback published"


def test_git_failed() -> None:
    s = _sub(git_retrieval_state="failed", git_retrieval_error_code="AUTH_DENIED")
    b = intern_submission_lifecycle_badge(submission=s, has_published_feedback=False)
    assert b.label == "Source retrieval failed"
    assert b.title == "AUTH_DENIED"


def test_git_success() -> None:
    s = _sub(git_retrieval_state="success")
    b = intern_submission_lifecycle_badge(submission=s, has_published_feedback=False)
    assert b.label == "Source retrieved"


def test_git_in_progress() -> None:
    s = _sub(git_retrieval_state="fetching")
    b = intern_submission_lifecycle_badge(submission=s, has_published_feedback=False)
    assert "Retrieving" in b.label


def test_fallback_coordinates_saved() -> None:
    s = _sub()
    b = intern_submission_lifecycle_badge(submission=s, has_published_feedback=False)
    assert b.label == "Coordinates saved"


def test_mentor_not_submitted() -> None:
    b = mentor_submission_lifecycle_badge(
        submission=None, has_published=False, has_mentor_draft=False
    )
    assert b.label == "Not submitted"


def test_mentor_published_wins() -> None:
    s = _sub(git_retrieval_state="success")
    b = mentor_submission_lifecycle_badge(
        submission=s, has_published=True, has_mentor_draft=True
    )
    assert b.label == "Published"


def test_mentor_fetch_failed() -> None:
    s = _sub(git_retrieval_state="failed", git_retrieval_error_code="NOT_FOUND")
    b = mentor_submission_lifecycle_badge(
        submission=s, has_published=False, has_mentor_draft=False
    )
    assert b.label == "Source retrieval failed"
    assert "warning" in b.css_class


def test_mentor_fetch_failed_auth_uses_danger() -> None:
    s = _sub(git_retrieval_state="failed", git_retrieval_error_code="AUTH_DENIED")
    b = mentor_submission_lifecycle_badge(
        submission=s, has_published=False, has_mentor_draft=False
    )
    assert "danger" in b.css_class


def test_mentor_draft_saved() -> None:
    s = _sub(git_retrieval_state="success")
    b = mentor_submission_lifecycle_badge(
        submission=s, has_published=False, has_mentor_draft=True
    )
    assert b.label == "Draft saved"


def test_mentor_ready_for_review() -> None:
    s = _sub(git_retrieval_state="success")
    b = mentor_submission_lifecycle_badge(
        submission=s, has_published=False, has_mentor_draft=False
    )
    assert b.label == "Ready for review"


def test_mentor_coordinates_saved() -> None:
    s = _sub()
    b = mentor_submission_lifecycle_badge(
        submission=s, has_published=False, has_mentor_draft=False
    )
    assert b.label == "Coordinates saved"
