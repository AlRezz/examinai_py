# Examinai (Python)

Server-rendered migration target: **FastAPI** + **Jinja2**, **SQLAlchemy 2** + **PostgreSQL** via **psycopg 3**, **httpx** for Git + Ollama calls.

Container deployments use **Liquibase** for schema (`db/changelog/`) on application startup; local SQLite tests use SQLAlchemy `create_all` instead.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Run (development, host Python)

```bash
uvicorn examai.main:app --reload --host 127.0.0.1 --port 8080
```

Health (contract path for operators):

```bash
curl -sSf http://127.0.0.1:8080/actuator/health
```

## Run with Docker Compose (full stack)

Build and start **app** (FastAPI on **8080**), **db** (PostgreSQL on **5432**), and **llm** (Ollama on **11434**):

```bash
docker compose up --build
```

- **Application URL:** `http://localhost:8080`
- **Health:** `GET http://localhost:8080/actuator/health` → `{"status":"UP"}`

The **app** service sets **`EXAMINAI_USE_LIQUIBASE=1`**: Liquibase applies `db/changelog/` before Uvicorn starts. Set **`EXAMINAI_ADMIN_INITIAL_PASSWORD`** (and optionally **`EXAMINAI_ADMIN_EMAIL`**) in `.env` so the first **administrator** account is created after migrations (see `.env.example`). Init scripts under **`db/init/`** are mounted into Postgres and run **once** on an empty data volume; they do **not** replace Liquibase DDL.

## Run the application image alone

From the repository root (after `docker compose build app`):

```bash
docker compose run --rm --service-ports app
```

Or build and run the image directly (you must supply **`EXAMINAI_DATABASE_URL`**, **`EXAMINAI_USE_LIQUIBASE`** if using Liquibase-managed Postgres, **`EXAMINAI_SECRET_KEY`**, **`OLLAMA_BASE_URL`**, etc.):

```bash
docker build -t examinai:local .
docker run --rm -p 8080:8080 \
  -e EXAMINAI_USE_LIQUIBASE=1 \
  -e EXAMINAI_DATABASE_URL=postgresql+psycopg://user:pass@host:5432/examinai \
  -e EXAMINAI_SECRET_KEY=change-me \
  -e OLLAMA_BASE_URL=http://llm-host:11434 \
  examinai:local
```

## Run PostgreSQL via Docker

**With Compose (recommended):** the **`db`** service uses `postgres:16-alpine`, persists data in the **`postgres_data`** volume, and publishes **5432**. Connection string for tools on the host:

`postgresql+psycopg://examinai:examinai@localhost:5432/examinai` (adjust user/password if you override them).

**Standalone** (matches [development-guide.md](docs/development-guide.md)):

```bash
docker run -d --name examinai-pg \
  -e POSTGRES_USER=examinai \
  -e POSTGRES_PASSWORD=examinai \
  -e POSTGRES_DB=examinai \
  -p 5432:5432 \
  postgres:16-alpine
```

Point **`EXAMINAI_DATABASE_URL`** at that instance. Without **`EXAMINAI_USE_LIQUIBASE`**, the app can create tables via SQLAlchemy on startup for local experiments; production-style Docker uses Liquibase instead.

## Run the LLM (Ollama) via Docker

**With Compose:** the **`llm`** service is **`ollama/ollama`** with models stored in **`ollama_data`**. The app must use **`OLLAMA_BASE_URL=http://llm:11434`** on the Compose network (not `127.0.0.1`). On first use, pull a model inside the container (can take a long time):

```bash
docker compose exec llm ollama pull llama3.2
```

Set **`OLLAMA_MODEL`** to the tag you pulled. If Ollama is missing or unreachable, mentor AI-draft flows show a **degraded** state; human review still works (see [docs/deployment-guide.md](docs/deployment-guide.md) and FR31–FR32 in the PRD).

## User flows by role

After sign-in, routes follow [docs/api-contracts.md](docs/api-contracts.md). Summary:

| Role | Representative URLs / actions |
|------|-----------------------------|
| **Intern** | `/intern/tasks`, `/intern/tasks/{taskId}`, submit coordinates, `/intern/submissions/{submissionId}/feedback` |
| **Mentor** (or admin on mentor routes) | `/tasks`, `/tasks/new`, assignments, `/tasks/{taskId}/submissions/...` workspace (Git fetch, AI draft, draft review, publish), `/review/queue` |
| **Coordinator** | `/coordinator`, `/coordinator/cases/{submissionId}` |
| **Administrator** | `/admin/users` (list/create/edit users and roles) |

Common: **`/login`**, **`/home`**, **`POST /logout`**. Public health: **`GET /actuator/health`**.

## Reference

- HTTP contract: `docs/api-contracts.md`
- Deployment topology & env names: `docs/deployment-guide.md`
- Optional Spring snapshot: `JAVA_APP/` — **reference only** (often gitignored); use for parity with routes/templates/DDL, not for new features
- Agent rules: `_bmad-output/project-context.md`
