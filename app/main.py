from __future__ import annotations

import os
import socket
from pathlib import Path

from fastapi import FastAPI

app = FastAPI(title="Hello DevOps API", version="1.0.0")


def app_version() -> str:
    return os.getenv("APP_VERSION", "dev")


def runtime_token_status() -> dict[str, bool | str]:
    """Report configuration presence without ever returning the secret value."""
    secrets_dir = os.getenv("APP_SECRETS_DIR")
    if secrets_dir:
        token_file = Path(secrets_dir) / "APP_DEMO_TOKEN"
        try:
            if token_file.read_text(encoding="utf-8").strip():
                return {"configured": True, "source": "file"}
        except OSError:
            pass

    if os.getenv("APP_DEMO_TOKEN"):
        return {"configured": True, "source": "environment"}

    return {"configured": False, "source": "not_configured"}


@app.get("/", tags=["application"])
def root() -> dict[str, str]:
    return {
        "message": "Hello DevOps",
        "version": app_version(),
        "hostname": socket.gethostname(),
    }


@app.get("/config-status", tags=["application"])
def config_status() -> dict[str, object]:
    return {
        "status": "ok",
        "version": app_version(),
        "runtimeParameters": {
            "APP_DEMO_TOKEN": runtime_token_status(),
        },
    }


@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
def readyz() -> dict[str, str]:
    return {"status": "ready"}
