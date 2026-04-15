# Story 5.1: Request AI draft with audit trail

Status: ready-for-dev

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

- [ ] **`integration/ai`** (AC: 2, 4)  
  - [ ] Ollama (or contract-aligned) client using **`OLLAMA_BASE_URL`** / env from **[docs/development-guide.md](../../docs/development-guide.md)** or deployment guide.

- [ ] **Persistence** (AC: 3)  
  - [ ] SQLAlchemy models for **`model_invocations`**, **`ai_drafts`**; transactional write after successful inference.

- [ ] **Route** (AC: 1, 5)  
  - [ ] `POST .../ai-draft-assessment` calls service layer; returns redirect/HTML with message per **UX-DR10**.

- [ ] **Tests**  
  - [ ] Mock httpx/Ollama for unit tests; optional integration test behind env flag.

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

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

---

**Story completion status:** Ultimate context engine analysis completed — comprehensive developer guide created. **ready-for-dev.**
