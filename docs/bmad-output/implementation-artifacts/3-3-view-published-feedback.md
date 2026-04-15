# Story 3.3: View published feedback

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **intern**,  
I want **to open published feedback for my submission**,  
so that **I see official outcomes**.

## Acceptance Criteria

1. **Published feedback page**  
   **Given** a published review exists for my submission  
   **When** I `GET /intern/submissions/{submissionId}/feedback`  
   **Then** I see published scores, narrative, and snapshot context per **FR10** and **[docs/data-models.md](../../docs/data-models.md)** (`published_reviews`).

2. **Access control**  
   **Then** only the owning intern can load feedback for that submission; other users get **403** (non-intern) or **404** (wrong intern / unknown submission / not yet published), consistent with intern task detail policy.

3. **Discoverability**  
   **Then** when published feedback exists, task detail shows a link to the feedback page (**UX-DR14** alignment).

## Tasks / Subtasks

- [x] **Repo** (AC: 1–2)  
  - [x] `get_published_feedback_for_intern_submission` — join `published_reviews` with `submissions` for ownership.

- [x] **Route + template** (AC: 1–2)  
  - [x] `GET /intern/submissions/{submissionId}/feedback` with intern session; render `intern/submissions/feedback.html`.

- [x] **Task detail link** (AC: 3)  
  - [x] Pass `published_feedback` from repo; show “View published feedback” when present.

- [x] **Tests** (AC: 1–2)  
  - [x] Happy path content; 404 wrong intern / not published; 403 non-intern; detail link when published.

## Dev Notes

### Dependencies

- **Story 3.1–3.2:** Intern tasks and submissions.  
- **Mentor publish:** `published_reviews` rows (Epic 4 / mentor workspace).

### References

- [docs/api-contracts.md](../../docs/api-contracts.md)  
- [docs/data-models.md](../../docs/data-models.md) — `published_reviews`

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

- Added `get_published_feedback_for_intern_submission` in `intern_tasks_repo.py`; `GET /intern/submissions/{submission_id}/feedback` and task-detail link in `intern_routes.py` / `intern/tasks/detail.html`; template `intern/submissions/feedback.html`. Tests in `tests/test_intern_tasks.py`. Full suite: 77 passed.

### File List

- `src/examai/intern_tasks_repo.py` (modified)
- `src/examai/intern_routes.py` (modified)
- `src/examai/templates/intern/tasks/detail.html` (modified)
- `src/examai/templates/intern/submissions/feedback.html` (new)
- `tests/test_intern_tasks.py` (modified)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)
- `_bmad-output/implementation-artifacts/3-3-view-published-feedback.md` (new)

### Change Log

- 2026-04-15 — Story 3.3: intern published feedback page; sprint status → review.

---

**Story completion status:** Implementation complete. **done.**
