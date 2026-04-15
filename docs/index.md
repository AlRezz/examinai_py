# Examinai — Project Documentation Index

**Type:** Migration — **Python** is the **active** implementation (`src/examai/`). **`JAVA_APP/`** (if present) is a **legacy Spring Boot snapshot** (often gitignored) — **reference only** for routes, Thymeleaf templates, Liquibase DDL, integrations, and Compose wiring; **not** a second app to ship or extend for new features.  
**Primary language:** **Python 3.9+**  
**Architecture:** Server-rendered web (**Jinja2** target; **Thymeleaf** in reference tree) + PostgreSQL + Ollama  
**Last updated:** 2026-04-15

## Project overview

Examinai coordinates **tasks**, **intern submissions** (repo coordinates + Git-backed source retrieval), **mentor reviews** (drafts and published outcomes), and **AI-assisted draft assessments** via Ollama. Roles: intern, mentor, administrator, coordinator.

## Quick reference

| Topic | Detail |
|-------|--------|
| **Python stack** | `pyproject.toml` — FastAPI, Jinja2, SQLAlchemy 2, Alembic, psycopg 3, httpx; package **`examai`** under `src/examai/` |
| **Reference (Java)** | Spring Boot 3.5, Thymeleaf, JPA, Liquibase — **`JAVA_APP/`** only, **reference**; no new product work in Java |
| **Entry point** | **`examai.main:app`** (Uvicorn) — default port **8080** |
| **Health** | `GET /actuator/health` |
| **Database** | **Tables:** [data-models.md](./data-models.md) + PostgreSQL; **Alembic** for forward migrations. **Liquibase** under **`JAVA_APP/`** (if snapshot exists) = **DDL reference only** |

## Generated documentation

### Core

- [Project overview](./project-overview.md) — Summary and classification (Python-first)
- [Architecture](./architecture.md) — Active Python design + Java reference
- [Source tree analysis](./source-tree-analysis.md) — Annotated directory layout

### Contracts and data

- [API contracts](./api-contracts.md) — Browser HTTP routes and form actions (not a JSON REST API)
- [Data models](./data-models.md) — Tables and mapping

### UI and operations

- [Component inventory](./component-inventory.md) — Jinja2 target + Thymeleaf reference paths
- [Development guide](./development-guide.md) — Python setup, run, test
- [Deployment guide](./deployment-guide.md) — Topology; Java Compose as reference

### Workflow state

- [project-scan-report.json](./project-scan-report.json) — BMAD document-project scan metadata

## Existing documentation (repository)

| Document | Description |
|----------|-------------|
| [JAVA_APP/README.md](../JAVA_APP/README.md) | **Reference** — legacy operator readme (**only if** `JAVA_APP/` snapshot exists; often gitignored) |
| [_bmad-output/planning-artifacts/](../_bmad-output/planning-artifacts/) | PRD, epics, sprint status (if present) |

## Getting started

**Python (only path for new work):** **[README-Python.md](../README-Python.md)** — `pip install -e ".[dev]"`, then `uvicorn examai.main:app --reload --port 8080`.

**Reference — legacy Java (optional):** JDK 21, Maven — **`JAVA_APP/README.md`** when the snapshot exists (parity checks only; not required for Python delivery).

**Compose / pilot topology:** Three services (app + Postgres + Ollama). **`JAVA_APP/docker-compose.yml`** is **reference** for wiring until a root-level Python Compose file exists — [deployment-guide.md](./deployment-guide.md).

## For AI-assisted development

- **Brownfield PRD / features:** This **index** + `_bmad-output/planning-artifacts/`.
- **UI:** Implement under **`src/examai/`** (Jinja2); use [component-inventory.md](./component-inventory.md); **`JAVA_APP/.../templates/`** (if present) for **reference** naming/layout parity only.
- **Backend / domain:** `src/examai/`; **`_bmad-output/project-context.md`** for agent rules.
- **Integrations:** Implement in Python (`examai.integration.*`); **`JAVA_APP/.../integration/`** is **reference** for behavior and prompts.

---

_Documentation index: Python stack primary; `JAVA_APP/` reference-only when present._
