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
    #: When ``ok``: ``patch`` | ``raw_url`` | ``contents_url`` | ``contents_api_file`` | ``contents_api_listing``.
    source_kind: str | None = None


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
    # Trailing slash breaks directory-prefix match (``src/`` + ``/`` ≠ ``src/main/...``).
    p = str(path_scope).strip().lstrip("/").rstrip("/")
    return p


def _github_headers(token: str) -> dict[str, str]:
    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    t = token.strip()
    if t:
        headers["Authorization"] = f"Bearer {t}"
    return headers


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


def _http_error_result(status_code: int) -> GitFetchResult:
    if status_code in (401, 403):
        return GitFetchResult(ok=False, error_code="AUTH_DENIED")
    if status_code == 404:
        return GitFetchResult(ok=False, error_code="NOT_FOUND")
    if status_code == 429:
        return GitFetchResult(ok=False, error_code="RATE_LIMIT")
    return GitFetchResult(ok=False, error_code=f"HTTP_{status_code}")


def _response_text(r: httpx.Response) -> str:
    r.encoding = r.encoding or "utf-8"
    return r.text


def _normalize_repo_path(p: str) -> str:
    return p.strip().replace("\\", "/").lstrip("/")


def _path_matches_scope(filename: str, want: str) -> bool:
    """True if GitHub ``filename`` refers to the same path as ``want`` (path scope)."""
    fn = _normalize_repo_path(filename)
    w = _normalize_repo_path(want)
    if not w:
        return False
    if fn == w:
        return True
    if fn.endswith("/" + w):
        return True
    if len(fn) > len(w) and fn.endswith(w) and fn[-len(w) - 1] == "/":
        return True
    return False


def _file_is_under_directory_scope(filename: str, dir_scope: str) -> bool:
    """True when ``filename`` is exactly ``dir_scope`` or lives under it (``dir_scope/...``)."""
    fn = _normalize_repo_path(filename)
    w = _normalize_repo_path(dir_scope)
    if not w or not fn:
        return False
    if fn == w:
        return True
    return fn.startswith(w + "/")


def _find_commit_file_entries(files: list[Any], want_path: str) -> list[dict[str, Any]]:
    """
    Match ``files[]`` to path scope: exact rules, basename, single-file commit, then directory prefix.

    When ``want_path`` is a folder (e.g. ``src``), every ``filename`` under that path matches
    (e.g. ``src/main/java/...``). Multiple matches return multiple rows (patches concatenated by caller).
    """
    w = _normalize_repo_path(want_path)
    if not w:
        return []

    dict_rows: list[dict[str, Any]] = [x for x in files if isinstance(x, dict)]
    if not dict_rows:
        return []

    for item in dict_rows:
        fn = _normalize_repo_path(item.get("filename") or "")
        if fn and _path_matches_scope(fn, w):
            return [item]

    want_base = w.split("/")[-1]
    if want_base:
        basename_hits = [
            item
            for item in dict_rows
            if _normalize_repo_path(item.get("filename") or "").split("/")[-1] == want_base
        ]
        if len(basename_hits) == 1:
            return basename_hits

    if len(dict_rows) == 1:
        # Single-file commit (e.g. init): GitHub ``files`` has one row — use ``files[0]`` for ``.patch`` / fallbacks.
        return [dict_rows[0]]

    prefix_hits = [
        item
        for item in dict_rows
        if _file_is_under_directory_scope(_normalize_repo_path(item.get("filename") or ""), w)
    ]
    prefix_hits.sort(key=lambda it: _normalize_repo_path(it.get("filename") or ""))
    if prefix_hits:
        return prefix_hits

    return []


def _try_text_from_commit_file_entry(
    client: httpx.Client,
    token: str,
    entry: dict[str, Any],
) -> tuple[str, str] | None:
    """Resolve text from one commit ``files[i]`` row (often ``files[0]``): patch → raw_url → contents_url."""
    patch = entry.get("patch")
    if isinstance(patch, str) and patch.strip():
        return (patch, "patch")

    headers = _github_headers(token)
    raw_url = entry.get("raw_url")
    if isinstance(raw_url, str) and raw_url.strip():
        try:
            rr = client.get(raw_url.strip(), headers=headers)
            if rr.status_code == 200:
                return (_response_text(rr), "raw_url")
        except (httpx.TransportError, httpx.TimeoutException):
            pass

    contents_url = entry.get("contents_url")
    if isinstance(contents_url, str) and contents_url.strip():
        try:
            cr = client.get(contents_url.strip(), headers=headers)
            if cr.status_code != 200:
                return None
            try:
                data = cr.json()
            except Exception:
                return None
            if isinstance(data, dict) and data.get("type") == "file":
                return (_decode_file_payload(data), "contents_url")
        except (httpx.TransportError, httpx.TimeoutException):
            return None

    return None


