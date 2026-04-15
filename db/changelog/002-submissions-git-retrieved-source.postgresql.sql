-- liquibase formatted sql

-- changeset examinai:012-submissions-git-retrieved-source dbms:postgresql
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS git_retrieved_source VARCHAR(32);
