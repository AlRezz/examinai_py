---
stepsCompleted:
  - step-01-fr-and-tasks
  - step-01-ux-design-requirements
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
workflowStatus: complete
workflowCompletedAt: '2026-04-15'
inputDocuments:
  - docs/README.md
  - docs/index.md
  - docs/project-overview.md
  - docs/architecture.md
  - docs/api-contracts.md
  - docs/data-models.md
  - docs/component-inventory.md
  - docs/deployment-guide.md
  - docs/development-guide.md
  - docs/source-tree-analysis.md
  - _bmad-output/planning-artifacts/architecture.md
scope_note: >-
  Functional requirements, UX design requirements, implementation tasks, epic list,
  coverage maps, and user stories. NFR inventory omitted unless added later.
  Epic 8 (Docker, DB seed, Liquibase, README-Python) added 2026-04-15 as a supplement.
---

# examinai_py — Functional Requirements, UX Design Requirements, and Tasks

## Overview

**examinai_py** is a server-rendered internship examination product (**FastAPI**, **Jinja2**, **PostgreSQL**). This document inventories **functional requirements**, **UX design requirements**, **implementation tasks**, **epics**, and **user stories**. References: **`docs/*.md`**, **`_bmad-output/planning-artifacts/architecture.md`**. Canonical HTTP surface: **[docs/api-contracts.md](../../docs/api-contracts.md)**; schema: **[docs/data-models.md](../../docs/data-models.md)**. UX-DRs follow **[docs/component-inventory.md](../../docs/component-inventory.md)** and architecture form/degraded patterns.

## Functional Requirements

Requirements are numbered for traceability. Paths and methods follow `api-contracts.md` unless noted.

### Authentication, session, and access

- **FR1:** A user can open a **login** page (`GET /login`) and submit credentials to establish a **session** (form login per contract).
- **FR2:** An authenticated user can reach **post-login home** (`GET /home`) and the **secure smoke** page (`GET /app/secure`).
- **FR3:** An authenticated user can **sign out** via `POST /logout`.
- **FR4:** **Unauthenticated** users can access **public** routes only: `GET /`, `GET /login`, `GET /error`, static `GET /webjars/**`, `GET /css/**`, `GET /js/**`, and `GET /actuator/health` (and `/actuator/health/**` as documented).
- **FR5:** **Role-gated** URL spaces are enforced: **intern** (`/intern/**`), **coordinator** (`/coordinator/**`), **mentor or administrator** (`/tasks/**`, `/review/**`), **administrator** (`/admin/**`), per contract and architecture RBAC mapping.

### Operations

- **FR6:** An operator (or script) can verify **liveness** via `GET /actuator/health` (and `GET /actuator/health/**`) with a **contract-documented** JSON response shape (e.g. `{"status":"UP"}` per `deployment-guide.md` / contract).

### Intern — tasks and submissions

- **FR7:** An intern can list **assigned tasks** (`GET /intern/tasks`).
- **FR8:** An intern can open **task detail** (`GET /intern/tasks/{taskId}`).
- **FR9:** An intern can **submit or update** version-control coordinates for a task (`POST /intern/tasks/{taskId}/submission`).
- **FR10:** An intern can view **published feedback** for a submission (`GET /intern/submissions/{submissionId}/feedback`).

### Coordinator

- **FR11:** A coordinator can open the **coordinator index** (`GET /coordinator`).
- **FR12:** A coordinator can open a **case record** for a submission (`GET /coordinator/cases/{submissionId}`).

### Mentor or administrator — tasks and assignments

- **FR13:** A mentor or administrator can **list tasks** (`GET /tasks`).
- **FR14:** A mentor or administrator can **create** a task via form (`GET`/`POST /tasks/new`).
- **FR15:** A mentor or administrator can **edit** a task (`GET`/`POST /tasks/{id}/edit`).
- **FR16:** A mentor or administrator can **view and save intern assignments** for a task (`GET`/`POST /tasks/{id}/assignments`).
- **FR17:** A mentor or administrator can **list submissions** for a task (`GET /tasks/{taskId}/submissions`).
- **FR18:** A mentor or administrator can open the **mentor submission workspace** for an intern (`GET /tasks/{taskId}/submissions/{internId}`).

### Mentor or administrator — submission workspace actions

- **FR19:** A mentor or administrator can **update repository coordinates** for a submission (`POST /tasks/{taskId}/submissions/{internId}/coordinates`).
- **FR20:** A mentor or administrator can **trigger Git-backed source retrieval** (`POST /tasks/{taskId}/submissions/{internId}/fetch`).
- **FR21:** A mentor or administrator can **request an AI draft assessment** (`POST /tasks/{taskId}/submissions/{internId}/ai-draft-assessment`) when Ollama integration is configured.
- **FR22:** A mentor or administrator can **save a mentor draft review** (`POST /tasks/{taskId}/submissions/{internId}/review-draft`).
- **FR23:** A mentor or administrator can **publish a review** (`POST /tasks/{taskId}/submissions/{internId}/publish-review`).

