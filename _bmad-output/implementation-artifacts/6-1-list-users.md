# Story 6.1: List users

Status: ready-for-dev

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

- [ ] **Route** (AC: 1, 3)  
  - [ ] `GET /admin/users` with **administrator-only** dependency.

- [ ] **Query** (AC: 1, 4)  
  - [ ] List users with optional join to **`user_roles`** / **`roles`** for display.

- [ ] **Template** (AC: 2)  
  - [ ] `admin/users/list.html`; shared layout/fragments per inventory.

- [ ] **Tests**  
  - [ ] Admin sees list; mentor/intern denied.

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

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

---

**Story completion status:** Ultimate context engine analysis completed — comprehensive developer guide created. **ready-for-dev.**
