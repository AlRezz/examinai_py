# Story 4.8: Git fetch — optional path scope

Status: review

## Story

As a **mentor or administrator**,  
I want **path scope to remain optional on fetch** (validate only when provided),  
so that **I can load the repository root listing without entering a path**.

## Acceptance Criteria

1. **No mandatory path**  
   **Given** coordinates have a commit ref but **no** path scope (empty or unset)  
   **When** I run Git fetch  
   **Then** the app does **not** fail with `PATH_SCOPE_REQUIRED`.

2. **Empty path behavior**  
   **Then** the integration layer uses **GET /repos/{owner}/{repo}/contents?ref={ref}** (repository root) and does **not** require a `files[]` match from the commit API.

3. **Non-empty path unchanged**  
   **Given** path scope is set  
   **Then** behavior matches Story 4.7 (commit `GET` first, then patch / raw_url / contents_url / contents fallback).

4. **Docs**  
   **Then** [README-Python.md](../../README-Python.md) states that path scope is optional and describes empty vs non-empty behavior.

## Tasks / Subtasks

- [x] `integration/git_provider.py` — empty path → contents root only; remove `PATH_SCOPE_REQUIRED`.
- [x] `mentor_workspace_routes.py` — remove fetch-time path requirement.
- [x] Tests — replace path-required tests with empty-path contents test; mentor test removed.
- [x] README-Python.md updated.

## References

- Story **4.7** — commit-first resolution when path is set.

## Dev Agent Record

### File List

- `src/examai/integration/git_provider.py`
- `src/examai/mentor_workspace_routes.py`
- `tests/test_git_provider.py`
- `tests/test_mentor_workspace_ai.py`
- `README-Python.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

---

**Story completion status:** Implemented; pending review.
