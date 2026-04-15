# Python app only — no JVM. Liquibase runs as a Compose one-shot service (see docker-compose.yml).
FROM python:3.12-slim-bookworm

RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

COPY pyproject.toml README-Python.md ./
COPY src ./src
COPY db ./db
COPY scripts/docker-entrypoint.sh ./scripts/docker-entrypoint.sh

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir . \
    && chmod +x scripts/docker-entrypoint.sh \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

ENV EXAMINAI_LIQUIBASE_CHANGELOG=/app/db/changelog/db.changelog-master.xml

ENTRYPOINT ["./scripts/docker-entrypoint.sh"]
