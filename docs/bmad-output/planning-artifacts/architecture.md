---
stepsCompleted:
  - 1
  - 2
  - 3
  - 4
  - 5
  - 6
  - 7
  - 8
lastStep: 8
status: complete
completedAt: '2026-04-15'
inputDocuments:
  - _bmad-output/planning-artifacts/prd/index.md
  - _bmad-output/planning-artifacts/prd/executive-summary.md
  - _bmad-output/planning-artifacts/prd/project-classification.md
  - _bmad-output/planning-artifacts/prd/success-criteria.md
  - _bmad-output/planning-artifacts/prd/product-scope.md
  - _bmad-output/planning-artifacts/prd/user-journeys.md
  - _bmad-output/planning-artifacts/prd/domain-specific-requirements.md
  - _bmad-output/planning-artifacts/prd/innovation-novel-patterns.md
  - _bmad-output/planning-artifacts/prd/web-application-specific-requirements.md
  - _bmad-output/planning-artifacts/prd/project-scoping-phased-development.md
  - _bmad-output/planning-artifacts/prd/functional-requirements.md
  - _bmad-output/planning-artifacts/prd/non-functional-requirements.md
  - _bmad-output/planning-artifacts/archive/prd.md
  - _bmad-output/project-context.md
  - docs/README.md
  - docs/index.md
  - docs/project-overview.md
  - docs/architecture.md
  - docs/development-guide.md
  - docs/source-tree-analysis.md
  - docs/data-models.md
  - docs/api-contracts.md
  - docs/component-inventory.md
  - docs/deployment-guide.md
workflowType: architecture
project_name: examinai_py
user_name: Alex
date: '2026-04-15'
---

# Architecture Decision Document

_This document was produced through the BMAD architecture workflow. **Workflow status: complete** (see YAML frontmatter)._

### Scope: solution vs reference

**The only implementation architecture is the Python application under `src/examai/`** (FastAPI, Jinja2 target, SQLAlchemy, PostgreSQL). **No Java, Spring, or `JAVA_APP/` tree is part of the solution** — not for deployment, migrations, templates, or configuration. If a legacy snapshot exists in the repository, it is **optional historical reference only** (e.g. to compare URLs or screen flow); it must **not** be treated as code to extend, a second runtime, or a dependency of the Python stack.

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

Thirty functional requirements (FR1–FR30) define a **multi-role internship examination** product: **sign-in/session** and **role-gated URL spaces**; **task CRUD and intern assignment**; **submissions** as version-control coordinates with **retrieval state** visible to mentors; **mentor draft reviews** and **publish** with **snapshot metadata** tied to evidence; **optional AI draft assessment** when the LLM is enabled, with **audit records** and **surfaced degraded/unavailable** LLM state; **intern-visible published feedback** distinguished from draft/AI policy; **coordinator** and **administrator** capabilities; **health** for operators; **compliance-oriented** limits on sensitive data in prompts and **role boundaries** on data access; **configurable failure behavior** for Git and LLM integrations.

Architecturally this implies a **cohesive server-side domain** (users, roles, tasks, submissions, reviews, AI audit entities) with **clear integration boundaries** for Git and LLM, and **workflow state machines** for submission retrieval and mentor publish paths.

**Non-Functional Requirements:**

NFRs emphasize: **responsive UX** for core flows with **explicit progress/failure** for long operations (Git fetch, LLM); **bounded timeouts/retries** for external calls; **password hashing**, **session/CSRF** on mutates, **secrets via environment**; **no credential leakage** into prompts or client-visible pages; **pilot-scale vertical scaling** acceptable; **progress toward WCAG 2.x** on core flows; **tolerant Git/LLM** integrations with **visible state** and **non-blocking human-only** mentor paths; **health** suitable for load balancers/smoke checks; **migrations** tracked through an agreed process so environments stay aligned.

**Scale & Complexity:**

- **Primary domain:** Full-stack **monolithic web application** (FastAPI/Jinja2 target, PostgreSQL, httpx-based integrations).
- **Complexity level:** **Medium–high** (external dependencies, audit trail, migration duality, multi-role RBAC).
- **Estimated architectural components (initial):** Web layer (routes, templates, static assets), **application services** per bounded areas (auth, tasks/submissions, review/feedback, admin), **integration adapters** (Git provider, Ollama), **persistence** (SQLAlchemy/Alembic trajectory), **operational** endpoints (health), and **cross-cutting** security/session/CSRF and logging policy.

