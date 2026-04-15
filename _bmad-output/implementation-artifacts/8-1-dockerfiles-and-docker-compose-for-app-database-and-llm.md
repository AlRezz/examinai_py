# Story 8.1: Dockerfiles and Docker Compose for app, database, and LLM

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **operator or developer**,  
I want **Dockerfile(s) and a `docker-compose` definition** that run the FastAPI app, PostgreSQL, and the LLM service,  
so that **I can reproduce the full stack locally or in a lab without manual installs**.

## Acceptance Criteria

1. **Compose topology**  
   **Given** the repository contains the new container definitions  
   **When** prerequisites are met (documented `.env` / env file)  
   **Then** `docker compose` (or documented equivalent) starts **application**, **database**, and **LLM** services with **stable service names** and **documented host ports** (align with **[docs/deployment-guide.md](../../docs/deployment-guide.md)** — app **8080**, Postgres default image port, Ollama **11434**).

2. **App configuration**  
   **Then** the app container receives **`DATABASE_URL`** (or equivalent DSN) and **`OLLAMA_BASE_URL`** via environment variables; inside Compose **`OLLAMA_BASE_URL`** uses the **`llm` service hostname** (e.g. `http://llm:11434`), not `127.0.0.1` per deployment guide.

3. **Persistence / mounts**  
   **Then** volumes or bind mounts exist for **Postgres data** and (if policy requires) **Ollama model storage**, so restarts do not lose DB state unnecessarily.

4. **Build context**  
   **Then** the Python image builds from **`pyproject.toml`** / `src/examai/` (editable install or production install pattern per team choice) and runs **Uvicorn** against **`examai.main:app`** (see **[README-Python.md](../../README-Python.md)**).

5. **Reference parity**  
   **Then** wiring is consistent with **[docs/deployment-guide.md](../../docs/deployment-guide.md)** and, if **`JAVA_APP/docker-compose.yml`** exists locally, **only** as **cross-check** for ports/env names — **do not** ship the JVM app as the active `app` service.

## Tasks / Subtasks

- [ ] Add root **`Dockerfile`** for the Python app (multi-stage optional); expose **8080**; non-root user if practical.
- [ ] Add **`docker-compose.yml`** (and optionally **`compose.override.yml`** for dev) with services **`app`**, **`db`** (PostgreSQL), **`llm`** (Ollama image).
- [ ] Add **`.env.example`** at repo root listing **`DATABASE_URL`**, **`OLLAMA_BASE_URL`**, **`OLLAMA_MODEL`**, and other vars from **[docs/deployment-guide.md](../../docs/deployment-guide.md)** / **[docs/development-guide.md](../../docs/development-guide.md)**.
- [ ] Document **`depends_on`** / health-aware startup so the app does not connect before DB is accepting connections (simple retry in app or `healthcheck` + condition — choose one pattern and document).
- [ ] Smoke: **`curl` health** — `GET /actuator/health` returns contract JSON (**[docs/api-contracts.md](../../docs/api-contracts.md)**, **[project-context](../project-context.md)**).

## Dev Notes

### Architecture / guardrails

- **Active code** only in **`src/examai/`** — see **[project-context](../project-context.md)**.
- **Health:** preserve **`{"status":"UP"}`** (or contract-documented shape) on **`GET /actuator/health`**.
- **Secrets:** never bake real credentials into images; use env / Docker secrets.

### Dependencies

- **Epic 8.2** will add DB init scripts — leave **`docker-entrypoint-initdb.d`** mount or path convention ready if Postgres init is file-based.
- **Epic 8.3** will add migration startup — entrypoint may later chain **Liquibase** (or documented runner) before Uvicorn; keep extension point clear in comments.

### References

- [docs/deployment-guide.md](../../docs/deployment-guide.md) — topology, env names, Ollama notes  
- [docs/development-guide.md](../../docs/development-guide.md) — local Postgres Docker example  
- [README-Python.md](../../README-Python.md) — run command baseline  
- [_bmad-output/planning-artifacts/epics.md](../planning-artifacts/epics.md) — Epic 8

### Previous story intelligence

- First story of Epic 8 — no prior epic-8 artifact; follow patterns from **[7-1-coordinator-index-and-case-record.md](./7-1-coordinator-index-and-case-record.md)** for doc links and test layout.

## Dev Agent Record

### Agent Model Used

_(filled on implementation)_

### Debug Log References

### Completion Notes List

### File List

---

**Context engine notes:** Ultimate story context created for Epic 8.1 — comprehensive developer guide for container topology.
