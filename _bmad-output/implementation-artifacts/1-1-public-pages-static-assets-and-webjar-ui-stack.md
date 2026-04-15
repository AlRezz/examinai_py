# Story 1.1: Public pages, static assets, and WebJar UI stack

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **visitor**,  
I want **landing, login, and error pages with Bootstrap, jQuery, WebJar-served libraries, and theme CSS under the contract paths**,  
so that **the app shell matches the documented HTTP and static surface before auth and domain features land**.

## Acceptance Criteria

1. **Public HTML routes (contract)**  
   **Given** the app is running  
   **When** a client requests `GET /`, `GET /login`, or `GET /error`  
   **Then** each returns **200** with **HTML** (`text/html`) and content consistent with **[docs/api-contracts.md](../../docs/api-contracts.md)** (public section).

2. **Static asset mounts**  
   **Given** the app is running  
   **When** a client requests paths under `/css/**`, `/js/**`, and `/webjars/**`  
   **Then** files are served with success responses and **Content-Type** appropriate to the asset (e.g. CSS, JS), matching the contract’s static surface.

3. **Template and fragment layout (UX)**  
   **Then** Jinja2 templates follow **[docs/component-inventory.md](../../docs/component-inventory.md)** names and areas for core pages: `index.html`, `login.html`, and an error template aligned with `GET /error` (e.g. dedicated template or shared error view).  
   **And** shared fragments exist and are used as documented: **`fragments/head-bootstrap.html`**, **`fragments/welcome-scripts.html`**, **`fragments/head-welcome-jqui.html`** (**UX-DR1**, **UX-DR2**).

4. **Design system assets (UX)**  
   **Then** the UI stack supports **Bootstrap 5**, **jQuery**, and **jQuery UI** as referenced by the inventory: scripts/styles reachable via **`/webjars/**`** (or equivalent paths that preserve the same browser URLs), plus **`/css/examai-theme.css`** for theming (**UX-DR5–UX-DR8**).  
   **And** pages that demonstrate the jQuery UI stack load the documented stack paths (e.g. `css/welcome-jqui.css`, `css/jquery-ui/themes/flick/jquery-ui.min.css`, `js/welcome-jqui-init.js` per inventory) where those files are in scope for this story.

5. **No regression to existing health route**  
   **Given** `GET /actuator/health` already exists on the app  
   **When** this story’s changes are merged  
   **Then** health continues to return the contract JSON shape (see **[docs/deployment-guide.md](../../docs/deployment-guide.md)** / existing tests) — this story does **not** redefine health behavior (**Story 1.2** owns extended health documentation; keep current behavior working).

## Tasks / Subtasks

- [ ] **App wiring** (AC: 1, 2, 5)  
  - [ ] Extend **`create_app()`** in [`src/examai/main.py`](../../src/examai/main.py): mount **`StaticFiles`** for `/css`, `/js`, `/webjars` (separate mounts or a single tree — paths must match the contract).  
  - [ ] Configure **Jinja2** (`Jinja2Templates`) with a **`templates/`** directory under **`src/examai/`** (or package-resolved path — document the chosen pattern).  
  - [ ] Register routes for **`GET /`**, **`GET /login`**, **`GET /error`** returning `HTMLResponse` from templates.  
  - [ ] Keep **`GET /actuator/health`** passing existing [`tests/test_health.py`](../../tests/test_health.py).

- [ ] **Static content** (AC: 2, 4)  
  - [ ] Add **`static/`** (or equivalent) under **`src/examai/`** with at least: **`css/examai-theme.css`**, and any **`css/welcome-jqui.css`**, **`js/welcome-jqui-init.js`**, **`css/jquery-ui/themes/flick/jquery-ui.min.css`** per **[docs/component-inventory.md](../../docs/component-inventory.md)**.  
  - [ ] Vendor **WebJar-equivalent** assets for **Bootstrap 5.3.3**, **jQuery 3.7.1**, **jQuery UI 1.13.2** (same versions as legacy reference) under paths that map to **`/webjars/**`** URLs expected by templates (mirror standard WebJar path segments so script `src`/`href` values stay predictable).

- [ ] **Templates** (AC: 1, 3, 4)  
  - [ ] Implement **`index.html`**, **`login.html`**, and error page template(s) using fragments for head/scripts.  
  - [ ] **`login.html`**: present a **GET** login screen with a form wired for a future **`POST`** login (Story 1.3) — **do not** implement session auth or credential verification in this story.  
  - [ ] **`GET /error`**: show a user-visible error page (static message or query param is acceptable if documented in code comments; no stack traces).

