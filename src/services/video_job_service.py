"""In-memory video job registry, execution wrapper, and artifact readers."""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
import threading
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

    def __init__(self, base_output_dir: str | Path = "local_outputs/api_video_jobs") -> None:
        self._jobs: dict[str, dict[str, Any]] = {}
        self.base_output_dir = Path(base_output_dir)
        self._lock = threading.Lock()

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
        self._set_job(job_id, job)
        if run_dir is not None:
            return self.attach_run_dir(job_id, run_dir)
        return dict(job)

    def create_execution_job(
        self,
        model_path: str | Path | None,
        video_path: str | Path | None,
        video_id: str = "demo",
        run_name: str | None = None,
        conf: float = 0.25,
        imgsz: int = 640,
        device: str = "cpu",
    ) -> dict[str, Any]:
        job_id = uuid4().hex
        effective_run_name = _safe_run_name(run_name or "api_run")
        output_dir = self.base_output_dir / job_id
        run_dir = output_dir / "video_analysis" / effective_run_name
        job = {
            "job_id": job_id,
            "status": "created",
            "video_id": video_id or "demo",
            "run_name": effective_run_name,
            "run_dir": str(run_dir),
            "output_dir": str(output_dir),
            "created_at": _utc_now_iso(),
            "started_at": None,
            "finished_at": None,
            "message": "Video analysis job created.",
            "model_path": str(model_path or ""),
            "video_path": str(video_path or ""),
            "conf": float(conf),
            "imgsz": int(imgsz),
            "device": str(device),
            "summary_path": None,
            "artifact_paths": {},
            "error": None,
        }
        self._set_job(job_id, job)
        return dict(job)

    def run_job(self, job_id: str) -> dict[str, Any]:
        job = self.get_job(job_id)
        self.mark_running(job_id)
        try:
            model_path = _require_existing_file(job.get("model_path"), "model_path")
            video_path = _require_existing_file(
                job.get("video_path"),
                "source/video_path",
            )

            # Keep compute imports lazy so API import and read-only result queries stay light.
            from src.run_video_analysis_smoke import run_four_step_smoke

            summary = run_four_step_smoke(
                model_path=model_path,
                source=video_path,
                output_dir=job["output_dir"],
                video_id=job["video_id"],
                conf=float(job["conf"]),
                imgsz=int(job["imgsz"]),
                device=str(job["device"]),
                run_name=job["run_name"],
            )
            return self.mark_succeeded(job_id, summary)
        except Exception as exc:
            return self.mark_failed(job_id, _short_error(exc))

    def get_job(self, job_id: str) -> dict[str, Any]:
        with self._lock:
            if job_id not in self._jobs:
                raise KeyError(f"Video job not found: {job_id}")
            return dict(self._jobs[job_id])

    def list_jobs(self) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(job) for job in self._jobs.values()]

    def attach_run_dir(self, job_id: str, run_dir: str | Path) -> dict[str, Any]:
        path = Path(run_dir)
        artifacts = discover_run_artifacts(path)
        has_artifacts = any(item["exists"] for item in artifacts.values())
        with self._lock:
            if job_id not in self._jobs:
                raise KeyError(f"Video job not found: {job_id}")
            job = self._jobs[job_id]
            job["run_dir"] = str(path)
            job["status"] = "attached" if has_artifacts else "missing_artifacts"
            job["message"] = (
                "Attached to existing VideoAnalysisCenter artifacts."
                if has_artifacts
                else "Run directory has no known artifacts."
            )
            return dict(job)

    def mark_running(self, job_id: str) -> dict[str, Any]:
        return self._update_job(
            job_id,
            status="running",
            started_at=_utc_now_iso(),
            message="Video analysis job is running.",
            error=None,
        )

    def mark_succeeded(self, job_id: str, summary: dict[str, Any]) -> dict[str, Any]:
        summary_path = Path(self.get_job(job_id)["run_dir"]) / "video_analysis_summary.json"
        artifact_paths = _collect_artifact_paths(summary_path.parent, summary)
        return self._update_job(
            job_id,
            status="succeeded",
            finished_at=_utc_now_iso(),
            message="Video analysis job succeeded.",
            summary_path=str(summary_path),
            artifact_paths=artifact_paths,
            error=None,
        )

    def mark_failed(self, job_id: str, error: str) -> dict[str, Any]:
        return self._update_job(
            job_id,
            status="failed",
            finished_at=_utc_now_iso(),
            message=f"Video analysis job failed: {error}",
            error=error,
        )

    def clear(self) -> None:
        with self._lock:
            self._jobs.clear()

    def _set_job(self, job_id: str, job: dict[str, Any]) -> None:
        with self._lock:
            self._jobs[job_id] = dict(job)

    def _update_job(self, job_id: str, **updates: Any) -> dict[str, Any]:
        with self._lock:
            if job_id not in self._jobs:
                raise KeyError(f"Video job not found: {job_id}")
            self._jobs[job_id].update(updates)
            return dict(self._jobs[job_id])


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


def _safe_run_name(run_name: str) -> str:
    name = str(run_name).strip()
    if not name or name in {".", ".."}:
        return "api_run"
    if "/" in name or "\\" in name:
        return name.replace("/", "_").replace("\\", "_")
    return name


def _require_existing_file(path: Any, field_name: str) -> Path:
    if path is None or not str(path).strip():
        raise FileNotFoundError(f"{field_name} is required")
    file_path = Path(str(path)).expanduser()
    if not file_path.is_file():
        raise FileNotFoundError(f"{field_name} not found: {file_path}")
    return file_path


def _short_error(exc: Exception, max_length: int = 240) -> str:
    message = str(exc).strip() or exc.__class__.__name__
    return message if len(message) <= max_length else f"{message[:max_length]}..."


def _collect_artifact_paths(run_dir: Path, summary: dict[str, Any]) -> dict[str, str]:
    paths = {
        "metadata": str(run_dir / "metadata.json"),
        "detections": str(run_dir / EXPECTED_ARTIFACTS["detections"]),
        "tracks": str(run_dir / EXPECTED_ARTIFACTS["tracks"]),
        "count_events": str(run_dir / EXPECTED_ARTIFACTS["count_events"]),
        "roi_frame_counts": str(run_dir / EXPECTED_ARTIFACTS["roi_frame_counts"]),
        "events": str(run_dir / EXPECTED_ARTIFACTS["events"]),
        "summary": str(run_dir / EXPECTED_ARTIFACTS["summary"]),
    }
    for key in ("detections_csv", "tracks_csv"):
        value = summary.get(key)
        if value:
            paths[key] = str(value)
    return paths
