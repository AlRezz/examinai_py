# Story 4.7: Commit-first Git fetch (normalized text)

Status: review

## Story

As a **mentor or administrator**,  
I want **Git fetch to prefer commit metadata and per-file hints (patch / raw / contents URL) before the Contents API**,  
so that **review and AI prompts see diffs and accurate file text when GitHub exposes them**.

## Acceptance Criteria

1. **Commit primary**  
   **Given** Git integration is configured and coordinates include **path scope** and **ref**  
   **When** the app fetches normalized source  
   **Then** it calls **`GET /repos/{owner}/{repo}/commits/{ref}`** (``ref`` = SHA, branch, or tag) and reads **`files[]`**.

2. **Per-file resolution order**  
   **Given** a **`files[]`** row whose **`filename`** matches the path scope  
   **Then** normalized text is taken in order: **`patch`**, else HTTP **`raw_url`**, else **`contents_url`** (Contents JSON + base64), else **`GET /repos/{owner}/{repo}/contents/{path}?ref={ref}`**.

3. **Path scope**  
   **Then** when path scope is set, commit `files[]` resolution applies (see **Story 4.8** for optional empty path / repository root).

4. **Docs**  
   **Then** [README-Python.md](../../README-Python.md) describes this behavior.

## Tasks / Subtasks

- [x] **`integration/git_provider.py`** — commit GET, match `filename`, resolution chain, Contents fallback.
- [x] **Mentor `POST .../fetch`** — (Story 4.8: path optional; no `PATH_SCOPE_REQUIRED`.)
- [x] **Tests** — unit tests for provider; mentor tests for path scope / existing fetch flows.
- [x] **README-Python.md** — Git provider section updated.

## Dev Notes

- Builds on **Story 4.3** (fetch POST, `git_retrieval_*` persistence).
- GitHub REST: [Get a commit](https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#get-a-commit).

## Dev Agent Record

### Completion Notes List

- Commit-first fetch with `files[]` resolution order and Contents API fallback; path scope required at fetch time.

### File List

- `src/examai/integration/git_provider.py`
- `src/examai/mentor_workspace_routes.py`
- `tests/test_git_provider.py`
- `tests/test_mentor_workspace_ai.py`
- `README-Python.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/4-7-commit-first-git-fetch-normalized-text.md`

---

**Story completion status:** Implementation complete; pending review.
