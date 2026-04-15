# Story 5.1: Request AI draft with audit trail

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **mentor**,  
I want **to request an AI draft assessment when the LLM is available**,  
so that **I get a starting point without losing accountability**.

## Acceptance Criteria

1. **Endpoint and role**  
   **Given** I am authenticated as mentor or administrator on the submission workspace  
   **When** I `POST /tasks/{taskId}/submissions/{internId}/ai-draft-assessment`  
   **Then** the request is accepted only for authorized roles on **`/tasks/**`** (**FR21**, **FR5**).

2. **Integration boundary**  
   **Given** Ollama (or configured LLM base URL) is available  
   **When** inference completes successfully  
   **Then** the HTTP/client logic runs in a **dedicated integration module** (e.g. `examai.integration.ai`), **not** inlined in the route handler ([_bmad-output/planning-artifacts/architecture.md](../../_bmad-output/planning-artifacts/architecture.md), [_bmad-output/project-context.md](../../_bmad-output/project-context.md)).

3. **Audit persistence**  
   **When** a successful run produces draft text  
   **Then** rows exist in **`model_invocations`** and **`ai_drafts`** per **[docs/data-models.md](../../docs/data-models.md)** (**FR32**, **FR28**): prompt hash, model metadata, link from draft to invocation.

4. **Timeouts and safety**  
   **Then** external calls use **httpx** with **bounded timeouts/retries**; no secrets or raw env contents in prompts (NFR / project-context AI rules).

5. **Workspace surfacing**  
   **Then** successful draft content is visible in the mentor workspace UI in a way that fits **UX-DR3** / **UX-DR12** (explicit state, not silent failure). Full **degraded** UX when LLM is down is refined in **Story 5.2**.

## Tasks / Subtasks

- [x] **`integration/ai`** (AC: 2, 4)  
  - [x] Ollama (or contract-aligned) client using **`OLLAMA_BASE_URL`** / env from **[docs/development-guide.md](../../docs/development-guide.md)** or deployment guide.

- [x] **Persistence** (AC: 3)  
  - [x] SQLAlchemy models for **`model_invocations`**, **`ai_drafts`**; transactional write after successful inference.

- [x] **Route** (AC: 1, 5)  
  - [x] `POST .../ai-draft-assessment` calls service layer; returns redirect/HTML with message per **UX-DR10**.

- [x] **Tests**  
  - [x] Mock httpx/Ollama for unit tests; optional integration test behind env flag.

## Dev Notes

### Dependencies

- **Story 4.1** workspace route must exist; **submission** row required to attach invocation.  
- **Epic 1** CSRF on POST.

### References

- [docs/api-contracts.md](../../docs/api-contracts.md) — external integration note + mentor routes  
- [docs/data-models.md](../../docs/data-models.md) — `model_invocations`, `ai_drafts`

### Previous story intelligence

- **`4-1-submissions-list-and-mentor-workspace.md`** defines the workspace surface; add POST handler and partials for AI result state.

## Dev Agent Record

### Agent Model Used

Composer (Cursor agent)

### Debug Log References

### Completion Notes List

- Added `examai.integration.ai` with `ollama_generate()` (httpx, timeouts, limited retries on transport errors).
- Extended SQLAlchemy models and `POST /tasks/{taskId}/submissions/{internId}/ai-draft-assessment` with CSRF; persists `model_invocations` + `ai_drafts` after successful inference.
- Implemented mentor workspace GET routes (`/tasks/.../submissions`, `/tasks/.../submissions/{internId}`) so the AI result can be shown on the page.
- Settings: `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT_SECONDS`, `OLLAMA_MAX_RETRIES`.

### File List

- `src/examai/integration/__init__.py`
- `src/examai/integration/ai.py`
- `src/examai/config.py`
- `src/examai/models.py`
- `src/examai/mentor_workspace_repo.py`
- `src/examai/mentor_workspace_routes.py`
- `src/examai/main.py`
- `src/examai/templates/tasks/submissions.html`
- `src/examai/templates/tasks/submission-detail.html`
- `src/examai/templates/tasks/fragments/git-retrieval.html`
- `src/examai/templates/tasks/list.html`
- `tests/test_mentor_workspace_ai.py`

### Change Log

- 2026-04-16: Story 5.1 — Ollama integration module, audit tables, mentor workspace + AI POST, tests; status → review.
- 2026-04-15: Review patches — `ollama_generate` failure tests, long-error flash truncation (`_shorten_for_flash`).

### Review Findings

- [x] [Review][Defer] Mentor workspace does not verify the current user is assigned as mentor for the task (only `/tasks` RBAC + intern assignment) — deferred, product scope [`src/examai/mentor_workspace_routes.py`]
- [x] [Review][Patch] Add test: mock `ollama_generate` raising `OllamaClientError` — expect warning flash, no `model_invocations` / `ai_drafts` rows, workspace still 200 [`tests/test_mentor_workspace_ai.py`]
- [x] [Review][Patch] Optionally truncate or summarize AI error text in session flash after Ollama failures (avoid very long upstream bodies in UI) [`src/examai/mentor_workspace_routes.py` ~240–243]

---

**Story completion status:** **done** (review patches applied 2026-04-15).
