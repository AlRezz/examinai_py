"""Unit tests for Git provider integration (parse + URL building)."""

from __future__ import annotations

import pytest

from examai.integration.git_provider import parse_repo_identifier


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
