# Story 4.3: Trigger Git fetch with visible state

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **mentor or administrator**,  
I want **to fetch normalized source and see success, failure, or in-progress state**,  
so that **I review real code, not stale guesses**.

## Acceptance Criteria

1. **POST fetch**  
   **Given** Git integration is configured  
   **When** I `POST /tasks/{taskId}/submissions/{internId}/fetch`  
   **Then** `git_retrieval_*` fields update per **FR20**, **FR29**, **FR31** (integration layer outside route handler).

2. **UI**  
   **Then** the workspace shows retrieval UI per **UX-DR3**, **UX-DR12** (explicit states, no silent hang).

3. **Safety**  
   **Then** CSRF applies; task and intern-assignment checks match other mentor workspace POSTs.

## Tasks / Subtasks

- [x] **Config** (AC: 1)  
  - [x] `GIT_PROVIDER_BASE_URL`, `GIT_PROVIDER_TOKEN`, optional `GIT_PROVIDER_TIMEOUT_SECONDS` on `Settings`.

- [x] **Integration** (AC: 1, FR31)  
  - [x] `integration/git_provider.py` — httpx client, `parse_repo_identifier`, `fetch_repository_contents` (GitHub REST v3 contents API).

- [x] **Route** (AC: 1, 3)  
  - [x] `POST .../fetch` — set `fetching` then terminal state; flash messages; persist `git_retrieved_text`, `git_fetch_version`, timestamps.

- [x] **Template** (AC: 2)  
  - [x] `tasks/fragments/git-retrieval.html` — badge, form, error code, retrieved text preview; degraded banner when provider not configured.

- [x] **Tests**  
  - [x] Unit: `tests/test_git_provider.py`; integration: `tests/test_mentor_workspace_ai.py` (success, not configured, missing commit, provider error).

## Dev Notes

### Dependencies

- **Story 4.2:** Coordinates and submission row.  
- **Models:** `Submission` git columns per **docs/data-models.md**.

### References

- [docs/api-contracts.md](../../docs/api-contracts.md)  
- [docs/architecture.md](../../_bmad-output/planning-artifacts/architecture.md) — integration/git

## Dev Agent Record

### Agent Model Used

(implementation session)

### Debug Log References

### Completion Notes List

- Added Git provider settings and `examai.integration.git_provider` (GitHub REST contents fetch). Mentor `POST .../fetch` updates `git_retrieval_*`, `git_fetch_version`, flash + `git-retrieval.html` UX. Full suite: 102 passed.

### File List

- `src/examai/config.py` (modified)
- `src/examai/integration/git_provider.py` (new)
- `src/examai/mentor_workspace_routes.py` (modified)
- `src/examai/templates/tasks/submission-detail.html` (modified)
- `src/examai/templates/tasks/fragments/git-retrieval.html` (modified)
- `tests/test_git_provider.py` (new)
- `tests/test_mentor_workspace_ai.py` (modified)
- `_bmad-output/implementation-artifacts/4-3-trigger-git-fetch-with-visible-state.md` (new)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)

### Change Log

- 2026-04-15 — Story 4.3: Git fetch POST, integration layer, workspace retrieval UI; sprint status → review.

---

**Story completion status:** Implementation complete. **review.**
