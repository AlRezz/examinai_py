# Story 4.6: Mentor review queue

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **mentor**,  
I want **a queue of outstanding review work**,  
so that **I can triage workload**.

## Acceptance Criteria

1. **GET /review/queue**  
   **Given** I am a mentor (or administrator per RBAC)  
   **When** I `GET /review/queue`  
   **Then** I see the queue view per **FR24** and **UX-DR1** (`review/queue.html`) listing assigned (task, intern) pairs **without** a published review, with links into the mentor workspace and task submissions.

## Tasks / Subtasks

- [x] **Data** (AC: 1)  
  - [x] Query outstanding items: `task_assignments` joined with tasks and interns, `submissions` and `published_reviews` such that `published_reviews` is absent (includes “awaiting submission” and “in review”).

- [x] **Route + template** (AC: 1)  
  - [x] `GET /review/queue` on mentor workspace router; render `review/queue.html` with nav consistent with other mentor pages.  
  - [x] Remove obsolete placeholder from `main.py` / `spaces/review-queue.html`.

- [x] **Tests** (AC: 1)  
  - [x] Mentor sees queue rows; published-only pairs excluded; awaiting submission shown; intern receives 403.

## Dev Notes

### Dependencies

- **Stories 4.1–4.5:** Submissions list, workspace, publish flow.  
- **RBAC:** `/review/**` — mentor or administrator (`rbac.py`).

### References

- [docs/api-contracts.md](../../docs/api-contracts.md)  
- [docs/data-models.md](../../docs/data-models.md)

## Dev Agent Record

### Agent Model Used

(implementation session)

### Debug Log References

### Completion Notes List

- Implemented `list_outstanding_review_queue` / `ReviewQueueRow` in `mentor_workspace_repo.py`.  
- Added `GET /review/queue` to `mentor_workspace_routes.py`; template `review/queue.html`.  
- Tests in `tests/test_review_queue.py`; full suite 107 passed.

### File List

- `src/examai/mentor_workspace_repo.py`  
- `src/examai/mentor_workspace_routes.py`  
- `src/examai/main.py`  
- `src/examai/templates/review/queue.html`  
- `src/examai/templates/spaces/review-queue.html` (deleted)  
- `tests/test_review_queue.py`  
- `_bmad-output/implementation-artifacts/4-6-mentor-review-queue.md`  
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log

- 2026-04-15 — Story 4.6: mentor review queue (FR24, `review/queue.html`).

---

**Story completion status:** Implementation complete. **done.**