### Technical Constraints & Dependencies

- **HTTP contract:** Parity with documented routes and static asset paths (`/css/**`, `/js/**`, `/webjars/**`) per **`docs/api-contracts.md`** and project context.
- **Data model:** Align with **`docs/data-models.md`** and PostgreSQL; forward schema changes go through **Alembic** once it is the migration owner. Optional archived DDL elsewhere is **reference only**, not a runtime or build dependency.
- **Stack (active):** Python **3.9+**, FastAPI, Uvicorn, Jinja2, SQLAlchemy 2.x, PostgreSQL, httpx; sessions (e.g. signed cookies) and role guards consistent with documented role → URL mapping.
- **Integrations:** GitHub-compatible REST for source retrieval; Ollama for optional drafts—both require **timeout/retry**, **rate-limit awareness**, and **degraded UX** without silent failure.
- **AI safety:** No raw LLM from route handlers; dedicated integration module; prompts limited to **task context + truncated normalized source** per policy.

### Cross-Cutting Concerns Identified

- **Authentication, session lifecycle, and CSRF** on all mutating server-rendered forms.
- **RBAC** mapped to URL prefixes (`/intern/**`, `/tasks/**`, `/review/**`, `/coordinator/**`, `/admin/**`).
- **External service resilience** (Git and LLM) with user-visible states and mentor **human-only publish** path.
- **Audit and provenance** for AI-assisted drafts and published feedback snapshots.
- **Accessibility** and **data minimization** progressing alongside feature delivery.
- **Brownfield migration:** contract-driven delivery without abandoning schema traceability (**documented model** + **Alembic** evolution — no reliance on a non-Python vendor tree as part of the solution).

## Starter Template Evaluation

### Primary Technology Domain

**Brownfield Python monolith — server-rendered web (FastAPI + Jinja2 + PostgreSQL)** with external **Git** and **Ollama** integrations. The product is **not** a JSON-first SPA or a greenfield Next.js app.

### Starter Options Considered

- **Greenfield FastAPI templates** (e.g. Cookiecutter-based community starters): useful for new APIs with bundled Docker/CI/auth choices; **not adopted** here because they would conflict with an in-progress **HTTP contract** migration and **documented schema** in **`docs/data-models.md`**.
- **Replacing the repo with a new generated tree:** rejected — high risk to **parity**, **documentation**, and **migration traceability**.

### Selected approach: Existing repository scaffold (incremental evolution)

**Rationale for selection:** The codebase already defines the “starter” decisions via **`pyproject.toml`**, **`src/examai/`** layout, and **`examai.main:app`**. Continuing this scaffold preserves alignment with **`docs/api-contracts.md`**, **`docs/data-models.md`**, and **`_bmad-output/project-context.md`**.

