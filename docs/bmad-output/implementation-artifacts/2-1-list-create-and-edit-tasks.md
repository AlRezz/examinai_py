# Story 2.1: List, create, and edit tasks

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **mentor or administrator**,  
I want **to list tasks and create or edit a task**,  
so that **program work is defined in the system**.

## Acceptance Criteria

1. **Task list**  
   **Given** I am authenticated with **mentor** or **administrator** role  
   **When** I `GET /tasks`  
   **Then** I see a list of tasks (**FR13**) using templates aligned with **UX-DR1** (`tasks/list.html` per **[docs/component-inventory.md](../../docs/component-inventory.md)**).

2. **Create task**  
   **Given** I am authenticated as mentor or administrator  
   **When** I `GET /tasks/new` and submit `POST /tasks/new` with valid fields  
   **Then** a new row exists in **`tasks`** per **[docs/data-models.md](../../docs/data-models.md)** (**FR14**, **FR28**).

3. **Edit task**  
   **Given** a task exists  
   **When** I `GET /tasks/{id}/edit` and submit `POST /tasks/{id}/edit` with valid fields  
   **Then** the task updates persist (**FR15**, **FR28**).

4. **UX and forms**  
   **Then** mutating flows use **redirect-after-POST** or flash (**UX-DR10**) and show clear validation/permission errors (**UX-DR11**).  
   **And** templates use **`tasks/form.html`** (or equivalent) for create/edit per inventory.

5. **Authorization**  
   **Then** only users whose roles allow **`/tasks/**`** per **[docs/api-contracts.md](../../docs/api-contracts.md)** and architecture RBAC can access these routes; others receive **403** or safe redirect to login as established in Epic 1.

## Tasks / Subtasks

- [x] **Persistence** (AC: 2, 3)  
  - [x] SQLAlchemy models for **`tasks`** (and session wiring) per **[docs/data-models.md](../../docs/data-models.md)**.  
  - [x] Service or repository helpers for list/create/update with typed IDs (**UUID**).

- [x] **Routes** (AC: 1–5)  
  - [x] Implement `GET /tasks`, `GET|POST /tasks/new`, `GET|POST /tasks/{id}/edit` per contract paths and methods.  
  - [x] Enforce **mentor or administrator** dependency on these routes (**FR5**).

- [x] **Templates** (AC: 1, 4)  
  - [x] `tasks/list.html`, `tasks/form.html`; shared layout/fragments per **UX-DR1–UX-DR2**.  
  - [x] Forms include **CSRF** per Epic 1 convention (**UX-DR9**) if mutating templates ship with this story.

- [x] **Tests**  
  - [x] `TestClient` tests with authenticated mentor/admin fixture: list/create/edit happy path; forbidden for wrong role.

## Dev Notes

### Dependencies

- **Epic 1** should provide **session auth**, **RBAC** for `/tasks/**`, and **CSRF** on POSTs. Do not reimplement security primitives; align with existing middleware/dependencies in **`src/examai/`**.

### Architecture

- Implementation only under **`src/examai/`** ([_bmad-output/planning-artifacts/architecture.md](../../_bmad-output/planning-artifacts/architecture.md)).  
- **Pydantic** for form parsing where appropriate; **SQLAlchemy 2.x** style queries.

### References

- [docs/api-contracts.md](../../docs/api-contracts.md) — mentor/admin task routes  
- [docs/data-models.md](../../docs/data-models.md) — `tasks`  
- [docs/component-inventory.md](../../docs/component-inventory.md) — task templates  
- [_bmad-output/project-context.md](../../_bmad-output/project-context.md)

### Previous story intelligence

- **Epic 1 stories** establish static shell, health, login/session, RBAC, CSRF — extend those patterns; see **`1-1-*`**, **`1-3-*`**, **`1-4-*`**, **`1-5-*`** story files in this folder when present.

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

- Implemented `Task` ORM model (`tasks` table) and `tasks_repo` for list/create/update with UUID keys.
- Added `tasks_routes` APIRouter: `GET/POST /tasks/new`, `GET/POST /tasks/{id}/edit`, `GET /tasks`; CSRF on POSTs, redirect-after-POST with session flash; 404 for unknown task on edit GET.
- Templates: `templates/tasks/list.html`, `templates/tasks/form.html` with Bootstrap shell, CSRF fragment, logout.
- Tests: `tests/test_tasks_crud.py` (mentor/admin happy paths, intern 403, CSRF rejection, validation, DB row check).
- Post–CR 2-1: `_current_user` raises `HTTPException(401)` if session user id missing; POST handlers reject titles over 500 characters; `test_tasks_validation_title_too_long` added.

### File List

- `src/examai/models.py`
- `src/examai/tasks_repo.py`
- `src/examai/tasks_routes.py`
- `src/examai/main.py`
- `src/examai/templates/tasks/list.html`
- `src/examai/templates/tasks/form.html`
- `tests/test_tasks_crud.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log

- 2026-04-15: Story 2.1 — task list/create/edit for mentor/admin, persistence, tests, sprint status → review.
- 2026-04-15: Code review (CR 2-1) — findings recorded; status → in-progress until patch items closed.
- 2026-04-15: CR 2-1 patch items applied (`_current_user` guard, title max length + test); story → done.

### Review Findings

- [x] [Review][Patch] Replace `assert uid` in `_current_user` with an explicit session guard (avoid relying on `assert`, which is stripped under `python -O`) — [`tasks_routes.py`](../../src/examai/tasks_routes.py) — fixed
- [x] [Review][Patch] Enforce `title` length ≤ 500 on create/edit POST handlers to match `Task.title` and the form’s `maxlength` — [`tasks_routes.py`](../../src/examai/tasks_routes.py) — fixed
- [x] [Review][Defer] GET `/tasks/{id}/edit` with a non-UUID `id` returns 422 (validation) instead of the HTML error shell used for unknown tasks — optional UX consistency; deferred

---

**Story completion status:** done
