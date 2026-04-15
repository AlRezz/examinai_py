# Development Guide — Examinai

Development uses the **Python** stack at the repo root: package **`examai`** under `src/examai/`.

## Prerequisites

- **Python ≥ 3.9** (prefer **3.12+** locally; see `.python-version` if present)
- **pip** and **venv** (`python3 -m venv`)
- **PostgreSQL** for real DB work (local install or Docker)
- Optional: **Docker Compose v2** for a multi-service stack — see [deployment-guide.md](./deployment-guide.md)

## Setup

From the **repository root** (where `pyproject.toml` lives):

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

This installs the **`examai`** package in editable mode and dev tools (**pytest**, **pytest-cov**).

## Configuration

- **Environment variables** — Use a local **`.env`** file (not committed) for secrets and service URLs. Typical names (wire in code as implemented): database URL/DSN, **`GIT_PROVIDER_BASE_URL`**, **`GIT_PROVIDER_TOKEN`**, **`OLLAMA_BASE_URL`**, **`OLLAMA_MODEL`**, and any **`EXAMINAI_*`** tuning. Add a committed **`.env.example`** at the repo root when the project standardizes names.
- **Application code** — `src/examai/` (entry: **`examai.main:app`**).

Do not commit tokens or production passwords.

## Local database (quick)

```bash
docker run -d --name examinai-pg \
  -e POSTGRES_USER=examinai \
  -e POSTGRES_PASSWORD=examinai \
  -e POSTGRES_DB=examinai \
  -p 5432:5432 \
  postgres:16-alpine
```

Point the app at **`postgresql://examinai:examinai@localhost:5432/examinai`** (or your overrides) once SQLAlchemy/Alembic wiring is in place.

**Schema:** See [data-models.md](./data-models.md) for tables and migration notes (Alembic vs existing changelogs).

## Run the application (development)

```bash
uvicorn examai.main:app --reload --host 127.0.0.1 --port 8080
```

Health check:

```bash
curl -sSf http://127.0.0.1:8080/actuator/health
```

## Tests

With the **`[dev]`** extra installed:

```bash
pytest
```

Coverage (optional):

```bash
pytest --cov=examai --cov-report=term-missing
```

Project planning may defer **mandatory** automated test gates during early work; see **`_bmad-output/planning-artifacts/prd/index.md`** (sharded PRD) if that applies to your sprint.

## Ollama (optional — AI flows)

- Set **`OLLAMA_BASE_URL`** and model selection as wired in code (e.g. **`OLLAMA_MODEL`**).
- On the host: `ollama pull <tag>` so the model exists before mentor AI-draft flows.

## Git integration (optional)

- **`GIT_PROVIDER_BASE_URL`** (e.g. `https://api.github.com`)
- **`GIT_PROVIDER_TOKEN`** for private repositories or higher API rate limits

## Project layout (for developers)

See [source-tree-analysis.md](./source-tree-analysis.md).

| Path | Role |
|------|------|
| `src/examai/` | FastAPI app, routes, services |
| `tests/` | **pytest** |
| `docs/` | HTTP contract, data models, guides |

## Related documentation

- [README-Python.md](../README-Python.md) — short copy-paste setup
- [api-contracts.md](./api-contracts.md) — browser HTTP surface
- **`_bmad-output/project-context.md`** — AI/agent implementation rules
