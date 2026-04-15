# Story 8.2: Database init scripts with administrator seed

Status: backlog

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **operator**,  
I want **SQL (or scripted) init** that creates baseline schema expectations and an **initial administrator account**,  
so that **a fresh database container is usable for first login without manual SQL**.

## Acceptance Criteria

1. **Init hook**  
   **Given** Postgres starts with an empty data volume  
   **When** the container runs init (e.g. **`/docker-entrypoint-initdb.d`**)  
   **Then** init scripts are applied in a documented order.

2. **Schema vs migrations (critical)**  
   **Then** init does **not** duplicate or fight **Liquibase** from **Story 8.3**: either (a) init only **reference data** (roles + admin user) after Liquibase owns tables, or (b) init creates **nothing** that Liquibase will also create — **document the split** (DDL vs seed). If tables are created only by Liquibase, seed may need to run **after** migrations (separate job or app bootstrap) — **call out** in implementation notes.

3. **Administrator user**  
   **Then** at least one user exists with the **`administrator`** role (see **`roles.name`** in **[docs/data-models.md](../../docs/data-models.md)**) and can authenticate per app expectations (**`users.email`**, **`password_hash`** BCrypt).

4. **Secrets**  
   **Then** admin password comes from **environment** (e.g. `ADMIN_INITIAL_PASSWORD` or secret file), **not** committed plaintext in repo; document required vars in **`.env.example`**.

5. **Idempotency / re-run**  
   **Then** behavior on **recreated** volume vs **existing** DB is documented (init scripts run only on first init for standard Postgres image).

## Tasks / Subtasks

- [ ] Define **seed strategy** with **8.3**: Liquibase creates schema → seed admin in SQL vs seed via small script after migrations.
- [ ] Ensure **`roles`** rows exist for **`administrator`** (and other role names the app expects per **[docs/data-models.md](../../docs/data-models.md)**) before attaching **`user_roles`**.
- [ ] Add SQL or shell init under a versioned directory (e.g. `db/init/`) mounted into Postgres **`docker-entrypoint-initdb.d`** **or** document **alternative** if seed moves to app startup.
- [ ] Hash password using **BCrypt** consistent with **`src/examai/`** auth code — locate existing hash utility and **reuse** (no reinvented crypto).
- [ ] Add tests or manual checklist: first login as admin with env-provided password (document in story completion).

## Dev Notes

### Architecture / guardrails

- **Tables:** **`users`**, **`roles`**, **`user_roles`** — **[docs/data-models.md](../../docs/data-models.md)**.
- **Role names:** seeded values include `intern`, `mentor`, `administrator`, `coordinator`.
- **Conflict with docs:** Historically **Alembic** was described as owning forward migrations; **Epic 8** adds **Liquibase** in **8.3**. Coordinate so this story only **seeds** data compatible with whatever creates DDL.

### Dependencies

- **Requires:** **8.1** Compose/DB volume path known.  
- **Blocks / coordinates with:** **8.3** — migration order vs seed order.

### References

- [docs/data-models.md](../../docs/data-models.md) — `users`, `roles`, `user_roles`  
- [8-1-dockerfiles-and-docker-compose-for-app-database-and-llm.md](./8-1-dockerfiles-and-docker-compose-for-app-database-and-llm.md)  
- [8-3-liquibase-migrations-on-application-startup.md](./8-3-liquibase-migrations-on-application-startup.md)

### Previous story intelligence

- From **8.1:** Use same **`db` service** name and volume so init runs on fresh DB.

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

---

**Context engine notes:** Ultimate story context created for Epic 8.2 — seed + Liquibase coordination is the highest-risk area; resolve before merging.
