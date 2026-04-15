# Story 5.3: Ollama model missing — clear messaging (404 / not found)

Status: done

## Story

As an **operator or mentor**,  
I want **a clear message when the configured Ollama model is not installed**,  
so that **I know to run `ollama pull` or fix `OLLAMA_MODEL` instead of parsing raw HTTP 404 JSON** — and I can **still save a manual review and publish** (unchanged from 5.2).

## Acceptance Criteria

1. **Actionable copy**  
   **Given** Ollama responds with an error that the requested model is not found (e.g. HTTP 404 with `{"error":"model '…' not found"}`)  
   **When** a mentor requests an AI draft  
   **Then** the flash message explains that the model is missing on the LLM host and points to `ollama pull` / `OLLAMA_MODEL`, without leading with opaque `HTTP 404 from Ollama`.

2. **Human path unchanged**  
   **Then** manual review save and publish remain available (FR32 degraded behavior, FR22–FR23).

## Tasks / Subtasks

- [x] **Client mapping** — `examai.integration.ai`: detect model-not-found payloads on HTTP error responses; raise `OllamaClientError` with operator-facing text including configured model name.
- [x] **Tests** — unit tests for friendly message vs generic HTTP errors.
- [x] **Regression** — existing mentor AI-draft failure path still flashes and redirects.

## Dev Notes

### References

- `src/examai/integration/ai.py` — `ollama_generate`, `OllamaClientError`
- `src/examai/mentor_workspace_routes.py` — `post_ai_draft_assessment` flash on `OllamaClientError`
- Story **5.2** — degraded UX; this story only improves **wording** for the common misconfiguration (wrong/unpulled model).

### Root cause

`OLLAMA_MODEL` (e.g. `deepseek-r1:8b`) must match a model **pulled** on the Ollama server. Ollama returns 404 with a JSON `error` when the tag is missing; the app previously surfaced the raw HTTP detail.

## Dev Agent Record

### Completion Notes List

- Added `_friendly_model_missing_message` in `integration/ai.py` for HTTP error responses whose body indicates a missing model.
- Added `tests/test_ai_ollama.py` for 404 model-not-found vs other HTTP errors.
- **Docker Compose:** `llm` service uses **`scripts/ollama-compose-entrypoint.sh`**; **`OLLAMA_PULL_MODEL`** mirrors host **`OLLAMA_MODEL`** so the model is pulled on **`llm`** start (first run can be slow). Docs: **README-Python.md**, **docs/deployment-guide.md**, **`.env.example`**.

### File List

- `src/examai/integration/ai.py`
- `tests/test_ai_ollama.py`
- `scripts/ollama-compose-entrypoint.sh`
- `docker-compose.yml`
- `README-Python.md`
- `docs/deployment-guide.md`
- `.env.example`

---

**Story completion status:** **done**
