-- liquibase formatted sql

-- changeset examinai:001-pgcrypto dbms:postgresql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- changeset examinai:002-roles dbms:postgresql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(64) NOT NULL UNIQUE
);

-- changeset examinai:003-users dbms:postgresql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(320) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- changeset examinai:004-user-roles dbms:postgresql
CREATE TABLE user_roles (
    user_id UUID NOT NULL,
    role_id UUID NOT NULL,
    PRIMARY KEY (user_id, role_id),
    CONSTRAINT fk_user_roles_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_user_roles_role FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
);

-- changeset examinai:005-tasks dbms:postgresql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    due_date DATE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- changeset examinai:006-task-assignments dbms:postgresql
CREATE TABLE task_assignments (
    task_id UUID NOT NULL,
    intern_user_id UUID NOT NULL,
    PRIMARY KEY (task_id, intern_user_id),
    CONSTRAINT fk_task_assignments_task FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
    CONSTRAINT fk_task_assignments_intern FOREIGN KEY (intern_user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- changeset examinai:007-submissions dbms:postgresql
CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL,
    intern_user_id UUID NOT NULL,
    repo_identifier VARCHAR(500) NOT NULL,
    commit_sha VARCHAR(64),
    path_scope VARCHAR(2000),
    status VARCHAR(64) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    git_retrieval_state VARCHAR(64),
    git_retrieval_error_code VARCHAR(128),
    git_retrieved_text TEXT,
    git_last_success_at TIMESTAMP WITH TIME ZONE,
    git_last_attempt_at TIMESTAMP WITH TIME ZONE,
    git_fetch_version VARCHAR(64),
    CONSTRAINT uq_submissions_task_intern UNIQUE (task_id, intern_user_id),
    CONSTRAINT fk_submissions_task FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
    CONSTRAINT fk_submissions_intern FOREIGN KEY (intern_user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_submissions_task_id ON submissions (task_id);
CREATE INDEX ix_submissions_intern_user_id ON submissions (intern_user_id);

-- changeset examinai:008-model-invocations dbms:postgresql
CREATE TABLE model_invocations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID NOT NULL,
    invoked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    model_name VARCHAR(200) NOT NULL,
    model_version VARCHAR(200),
    prompt_hash VARCHAR(64) NOT NULL,
    CONSTRAINT fk_model_invocations_submission FOREIGN KEY (submission_id) REFERENCES submissions (id) ON DELETE CASCADE
);

CREATE INDEX ix_model_invocations_submission_invoked ON model_invocations (submission_id, invoked_at);

-- changeset examinai:009-ai-drafts dbms:postgresql
CREATE TABLE ai_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_invocation_id UUID NOT NULL UNIQUE,
    assessment_text TEXT NOT NULL,
    CONSTRAINT fk_ai_drafts_invocation FOREIGN KEY (model_invocation_id) REFERENCES model_invocations (id) ON DELETE CASCADE
);

-- changeset examinai:010-mentor-review-drafts dbms:postgresql
CREATE TABLE mentor_review_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID NOT NULL UNIQUE,
    quality_score INTEGER,
    readability_score INTEGER,
    correctness_score INTEGER,
    narrative_feedback TEXT,
    mentor_user_id UUID NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_mentor_review_drafts_submission FOREIGN KEY (submission_id) REFERENCES submissions (id) ON DELETE CASCADE,
    CONSTRAINT fk_mentor_review_drafts_mentor FOREIGN KEY (mentor_user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- changeset examinai:011-published-reviews dbms:postgresql
CREATE TABLE published_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID NOT NULL UNIQUE,
    quality_score INTEGER,
    readability_score INTEGER,
    correctness_score INTEGER,
    narrative TEXT,
    publishing_mentor_user_id UUID NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    snapshot_commit_sha VARCHAR(64),
    snapshot_git_fetch_version VARCHAR(64),
    snapshot_path_scope VARCHAR(2000),
    CONSTRAINT fk_published_reviews_submission FOREIGN KEY (submission_id) REFERENCES submissions (id) ON DELETE CASCADE,
    CONSTRAINT fk_published_reviews_mentor FOREIGN KEY (publishing_mentor_user_id) REFERENCES users (id) ON DELETE CASCADE
);
