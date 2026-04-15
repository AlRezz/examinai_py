---
stepsCompleted:
  - step-01-init
  - step-02-discovery
  - step-02b-vision
  - step-02c-executive-summary
  - step-03-success
  - step-04-journeys
  - step-05-domain
  - step-06-innovation
  - step-07-project-type
  - step-08-scoping
  - step-09-functional
  - step-10-nonfunctional
  - step-11-polish
  - step-12-complete
classification:
  projectType: web_app
  domain: edtech
  complexity: medium
  projectContext: brownfield
inputDocuments:
  - docs/README.md
  - docs/index.md
  - docs/project-overview.md
  - docs/architecture.md
  - docs/api-contracts.md
  - docs/data-models.md
  - docs/component-inventory.md
  - docs/development-guide.md
  - docs/deployment-guide.md
  - docs/source-tree-analysis.md
  - _bmad-output/project-context.md
workflowType: prd
documentCounts:
  briefCount: 0
  researchCount: 0
  brainstormingCount: 0
  projectDocsCount: 11
---

# Product Requirements Document — examinai_py

**Author:** Alex  
**Date:** 2026-04-15

## Executive Summary

Examinai is a **server-rendered web application** for **internship-style examination programs**: program staff define tasks and assignments; **interns** submit **version-control coordinates** (repository, commit, path scope); **mentors** retrieve **normalized source** from a Git-provider API, maintain **draft reviews**, optionally request **LLM-assisted draft assessments** (Ollama) with **persisted audit** (`model_invocations`, `ai_drafts`), and **publish** structured feedback visible to interns and **coordinators**. The active codebase is a **brownfield migration**: implement parity with the documented **browser HTTP contract** (`docs/api-contracts.md`) and static asset routes while moving the implementation to **Python (FastAPI)** at `src/examai/`, with an optional **Spring Boot** snapshot (`JAVA_APP/`, often gitignored) retained **as reference only** for parity — **not** part of the shipped Python solution.

**Problem:** Assessment workflows scattered across email, ad hoc repo links, and unstructured feedback lose **provenance**, slow **time-to-feedback**, and make **AI assistance** untrustworthy without an audit trail.

**Target outcome (product, not migration-only):** One place where **evidence ties to commits and scope**, mentor judgment has a **draft → publish** lifecycle, and optional AI is **labeled, auditable, and survivable** when Git or the LLM is degraded—so programs can run repeatable reviews without losing artifacts.

**Open product-definition hooks** (to tighten in later PRD sections): **primary success metric** (e.g. time-to-published feedback vs. intern completion vs. coordinator setup time), **explicit v1 non-goals**, and **binding compliance** (e.g. FERPA/COPPA, retention) where interns qualify as students in scope.

### What Makes This Special

- **Git-backed provenance:** Reviews anchor to **repository coordinates and fetch state**, not pasted snapshots alone.
- **Mentor workflow with a clear gate:** **Draft review → publish** separates iteration from intern-visible outcomes; published rows carry **snapshot metadata** aligned with Git fetch versioning.
- **AI with audit, not magic:** Successful inference is **recorded** and linked to draft text; **degraded** LLM behavior is a **first-class UX** concern (mentors can still complete human-only paths).
- **Brownfield with a contract:** **HTTP route parity** is an **engineering constraint**; the **value proposition** is the integrated loop above—not “same URLs” alone.

### Delivery and testing strategy

**Automated tests are explicitly out of scope during initial implementation.** The team will **not** create new test suites or **run** automated tests as a required part of building and landing features in this phase. Validation may rely on **manual checks**, smoke paths, and **health endpoints** where applicable. **Unit, integration, and broader automated tests will be added after** the core implementation reaches agreed milestones—not as a per-story gate while features are first delivered.

## Project Classification

| Dimension | Value |
|-----------|--------|
| **Project type** | Web application (server-rendered HTML; multi-page flows, not a standalone JSON API product) |
| **Domain** | Education / internship assessment (edtech-adjacent; medium domain complexity) |
| **Complexity** | **Medium** — multi-role RBAC, external Git and LLM integrations, audit expectations, operational health |
| **Project context** | **Brownfield** — documented legacy behavior + schema (`Liquibase` reference); active implementation migrates to **FastAPI + Jinja2** while preserving operator-relevant routes (e.g. `/actuator/health`) |

