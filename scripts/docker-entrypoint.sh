#!/bin/sh
set -eu

if [ "${EXAMINAI_USE_LIQUIBASE:-}" = "1" ] || [ "${EXAMINAI_USE_LIQUIBASE:-}" = "true" ]; then
  python -m examai.liquibase_cli
fi

exec uvicorn examai.main:app --host 0.0.0.0 --port 8080
