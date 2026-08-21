from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_has_version_and_hostname() -> None:
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "Hello DevOps"
    assert "version" in payload
    assert "hostname" in payload


def test_health_endpoints() -> None:
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/readyz").json() == {"status": "ready"}
