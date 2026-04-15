# Story 8.4: README-Python — run the application as a Docker image

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,  
I want **`README-Python.md` to explain how to build and run the application container**,  
so that **I can start the server from Docker without guessing compose service names or ports**.

## Acceptance Criteria

1. **Build & run**  
   **Given** **Story 8.1** is implemented (Dockerfile / compose exist)  
   **When** I follow **`README-Python.md`**  
   **Then** I can **build** the app image and **run** it (standalone `docker run` and/or **`docker compose up app`** — match what the repo actually supports).

2. **Environment**  
   **Then** required env vars for the app container are listed (minimum **`DATABASE_URL`**, **`OLLAMA_BASE_URL`** when LLM used) with pointers to **`.env.example`**.

3. **Health check**  
   **Then** the doc shows **`curl`** (or equivalent) against **`GET /actuator/health`** on the published port (default **8080**) and expected JSON per contract.

4. **Accuracy**  
   **Then** service names, ports, and paths **match** the checked-in **`Dockerfile`** / **`docker-compose.yml`** (no stale placeholders).

## Tasks / Subtasks

- [ ] Add a **“Run with Docker”** (or similarly named) section to **[README-Python.md](../../README-Python.md)**.
- [ ] Cross-link **[docs/deployment-guide.md](../../docs/deployment-guide.md)** for full topology.
- [ ] Keep existing **local venv** instructions intact; Docker is an **additional** path, not a replacement for dev workflow unless stated.

## Dev Notes

### Guardrails

- Do not duplicate entire deployment guide — **summarize** and link.
- Preserve **[README-Python.md](../../README-Python.md)** tone: short, command-first.

### Dependencies

- **Depends on:** **8.1** (real compose/Dockerfile names and ports).

### References

- [README-Python.md](../../README-Python.md)  
- [docs/deployment-guide.md](../../docs/deployment-guide.md)  
- [8-1-dockerfiles-and-docker-compose-for-app-database-and-llm.md](./8-1-dockerfiles-and-docker-compose-for-app-database-and-llm.md)

### Previous story intelligence

- **8.1–8.3** define the runnable stack; this story is **documentation only** for the **app** slice.

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

---

**Context engine notes:** Ultimate story context created for Epic 8.4.
