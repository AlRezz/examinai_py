# Innovation & Novel Patterns

## Detected innovation areas

- **Integrated assessment pipeline:** Combines **version-control coordinates**, **normalized source retrieval**, **mentor draft → publish**, and **optional LLM assistance** with **persisted inference audit**—so programs get reproducibility and human judgment without treating AI as authoritative.
- **Degraded-first product design:** Treats **LLM and Git outages** as expected states with **usable human paths**, not hard failures—reduces operational fragility versus “AI-first” grading tools.
- **Migration as contract:** Shipping **HTTP parity** to a documented surface (`docs/api-contracts.md`) while swapping the stack is a disciplined form of **risk-managed modernization** (innovation in delivery, not only features).

## Market context & competitive landscape

- **LMS / generic code review tools** often lack **program-specific** draft→publish review semantics and **audit-linked** AI drafts in one intern–mentor loop.
- **Standalone AI coding assistants** lack **role-governed** workflows and **published feedback** artifacts tied to institutional tasks.
- Exact competitive set is **program-dependent**; positioning should stress **provenance + audit + role boundaries**, not “more AI.”

## Validation approach

- **Pilot cohort** with manual smoke and health checks (per **Delivery and testing strategy**); measure **time-to-published feedback** and **human-only path** usage when LLM is off.
- **Audit sampling:** Spot-check that successful AI-visible drafts have **`model_invocations` / `ai_drafts`** linkage.
- **Automated test suite** validation comes **after** implementation milestones—not a gate in this phase.

## Risk mitigation

| Risk | Mitigation |
|------|------------|
| “Parity” displaces user value | Keep **outcomes** (published feedback, provenance) primary; URLs are **constraints** |
| AI trust or liability | **Publish** remains human; drafts labeled; audit trail |
| Integration brittleness | Explicit failure surfaces, degraded UX, ops runbooks (`deployment-guide.md`) |
