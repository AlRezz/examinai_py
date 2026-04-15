# Story 1.2: Operator health check

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an **operator**,  
I want **`GET /actuator/health` to return contract-shaped JSON**,  
so that **deployments and smoke scripts can verify liveness**.

## Acceptance Criteria

1. **Contract JSON (root)**  
   **Given** the app is running  
   **When** I `GET /actuator/health`  
   **Then** the response is **200** with **`Content-Type` JSON** and body **`{"status":"UP"}`** per **[docs/deployment-guide.md](../../docs/deployment-guide.md)** and **[docs/api-contracts.md](../../docs/api-contracts.md)**.

2. **Health subpaths (contract)**  
   **Given** the app is running  
   **When** I request **`GET /actuator/health/**`** (e.g. liveness-style subpaths under that prefix)  
   **Then** responses return the **same contract shape** **`{"status":"UP"}`** with **200** (parity with **[docs/api-contracts.md](../../docs/api-contracts.md)** public table).

3. **Unauthenticated (FR6 / FR4)**  
   **Given** no session or credentials  
   **When** I call the health endpoints above  
   **Then** access succeeds without authentication.

## Tasks / Subtasks

- [x] **Health routes** (AC: 1, 2)  
  - [x] Keep **`GET /actuator/health`** returning **`{"status":"UP"}`**.  
  - [x] Register **`GET /actuator/health/{path:path}`** (or equivalent) so subpaths under **`/actuator/health/`** return the **same** JSON shape for operator/Spring-style probes.

- [x] **Tests** (AC: 1–3)  
  - [x] Extend **[`tests/test_health.py`](../../tests/test_health.py)** (or add focused tests): root health JSON; at least one **subpath**; assert **no** auth headers/cookies required (default `TestClient`).

- [x] **Docs alignment** (AC: 1)  
  - [x] Confirm **[docs/deployment-guide.md](../../docs/deployment-guide.md)** `curl` example remains accurate; adjust only if behavior changes.

## Dev Notes

### Scope boundaries

| In scope | Out of scope |
|----------|----------------|
| Liveness JSON contract, **`/actuator/health`**, **`/actuator/health/**`** | DB/LLM **component** health aggregation (future if needed) |
| Public (no auth) health | **`POST /login`**, sessions (**Story 1.3**) |

### Architecture and patterns

- **Single app factory:** [`src/examai/main.py`](../../src/examai/main.py) — `create_app()`; avoid coupling health to future security middleware (health must stay public).  
- **Contract:** [docs/api-contracts.md](../../docs/api-contracts.md), [docs/deployment-guide.md](../../docs/deployment-guide.md).

### References

- [docs/deployment-guide.md](../../docs/deployment-guide.md)  
- [docs/api-contracts.md](../../docs/api-contracts.md)  
- [_bmad-output/planning-artifacts/epics.md](../../_bmad-output/planning-artifacts/epics.md) — Epic 1, Story 1.2  

### Previous story intelligence

- **Story 1.1** implemented the public shell; health root already returned **`{"status":"UP"}`**; **subpaths returned 404** — **Story 1.2** adds **`/actuator/health/**`** per contract.

## Dev Agent Record

### Agent Model Used

Composer (Cursor agent)

### Debug Log References

— 

### Completion Notes List

- Added **`GET /actuator/health/{subpath:path}`** so **`/actuator/health/**`** probes return the same **`{"status":"UP"}`** JSON as root, matching **[docs/api-contracts.md](../../docs/api-contracts.md)**.
- Documented public (no-auth) intent on the root health handler; tests assert JSON **`Content-Type`**, subpaths **`liveness`** / **`readiness`**, and unauthenticated **`GET`**.
- **[docs/deployment-guide.md](../../docs/deployment-guide.md)** `curl` example unchanged and still valid.

### File List

- `src/examai/main.py`
- `tests/test_health.py`
- `_bmad-output/implementation-artifacts/1-2-operator-health-check.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log

- 2026-04-15: Story 1.2 — actuator health root + subpaths, extended tests, sprint status.

## Review Findings

- [x] [Review][Patch] Strengthen health tests for AC2–AC3 — assert `Content-Type` is JSON on subpath responses (parity with root test) and call at least one subpath in the unauthenticated test so AC3 explicitly covers `/actuator/health/**`, not only the root. [`tests/test_health.py`] — fixed 2026-04-15

---

**Story completion status:** Done (code review complete).
