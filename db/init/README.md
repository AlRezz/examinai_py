# PostgreSQL `docker-entrypoint-initdb.d` hook

Scripts in this directory are copied into the **`db`** container at **`/docker-entrypoint-initdb.d`** and run **once** when the data volume is empty.

**Schema (DDL)** is **not** defined here for the Docker stack. The application image runs **Liquibase** on startup (see `db/changelog/`, Epic 8.3) so schema stays aligned with releases.

**Story 8.2 split:**

| Layer | Responsibility |
|-------|----------------|
| **Liquibase** | Creates tables, indexes, constraints (`001-baseline.postgresql.sql`). |
| **App bootstrap** | Seeds reference **`roles`** and optional **administrator** user when `EXAMINAI_ADMIN_INITIAL_PASSWORD` is set (after migrations). |

The optional **`00-prep.sql`** script only prepares the database before the app connects (e.g. harmless validation); it does **not** create application tables.
