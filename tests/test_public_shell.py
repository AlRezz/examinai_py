"""Public HTML routes and static mounts (Story 1-1)."""

from fastapi.testclient import TestClient

from examai.main import app

client = TestClient(app)


def test_public_pages_return_html() -> None:
    for path in ("/", "/login", "/error"):
        r = client.get(path)
        assert r.status_code == 200, path
        assert "text/html" in r.headers.get("content-type", ""), path


def test_error_accepts_optional_message_query() -> None:
    r = client.get("/error", params={"message": "Custom"})
    assert r.status_code == 200
    assert "Custom" in r.text


def test_static_theme_css() -> None:
    r = client.get("/css/examai-theme.css")
    assert r.status_code == 200
    assert "text/css" in r.headers.get("content-type", "")


def test_webjar_bootstrap_css() -> None:
    r = client.get("/webjars/bootstrap/5.3.3/css/bootstrap.min.css")
    assert r.status_code == 200
    assert "text/css" in r.headers.get("content-type", "")


def test_js_welcome_init() -> None:
    r = client.get("/js/welcome-jqui-init.js")
    assert r.status_code == 200
    assert "javascript" in r.headers.get("content-type", "").lower()