### Mentor — review queue

- **FR24:** A mentor can open the **review queue** (`GET /review/queue`) when implemented for the release.

### Administrator — users

- **FR25:** An administrator can **list users** (`GET /admin/users`).
- **FR26:** An administrator can **create** a user (`GET`/`POST /admin/users/new`).
- **FR27:** An administrator can **edit** a user (`GET`/`POST /admin/users/{id}/edit`).

### Domain persistence and evidence (aligned with data-models.md)

- **FR28:** The application **persists and reads** user identity, roles, tasks, assignments, submissions, mentor drafts, published reviews, and (when AI is used) **audit rows** (`model_invocations`, `ai_drafts`) consistent with **[docs/data-models.md](../../docs/data-models.md)** table and column semantics.
- **FR29:** **Submissions** store coordinates and **Git retrieval state** (e.g. `git_retrieval_state`, retrieved text, fetch version, error codes) so mentors and workflows can reflect **success, failure, or in-progress** retrieval without silent corruption.
- **FR30:** **Published reviews** store **snapshot metadata** (`snapshot_commit_sha`, `snapshot_git_fetch_version`, `snapshot_path_scope`) tying the published outcome to evidence at publish time.

### External integration behavior (product-facing)

- **FR31:** **Git provider** retrieval is invoked via a **dedicated integration layer** (not embedded ad hoc in route handlers); outcomes are reflected in submission/workspace **state** visible in the mentor flow.
- **FR32:** **Ollama** draft generation is invoked via a **dedicated integration layer**; successful runs that produce draft content are **auditable** via `model_invocations` / `ai_drafts` per data model; **degraded or unavailable** LLM behavior is **surfaced** in the mentor workspace (per architecture and component-inventory partials such as degraded-inference UI when implemented).

### UI delivery (server-rendered)

- **FR33:** Product pages are delivered as **server-rendered HTML** (Jinja2 target) with **CSRF on POST** actions per contract; **static assets** are served at `/css/**`, `/js/**`, `/webjars/**` for parity with **[docs/component-inventory.md](../../docs/component-inventory.md)** and the contract.

---

## UX design requirements

Each item is numbered for traceability (`UX-DR*`). Scope is **implementation-ready** (templates, assets, patterns)—not generic “good UX.” Sources: **[docs/component-inventory.md](../../docs/component-inventory.md)**, **`_bmad-output/planning-artifacts/architecture.md`** (forms, loading/degraded behavior).

### Templates and information architecture

- **UX-DR1:** **Jinja2** templates follow **reference file paths and names** from the component inventory for each product area: core (`index.html`, `home.html`, `login.html`), `app/secure.html`, admin (`admin/users/list.html`, `admin/user-form.html`), coordinator (`coordinator/index.html`, `coordinator/case-record.html`), intern (`intern/tasks/list.html`, `intern/tasks/detail.html`, `intern/submissions/feedback.html`), mentor/tasks (`tasks/list.html`, `tasks/form.html`, `tasks/assign.html`, `tasks/submissions.html`, `tasks/submission-detail.html`), review (`review/queue.html`), unless a deliberate rename is documented in `docs/`.

- **UX-DR2:** **Shared layout fragments** are implemented and reused as **include/embed partials** (Jinja `{% include %}` or macros), aligned to reference names: `fragments/head-bootstrap.html`, `fragments/welcome-scripts.html`, `fragments/head-welcome-jqui.html`, so head/scripts stay consistent across pages that rely on Bootstrap and (where needed) jQuery UI.

- **UX-DR3:** The **mentor submission workspace** includes partials mapped from reference: `tasks/fragments/git-retrieval.html` for **Git fetch status and retrieved-source context**, and `tasks/fragments/degraded-inference-banner.html` for **LLM unavailable/degraded** messaging when AI draft is in scope.

- **UX-DR4:** **Intern** task/submission views include `intern/fragments/submission-lifecycle-badge.html` (or equivalent) so **submission/Git state** is visible as a **status badge** (not only raw error text in body copy).

### Design system and static assets

- **UX-DR5:** The UI uses **Bootstrap 5** and **jQuery** where legacy behavior depends on them; interactive patterns from the reference tree are **reproduced in Jinja2** (not replaced by a new component framework without an explicit decision).

- **UX-DR6:** **Application theming** is delivered via `css/examai-theme.css` (and any successor path) under the **`/css/**`** mount so branding/colors match the reference design intent.

