"""Intern-facing submission / Git lifecycle labels for UI badges (UX-DR4, FR29 visibility)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from examai.models import Submission


@dataclass(frozen=True)
class SubmissionLifecycleBadge:
    """Bootstrap badge payload for templates."""

    label: str
    css_class: str
    title: str | None = None


def intern_submission_lifecycle_badge(
    *,
    submission: Submission | None,
    has_published_feedback: bool,
) -> SubmissionLifecycleBadge:
    """
    Map submission row + publication flag to a single human-readable pipeline state.
    Published feedback wins over intermediate Git states.
    """
    if submission is None:
        return SubmissionLifecycleBadge(
            label="No submission yet",
            css_class="bg-secondary",
        )
    if has_published_feedback:
        return SubmissionLifecycleBadge(
            label="Feedback published",
            css_class="bg-success",
        )

    state = (submission.git_retrieval_state or "").strip().lower()
    if state == "failed":
        detail = submission.git_retrieval_error_code or "retrieval_failed"
        return SubmissionLifecycleBadge(
            label="Source retrieval failed",
            css_class="bg-danger",
            title=detail,
        )
    if state in ("success", "ok", "complete", "succeeded"):
        return SubmissionLifecycleBadge(
            label="Source retrieved",
            css_class="bg-success",
        )
    if state in ("pending", "in_progress", "fetching", "running", "queued"):
        return SubmissionLifecycleBadge(
            label="Retrieving source…",
            css_class="bg-warning text-dark",
        )

    st = (submission.status or "pending").strip().lower()
    if st == "pending":
        return SubmissionLifecycleBadge(
            label="Coordinates saved",
            css_class="bg-info text-dark",
        )
    return SubmissionLifecycleBadge(
        label=submission.status.replace("_", " ").strip().title() or "Unknown",
        css_class="bg-primary",
    )


_AUTH_GIT_ERROR_CODES = frozenset(
    {
        "AUTH_DENIED",
        "FORBIDDEN",
        "PERMISSION_DENIED",
        "GIT_AUTH_FAILED",
    }
)


def _git_failure_badge_class(error_code: str | None) -> str:
    """Retryable fetch failures use warning; auth/permission use danger (AC5)."""
    code = (error_code or "").strip().upper()
    if code in _AUTH_GIT_ERROR_CODES or "AUTH" in code or "FORBIDDEN" in code:
        return "bg-danger"
    return "bg-warning text-dark"


def mentor_submission_lifecycle_badge(
    *,
    submission: Submission | None,
    has_published: bool,
    has_mentor_draft: bool,
) -> SubmissionLifecycleBadge:
    """
    Mentor workspace pipeline badge (UX Phase 1).
    Published wins; draft saved wins over ready-for-review when fetch succeeded.
    """
    if submission is None:
        return SubmissionLifecycleBadge(
            label="Not submitted",
            css_class="bg-secondary",
        )
    if has_published:
        return SubmissionLifecycleBadge(
            label="Published",
            css_class="bg-success",
        )

    state = (submission.git_retrieval_state or "").strip().lower()
    if state in ("pending", "in_progress", "fetching", "running", "queued"):
        return SubmissionLifecycleBadge(
            label="Retrieving source…",
            css_class="bg-warning text-dark",
        )
    if state == "failed":
        detail = submission.git_retrieval_error_code or "retrieval_failed"
        return SubmissionLifecycleBadge(
            label="Source retrieval failed",
            css_class=_git_failure_badge_class(detail),
            title=detail,
        )
    if has_mentor_draft:
        return SubmissionLifecycleBadge(
            label="Draft saved",
            css_class="bg-info text-dark",
        )
    if state in ("success", "ok", "complete", "succeeded"):
        return SubmissionLifecycleBadge(
            label="Ready for review",
            css_class="bg-primary",
        )

    return SubmissionLifecycleBadge(
        label="Coordinates saved",
        css_class="bg-info text-dark",
    )
