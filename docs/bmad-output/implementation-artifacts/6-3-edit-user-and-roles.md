# Story 6.3: Edit user and roles

Status: done

## Story

As an **administrator**,  
I want **to edit an existing user**,  
so that **roles and details stay current**.

## Acceptance Criteria

1. **Routes**  
   **Given** I am authenticated with the **administrator** role and a user exists  
   **When** I `GET /admin/users/{id}/edit` or `POST /admin/users/{id}/edit`  
   **Then** updates persist to **`users`** and **`user_roles`** per **FR27**, **FR28** and **[docs/data-models.md](../../docs/data-models.md)**.

2. **Form (UX)**  
   **Then** the UI reuses **`admin/user-form.html`** per **UX-DR1** and **[docs/component-inventory.md](../../docs/component-inventory.md)** (edit vs. create distinguished by context).

3. **Authorization**  
   **Given** a non-admin authenticated user  
   **When** they request edit routes  
   **Then** access is denied (**403**) — **FR5**.

4. **Safety**  
   **Then** responses never expose **`password_hash`** (**UX-DR11**).

5. **Not found**  
   **Given** an id that does not match a user  
   **When** I `GET` the edit page  
   **Then** the server responds with **404**.

## Tasks / Subtasks

- [x] **Repository** (AC: 1)  
  - [x] `update_user_with_roles`: email/enabled/optional password/roles; duplicate-email check; at least one role; self-edit cannot disable own account or strip own administrator role.

- [x] **Routes** (AC: 1, 3)  
  - [x] `GET|POST /admin/users/{user_id}/edit` with CSRF on POST; flash + redirect on validation errors.

- [x] **Templates** (AC: 2, 4)  
  - [x] Extend `admin/user-form.html` for edit (optional password, pre-filled fields); `admin/users/list.html` links to edit.

- [x] **Tests**  
  - [x] Admin can edit user; non-admin denied; unknown user 404; duplicate email; CSRF; self-edit safeguards.

## Dev Notes

### References

- [docs/api-contracts.md](../../docs/api-contracts.md)  
- [docs/data-models.md](../../docs/data-models.md)

### Previous story intelligence

- Mirror **`6-2-create-user-with-roles`** patterns in `admin_routes` and `users_repo`; same CSRF and flash behavior.

## Dev Agent Record

### Agent Model Used

Composer (Cursor agent)

### Debug Log References

### Completion Notes List

- Added `update_user_with_roles` in `users_repo` (optional password change, role replacement, duplicate-email check excluding current user, at least one role, self-edit guards).
- `admin_routes`: `GET|POST /admin/users/{user_id}/edit` with CSRF; 404 when user missing; success redirects to `/admin/users` with flash.
- `admin/user-form.html` supports create and edit via `is_edit`, `selected_role_names`; list page **Edit** links.
- Tests cover edit flow, 403/404, duplicate email, CSRF, password hash unchanged when password blank, self-demote/disabled blocked.

### File List

- `src/examai/users_repo.py`
- `src/examai/admin_routes.py`
- `src/examai/templates/admin/user-form.html`
- `src/examai/templates/admin/users/list.html`
- `tests/test_admin_users.py`
- `_bmad-output/implementation-artifacts/6-3-edit-user-and-roles.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log

- 2026-04-15: Implemented admin edit-user flow (Story 6.3).

---

**Story completion status:** Done (`done` in sprint-status).
