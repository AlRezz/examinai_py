# Story 4.5: Publish review with snapshot metadata

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **mentor**,  
I want **to publish my review as the official outcome with snapshot fields**,  
so that **feedback is tied to evidence at publish time**.

## Acceptance Criteria

1. **POST publish-review + snapshots**  
   **Given** a draft exists (or equivalent mentor content via form/draft merge)  
   **When** I `POST /tasks/{taskId}/submissions/{internId}/publish-review`  
   **Then** `published_reviews` persists scores/narrative and **snapshot metadata** per **FR23**, **FR30** and **[docs/data-models.md](../../docs/data-models.md)** (`snapshot_commit_sha`, `snapshot_git_fetch_version`, `snapshot_path_scope` from the submission at publish time).

## Tasks / Subtasks

- [x] **Persistence** (AC: 1)  
  - [x] `upsert_published_review` — copy `submission.commit_sha`, `submission.git_fetch_version`, `submission.path_scope` into snapshot columns on insert/update.

- [x] **Route** (AC: 1)  
  - [x] `POST .../publish-review` — CSRF, assignment checks, merge form with saved draft, call `upsert_published_review`.

- [x] **Tests** (AC: 1)  
  - [x] Integration: after publish, `PublishedReview` row matches submission snapshot fields (commit, path scope, git fetch version).

## Dev Notes

### Dependencies

- **Stories 4.1–4.4:** Workspace, coordinates, Git fetch, mentor drafts.  
- **Models:** `PublishedReview` snapshot columns per **docs/data-models.md**.

### References

- [docs/api-contracts.md](../../docs/api-contracts.md)  
- [docs/data-models.md](../../docs/data-models.md)

## Dev Agent Record

### Agent Model Used

(implementation session)

### Debug Log References

### Completion Notes List

- Verified existing `POST .../publish-review` and `upsert_published_review` snapshot copy from `Submission`; extended `test_publish_review_persists_and_shows_flash` to assert all three snapshot fields (including non-null `git_fetch_version`). Full pytest suite run green.

### File List

- `tests/test_mentor_workspace_ai.py` (modified)
- `_bmad-output/implementation-artifacts/4-5-publish-review-with-snapshot-metadata.md` (new)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modified)

### Change Log

- 2026-04-15 — Story 4.5: documented publish + snapshot provenance; strengthened snapshot assertions; sprint status → review.

---

**Story completion status:** Implementation complete. **review.**
