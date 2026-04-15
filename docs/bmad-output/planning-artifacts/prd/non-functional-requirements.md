# Non-Functional Requirements

## Performance

- **NFR-P1:** Interactive page transitions for core flows (task list → detail → submit; mentor workspace) complete without indefinite blocking; long-running operations (Git fetch, LLM request) show explicit in-progress or terminal state to the user.
- **NFR-P2:** Git provider and LLM calls use bounded timeouts and retries configurable per environment so workers do not hang unbounded.

## Security

- **NFR-S1:** Passwords are stored using a strong one-way hash; credentials are never logged or returned in API responses.
- **NFR-S2:** Session and CSRF protections apply to mutating requests per the product’s security model.
- **NFR-S3:** Secrets (database, Git token, LLM endpoints) are supplied via environment or secure configuration—not committed to source control.
- **NFR-S4:** Git and LLM credentials are not embedded in prompts, logs, or intern-visible pages.

## Scalability

- **NFR-SC1:** The pilot deployment supports concurrent mentors and interns typical of a single program cohort without requiring horizontal scaling as a prerequisite for MVP (vertical scaling acceptable initially).

## Accessibility

- **NFR-A1:** Core flows (login, task view, submission, published feedback) are implementable to progress toward **WCAG 2.x** conformance; exact level is confirmed when procurement or policy requires it.

## Integration

- **NFR-I1:** Git provider integration tolerates rate limits and transient failures with user-visible state and without corrupting stored submission evidence.
- **NFR-I2:** LLM integration tolerates model unavailability with mentor-visible degraded behavior and without blocking human-only publish.

## Reliability & operability

- **NFR-R1:** A health endpoint returns a consistent success/failure signal suitable for load balancers and scripted smoke checks.
- **NFR-R2:** Database schema changes are tracked through an agreed migration process so environments stay aligned with the data model.
