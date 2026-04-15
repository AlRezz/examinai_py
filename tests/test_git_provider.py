"""Unit tests for Git provider integration (parse, commit-first fetch, fallbacks)."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import patch

import httpx
import pytest

from examai.integration.git_provider import fetch_repository_contents, parse_repo_identifier

# Preserve real Client; patched `examai.integration.git_provider.httpx.Client` must not recurse here.
_RealHttpxClient = httpx.Client


@pytest.mark.parametrize(
    "raw,owner,repo",
    [
        ("org/repo", "org", "repo"),
        ("org/repo.git", "org", "repo"),
        ("https://github.com/foo/bar", "foo", "bar"),
        ("https://github.com/foo/bar.git", "foo", "bar"),
        ("git@github.com:foo/bar.git", "foo", "bar"),
        ("github.com/zed/app", "zed", "app"),
    ],
)
def test_parse_repo_identifier_accepts_common_forms(raw: str, owner: str, repo: str) -> None:
    o, r = parse_repo_identifier(raw)
    assert o == owner
    assert r == repo


def test_parse_repo_identifier_rejects_empty() -> None:
    with pytest.raises(ValueError, match="empty"):
        parse_repo_identifier("   ")


def test_parse_repo_identifier_rejects_single_segment() -> None:
    with pytest.raises(ValueError):
        parse_repo_identifier("onlyone")


def test_fetch_empty_path_scope_uses_commit_all_files() -> None:
    """Empty path_scope: GET /commits/{ref} and concatenate every ``files[]`` row."""

    def handler(request: httpx.Request) -> httpx.Response:
        u = str(request.url)
        assert "/repos/o/r/commits/main" in u
        if "/commits/" in u:
            return httpx.Response(
                200,
                json={
                    "files": [
                        {"filename": "README.md", "patch": "diff --git a/README.md\n+hello\n"},
                        {"filename": "src/a.py", "patch": "diff --git a/src/a.py\n+code\n"},
                    ]
                },
            )
        return httpx.Response(404)

    with patch("examai.integration.git_provider.httpx.Client", _client_with_mock(handler)):
        r = fetch_repository_contents(
            api_base="https://api.github.com",
            token="",
            owner="o",
            repo="r",
            ref="main",
            path_scope="",
            timeout_seconds=30.0,
        )

    assert r.ok
    assert r.normalized_text
    assert r.source_kind == "patch"
    assert "README.md" in r.normalized_text
    assert "src/a.py" in r.normalized_text


def test_fetch_empty_path_scope_falls_back_to_contents_when_commit_has_no_usable_files() -> None:
    """If the commit has no resolvable file text, GET /contents?ref= at repository root."""

    def handler(request: httpx.Request) -> httpx.Response:
        u = str(request.url)
        if "/commits/" in u:
            return httpx.Response(200, json={"files": []})
        if u.rstrip("/").endswith("/repos/o/r/contents") or "/repos/o/r/contents?" in u:
            return httpx.Response(
                200,
                json=[{"name": "README.md", "type": "file"}, {"name": "src", "type": "dir"}],
            )
        return httpx.Response(404)

    with patch("examai.integration.git_provider.httpx.Client", _client_with_mock(handler)):
        r = fetch_repository_contents(
            api_base="https://api.github.com",
            token="",
            owner="o",
            repo="r",
            ref="main",
            path_scope="",
            timeout_seconds=30.0,
        )

    assert r.ok
    assert r.normalized_text
    assert r.source_kind == "contents_api_listing"
    assert "README.md" in r.normalized_text
    assert "dir" in r.normalized_text


def _client_with_mock(handler: Callable[[httpx.Request], httpx.Response]) -> type:
    transport = httpx.MockTransport(handler)

    def _factory(*args: object, **kwargs: object) -> httpx.Client:
        k = dict(kwargs)
        k["transport"] = transport
        return _RealHttpxClient(*args, **k)

    return _factory


def test_fetch_prefers_patch_from_commit_files() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        u = str(request.url)
        if u.endswith("/commits/abc123") or "/commits/abc123" in u:
            return httpx.Response(
                200,
                json={
                    "files": [
                        {
                            "filename": "src/a.py",
                            "patch": "diff --git a/src/a.py\n+hello\n",
                        }
                    ]
                },
            )
        return httpx.Response(404, json={"message": "unexpected"})

    with patch("examai.integration.git_provider.httpx.Client", _client_with_mock(handler)):
        r = fetch_repository_contents(
            api_base="https://api.github.com",
            token="",
            owner="org",
            repo="repo",
            ref="abc123",
            path_scope="src/a.py",
            timeout_seconds=30.0,
        )

    assert r.ok
    assert r.normalized_text
    assert r.source_kind == "patch"
    assert "diff --git" in r.normalized_text


def test_fetch_falls_back_to_contents_when_not_in_commit_files() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        u = str(request.url)
        if "/commits/" in u:
            return httpx.Response(200, json={"files": []})
        if "/contents/legacy.py" in u:
            return httpx.Response(
                200,
                json={
                    "type": "file",
                    "encoding": "base64",
                    "content": "SGVsbG8=\n",
                },
            )
        return httpx.Response(404)

    with patch("examai.integration.git_provider.httpx.Client", _client_with_mock(handler)):
        r = fetch_repository_contents(
            api_base="https://api.github.com",
            token="",
            owner="org",
            repo="repo",
            ref="abc123",
            path_scope="legacy.py",
            timeout_seconds=30.0,
        )

    assert r.ok
    assert r.normalized_text == "Hello"
    assert r.source_kind == "contents_api_file"


def test_fetch_single_file_commit_uses_files_zero_patch_github_api_shape() -> None:
    """Commit response ``files`` array: first entry’s ``patch`` (``files[0].patch``) — real GitHub JSON shape."""

    def handler(request: httpx.Request) -> httpx.Response:
        u = str(request.url)
        if "/commits/" in u:
            return httpx.Response(
                200,
                json={
                    "sha": "e541b4093062c63a958769f1dab89ad02cf3224d",
                    "files": [
                        {
                            "sha": "b5a75a2c909a4e75a0fb47764b558644e41c91ac",
                            "filename": "src/main/java/org/example/Main.java",
                            "status": "added",
                            "patch": "@@ -0,0 +1,16 @@\n+package org.example;\n",
                        }
                    ],
                },
            )
        return httpx.Response(404)

    with patch("examai.integration.git_provider.httpx.Client", _client_with_mock(handler)):
        r = fetch_repository_contents(
            api_base="https://api.github.com",
            token="",
            owner="AlRezz",
            repo="TestFibonacci",
            ref="e541b4093062c63a958769f1dab89ad02cf3224d",
            path_scope="src/main/java/org/example/Main.java",
            timeout_seconds=30.0,
        )

    assert r.ok
    assert r.source_kind == "patch"
    assert r.normalized_text
    assert "package org.example" in (r.normalized_text or "")


def test_fetch_single_file_commit_still_resolves_patch_when_scope_does_not_match() -> None:
    """GitHub init commit: one file; path scope typo still picks ``files[0]`` and ``patch``."""

    def handler(request: httpx.Request) -> httpx.Response:
        u = str(request.url)
        if "/commits/" in u:
            return httpx.Response(
                200,
                json={
                    "files": [
                        {
                            "filename": "src/main/java/org/example/Main.java",
                            "patch": "@@ -0,0 +1,2 @@\n+ok\n",
                        }
                    ]
                },
            )
        return httpx.Response(404)

    with patch("examai.integration.git_provider.httpx.Client", _client_with_mock(handler)):
        r = fetch_repository_contents(
            api_base="https://api.github.com",
            token="",
            owner="org",
            repo="repo",
            ref="e541b4",
            path_scope="does/not/match/anything.java",
            timeout_seconds=30.0,
        )

    assert r.ok
    assert r.source_kind == "patch"
    assert "@@ -0,0 +1,2 @@" in (r.normalized_text or "")


def test_fetch_directory_scope_with_trailing_slash_resolves_patch() -> None:
    """Path scope ``src/`` must normalize like ``src`` so prefix match finds ``files[].patch``."""

    def handler(request: httpx.Request) -> httpx.Response:
        u = str(request.url)
        if "/commits/" in u:
            return httpx.Response(
                200,
                json={
                    "files": [
                        {
                            "filename": "src/App.java",
                            "patch": "trailing-slash-scope\n",
                        }
                    ]
                },
            )
        return httpx.Response(404)

    with patch("examai.integration.git_provider.httpx.Client", _client_with_mock(handler)):
        r = fetch_repository_contents(
            api_base="https://api.github.com",
            token="",
            owner="org",
            repo="repo",
            ref="abc",
            path_scope="src/",
            timeout_seconds=30.0,
        )

    assert r.ok
    assert r.source_kind == "patch"
    assert "trailing-slash-scope" in (r.normalized_text or "")


def test_fetch_directory_scope_resolves_nested_file_patch() -> None:
    """Path scope ``src`` must match ``src/main/java/...`` and return ``files[].patch``, not a dir listing."""

    def handler(request: httpx.Request) -> httpx.Response:
        u = str(request.url)
        if "/commits/" in u:
            return httpx.Response(
                200,
                json={
                    "files": [
                        {
                            "filename": "src/main/java/org/example/Main.java",
                            "patch": "@@ -0,0 +1,2 @@\n+package org.example;\n",
                        }
                    ]
                },
            )
        return httpx.Response(404, json={"message": "should not GET contents for src dir"})

    with patch("examai.integration.git_provider.httpx.Client", _client_with_mock(handler)):
        r = fetch_repository_contents(
            api_base="https://api.github.com",
            token="",
            owner="org",
            repo="repo",
            ref="e541b4093062c63a958769f1dab89ad02cf3224d",
            path_scope="src",
            timeout_seconds=30.0,
        )

    assert r.ok
    assert r.source_kind == "patch"
    assert r.normalized_text
    assert "@@ -0,0 +1,2 @@" in (r.normalized_text or "")
    assert "dir" not in (r.normalized_text or "").lower()


def test_fetch_matches_unique_basename() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if "/commits/" in str(request.url):
            return httpx.Response(
                200,
                json={
                    "files": [
                        {
                            "filename": "src/main/java/org/example/Main.java",
                            "patch": "diff --git\n",
                        }
                    ]
                },
            )
        return httpx.Response(404)

    with patch("examai.integration.git_provider.httpx.Client", _client_with_mock(handler)):
        r = fetch_repository_contents(
            api_base="https://api.github.com",
            token="",
            owner="org",
            repo="repo",
            ref="abc",
            path_scope="Main.java",
            timeout_seconds=30.0,
        )

    assert r.ok
    assert r.source_kind == "patch"


def test_fetch_commit_404() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"message": "Not Found"})

    with patch("examai.integration.git_provider.httpx.Client", _client_with_mock(handler)):
        r = fetch_repository_contents(
            api_base="https://api.github.com",
            token="",
            owner="org",
            repo="repo",
            ref="badref",
            path_scope="x.py",
            timeout_seconds=30.0,
        )

    assert not r.ok
    assert r.error_code == "NOT_FOUND"
