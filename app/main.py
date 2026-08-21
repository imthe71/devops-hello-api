from __future__ import annotations

import os
import socket

from fastapi import FastAPI

app = FastAPI(title="Hello DevOps API", version="1.0.0")


def app_version() -> str:
    return os.getenv("APP_VERSION", "dev")


@app.get("/", tags=["application"])
def root() -> dict[str, str]:
    return {
        "message": "Hello DevOps",
        "version": app_version(),
        "hostname": socket.gethostname(),
    }


@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
def readyz() -> dict[str, str]:
    return {"status": "ready"}
