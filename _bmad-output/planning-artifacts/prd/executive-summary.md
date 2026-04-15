# Executive Summary

Examinai is a **server-rendered web application** for **internship-style examination programs**: program staff define tasks and assignments; **interns** submit **version-control coordinates** (repository, commit, path scope); **mentors** retrieve **normalized source** from a Git-provider API, maintain **draft reviews**, optionally request **LLM-assisted draft assessments** (Ollama) with **persisted audit** (`model_invocations`, `ai_drafts`), and **publish** structured feedback visible to interns and **coordinators**. The active codebase is a **brownfield migration**: implement parity with the documented **browser HTTP contract** (`docs/api-contracts.md`) and static asset routes while moving the implementation to **Python (FastAPI)** at `src/examai/`, with an optional **Spring Boot** snapshot (`JAVA_APP/`, often gitignored) retained **as reference only** for parity — **not** part of the shipped Python solution.

**Problem:** Assessment workflows scattered across email, ad hoc repo links, and unstructured feedback lose **provenance**, slow **time-to-feedback**, and make **AI assistance** untrustworthy without an audit trail.

**Target outcome (product, not migration-only):** One place where **evidence ties to commits and scope**, mentor judgment has a **draft → publish** lifecycle, and optional AI is **labeled, auditable, and survivable** when Git or the LLM is degraded—so programs can run repeatable reviews without losing artifacts.

**Open product-definition hooks** (to tighten in later PRD sections): **primary success metric** (e.g. time-to-published feedback vs. intern completion vs. coordinator setup time), **explicit v1 non-goals**, and **binding compliance** (e.g. FERPA/COPPA, retention) where interns qualify as students in scope.

## What Makes This Special

- **Git-backed provenance:** Reviews anchor to **repository coordinates and fetch state**, not pasted snapshots alone.
- **Mentor workflow with a clear gate:** **Draft review → publish** separates iteration from intern-visible outcomes; published rows carry **snapshot metadata** aligned with Git fetch versioning.
- **AI with audit, not magic:** Successful inference is **recorded** and linked to draft text; **degraded** LLM behavior is a **first-class UX** concern (mentors can still complete human-only paths).
- **Brownfield with a contract:** **HTTP route parity** is an **engineering constraint**; the **value proposition** is the integrated loop above—not “same URLs” alone.

## Delivery and testing strategy

**Automated tests are explicitly out of scope during initial implementation.** The team will **not** create new test suites or **run** automated tests as a required part of building and landing features in this phase. Validation may rely on **manual checks**, smoke paths, and **health endpoints** where applicable. **Unit, integration, and broader automated tests will be added after** the core implementation reaches agreed milestones—not as a per-story gate while features are first delivered.
