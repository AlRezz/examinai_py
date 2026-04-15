# Story 8.3: Liquibase migrations on application startup

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **operator**,  
I want **Liquibase to apply changelogs when the application starts**,  
so that **schema stays aligned with code in every environment that runs the container**.

## Acceptance Criteria

1. **Run on boot**  
   **Given** the database is reachable from the app container  
   **When** the application process starts (entrypoint script or documented wrapper)  
   **Then** **Liquibase** runs and applies **pending** changesets.

2. **Fail fast**  
   **Then** if Liquibase fails, the process **exits non-zero** with **clear logs** (no silent continue into Uvicorn with a broken schema).

3. **Changelog location**  
   **Then** changelogs live under a **versioned path** in the repo (e.g. `db/changelog/`) and are **copied** or **mounted** into the image as appropriate; master changelog file name documented.

4. **Coordination with 8.2**  
   **Then** document and implement: **Liquibase** owns **DDL**; **init seed** from **8.2** runs only after schema exists (order: migrations → seed — adjust **8.2** delivery mechanism if init scripts ran too early).

5. **Connection**  
   **Then** Liquibase uses the same **`DATABASE_URL`** (or JDBC URL derived from it) as the app; credentials are **not** logged.

## Tasks / Subtasks

- [ ] Add **Liquibase** CLI to the image **or** invoke via **Java-free** distribution (official Liquibase CLI / Docker sidecar pattern — pick one, document tradeoffs).
- [ ] Author or **port** baseline changelog: align tables with **[docs/data-models.md](../../docs/data-models.md)**. If **`JAVA_APP/.../db/changelog/`** exists locally, use as **DDL reference only** for parity — **do not** depend on JAVA_APP at runtime.
- [ ] Wire **entrypoint** script: `liquibase update` (or equivalent) **then** `uvicorn examai.main:app ...`.
- [ ] Update **`docs/data-models.md`** and/or **`_bmad-output/project-context.md`** **one paragraph** if migration authority policy changes (Liquibase for container deploy vs prior Alembic-only notes).
- [ ] Integration smoke: bring up compose, verify migration runs, app serves **health**.

## Dev Notes

### Architecture / guardrails — **must read**

- **Project docs** previously stated **Alembic** would own forward revisions and **Liquibase** under `JAVA_APP/` was **reference only**. **This epic explicitly requires Liquibase at startup** — implementation **must** reconcile:
  - Update canonical docs to match reality after this lands, **or**
  - Implement Liquibase only for Docker bootstrap and keep Alembic for dev (only if explicitly documented — avoid two conflicting DDL sources long-term).
- Prefer **single** schema authority going forward; flag **technical debt** if both Liquibase and Alembic exist.

### Dependencies

- **After:** **8.1** (image/compose). **Coordinates with:** **8.2** (seed order).

### References

- [docs/data-models.md](../../docs/data-models.md)  
- [docs/architecture.md](../../docs/architecture.md) — migration notes  
- [8-2-database-init-scripts-with-administrator-seed.md](./8-2-database-init-scripts-with-administrator-seed.md)

### Previous story intelligence

- **8.1** establishes how the app container starts — extend entrypoint there or replace with `docker-entrypoint.sh`.

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

---

**Context engine notes:** Ultimate story context created for Epic 8.3 — migration authority vs existing docs is the main architectural decision.
