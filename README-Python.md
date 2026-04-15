# Examinai (Python)

Server-rendered migration target: **FastAPI** + **Jinja2**, **SQLAlchemy 2** + **Alembic**, **PostgreSQL** via **psycopg 3**, **httpx** for Git + Ollama calls.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Run (development)

```bash
uvicorn examai.main:app --reload --host 127.0.0.1 --port 8080
```

Health (Spring-compatible path for operators):

```bash
curl -sSf http://127.0.0.1:8080/actuator/health
```

## Reference

- HTTP contract: `docs/api-contracts.md`
- Legacy app: `JAVA_APP/` (gitignored local snapshot)
- Agent rules: `_bmad-output/project-context.md`
