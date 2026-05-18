# Story 4.9: Commit `patch` matching and source label

Status: done

## Story

As a **mentor**,  
I want **the commit API `files[].patch` to be preferred and visible in Source retrieval, with clear labeling when raw/contents are used instead**,  
so that **I see unified diffs when GitHub provides them and understand what was loaded**.

## Acceptance Criteria

1. **Patch first** — From the matching `files[]` row, use **`patch`** when non-empty; otherwise **`raw_url`**, then **`contents_url`**.

2. **Matching** — Resolve `files[]` when path scope matches GitHub’s `filename` (including suffix/basename rules and single-file commits).

3. **UI** — Source retrieval shows **retrieved as:** patch vs raw vs Contents API.

4. **Persistence** — `git_retrieved_source` stored on success; cleared on failure.

5. **README** — [README-Python.md](../../README-Python.md) updated.

## Tasks

- [x] `git_provider.py` — single-file commits resolve text from `files[0]` (`files[0].patch` per GitHub commit API).
- [x] `git_provider.py` — matching helpers, `GitFetchResult.source_kind`.
- [x] `submissions.git_retrieved_source` — Liquibase `002`, SQLAlchemy model.
- [x] Mentor fetch handler + `git-retrieval.html`.
- [x] Tests + `docs/data-models.md`.

---

**Story completion status:** Done.
