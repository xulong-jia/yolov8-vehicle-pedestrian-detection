"""In-memory video job registry and artifact readers for FastAPI.

This service is intentionally read-only for artifacts. It does not run YOLO,
does not run tracking, does not run analytics, and does not write files.
"""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


EXPECTED_ARTIFACTS = {
    "metadata": "metadata.json",
    "detections": "detections.csv",
    "tracks": "tracks.csv",
    "count_events": "count_events.csv",
    "roi_frame_counts": "roi_frame_counts.csv",
    "events": "events.jsonl",
    "summary": "video_analysis_summary.json",
}


class VideoJobRegistry:
    """Store short-lived video job records in memory."""

    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}

    def create_job(
        self,
        run_dir: str | Path | None = None,
        video_id: str = "demo",
        run_name: str | None = None,
    ) -> dict[str, Any]:
        job_id = uuid4().hex
        effective_run_name = run_name or job_id
        job = {
            "job_id": job_id,
            "status": "created",
            "video_id": video_id or "demo",
            "run_name": effective_run_name,
            "run_dir": "",
            "created_at": _utc_now_iso(),
            "message": "Video execution is not implemented in this skeleton.",
        }
        self._jobs[job_id] = job
        if run_dir is not None:
            return self.attach_run_dir(job_id, run_dir)
        return dict(job)

    def get_job(self, job_id: str) -> dict[str, Any]:
        if job_id not in self._jobs:
            raise KeyError(f"Video job not found: {job_id}")
        return dict(self._jobs[job_id])

    def list_jobs(self) -> list[dict[str, Any]]:
        return [dict(job) for job in self._jobs.values()]

    def attach_run_dir(self, job_id: str, run_dir: str | Path) -> dict[str, Any]:
        if job_id not in self._jobs:
            raise KeyError(f"Video job not found: {job_id}")
        path = Path(run_dir)
        artifacts = discover_run_artifacts(path)
        has_artifacts = any(item["exists"] for item in artifacts.values())
        job = self._jobs[job_id]
        job["run_dir"] = str(path)
        job["status"] = "attached" if has_artifacts else "missing_artifacts"
        job["message"] = (
            "Attached to existing VideoAnalysisCenter artifacts."
            if has_artifacts
            else "Run directory has no known artifacts."
        )
        return dict(job)

    def clear(self) -> None:
        self._jobs.clear()


registry = VideoJobRegistry()


def read_csv_artifact(path: str | Path, max_rows: int | None = None) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_file():
        return _missing_artifact(file_path, "csv")

    with file_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    return {
        "exists": True,
        "path": str(file_path),
        "type": "csv",
        "row_count": len(rows),
        "data": _limit_rows(rows, max_rows),
    }


def read_json_artifact(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_file():
        return _missing_artifact(file_path, "json")

    with file_path.open(encoding="utf-8") as file:
        data = json.load(file)
    return {
        "exists": True,
        "path": str(file_path),
        "type": "json",
        "data": data,
    }


def read_jsonl_artifact(path: str | Path, max_rows: int | None = None) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_file():
        return _missing_artifact(file_path, "jsonl")

    rows: list[Any] = []
    with file_path.open(encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return {
        "exists": True,
        "path": str(file_path),
        "type": "jsonl",
        "row_count": len(rows),
        "data": _limit_rows(rows, max_rows),
    }


def discover_run_artifacts(run_dir: str | Path) -> dict[str, dict[str, Any]]:
    base = Path(run_dir)
    return {
        key: {
            "exists": (base / filename).is_file(),
            "path": str(base / filename),
        }
        for key, filename in EXPECTED_ARTIFACTS.items()
    }


def get_job_artifact(
    job: dict[str, Any],
    artifact_type: str,
    max_rows: int | None = None,
) -> dict[str, Any]:
    run_dir = job.get("run_dir")
    if not run_dir:
        return {
            "exists": False,
            "path": "",
            "type": artifact_type,
            "data": [],
            "row_count": 0,
        }

    base = Path(str(run_dir))
    if artifact_type == "detections":
        return read_csv_artifact(base / EXPECTED_ARTIFACTS["detections"], max_rows)
    if artifact_type == "tracks":
        return read_csv_artifact(base / EXPECTED_ARTIFACTS["tracks"], max_rows)
    if artifact_type == "events":
        return read_jsonl_artifact(base / EXPECTED_ARTIFACTS["events"], max_rows)
    if artifact_type == "analytics":
        return _read_analytics_artifacts(base, max_rows)
    raise ValueError(f"Unsupported artifact type: {artifact_type}")


def _read_analytics_artifacts(base: Path, max_rows: int | None) -> dict[str, Any]:
    summary = read_json_artifact(base / EXPECTED_ARTIFACTS["summary"])
    count_events = read_csv_artifact(base / EXPECTED_ARTIFACTS["count_events"], max_rows)
    roi_frame_counts = read_csv_artifact(
        base / EXPECTED_ARTIFACTS["roi_frame_counts"],
        max_rows,
    )
    exists = summary["exists"] or count_events["exists"] or roi_frame_counts["exists"]
    return {
        "exists": exists,
        "path": str(base),
        "type": "analytics",
        "data": {
            "summary": summary,
            "count_events": count_events,
            "roi_frame_counts": roi_frame_counts,
        },
    }


def _missing_artifact(path: Path, artifact_type: str) -> dict[str, Any]:
    return {
        "exists": False,
        "path": str(path),
        "type": artifact_type,
        "row_count": 0,
        "data": [] if artifact_type in {"csv", "jsonl"} else {},
    }


def _limit_rows(rows: list[Any], max_rows: int | None) -> list[Any]:
    if max_rows is None:
        return rows
    return rows[: max(0, max_rows)]


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
