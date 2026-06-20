"""Tests for FastAPI video job/result query skeleton."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

from fastapi.testclient import TestClient
import pytest

from src.api import create_app
from src.services.job_store import SQLiteVideoJobStore
from src.services.video_job_service import VideoJobRegistry, registry


@pytest.fixture(autouse=True)
def clear_video_jobs(tmp_path: Path) -> None:
    registry.base_output_dir = tmp_path / "api_video_jobs"
    registry.store = SQLiteVideoJobStore(tmp_path / "api_video_jobs" / "video_jobs.sqlite3")
    registry.clear()
    yield
    registry.base_output_dir = tmp_path / "api_video_jobs"
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
    assert "created" in body["message"].lower()
    assert set(tmp_path.rglob("*")) == before

    fetched = client.get(f"/api/videos/jobs/{body['job_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "failed"
    assert "model_path is required" in fetched.json()["error"]


def test_create_video_job_runs_background_flow_and_records_artifacts(
    tmp_path,
    monkeypatch,
):
    from src import run_video_analysis_smoke

    model_path = tmp_path / "best.pt"
    video_path = tmp_path / "demo.mp4"
    model_path.write_bytes(b"fake model")
    video_path.write_bytes(b"fake video")
    registry.base_output_dir = tmp_path / "api_video_jobs"
    calls = []

    def fake_run_four_step_smoke(**kwargs):
        calls.append(kwargs)
        output_dir = Path(kwargs["output_dir"])
        run_name = kwargs["run_name"]
        run_dir = output_dir / "video_analysis" / run_name
        run_dir.mkdir(parents=True)
        (output_dir / "tracking").mkdir()
        _write_csv(output_dir / "detections.csv", [{"video_id": "demo", "frame_index": 0}])
        _write_csv(output_dir / "tracking" / "tracks.csv", [{"video_id": "demo", "track_id": 1}])
        _write_json(run_dir / "metadata.json", {"video_id": kwargs["video_id"]})
        _write_csv(run_dir / "detections.csv", [{"video_id": "demo", "frame_index": 0}])
        _write_csv(run_dir / "tracks.csv", [{"video_id": "demo", "track_id": 1}])
        _write_csv(run_dir / "count_events.csv", [{"line_id": "main"}])
        _write_csv(run_dir / "roi_frame_counts.csv", [{"roi_id": "main"}])
        _write_jsonl(run_dir / "events.jsonl", [{"event_id": "e1"}])
        _write_json(
            run_dir / "video_analysis_summary.json",
            {"video_id": kwargs["video_id"], "track_count": 1},
        )
        return {
            "video_id": kwargs["video_id"],
            "detections_csv": str(output_dir / "detections.csv"),
            "tracks_csv": str(output_dir / "tracking" / "tracks.csv"),
        }

    monkeypatch.setattr(run_video_analysis_smoke, "run_four_step_smoke", fake_run_four_step_smoke)
    client = _client()

    response = client.post(
        "/api/videos/analyze",
        json={
            "model_path": str(model_path),
            "video_path": str(video_path),
            "video_id": "demo",
            "run_name": "api_run",
            "conf": 0.3,
            "imgsz": 320,
            "device": "cpu",
        },
    )

    assert response.status_code == 200
    created = response.json()
    assert created["status"] == "created"
    assert created["output_dir"].endswith(f"api_video_jobs/{created['job_id']}")
    assert calls[0]["model_path"] == model_path
    assert calls[0]["source"] == video_path
    assert calls[0]["conf"] == 0.3
    assert calls[0]["imgsz"] == 320

    fetched = client.get(f"/api/videos/jobs/{created['job_id']}")
    assert fetched.status_code == 200
    job = fetched.json()
    assert job["status"] == "succeeded"
    assert job["created_at"]
    assert job["updated_at"]
    assert job["started_at"]
    assert job["finished_at"]
    assert job["summary_path"].endswith("video_analysis/api_run/video_analysis_summary.json")
    assert job["artifact_paths"]["summary"].endswith("video_analysis_summary.json")
    assert job["artifact_paths"]["detections"].endswith("video_analysis/api_run/detections.csv")

    analytics = client.get(f"/api/videos/jobs/{created['job_id']}/analytics")
    assert analytics.status_code == 200
    assert analytics.json()["data"]["summary"]["data"]["track_count"] == 1

    persisted = registry.store.get_job(created["job_id"])
    assert persisted["status"] == "succeeded"
    assert persisted["artifact_paths"]["summary"].endswith("video_analysis_summary.json")


def test_create_video_job_accepts_source_alias_for_video_path(tmp_path, monkeypatch):
    from src import run_video_analysis_smoke

    model_path = tmp_path / "best.pt"
    source_path = tmp_path / "source.mp4"
    model_path.write_bytes(b"fake model")
    source_path.write_bytes(b"fake video")
    registry.base_output_dir = tmp_path / "api_video_jobs"
    calls = []

    def fake_run_four_step_smoke(**kwargs):
        calls.append(kwargs)
        output_dir = Path(kwargs["output_dir"])
        run_dir = output_dir / "video_analysis" / kwargs["run_name"]
        run_dir.mkdir(parents=True)
        _write_json(run_dir / "video_analysis_summary.json", {"video_id": kwargs["video_id"]})
        return {"video_id": kwargs["video_id"]}

    monkeypatch.setattr(run_video_analysis_smoke, "run_four_step_smoke", fake_run_four_step_smoke)
    client = _client()

    response = client.post(
        "/api/videos/analyze",
        json={
            "model_path": str(model_path),
            "source": str(source_path),
            "video_id": "demo_api",
            "run_name": "source_alias",
        },
    )

    assert response.status_code == 200
    created = response.json()
    assert calls[0]["source"] == source_path
    fetched = client.get(f"/api/videos/jobs/{created['job_id']}")
    assert fetched.json()["status"] == "succeeded"


def test_video_job_state_flow_helpers(tmp_path):
    registry.base_output_dir = tmp_path / "api_video_jobs"
    job = registry.create_execution_job(
        model_path=tmp_path / "best.pt",
        video_path=tmp_path / "demo.mp4",
        video_id="demo",
        run_name="flow",
    )

    assert job["status"] == "created"
    assert registry.mark_running(job["job_id"])["status"] == "running"
    failed = registry.mark_failed(job["job_id"], "clear failure")
    assert failed["status"] == "failed"
    assert failed["error"] == "clear failure"

    persisted = registry.store.get_job(job["job_id"])
    assert persisted["status"] == "failed"
    assert persisted["error"] == "clear failure"


def test_new_registry_instance_can_query_persisted_job(tmp_path):
    db_path = tmp_path / "persisted" / "video_jobs.sqlite3"
    store = SQLiteVideoJobStore(db_path)
    first_registry = VideoJobRegistry(base_output_dir=tmp_path / "outputs", store=store)

    job = first_registry.create_execution_job(
        model_path=tmp_path / "best.pt",
        video_path=tmp_path / "demo.mp4",
        video_id="demo",
        run_name="persisted_run",
    )
    first_registry.mark_succeeded(
        job["job_id"],
        {"detections_csv": "detections.csv", "tracks_csv": "tracks.csv"},
    )

    second_registry = VideoJobRegistry(
        base_output_dir=tmp_path / "outputs",
        store=SQLiteVideoJobStore(db_path),
    )
    restored = second_registry.get_job(job["job_id"])

    assert restored["status"] == "succeeded"
    assert restored["run_name"] == "persisted_run"
    assert restored["artifact_paths"]["summary"].endswith("video_analysis_summary.json")
    assert restored["artifact_paths"]["detections_csv"] == "detections.csv"


def test_sqlite_store_round_trips_artifact_paths_and_creates_missing_directory(tmp_path):
    db_path = tmp_path / "missing" / "nested" / "video_jobs.sqlite3"
    store = SQLiteVideoJobStore(db_path)

    store.upsert_job(
        {
            "job_id": "job-1",
            "status": "succeeded",
            "video_id": "demo",
            "run_name": "run",
            "run_dir": "run-dir",
            "output_dir": "output-dir",
            "summary_path": "summary.json",
            "artifact_paths": {"summary": "summary.json", "events": "events.jsonl"},
            "error": None,
            "message": "ok",
            "created_at": "2026-06-20T00:00:00+00:00",
            "updated_at": "2026-06-20T00:00:01+00:00",
        }
    )

    assert db_path.is_file()
    restored = store.get_job("job-1")
    assert restored["artifact_paths"] == {"summary": "summary.json", "events": "events.jsonl"}
    assert restored["status"] == "succeeded"


def test_create_video_job_missing_model_or_video_fails_clearly(tmp_path):
    registry.base_output_dir = tmp_path / "api_video_jobs"
    video_path = tmp_path / "demo.mp4"
    model_path = tmp_path / "best.pt"
    video_path.write_bytes(b"fake video")
    model_path.write_bytes(b"fake model")
    client = _client()

    response = client.post(
        "/api/videos/analyze",
        json={
            "model_path": str(tmp_path / "missing.pt"),
            "video_path": str(video_path),
            "run_name": "missing_model",
        },
    )

    assert response.status_code == 200
    created = response.json()
    fetched = client.get(f"/api/videos/jobs/{created['job_id']}")
    assert fetched.status_code == 200
    body = fetched.json()
    assert body["status"] == "failed"
    assert "model_path not found" in body["error"]

    response = client.post(
        "/api/videos/analyze",
        json={
            "model_path": str(video_path),
            "video_path": str(tmp_path / "missing.mp4"),
            "run_name": "missing_video",
        },
    )
    created = response.json()
    body = client.get(f"/api/videos/jobs/{created['job_id']}").json()
    assert body["status"] == "failed"
    assert "source/video_path not found" in body["error"]

    response = client.post(
        "/api/videos/analyze",
        json={
            "model_path": str(model_path),
            "run_name": "missing_source_and_video_path",
        },
    )
    created = response.json()
    body = client.get(f"/api/videos/jobs/{created['job_id']}").json()
    assert body["status"] == "failed"
    assert "source/video_path is required" in body["error"]


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


def test_download_summary_artifact(tmp_path):
    run_dir = _make_run_dir(tmp_path)
    client = _client()
    job = client.post("/api/videos/analyze", json={"run_dir": str(run_dir)}).json()

    response = client.get(
        f"/api/videos/jobs/{job['job_id']}/artifacts/summary/download",
    )

    assert response.status_code == 200
    assert response.headers["content-disposition"].endswith(
        'filename="video_analysis_summary.json"'
    )
    assert response.json()["track_count"] == 2


def test_download_registered_csv_artifacts(tmp_path):
    run_dir = _make_run_dir(tmp_path)
    client = _client()
    job = client.post("/api/videos/analyze", json={"run_dir": str(run_dir)}).json()

    detections = client.get(
        f"/api/videos/jobs/{job['job_id']}/artifacts/detections/download",
    )
    tracks = client.get(
        f"/api/videos/jobs/{job['job_id']}/artifacts/tracks/download",
    )

    assert detections.status_code == 200
    assert "class_name" in detections.text
    assert "Person" in detections.text
    assert tracks.status_code == 200
    assert "track_id" in tracks.text


def test_download_unknown_artifact_returns_404(tmp_path):
    run_dir = _make_run_dir(tmp_path)
    client = _client()
    job = client.post("/api/videos/analyze", json={"run_dir": str(run_dir)}).json()

    response = client.get(
        f"/api/videos/jobs/{job['job_id']}/artifacts/not_registered/download",
    )

    assert response.status_code == 404
    assert "artifact" in response.json()["detail"].lower()


def test_download_registered_missing_file_returns_404(tmp_path):
    run_dir = _make_run_dir(tmp_path)
    client = _client()
    job = client.post("/api/videos/analyze", json={"run_dir": str(run_dir)}).json()
    (run_dir / "tracks.csv").unlink()

    response = client.get(
        f"/api/videos/jobs/{job['job_id']}/artifacts/tracks/download",
    )

    assert response.status_code == 404
    assert "file not found" in response.json()["detail"].lower()


def test_download_rejects_path_traversal_artifact_name(tmp_path):
    run_dir = _make_run_dir(tmp_path)
    client = _client()
    job = client.post("/api/videos/analyze", json={"run_dir": str(run_dir)}).json()

    response = client.get(
        f"/api/videos/jobs/{job['job_id']}/artifacts/%2E%2E/download",
    )

    assert response.status_code in {400, 404}


def test_download_unknown_job_returns_404():
    client = _client()

    response = client.get("/api/videos/jobs/missing/artifacts/summary/download")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


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
