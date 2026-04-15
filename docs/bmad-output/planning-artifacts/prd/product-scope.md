# Product Scope

## MVP - Minimum Viable Product

- **Parity slice:** Core **intern + mentor** loop for at least one task/submission path: list tasks, submit coordinates, mentor workspace with fetch + draft + publish (AI optional).
- **Auth & roles:** Role-gated URLs consistent with **`docs/api-contracts.md`** and **`project-context.md`** (session strategy TBD but behavior matches).
- **Ops:** Health endpoint; documented run via **`README-Python.md`**; DB connectivity.
- **Schema:** Read/write against existing tables per **`docs/data-models.md`** without undefined migration authority (optional Liquibase YAML under **`JAVA_APP/`** — if present — is **DDL reference only** until **Alembic** owns revisions explicitly).
- **Testing:** No requirement to **create or run** automated tests during MVP build; aligns with [Delivery and testing strategy](#delivery-and-testing-strategy).

## Growth Features (Post-MVP)

- **Full route parity** across admin, coordinator, review queue, and edge cases in **`api-contracts.md`**.
- **Alembic** as sole migration authority with a clean cutover plan from any **legacy DDL reference** (e.g. optional Liquibase snapshot paths).
- **Hardening:** Rate limiting, observability, richer degraded-mode semantics per integration (Git/Ollama).
- **UX:** Template parity then **targeted UX improvements** (not 1:1 legacy friction).
- **Automated tests:** Introduced **after** core implementation milestones, covering critical paths, auth/role gates, and integrations.

## Vision (Future)

- **Analytics** for programs (time-to-feedback, cohort comparisons) where data policy allows.
- **Deeper compliance packaging** (FERPA/COPPA, retention, export/delete) once personas and jurisdictions are fixed.
- **Optional** richer AI (multiple models, policy per program) still under **audit** and **human publish** gate.
