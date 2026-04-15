-- Runs once on empty Postgres data dir (see db/init/README.md).
-- Application schema is applied by Liquibase from the app container.
SELECT 1 AS docker_entrypoint_initdb_ready;
