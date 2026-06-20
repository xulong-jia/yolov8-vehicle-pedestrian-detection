"""Tests for FastAPI video job/result query skeleton."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient
import pytest

from src.api import create_app
from src.services.video_job_service import registry


@pytest.fixture(autouse=True)
def clear_video_jobs() -> None:
    registry.clear()
    yield
    registry.clear()


def _client() -> TestClient:
    return TestClient(create_app())


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = list(rows[0].keys()) if rows else ["id"]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(f"{json.dumps(row)}\n" for row in rows),
        encoding="utf-8",
    )


def _make_run_dir(tmp_path: Path) -> Path:
    run_dir = tmp_path / "video_analysis" / "demo_run"
    run_dir.mkdir(parents=True)
    _write_json(run_dir / "metadata.json", {"video_id": "demo", "run_name": "demo_run"})
    _write_csv(
        run_dir / "detections.csv",
        [
            {"frame_index": 0, "class_name": "Car", "confidence": 0.9},
            {"frame_index": 1, "class_name": "Person", "confidence": 0.8},
        ],
    )
    _write_csv(
        run_dir / "tracks.csv",
        [
            {"frame_index": 0, "track_id": 1, "class_name": "Car"},
            {"frame_index": 1, "track_id": 2, "class_name": "Person"},
        ],
    )
    _write_csv(
        run_dir / "count_events.csv",
        [{"line_id": "line_main", "track_id": 1, "direction": "up"}],
    )
    _write_csv(
        run_dir / "roi_frame_counts.csv",
        [{"roi_id": "roi_main", "frame_index": 1, "object_count": 2}],
    )
    _write_jsonl(
        run_dir / "events.jsonl",
        [
            {"event_id": "e1", "event_type": "long_stay"},
            {"event_id": "e2", "event_type": "crowd_warning"},
        ],
    )
    _write_json(
        run_dir / "video_analysis_summary.json",
        {"video_id": "demo", "track_count": 2, "event_summary": {"total": 2}},
    )
    return run_dir


def test_create_video_job_without_run_dir_does_not_create_files(tmp_path):
    client = _client()
    before = set(tmp_path.rglob("*"))

    response = client.post(
        "/api/videos/analyze",
        json={"video_id": "demo", "run_name": "demo_run"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "created"
    assert body["video_id"] == "demo"
    assert body["run_name"] == "demo_run"
    assert "not implemented" in body["message"]
    assert set(tmp_path.rglob("*")) == before


def test_create_video_job_with_run_dir_attaches_existing_artifacts(tmp_path):
    run_dir = _make_run_dir(tmp_path)
    client = _client()

    response = client.post(
        "/api/videos/analyze",
        json={"video_id": "demo", "run_name": "demo_run", "run_dir": str(run_dir)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "attached"
    assert body["run_dir"] == str(run_dir)
    assert body["job_id"]


def test_get_video_job_and_unknown_job(tmp_path):
    run_dir = _make_run_dir(tmp_path)
    client = _client()
    created = client.post(
        "/api/videos/analyze",
        json={"video_id": "demo", "run_dir": str(run_dir)},
    ).json()

    response = client.get(f"/api/videos/jobs/{created['job_id']}")
    missing = client.get("/api/videos/jobs/missing")

    assert response.status_code == 200
    assert response.json()["job_id"] == created["job_id"]
    assert missing.status_code == 404
    assert "not found" in missing.json()["detail"].lower()


def test_get_detections_respects_max_rows(tmp_path):
    run_dir = _make_run_dir(tmp_path)
    client = _client()
    job = client.post("/api/videos/analyze", json={"run_dir": str(run_dir)}).json()

    response = client.get(f"/api/videos/jobs/{job['job_id']}/detections?max_rows=1")

    assert response.status_code == 200
    body = response.json()
    assert body["artifact_type"] == "detections"
    assert body["exists"] is True
    assert body["row_count"] == 2
    assert len(body["data"]) == 1
    assert body["data"][0]["class_name"] == "Car"


def test_get_tracks(tmp_path):
    run_dir = _make_run_dir(tmp_path)
    client = _client()
    job = client.post("/api/videos/analyze", json={"run_dir": str(run_dir)}).json()

    response = client.get(f"/api/videos/jobs/{job['job_id']}/tracks")

    assert response.status_code == 200
    body = response.json()
    assert body["row_count"] == 2
    assert body["data"][1]["track_id"] == "2"


def test_get_analytics_combines_summary_count_and_roi(tmp_path):
    run_dir = _make_run_dir(tmp_path)
    client = _client()
    job = client.post("/api/videos/analyze", json={"run_dir": str(run_dir)}).json()

    response = client.get(f"/api/videos/jobs/{job['job_id']}/analytics")

    assert response.status_code == 200
    body = response.json()
    assert body["artifact_type"] == "analytics"
    assert body["data"]["summary"]["data"]["track_count"] == 2
    assert body["data"]["count_events"]["row_count"] == 1
    assert body["data"]["roi_frame_counts"]["row_count"] == 1


def test_get_events_respects_max_rows(tmp_path):
    run_dir = _make_run_dir(tmp_path)
    client = _client()
    job = client.post("/api/videos/analyze", json={"run_dir": str(run_dir)}).json()

    response = client.get(f"/api/videos/jobs/{job['job_id']}/events?max_rows=1")

    assert response.status_code == 200
    body = response.json()
    assert body["row_count"] == 2
    assert len(body["data"]) == 1
    assert body["data"][0]["event_type"] == "long_stay"


def test_missing_artifact_returns_404(tmp_path):
    run_dir = tmp_path / "empty_run"
    run_dir.mkdir()
    client = _client()
    job = client.post("/api/videos/analyze", json={"run_dir": str(run_dir)}).json()

    response = client.get(f"/api/videos/jobs/{job['job_id']}/detections")

    assert job["status"] == "missing_artifacts"
    assert response.status_code == 404
    assert "artifact not found" in response.json()["detail"]


def test_video_job_endpoints_do_not_import_compute_runtimes(tmp_path):
    run_dir = _make_run_dir(tmp_path)
    sys.modules.pop("src.predict_video", None)
    sys.modules.pop("src.track_video", None)
    sys.modules.pop("src.render_tracked_video", None)

    client = _client()
    job = client.post("/api/videos/analyze", json={"run_dir": str(run_dir)}).json()
    client.get(f"/api/videos/jobs/{job['job_id']}/detections")
    client.get(f"/api/videos/jobs/{job['job_id']}/tracks")
    client.get(f"/api/videos/jobs/{job['job_id']}/analytics")
    client.get(f"/api/videos/jobs/{job['job_id']}/events")

    assert "src.predict_video" not in sys.modules
    assert "src.track_video" not in sys.modules
    assert "src.render_tracked_video" not in sys.modules
