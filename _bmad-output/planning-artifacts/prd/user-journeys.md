# User Journeys

## Intern Maya — happy path

**Opening:** Maya is assigned a coding task for the internship program. She keeps work in a private repo and needs official credit without emailing ZIP files.

**Rising action:** She logs in, opens **Intern → tasks**, reads the task, and submits **repository, commit SHA, and path scope** on the task detail page. She fixes validation issues until the submission is accepted.

**Climax:** After the mentor **publishes** a review, she opens **feedback** for her submission and sees structured scores and narrative tied to the work she submitted.

**Resolution:** She has a single durable record of feedback aligned to her coordinates—not a lost thread in chat.

**Failure / recovery:** If she mistypes a ref, she updates coordinates and resubmits; status makes clear what is wrong.

## Mentor Diego — degraded AI, human publish

**Opening:** Diego reviews several interns. Ollama is down or timing out (Compose restart, model missing).

**Rising action:** He opens the **mentor submission workspace**, sees a **degraded inference** signal, and skips AI draft. He still runs **Git fetch** when the provider is up, fills the **draft review** from normalized source, and **publishes**.

**Climax:** Interns receive published feedback without waiting for the LLM; audit shows no successful model invocation for that attempt—consistent with policy.

**Resolution:** The program keeps moving; AI is optional, not a blocker.

**Requirements surfaced:** Degraded banners, human-only publish path, clear intern-visible distinction when AI was not used.

## Coordinator Priya — oversight without taking the pen

**Opening:** Priya needs to confirm a case is moving and spot stuck submissions.

**Rising action:** She uses **Coordinator** routes to open a **case record** for a submission and sees status relevant to coordination (assignments, submission state, published vs. draft as policy allows).

**Climax:** She identifies a stuck flow and nudges the mentor or intern out of band—without needing admin keys for day-to-day triage.

**Resolution:** Visibility matches role; she does not need mentor-intern DMs to guess state.

## Administrator Sam — users and access

**Opening:** A new cohort joins; accounts and roles must exist before interns can log in.

**Rising action:** Sam uses **Admin → users** to create or edit users and assign **intern / mentor / coordinator / administrator** roles as defined by the program.

**Climax:** The next login routes each user to the right home surface per role.

**Resolution:** RBAC and URL gates match **documented route rules** in `docs/api-contracts.md`.

## Operator — deploy and smoke

**Opening:** A release is deployed to the pilot stack (app + Postgres + Ollama).

**Rising action:** They rely on **`/actuator/health`**, Compose logs, and a short **manual** happy-path smoke (login optional, health required).

**Climax:** Green health and one manual path confirm the build is alive; no automated suite is required in this phase.

**Resolution:** Operations match **Delivery and testing strategy**.

## Journey Requirements Summary

| Area | Capabilities implied |
|------|----------------------|
| Intern | Task list/detail, submission coordinates, feedback view |
| Mentor | Submission workspace, Git fetch, draft review, optional AI draft, publish, degraded LLM UX |
| Coordinator | Case/submission visibility within role |
| Administrator | User CRUD, role assignment |
| Ops | Health endpoint, manual/smoke validation (no automated test gate in this phase) |
| Cross-cutting | Sessions, CSRF on POSTs, role-based routing, audit fields for successful AI |
