# Python app + Liquibase (Java runtime for CLI only). Uvicorn on 8080 — docs/deployment-guide.md
FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends openjdk-17-jre-headless unzip curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL -o /tmp/lb.zip https://github.com/liquibase/liquibase/releases/download/v4.29.2/liquibase-4.29.2.zip \
    && unzip -q /tmp/lb.zip -d /opt \
    && mv /opt/liquibase-4.29.2 /opt/liquibase \
    && rm /tmp/lb.zip \
    && chmod +x /opt/liquibase/liquibase

ENV PATH="/opt/liquibase:${PATH}"

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
