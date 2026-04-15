# Data Models and Schema (Examinai)

**Authority for the Python app:** **[This document](./data-models.md)** summarizes tables and columns for **`src/examai/`** SQLAlchemy models and application code. **PostgreSQL** is the database.

**Migrations:** The **Docker** stack (see `docker-compose.yml`, `Dockerfile`) runs **Liquibase** on startup when **`EXAMINAI_USE_LIQUIBASE`** is set; changelogs live under **`db/changelog/`** (baseline: `001-baseline.postgresql.sql`). **Do not** duplicate that DDL in Postgres `docker-entrypoint-initdb.d` — init scripts there are for optional hooks only; **Liquibase owns DDL** in that deployment mode. For local development on **SQLite** or Postgres without Liquibase, the app may still use SQLAlchemy **`create_all`** (see `examai.database.create_schema`). **Alembic** remains available in **`pyproject.toml`** for a future single migration pipeline; until Alembic revisions exist, treat **Liquibase** as the source of truth for containerized PostgreSQL schema.

**Reference (`JAVA_APP/` — if a snapshot exists locally):** Historical **Liquibase** YAML under **`JAVA_APP/src/main/resources/db/changelog/`** (master: `db.changelog-master.yaml`) can be used to **cross-check** DDL details (column types, constraints). It is **not** a runtime or deployment dependency of the Python stack. **JPA** entities under `com.examinai.app.domain` in that snapshot map the same tables — use them only to verify names and relationships when building SQLAlchemy models; **do not** treat JPA as a source for new Python code.

## Identity and access

### `users`

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| email | varchar(320) | Unique |
| password_hash | varchar(255) | BCrypt |
| created_at, updated_at | timestamptz | |
| enabled | boolean | Added in `002-user-account-enabled.yaml`; default true |

### `roles`

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| name | varchar(64) | Unique; seeded: `intern`, `mentor`, `administrator`, `coordinator` |

### `user_roles`

Composite PK `(user_id, role_id)` → FK to `users`, `roles` (CASCADE delete).

## Program work

### `tasks`

Program tasks: `title`, `description`, `due_date`, `created_at`, `updated_at`.

### `task_assignments`

Links `task_id` + `intern_user_id` (unique pair); FKs to `tasks`, `users`.

### `submissions`

One row per `(task_id, intern_user_id)` pair (unique): `repo_identifier`, `commit_sha`, `path_scope`, `status`, timestamps.

**Git retrieval (Epic 3):** `git_retrieval_state`, `git_retrieval_error_code`, `git_retrieved_text`, `git_last_success_at`, `git_last_attempt_at`, `git_fetch_version`.

## Mentor review

### `mentor_review_drafts`

WIP rubric per submission (unique `submission_id`): scores (quality, readability, correctness), `narrative_feedback`, `mentor_user_id`, `updated_at`.

### `published_reviews`

Published outcome per submission: scores, narrative, `publishing_mentor_user_id`, `published_at`, snapshot fields (`snapshot_commit_sha`, `snapshot_git_fetch_version`, `snapshot_path_scope`).

## AI audit (Epic 5)

### `model_invocations`

Per successful inference: `submission_id`, `invoked_at`, `model_name`, `model_version`, `prompt_hash`; index on `(submission_id, invoked_at)`.

### `ai_drafts`

`assessment_text` linked to `model_invocation_id` (unique FK to `model_invocations`).

## Entity map (JPA names — reference snapshot only)

| Entity (legacy JPA, if `JAVA_APP/` present) | Table |
|---------------------------------------------|-------|
| `User` | users |
| `Role` | roles |
| `Task` | tasks |
| `TaskAssignment` | task_assignments |
| `Submission` | submissions |
| `MentorReviewDraft` | mentor_review_drafts |
| `PublishedReview` | published_reviews |
| `ModelInvocation` | model_invocations |
| `AiDraft` | ai_drafts |

Implement corresponding **SQLAlchemy** models under `src/examai/` as features land.

---

_Implementation: this doc + PostgreSQL + ORM in `src/examai/`. **Liquibase** changelogs at **`db/changelog/`** for Docker PostgreSQL; **`JAVA_APP/`** Liquibase/JPA — reference only._
