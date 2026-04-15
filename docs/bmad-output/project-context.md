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
| **`JAVA_APP/`** (if present) | **Not part of the solution.** Optional historical snapshot only — do **not** extend for product work, migrations, or deployment. May be gitignored or absent. |
| **`docs/`** | HTTP contract, schema, UI inventory (`index.md` entry). |
| **`_bmad-output/`**, **`_bmad/`** | BMAD artifacts — preserve. |

**Python stack (pinned in `pyproject.toml`)**

| Concern | Choice |
|---------|--------|
| Runtime | **Python ≥ 3.9** (prefer **3.12+** for local dev; see `.python-version`) |
| Web | **FastAPI** + **Uvicorn**; **Jinja2** for server-rendered HTML; **`python-multipart`** for forms |
| DB | **SQLAlchemy 2.x** + **psycopg** (binary) → PostgreSQL; **Liquibase** applies **`db/changelog/`** via Compose **`db-migrate`** (or host CLI) when **`EXAMINAI_USE_LIQUIBASE`** is set — the app image has no JDK. **Alembic** is listed in `pyproject.toml` for future revisions. |
| HTTP clients | **httpx** for Git provider + Ollama APIs |
| Sessions | **itsdangerous** (signed cookies) — wire session middleware before role guards |
| Tests | **pytest**, **pytest-cov** (optional dev extra) |

**Non-Python snapshots (optional, not authoritative):** A JVM tree may exist elsewhere in the repo for **occasional comparison only** (e.g. old route names). **Do not** treat it as a second app, migration source, or template source of truth.

**Parity target:** Match routes and behavior in **`docs/api-contracts.md`**; preserve static paths **`/css/**`**, **`/js/**`**, **`/webjars/**`** as documented.

---

## Critical Implementation Rules

### Language-specific rules

**Python**

- Use **`from __future__ import annotations`** in new modules when using forward refs; support **3.9** until the project bumps minimum version.
- **Type hints** on public functions, route handlers, and service methods.
- **UUID** objects for DB IDs matching the existing schema (`uuid` columns).
- **No raw LLM calls from route handlers** — use a dedicated service module (e.g. `examai.integration.ai`).

**Legacy snapshots:** If a non-Python tree exists, do not refactor or build product features there. All implementation belongs in **`src/examai/`**.

### Framework-specific rules

**FastAPI**

- **`create_app()`** factory pattern is established in `examai.main` — extend via **`app.include_router`** and lifespan hooks rather than globals.
- **OpenAPI** (`/docs`) is **disabled** on the default app — enable only behind dev settings if needed.
- **Health JSON:** keep **`GET /actuator/health`** returning the **contract-documented** shape (e.g. `{"status": "UP"}`) unless operators agree to change.

**Jinja2 (when added)**

- Mount **`StaticFiles`** for `/css`, `/js` (and WebJar static routes if you vendor assets).
- Follow **`docs/component-inventory.md`** and **`docs/api-contracts.md`** for page structure and URLs; optional old HTML may exist only as informal reference.

**SQLAlchemy / Alembic**

- Target schema must stay aligned with **`docs/data-models.md`** and PostgreSQL; **Alembic** owns forward revisions once active. Archived DDL elsewhere is **historical reference only**, not a runtime dependency.
- Use **2.0-style** `select()` / `session.execute()` patterns.

### Testing rules

- **pytest** default; place tests under **`tests/`**, name `test_*.py`.
- Use **FastAPI `TestClient`** for HTTP tests (see `tests/test_health.py`).
- Add **integration tests** early for **auth + role-gated paths** once security exists.

### Code quality and style rules

- **Secrets:** never commit `.env`; document env vars in **`docs/deployment-guide.md`** and use a repo **`.env.example`** when present (`GIT_PROVIDER_*`, `DATABASE_*`, `OLLAMA_*`, etc.).
- **Git client:** GitHub REST v3–compatible; **`Authorization: Bearer`**; no token logging.
- **AI payloads:** task text + truncated normalized source only — no tokens, no `.env` contents in prompts.
- Update **`docs/index.md`** when public routes or setup change; keep **this file** in sync when stack rules change.

### Development workflow rules

- **Install:** `python -m venv .venv` → `pip install -e ".[dev]"` (see **`README-Python.md`**).
- **Run:** `uvicorn examai.main:app --reload --host 127.0.0.1 --port 8080`
- **`.venv/`** is gitignored — do not commit virtualenvs.

### Critical don't-miss rules

- **URL contract** in **`docs/api-contracts.md`** — path or method changes break clients and security expectations.
- **Roles:** `ADMINISTRATOR` → `/admin/**`; `MENTOR` + admin → `/tasks/**`, `/review/**`; `INTERN` → `/intern/**`; `COORDINATOR` → `/coordinator/**`.
- **Schema drift:** Do not change PostgreSQL tables casually; align with **`docs/data-models.md`** and the **Alembic** workflow when it owns migrations.
- **Degraded Ollama:** Mentor flows must survive LLM outage (banner, publish rules) — mirror NFR from product docs.
- **Optional snapshots:** Do not delete arbitrary trees in automated passes without human confirmation.

---

## Usage Guidelines

**For AI agents**

- Read this file and **`docs/index.md`** before coding; use **`docs/api-contracts.md`** for routes.
- Implement new features only in **`src/examai/`**.
- Prefer **stricter** security and data-handling when uncertain.

**For humans**

- Bump **`requires-python`** and **`.python-version`** together when raising the floor.
- Re-run **GPC** after major stack or layout changes.
- Trim redundant rules over time so this file stays lean.

_Last updated: 2026-04-15_
