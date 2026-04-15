# Story 9.1: AI draft rubric, mentor draft fill-in, publish UX

Status: done

## Story

As a **mentor**,  
I want **the AI draft to return Quality, Readability, and Correctness (1–5) plus feedback sections, and to have that parsed into the mentor review draft**,  
so that **the workspace rubric and narrative are pre-filled and I can publish from one place**.

## Acceptance Criteria

1. **Structured LLM output** — The AI assessment prompt instructs the model to emit scores (1–5) and sections **Feedback on the code** / **Suggestions to improve**, using retrieved source when available.
2. **Parsing** — Server parses model output for audit (full text unchanged in `ai_drafts`) and for mentor fields (`mentor_review_drafts`): scores + combined narrative from the two sections (with sensible fallback when headings are missing).
3. **Persistence** — On successful `POST .../ai-draft-assessment`, persist `model_invocations` / `ai_drafts` as today and upsert `mentor_review_drafts` with parsed values for the current user.
4. **Workspace UI** — Mentor review section is not labeled “manual”; it includes **Publish review** (same behavior as publish endpoint). **Publish status** section is reduced (no duplicate full rubric form; optional **Publish saved draft**).

## Tasks / Subtasks

- [x] Extend `_build_ai_prompt` with code context and structured output instructions.
- [x] Add `examai.ai_assessment_parsing.parse_ai_assessment_output`.
- [x] Wire AI draft POST to `upsert_mentor_review_draft`; accept `narrative_feedback` on publish for mentor form compatibility.
- [x] Update `submission-detail.html`; tests for parsing, AI→draft, publish alias.

## Dev Agent Record

### File List

- `src/examai/ai_assessment_parsing.py`
- `src/examai/mentor_workspace_routes.py`
- `src/examai/templates/tasks/submission-detail.html`
- `tests/test_ai_assessment_parsing.py`
- `tests/test_mentor_workspace_ai.py`

### Completion Notes

- Full model response remains stored in `ai_drafts.assessment_text` for audit.
- `POST .../publish-review` accepts optional `narrative_feedback` when `narrative` is empty (mentor workspace form).

**Story completion status:** done (2026-04-15).
