---
project_name: examinai_py
user_name: Alex
date: '2026-04-15'
sections_completed:
  - technology_stack
  - language_rules
  - framework_rules
  - testing_rules
  - quality_rules
  - workflow_rules
  - anti_patterns
status: complete
rule_count: 48
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

**Repository layout**

| Path | Role |
|------|------|
| **`src/examai/`** | **Active Python implementation** — FastAPI entry `examai.main:app`, future Jinja2 templates, services, integrations. |
| **`pyproject.toml`** | Canonical dependency manifest; **editable install:** `pip install -e ".[dev]"`. |
| **`README-Python.md`** | Python setup and run commands. |
| **`JAVA_APP/`** | Legacy **Spring Boot** snapshot (`pom.xml`, full `src/`, Docker). **Gitignored** — reference for parity; may be absent in CI. |
| **`docs/`** | HTTP contract, schema, UI inventory (`index.md` entry). |
| **`_bmad-output/`**, **`_bmad/`** | BMAD artifacts — preserve. |

**Python stack (pinned in `pyproject.toml`)**

| Concern | Choice |
|---------|--------|
| Runtime | **Python ≥ 3.9** (prefer **3.12+** for local dev; see `.python-version`) |
| Web | **FastAPI** + **Uvicorn**; **Jinja2** for server-rendered HTML; **`python-multipart`** for forms |
| DB | **SQLAlchemy 2.x** + **Alembic** + **psycopg** (binary) → PostgreSQL |
| HTTP clients | **httpx** for Git provider + Ollama APIs |
| Sessions | **itsdangerous** (signed cookies) — wire session middleware before role guards |
| Tests | **pytest**, **pytest-cov** (optional dev extra) |

**Legacy Java (reference only — `JAVA_APP/pom.xml`)**

| Layer | Version |
|-------|---------|
| Java | 21 |
| Spring Boot | 3.5.13 |
| Spring AI | 1.1.4 (Ollama) |
| Migrations | Liquibase YAML under `JAVA_APP/src/main/resources/db/changelog/` |

**Parity target:** Match routes and behavior in **`docs/api-contracts.md`**; preserve static paths **`/css/**`**, **`/js/**`**, **`/webjars/**`** when serving the same UI.

---

## Critical Implementation Rules

### Language-specific rules

**Python**

- Use **`from __future__ import annotations`** in new modules when using forward refs; support **3.9** until the project bumps minimum version.
- **Type hints** on public functions, route handlers, and service methods.
- **UUID** objects for DB IDs matching the existing schema (`uuid` columns).
- **No raw LLM calls from route handlers** — use a dedicated service module (e.g. `examai.integration.ai`) mirroring Java’s `integration.ai`.

**Java (only under `JAVA_APP/`)**

- Do not refactor legacy code unless explicitly requested; keep **integration boundaries** (AI, Git) out of web controllers.

### Framework-specific rules

**FastAPI**

- **`create_app()`** factory pattern is established in `examai.main` — extend via **`app.include_router`** and lifespan hooks rather than globals.
- **OpenAPI** (`/docs`) is **disabled** on the default app — enable only behind dev settings if needed.
- **Spring-compatible health:** keep **`GET /actuator/health`** returning JSON like `{"status": "UP"}` unless operators agree to change.

**Jinja2 (when added)**

- Mount **`StaticFiles`** for `/css`, `/js` (and WebJar static routes if you vendor assets).
- Mirror **Thymeleaf** template names and URL structure from `JAVA_APP/src/main/resources/templates/` where “same UI” is required.

**SQLAlchemy / Alembic**

- Target schema must stay aligned with **Liquibase** until a deliberate cutover; generate Alembic revisions from the same tables (`users`, `roles`, `tasks`, `submissions`, etc. — see `docs/data-models.md`).
- Use **2.0-style** `select()` / `session.execute()` patterns.

### Testing rules

- **pytest** default; place tests under **`tests/`**, name `test_*.py`.
- Use **FastAPI `TestClient`** for HTTP tests (see `tests/test_health.py`).
- Add **integration tests** early for **auth + role-gated paths** once security exists.
- **Java tests** remain under `JAVA_APP/src/test/java` only if editing legacy code.

### Code quality and style rules

- **Secrets:** never commit `.env`; use **`JAVA_APP/.env.example`** as the name template for vars (`GIT_PROVIDER_*`, `SPRING_*` / future `DATABASE_*`, `OLLAMA_*`).
- **Git client:** GitHub REST v3–compatible; **`Authorization: Bearer`**; no token logging.
- **AI payloads:** task text + truncated normalized source only — no tokens, no `.env` contents in prompts.
- Update **`docs/index.md`** when public routes or setup change; keep **this file** in sync when stack rules change.

### Development workflow rules

- **Install:** `python -m venv .venv` → `pip install -e ".[dev]"` (see **`README-Python.md`**).
- **Run:** `uvicorn examai.main:app --reload --host 127.0.0.1 --port 8080`
- **Legacy Java:** `cd JAVA_APP && ./mvnw ...` — only when working on the snapshot.
- **`.venv/`** is gitignored — do not commit virtualenvs.

### Critical don't-miss rules

- **URL contract** in **`docs/api-contracts.md`** — path or method changes break clients and security expectations.
- **Roles:** `ADMINISTRATOR` → `/admin/**`; `MENTOR` + admin → `/tasks/**`, `/review/**`; `INTERN` → `/intern/**`; `COORDINATOR` → `/coordinator/**`.
- **Schema drift:** Do not change PostgreSQL tables casually; **Liquibase** in `JAVA_APP` is the reference until Alembic fully replaces it.
- **Degraded Ollama:** Mentor flows must survive LLM outage (banner, publish rules) — mirror NFR from product docs.
- **`JAVA_APP/`** may be the only legacy copy — do not delete in automated passes.

---

## Usage Guidelines

**For AI agents**

- Read this file and **`docs/index.md`** before coding; use **`docs/api-contracts.md`** for routes.
- Implement new features in **`src/examai/`** unless the task is explicitly legacy Java.
- Prefer **stricter** security and data-handling when uncertain.

**For humans**

- Bump **`requires-python`** and **`.python-version`** together when raising the floor.
- Re-run **GPC** after major stack or layout changes.
- Trim redundant rules over time so this file stays lean.

_Last updated: 2026-04-15_
