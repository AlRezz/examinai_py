# Story 8.10: Compose and docs — Git provider env for mentor fetch

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer or operator running the Docker stack**,  
I want **`GIT_PROVIDER_BASE_URL` (and optional `GIT_PROVIDER_TOKEN`) passed into the `app` service** and **documented next to the other stack variables**,  
So that **mentor submission workspace Git fetch works** after setting values in `.env` — instead of seeing *“Git provider is not configured…”* when those vars are only defined on the host.

## Context

- **Runtime check:** `get_settings().git_provider_base_url` must be non-empty or fetch fails with flash `GIT_NOT_CONFIGURED` and the UI copy in `src/examai/templates/tasks/fragments/git-retrieval.html` (“Set `GIT_PROVIDER_BASE_URL`…”).
- **Config:** `src/examai/config.py` reads `GIT_PROVIDER_BASE_URL`, `GIT_PROVIDER_TOKEN`, `GIT_PROVIDER_TIMEOUT_SECONDS` (defaults aligned with `.env.example`).
- **Gap:** Root `docker-compose.yml` **`app.environment`** lists DB, Ollama, Liquibase, admin bootstrap, and secret — **it does not reference `GIT_PROVIDER_*`**. Docker Compose only substitutes variables that appear in the compose file; a line in `.env` alone does **not** inject env into a container unless passed through `environment:` or `env_file:`.

## Acceptance Criteria

1. **Compose passthrough**  
   **Given** a `.env` next to `docker-compose.yml` defines `GIT_PROVIDER_BASE_URL` (and optionally `GIT_PROVIDER_TOKEN`, `GIT_PROVIDER_TIMEOUT_SECONDS`)  
   **When** `docker compose up` runs the **`app`** service  
   **Then** the application process sees those variables (verify with `docker compose exec app env | grep GIT_PROVIDER` or equivalent).

2. **Sensible defaults**  
   **Then** unset variables do not break startup: use Compose substitution such as `${GIT_PROVIDER_BASE_URL:-}` / `${GIT_PROVIDER_TOKEN:-}` so missing keys do not error at parse time; match app defaults for timeout (document whether `GIT_PROVIDER_TIMEOUT_SECONDS` is omitted when unset or explicitly defaulted — must align with `config.py`).

3. **Documentation parity**  
   **Then** **[README-Python.md](../../README-Python.md)** mentions Git provider env in the same spirit as Ollama (mentor flows): at minimum one short subsection or table row stating that **mentor Git fetch** needs `GIT_PROVIDER_BASE_URL` (e.g. `https://api.github.com` for GitHub’s REST API) and that **`GIT_PROVIDER_TOKEN`** is optional for public repos but helps rate limits / private repos — with pointers to **[docs/deployment-guide.md](../../docs/deployment-guide.md)** and **[docs/development-guide.md](../../docs/development-guide.md)**.

4. **`.env.example`**  
   **Then** comments clarify that for **Docker Compose**, these variables must be listed in **`.env`** at the repo root (and are now wired through **`docker-compose.yml`**); keep **secrets out of git**.

5. **No application logic change required**  
   **Then** implementation is **Compose + docs + `.env.example`** unless a small comment in `docker-compose.yml` is needed; **do not** change `Settings` / fetch behavior in this story.

## Tasks / Subtasks

- [ ] Update **`docker-compose.yml`** — under **`app.environment`**, add `GIT_PROVIDER_BASE_URL`, `GIT_PROVIDER_TOKEN`, and `GIT_PROVIDER_TIMEOUT_SECONDS` with `${…}` passthrough per AC1–2.
- [ ] Update **`.env.example`** — clarify Docker usage for Git provider block (AC4).
- [ ] Update **`README-Python.md`** — mentor / env section per AC3 (link to existing guides).
- [ ] Optional tighten **`docs/deployment-guide.md`** Compose bullet list if anything is now redundant or needs a one-line cross-reference to Compose wiring.
- [ ] Manual smoke: set `GIT_PROVIDER_BASE_URL=https://api.github.com` in `.env`, `docker compose up`, confirm container env and that mentor workspace no longer shows “not configured” for the **configuration** case (fetch may still fail on bad repo/SHA — that is OK for this story).

## Dev Notes

### Architecture / guardrails

- **Git client:** HTTP client to GitHub REST v3–compatible API — see **[docs/architecture.md](../../docs/architecture.md)** (Git provider section).
- **Secrets:** never commit real `GIT_PROVIDER_TOKEN`; document copy-paste from `.env` only.
- **Epic 8 scope:** operations and documentation; **Epic 4** already implemented mentor fetch behavior.

### Files to touch (expected)

| File | Change |
|------|--------|
| `docker-compose.yml` | Add `GIT_PROVIDER_*` to `app.environment`. |
| `.env.example` | Clarify Compose passthrough for mentor fetch. |
| `README-Python.md` | Document Git provider env for Docker / mentor flows. |
| `docs/deployment-guide.md` | Minor alignment if needed (already lists `GIT_PROVIDER_*`). |

### References

- Flash + route logic: `src/examai/mentor_workspace_routes.py` (`GIT_NOT_CONFIGURED` when `not settings.git_provider_base_url`).
- UI fragment: `src/examai/templates/tasks/fragments/git-retrieval.html`.
- Settings: `src/examai/config.py` — `git_provider_*` fields.
- Prior mentor story: [_bmad-output/implementation-artifacts/4-3-trigger-git-fetch-with-visible-state.md](./4-3-trigger-git-fetch-with-visible-state.md).

### Previous story intelligence

- **8.9** (welcome page) is UI-only on `/` — no conflict.
- **8.1 / 8.4–8.7** established README and Compose env patterns; follow the same tone and cross-links to **`docs/deployment-guide.md`**.

## Dev Agent Record

### Agent Model Used

_(filled on implementation)_

### Debug Log References

### Completion Notes List

### File List

---

**Context engine notes:** Ultimate story context created for Epic 8.10 — Compose env passthrough fixes “Git provider is not configured” when vars exist only in host `.env`.
