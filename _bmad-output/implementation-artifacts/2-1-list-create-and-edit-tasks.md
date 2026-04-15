# Story 2.1: List, create, and edit tasks

Status: ready-for-dev

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

- [ ] **Persistence** (AC: 2, 3)  
  - [ ] SQLAlchemy models for **`tasks`** (and session wiring) per **[docs/data-models.md](../../docs/data-models.md)**.  
  - [ ] Service or repository helpers for list/create/update with typed IDs (**UUID**).

- [ ] **Routes** (AC: 1–5)  
  - [ ] Implement `GET /tasks`, `GET|POST /tasks/new`, `GET|POST /tasks/{id}/edit` per contract paths and methods.  
  - [ ] Enforce **mentor or administrator** dependency on these routes (**FR5**).

- [ ] **Templates** (AC: 1, 4)  
  - [ ] `tasks/list.html`, `tasks/form.html`; shared layout/fragments per **UX-DR1–UX-DR2**.  
  - [ ] Forms include **CSRF** per Epic 1 convention (**UX-DR9**) if mutating templates ship with this story.

- [ ] **Tests**  
  - [ ] `TestClient` tests with authenticated mentor/admin fixture: list/create/edit happy path; forbidden for wrong role.

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

### File List

---

**Story completion status:** Ultimate context engine analysis completed — comprehensive developer guide created. **ready-for-dev.**
