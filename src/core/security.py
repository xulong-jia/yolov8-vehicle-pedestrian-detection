"""Minimal API key security helpers for FastAPI."""

from __future__ import annotations

import os


API_KEY_HEADER = "X-API-Key"
PUBLIC_PATHS = {
    "/health",
    "/model-status",
    "/config",
    "/docs",
    "/openapi.json",
    "/redoc",
}


def is_api_key_auth_enabled() -> bool:
    return os.environ.get("API_KEY_AUTH_ENABLED", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def get_expected_api_key() -> str:
    return os.environ.get("API_KEY", "")


def is_public_path(path: str) -> bool:
    return path in PUBLIC_PATHS or path.startswith("/docs/")


def api_key_is_valid(provided_key: str | None) -> bool:
    expected_key = get_expected_api_key()
    return bool(expected_key) and provided_key == expected_key