def _try_text_from_commit_file_entries(
    client: httpx.Client,
    token: str,
    entries: list[dict[str, Any]],
) -> tuple[str, str] | None:
    """Resolve text for one or more ``files[]`` rows (concatenate when multiple)."""
    if not entries:
        return None
    if len(entries) == 1:
        return _try_text_from_commit_file_entry(client, token, entries[0])

    parts: list[str] = []
    kinds: list[str] = []
    for entry in entries:
        got = _try_text_from_commit_file_entry(client, token, entry)
        if got is None:
            return None
        text, kind = got
        fname = _normalize_repo_path(entry.get("filename") or "?")
        parts.append(f"=== {fname} ===\n{text}")
        kinds.append(kind)

    combined = "\n\n".join(parts)
    uniq = set(kinds)
    if len(uniq) == 1:
        source_kind = kinds[0]
    elif "patch" in kinds:
        source_kind = "patch"
    else:
        source_kind = kinds[0]
    return (combined, source_kind)


def _fetch_via_contents_api(
    client: httpx.Client,
    *,
    api_base: str,
    owner: str,
    repo: str,
    ref: str,
    rel_path: str,
    max_text_chars: int,
    headers: dict[str, str],
) -> GitFetchResult:
    """GET /repos/{owner}/{repo}/contents/{path}?ref={ref}."""
    root = api_base.rstrip("/")
    path_enc = "/".join(quote(seg, safe="") for seg in rel_path.split("/")) if rel_path else ""
    url = f"{root}/repos/{quote(owner, safe='')}/{quote(repo, safe='')}/contents"
    if path_enc:
        url = f"{url}/{path_enc}"

    try:
        r = client.get(url, headers=headers, params={"ref": ref.strip()})
    except (httpx.TransportError, httpx.TimeoutException) as e:
        return GitFetchResult(ok=False, error_code=f"TRANSPORT_{type(e).__name__.upper()}")

    if r.status_code != 200:
        return _http_error_result(r.status_code)

    try:
        data = r.json()
    except Exception:
        return GitFetchResult(ok=False, error_code="INVALID_JSON")

    text: str
    source_kind: str
    if isinstance(data, list):
        text = _format_dir_listing(data)
        source_kind = "contents_api_listing"
    elif isinstance(data, dict):
        typ = data.get("type")
        if typ == "file":
            text = _decode_file_payload(data)
            source_kind = "contents_api_file"
        else:
            text = f"(unsupported Git contents entry type: {typ!r})"
            source_kind = "contents_api_unsupported"
    else:
        text = str(data)
        source_kind = "contents_api_unsupported"

    if len(text) > max_text_chars:
        text = text[: max_text_chars - 1] + "…"
    return GitFetchResult(ok=True, normalized_text=text, source_kind=source_kind)


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
    Load normalized text for mentor review / AI.

    If ``path_scope`` is empty, only **GET /repos/{owner}/{repo}/contents?ref={ref}** (repository root listing).

    Otherwise: **GET /repos/{owner}/{repo}/commits/{ref}** (``ref`` = commit SHA, branch, or tag), find
    ``path_scope`` in ``files[]`` (``filename``): exact path, unique basename, single-file commit, or any file
    under a **directory** scope (e.g. scope ``src`` matches ``src/main/java/...``). For matched row(s):
    ``patch``, ``raw_url``, ``contents_url``; else **GET .../contents/{path}?ref={ref}**.
    """
    rel = _contents_path_for_scope(path_scope)
    root = api_base.rstrip("/")
    ref_s = ref.strip()
    headers = _github_headers(token)
    commit_url = (
        f"{root}/repos/{quote(owner, safe='')}/{quote(repo, safe='')}/commits/{quote(ref_s, safe='')}"
    )
    timeout = httpx.Timeout(timeout_seconds, connect=min(10.0, timeout_seconds))

    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            if not rel:
                return _fetch_via_contents_api(
                    client,
                    api_base=api_base,
                    owner=owner,
                    repo=repo,
                    ref=ref_s,
                    rel_path="",
                    max_text_chars=max_text_chars,
                    headers=headers,
                )

            try:
                r = client.get(commit_url, headers=headers)
            except (httpx.TransportError, httpx.TimeoutException) as e:
                return GitFetchResult(ok=False, error_code=f"TRANSPORT_{type(e).__name__.upper()}")

            if r.status_code != 200:
                return _http_error_result(r.status_code)

            try:
                payload = r.json()
            except Exception:
                return GitFetchResult(ok=False, error_code="INVALID_JSON")

            raw_files = payload.get("files")
            files: list[Any] = raw_files if isinstance(raw_files, list) else []

            entries = _find_commit_file_entries(files, rel)
            text: str | None = None
            source_kind: str | None = None
            if entries:
                resolved = _try_text_from_commit_file_entries(client, token, entries)
                if resolved is not None:
                    text, source_kind = resolved

            if text is not None:
                if len(text) > max_text_chars:
                    text = text[: max_text_chars - 1] + "…"
                return GitFetchResult(ok=True, normalized_text=text, source_kind=source_kind)

            return _fetch_via_contents_api(
                client,
                api_base=api_base,
                owner=owner,
                repo=repo,
                ref=ref_s,
                rel_path=rel,
                max_text_chars=max_text_chars,
                headers=headers,
            )
    except (httpx.TransportError, httpx.TimeoutException) as e:
        return GitFetchResult(ok=False, error_code=f"TRANSPORT_{type(e).__name__.upper()}")
