# Story 3.2: Submit or update submission coordinates

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **intern**,  
I want **to submit or update repo, commit, and path scope for my task**,  
so that **mentors can retrieve my work**.

## Acceptance Criteria

1. **Upsert coordinates**  
   **Given** I have an assigned task  
   **When** I `POST /intern/tasks/{taskId}/submission` with valid coordinates  
   **Then** a `submissions` row exists or updates per **[docs/data-models.md](../../docs/data-models.md)** (**FR9**, **FR28–FR29**).

2. **Contract and safety**  
   **Then** the route matches **[docs/api-contracts.md](../../docs/api-contracts.md)**; CSRF applies to POST; unassigned `taskId` yields the same **404** policy as task detail.

3. **UI**  
   **Then** task detail includes a form with labeled fields for repository, optional commit SHA, and optional path scope (**UX-DR14** alignment).

## Tasks / Subtasks

- [x] **Persistence** (AC: 1)  
  - [x] Load existing submission for `(task_id, intern_user_id)`; upsert `repo_identifier`, `commit_sha`, `path_scope`.

- [x] **Route** (AC: 1–2)  
  - [x] `POST /intern/tasks/{taskId}/submission` with intern-only access and assignment check.

- [x] **Template** (AC: 3)  
  - [x] Extend **`intern/tasks/detail.html`** with coordinate form and CSRF.

- [x] **Tests**  
  - [x] Create + update row; 404 when not assigned; bad CSRF; non-intern forbidden.

## Dev Notes

### Dependencies

- **Story 3.1:** Intern task detail and assignment checks.  
- **Epic 2:** Tasks and assignments exist.

### References

- [docs/api-contracts.md](../../docs/api-contracts.md)  
- [docs/data-models.md](../../docs/data-models.md) — `submissions`

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

- Added `get_submission_for_intern_pair` and `upsert_intern_submission_coordinates` in `intern_tasks_repo.py`; `POST /intern/tasks/{task_id}/submission` in `intern_routes.py` with validation and CSRF; task detail form in `intern/tasks/detail.html`. Tests in `tests/test_intern_tasks.py`. Full suite: 73 passed.

### File List

- `src/examai/intern_tasks_repo.py` (modified)
- `src/examai/intern_routes.py` (modified)
- `src/examai/templates/intern/tasks/detail.html` (modified)
- `tests/test_intern_tasks.py` (modified)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)
- `_bmad-output/implementation-artifacts/3-2-submit-or-update-submission-coordinates.md` (new)

### Change Log

- 2026-04-15 — Story 3.2: intern POST submission coordinates; sprint status → review.

---

**Story completion status:** Implementation complete. **review.**
