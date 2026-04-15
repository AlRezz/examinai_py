from fastapi.testclient import TestClient

from examai.main import app

client = TestClient(app)


def test_actuator_health() -> None:
    r = client.get("/actuator/health")
    assert r.status_code == 200
    assert r.json() == {"status": "UP"}