**Initialization commands:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn examai.main:app --reload --host 127.0.0.1 --port 8080
```

**Architectural decisions provided by the current scaffold:**

| Area | Decision |
|------|----------|
| **Language & runtime** | Python **≥ 3.9**; dependencies pinned in `pyproject.toml` (FastAPI constrained to `<0.117` until a deliberate upgrade; PyPI latest FastAPI as of this document’s drafting was **0.135.3** — upgrade requires explicit testing). |
| **Web** | FastAPI + Uvicorn; Jinja2 + `python-multipart` for forms. |
| **Data** | SQLAlchemy 2.x, Alembic, PostgreSQL (psycopg 3). |
| **HTTP clients** | httpx for Git provider and Ollama. |
| **Sessions** | itsdangerous (signed cookies) per project-context wiring plan. |
| **Tests** | pytest / pytest-cov under `[dev]` optional extra. |
| **Code organization** | Package **`examai`** under `src/`; extend via routers and services, not ad hoc globals. |

**Development experience:** Editable install, single-process dev server with reload; OpenAPI may remain disabled by default per project conventions.

**Note:** New work should **extend** this scaffold; **greenfield template CLI** adoption is **out of scope** unless the team explicitly resets the migration strategy.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical decisions (block implementation if unset):**

- **Data store and schema authority:** PostgreSQL; schema aligned with **`docs/data-models.md`**. **Alembic** becomes the sole owner of forward migrations when explicitly adopted; any historical DDL files elsewhere are **documentation/traceability only**, not part of the deployable solution.
- **Application style:** **Server-rendered MPA** (GET/POST forms, redirects) matching **`docs/api-contracts.md`** — not a JSON-first SPA or GraphQL for core workflows.
- **AuthN / AuthZ:** **Session-based** authentication after form login; **role-based access** by URL prefix (`/intern/**`, `/tasks/**`, `/review/**`, `/coordinator/**`, `/admin/**`) consistent with project-context and API contract.
- **Integration boundaries:** **Git** (GitHub-compatible REST) and **Ollama** accessed only via **dedicated service modules** (httpx), with **timeouts/retries** and **user-visible** failure/degraded states.

**Important decisions (shape the architecture):**

- **ORM and validation:** **SQLAlchemy 2.x** (2.0-style `select`/`execute`) for persistence; **Pydantic** models at HTTP boundaries for parsing/validation (FastAPI defaults).
- **Security mechanics:** **Strong password hashing** (one-way; not logged); **CSRF protection** on mutating requests per product security model; **secrets** from environment only.
- **AI and audit:** **No raw LLM calls in route handlers**; persist **model_invocations** / **ai_drafts** as in the data model; **human publish** gate for intern-visible outcomes.

**Deferred (post-MVP / explicit follow-up):**

- **Alembic-only** migration authority (retire dependence on any non-repo or legacy DDL workflow once cutover is explicit).
- **Horizontal scaling**, **Redis/caching**, **rate limiting** at the edge, **full automated test gates** (PRD defers test mandate in early phase).
- **Formal WCAG tier** and **FERPA/COPPA** operational controls until procurement/legal fixes scope.

### Data Architecture

| Topic | Decision | Rationale |
|--------|-----------|-----------|
| **Database** | **PostgreSQL** | Matches NFRs, existing schema, and `psycopg` stack. |
| **Modeling** | **SQLAlchemy 2.x** ORM + modules reflecting **`docs/data-models.md`** | Single persistence layer; UUID IDs as in schema. |
| **Validation** | **Pydantic v2** (via FastAPI) for request bodies/forms where applicable | Consistent boundary validation; aligns with FastAPI. |
| **Migrations** | **Documented model** (`docs/data-models.md`) + **Alembic** when active; **no casual drift**; legacy DDL snapshots (if any) are **read-only reference**, not a second migration pipeline in scope for the solution. |
| **Caching** | **None required for MVP** (vertical scaling acceptable per NFR) | Avoid premature Redis/infra; revisit with load. |

### Authentication & Security

| Topic | Decision | Rationale |
|--------|-----------|-----------|
| **Authentication** | **Session cookie** after credential verification (itsdangerous/signed cookies per project-context plan) | Fits MPA and PRD FR1–FR3. |
| **Authorization** | **RBAC** enforced in middleware/dependencies mapping **roles → allowed route prefixes** | Matches FR4–FR5 and documented URL matrix. |
| **Password storage** | **Strong one-way hash** (e.g. bcrypt-compatible scheme); never return or log credentials | NFR-S1. |
| **Mutating requests** | **CSRF tokens** on forms/posts | NFR-S2, web-app requirements. |
| **Secrets** | Environment / secure config only | NFR-S3; no tokens in prompts/logs (NFR-S4). |

### API & Communication Patterns

| Topic | Decision | Rationale |
|--------|-----------|-----------|
| **Primary interface** | **Browser-facing HTML** over **GET/POST** with redirects; **not** GraphQL/SPA API for core flows | PRD + `web-application-specific-requirements`. |
| **Machine-readable endpoints** | **`GET /actuator/health`** (and any other contract-listed JSON endpoints) as documented | Ops NFR-R1; match the **documented** JSON shape (e.g. load balancers/smoke scripts). |
| **OpenAPI** | **Disabled by default** on the app; enable only in dev if needed | Project-context convention. |
| **External HTTP** | **httpx** clients with **bounded timeouts/retries** and **structured error mapping** to UI state | NFR-P2, NFR-I1–I2. |
| **Rate limiting** | **Post-MVP** hardening unless program requires earlier | Product-scope growth features. |

### Frontend Architecture

| Topic | Decision | Rationale |
|--------|-----------|-----------|
| **Paradigm** | **Jinja2** server-rendered **MPA** | No client-side router requirement for MVP. |
| **State** | **Server-side session + DB**; minimal JS for Bootstrap/interaction | Aligns with **`docs/component-inventory.md`** and the HTTP contract. |
| **Assets** | **StaticFiles** for `/css/**`, `/js/**`, `/webjars/**` as in contract | FR/static parity. |
| **Accessibility** | Implement core flows to **progress toward WCAG 2.x** | NFR-A1. |

### Infrastructure & Deployment

| Topic | Decision | Rationale |
|--------|-----------|-----------|
| **Hosting** | **Process + PostgreSQL** (container or VM per **`docs/deployment-guide.md`** and team ops) | Pilot vertical scale NFR-SC1. |
| **Configuration** | **12-factor** env vars; **`.env` not committed** | NFR-S3; document names in **`docs/deployment-guide.md`** and/or a repo-level **`.env.example`** when maintained. |
| **Health & smoke** | **`/actuator/health`** for liveness | FR26, NFR-R1. |
| **CI/CD** | **Team-defined**; PRD does not mandate automated tests as an early gate — pipeline should still allow **lint/type/test** when introduced | Executive summary delivery strategy. |
| **Observability** | **Health first**; structured logging/metrics as follow-on | Reliability NFRs. |

### Decision Impact Analysis

**Implementation sequence (suggested):**

1. Session + role guards + CSRF baseline aligned with contract routes.
2. Core domain: users/roles/tasks/submissions against existing tables.
3. Mentor flow: Git fetch integration → draft/publish with provenance.
4. Ollama integration + audit tables + degraded UX.
5. Admin/coordinator routes per phased scope.
6. Alembic ownership and hardening (rate limits, richer observability) when explicitly scheduled.

**Cross-component dependencies:**

- **RBAC** depends on **session** and stable **role** model in DB.
- **Published feedback** depends on **submission state** and optional **Git fetch** success path.
- **AI drafts** depend on **audit** persistence and **mentor publish** separation from intern-visible content.
- **Migrations** must stay aligned with **`docs/data-models.md`** and the **Alembic** process once it owns schema changes (no solution dependency on a legacy vendor tree).

## Implementation Patterns & Consistency Rules

### Pattern categories defined

**Critical conflict points addressed:** naming (DB, Python, URLs), package layout, HTML vs JSON behavior, integration and logging boundaries, tests placement, error and loading semantics for server-rendered flows.

### Naming patterns

**Database naming conventions:**

- **Follow existing PostgreSQL names exactly:** lowercase **`snake_case`** tables and columns (e.g. `users`, `task_assignments`, `git_retrieval_state`). SQLAlchemy `__tablename__` and mapped attributes must match **`docs/data-models.md`** — **do not** introduce alternate pluralization or camelCase columns.
- **UUID primary keys:** Use **UUID** types in Python for columns documented as UUID.

**API and URL naming conventions:**

- **Path strings** must match **`docs/api-contracts.md`** literally (including **prefixes** `/intern/`, `/tasks/`, `/review/`, `/coordinator/`, `/admin/`, static `/css/`, `/js/`, `/webjars/`, **`/actuator/health`**). No “REST pluralization” drift for HTML routes — the contract is authoritative.
- **FastAPI path parameters:** Use `{param_name}` with names that match the contract; prefer **snake_case** parameter names in Python unless the documented path uses a different segment name.

**Code naming conventions:**

- **Python:** **PEP 8** — modules and packages **`lowercase_with_underscores`**, classes **`PascalCase`**, functions/variables **`snake_case`**. Route handler functions remain explicit (e.g. `list_tasks`, `post_submission`).
- **Templates:** **Jinja2** file names and paths follow **`docs/api-contracts.md`**, **`docs/component-inventory.md`**, and product UX needs; optional historical HTML snapshots (if present) are **reference only** — **do not** treat any non-Python template tree as part of the solution.
- **Integration modules:** Place Git and Ollama clients under a dedicated package (e.g. **`examai.integration.git`**, **`examai.integration.ai`**) — **never** embed provider logic in route functions.

### Structure patterns

**Project organization:**

- **Application code:** Only under **`src/examai/`** for new Python (extend with `routers/`, `services/`, `integration/`, `templates/`, `static/` as needed).
- **Tests:** **`tests/`** at repo root, files `test_*.py`, mirroring feature areas (e.g. `tests/test_health.py`). Do not co-locate tests inside `src/` unless the team later standardizes otherwise.
- **Reference-only artifacts:** Legacy snapshots (e.g. old JVM/HTML trees) are **not** in the solution surface; **all product code** lives under **`src/examai/`** and **`tests/`**.
- **Docs:** Public contract and setup live in **`docs/`**; update **`docs/index.md`** when routes or setup change (per project-context).

**File and config structure:**

- **Dependencies:** Root **`pyproject.toml`** only — no ad-hoc `requirements.txt` for the main app.
- **Environment:** Use **`.env`** locally (gitignored); align variable names with **`docs/deployment-guide.md`** and any repo **`.env.example`**.
- **Alembic:** When used, keep revisions under the conventional **`alembic/`** tree once introduced; until then defer schema changes to the agreed migration process.

### Format patterns

**HTML and form flows (primary):**

- **Success and errors** for mutating POSTs: use **redirect-after-POST** with **flash/session messages** or dedicated result pages — avoid ambiguous double-submit patterns.
- **CSRF:** Every state-changing form includes the **token** expected by the security middleware (single convention across templates).

**JSON responses (where the contract defines them, e.g. health):**

- **`GET /actuator/health`:** Preserve the **contract-documented** JSON shape (e.g. `{"status": "UP"}`) unless operators explicitly agree to change **and** docs are updated.

**Data in Python:**

- **Datetime:** Store **timezone-aware** values consistent with DB **`timestamptz`**; serialize for APIs as **ISO 8601** strings when JSON is used.
- **Booleans:** Use Python **`True`/`False`**; DB **`boolean`** columns as mapped by SQLAlchemy.

### Communication patterns

**Server-side “events”:**

- No cross-browser event bus is required for MVP. Prefer **explicit service methods** and, where needed, **structured logging** with consistent keys (e.g. `submission_id`, `integration=git|ollama`, `outcome=success|retry|fail`).

**Integration calls:**

- **httpx** only inside integration modules; **timeouts and retries** configured in one place per integration; **surface** terminal states to the UI (mentor/intern), never silent failure for long operations.

### Process patterns

**Error handling:**

- **User-facing:** Clear, non-technical messages on HTML pages for validation and permission errors; link back to safe navigation (task list, login).
- **Operator-facing:** **Health** endpoint for liveness; **do not** leak stack traces or secrets in responses.
- **Logging:** Never log **passwords, tokens, or full LLM prompts** with secrets; align with NFR-S3/S4.

**Loading and long operations:**

- **Git fetch / LLM:** Use **explicit** in-progress and terminal states in the DB or session-backed UI flags (per FR10–FR12, FR17–FR19) — **no** indefinite spinners without backend state.

**Authentication flow:**

- **Login → role-appropriate redirect** (FR5); **logout** clears server session; **unauthenticated** users only reach public routes (FR3).

### Enforcement guidelines

**All AI agents MUST:**

- Treat **`docs/api-contracts.md`** and **`docs/data-models.md`** as **canonical** for routes and schema.
- Keep **Git and Ollama** logic out of **route handlers**; use **service/integration** layers.
- Use **SQLAlchemy 2.0-style** session/query patterns and **UUID** IDs per schema.
- Preserve **role → URL** rules from **`_bmad-output/project-context.md`** when implementing guards.

**Pattern enforcement:**

- **Code review / PR checklist:** Contract diff for any route change; migration note for any DDL change; integration tests when auth paths are touched (once tests are in scope).
- **Violations:** Fix before merge if routes or schema diverge; update **`docs/`** and **`project-context.md`** when stack or layout rules change.

### Pattern examples

**Good examples:**

- Router module `src/examai/routers/intern.py` registers paths that **exactly match** the intern section of **`api-contracts.md`**; handler delegates to `services/submissions.py`.
- SQLAlchemy model class `Submission` maps to table **`submissions`** with columns **`commit_sha`**, **`git_retrieval_state`**, matching **`docs/data-models.md`**.
- `integration/git/client.py` wraps httpx calls with **timeouts** and returns a **typed result** consumed by the mentor workflow.

**Anti-patterns:**

- Adding **LLM calls** directly inside a `@router.get` / `@router.post` function.
- Renaming API paths for “REST purity” when the **documented** path is different.
- Introducing **camelCase** JSON field names for Python-internal DTOs when the DB and contract use **snake_case**, without an explicit versioning decision.
- Creating **parallel** `requirements.txt` or duplicate env loading mechanisms without team agreement.

## Project Structure & Boundaries

### Complete project directory structure

**Current layout (representative; optional `JAVA_APP/` reference snapshot may be gitignored):**

```
examinai_py/
├── pyproject.toml
├── README-Python.md
├── src/examai/
│   ├── __init__.py
│   └── main.py                    # FastAPI app — examai.main:app
├── tests/
│   └── test_health.py
├── docs/                          # Contract, schema, guides (index.md)
├── _bmad/, _bmad-output/
│   └── project-context.md
└── .cursor/                       # optional
```

**Target growth under `src/examai/`** (add as features land): `routers/`, `services/`, `integration/git/`, `integration/ai/`, `db/models/`, `templates/`, `static/`, optional `middleware/`; **`alembic/`** when migrations are owned by Python.

### Architectural boundaries

- **Routers** → **services** → **db** / **integration**; no httpx or LLM calls in route handlers.
- **Browser contract:** `docs/api-contracts.md`; **schema:** `docs/data-models.md`; **`JAVA_APP/`** paths (if present) are **reference only** per project docs.

### Requirements to structure (FR categories → modules)

| FR area | Primary location |
|---------|------------------|
| Auth & session (FR1–FR3) | `routers/auth.py`, `services/users.py`, session middleware |
| Tasks / submissions / Git (FR6–FR12, FR29) | `services/tasks.py`, `services/submissions.py`, `integration/git/` |
| Review / AI (FR13–FR20, FR30) | `services/reviews.py`, `integration/ai/`, `routers/mentor.py` |
| Admin / coordinator / ops | `routers/admin.py`, `routers/coordinator.py`, health in `main` or `routers/system.py` |

### Integration points

Internal: routers → services → PostgreSQL via SQLAlchemy. External: Git + Ollama only through `integration/` with timeouts and visible UI state.

## Architecture Validation Results

### Coherence

- **Stack:** FastAPI + Jinja2 + SQLAlchemy 2 + PostgreSQL + httpx is consistent; session/RBAC/CSRF align with MPA and PRD NFRs.
- **Patterns:** Naming, layering, and `docs/` as contract authority match **Core decisions** and **Implementation patterns**.
- **Reference:** `JAVA_APP/` explicitly excluded from solution scope; no conflicting second runtime.

### Requirements coverage

- **FR1–FR30:** Covered by session/RBAC, domain services, Git/Ollama integrations, audit entities, health — as mapped in **Project Context Analysis** and **Core Architectural Decisions**.
- **NFRs:** Performance (async UX for long ops), security, scalability pilot, accessibility progress, integration resilience, reliability — addressed in decisions and patterns.

### Implementation readiness

- Decisions, patterns, and anti-patterns are documented for AI agents; first priority remains **extend `src/examai/`** per **`pip install -e ".[dev]"`** and **`uvicorn examai.main:app`**.

### Gap analysis (non-blocking)

- **Alembic** revisions when schema ownership is explicit; root **Dockerfile/Compose** for Python when ops ready; automated tests when PRD phase allows.
- **WCAG tier** and **compliance** operational details when procurement/legal scope is fixed.

### Validation checklist

- [x] Context, starter/scaffold, core decisions, implementation patterns, structure
- [x] Coherence and FR/NFR coverage reviewed
- [x] Ready to use as implementation authority alongside **`docs/`** and **`_bmad-output/project-context.md`**

**Overall:** **READY FOR IMPLEMENTATION** — **High** confidence for MVP-scope parity work; refine with Alembic and ops artifacts as they land.

## Architecture workflow completion

This **Architecture Decision Document** is **complete** (workflow steps 1–8). Use it with **`docs/api-contracts.md`**, **`docs/data-models.md`**, and **`_bmad-output/project-context.md`** as the technical source of truth for **`examai`**. For BMAD “what next,” use the **`bmad-help`** skill if you want suggested follow-on artifacts or stories.
