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


def test_config_status_reports_environment_without_leaking_value(monkeypatch) -> None:
    monkeypatch.delenv("APP_SECRETS_DIR", raising=False)
    monkeypatch.setenv("APP_DEMO_TOKEN", "never-return-this-value")

    response = client.get("/config-status")

    assert response.status_code == 200
    assert response.json()["runtimeParameters"]["APP_DEMO_TOKEN"] == {
        "configured": True,
        "source": "environment",
    }
    assert "never-return-this-value" not in response.text


def test_config_status_prefers_csi_file_over_environment(tmp_path, monkeypatch) -> None:
    (tmp_path / "APP_DEMO_TOKEN").write_text("mounted-value", encoding="utf-8")
    monkeypatch.setenv("APP_SECRETS_DIR", str(tmp_path))
    monkeypatch.setenv("APP_DEMO_TOKEN", "environment-value")

    response = client.get("/config-status")

    assert response.status_code == 200
    assert response.json()["runtimeParameters"]["APP_DEMO_TOKEN"] == {
        "configured": True,
        "source": "file",
    }
    assert "mounted-value" not in response.text
    assert "environment-value" not in response.text