- **UX-DR7:** Pages that use **jQuery UI** welcome patterns load the documented stack: `css/welcome-jqui.css`, `css/jquery-ui/themes/flick/jquery-ui.min.css`, and `js/welcome-jqui-init.js`, served under **`/css/**` and `/js/**`** per contract.

- **UX-DR8:** **WebJars** provide **Bootstrap 5.3.3**, **jQuery 3.7.1**, and **jQuery UI 1.13.2** (or equivalent pinned versions documented in `docs/`) and are reachable at **`/webjars/**`** so script/style URLs stay aligned with the inventory.

### Forms, feedback, and anti-double-submit

- **UX-DR9:** Every **state-changing** HTML form includes a **CSRF token** using **one application-wide convention** (same field name and placement across templates), matching the architecture security model.

- **UX-DR10:** Mutating **POST** flows use **redirect-after-POST** with **flash/session messages** or a **dedicated result page**—not ambiguous double-submit or “refresh repeats POST” patterns for core flows.

- **UX-DR11:** **Validation and permission errors** show **clear, user-facing messages** on the relevant page (or flash after redirect), with **safe navigation** back to task list, login, or home as appropriate—without exposing stack traces or secrets.

### Long-running and integration-driven UI

- **UX-DR12:** **Git fetch** and **AI draft** actions show **explicit in-progress** and **terminal** states in the UI (e.g. disabled buttons, banners, or section state) that reflect **backend retrieval/review state**, not indefinite spinners with no persisted meaning.

- **UX-DR13:** When the **LLM is disabled, misconfigured, or failing**, the mentor workspace shows the **degraded-inference** treatment (banner or equivalent) and keeps **human-only** draft and **publish** paths **obviously available** (primary actions remain usable).

### Accessibility (core flows)

- **UX-DR14:** **Core flows**—login, intern task list/detail, coordinate submission, mentor workspace, published feedback—use **semantic structure** (landmarks/headings), **visible labels** (or `label` associated with controls) for form fields, and **keyboard-operable** primary actions, **progressing toward WCAG 2.x** expectations for these paths (exact conformance tier TBD by procurement).

---

## Implementation tasks

Tasks are ordered for a typical **vertical slice** (foundation → intern/mentor loop → admin/coordinator/queue). Adjust sequencing per sprint. IDs support traceability to FRs.

| ID | Task | Traces to |
|----|------|-----------|
| T1 | Scaffold **FastAPI app** entry (`examai.main:app`), **StaticFiles** for `/css`, `/js`, `/webjars`, and **session/CSRF** baseline per architecture; wire **UX-DR6–UX-DR8** asset paths; **UX-DR9**. | FR4, FR33, architecture |
| T2 | Implement **`GET /actuator/health`** (contract JSON shape). | FR6 |
| T3 | Implement **public** routes: `GET /`, `GET /login`, `GET /error` and wire **form login** → session → **`GET /home`**, **`GET /app/secure`**, **`POST /logout`**; **UX-DR1**, **UX-DR2**, **UX-DR10**, **UX-DR11**, **UX-DR14** on these flows. | FR1–FR4 |
| T4 | Add **RBAC dependencies/middleware**: map roles to `/intern/**`, `/coordinator/**`, `/tasks/**`, `/review/**`, `/admin/**`. | FR5 |
| T5 | **SQLAlchemy models** for `users`, `roles`, `user_roles`, `tasks`, `task_assignments`, `submissions` per **data-models.md**; DB session wiring. | FR28, FR29 |
| T6 | **Intern** routes: task list/detail, submission POST, feedback GET — templates per **component-inventory** names/paths; **UX-DR1**, **UX-DR4**. | FR7–FR10 |
| T7 | **Mentor/admin** task CRUD and assignments: `/tasks`, `/tasks/new`, `/tasks/{id}/edit`, `/tasks/{id}/assignments`. | FR13–FR16 |
| T8 | **Submissions list** and **mentor workspace** page: `/tasks/{taskId}/submissions`, `/tasks/{taskId}/submissions/{internId}`; include **UX-DR3** partials. | FR17, FR18 |
| T9 | **`integration/git`**: httpx client, timeouts; **`POST .../fetch`** updates `submissions` Git fields and surfaces state in UI (**UX-DR3**, **UX-DR12**). | FR20, FR29, FR31 |
| T10 | **Mentor drafts** and **published reviews** persistence + **`POST .../review-draft`**, **`POST .../publish-review`** with snapshot fields. | FR22, FR23, FR30 |
| T11 | **`integration/ai`**: Ollama client; **`POST .../ai-draft-assessment`**; persist **`model_invocations`** / **`ai_drafts`**; **UX-DR12**, **UX-DR13**. | FR21, FR32 |
| T12 | **`GET /review/queue`** mentor queue view. | FR24 |
| T13 | **Admin** user list/create/edit routes and templates. | FR25–FR27 |
| T14 | **Coordinator** index and case record routes. | FR11, FR12 |
| T15 | **Docs/ops alignment**: env vars (`DATABASE_URL`, Git, Ollama) per **development-guide** / **deployment-guide**; optional root **Dockerfile/Compose** for Python when scheduled (not a functional route FR, but delivery enabler for FR6 pilot topology). | FR6, docs |

