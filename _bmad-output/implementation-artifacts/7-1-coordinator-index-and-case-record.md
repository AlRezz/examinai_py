# Story 7.1: Coordinator index and case record

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **coordinator**,  
I want **an index and a case record for a submission**,  
so that **I can spot stuck work without mentor tools**.

## Acceptance Criteria

1. **Coordinator index**  
   **Given** I am logged in with the **coordinator** role  
   **When** I `GET /coordinator`  
   **Then** I see a coordinator-scoped index (**FR11**) appropriate for oversight (e.g. submissions/cases summary — align fields to **`submissions`** and related entities per **[docs/data-models.md](../../docs/data-models.md)**).

2. **Case record**  
   **Given** a submission exists  
   **When** I `GET /coordinator/cases/{submissionId}`  
   **Then** I see a **case record** view for that submission (**FR12**) without exposing mentor-only write actions unless explicitly in scope for coordinators (default: **read-only** oversight).

3. **Templates (UX)**  
   **Then** templates follow **`coordinator/index.html`** and **`coordinator/case-record.html`** per **UX-DR1** and **[docs/component-inventory.md](../../docs/component-inventory.md)**.

4. **Authorization**  
   **Then** only **`/coordinator/**`** is used by coordinator role per **[docs/api-contracts.md](../../docs/api-contracts.md)**; mentors/admins/interns are denied coordinator pages (**FR5**).

5. **Data boundaries**  
   **Then** coordinator views show only data appropriate for oversight (no unnecessary PII expansion beyond product policy; follow role boundaries from architecture).

## Tasks / Subtasks

- [x] **Routes** (AC: 1, 2, 4)  
  - [x] `GET /coordinator`, `GET /coordinator/cases/{submissionId}` with **coordinator-only** dependency.

- [x] **Queries** (AC: 1, 2, 5)  
  - [x] Index query across submissions (and joins as needed); single submission case record with task/intern context.

- [x] **Templates** (AC: 3)  
  - [x] `coordinator/index.html`, `coordinator/case-record.html`.

- [x] **Tests**  
  - [x] Coordinator can access both routes; non-coordinator denied; invalid `submissionId` handled safely.

## Dev Notes

### Dependencies

- **Epic 1:** Auth + RBAC for **`/coordinator/**`.  
- **`submissions`** (and tasks/users for labels) from earlier epics — case record requires real IDs.

### References

- [docs/api-contracts.md](../../docs/api-contracts.md) — coordinator routes  
- [docs/data-models.md](../../docs/data-models.md) — `submissions`, related tables

### Previous story intelligence

- Read-only, oversight-focused — mirror list/detail patterns from **`3-1-*`** (intern) and **`4-1-*`** (mentor) but **no** mentor workspace POST actions.

## Dev Agent Record

### Agent Model Used

Cursor agent (implementation session)

### Debug Log References

### Completion Notes List

- Added SQLAlchemy `Submission` model (`submissions` table) per data-models (unique task+intern pair, repo/status fields).
- New `coordinator_repo` list + case lookups joining `submissions`, `tasks`, `users`.
- `coordinator_routes` serves Jinja templates under `coordinator/`; removed obsolete `spaces/coordinator-index.html` placeholder.
- Tests cover coordinator success paths, mentor/intern 403 on `/coordinator`, 404 missing case, 422 invalid UUID path.

### File List

- `src/examai/models.py`
- `src/examai/coordinator_repo.py`
- `src/examai/coordinator_routes.py`
- `src/examai/main.py`
- `src/examai/templates/coordinator/index.html`
- `src/examai/templates/coordinator/case-record.html`
- `tests/test_coordinator.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (story status)
- `src/examai/templates/spaces/coordinator-index.html` (deleted)

## Change Log

- 2026-04-16: Implemented coordinator index and case record (Story 7.1); submission model + integration tests.

---

**Story completion status:** Implementation complete; **review**.
