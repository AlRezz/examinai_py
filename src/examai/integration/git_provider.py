"""Git provider HTTP client (GitHub REST v3–compatible) — FR31, docs/architecture.md."""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlparse

import httpx


@dataclass(frozen=True)
class GitFetchResult:
    """Outcome of a single contents fetch."""

    ok: bool
    normalized_text: str | None = None
    error_code: str | None = None


def parse_repo_identifier(raw: str) -> tuple[str, str]:
    """
    Resolve owner and repo from `repo_identifier` (owner/repo, https://github.com/..., or git@github.com:...).
    """
    s = raw.strip()
    if not s:
        raise ValueError("Repository identifier is empty.")

    if s.startswith("git@"):
        _, _, tail = s.partition(":")
        tail = tail.strip()
        if not tail:
            raise ValueError("Invalid git SSH URL.")
        tail = re.sub(r"\.git$", "", tail)
        parts = [p for p in tail.split("/") if p]
        if len(parts) < 2:
            raise ValueError("Invalid git SSH URL (expected host:owner/repo).")
        return parts[0], parts[1]

    if "://" in s or re.match(r"(?i)^github\.com/", s):
        url = s if "://" in s else f"https://{s}"
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower()
        if "github.com" not in host and not host.endswith(".github.com"):
            raise ValueError("Only github.com repository URLs are supported.")
        path = parsed.path.strip("/")
        parts = [p for p in path.split("/") if p]
        if len(parts) < 2:
            raise ValueError("Repository URL must include owner and repo.")
        return parts[0], re.sub(r"\.git$", "", parts[1])

    parts = [p for p in s.split("/") if p]
    if len(parts) < 2:
        raise ValueError("Repository must look like owner/repo.")
    return parts[0], re.sub(r"\.git$", "", parts[1])


def _contents_path_for_scope(path_scope: str | None) -> str:
    if not path_scope or not str(path_scope).strip():
        return ""
    p = str(path_scope).strip().lstrip("/")
    return p


def _decode_file_payload(payload: dict[str, Any]) -> str:
    enc = (payload.get("encoding") or "").lower()
    raw = payload.get("content")
    if enc == "base64" and isinstance(raw, str):
        cleaned = "".join(raw.splitlines())
        try:
            data = base64.b64decode(cleaned)
        except Exception:
            return "(unable to decode file content)"
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("utf-8", errors="replace")
    if isinstance(raw, str) and not enc:
        return raw
    return repr(payload)[:2000]


def _format_dir_listing(items: list[dict[str, Any]], *, max_rows: int = 500) -> str:
    lines: list[str] = []
    for it in items[:max_rows]:
        name = it.get("name", "?")
        typ = it.get("type", "?")
        lines.append(f"{typ}\t{name}")
    if len(items) > max_rows:
        lines.append(f"... ({len(items) - max_rows} more entries omitted)")
    return "\n".join(lines) if lines else "(empty directory)"


def fetch_repository_contents(
    *,
    api_base: str,
    token: str,
    owner: str,
    repo: str,
    ref: str,
    path_scope: str | None,
    timeout_seconds: float,
    max_text_chars: int = 120_000,
) -> GitFetchResult:
    """
    GET /repos/{owner}/{repo}/contents/{path}?ref={ref} (GitHub REST v3).
    """
    root = api_base.rstrip("/")
    rel = _contents_path_for_scope(path_scope)
    path_enc = "/".join(quote(seg, safe="") for seg in rel.split("/")) if rel else ""
    url = f"{root}/repos/{quote(owner, safe='')}/{quote(repo, safe='')}/contents"
    if path_enc:
        url = f"{url}/{path_enc}"

    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    t = token.strip()
    if t:
        headers["Authorization"] = f"Bearer {t}"

    timeout = httpx.Timeout(timeout_seconds, connect=min(10.0, timeout_seconds))
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            r = client.get(url, headers=headers, params={"ref": ref.strip()})
    except (httpx.TransportError, httpx.TimeoutException) as e:
        return GitFetchResult(ok=False, error_code=f"TRANSPORT_{type(e).__name__.upper()}")

    if r.status_code == 200:
        try:
            data = r.json()
        except Exception:
            return GitFetchResult(ok=False, error_code="INVALID_JSON")

        text: str
        if isinstance(data, list):
            text = _format_dir_listing(data)
        elif isinstance(data, dict):
            typ = data.get("type")
            if typ == "file":
                text = _decode_file_payload(data)
            else:
                text = f"(unsupported Git contents entry type: {typ!r})"
        else:
            text = str(data)

        if len(text) > max_text_chars:
            text = text[: max_text_chars - 1] + "…"
        return GitFetchResult(ok=True, normalized_text=text)

    if r.status_code in (401, 403):
        return GitFetchResult(ok=False, error_code="AUTH_DENIED")
    if r.status_code == 404:
        return GitFetchResult(ok=False, error_code="NOT_FOUND")
    if r.status_code == 429:
        return GitFetchResult(ok=False, error_code="RATE_LIMIT")
    return GitFetchResult(ok=False, error_code=f"HTTP_{r.status_code}")