---

## FR coverage map

| FR | Epic | Brief |
|----|------|--------|
| FR1 | Epic 1 | Login page and session establishment |
| FR2 | Epic 1 | Post-login home and secure smoke page |
| FR3 | Epic 1 | Logout |
| FR4 | Epic 1 | Public routes and static asset access rules |
| FR5 | Epic 1 | Role-gated URL spaces |
| FR6 | Epic 1 | Health endpoint |
| FR7 | Epic 3 | Intern task list |
| FR8 | Epic 3 | Intern task detail |
| FR9 | Epic 3 | Submit/update coordinates |
| FR10 | Epic 3 | Intern feedback view |
| FR11 | Epic 7 | Coordinator index |
| FR12 | Epic 7 | Coordinator case record |
| FR13 | Epic 2 | List tasks |
| FR14 | Epic 2 | Create task |
| FR15 | Epic 2 | Edit task |
| FR16 | Epic 2 | Assign interns to task |
| FR17 | Epic 4 | Submissions list for task |
| FR18 | Epic 4 | Mentor submission workspace |
| FR19 | Epic 4 | Update coordinates (mentor) |
| FR20 | Epic 4 | Trigger Git fetch |
| FR21 | Epic 5 | Request AI draft assessment |
| FR22 | Epic 4 | Save mentor draft review |
| FR23 | Epic 4 | Publish review |
| FR24 | Epic 4 | Review queue |
| FR25 | Epic 6 | List users |
| FR26 | Epic 6 | Create user |
| FR27 | Epic 6 | Edit user |
| FR28 | Epics 1–6 | ORM/schema aligned with data-models (incremental per epic) |
| FR29 | Epic 3–4 | Submission Git state and visibility |
| FR30 | Epic 4 | Published review snapshot metadata |
| FR31 | Epic 4 | Git integration layer and UI state |
| FR32 | Epic 5 | Ollama integration, audit, degraded surfacing |
| FR33 | Epic 1 | Server-rendered UI, CSRF, static mounts |

## UX coverage map

| UX-DR | Primary epic | Notes |
|-------|----------------|--------|
| UX-DR1 | Epics 1–7 | Template paths/names per area |
| UX-DR2 | Epic 1 | Shared head/script fragments |
| UX-DR3 | Epic 4 | Git retrieval + degraded-inference partials |
| UX-DR4 | Epic 3 | Intern submission lifecycle badge |
| UX-DR5–UX-DR8 | Epic 1 | Bootstrap/jQuery/WebJars/theme |
| UX-DR9 | Epic 1 | CSRF convention |
| UX-DR10 | Epics 1–7 | Redirect-after-POST / flash |
| UX-DR11 | Epics 1–7 | User-facing errors, safe navigation |
| UX-DR12 | Epics 4–5 | Long-running Git/AI UI state |
| UX-DR13 | Epic 5 | Degraded LLM; human path visible |
| UX-DR14 | Epics 1, 3, 4 | Core-flow accessibility |

## Epic list

### Epic 1: Platform shell — authentication, health, static web, and role-based access

Users and operators get a working shell: **sign-in**, **session**, **logout**, **health**, **static assets**, **CSRF-safe** forms, and **role-appropriate** URL access. Delivers the foundation for all other epics.

**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR28 (users/roles/session tables as needed), FR33.

### Epic 2: Program tasks — create, edit, and assign work to interns

Mentors and administrators **define program tasks** and **assign interns** so downstream intern and mentor flows have work to act on.

**FRs covered:** FR13, FR14, FR15, FR16, FR28 (tasks, task_assignments).

### Epic 3: Intern participation — assigned tasks, coordinates, and published feedback

Interns **see assigned work**, **submit version-control coordinates**, and **read published feedback** tied to their submission.

**FRs covered:** FR7, FR8, FR9, FR10, FR28, FR29 (submissions; intern-visible state; reading published outcomes).

### Epic 4: Mentor review workspace — retrieval, drafts, publish, and queue

Mentors **triage submissions**, **fetch source**, **write drafts**, **publish** outcomes with **snapshot provenance**, and use the **review queue**.

**FRs covered:** FR17, FR18, FR19, FR20, FR22, FR23, FR24, FR28–FR31, FR29, FR30.

