# Story 8.5: README-Python — run the database as a Docker image

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,  
I want **`README-Python.md` to document running PostgreSQL via Docker**,  
so that **I can run or troubleshoot the DB in isolation or understand compose networking**.

## Acceptance Criteria

1. **Compose and standalone**  
   **Given** **8.1** defines the **`db`** service  
   **When** I read **`README-Python.md`**  
   **Then** I see how to run Postgres via **`docker compose`** and, if applicable, a **one-off** `docker run` for local-only DB testing.

2. **Connection**  
   **Then** the doc explains **host/port** from host machine vs from **`app` container** (e.g. service name **`db`**, port **5432**).

3. **Persistence**  
   **Then** volume behavior is mentioned (named volume or bind mount) so operators know data survives restarts.

4. **Seed / admin**  
   **Then** brief pointer to **8.2** behavior: first-time init, admin user from env — **no secrets** in README body.

5. **Consistency**  
   **Then** variable names align with **`.env.example`** and **[docs/development-guide.md](../../docs/development-guide.md)**.

## Tasks / Subtasks

- [ ] Extend **[README-Python.md](../../README-Python.md)** with a **Database (Docker)** subsection (or merge into a larger Docker chapter with anchors).
- [ ] Cross-link **[docs/development-guide.md](../../docs/development-guide.md)** existing `docker run` Postgres example if still valid; **dedupe** if redundant.

## Dev Notes

### Dependencies

- **Depends on:** **8.1** (service name, volume). **Cross-reference:** **8.2** (init/seed).

### References

- [docs/development-guide.md](../../docs/development-guide.md)  
- [8-2-database-init-scripts-with-administrator-seed.md](./8-2-database-init-scripts-with-administrator-seed.md)  
- [8-1-dockerfiles-and-docker-compose-for-app-database-and-llm.md](./8-1-dockerfiles-and-docker-compose-for-app-database-and-llm.md)

### Previous story intelligence

- **8.4** may have added a top-level Docker section — **extend** it rather than scattering duplicate prose.

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

---

**Context engine notes:** Ultimate story context created for Epic 8.5.