## Success Criteria

### User Success

- **Interns** can see assigned tasks, submit **valid coordinates** for their work, and open **published feedback** for their submission without admin intervention.
- **Mentors** can drive a submission from **coordinates → successful Git fetch (when configured) → draft review → publish**; with LLM enabled, they can obtain an **AI draft** that is clearly secondary to their judgment; with LLM **disabled or failing**, they can still **publish** a human-only review (degraded path is usable, not blocked).
- **Coordinators** can open **case-level visibility** aligned with product routes (e.g. coordinator case view) for oversight without breaking intern/mentor confidentiality rules implied by roles.
- **Administrators** can manage users/roles as required for the program.

### Business Success

- **Migration:** Replace reliance on the legacy Java app for **pilot/program use** by running the **Python app** against the same PostgreSQL schema contract, with **documented HTTP parity** for browser workflows.
- **Operational:** **Health checks** (`/actuator/health`) support deploy/compose verification; pilot topology (app + Postgres + Ollama per `deployment-guide.md`) remains a credible **smoke path**.
- **Trust:** Stakeholders perceive **auditability** for AI-assisted steps (invocation + draft linkage), not “black box” scoring.

### Technical Success

- **Contract:** Route and method coverage consistent with **`docs/api-contracts.md`** for product flows; static paths **`/css/**`, **`/js/**`, **`/webjars/**`** preserved where required for UI parity.
- **Data:** Application behavior matches **`docs/data-models.md`** / Liquibase-backed schema expectations; no silent drift without migration story.
- **Integrations:** Git provider and Ollama clients live behind **integration** modules with explicit failure behavior (timeouts, errors surfaced in UI/state columns, not silent corruption).
- **Quality (this phase):** Validation through **manual checks**, smoke paths, and health endpoints—not automated test suites. **Automated tests are deferred** per [Delivery and testing strategy](#delivery-and-testing-strategy).

### Measurable Outcomes

- **MVP migration:** Python app runs end-to-end **one full role workflow** per persona (smoke-level), with **health green** in target environments.
- **Mentor loop:** Median **time from submission coordinates present to published review** trackable internally (even if v1 is manual measurement); **publish** always implies a durable row with snapshot fields when Git was used.
- **AI:** **100%** of successful LLM runs that produce user-visible draft text have a corresponding **`model_invocations`** / **`ai_drafts`** linkage (audit completeness for successful path).
- **Degradation:** When Ollama is down, **mentor publish rate** is non-zero (human-only path proven).

## Product Scope

### MVP - Minimum Viable Product

- **Parity slice:** Core **intern + mentor** loop for at least one task/submission path: list tasks, submit coordinates, mentor workspace with fetch + draft + publish (AI optional).
- **Auth & roles:** Role-gated URLs consistent with **`docs/api-contracts.md`** and **`project-context.md`** (session strategy TBD but behavior matches).
- **Ops:** Health endpoint; documented run via **`README-Python.md`**; DB connectivity.
- **Schema:** Read/write against existing tables without undefined migration authority (Liquibase remains reference until Alembic owns revisions explicitly).
- **Testing:** No requirement to **create or run** automated tests during MVP build; aligns with [Delivery and testing strategy](#delivery-and-testing-strategy).

### Growth Features (Post-MVP)

- **Full route parity** across admin, coordinator, review queue, and edge cases in **`api-contracts.md`**.
- **Alembic** as sole migration authority with a clean cutover plan from Liquibase reference.
- **Hardening:** Rate limiting, observability, richer degraded-mode semantics per integration (Git/Ollama).
- **UX:** Template parity then **targeted UX improvements** (not 1:1 legacy friction).
- **Automated tests:** Introduced **after** core implementation milestones, covering critical paths, auth/role gates, and integrations.

### Vision (Future)

- **Analytics** for programs (time-to-feedback, cohort comparisons) where data policy allows.
- **Deeper compliance packaging** (FERPA/COPPA, retention, export/delete) once personas and jurisdictions are fixed.
- **Optional** richer AI (multiple models, policy per program) still under **audit** and **human publish** gate.

## User Journeys

### Intern Maya — happy path

**Opening:** Maya is assigned a coding task for the internship program. She keeps work in a private repo and needs official credit without emailing ZIP files.

**Rising action:** She logs in, opens **Intern → tasks**, reads the task, and submits **repository, commit SHA, and path scope** on the task detail page. She fixes validation issues until the submission is accepted.

**Climax:** After the mentor **publishes** a review, she opens **feedback** for her submission and sees structured scores and narrative tied to the work she submitted.

**Resolution:** She has a single durable record of feedback aligned to her coordinates—not a lost thread in chat.

**Failure / recovery:** If she mistypes a ref, she updates coordinates and resubmits; status makes clear what is wrong.

### Mentor Diego — degraded AI, human publish

**Opening:** Diego reviews several interns. Ollama is down or timing out (Compose restart, model missing).

**Rising action:** He opens the **mentor submission workspace**, sees a **degraded inference** signal, and skips AI draft. He still runs **Git fetch** when the provider is up, fills the **draft review** from normalized source, and **publishes**.

**Climax:** Interns receive published feedback without waiting for the LLM; audit shows no successful model invocation for that attempt—consistent with policy.

**Resolution:** The program keeps moving; AI is optional, not a blocker.

**Requirements surfaced:** Degraded banners, human-only publish path, clear intern-visible distinction when AI was not used.

### Coordinator Priya — oversight without taking the pen

**Opening:** Priya needs to confirm a case is moving and spot stuck submissions.

**Rising action:** She uses **Coordinator** routes to open a **case record** for a submission and sees status relevant to coordination (assignments, submission state, published vs. draft as policy allows).

**Climax:** She identifies a stuck flow and nudges the mentor or intern out of band—without needing admin keys for day-to-day triage.

**Resolution:** Visibility matches role; she does not need mentor-intern DMs to guess state.

### Administrator Sam — users and access

**Opening:** A new cohort joins; accounts and roles must exist before interns can log in.

**Rising action:** Sam uses **Admin → users** to create or edit users and assign **intern / mentor / coordinator / administrator** roles as defined by the program.

**Climax:** The next login routes each user to the right home surface per role.

**Resolution:** RBAC and URL gates match **documented route rules** in `docs/api-contracts.md`.

### Operator — deploy and smoke

**Opening:** A release is deployed to the pilot stack (app + Postgres + Ollama).

**Rising action:** They rely on **`/actuator/health`**, Compose logs, and a short **manual** happy-path smoke (login optional, health required).

**Climax:** Green health and one manual path confirm the build is alive; no automated suite is required in this phase.

**Resolution:** Operations match **Delivery and testing strategy**.

### Journey Requirements Summary

| Area | Capabilities implied |
|------|----------------------|
| Intern | Task list/detail, submission coordinates, feedback view |
| Mentor | Submission workspace, Git fetch, draft review, optional AI draft, publish, degraded LLM UX |
| Coordinator | Case/submission visibility within role |
| Administrator | User CRUD, role assignment |
| Ops | Health endpoint, manual/smoke validation (no automated test gate in this phase) |
| Cross-cutting | Sessions, CSRF on POSTs, role-based routing, audit fields for successful AI |

## Domain-Specific Requirements

### Compliance & regulatory

- **Privacy (US education context):** If users are **students** in an institution covered by **FERPA**, or **children under 13** interact with the product, define data categories, **school vs. operator** roles, and any **parental consent** path. Until jurisdictions and age range are fixed, treat **minimum necessary** collection, **no gratuitous PII in LLM prompts** (align with `project-context`: prompts use task text + truncated normalized source only), and **subprocessor transparency** for Ollama/Git cloud endpoints if used.
- **Accessibility:** Browser-based, server-rendered UI should progress toward **WCAG-aligned** patterns for core flows (login, tasks, submission, feedback); exact tier can be set when procurement requires it.
- **Assessment integrity:** Git-backed coordinates support **reproducibility**; published reviews should remain attributable to **human judgment** with AI clearly **draft** unless product policy states otherwise.

### Technical constraints

- **Data minimization:** Store and display only what roles require (intern vs. mentor vs. coordinator vs. admin); enforce via **RBAC** and row-level expectations consistent with `docs/data-models.md`.
- **Audit:** AI-related rows (`model_invocations`, `ai_drafts`) support defensibility and internal review; retention/export/deletion policies are **TBD** until compliance scope is chosen.
- **Third parties:** Git provider and Ollama endpoints process **metadata and code content**; contracts and DPA posture are **program-specific**—document who operates each integration in deployment.

### Integration requirements

- **Git provider:** GitHub-compatible REST; tokens via environment; no token logging; rate-limit and failure behavior visible in product state.
- **Ollama:** Configurable base URL and model; degraded behavior when unavailable; optional health probe per ops docs.

### Risk mitigations

| Risk | Mitigation |
|------|------------|
| COPPA/FERPA ambiguity | Lock **personas + age band** in a later PRD/legal pass; default to conservative collection and prompt hygiene |
| AI over-reliance | Human **publish** gate; audit linkage; degraded UX when LLM fails |
| Cross-tenant visibility | Role URLs and coordinator visibility rules; no cross-intern leakage in requirements |

## Innovation & Novel Patterns

### Detected innovation areas

- **Integrated assessment pipeline:** Combines **version-control coordinates**, **normalized source retrieval**, **mentor draft → publish**, and **optional LLM assistance** with **persisted inference audit**—so programs get reproducibility and human judgment without treating AI as authoritative.
- **Degraded-first product design:** Treats **LLM and Git outages** as expected states with **usable human paths**, not hard failures—reduces operational fragility versus “AI-first” grading tools.
- **Migration as contract:** Shipping **HTTP parity** to a documented surface (`docs/api-contracts.md`) while swapping the stack is a disciplined form of **risk-managed modernization** (innovation in delivery, not only features).

### Market context & competitive landscape

- **LMS / generic code review tools** often lack **program-specific** draft→publish review semantics and **audit-linked** AI drafts in one intern–mentor loop.
- **Standalone AI coding assistants** lack **role-governed** workflows and **published feedback** artifacts tied to institutional tasks.
- Exact competitive set is **program-dependent**; positioning should stress **provenance + audit + role boundaries**, not “more AI.”

### Validation approach

- **Pilot cohort** with manual smoke and health checks (per **Delivery and testing strategy**); measure **time-to-published feedback** and **human-only path** usage when LLM is off.
- **Audit sampling:** Spot-check that successful AI-visible drafts have **`model_invocations` / `ai_drafts`** linkage.
- **Automated test suite** validation comes **after** implementation milestones—not a gate in this phase.

### Risk mitigation

| Risk | Mitigation |
|------|------------|
| “Parity” displaces user value | Keep **outcomes** (published feedback, provenance) primary; URLs are **constraints** |
| AI trust or liability | **Publish** remains human; drafts labeled; audit trail |
| Integration brittleness | Explicit failure surfaces, degraded UX, ops runbooks (`deployment-guide.md`) |

## Web Application Specific Requirements

### Project-type overview

Examinai is a **multi-page, server-rendered web application** (FastAPI + Jinja2 target): authenticated users move between pages via **GET** and **POST** forms with **CSRF** on mutating requests, aligned with `docs/api-contracts.md`. The product is **not** a public marketing site or a JSON-first SPA; the browser is the client for role-specific workflows.

### Technical architecture considerations

- **MPA vs SPA:** **MPA** (full page loads / redirects, form posts). No requirement for client-side routing or a separate frontend repo in MVP.
- **Sessions & security:** Form login, session cookie, role-based URL authorization; static assets under `/css/**`, `/js/**`, `/webjars/**` as documented.

### Browser matrix

| Tier | Browsers | Notes |
|------|----------|--------|
| **Primary** | Latest **Chrome**, **Firefox**, **Safari**, **Edge** (current −1) | Pilot and local dev |
| **Baseline** | Exact “must support” list may be tightened by program IT | Document when procurement requires |

### Responsive design

- Layouts should be **usable on common laptop widths** first; **tablet/mobile** readability is desirable for coordinator/intern quick checks but **not** a native-app replacement. Bootstrap-aligned patterns per `docs/component-inventory.md` and Jinja parity.

### Performance targets

- **Page-level:** Interactive tasks (list → detail → submit) should avoid unnecessary round-trips; Git fetch and LLM calls are **explicit actions** with user-visible progress or failure (no silent long hangs without feedback).
- **Integrations:** Timeouts and retries for **Git** and **Ollama** owned by integration modules; degrade gracefully per mentor journey.

### SEO strategy

- **Minimal:** Most value is **behind login**. No reliance on public indexing for core workflows. Public/static pages (e.g. landing) may exist but are not the MVP differentiator.

### Accessibility level

- **Target:** Progress toward **WCAG 2.x** alignment on core flows (login, tasks, submission, feedback), consistent with [Domain-Specific Requirements](#domain-specific-requirements). Formal audit tier **TBD** by procurement.

### Implementation considerations

- **Templates & static files:** Mirror template names and URL structure from product docs where “same UI” is required; mount static files for CSS/JS/WebJars paths.
- **Health:** `GET /actuator/health` for operators (JSON shape agreed with ops).
- **Testing:** Per [Delivery and testing strategy](#delivery-and-testing-strategy)—**no automated browser suite** required during initial implementation; manual passes for primary browsers; automated tests in a later phase per PRD.

## Project Scoping & Phased Development

Feature boundaries for **MVP / Growth / Vision** are stated under [Product Scope](#product-scope). This section adds **delivery emphasis**, **phasing**, and **risk**—not a second scope definition.

### MVP strategy & philosophy

**MVP approach:** **Problem-solving + migration MVP** — prove the **intern → mentor loop** on the new stack with **documented route parity** (`docs/api-contracts.md`), **manual/smoke** validation, and **no automated test gate** during initial delivery (per **Delivery and testing strategy**).

**Resource requirements:** Team comfortable with server-rendered web delivery, relational persistence, and external integrations (Git host, LLM host); ops follow **`docs/development-guide.md`**.

### MVP feature set (Phase 1)

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

### Post-MVP features

**Phase 2 (growth)**

- **Full route parity** across roles in `api-contracts.md`.
- **Owned database migrations** with a clear handoff from reference DDL.
- **Automated tests** for critical paths and integrations.
- Hardening: rate limits, observability, richer degraded semantics.

**Phase 3 (expansion)**

- Analytics and reporting where policy allows.
- Deeper compliance packaging (retention, export, jurisdictional rules).
- Optional multi-model / program-level AI policy (still **human publish** gate).

### Risk mitigation strategy

| Category | Mitigation |
|----------|------------|
| **Technical** | Thin vertical slices; integration timeouts and visible errors; schema aligned with `data-models.md` |
| **Market / user** | Pilot cohort; measure time-to-published feedback manually first |
| **Resource** | Smallest shippable slice per milestone; defer full parity and test automation per phased plan |

## Functional Requirements

### Authentication & session

- **FR1:** A user can sign in with credentials and establish an authenticated session.
- **FR2:** An authenticated user can sign out.
- **FR3:** An unauthenticated user cannot access role-protected workflows except where explicitly public (e.g. login, static assets, health).

### Role-based access

- **FR4:** The system enforces role-appropriate access to URL spaces (intern, mentor, coordinator, administrator) per the product’s route rules.
- **FR5:** After authentication, a user is directed to an experience appropriate to their role.

### Tasks & program work

- **FR6:** A mentor or administrator can create, view, edit, and list program tasks.
- **FR7:** A mentor or administrator can assign interns to tasks.
- **FR8:** An intern can view tasks assigned to them and open task details.

### Submissions & source evidence

- **FR9:** An intern can submit or update version-control coordinates (repository, commit, path scope) for an assigned task.
- **FR10:** The system stores submission state relevant to retrieval and review (including error state when retrieval fails).
- **FR11:** A mentor can trigger retrieval of normalized source from the configured Git provider for a submission, when integrated.
- **FR12:** A mentor can see whether retrieval succeeded, failed, or is in progress, without silent failure.

### Mentor review (draft and publish)

- **FR13:** A mentor can maintain a draft review (scores and narrative) for a submission.
- **FR14:** A mentor can publish a review so it becomes the official outcome for that submission.
- **FR15:** A mentor can publish a human-only review when AI assistance is unavailable or unused.
- **FR16:** Published feedback includes snapshot metadata tying the outcome to the evidence at publish time (e.g. commit, fetch version, path scope) as defined by the data model.

### AI-assisted draft assessment

- **FR17:** A mentor can request an AI-generated draft assessment for a submission when the LLM integration is enabled.
- **FR18:** The system persists an audit record for each successful AI inference used for draft assessment (model identity, timing, linkage to draft content).
- **FR19:** The system surfaces degraded or unavailable LLM state to mentors in the review workflow.
- **FR20:** Intern-facing outcomes distinguish human-published feedback from optional AI draft content as required by product policy.

### Intern feedback consumption

- **FR21:** An intern can view published feedback for their submission.

### Coordinator oversight

- **FR22:** A coordinator can access coordinator-scoped views (e.g. case/submission visibility) per role rules.

### User administration

- **FR23:** An administrator can list, create, and edit user accounts.
- **FR24:** An administrator can assign roles to users (intern, mentor, coordinator, administrator).

### Review queue & workload (full product)

- **FR25:** A mentor can access a review queue view for outstanding work, when that route is in scope for the release.

### Operations

- **FR26:** An operator can verify application liveness via a documented health endpoint.

### Compliance & data handling (domain)

- **FR27:** The system limits use of personal/sensitive data in AI prompts to what the program requires (task context and retrieved source per policy).
- **FR28:** Role boundaries prevent users from accessing other users’ prohibited data per the access model.

### Integrations (behavioral)

- **FR29:** The system applies configurable behavior for Git provider failures (timeouts, errors, user-visible state).
- **FR30:** The system applies configurable behavior for LLM failures (timeouts, errors, degraded messaging).

## Non-Functional Requirements

### Performance

- **NFR-P1:** Interactive page transitions for core flows (task list → detail → submit; mentor workspace) complete without indefinite blocking; long-running operations (Git fetch, LLM request) show explicit in-progress or terminal state to the user.
- **NFR-P2:** Git provider and LLM calls use bounded timeouts and retries configurable per environment so workers do not hang unbounded.

### Security

- **NFR-S1:** Passwords are stored using a strong one-way hash; credentials are never logged or returned in API responses.
- **NFR-S2:** Session and CSRF protections apply to mutating requests per the product’s security model.
- **NFR-S3:** Secrets (database, Git token, LLM endpoints) are supplied via environment or secure configuration—not committed to source control.
- **NFR-S4:** Git and LLM credentials are not embedded in prompts, logs, or intern-visible pages.

### Scalability

- **NFR-SC1:** The pilot deployment supports concurrent mentors and interns typical of a single program cohort without requiring horizontal scaling as a prerequisite for MVP (vertical scaling acceptable initially).

### Accessibility

- **NFR-A1:** Core flows (login, task view, submission, published feedback) are implementable to progress toward **WCAG 2.x** conformance; exact level is confirmed when procurement or policy requires it.

### Integration

- **NFR-I1:** Git provider integration tolerates rate limits and transient failures with user-visible state and without corrupting stored submission evidence.
- **NFR-I2:** LLM integration tolerates model unavailability with mentor-visible degraded behavior and without blocking human-only publish.

### Reliability & operability

- **NFR-R1:** A health endpoint returns a consistent success/failure signal suitable for load balancers and scripted smoke checks.
- **NFR-R2:** Database schema changes are tracked through an agreed migration process so environments stay aligned with the data model.
