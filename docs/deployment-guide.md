# Deployment Guide — Examinai

**Target stack:** **Python app** (Uvicorn) + **PostgreSQL** + **Ollama** — same three-service **pilot** topology as the product docs (FR32). **Implementation in this repo:** add a **Python Dockerfile / Compose** at the repo root when ready.

**Reference only (`JAVA_APP/` — if the snapshot exists locally):** A **Spring Boot** image and **`JAVA_APP/docker-compose.yml`** may exist (build context **`JAVA_APP/`**). Use them to **validate compose wiring** (ports, env vars, Ollama pull behavior) — **not** the long-term production path; the Python image replaces the `app` service when ready.

## Topology

| Service | Active target | Reference (today) |
|---------|----------------|-------------------|
| App | **Python / Uvicorn** — port **8080** | JVM image from **`JAVA_APP/Dockerfile`** |
| `db` | **PostgreSQL** (e.g. `postgres:16-alpine`) | Same in reference Compose |
| `llm` | **Ollama** (`ollama/ollama`) | Same in reference Compose |

Reference file: **`JAVA_APP/docker-compose.yml`**.

## Dockerfile (reference — Java)

The checked-in multi-stage build uses **Temurin 21**, runs **`./mvnw package`**, and ships a **JAR**. **Do not treat this as the long-term production path** for new work—mirror the same **8080** health and env contract in the **Python** image when you add it.

## Compose environment

Typical variables — document names in this guide and/or repo **`.env.example`**; **`JAVA_APP/.env.example`** (if present) may be used **only as a naming cross-reference**:

- **Database** — JDBC-style `SPRING_DATASOURCE_*` in reference Java stack; Python uses **`EXAMINAI_DATABASE_URL`** (SQLAlchemy DSN, e.g. `postgresql+psycopg://…`).
- **`EXAMINAI_USE_LIQUIBASE`** — set to **`1`** in the Compose **`app`** service so **Liquibase** runs **`db/changelog/`** before the server starts; do not rely on SQLAlchemy `create_all` for that deployment.
- **`EXAMINAI_ADMIN_INITIAL_PASSWORD`** / **`EXAMINAI_ADMIN_EMAIL`** — optional first **administrator** bootstrap after migrations (see **README-Python.md**).
- **`OLLAMA_BASE_URL`** — inside Compose use **`http://llm:11434`** (not `127.0.0.1`).
- **`OLLAMA_MODEL`** — must match a pulled model on the `llm` service.
- **`GIT_PROVIDER_BASE_URL`**, **`GIT_PROVIDER_TOKEN`** — for mentor Git fetch flows.

The **`llm`** service entrypoint in reference Compose may run **`ollama pull`** — first boot can take a long time.

## Health checks

```bash
curl -sSf http://localhost:8080/actuator/health
```

(Contract-documented JSON shape: `{"status":"UP"}` — keep for operator parity.)

## macOS Docker note

When the snapshot exists, **`JAVA_APP/README.md`** documents **Homebrew `docker`** vs **Docker Desktop** credential issues and **`JAVA_APP/scripts/docker-with-desktop-path.sh`** — useful for any Compose workflow on macOS, including a future Python-based Compose file.

## Production considerations (high level)

- Secrets management and **`prod`-style** settings—not dev defaults.
- Ollama: control auto-pull vs pre-baked images per ops policy (legacy Java used `SPRING_AI_OLLAMA_INIT_PULL_MODEL_STRATEGY`; Python stack should expose an equivalent policy).
- TLS termination and session hardening are environment-specific.

## Operator runbook

- **Python / FastAPI:** follow [development-guide.md](./development-guide.md) and [README-Python.md](../README-Python.md).
- **Optional Java snapshot:** **`JAVA_APP/README.md`** (if present) — JVM runbook and degraded-LLM notes as **reference**.

---

_Updated: Python stack as deployment target; Java Compose/Dockerfile as reference._
