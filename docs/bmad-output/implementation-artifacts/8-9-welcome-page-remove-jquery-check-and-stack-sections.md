# Story 8.9: Welcome page — remove jQuery UI check and Stack demo sections

Status: ready-for-dev

## Story

As a **visitor or operator**,  
I want the **public landing page (`/`)** to present a **clean welcome** without **internal stack smoke-test copy**,  
So that **the first screen looks product-ready** and **does not expose implementation trivia** (jQuery UI wiring, WebJar paths).

## Context

- **Welcome page template:** `src/examai/templates/index.html` — currently includes an **accordion** (`#welcome-accordion`) with two panels: **“jQuery UI check”** and **“Stack”** (Story 1-1 demo).
- **jQuery UI on `/`:** `fragments/head-welcome-jqui.html`, `/webjars/.../jquery-ui.min.js`, and `/js/welcome-jqui-init.js` exist **only to drive that accordion** on the landing page. No other template references `#welcome-accordion` (verified via repo search).
- **Epic 8:** Follow-up UX polish after the Docker/README stack stories; **does not** change Compose, Liquibase, or deployment behavior.

## Acceptance Criteria

1. **Removed demo content** — `GET /` HTML **must not** contain the accordion panel titles **“jQuery UI check”** or **“Stack”**, nor their demo explanatory paragraphs (WebJar / accordion wiring text).
2. **Landing layout** — The page **keeps** the existing shell: navbar with **Sign in**, heading **Welcome**, and the short line **“Server-rendered shell…”** with link to `/login` (wording may be tweaked only if necessary for layout; no new marketing scope).
3. **Drop jQuery UI from the landing page** — Remove jQuery UI–specific **head**, **scripts**, and the **accordion markup** from `index.html` so `/` no longer loads flick theme CSS, jQuery UI JS, or `welcome-jqui-init.js` **for that route**. (Fragments remain available for other templates if needed.)
4. **jQuery / Bootstrap** — Keep **`fragments/welcome-scripts.html`** on `index.html` **only if** still needed for Bootstrap JS behavior on that page; **Bootstrap 5** does not require jQuery. Prefer **minimal** includes: typically **`head-bootstrap.html`** + body content + optional **`welcome-scripts.html`** — if the landing page is static and nothing calls `$`, you may omit **`welcome-scripts.html`** on `index.html` to avoid loading jQuery on `/` entirely. **Document the chosen minimal set in the Dev Agent Record.**
5. **Tests** — Extend **`tests/test_public_shell.py`** (or add a focused test) so **`GET /`** asserts **200** and that the response body **does not** contain **`jQuery UI check`** or **`welcome-accordion`** (or equivalent stable negated strings). Existing **`test_public_pages_return_html`** should remain green.
6. **Static assets** — Do **not** delete **`/js/welcome-jqui-init.js`** or WebJar mounts unless a follow-up story retires them globally; they may still be served and covered by existing static tests.

## Tasks / Subtasks

- [ ] Edit **`src/examai/templates/index.html`**: remove accordion block and jQUI-only includes; simplify scripts per AC4.
- [ ] Optional: adjust **`src/examai/static/js/welcome-jqui-init.js`** top comment if it still claims “landing page demo” as the only use (accurate docs only; no behavior change required).
- [ ] Add/update tests per AC5.
- [ ] Run **`pytest`** for affected tests; fix any regressions.

## Dev Notes

### Files to touch (expected)

| File | Change |
|------|--------|
| `src/examai/templates/index.html` | Remove `#welcome-accordion` / `.examai-welcome-jqui` block; remove `{% include "fragments/head-welcome-jqui.html" %}`; remove jquery-ui + `welcome-jqui-init.js` script tags; trim foot scripts per AC4. |
| `tests/test_public_shell.py` | Assertions for absent demo strings on `/`. |

### Regression guardrails

- **`/login`**, **`/error`**, and authenticated templates are **unchanged** unless they shared `index.html` only via fragments (they do not).
- **`docs/api-contracts.md`** still lists **`/webjars/**`** — this story does **not** remove WebJar serving; it only stops **loading** jQUI on `/`.

### References

- Current landing markup: `src/examai/templates/index.html` (lines 18–35 area).
- Story 1-1 stack demo background: `_bmad-output/implementation-artifacts/1-1-public-pages-static-assets-and-webjar-ui-stack.md`
- Component inventory (fragments): `docs/component-inventory.md`

## Dev Agent Record

### Agent Model Used

_(fill on completion)_

### Completion Notes List

_(fill on completion)_

### File List

_(fill on completion)_