### Epic 5: AI-assisted draft assessment (audited) and degraded UX

Mentors **optionally request AI drafts** when Ollama is configured; the system **persists audit records** and **surfaces degraded** LLM state without blocking human review.

**FRs covered:** FR21, FR32, FR28 (model_invocations, ai_drafts).

### Epic 6: Administrator — user and role management

Administrators **maintain accounts** and **role membership** for the program.

**FRs covered:** FR25, FR26, FR27, FR28 (user admin slice).

### Epic 7: Coordinator — case visibility

Coordinators **see case-level status** for oversight without taking the mentor pen.

**FRs covered:** FR11, FR12.

---

## Epic 1: Platform shell — authentication, health, static web, and role-based access

Mentors, interns, coordinators, and administrators can **sign in** and reach **role-appropriate** pages; operators can verify **liveness**; everyone receives **correct static assets** and **CSRF-protected** forms.

### Story 1.1: Public pages, static assets, and WebJar UI stack

As a **visitor**,  
I want **landing, login, and error pages with Bootstrap/jQuery/WebJars and theme CSS served under the contract paths**,  
So that **the app shell matches the documented static surface**.

**Acceptance Criteria:**

**Given** the app is running  
**When** I request `GET /`, `GET /login`, `GET /error` and static paths under `/css/**`, `/js/**`, `/webjars/**`  
**Then** responses return the expected HTML or assets per **[docs/api-contracts.md](../../docs/api-contracts.md)**  
**And** shared fragments align with **UX-DR1** (core templates), **UX-DR2**, **UX-DR5–UX-DR8**

### Story 1.2: Operator health check

As an **operator**,  
I want **`GET /actuator/health` to return contract-shaped JSON**,  
So that **deployments and smoke scripts can verify liveness**.

**Acceptance Criteria:**

**Given** the app is running  
**When** I `GET /actuator/health` (and `/actuator/health/**` if supported)  
**Then** the response body matches the documented shape (e.g. `{"status":"UP"}`) per **[docs/deployment-guide.md](../../docs/deployment-guide.md)**  
**And** no authentication is required (**FR6**, **FR4**)

### Story 1.3: Sign in, session, home, secure page, and sign out

As a **user with credentials**,  
I want **to sign in, land on a home page, open a secure smoke page, and sign out**,  
So that **I have a normal authenticated session lifecycle**.

**Acceptance Criteria:**

**Given** a valid user exists in the database  
**When** I submit credentials on `POST` login and visit `GET /home` and `GET /app/secure`  
**Then** I am authenticated per **FR1–FR2**  
**When** I `POST /logout`  
**Then** the session ends and protected pages reject access (**FR3**)  
**And** forms use **redirect-after-POST** or flash per **UX-DR10**; errors follow **UX-DR11**; login flow supports **UX-DR14**

### Story 1.4: Role-based access to URL spaces

As **any authenticated user**,  
I want **my role to determine which route prefixes I may use**,  
So that **intern, mentor, coordinator, and admin areas stay separated**.

**Acceptance Criteria:**

**Given** users with distinct roles  
**When** each requests routes under `/intern/**`, `/coordinator/**`, `/tasks/**`, `/review/**`, `/admin/**`  
**Then** access matches **[docs/api-contracts.md](../../docs/api-contracts.md)** and architecture RBAC rules (**FR5**)

### Story 1.5: CSRF on mutating requests

As a **security stakeholder**,  
I want **every state-changing form to include a CSRF token under one convention**,  
So that **POST flows resist cross-site forgery**.

**Acceptance Criteria:**

**Given** any mutating HTML form in scope for this epic  
**When** the form is rendered  
**Then** it includes a CSRF token field consistent across templates (**FR33**, **UX-DR9**)

---

## Epic 2: Program tasks — create, edit, and assign work to interns

Mentors and administrators **create and edit tasks** and **assign interns** so the program has structured work.

### Story 2.1: List, create, and edit tasks

As a **mentor or administrator**,  
I want **to list tasks and create or edit a task**,  
So that **program work is defined in the system**.

**Acceptance Criteria:**

**Given** I am authenticated with mentor or admin role  
**When** I use `GET /tasks`, `GET|POST /tasks/new`, `GET|POST /tasks/{id}/edit`  
**Then** tasks are listed and persisted per **FR13–FR15** and **[docs/data-models.md](../../docs/data-models.md)**  
**And** templates follow **UX-DR1** (tasks list/form); mutating flows use **UX-DR10–UX-DR11**

### Story 2.2: Assign interns to a task

As a **mentor or administrator**,  
I want **to assign interns to a task**,  
So that **interns see the right assignments**.

**Acceptance Criteria:**

