# Examinai — Project Overview

**Date:** 2026-04-15  
**Type:** Backend monolith with **server-rendered web UI**  
**Active architecture:** **FastAPI** + **Jinja2** + **SQLAlchemy 2** + **PostgreSQL** (see [architecture.md](./architecture.md))

## Executive summary

Examinai supports **structured internship examination workflows**: program tasks assigned to interns, **version-control submissions** (repo + ref + path scope), **mentor review** with optional **Git-backed source retrieval** and **LLM-assisted draft assessments** (Ollama), and **published feedback** visible to interns and coordinators.

**Implementation focus:** the **Python** package **`examai`** at `src/examai/`. **`JAVA_APP/`** (if present) is **reference only** — Spring Boot snapshot for HTTP/template/DDL/integration comparison; **not** an implementation target.

## Classification

| Attribute | Value |
|-----------|--------|
| Repository type | Monolith |
| **Primary language** | **Python 3.9+** (package `examai`) |
| **Primary framework** | **FastAPI**, Jinja2, SQLAlchemy 2, Alembic (migrations — future sole owner) |
| UI | **Jinja2** (target) + Bootstrap/static parity — legacy **Thymeleaf** in `JAVA_APP/` as reference |
| Database | PostgreSQL 16 (typical) |
| LLM | **Ollama** (httpx client from Python; legacy used Spring AI) |
| Migrations | **[data-models.md](./data-models.md)** + **Alembic** (forward); Liquibase under **`JAVA_APP/`** (if present) = **DDL reference only** |
| **Legacy reference** | Java 21, Spring Boot 3.5, Thymeleaf, JPA — **`JAVA_APP/`** only |

## Technology stack summary (active)

| Category | Technology |
|----------|------------|
| Runtime | Python ≥ 3.9 |
| Web | FastAPI, Uvicorn, Jinja2, python-multipart |
| Security | Session-based auth, role URL gates (parity with legacy) |
| Data | SQLAlchemy 2, psycopg 3, PostgreSQL |
| HTTP clients | httpx (Git provider, Ollama) |
| AI | Ollama (integration module — no raw LLM in route handlers) |
| Build / deps | `pyproject.toml`, `pip install -e ".[dev]"` |
| Containers | Python image TBD at repo root; **`JAVA_APP/Dockerfile`** (if snapshot exists) = **reference** JVM build |

## Key features (product-level)

- Multi-role access: **intern**, **mentor**, **administrator**, **coordinator**
- Task CRUD and **intern assignment**
- Per-submission **Git fetch** and **normalized source** for review/AI
- **Mentor review drafts** and **published reviews** with snapshot provenance
- **AI draft** generation with **audit** (`model_invocations`, `ai_drafts`)
- **`/actuator/health`** for operations

## Architecture highlights

- **No separate frontend repo** — HTML server-rendered.
- **Integration boundaries:** Git and Ollama isolated in **`examai.integration.*`** (or equivalent), mirroring legacy `integration.*` separation.
- **Schema:** **[data-models.md](./data-models.md)** + PostgreSQL; **Alembic** when it owns migrations. Liquibase under **`JAVA_APP/`** (if present) is **supplemental DDL reference only**.

## Development overview

See [development-guide.md](./development-guide.md) for setup, run, and test commands. Summary:

- **Install:** `python3 -m venv .venv` → `pip install -e ".[dev]"`
- **Run:** `uvicorn examai.main:app --reload --host 127.0.0.1 --port 8080`

## Links

| Document | Description |
|----------|-------------|
| [index.md](./index.md) | Master documentation index |
| [architecture.md](./architecture.md) | Technical architecture (Python + reference) |
| [api-contracts.md](./api-contracts.md) | HTTP routes and form actions |
| [data-models.md](./data-models.md) | Schema summary |
| [source-tree-analysis.md](./source-tree-analysis.md) | Annotated tree |
| [component-inventory.md](./component-inventory.md) | UI inventory (Jinja target + Thymeleaf reference) |
| [development-guide.md](./development-guide.md) | Local development (Python) |
| [deployment-guide.md](./deployment-guide.md) | Docker / topology |
| [../JAVA_APP/README.md](../JAVA_APP/README.md) | **Reference** — operator readme (**if** `JAVA_APP/` snapshot exists) |

---

_Updated: Python-first; Java snapshot as reference._
