# Story 8.7: README-Python — user flows for all user types

Status: backlog

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **new contributor or operator**,  
I want **`README-Python.md` to summarize user flows by role**,  
so that **I can sanity-check intern, mentor, coordinator, and administrator journeys after bringing the stack up**.

## Acceptance Criteria

1. **Coverage**  
   **Given** roles in **[docs/api-contracts.md](../../docs/api-contracts.md)** and **FR4–FR5**, **FR7–FR27**  
   **When** I read **`README-Python.md`**  
   **Then** there is a **User flows** (or **Smoke paths by role**) section covering: **intern**, **mentor** (and note **administrator** can use mentor routes where applicable), **coordinator**, **administrator** (admin-only **`/admin/**`**).

2. **Representative URLs**  
   **Then** each role lists **entry URLs** (e.g. login → home → role-specific hub) consistent with the contract — **no invented paths**.

3. **Auth reminder**  
   **Then** the doc states that **unauthenticated** users only reach public routes (**FR4**) and points to contract for the full matrix.

4. **Freshness**  
   **Then** routes match **current** **[docs/api-contracts.md](../../docs/api-contracts.md)**; if contract changes, update this section in the same PR.

5. **Length**  
   **Then** section stays **concise** (table or bullet journey per role), not a second PRD.

## Tasks / Subtasks

- [ ] Add **User flows by role** to **[README-Python.md](../../README-Python.md)**.
- [ ] Derive paths from **[docs/api-contracts.md](../../docs/api-contracts.md)** and **[docs/index.md](../../docs/index.md)** entry points.
- [ ] Optional: add **“smoke checklist”** table (role → URL → expected outcome).

## Dev Notes

### Guardrails

- **Single source of truth** for routes is **`docs/api-contracts.md`** — README is a **summary**.
- **RBAC:** **[project-context](../project-context.md)** — `INTERN` → `/intern/**`, `COORDINATOR` → `/coordinator/**`, `MENTOR` + admin → `/tasks/**`, `/review/**`, `ADMINISTRATOR` → `/admin/**`.

### Dependencies

- **Depends on:** Stable route list — implement **after** **8.4–8.6** or in same pass as final README polish.

### References

- [docs/api-contracts.md](../../docs/api-contracts.md)  
- [_bmad-output/planning-artifacts/epics.md](../planning-artifacts/epics.md) — role epics  
- [README-Python.md](../../README-Python.md)

### Previous story intelligence

- **8.4–8.6** added Docker operations; **8.7** is the **capstone** README section for human verification of the running system.

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

---

**Context engine notes:** Ultimate story context created for Epic 8.7.