**Given** a task exists  
**When** I use `GET|POST /tasks/{id}/assignments`  
**Then** `task_assignments` rows reflect chosen interns (**FR16**, **FR28**)

---

## Epic 3: Intern participation — assigned tasks, coordinates, and published feedback

Interns **complete the assigned loop**: view tasks, **submit coordinates**, **see status**, and **read published feedback**.

### Story 3.1: View assigned tasks and task detail

As an **intern**,  
I want **to list and open my assigned tasks**,  
So that **I know what work is required**.

**Acceptance Criteria:**

**Given** I am logged in as an intern with assignments  
**When** I open `GET /intern/tasks` and `GET /intern/tasks/{taskId}`  
**Then** I see my tasks and task detail per **FR7–FR8** and **UX-DR1**

### Story 3.2: Submit or update submission coordinates

As an **intern**,  
I want **to submit or update repo, commit, and path scope for my task**,  
So that **mentors can retrieve my work**.

**Acceptance Criteria:**

**Given** I have an assigned task  
**When** I `POST /intern/tasks/{taskId}/submission` with valid coordinates  
**Then** a `submissions` row exists/updates per contract (**FR9**, **FR28–FR29**)

### Story 3.3: View published feedback

As an **intern**,  
I want **to open published feedback for my submission**,  
So that **I see official outcomes**.

**Acceptance Criteria:**

**Given** a published review exists for my submission  
**When** I `GET /intern/submissions/{submissionId}/feedback`  
**Then** I see published scores/narrative per **FR10** (and snapshot context as designed)

### Story 3.4: Submission lifecycle status badge

As an **intern**,  
I want **a clear status indicator for my submission pipeline**,  
So that **I understand retrieval/review state without raw errors only**.

**Acceptance Criteria:**

**Given** I am on intern task/detail or related views  
**When** the page renders  
**Then** a badge or equivalent shows submission/Git lifecycle state (**UX-DR4**, aligns with **FR29** visibility)

---

## Epic 4: Mentor review workspace — retrieval, drafts, publish, and queue

Mentors **run the assessment loop**: **workspace**, **Git fetch**, **draft**, **publish** with **provenance**, and **queue**.

### Story 4.1: Submissions list and mentor workspace

As a **mentor or administrator**,  
I want **to list submissions for a task and open a submission workspace**,  
So that **I can review intern work**.

**Acceptance Criteria:**

**Given** submissions exist for a task  
**When** I use `GET /tasks/{taskId}/submissions` and `GET /tasks/{taskId}/submissions/{internId}`  
**Then** I see the list and workspace per **FR17–FR18** and **UX-DR1** (submission-detail template)

### Story 4.2: Update coordinates from the workspace

As a **mentor or administrator**,  
I want **to correct or enter coordinates from the mentor side**,  
So that **retrieval can proceed even if the intern made mistakes**.

**Acceptance Criteria:**

**Given** I am on the workspace  
**When** I `POST .../coordinates`  
**Then** submission coordinates update per **FR19**

### Story 4.3: Trigger Git fetch with visible state

As a **mentor or administrator**,  
I want **to fetch normalized source and see success, failure, or in-progress state**,  
So that **I review real code, not stale guesses**.

**Acceptance Criteria:**

**Given** Git integration is configured  
**When** I `POST .../fetch`  
**Then** `git_retrieval_*` fields update per **FR20**, **FR29**, **FR31**  
**And** the workspace shows retrieval UI per **UX-DR3**, **UX-DR12** (no silent hang)

### Story 4.4: Save mentor draft review

As a **mentor**,  
I want **to save rubric scores and narrative as a draft**,  
So that **I can iterate before publishing**.

**Acceptance Criteria:**

**Given** I am on the workspace  
**When** I `POST .../review-draft`  
**Then** `mentor_review_drafts` persists scores/narrative per **FR22** and data-models

### Story 4.5: Publish review with snapshot metadata

As a **mentor**,  
I want **to publish my review as the official outcome with snapshot fields**,  
So that **feedback is tied to evidence at publish time**.

**Acceptance Criteria:**

**Given** a draft exists  
**When** I `POST .../publish-review`  
**Then** `published_reviews` includes snapshot fields per **FR23**, **FR30**

### Story 4.6: Mentor review queue

As a **mentor**,  
I want **a queue of outstanding review work**,  
So that **I can triage workload**.

**Acceptance Criteria:**

**Given** I am a mentor  
**When** I `GET /review/queue`  
**Then** I see the queue view per **FR24** and **UX-DR1** (`review/queue.html`)

---

## Epic 5: AI-assisted draft assessment (audited) and degraded UX

Mentors **optionally** use **Ollama** for drafts; the system **audits** successful inference and **surfaces degradation**.

