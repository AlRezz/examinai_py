# Story 4.1: Submissions list and mentor workspace

Status: review

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

- [x] **Queries** (AC: 1, 2, 5)  
  - [x] List submissions for `task_id`; load workspace for `(task_id, intern_user_id)`.  
  - [x] Handle missing submission row (show empty state vs error — choose and document).

- [x] **Routes** (AC: 1–4)  
  - [x] `GET /tasks/{taskId}/submissions`, `GET /tasks/{taskId}/submissions/{internId}` per contract.

- [x] **Templates** (AC: 2, 3)  
  - [x] `tasks/submissions.html`, `tasks/submission-detail.html`; optional includes for Git/degraded fragments.

- [x] **Tests**  
  - [x] Mentor/admin access; intern denied; happy path with seeded DB/fixtures.

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

Composer (Cursor agent)

### Debug Log References

### Completion Notes List

- Verified existing implementation: `mentor_workspace_repo.list_intern_submissions_for_task` (left join assignment → submission), `get_submission_for_pair`, workspace template `tasks/submission-detail.html` with empty state when no submission row; fragments `tasks/fragments/git-retrieval.html` and `tasks/fragments/degraded-inference-banner.html` included per UX-DR3.
- RBAC: `rbac.required_roles_for_path` restricts `/tasks/**` to mentor or administrator; `SecurityMiddleware` enforces before handlers.
- Added tests: intern receives 403 on submissions list and workspace URLs; administrator can open list and workspace (`tests/test_mentor_workspace_ai.py`).

### File List

- `tests/test_mentor_workspace_ai.py` (Story 4.1 RBAC coverage)

---

**Story completion status:** **review** — ACs satisfied; full suite `85 passed` (2026-04-15).