- [ ] **Tests** (AC: 1–5)  
  - [ ] Add **`TestClient`** tests: `GET /`, `/login`, `/error` → 200 and `text/html`.  
  - [ ] Smoke-test key static URLs (theme CSS, at least one `/webjars/...` asset) → 200.  
  - [ ] Keep or extend health test so it still passes.

## Dev Notes

### Scope boundaries

| In scope | Out of scope (later stories) |
|----------|------------------------------|
| Public GET pages and static mounts | **`POST /login`**, sessions, **`GET /home`**, **`GET /app/secure`**, **`POST /logout`** (**Story 1.3**) |
| Landing/login/error **shell** | **RBAC** and role-gated prefixes (**Story 1.4**) |
| Asset and template parity with contract/inventory | **CSRF tokens on forms** (**Story 1.5**) — login form may omit token until 1.5 |
| | **`GET /actuator/health`** behavior changes (**Story 1.2** focuses operator docs/behavior; current JSON already exists) |

### Architecture and patterns

- **Single solution tree:** All new code and assets live under **`src/examai/`** — see [_bmad-output/planning-artifacts/architecture.md](../../_bmad-output/planning-artifacts/architecture.md) (Python-only; `JAVA_APP/` is reference-only).  
- **HTTP contract is authoritative:** Path strings must match **[docs/api-contracts.md](../../docs/api-contracts.md)** literally (no REST-style renaming for HTML routes).  
- **Web layer:** Server-rendered **MPA** with **Jinja2**; use **`create_app()`** factory and **`include_router`** as the app grows — avoid global mutable singletons.  
- **OpenAPI:** Leave **`docs_url=None`**, **`redoc_url=None`** on the default app unless a dev-only flag is introduced later ([_bmad-output/project-context.md](../../_bmad-output/project-context.md)).

### Project structure notes

- **Templates:** Target layout per **[docs/component-inventory.md](../../docs/component-inventory.md)** — `index.html`, `login.html`, `fragments/...` under the chosen `templates/` root.  
- **Static files:** **`fastapi.staticfiles.StaticFiles`** — mount directories so URLs are **`/css/...`**, **`/js/...`**, **`/webjars/...`** as in the contract. Package static files inside **`src/examai/static/`** (or documented subpaths) so editable installs resolve reliably.  
- **Tests:** Keep tests under **`tests/`**, `test_*.py`, using **`TestClient`** ([`tests/test_health.py`](../../tests/test_health.py) pattern).

### Library / version guardrails

| Library | Target version (parity) | Notes |
|---------|-------------------------|--------|
| Bootstrap | **5.3.3** | Via `/webjars/**` paths |
| jQuery | **3.7.1** | Same |
| jQuery UI | **1.13.2** | Theme **flick** per inventory |
| FastAPI | **`pyproject.toml` range** (`>=0.115,<0.117`) | Extend app, do not bump major without team decision |
| Jinja2 | **`pyproject.toml`** | Use Starlette/FastAPI `Jinja2Templates` |

### Testing requirements

- **pytest** + **FastAPI `TestClient`**.  
- Assert **status codes** and **content types** for HTML routes; spot-check static asset URLs.  
- Do not add PostgreSQL dependency for this story unless you introduce DB (not required for static shell).

### References

- [docs/api-contracts.md](../../docs/api-contracts.md) — public routes and static paths  
- [docs/component-inventory.md](../../docs/component-inventory.md) — template names, fragments, CSS/JS list, WebJar versions  
- [docs/source-tree-analysis.md](../../docs/source-tree-analysis.md) — `src/examai/` layout  
- [_bmad-output/planning-artifacts/architecture.md](../../_bmad-output/planning-artifacts/architecture.md) — stack, StaticFiles, template rules  
- [_bmad-output/project-context.md](../../_bmad-output/project-context.md) — FastAPI/Jinja rules, `examai.main:app`  
- **Epic context:** [_bmad-output/planning-artifacts/epics.md](../../_bmad-output/planning-artifacts/epics.md) — Epic 1, Story 1.1 (FR4 partial, FR33 partial; **FR1–FR3** deferred to 1.3)

### Previous story intelligence

_None — first story in Epic 1._

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

---

**Story completion status:** Ultimate context engine analysis completed — comprehensive developer guide created. **ready-for-dev.**
