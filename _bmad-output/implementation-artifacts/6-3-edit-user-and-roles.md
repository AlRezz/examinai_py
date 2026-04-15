# Story 6.3: Edit user and roles

Status: in-progress

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

- [ ] **Repository** (AC: 1)  
  - [ ] `update_user_with_roles`: email/enabled/optional password/roles; duplicate-email check; at least one role; self-edit cannot disable own account or strip own administrator role.

- [ ] **Routes** (AC: 1, 3)  
  - [ ] `GET|POST /admin/users/{user_id}/edit` with CSRF on POST; flash + redirect on validation errors.

- [ ] **Templates** (AC: 2, 4)  
  - [ ] Extend `admin/user-form.html` for edit (optional password, pre-filled fields); `admin/users/list.html` links to edit.

- [ ] **Tests**  
  - [ ] Admin can edit user; non-admin denied; unknown user 404; duplicate email; CSRF; self-edit safeguards.

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

### File List

### Change Log

---

**Story completion status:** _In progress._
