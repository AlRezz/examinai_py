"""Run Liquibase update for PostgreSQL when EXAMINAI_USE_LIQUIBASE is enabled.

Docker Compose normally runs migrations via the db-migrate service (Liquibase image).
Use this module when the liquibase CLI is on PATH (local dev or CI).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy.engine.url import make_url


def _truthy(name: str) -> bool:
    v = (os.environ.get(name) or "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _default_changelog_path() -> Path:
    override = (os.environ.get("EXAMINAI_LIQUIBASE_CHANGELOG") or "").strip()
    if override:
        return Path(override)
    docker = Path("/app/db/changelog/db.changelog-master.xml")
    if docker.exists():
        return docker
    # Development: repo root is three levels above this package file (src/examai/liquibase_cli.py)
    return Path(__file__).resolve().parent.parent.parent / "db/changelog/db.changelog-master.xml"


def main() -> int:
    if not _truthy("EXAMINAI_USE_LIQUIBASE"):
        return 0

    raw = (os.environ.get("EXAMINAI_DATABASE_URL") or "").strip()
    if not raw.startswith("postgresql"):
        print(
            "EXAMINAI_USE_LIQUIBASE is set but EXAMINAI_DATABASE_URL is not a PostgreSQL URL; "
            "skipping Liquibase.",
            file=sys.stderr,
        )
        return 1

    u = make_url(raw)
    host = u.host or "localhost"
    port = u.port or 5432
    db = u.database or ""
    user = u.username or ""
    password = u.password or ""

    changelog = _default_changelog_path()
    if not changelog.is_file():
        print(f"Liquibase changelog not found: {changelog}", file=sys.stderr)
        return 1

    jdbc = f"jdbc:postgresql://{host}:{port}/{db}"

    env = os.environ.copy()
    if password:
        env["LIQUIBASE_COMMAND_PASSWORD"] = password

    cmd = [
        "liquibase",
        f"--changelog-file={changelog}",
        f"--url={jdbc}",
        f"--username={user}",
        "update",
    ]

    print("Running Liquibase update…", file=sys.stderr)
    try:
        subprocess.run(cmd, env=env, check=True)
    except FileNotFoundError:
        print("Liquibase executable not found on PATH.", file=sys.stderr)
        return 127
    except subprocess.CalledProcessError as e:
        print(
            "Liquibase update failed; fix migrations or database state before starting the app.",
            file=sys.stderr,
        )
        return e.returncode or 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
