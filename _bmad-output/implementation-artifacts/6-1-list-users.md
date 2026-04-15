# Story 6.1: List users

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **administrator**,  
I want **to list user accounts**,  
so that **I can manage cohort membership**.

## Acceptance Criteria

1. **Admin user list**  
   **Given** I am authenticated with the **administrator** role  
   **When** I `GET /admin/users`  
   **Then** I see a list of users (**FR25**) from **`users`** per **[docs/data-models.md](../../docs/data-models.md)**.

2. **Templates (UX)**  
   **Then** the page uses **`admin/users/list.html`** per **UX-DR1** and **[docs/component-inventory.md](../../docs/component-inventory.md)**.

3. **Authorization**  
   **Given** a non-admin authenticated user  
   **When** they request `GET /admin/users`  
   **Then** access is denied (**403** or redirect per Epic 1 policy) — **FR5** administrator-only **`/admin/**` space.

4. **Data presentation**  
   **Then** the list exposes safe fields (e.g. email, enabled, roles summary); **never** expose **`password_hash`** or secrets (**UX-DR11**, NFR).

## Tasks / Subtasks

- [x] **Route** (AC: 1, 3)  
  - [x] `GET /admin/users` with **administrator-only** dependency.

- [x] **Query** (AC: 1, 4)  
  - [x] List users with optional join to **`user_roles`** / **`roles`** for display.

- [x] **Template** (AC: 2)  
  - [x] `admin/users/list.html`; shared layout/fragments per inventory.

- [x] **Tests**  
  - [x] Admin sees list; mentor/intern denied.

## Dev Notes

### Dependencies

- **Epic 1:** Session auth + RBAC enforcing **`/admin/**`** for **`administrator`** role only.

### References

- [docs/api-contracts.md](../../docs/api-contracts.md) — administrator routes  
- [docs/data-models.md](../../docs/data-models.md) — `users`, `roles`, `user_roles`

### Previous story intelligence

- Align HTML table/list patterns with **`tasks/list.html`** from **`2-1-*`** for consistency; different RBAC dependency.

## Dev Agent Record

### Agent Model Used

Composer (Cursor agent)

### Debug Log References

### Completion Notes List

- Implemented `GET /admin/users` via `admin_routes` + `list_users_with_roles` (eager-loaded roles); RBAC remains in `SecurityMiddleware` (administrator-only for `/admin/**`).
- Template `admin/users/list.html` mirrors tasks list shell; shows email, enabled, sorted role names; no password hashes in HTML (asserted in tests).

### File List

- `src/examai/admin_routes.py` (new)
- `src/examai/main.py`
- `src/examai/users_repo.py`
- `src/examai/templates/admin/users/list.html` (new)
- `src/examai/templates/spaces/admin-users.html` (removed — superseded)
- `tests/test_auth_rbac.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

---

**Story completion status:** Done (`done` in sprint-status).
