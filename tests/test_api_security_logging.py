"""Tests for FastAPI API-key auth, request ids, and structured logging."""

from __future__ import annotations

from io import BytesIO
import json
import logging
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image
import pytest


@pytest.fixture(autouse=True)
def isolate_bad_case_service(monkeypatch, tmp_path):
    from src import api
    from src.services.bad_case_service import BadCaseService

    monkeypatch.setattr(
        api,
        "bad_case_service",
        BadCaseService(
            csv_path=tmp_path / "bad_cases.csv",
            jsonl_path=tmp_path / "bad_cases.jsonl",
        ),
    )


def _png_bytes(size: tuple[int, int] = (8, 6)) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", size, color="white").save(buffer, format="PNG")
    return buffer.getvalue()


def _client(monkeypatch, auth_enabled: bool = False) -> TestClient:
    from src.api import create_app

    if auth_enabled:
        monkeypatch.setenv("API_KEY_AUTH_ENABLED", "true")
        monkeypatch.setenv("API_KEY", "test-secret")
    else:
        monkeypatch.delenv("API_KEY_AUTH_ENABLED", raising=False)
        monkeypatch.delenv("API_KEY", raising=False)
    return TestClient(create_app())


def test_api_key_auth_is_disabled_by_default(monkeypatch):
    client = _client(monkeypatch)

    response = client.post(
        "/api/bad-cases",
        json={
            "module": "api",
            "case_type": "default_auth_off",
            "expected_result": "accepted",
            "actual_result": "accepted",
            "root_cause": "smoke",
        },
    )

    assert response.status_code == 200


def test_api_key_auth_rejects_missing_and_wrong_key(monkeypatch):
    client = _client(monkeypatch, auth_enabled=True)
    payload = {
        "module": "api",
        "case_type": "auth",
        "expected_result": "accepted",
        "actual_result": "accepted",
        "root_cause": "smoke",
    }

    missing = client.post("/api/bad-cases", json=payload)
    wrong = client.post("/api/bad-cases", json=payload, headers={"X-API-Key": "wrong"})

    assert missing.status_code == 401
    assert "api key" in missing.json()["detail"].lower()
    assert wrong.status_code == 401
    assert "api key" in wrong.json()["detail"].lower()


def test_api_key_auth_accepts_correct_key(monkeypatch):
    client = _client(monkeypatch, auth_enabled=True)

    response = client.post(
        "/api/bad-cases",
        headers={"X-API-Key": "test-secret"},
        json={
            "module": "api",
            "case_type": "auth_success",
            "expected_result": "accepted",
            "actual_result": "accepted",
            "root_cause": "smoke",
        },
    )

    assert response.status_code == 200
    assert response.json()["case_type"] == "auth_success"


def test_public_endpoints_do_not_require_api_key_when_auth_enabled(monkeypatch):
    client = _client(monkeypatch, auth_enabled=True)

    health = client.get("/health")
    model_status = client.get("/model-status")
    config = client.get("/config")

    assert health.status_code == 200
    assert model_status.status_code == 200
    assert config.status_code == 200


def test_cors_preflight_allows_local_react_origin(monkeypatch):
    client = _client(monkeypatch)

    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Request-ID",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "GET" in response.headers["access-control-allow-methods"]
    allowed_headers = response.headers["access-control-allow-headers"].lower()
    assert "x-request-id" in allowed_headers


