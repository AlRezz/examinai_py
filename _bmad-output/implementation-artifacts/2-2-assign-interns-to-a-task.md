# Story 2.2: Assign interns to a task

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **mentor or administrator**,  
I want **to assign interns to a task**,  
so that **interns see the right assignments**.

## Acceptance Criteria

1. **Assignments page**  
   **Given** a task exists and I am authenticated as **mentor** or **administrator**  
   **When** I `GET /tasks/{id}/assignments`  
   **Then** I see a form to choose interns (users with the **intern** role) with current assignments reflected (**FR16**, **FR28**).

2. **Save assignments**  
   **Given** the same  
   **When** I `POST /tasks/{id}/assignments` with selected interns  
   **Then** **`task_assignments`** rows match the selection (**FR16**, **FR28**).

3. **Security and UX**  
   **Then** mutating POST uses **CSRF** (Epic 1) and **redirect-after-POST** with flash; only **mentor/admin** may access **`/tasks/**`** per RBAC.

4. **Validation**  
   **Then** assigning a user who is not an intern is rejected with a clear message; unknown task returns **404** on GET.

## Tasks / Subtasks

- [x] **Persistence** (AC: 2)  
  - [x] SQLAlchemy model **`task_assignments`** per **[docs/data-models.md](../../docs/data-models.md)** (composite key `task_id` + `intern_user_id`).  
  - [x] Repository helpers: list interns; read/set assignments for a task (replace set).

- [x] **Routes** (AC: 1–4)  
  - [x] `GET|POST /tasks/{id}/assignments` per **[docs/api-contracts.md](../../docs/api-contracts.md)**.  
  - [x] Enforce mentor/admin via existing **`/tasks`** RBAC (no bypass).

- [x] **Templates** (AC: 1)  
  - [x] `tasks/assign.html` (see **[docs/component-inventory.md](../../docs/component-inventory.md)**); link from task list.

- [x] **Tests**  
  - [x] `TestClient`: mentor saves assignments; intern 403; invalid non-intern rejected; GET 404 unknown task.

## Dev Notes

### Dependencies

- **Story 2.1** provides **`tasks`** and task routes; **Epic 1** provides session, RBAC, CSRF.

### References

- [docs/api-contracts.md](../../docs/api-contracts.md)  
- [docs/data-models.md](../../docs/data-models.md)  
- [_bmad-output/project-context.md](../../_bmad-output/project-context.md)

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

- Added **`TaskAssignment`** ORM model and **`task_assignments`** table; **`list_users_with_role`** on **`users_repo`**; **`task_assignments_repo`** for read/replace assignments.
- **`GET|POST /tasks/{task_id}/assignments`**: CSRF + redirect/flash; POST parses `intern_id` from form (supports empty selection); rejects non-intern user ids; invalid UUID strings flash and redirect (CR 2-2); async POST for reliable multipart/urlencoded duplicate keys.
- Template **`tasks/assign.html`**; task list **Assign** link beside **Edit**.
- Tests: **`tests/test_task_assignments.py`** (persist, clear, RBAC, validation, malformed id, admin save, 404, list link).

### File List

- `src/examai/models.py`
- `src/examai/users_repo.py`
- `src/examai/task_assignments_repo.py`
- `src/examai/tasks_routes.py`
- `src/examai/templates/tasks/assign.html`
- `src/examai/templates/tasks/list.html`
- `tests/test_task_assignments.py`
- `_bmad-output/implementation-artifacts/2-2-assign-interns-to-a-task.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log

- 2026-04-15: Story 2.2 — task intern assignments UI, persistence, tests; sprint status → review.
- 2026-04-16: CR 2-2 — POST rejects malformed `intern_id` with flash (no 500); tests for admin save + malformed id; story → done.

---

**Story completion status:** done
