from fastapi.testclient import TestClient

from examai.main import app

client = TestClient(app)

_HEALTH_JSON = {"status": "UP"}


def test_actuator_health() -> None:
    r = client.get("/actuator/health")
    assert r.status_code == 200
    assert r.headers.get("content-type", "").startswith("application/json")
    assert r.json() == _HEALTH_JSON


def test_actuator_health_subpaths_match_contract() -> None:
    for path in ("/actuator/health/liveness", "/actuator/health/readiness"):
        r = client.get(path)
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("application/json")
        assert r.json() == _HEALTH_JSON


def test_actuator_health_unauthenticated_ok() -> None:
    """FR4/FR6: health must not require a session (default TestClient has no cookies)."""
    for path in ("/actuator/health", "/actuator/health/liveness"):
        r = client.get(path, headers={})
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("application/json")
        assert r.json() == _HEALTH_JSON
