# Deferred work

## Deferred from: code review of 2-1-list-create-and-edit-tasks.md (2026-04-15)

- **Invalid task id shape (non-UUID):** `GET /tasks/{id}/edit` with a malformed id returns FastAPI’s 422 validation response instead of the same HTML error experience as “unknown UUID.” Optional polish if mentors should never see JSON error pages.

## Deferred from: code review of 1-1-public-pages-static-assets-and-webjar-ui-stack.md (2026-04-15)

- **Actuator health subpaths:** `docs/api-contracts.md` documents `GET /actuator/health/**`, but the FastAPI app only exposes `GET /actuator/health`. Any client probing `/actuator/health/liveness` (or similar) receives 404. Story 1.1 defers extended health documentation and behavior to Story 1.2; resolve when implementing operator-facing health parity.
