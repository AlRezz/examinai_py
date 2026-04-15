# Functional Requirements

## Authentication & session

- **FR1:** A user can sign in with credentials and establish an authenticated session.
- **FR2:** An authenticated user can sign out.
- **FR3:** An unauthenticated user cannot access role-protected workflows except where explicitly public (e.g. login, static assets, health).

## Role-based access

- **FR4:** The system enforces role-appropriate access to URL spaces (intern, mentor, coordinator, administrator) per the product’s route rules.
- **FR5:** After authentication, a user is directed to an experience appropriate to their role.

## Tasks & program work

- **FR6:** A mentor or administrator can create, view, edit, and list program tasks.
- **FR7:** A mentor or administrator can assign interns to tasks.
- **FR8:** An intern can view tasks assigned to them and open task details.

## Submissions & source evidence

- **FR9:** An intern can submit or update version-control coordinates (repository, commit, path scope) for an assigned task.
- **FR10:** The system stores submission state relevant to retrieval and review (including error state when retrieval fails).
- **FR11:** A mentor can trigger retrieval of normalized source from the configured Git provider for a submission, when integrated.
- **FR12:** A mentor can see whether retrieval succeeded, failed, or is in progress, without silent failure.

## Mentor review (draft and publish)

- **FR13:** A mentor can maintain a draft review (scores and narrative) for a submission.
- **FR14:** A mentor can publish a review so it becomes the official outcome for that submission.
- **FR15:** A mentor can publish a human-only review when AI assistance is unavailable or unused.
- **FR16:** Published feedback includes snapshot metadata tying the outcome to the evidence at publish time (e.g. commit, fetch version, path scope) as defined by the data model.

## AI-assisted draft assessment

- **FR17:** A mentor can request an AI-generated draft assessment for a submission when the LLM integration is enabled.
- **FR18:** The system persists an audit record for each successful AI inference used for draft assessment (model identity, timing, linkage to draft content).
- **FR19:** The system surfaces degraded or unavailable LLM state to mentors in the review workflow.
- **FR20:** Intern-facing outcomes distinguish human-published feedback from optional AI draft content as required by product policy.

## Intern feedback consumption

- **FR21:** An intern can view published feedback for their submission.

## Coordinator oversight

- **FR22:** A coordinator can access coordinator-scoped views (e.g. case/submission visibility) per role rules.

## User administration

- **FR23:** An administrator can list, create, and edit user accounts.
- **FR24:** An administrator can assign roles to users (intern, mentor, coordinator, administrator).

## Review queue & workload (full product)

- **FR25:** A mentor can access a review queue view for outstanding work, when that route is in scope for the release.

## Operations

- **FR26:** An operator can verify application liveness via a documented health endpoint.

## Compliance & data handling (domain)

- **FR27:** The system limits use of personal/sensitive data in AI prompts to what the program requires (task context and retrieved source per policy).
- **FR28:** Role boundaries prevent users from accessing other users’ prohibited data per the access model.

## Integrations (behavioral)

- **FR29:** The system applies configurable behavior for Git provider failures (timeouts, errors, user-visible state).
- **FR30:** The system applies configurable behavior for LLM failures (timeouts, errors, degraded messaging).
