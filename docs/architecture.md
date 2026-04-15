# Technical Architecture — Examinai

**Active stack:** Python (**FastAPI**, **Jinja2**, **SQLAlchemy 2**, **Uvicorn**) under `src/examai/`. **`JAVA_APP/`** (when present) is **reference only** — optional Spring Boot snapshot for comparing **routes, Thymeleaf templates, Liquibase DDL, and integration behavior**. **All new product work** is implemented in **`src/examai/`**; do not extend the Java tree for features.

## Executive summary

Examinai is a **monolithic server-rendered web application** for internship-style workflows: coordinators and administrators manage users; interns submit **repository coordinates** for assigned tasks; mentors **fetch normalized source** from a **Git provider API**, optionally request **Ollama-backed AI draft assessments**, and **publish** structured feedback. The **product behavior** is defined by **`docs/api-contracts.md`**; the **Python app** implements that surface with **Jinja2** templates and **integration modules** (Git, Ollama) isolated from route handlers.

## Architecture pattern (Python)

**Layered monolith (target):**

1. **Web** — FastAPI routers, Jinja2 responses, form posts, redirects/flash patterns as implemented.
2. **Services** — Application services coordinate transactions and policies (mirror legacy `*Service` responsibilities).
3. **Domain / persistence** — SQLAlchemy 2.x models and repositories; **UUID** keys aligned with [data-models.md](./data-models.md).
4. **Integration** — `examai.integration` (or equivalent): **httpx** clients for Ollama and GitHub-compatible REST; explicit timeouts, errors, and degraded behavior.

Cross-cutting: **session-based auth**, **role-gated routes** (documented URL rules; legacy snapshot optional for comparison), **`GET /actuator/health`**, schema evolution via **`db/changelog/`** (Liquibase when **`EXAMINAI_USE_LIQUIBASE`** is set) and [data-models.md](./data-models.md); optional Liquibase/JPA under **`JAVA_APP/`** remains **DDL reference only** if a snapshot exists.

## Security model

- **Authentication:** Form login at `/login`; session cookie; logout at `/logout` — **behavior** matches the legacy Spring Security layout; **implementation** is Python (e.g. itsdangerous/sessions per `project-context.md`).
- **Authorization:** URL prefixes by role (see [api-contracts.md](./api-contracts.md)):
  - `/admin/**` → administrator
  - `/review/**`, `/tasks/**` → mentor or administrator
  - `/intern/**` → intern
  - `/coordinator/**` → coordinator
- **Secrets:** Git token, DB URL/credentials, Ollama settings via **environment** — document names in [deployment-guide.md](./deployment-guide.md) and/or a repo **`.env.example`**; a **`JAVA_APP/.env.example`** (if the snapshot exists) may be used **only as a naming cross-reference**.

## Data architecture

**PostgreSQL.** Table definitions follow [data-models.md](./data-models.md). In **Docker Compose**, the **`db-migrate`** service (official Liquibase image) applies **`db/changelog/`** before the **app** container starts; the **app** image has no JVM. **`EXAMINAI_USE_LIQUIBASE`** on the app means schema is Liquibase-managed (skip ORM `create_all`). **Liquibase** YAML under **`JAVA_APP/.../db/changelog/`** (if present) is **reference DDL only** for parity checks, not a runtime dependency of the Python stack.

## AI and degraded behavior

- **Inference:** httpx (or async client) to Ollama; configurable timeouts, retries, and payload limits (mirror `examinai.ai.draft-assessment.*` semantics from legacy YAML where applicable).
- **Persistence:** Successful runs create `model_invocations` + `ai_drafts` rows (audit).
- **UX:** Mentor views surface **degraded** state when the LLM is unavailable (parity with legacy `DegradedInferenceModelAdvice` behavior).

## Git integration

- **Client:** httpx-based client to `GIT_PROVIDER_BASE_URL` (GitHub REST v3–compatible).
- **Config:** `GIT_PROVIDER_BASE_URL`, `GIT_PROVIDER_TOKEN`.
- **Storage:** Normalized text and fetch state on `submissions` columns as in schema docs.

## UI architecture

- **Templates:** **Jinja2** under `src/examai/` (layout grows with implementation); **parity** with legacy Thymeleaf names/paths where “same UI” is required.
- **Static:** `/css`, `/js`, `/webjars/**` — mount **StaticFiles** / WebJar routes per [project-context.md](../_bmad-output/project-context.md).
- **No SPA:** Full page navigation and form POST for core flows.

## Testing strategy

- **pytest** under `tests/` when automated tests are in scope (see **`_bmad-output/planning-artifacts/prd/index.md`** for any phased deferral).
- **Health:** `GET /actuator/health` for ops smoke.

## Deployment architecture

- **Target:** Single container or process running **Uvicorn** + app, plus **PostgreSQL** and optional **Ollama** (three-service pilot topology). A **Python Dockerfile** at repo root is the long-term default. **`JAVA_APP/docker-compose.yml`** (if the snapshot exists) is **reference only** for compose wiring — see [deployment-guide.md](./deployment-guide.md).

---

## Reference: Spring Boot snapshot (`JAVA_APP/`)

_Optional local snapshot — **not** the shipped solution. Use for **parity checks** (URLs, templates, schema DDL, integration patterns) only._

- **Stack:** Spring Boot 3, Thymeleaf, Spring Security, Spring Data JPA, Spring AI (Ollama), Liquibase.
- **Web:** `@Controller`, Thymeleaf views; `integration.ai` / `integration.git`; `SecurityConfig` URL rules; `RoleBasedAuthenticationSuccessHandler`.
- **Tests:** JUnit, WebMvc, Testcontainers — under `JAVA_APP/src/test/java/` **only** if maintaining the snapshot for comparison (not part of Python CI).
- **Operator detail (reference):** **`JAVA_APP/README.md`** when the tree is present.

## Related documents

- [api-contracts.md](./api-contracts.md) — HTTP route catalog
- [data-models.md](./data-models.md) — tables and mapping
- [source-tree-analysis.md](./source-tree-analysis.md) — directory map
- [development-guide.md](./development-guide.md) — Python setup

---

_Updated: Python as active stack; `JAVA_APP/` reference-only when present._
