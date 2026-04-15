# Component Inventory — UI and Web Layer

The product UI is **server-rendered**. The **active** implementation uses **Jinja2** templates and static assets under **`src/examai/`** (paths evolve as features land). There is no React/Vue SPA.

**Reference (`JAVA_APP/` — if snapshot exists):** **`JAVA_APP/src/main/resources/templates/`** holds **Thymeleaf** sources — use **only as reference** for **URL, template name, and fragment parity** when matching the existing UI.

## Target layout (Python / Jinja2)

| Area | Location (target) | Notes |
|------|-------------------|--------|
| Templates | `src/examai/` (e.g. `templates/` or package-relative paths TBD) | Mirror legacy **paths and names** from reference where required |
| Static assets | Served via FastAPI `StaticFiles` — `/css/**`, `/js/**`, `/webjars/**` | Align with [api-contracts.md](./api-contracts.md) |

_Add rows here as the Python tree grows._

## Reference — template layout (`JAVA_APP/src/main/resources/templates/` — if present)

| Area | Templates | Notes |
|------|-----------|--------|
| Core | `index.html`, `home.html`, `login.html` | Entry and auth |
| App shell | `app/secure.html` | Authenticated smoke |
| Admin | `admin/users/list.html`, `admin/user-form.html` | User CRUD |
| Coordinator | `coordinator/index.html`, `coordinator/case-record.html` | Case visibility |
| Intern | `intern/tasks/list.html`, `intern/tasks/detail.html`, `intern/submissions/feedback.html` | Tasks and feedback |
| Mentor / tasks | `tasks/list.html`, `tasks/form.html`, `tasks/assign.html`, `tasks/submissions.html`, `tasks/submission-detail.html` | Task lifecycle and mentor workspace |
| Review | `review/queue.html` | Mentor queue |
| Fragments | `fragments/head-bootstrap.html`, `fragments/welcome-scripts.html`, `fragments/head-welcome-jqui.html` | Shared head/scripts |
| Task fragments | `tasks/fragments/git-retrieval.html`, `tasks/fragments/degraded-inference-banner.html` | Partials |
| Intern fragments | `intern/fragments/submission-lifecycle-badge.html` | Status badge |

## Reference — static assets (`JAVA_APP/src/main/resources/static/` — if present)

| Path | Purpose |
|------|---------|
| `css/examai-theme.css` | Application theming |
| `css/welcome-jqui.css` | jQuery UI welcome styling |
| `css/jquery-ui/themes/flick/jquery-ui.min.css` | jQuery UI theme |
| `js/welcome-jqui-init.js` | jQuery UI initialization |

## Third-party UI (WebJars)

Legacy **`pom.xml`** declares WebJars (Bootstrap 5.3.3, jQuery 3.7.1, jQuery UI 1.13.2). Python stack should serve equivalent static/WebJar routes for parity.

## Server-side components

| Type | Active (Python) | Reference (Java) |
|------|-----------------|------------------|
| HTTP handlers | FastAPI routers in `src/examai/` | `com.examinai.app.web.*` |
| Cross-cutting | Middleware, dependencies, Jinja globals | Controller advice (e.g. degraded LLM) |
| Forms | Pydantic / Starlette form handling | `*Form` classes in legacy web packages |

## Design system

- **Bootstrap 5** + jQuery where legacy UI depends on them — reproduce behavior in Jinja2; **reference** Thymeleaf fragments for structure.

---

_Updated: Jinja2/Python primary; `JAVA_APP/` Thymeleaf/static as reference when snapshot exists._
