# Story 10.1: Mentor workspace structured layout (UX Phase 1)

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **mentor or administrator**,  
I want **the submission workspace to follow the structured UX layout (evidence card, status-first hierarchy, two-column source + draft, calm degraded LLM messaging)**,  
so that **I can fetch source, draft, optionally use AI, and publish without cognitive overload—and without blocking publish when integrations degrade**.

## Acceptance Criteria

1. **Page structure (Direction 2)** — `GET /tasks/{taskId}/submissions/{internId}` renders `tasks/submission-detail.html` with this vertical order:
   - Flash alerts (existing behavior preserved).
   - **Degraded LLM banner** (fragment) when applicable.
   - **Evidence card** (new fragment): repo, commit SHA, path scope in monospace; **submission lifecycle badge**; inline coordinate edit form (same POST as today); fetch status summary when a submission row exists.
   - **Two-column workspace** (`row`, `col-lg-5` / `col-lg-7`, stack below `lg`): left = source retrieval + preview; right = draft review panel + AI draft block.
   - **Publish status** footer remains but is visually de-emphasized (`text-muted`, no duplicate primary CTA).

2. **Evidence card fragment** — New `tasks/fragments/evidence-card.html`:
   - Card header **Evidence** with provenance fields grouped.
   - Monospace styling for repo / SHA / scope (Bootstrap `font-monospace` or `.examai-provenance` in theme CSS).
   - Includes lifecycle badge and coordinate form (move from flat page sections—no behavior change to POST endpoints).
   - When no submission row: instructional empty state pointing to saving coordinates (same as today).

3. **Lifecycle badge on mentor workspace** — Mentor workspace shows a lifecycle badge using server-side mapping (extend `submission_lifecycle.py` or add `mentor_submission_lifecycle_badge`):
   - States aligned with UX spec: **not submitted**, **coordinates saved**, **retrieving source…**, **source retrieval failed**, **ready for review** (fetch OK, not published), **draft saved** (mentor draft exists, not published), **published**.
   - Badge uses text labels (not color-only); reuse `intern/fragments/submission-lifecycle-badge.html` macro/include with shared `submission_lifecycle` view model.
   - Route passes `submission_lifecycle` in template context from `mentor_workspace_routes.submission_workspace`.

4. **Degraded LLM banner (UX consistency)** — `tasks/fragments/degraded-inference-banner.html`:
   - Use Bootstrap **`alert-info`** (not `alert-warning`) per UX spec § Feedback Patterns.
   - Copy preserves mentor agency (“you can still publish a human-only review”).
   - `aria-live="polite"` on the banner container.

5. **Git retrieval fragment enhancements** — `tasks/fragments/git-retrieval.html`:
   - Failed fetch badge uses **`bg-warning text-dark`** (retryable), not `bg-danger`, unless auth/permission errors warrant danger (document choice in Dev Agent Record if split).
   - Source preview panel: empty state copy **“Fetch source to preview code here.”** when no `git_retrieved_text`.
   - Status region after fetch: `aria-live="polite"` on the badge/status area.
   - **Primary CTA rule:** **Fetch source** is `btn-primary` only when source not yet successfully retrieved; otherwise outline/secondary.

6. **Draft review panel** — New `tasks/fragments/mentor-draft-panel.html` (or equivalent):
   - Header **Draft review** with **`badge bg-secondary`** “Draft — not published” when no published review.
   - Rubric fields + narrative unchanged (same field names for POST compatibility).
   - **One primary** per panel: **Publish review** (`btn-success` or `btn-primary` per button hierarchy—Publish is primary on workspace); **Save draft** is `btn-outline-secondary`.
   - Remove misleading “manual” framing; keep AI pre-fill explanation concise.

7. **AI draft block** — Refactor AI section into `tasks/fragments/ai-draft-block.html`:
   - Labeled panel: **“AI draft — not published”** (bordered card or `alert-secondary`).
   - **Request AI draft** stays `btn-outline-secondary` (secondary action).
   - Audit metadata line (model, timestamp) preserved from current template.
   - Does not auto-publish; no new endpoints.

8. **Theme tokens** — `src/examai/static/css/examai-theme.css`:
   - Add semantic classes: `.examai-evidence-card`, `.examai-draft-panel`, `.examai-provenance` (monospace + light background).
   - Evidence card border accent per Direction 2 (`border-primary border-opacity-25` or theme equivalent).

9. **No regressions** — All existing workspace POST routes unchanged (`coordinates`, `fetch`, `ai-draft-assessment`, `review-draft`, `publish-review`). CSRF, RBAC, flash messages, and Epic 5/9 AI→draft parsing behavior preserved.

