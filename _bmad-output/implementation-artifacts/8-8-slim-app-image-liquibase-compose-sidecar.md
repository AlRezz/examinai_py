# Story 8.8: Slim app image — Liquibase Compose sidecar (no OpenJDK in app)

Status: done

## Story

As an **operator or developer**,  
I want the **application Docker image to stay Python-only** while **Liquibase** still applies **`db/changelog/`** reliably,  
So that **image builds do not bundle OpenJDK**, **failed Liquibase zip layouts do not break `docker build`**, and **migrations remain ordered before the app**.

## Root cause (build failure)

The previous **`Dockerfile`** assumed the Liquibase OSS zip extracted to **`/opt/liquibase-4.29.2`**. Many releases extract to a different top-level directory (e.g. **`liquibase`**), so **`mv /opt/liquibase-4.29.2 /opt/liquibase`** failed with **exit code 1** during **`RUN`**.

## Resolution

- **`db-migrate`** service: **`liquibase/liquibase:4.29`** with **`db/changelog`** bind-mounted to **`/changelog`**; runs **`update`** after **`db`** is healthy.
- **`app`**: **`depends_on: db-migrate`** with **`condition: service_completed_successfully`** (requires modern Docker Compose).
- **`Dockerfile`**: Python + **`pip install`** only; no **`apt`** OpenJDK, no Liquibase zip.
- **`scripts/docker-entrypoint.sh`**: starts Uvicorn only; **`examai.liquibase_cli`** remains for optional host runs.

## References

- `docker-compose.yml`, `Dockerfile`, `README-Python.md`, `docs/deployment-guide.md`

## Dev Agent Record

### Completion Notes List

- Implemented Compose **`db-migrate`** + slim **`Dockerfile`**; docs updated.

### File List

- `docker-compose.yml`, `Dockerfile`, `scripts/docker-entrypoint.sh`, `README-Python.md`, `docs/*`, `_bmad-output/project-context.md`
