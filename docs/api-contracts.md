# HTTP Surface and Form Actions (Examinai)

This document is the **contract** for the **Python (FastAPI)** implementation. “API” means **browser-facing HTTP routes**: GET pages and POST form actions. There is no separate JSON REST API for the main product UI.

**UI engine:** **Jinja2** (active). **`JAVA_APP/.../templates/`** (if snapshot exists): Thymeleaf sources — **reference only** for naming and layout parity.

**Authentication:** **Form login** (`/login`), session cookie, **CSRF** on POSTs — **behavior** matches the legacy Spring Security setup; see [architecture.md](./architecture.md) for role routing. Implementation is Python (sessions per `_bmad-output/project-context.md`).

## Public and static

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Landing / index |
| GET | `/login` | Login page |
| GET | `/error` | Error page (framework) |
| GET | `/webjars/**` | Bootstrap, jQuery, jQuery UI (WebJars) |
| GET | `/css/**`, `/js/**` | Static assets |
| GET | `/actuator/health`, `/actuator/health/**` | Health checks |

## Authenticated (any logged-in user)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/home` | Post-login home |
| GET | `/app/secure` | Secure smoke page |

## Role: INTERN

Base: `/intern/**`

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/intern/tasks` | Intern task list |
| GET | `/intern/tasks/{taskId}` | Task detail |
| POST | `/intern/tasks/{taskId}/submission` | Submit/update submission coordinates |
| GET | `/intern/submissions/{submissionId}/feedback` | Feedback view |

## Role: COORDINATOR

Base: `/coordinator/**`

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/coordinator` | Coordinator index |
| GET | `/coordinator/cases/{submissionId}` | Case record view |

## Role: MENTOR or ADMINISTRATOR

### Tasks and assignments

Base: `/tasks/**` (shared prefix; multiple controllers).

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/tasks` | Task list |
| GET | `/tasks/new` | Create task form |
| POST | `/tasks/new` | Create task |
| GET | `/tasks/{id}/edit` | Edit task form |
| POST | `/tasks/{id}/edit` | Update task |
| GET | `/tasks/{id}/assignments` | Assign interns to task |
| POST | `/tasks/{id}/assignments` | Save assignments |
| GET | `/tasks/{taskId}/submissions` | Submissions list for task |
| GET | `/tasks/{taskId}/submissions/{internId}` | Mentor submission workspace |
| POST | `/tasks/{taskId}/submissions/{internId}/coordinates` | Update repo coordinates |
| POST | `/tasks/{taskId}/submissions/{internId}/fetch` | Trigger Git fetch |
| POST | `/tasks/{taskId}/submissions/{internId}/ai-draft-assessment` | Request AI draft |
| POST | `/tasks/{taskId}/submissions/{internId}/review-draft` | Save mentor draft review |
| POST | `/tasks/{taskId}/submissions/{internId}/publish-review` | Publish review |

### Review queue

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/review/queue` | Mentor review queue |

## Role: ADMINISTRATOR

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/admin/users` | User list |
| GET | `/admin/users/new` | New user form |
| POST | `/admin/users/new` | Create user |
| GET | `/admin/users/{id}/edit` | Edit user |
| POST | `/admin/users/{id}/edit` | Update user |

## Logout

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/logout` | Logout |

## External integration (not browser routes)

- **Ollama:** HTTP client (e.g. **httpx**) to `OLLAMA_BASE_URL` (e.g. `http://127.0.0.1:11434`). Legacy used Spring AI — **reference** only.
- **Git provider:** HTTP client to `GIT_PROVIDER_BASE_URL` (GitHub REST v3–compatible). Legacy `GitSourceClient` is **reference** only.

---

_Contract for Python implementation; legacy Spring behavior as reference._

