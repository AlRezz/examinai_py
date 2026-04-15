# Story 3.4: Submission lifecycle status badge

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **intern**,  
I want **a clear status indicator for my submission pipeline**,  
so that **I understand retrieval/review state without raw errors only**.

## Acceptance Criteria

1. **Badge on intern task detail**  
   **Given** I am on an intern task detail page  
   **When** the page renders  
   **Then** a badge shows submission/Git lifecycle state (**UX-DR4**, **FR29** visibility).

2. **Badge on published feedback**  
   **Given** I open published feedback for my submission  
   **When** the page renders  
   **Then** the same badge pattern shows consistent pipeline state (published when applicable).

3. **Model alignment**  
   **Then** lifecycle logic can use `submissions.git_retrieval_*` fields per **[docs/data-models.md](../../docs/data-models.md)** when set (mentor/workspace flows).

## Tasks / Subtasks

- [x] **ORM** (AC: 3)  
  - [x] Add nullable `git_retrieval_*` and `git_fetch_version` on `Submission` for data-models parity.

- [x] **Lifecycle mapping** (AC: 1–3)  
  - [x] `intern_submission_lifecycle_badge()` — published → Git state → `submission.status` fallback.

- [x] **Templates** (AC: 1–2)  
  - [x] `intern/fragments/submission-lifecycle-badge.html`; include on `intern/tasks/detail.html` and `intern/submissions/feedback.html`.

- [x] **Routes** (AC: 1–2)  
  - [x] Pass `submission_lifecycle` from `intern_routes` for detail and feedback.

- [x] **Tests** (AC: 1–2)  
  - [x] Unit tests for mapping; intern HTML asserts for “No submission yet”, “Coordinates saved”, “Feedback published”.

## Dev Notes

### Dependencies

- **Stories 3.1–3.3:** Intern tasks, submissions, published feedback.

### References

- [docs/data-models.md](../../docs/data-models.md) — `submissions` Git retrieval fields  
- Epic planning: **UX-DR4**

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

- Added `Submission` git columns; `submission_lifecycle.py` + fragment; wired intern task detail and feedback pages; `mentor_workspace_repo` publish snapshot uses `git_fetch_version`. Tests: `tests/test_submission_lifecycle.py`, extended `tests/test_intern_tasks.py`. Full suite: 83 passed.

### File List

- `src/examai/models.py` (modified)
- `src/examai/submission_lifecycle.py` (new)
- `src/examai/intern_routes.py` (modified)
- `src/examai/mentor_workspace_repo.py` (modified)
- `src/examai/templates/intern/fragments/submission-lifecycle-badge.html` (new)
- `src/examai/templates/intern/tasks/detail.html` (modified)
- `src/examai/templates/intern/submissions/feedback.html` (modified)
- `tests/test_submission_lifecycle.py` (new)
- `tests/test_intern_tasks.py` (modified)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)
- `_bmad-output/implementation-artifacts/3-4-submission-lifecycle-status-badge.md` (new)

### Change Log

- 2026-04-15 — Story 3.4: intern submission lifecycle badge; sprint status → review.

---

**Story completion status:** Implementation complete. **done.**
