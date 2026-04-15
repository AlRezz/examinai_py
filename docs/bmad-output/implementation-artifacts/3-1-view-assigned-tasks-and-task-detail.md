# Story 3.1: View assigned tasks and task detail

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **intern**,  
I want **to list and open my assigned tasks**,  
so that **I know what work is required**.

## Acceptance Criteria

1. **Intern task list**  
   **Given** I am logged in as a user with the **intern** role and have **task_assignments**  
   **When** I `GET /intern/tasks`  
   **Then** I see only **my** assigned tasks (**FR7**) via **`task_assignments`** joined to **`tasks`** per **[docs/data-models.md](../../docs/data-models.md)**.

2. **Task detail**  
   **Given** I have an assignment for a task  
   **When** I `GET /intern/tasks/{taskId}`  
   **Then** I see task detail for that task (**FR8**) and cannot open tasks I am not assigned to (**safe 403/404** per product policy — document chosen behavior in code).

3. **Templates (UX)**  
   **Then** pages use **`intern/tasks/list.html`** and **`intern/tasks/detail.html`** per **UX-DR1**.

4. **Authorization**  
   **Then** only the **intern** role uses **`/intern/**`** routes per **[docs/api-contracts.md](../../docs/api-contracts.md)**; other roles are denied from intern-only pages.

## Tasks / Subtasks

- [x] **Queries** (AC: 1, 2)  
  - [x] List tasks for `current_user.id` through **`task_assignments`**.  
  - [x] Load task by ID with assignment check.

- [x] **Routes** (AC: 1–4)  
  - [x] `GET /intern/tasks`, `GET /intern/tasks/{taskId}` with intern-only dependency.

- [x] **Templates** (AC: 3)  
  - [x] Jinja2 templates under intern paths per **[docs/component-inventory.md](../../docs/component-inventory.md)**.

- [x] **Tests**  
  - [x] Intern sees assigned tasks; intern cannot access unassigned `taskId`; non-intern cannot access `/intern/tasks`.

## Dev Notes

### Dependencies

- **Epic 1:** Auth + RBAC for **`/intern/**` (**FR5**).  
- **Epic 2:** **`tasks`** and **`task_assignments`** populated so intern views have data (**FR28**).

### References

- [docs/api-contracts.md](../../docs/api-contracts.md) — intern routes  
- [docs/data-models.md](../../docs/data-models.md) — `tasks`, `task_assignments`  
- [docs/component-inventory.md](../../docs/component-inventory.md)

### Previous story intelligence

- Follow patterns from **`2-1-list-create-and-edit-tasks.md`** for task loading and UUID handling; intern scope is **assignment-filtered**.

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

- Implemented `intern_tasks_repo` (join `tasks` ↔ `task_assignments` for current intern), `intern_routes` with `GET /intern/tasks` and `GET /intern/tasks/{task_id}`, Jinja templates `intern/tasks/list.html` and `intern/tasks/detail.html`. Unassigned or unknown tasks return **404** with an inline policy comment (no distinction from missing tasks). RBAC for `/intern/**` remains in `SecurityMiddleware` (intern-only). Removed placeholder `/intern/tasks` from `main.py`. Added `tests/test_intern_tasks.py`. Full suite: 69 passed.

### File List

- `src/examai/intern_tasks_repo.py` (new)
- `src/examai/intern_routes.py` (new)
- `src/examai/main.py` (modified)
- `src/examai/templates/intern/tasks/list.html` (new)
- `src/examai/templates/intern/tasks/detail.html` (new)
- `tests/test_intern_tasks.py` (new)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)
- `_bmad-output/implementation-artifacts/3-1-view-assigned-tasks-and-task-detail.md` (modified)

### Change Log

- 2026-04-15 — Story 3.1: intern assigned task list and detail; 404 policy for non-assigned task IDs; tests and sprint status → review.

---

**Story completion status:** Implementation complete. **done.**