10. **Tests** — Extend or add tests:
    - Mentor workspace HTML includes Evidence card, lifecycle badge, and two-column layout markers (`col-lg-5`, `col-lg-7`).
    - Degraded banner renders `alert-info` when `degraded_inference` is true.
    - Unit tests for mentor lifecycle mapping (published wins; fetch failed; draft saved; ready for review).
    - Existing `tests/test_mentor_workspace_ai.py` (and related) still pass.

## Tasks / Subtasks

- [x] **Lifecycle mapping** (AC: 3, 10)
  - [x] Add `mentor_submission_lifecycle_badge(...)` in `submission_lifecycle.py` (inputs: submission, has_published, has_mentor_draft).
  - [x] Pass `submission_lifecycle` from `submission_workspace` handler.

- [x] **Fragments** (AC: 2, 4, 5, 6, 7)
  - [x] Create `evidence-card.html`, `mentor-draft-panel.html`, `ai-draft-block.html`.
  - [x] Update `degraded-inference-banner.html`, `git-retrieval.html`.
  - [x] Refactor `submission-detail.html` to structured layout.

- [x] **Theme** (AC: 8)
  - [x] Extend `examai-theme.css` with semantic classes.

- [x] **Tests** (AC: 10)
  - [x] `tests/test_submission_lifecycle.py` — mentor variants.
  - [x] Workspace HTML assertions in mentor workspace tests.

### Review Findings

- [x] [Review][Patch] Enter key in draft score fields can publish instead of save [`src/examai/templates/tasks/fragments/mentor-draft-panel.html`:29]
- [x] [Review][Patch] Git failure badges classify auth and permission errors inconsistently [`src/examai/templates/tasks/fragments/git-retrieval.html`:6]
- [x] [Review][Patch] Evidence card omits fetch status summary before first fetch attempt [`src/examai/templates/tasks/fragments/evidence-card.html`:16]
- [x] [Review][Patch] Workspace HTML test does not assert lifecycle badge output [`tests/test_mentor_workspace_ai.py`:93]
- [x] [Review][Patch] `.examai-provenance` does not itself apply monospace styling [`src/examai/static/css/examai-theme.css`:18]
- [x] [Review][Patch] Scrollable source preview is not keyboard-focusable [`src/examai/templates/tasks/fragments/git-retrieval.html`:54]
- [x] [Review][Patch] Successful empty source text renders as an unfetched empty state [`src/examai/templates/tasks/fragments/git-retrieval.html`:55]

## Dev Notes

### Scope boundary (Phase 1 only)

This story implements **UX Implementation Roadmap Phase 1** from `_bmad-output/planning-artifacts/ux-design-specification.md` (lines 577–578). **Out of scope here** (later stories):

- **Phase 2:** Intern provenance summary card, review queue `table-sm` styling, intern submit validation UX.
- **Phase 3:** Coordinator case status strip, publish confirm modal, accessibility pass / skip link.

Do not refactor `review/queue.html`, `intern/submissions/feedback.html`, or coordinator templates in this story.

### Design references

| Topic | Source |
|-------|--------|
| Chosen layout | UX spec § Design Direction Decision — **Direction 2 (Structured workspace)** |
| Mock / visual | `_bmad-output/planning-artifacts/ux-design-directions.html` § `#d2` |
| Component anatomy | UX spec § Custom Components — Evidence card, lifecycle badge, draft panel, AI draft block, source panel |
| Button hierarchy | UX spec § UX Consistency Patterns — one primary per viewport; Publish primary on workspace |
| Degraded LLM | UX spec § Feedback Patterns — **`alert-info`** for LLM degradation |

### Current brownfield (do not reinvent)

| Asset | Path | Notes |
|-------|------|-------|
| Workspace template | `src/examai/templates/tasks/submission-detail.html` | Flat sections today; refactor in place |
| Git fragment | `tasks/fragments/git-retrieval.html` | Card with fetch + preview—move into left column |
| Degraded banner | `tasks/fragments/degraded-inference-banner.html` | Currently `alert-warning` — change to `alert-info` |
| Lifecycle badge include | `intern/fragments/submission-lifecycle-badge.html` | Reuse; only intern routes pass `submission_lifecycle` today |
| Lifecycle logic | `src/examai/submission_lifecycle.py` | `intern_submission_lifecycle_badge` — extend for mentor states |
| Routes | `src/examai/mentor_workspace_routes.py` | `submission_workspace` ~L204–275 — add context vars only |
| Theme | `src/examai/static/css/examai-theme.css` | Minimal today—extend, don’t replace Bootstrap |
| Tests | `tests/test_mentor_workspace_ai.py`, `tests/test_submission_lifecycle.py` | Primary regression targets |

### Architecture compliance

