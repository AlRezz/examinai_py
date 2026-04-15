# Story 4.4: Save mentor draft review

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **mentor**,  
I want **to save rubric scores and narrative as a draft**,  
so that **I can iterate before publishing**.

## Acceptance Criteria

1. **POST review-draft**  
   **Given** I am on the workspace  
   **When** I `POST /tasks/{taskId}/submissions/{internId}/review-draft`  
   **Then** `mentor_review_drafts` persists scores/narrative per **FR22** and **[docs/data-models.md](../../docs/data-models.md)**

## Tasks / Subtasks

- [x] **Route + persistence** (AC: 1)  
  - [x] `POST .../review-draft` — CSRF, submission/assignment checks, `upsert_mentor_review_draft` (quality/readability/correctness 1–5, narrative).

- [x] **Workspace UI** (AC: 1)  
  - [x] `tasks/submission-detail.html` — manual mentor form posts to `review-draft`; fields repopulate from saved draft.

- [x] **Tests**  
  - [x] Integration: manual save without AI; DB assertion on `mentor_review_drafts` row (scores, narrative, `mentor_user_id`).

## Dev Notes

### Dependencies

- **Stories 4.1–4.3:** Workspace, coordinates, Git fetch.  
- **Models:** `MentorReviewDraft` per **docs/data-models.md**.

### References

- [docs/api-contracts.md](../../docs/api-contracts.md)  
- [docs/data-models.md](../../docs/data-models.md)

## Dev Agent Record

### Agent Model Used

(implementation session)

### Debug Log References

### Completion Notes List

- Confirmed existing `POST .../review-draft` and `upsert_mentor_review_draft`; added `test_review_draft_post_persists_mentor_review_drafts_row` for explicit table-level AC coverage. Full pytest suite run green.

### File List

- `tests/test_mentor_workspace_ai.py` (modified)
- `_bmad-output/implementation-artifacts/4-4-save-mentor-draft-review.md` (new)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)

### Change Log

- 2026-04-15 — Story 4.4: documented save-draft flow; strengthened tests; sprint status → review.

---

**Story completion status:** Implementation complete. **review.**
