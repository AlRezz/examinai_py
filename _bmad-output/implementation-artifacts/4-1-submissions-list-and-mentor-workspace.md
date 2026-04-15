# Story 4.1: Submissions list and mentor workspace

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **mentor or administrator**,  
I want **to list submissions for a task and open a submission workspace**,  
so that **I can review intern work**.

## Acceptance Criteria

1. **Submissions list for task**  
   **Given** I am authenticated as mentor or administrator  
   **When** I `GET /tasks/{taskId}/submissions`  
   **Then** I see submissions for that task (**FR17**) — typically one row per assigned intern with a submission or placeholder state per data model.

2. **Mentor workspace**  
   **Given** submissions exist for the task  
   **When** I `GET /tasks/{taskId}/submissions/{internId}`  
   **Then** I see the **mentor submission workspace** (**FR18**) using **`tasks/submission-detail.html`** per **UX-DR1**.

3. **Templates / partials (foundation)**  
   **Then** workspace template can embed or prepare slots for **`tasks/fragments/git-retrieval.html`** and **`tasks/fragments/degraded-inference-banner.html`** (**UX-DR3**) even if full Git/AI behavior lands in later stories — structure the page so fragments attach without rework.

4. **Authorization**  
   **Then** routes under **`/tasks/**`** follow **FR5**; only mentor or administrator roles.

5. **Data**  
   **Then** reads use **`submissions`** (and related joins) per **[docs/data-models.md](../../docs/data-models.md)** (**FR28**).

## Tasks / Subtasks

- [ ] **Queries** (AC: 1, 2, 5)  
  - [ ] List submissions for `task_id`; load workspace for `(task_id, intern_user_id)`.  
  - [ ] Handle missing submission row (show empty state vs error — choose and document).

- [ ] **Routes** (AC: 1–4)  
  - [ ] `GET /tasks/{taskId}/submissions`, `GET /tasks/{taskId}/submissions/{internId}` per contract.

- [ ] **Templates** (AC: 2, 3)  
  - [ ] `tasks/submissions.html`, `tasks/submission-detail.html`; optional includes for Git/degraded fragments.

- [ ] **Tests**  
  - [ ] Mentor/admin access; intern denied; happy path with seeded DB/fixtures.

## Dev Notes

### Dependencies

- **`tasks`** and **`task_assignments`** (Epic 2); **`submissions`** rows may be created by intern flow (**Epic 3 Story 3.2**) or seeded for demo — workspace must tolerate evolving submission state.

### References

- [docs/api-contracts.md](../../docs/api-contracts.md) — `/tasks/{taskId}/submissions`  
- [docs/data-models.md](../../docs/data-models.md) — `submissions`  
- [docs/component-inventory.md](../../docs/component-inventory.md) — mentor task templates and fragments

### Previous story intelligence

- Reuse mentor/admin routing and layout from **`2-1-list-create-and-edit-tasks.md`**; add submission-specific context and intern user identity in the path.

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

---

**Story completion status:** Ultimate context engine analysis completed — comprehensive developer guide created. **ready-for-dev.**