### Story 5.1: Request AI draft with audit trail

As a **mentor**,  
I want **to request an AI draft assessment when the LLM is available**,  
So that **I get a starting point without losing accountability**.

**Acceptance Criteria:**

**Given** Ollama is configured and the workspace is loaded  
**When** I `POST .../ai-draft-assessment` and inference succeeds  
**Then** `model_invocations` and `ai_drafts` record the run and text per **FR21**, **FR32**, **FR28**  
**And** integration logic lives outside route handlers per architecture

### Story 5.2: Degraded LLM experience without blocking humans

As a **mentor**,  
I want **clear degraded messaging and an obvious human-only path when the LLM fails**,  
So that **I can still publish without waiting for AI**.

**Acceptance Criteria:**

**Given** Ollama is down, misconfigured, or times out  
**When** I use the workspace  
**Then** degraded state is visible (**FR32**, **UX-DR12**, **UX-DR13**)  
**And** draft save and publish remain usable (**FR22–FR23**)

---

## Epic 6: Administrator — user and role management

Administrators **provision users** and **assign roles** for the program.

### Story 6.1: List users

As an **administrator**,  
I want **to list user accounts**,  
So that **I can manage cohort membership**.

**Acceptance Criteria:**

**Given** I am an administrator  
**When** I `GET /admin/users`  
**Then** I see the user list per **FR25** and **UX-DR1** (admin list template)

### Story 6.2: Create user with roles

As an **administrator**,  
I want **to create a user and assign roles**,  
So that **new cohort members can sign in with correct access**.

**Acceptance Criteria:**

**Given** I use `GET|POST /admin/users/new`  
**Then** users and `user_roles` persist per **FR26**, **FR28**

### Story 6.3: Edit user and roles

As an **administrator**,  
I want **to edit an existing user**,  
So that **roles and details stay current**.

**Acceptance Criteria:**

**Given** a user exists  
**When** I `GET|POST /admin/users/{id}/edit`  
**Then** updates persist per **FR27**

---

## Epic 7: Coordinator — case visibility

Coordinators **see submission/case status** for oversight.

### Story 7.1: Coordinator index and case record

As a **coordinator**,  
I want **an index and a case record for a submission**,  
So that **I can spot stuck work without mentor tools**.

**Acceptance Criteria:**

**Given** I am logged in as a coordinator  
**When** I `GET /coordinator` and `GET /coordinator/cases/{submissionId}`  
**Then** I see coordinator-scoped views per **FR11–FR12** and **UX-DR1**

---

## Epic 8: Containerized runtime, database bootstrap, and README operations

**Theme:** Ship **Dockerfile(s)** and **Docker Compose** so operators can run the **application**, **PostgreSQL**, and **LLM (e.g. Ollama)** consistently; **seed** an initial **administrator** via DB init scripts; run **Liquibase** migrations on application startup; and extend **`README-Python.md`** with accurate **run instructions** and **user-flow** summaries for every role.

**Suggested sequence:** Implement **8.1 → 8.2 → 8.3** first (stack + data). Then **8.4–8.6** (README aligned with compose service names and ports). Finish with **8.7** (user flows) so routes and roles match the running product.

### Story 8.1: Dockerfiles and Docker Compose for app, database, and LLM

As an **operator or developer**,  
I want **Dockerfile(s) and a `docker-compose` definition** that run the FastAPI app, PostgreSQL, and the LLM service,  
So that **I can reproduce the full stack locally or in a lab without manual installs**.

**Acceptance Criteria:**

**Given** the repository contains the new container definitions  
**When** I follow the compose file’s documented prerequisites (e.g. `.env` variables)  
**Then** I can build images and start **application**, **database**, and **LLM** services with **named services** and **stable ports** suitable for README cross-links  
**And** the app container receives configuration for DB host and LLM base URL via environment variables consistent with **`docs/deployment-guide.md`** / architecture  
**And** volumes or bind mounts are defined where needed for persistence (e.g. Postgres data, optional Ollama models path if applicable)

### Story 8.2: Database init scripts with administrator seed

As an **operator**,  
I want **SQL (or scripted) init** that creates baseline schema expectations and an **initial administrator account**,  
So that **a fresh database container is usable for first login without manual SQL**.

**Acceptance Criteria:**

**Given** Postgres starts with an init hook (e.g. `docker-entrypoint-initdb.d`) or documented equivalent  
**When** the init runs on an **empty** data directory  
**Then** required roles/users/tables expected by the app exist or are compatible with **Liquibase** baseline (no conflicting duplicate DDL if Liquibase owns schema)  
**And** at least one **administrator** user exists with credentials sourced from **secrets/env** (not hard-coded in repo), documented for operators  
**And** init is **idempotent** or clearly scoped so re-apply behavior is documented

