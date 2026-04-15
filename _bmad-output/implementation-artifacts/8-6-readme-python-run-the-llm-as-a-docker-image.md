# Story 8.6: README-Python — run the LLM as a Docker image

Status: backlog

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,  
I want **`README-Python.md` to document running the LLM (e.g. Ollama) in Docker**,  
so that **AI draft features can be enabled consistently with deployment architecture**.

## Acceptance Criteria

1. **Service**  
   **Given** **8.1** defines the **`llm`** service (Ollama or equivalent)  
   **When** I read **`README-Python.md`**  
   **Then** I see how to start it via compose and the **port** (typically **11434**).

2. **Model pull / first boot**  
   **Then** the doc warns that **first boot** may run **`ollama pull`** and take time (**[docs/deployment-guide.md](../../docs/deployment-guide.md)**).

3. **App wiring**  
   **Then** **`OLLAMA_BASE_URL`** / **`OLLAMA_MODEL`** (or project’s actual env names) are documented; from app container, base URL uses **service DNS** (`http://llm:11434`), from host machine use **`localhost`** with mapped port — **spell out both**.

4. **Degraded behavior**  
   **Then** one sentence points to product behavior when LLM is down (**FR31–FR32**, mentor workspace) and **[docs/architecture.md](../../docs/architecture.md)** or component inventory if needed — no need to duplicate full NFR.

## Tasks / Subtasks

- [ ] Add **LLM / Ollama (Docker)** section to **[README-Python.md](../../README-Python.md)**.
- [ ] Align env var names with **`src/examai/`** integration (grep **`OLLAMA`** in codebase and match docs).

## Dev Notes

### Dependencies

- **Depends on:** **8.1**. Optional cross-link to **5-1** / **5-2** story artifacts for AI behavior context.

### References

- [docs/deployment-guide.md](../../docs/deployment-guide.md) — Ollama, `OLLAMA_BASE_URL`  
- [_bmad-output/planning-artifacts/epics.md](../planning-artifacts/epics.md) — FR31, FR32  
- [8-1-dockerfiles-and-docker-compose-for-app-database-and-llm.md](./8-1-dockerfiles-and-docker-compose-for-app-database-and-llm.md)

### Previous story intelligence

- Match whatever **`llm`** service name and env vars **8.1** shipped.

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

---

**Context engine notes:** Ultimate story context created for Epic 8.6.