- **MPA + Jinja2:** No SPA; full page reload after POST unchanged.
- **View models in Python:** Lifecycle enum/badge built in `submission_lifecycle.py`, not template logic.
- **CSRF:** Keep `{% include "fragments/csrf-field.html" %}` on every mutating form.
- **RBAC:** No route changes; `/tasks/**` mentor/admin only.
- **Integrations:** No changes to Git or Ollama service modules—UI/layout only unless lifecycle needs read-only flags already on `Submission` model.

### File structure requirements

```
src/examai/
  submission_lifecycle.py          # ADD mentor_submission_lifecycle_badge
  mentor_workspace_routes.py       # PASS submission_lifecycle (+ has_mentor_draft flag)
  static/css/examai-theme.css      # ADD semantic classes
  templates/tasks/
    submission-detail.html         # REFACTOR layout
    fragments/
      evidence-card.html           # NEW
      mentor-draft-panel.html      # NEW
      ai-draft-block.html          # NEW
      git-retrieval.html           # ENHANCE
      degraded-inference-banner.html  # ENHANCE
tests/
  test_submission_lifecycle.py     # ADD mentor cases
  test_mentor_workspace_ai.py      # ADD HTML structure checks
```

### Testing requirements

- Run: `pytest tests/test_submission_lifecycle.py tests/test_mentor_workspace_ai.py -q`
- Full suite before marking done: `pytest`
- Manual smoke: open workspace with seeded submission—verify column stack at &lt;992px, fetch failure shows warning (not panic red page), degraded Ollama shows info banner, Publish still visible.

### Previous story intelligence (Epic 9.1)

- AI draft POST upserts `mentor_review_drafts` via parsing—draft form fields **`quality_score`**, **`readability_score`**, **`correctness_score`**, **`narrative_feedback`** must keep exact `name` attributes.
- **Publish review** uses `formaction` on draft form—preserve dual submit buttons when splitting fragments.
- `POST .../publish-review` accepts optional `narrative_feedback` when `narrative` empty—do not remove.
- Latest AI draft shown in card with audit line—move into `ai-draft-block.html` without dropping `ai_draft` / `ai_invocation` template vars.

### Git intelligence (recent)

- `8ee5fdc` — Story 9-1: AI rubric parsing + workspace publish UX (touch `submission-detail.html`, `mentor_workspace_routes.py`).
- `7ba10f5` / `ad9948b` — Epic 4 Git fetch/patch matching (git-retrieval fragment content)—preserve retrieval state display.

### Latest technical notes

- **Bootstrap 5.3** via WebJars (`fragments/head-bootstrap.html`); grid breakpoints: `lg` = 992px for two-column split.
- **jQuery** on workspace via `welcome-scripts.html`—no new JS required for layout; avoid adding toast libraries.

### Project context reference

- `_bmad-output/project-context.md` — implement only under `src/examai/`; no LLM calls from templates; degraded Ollama must not block publish.
- `docs/component-inventory.md` — update row for new fragments when adding files (optional doc touch if team expects inventory sync).

## Dev Agent Record

### Agent Model Used

Composer (dev-story workflow)

### Debug Log References

- Git fetch failure badges: retryable errors use `bg-warning text-dark`; `AUTH_DENIED` / auth-forbidden codes use `bg-danger` (shared `_git_failure_badge_class` in `submission_lifecycle.py` and inline check in `git-retrieval.html` header badge).

### Completion Notes List

- Added `mentor_submission_lifecycle_badge` with mentor-specific labels (not submitted → published pipeline).
- Refactored workspace into Direction 2 layout: evidence card, two-column source/draft, de-emphasized publish footer.
- New fragments: evidence-card, mentor-draft-panel, ai-draft-block; enhanced degraded banner (`alert-info`) and git-retrieval (primary fetch CTA, preview empty state, `aria-live`).
- Theme semantic classes for evidence card, provenance block, draft panel.
- Tests: 7 mentor lifecycle unit tests, workspace HTML structure + degraded banner assertions. Full suite: 134 passed.

### File List

- src/examai/submission_lifecycle.py
- src/examai/mentor_workspace_routes.py
- src/examai/static/css/examai-theme.css
- src/examai/templates/tasks/submission-detail.html
- src/examai/templates/tasks/fragments/evidence-card.html
- src/examai/templates/tasks/fragments/mentor-draft-panel.html
- src/examai/templates/tasks/fragments/ai-draft-block.html
- src/examai/templates/tasks/fragments/git-retrieval.html
- src/examai/templates/tasks/fragments/degraded-inference-banner.html
- tests/test_submission_lifecycle.py
- tests/test_mentor_workspace_ai.py

## Change Log

- 2026-05-18: UX Phase 1 structured mentor workspace layout (story 10.1).
