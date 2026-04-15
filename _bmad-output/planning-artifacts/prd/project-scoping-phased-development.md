# Project Scoping & Phased Development

Feature boundaries for **MVP / Growth / Vision** are stated under [Product Scope](#product-scope). This section adds **delivery emphasis**, **phasing**, and **risk**—not a second scope definition.

## MVP strategy & philosophy

**MVP approach:** **Problem-solving + migration MVP** — prove the **intern → mentor loop** on the new stack with **documented route parity** (`docs/api-contracts.md`), **manual/smoke** validation, and **no automated test gate** during initial delivery (per **Delivery and testing strategy**).

**Resource requirements:** Team comfortable with server-rendered web delivery, relational persistence, and external integrations (Git host, LLM host); ops follow **`docs/development-guide.md`**.

## MVP feature set (Phase 1)

**Core user journeys supported**

- **Intern:** Tasks → submit coordinates → view published feedback (happy path).
- **Mentor:** Submission workspace → Git fetch (when configured) → draft review → optional AI draft → **publish**; **human-only path** when LLM unavailable.
- **Smoke:** **Health** endpoint; DB connectivity; role routing as implemented.

**Must-have capabilities**

- **HTTP contract** for the chosen MVP slice (subset of `api-contracts.md` agreed per sprint).
- **Sessions + CSRF** on POSTs; **role-gated** URLs per product rules.
- **Integration behavior** for Git and LLM providers with **degraded** UX when services fail.
- **Audit** linkage for successful AI drafts when AI is in scope for MVP.

**Explicit MVP boundaries**

- **Automated tests** not required to ship MVP stories (added post-milestone).
- **Full** admin/coordinator/review-queue parity **optional** until Phase 2 unless pulled forward by program need.

## Post-MVP features

**Phase 2 (growth)**

- **Full route parity** across roles in `api-contracts.md`.
- **Owned database migrations** with a clear handoff from reference DDL.
- **Automated tests** for critical paths and integrations.
- Hardening: rate limits, observability, richer degraded semantics.

**Phase 3 (expansion)**

- Analytics and reporting where policy allows.
- Deeper compliance packaging (retention, export, jurisdictional rules).
- Optional multi-model / program-level AI policy (still **human publish** gate).

## Risk mitigation strategy

| Category | Mitigation |
|----------|------------|
| **Technical** | Thin vertical slices; integration timeouts and visible errors; schema aligned with `data-models.md` |
| **Market / user** | Pilot cohort; measure time-to-published feedback manually first |
| **Resource** | Smallest shippable slice per milestone; defer full parity and test automation per phased plan |
