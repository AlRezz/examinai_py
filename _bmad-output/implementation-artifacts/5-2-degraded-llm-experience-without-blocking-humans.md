# Story 5.2: Degraded LLM experience without blocking humans

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **mentor**,  
I want **clear degraded messaging and an obvious human-only path when the LLM fails**,  
so that **I can still publish without waiting for AI**.

## Acceptance Criteria

1. **Degraded visibility**  
   **Given** Ollama is down, misconfigured, or times out  
   **When** I use the workspace  
   **Then** degraded state is visible (**FR32**, **UX-DR12**, **UX-DR13**).

2. **Human path**  
   **Then** draft save and publish remain usable (**FR22–FR23**) without depending on AI.

## Tasks / Subtasks

- [x] **Workspace banner** (AC: 1)  
  - [x] `tasks/fragments/degraded-inference-banner.html` when Ollama is not configured or the last AI request failed; flash messaging distinguishes success vs failure.

- [x] **Non-blocking POST behavior** (AC: 1–2)  
  - [x] `POST .../ai-draft-assessment` surfaces errors via redirect + flash; no uncaught exceptions; manual review and publish forms stay available.

- [x] **Manual review + publish** (AC: 2)  
  - [x] `POST .../review-draft` and `POST .../publish-review` persist mentor work independently of LLM (minimal rubric + narrative per data-models).

- [x] **Tests**  
  - [x] Degraded/unconfigured Ollama skips httpx client; manual draft save without `OLLAMA_BASE_URL`.

## Dev Notes

### References

- [docs/api-contracts.md](../../docs/api-contracts.md)  
- [docs/data-models.md](../../docs/data-models.md) — `mentor_review_drafts`, `published_reviews`

### Previous story intelligence

- **5.1** adds Ollama integration and audit tables; **5.2** focuses on UX when integration is absent or failing.

## Dev Agent Record

### Agent Model Used

Composer (Cursor agent)

### Debug Log References

### Completion Notes List

- Implemented degraded banner and flash-based failure signaling on the mentor submission workspace; Ollama client is not invoked when `OLLAMA_BASE_URL` is unset.
- Wired minimal mentor draft save and publish so human workflows work without AI.

### File List

- `src/examai/templates/tasks/fragments/degraded-inference-banner.html`
- `src/examai/templates/tasks/submission-detail.html` (banner + manual sections)
- `src/examai/mentor_workspace_routes.py` (POST handlers, flash messages)
- `tests/test_mentor_workspace_ai.py`

---

**Story completion status:** Implementation complete — **review**.
