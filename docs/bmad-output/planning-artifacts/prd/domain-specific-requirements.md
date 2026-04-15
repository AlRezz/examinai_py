# Domain-Specific Requirements

## Compliance & regulatory

- **Privacy (US education context):** If users are **students** in an institution covered by **FERPA**, or **children under 13** interact with the product, define data categories, **school vs. operator** roles, and any **parental consent** path. Until jurisdictions and age range are fixed, treat **minimum necessary** collection, **no gratuitous PII in LLM prompts** (align with `project-context`: prompts use task text + truncated normalized source only), and **subprocessor transparency** for Ollama/Git cloud endpoints if used.
- **Accessibility:** Browser-based, server-rendered UI should progress toward **WCAG-aligned** patterns for core flows (login, tasks, submission, feedback); exact tier can be set when procurement requires it.
- **Assessment integrity:** Git-backed coordinates support **reproducibility**; published reviews should remain attributable to **human judgment** with AI clearly **draft** unless product policy states otherwise.

## Technical constraints

- **Data minimization:** Store and display only what roles require (intern vs. mentor vs. coordinator vs. admin); enforce via **RBAC** and row-level expectations consistent with `docs/data-models.md`.
- **Audit:** AI-related rows (`model_invocations`, `ai_drafts`) support defensibility and internal review; retention/export/deletion policies are **TBD** until compliance scope is chosen.
- **Third parties:** Git provider and Ollama endpoints process **metadata and code content**; contracts and DPA posture are **program-specific**—document who operates each integration in deployment.

## Integration requirements

- **Git provider:** GitHub-compatible REST; tokens via environment; no token logging; rate-limit and failure behavior visible in product state.
- **Ollama:** Configurable base URL and model; degraded behavior when unavailable; optional health probe per ops docs.

## Risk mitigations

| Risk | Mitigation |
|------|------------|
| COPPA/FERPA ambiguity | Lock **personas + age band** in a later PRD/legal pass; default to conservative collection and prompt hygiene |
| AI over-reliance | Human **publish** gate; audit linkage; degraded UX when LLM fails |
| Cross-tenant visibility | Role URLs and coordinator visibility rules; no cross-intern leakage in requirements |
