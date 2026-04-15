# Success Criteria

## User Success

- **Interns** can see assigned tasks, submit **valid coordinates** for their work, and open **published feedback** for their submission without admin intervention.
- **Mentors** can drive a submission from **coordinates → successful Git fetch (when configured) → draft review → publish**; with LLM enabled, they can obtain an **AI draft** that is clearly secondary to their judgment; with LLM **disabled or failing**, they can still **publish** a human-only review (degraded path is usable, not blocked).
- **Coordinators** can open **case-level visibility** aligned with product routes (e.g. coordinator case view) for oversight without breaking intern/mentor confidentiality rules implied by roles.
- **Administrators** can manage users/roles as required for the program.

## Business Success

- **Migration:** Replace reliance on the legacy Java app for **pilot/program use** by running the **Python app** against the same PostgreSQL schema contract, with **documented HTTP parity** for browser workflows.
- **Operational:** **Health checks** (`/actuator/health`) support deploy/compose verification; pilot topology (app + Postgres + Ollama per `deployment-guide.md`) remains a credible **smoke path**.
- **Trust:** Stakeholders perceive **auditability** for AI-assisted steps (invocation + draft linkage), not “black box” scoring.

## Technical Success

- **Contract:** Route and method coverage consistent with **`docs/api-contracts.md`** for product flows; static paths **`/css/**`, **`/js/**`, **`/webjars/**`** preserved where required for UI parity.
- **Data:** Application behavior matches **`docs/data-models.md`** and PostgreSQL; optional Liquibase under **`JAVA_APP/`** (if present) is **reference only** for DDL cross-check — no silent drift without migration story.
- **Integrations:** Git provider and Ollama clients live behind **integration** modules with explicit failure behavior (timeouts, errors surfaced in UI/state columns, not silent corruption).
- **Quality (this phase):** Validation through **manual checks**, smoke paths, and health endpoints—not automated test suites. **Automated tests are deferred** per [Delivery and testing strategy](#delivery-and-testing-strategy).

## Measurable Outcomes

- **MVP migration:** Python app runs end-to-end **one full role workflow** per persona (smoke-level), with **health green** in target environments.
- **Mentor loop:** Median **time from submission coordinates present to published review** trackable internally (even if v1 is manual measurement); **publish** always implies a durable row with snapshot fields when Git was used.
- **AI:** **100%** of successful LLM runs that produce user-visible draft text have a corresponding **`model_invocations`** / **`ai_drafts`** linkage (audit completeness for successful path).
- **Degradation:** When Ollama is down, **mentor publish rate** is non-zero (human-only path proven).
