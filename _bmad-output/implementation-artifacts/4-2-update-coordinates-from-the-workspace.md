# Story 4.2: Update coordinates from the workspace

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **mentor or administrator**,  
I want **to correct or enter coordinates from the mentor side**,  
so that **retrieval can proceed even if the intern made mistakes**.

## Acceptance Criteria

1. **POST coordinates**  
   **Given** I am on the workspace  
   **When** I `POST /tasks/{taskId}/submissions/{internId}/coordinates` with valid coordinates  
   **Then** submission coordinates update (or create) per **FR19** and **[docs/api-contracts.md](../../docs/api-contracts.md)**.

2. **Safety**  
   **Then** CSRF applies; task and intern-assignment checks match other mentor workspace POSTs.

3. **UI**  
   **Then** the workspace includes a labeled form for repository, optional commit SHA, and optional path scope (**UX-DR14** alignment).

## Tasks / Subtasks

- [x] **Route** (AC: 1–2)  
  - [x] `POST /tasks/{taskId}/submissions/{internId}/coordinates` with validation aligned to intern `POST /intern/tasks/{taskId}/submission`; persist via `upsert_intern_submission_coordinates`.

- [x] **Template** (AC: 3)  
  - [x] **`tasks/submission-detail.html`** — repository coordinates section with CSRF.

- [x] **Tests**  
  - [x] Create submission when none; update existing; empty-repo validation flash; intern forbidden on POST.

## Dev Notes

### Dependencies

- **Story 4.1:** Mentor workspace GET routes.  
- **Story 3.2:** `upsert_intern_submission_coordinates` in `intern_tasks_repo.py`.

### References

- [docs/api-contracts.md](../../docs/api-contracts.md)  
- [docs/data-models.md](../../docs/data-models.md) — `submissions`

## Dev Agent Record

### Agent Model Used

(implementation session)

### Debug Log References

### Completion Notes List

- Implemented `POST .../coordinates` in `mentor_workspace_routes.py` (same field limits as intern flow); extended `submission-detail.html` with coordinates form available even when no submission row exists (mentor can create). Tests in `tests/test_mentor_workspace_ai.py`. Full suite: 89 passed.

### File List

- `src/examai/mentor_workspace_routes.py` (modified)
- `src/examai/templates/tasks/submission-detail.html` (modified)
- `tests/test_mentor_workspace_ai.py` (modified)
- `_bmad-output/implementation-artifacts/4-2-update-coordinates-from-the-workspace.md` (new)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)

### Change Log

- 2026-04-15 — Story 4.2: mentor POST submission coordinates; sprint status → review.

---

**Story completion status:** Implementation complete. **review.**
