from __future__ import annotations

import os
import socket
from pathlib import Path

import psycopg
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from psycopg.rows import dict_row

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


def database_settings() -> dict[str, str] | None:
    """Read database connectivity settings without exposing the password."""
    names = {
        "host": "DATABASE_HOST",
        "port": "DATABASE_PORT",
        "dbname": "DATABASE_NAME",
        "user": "DATABASE_USER",
        "password": "DATABASE_PASSWORD",
    }
    settings = {key: os.getenv(env_name, "") for key, env_name in names.items()}
    return settings if all(settings.values()) else None


def database_configuration_status() -> dict[str, bool | str]:
    settings = database_settings()
    return {
        "configured": settings is not None,
        "source": "environment" if settings else "not_configured",
    }


def connect_database() -> psycopg.Connection:
    settings = database_settings()
    if settings is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database_not_configured",
        )

    try:
        return psycopg.connect(connect_timeout=2, **settings)
    except psycopg.Error as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database_unavailable",
        ) from error


def initialize_notes_table(connection: psycopg.Connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS demo_notes (
                id BIGSERIAL PRIMARY KEY,
                content TEXT NOT NULL CHECK (char_length(content) <= 500),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )


def database_runtime_status() -> dict[str, bool | str]:
    settings = database_settings()
    if settings is None:
        return {"configured": False, "reachable": False, "source": "not_configured"}

    try:
        with psycopg.connect(connect_timeout=2, **settings) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        return {"configured": True, "reachable": True, "source": "environment"}
    except psycopg.Error:
        return {"configured": True, "reachable": False, "source": "environment"}


class NoteCreate(BaseModel):
    content: str = Field(min_length=1, max_length=500)


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
        "database": database_configuration_status(),
    }


@app.get("/db-status", tags=["database"])
def db_status() -> dict[str, bool | str]:
    """Return connection state only; never return database credentials."""
    return database_runtime_status()


@app.get("/notes", tags=["database"])
def list_notes() -> dict[str, list[dict[str, object]]]:
    with connect_database() as connection:
        initialize_notes_table(connection)
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT id, content, created_at FROM demo_notes ORDER BY id ASC"
            )
            return {"items": list(cursor.fetchall())}


@app.post("/notes", status_code=status.HTTP_201_CREATED, tags=["database"])
def create_note(note: NoteCreate) -> dict[str, object]:
    with connect_database() as connection:
        initialize_notes_table(connection)
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO demo_notes (content)
                VALUES (%s)
                RETURNING id, content, created_at
                """,
                (note.content,),
            )
            return cursor.fetchone()


@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
def readyz() -> dict[str, str]:
    database = database_runtime_status()
    if database["configured"] and not database["reachable"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database_unavailable",
        )
    return {"status": "ready"}