### Story 8.3: Liquibase migrations on application startup

As an **operator**,  
I want **Liquibase to apply changelogs when the application starts**,  
So that **schema stays aligned with code in every environment that runs the container**.

**Acceptance Criteria:**

**Given** the app image starts with database reachable  
**When** the process boots (entrypoint or application main)  
**Then** Liquibase runs against the configured database URL (per project tooling) and applies pending changes  
**And** startup **fails fast** with a clear log message if migration fails (no silent partial state)  
**And** interaction with **Story 8.2** init is defined (e.g. baseline vs. seed-only) to avoid duplicate or conflicting DDL

### Story 8.4: README-Python — run the application as a Docker image

As a **developer**,  
I want **`README-Python.md` to explain how to build and run the application container**,  
So that **I can start the server from Docker without guessing compose service names or ports**.

**Acceptance Criteria:**

**Given** **Story 8.1** compose/service names exist  
**When** I read **`README-Python.md`**  
**Then** I find **build** and **run** commands (or compose targets) for the **application** image, environment variables, and health check URL (e.g. **`GET /actuator/health`**)  
**And** the steps match the actual **`Dockerfile`/compose** in the repo

### Story 8.5: README-Python — run the database as a Docker image

As a **developer**,  
I want **`README-Python.md` to document running PostgreSQL via Docker**,  
So that **I can run or troubleshoot the DB in isolation or understand compose networking**.

**Acceptance Criteria:**

**Given** **Story 8.1** defines the DB service  
**When** I read **`README-Python.md`**  
**Then** I see how to start the **database** container (standalone or via compose), connection parameters, volume/persistence notes, and how the app connects  
**And** **Story 8.2** seed/admin assumptions are referenced or summarized where relevant

### Story 8.6: README-Python — run the LLM as a Docker image

As a **developer**,  
I want **`README-Python.md` to document running the LLM (e.g. Ollama) in Docker**,  
So that **AI draft features can be enabled consistently with deployment architecture**.

**Acceptance Criteria:**

**Given** **Story 8.1** defines the LLM service  
**When** I read **`README-Python.md`**  
**Then** I see how to run the **LLM** image, required **model pull** or mount steps, ports, and the **environment variables** the app uses to reach the LLM  
**And** behavior matches **FR31–FR32** / degraded-LLM expectations at a high level (point to **`docs/`** for detail if needed)

### Story 8.7: README-Python — user flows for all user types

As a **new contributor or operator**,  
I want **`README-Python.md` to summarize user flows by role**,  
So that **I can sanity-check intern, mentor, coordinator, and administrator journeys after bringing the stack up**.

**Acceptance Criteria:**

**Given** the product’s roles (**FR4–FR5**, **FR7–FR27**)  
**When** I read **`README-Python.md`**  
**Then** I see a concise **user-flow** section covering **intern**, **mentor (or administrator on mentor routes)**, **coordinator**, and **administrator**, with **representative URLs or navigation** (aligned with **`docs/api-contracts.md`** / epics)  
**And** flows are accurate for the current release (no obsolete routes)

### Story 8.8: Slim app image — Liquibase Compose sidecar (no OpenJDK in app)

As an **operator or developer**,  
I want the **application Docker image to stay Python-only** while **Liquibase** still applies **`db/changelog/`** reliably,  
So that **image builds do not bundle OpenJDK**, **failed Liquibase zip layouts do not break `docker build`**, and **migrations remain ordered before the app**.

**Acceptance Criteria:**

**Given** **`docker-compose.yml`** defines a one-shot **`db-migrate`** service using the official **`liquibase/liquibase`** image  
**When** **`db`** is healthy  
**Then** **`db-migrate`** runs **`liquibase update`** against the mounted **`db/changelog/`** and exits successfully before **`app`** starts (e.g. **`depends_on`** with **`service_completed_successfully`**)  
**And** the **`app`** **`Dockerfile`** does not install **OpenJDK** or download the Liquibase OSS zip  
**And** **`EXAMINAI_USE_LIQUIBASE=1`** on **`app`** still means the server skips SQLAlchemy **`create_all`** for PostgreSQL  
**And** **README** / **deployment-guide** describe the split (sidecar vs. optional **`python -m examai.liquibase_cli`** on the host)

---

## Non-functional requirements

_NFR inventory not populated in this document scope; add under a future pass if needed._

---

## BMAD workflow — Create Epics and Stories

**Status:** Complete for the original PRD-aligned backlog; **Epic 8** (containerized runtime and README) was added as a **2026-04-15** supplement. Requirements inventory, epic list, coverage maps, and user stories are recorded above; this artifact feeds **implementation readiness**, **sprint planning**, and **per-story development**.