def test_cors_preflight_allows_api_headers(monkeypatch):
    client = _client(monkeypatch)

    response = client.options(
        "/api/bad-cases",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-API-Key,X-Request-ID,Content-Type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "POST" in response.headers["access-control-allow-methods"]
    allowed_headers = response.headers["access-control-allow-headers"].lower()
    assert "x-api-key" in allowed_headers
    assert "x-request-id" in allowed_headers
    assert "content-type" in allowed_headers


def test_cors_simple_get_allows_local_react_origin(monkeypatch):
    client = _client(monkeypatch)

    response = client.get("/health", headers={"Origin": "http://localhost:5173"})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_exported_uvicorn_app_has_cors_middleware(monkeypatch):
    from fastapi.testclient import TestClient
    from src import api

    monkeypatch.delenv("API_KEY_AUTH_ENABLED", raising=False)
    monkeypatch.delenv("API_KEY", raising=False)
    client = TestClient(api.app)

    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Request-ID",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_preflight_is_not_blocked_by_api_key_auth(monkeypatch):
    client = _client(monkeypatch, auth_enabled=True)

    response = client.options(
        "/api/bad-cases",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-API-Key,X-Request-ID,Content-Type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    allowed_headers = response.headers["access-control-allow-headers"].lower()
    assert "x-api-key" in allowed_headers
    assert "x-request-id" in allowed_headers


def test_cors_origins_can_be_overridden_by_environment(monkeypatch):
    monkeypatch.setenv("CORS_ALLOW_ORIGINS", "http://localhost:5173,http://example.test")
    client = _client(monkeypatch)

    allowed = client.get("/health", headers={"Origin": "http://example.test"})
    not_allowed = client.get("/health", headers={"Origin": "http://127.0.0.1:8501"})

    assert allowed.headers["access-control-allow-origin"] == "http://example.test"
    assert "access-control-allow-origin" not in not_allowed.headers


def test_request_id_is_generated_and_echoed(monkeypatch):
    client = _client(monkeypatch)

    generated = client.get("/health")
    provided = client.get("/health", headers={"X-Request-ID": "req-fixed-123"})

    assert generated.status_code == 200
    assert generated.headers["X-Request-ID"]
    assert provided.headers["X-Request-ID"] == "req-fixed-123"


def test_request_log_contains_request_id_path_and_status(monkeypatch, caplog):
    client = _client(monkeypatch)
    caplog.set_level(logging.INFO, logger="yolov8.api")

    response = client.get("/health", headers={"X-Request-ID": "req-log-1"})

    assert response.status_code == 200
    entries = [json.loads(record.message) for record in caplog.records]
    request_entries = [entry for entry in entries if entry.get("event") == "http_request"]
    assert request_entries
    assert request_entries[-1]["request_id"] == "req-log-1"
    assert request_entries[-1]["path"] == "/health"
    assert request_entries[-1]["status_code"] == 200
    assert "duration_ms" in request_entries[-1]


def test_video_job_create_log_contains_job_fields(monkeypatch, tmp_path, caplog):
    from src.services.job_store import SQLiteVideoJobStore
    from src.services.video_job_service import registry

    registry.base_output_dir = tmp_path / "api_video_jobs"
    registry.store = SQLiteVideoJobStore(tmp_path / "api_video_jobs" / "video_jobs.sqlite3")
    registry.clear()
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "video_analysis_summary.json").write_text(
        '{"video_id":"log_demo"}',
        encoding="utf-8",
    )
    client = _client(monkeypatch)
    caplog.set_level(logging.INFO, logger="yolov8.api")

    response = client.post(
        "/api/videos/analyze",
        headers={"X-Request-ID": "req-job-log"},
        json={"video_id": "log_demo", "run_name": "log_run", "run_dir": str(run_dir)},
    )

    assert response.status_code == 200
    job_id = response.json()["job_id"]
    entries = [json.loads(record.message) for record in caplog.records]
    job_entries = [entry for entry in entries if entry.get("event") == "video_job_created"]
    assert job_entries
    assert job_entries[-1]["job_id"] == job_id
    assert job_entries[-1]["request_id"] == "req-job-log"
    assert job_entries[-1]["video_id"] == "log_demo"
    assert job_entries[-1]["run_name"] == "log_run"
    assert job_entries[-1]["status"] == "attached"


def test_predict_requires_api_key_when_auth_enabled(monkeypatch):
    client = _client(monkeypatch, auth_enabled=True)

    response = client.post(
        "/predict",
        files={"file": ("sample.png", _png_bytes(), "image/png")},
    )

    assert response.status_code == 401


def test_predict_accepts_correct_api_key(monkeypatch):
    from src import api

    def fake_run_image_prediction(**kwargs):
        return {
            "image_name": kwargs["image_name"],
            "image_size": {"width": 8, "height": 6},
            "model_path": kwargs["model_path"],
            "confidence_threshold": kwargs["conf"],
            "image_size_requested": kwargs["imgsz"],
            "device": kwargs["device"],
            "num_detections": 0,
            "detections": [],
        }

    monkeypatch.setattr(
        api.image_inference_service,
        "run_image_prediction",
        fake_run_image_prediction,
    )
    client = _client(monkeypatch, auth_enabled=True)

    response = client.post(
        "/predict",
        headers={"X-API-Key": "test-secret"},
        files={"file": ("sample.png", _png_bytes(), "image/png")},
    )

    assert response.status_code == 200
    assert response.json()["num_detections"] == 0
