# Story 6.2: Create user with roles

Status: done

## Story

As an **administrator**,  
I want **to create a user and assign roles**,  
so that **new cohort members can sign in with correct access**.

## Acceptance Criteria

1. **Routes**  
   **Given** I am authenticated with the **administrator** role  
   **When** I `GET /admin/users/new` or `POST /admin/users/new`  
   **Then** the flow creates a user and **`user_roles`** rows per **FR26**, **FR28** and **[docs/data-models.md](../../docs/data-models.md)**.

2. **Form (UX)**  
   **Then** the new-user UI uses **`admin/user-form.html`** per **UX-DR1** and **[docs/component-inventory.md](../../docs/component-inventory.md)**.

3. **Authorization**  
   **Given** a non-admin authenticated user  
   **When** they request `/admin/users/new`  
   **Then** access is denied (**403**) — **FR5**.

4. **Safety**  
   **Then** responses never expose **`password_hash`** (**UX-DR11**).

## Tasks / Subtasks

- [x] **Repository** (AC: 1)  
  - [x] List assignable roles; create user with hashed password and role assignments.

- [x] **Routes** (AC: 1, 3)  
  - [x] `GET|POST /admin/users/new` with CSRF on POST; redirect + flash on validation errors.

- [x] **Template** (AC: 2, 4)  
  - [x] `admin/user-form.html`; link from user list.

- [x] **Tests**  
  - [x] Admin can create user with roles; non-admin denied; duplicate email handled.

## Dev Notes

### References

- [docs/api-contracts.md](../../docs/api-contracts.md)  
- [docs/data-models.md](../../docs/data-models.md)

### Previous story intelligence

- Follow **`tasks_routes.py`** CSRF + flash + redirect patterns; **`6-1-list-users`** admin shell.

## Dev Agent Record

### Agent Model Used

Composer (Cursor agent)

### Debug Log References

### Completion Notes List

- Added `list_roles_ordered` and `create_user_with_roles` in `users_repo` (bcrypt hash, duplicate email check, `IntegrityError` fallback, at least one role).
- `admin_routes`: `GET|POST /admin/users/new` with session CSRF validation; success redirects to `/admin/users` with flash.
- Template `admin/user-form.html` with role checkboxes; list page links to **New user**. HTML never includes password hashes (asserted in tests).

### File List

- `src/examai/users_repo.py`
- `src/examai/admin_routes.py`
- `src/examai/templates/admin/user-form.html`
- `src/examai/templates/admin/users/list.html`
- `tests/test_admin_users.py`
- `_bmad-output/implementation-artifacts/6-2-create-user-with-roles.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log

- 2026-04-15: Implemented admin create-user flow (Story 6.2).

---

**Story completion status:** Done (`done` in sprint-status).
