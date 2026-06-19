"""Organize existing video detection/tracking artifacts into analysis runs.

This module organizes existing detections.csv and tracks.csv into a
VideoAnalysisCenter run. It does not run YOLO, does not run a tracker, and does
not render tracked video.
"""

from __future__ import annotations

import csv
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.services.video_analysis_center import VideoAnalysisCenter


ARTIFACT_PATHS = {
    "metadata_json": "metadata.json",
    "detections_csv": "detections.csv",
    "tracks_csv": "tracks.csv",
    "video_analysis_summary_json": "video_analysis_summary.json",
}


def load_csv_rows(csv_path: str | Path) -> list[dict[str, str]]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def build_video_analysis_summary(
    run_name: str,
    metadata: dict[str, Any],
    detections: list[dict[str, Any]],
    tracks: list[dict[str, Any]],
    artifact_paths: dict[str, str],
) -> dict[str, Any]:
    track_ids = {row.get("track_id") for row in tracks if row.get("track_id")}
    return {
        "video_id": metadata.get("video_id") or run_name,
        "run_name": run_name,
        "created_at": _utc_now_iso(),
        "input_video": metadata.get("input_video", ""),
        "mode": metadata.get("mode", "two_command_smoke"),
        "artifact_paths": artifact_paths,
        "detection_count": len(detections),
        "track_row_count": len(tracks),
        "track_count": len(track_ids),
        "count_summary": {},
        "roi_summary": {},
        "event_summary": {},
        "bad_case_links": [],
    }


def create_video_analysis_job_run(
    run_name: str,
    base_dir: str | Path,
    detections_csv: str | Path,
    tracks_csv: str | Path,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    detections_path = _existing_file(detections_csv, "detections_csv")
    tracks_path = _existing_file(tracks_csv, "tracks_csv")
    metadata_payload = {
        "mode": "two_command_smoke",
        "input_video": "",
        "video_id": run_name,
    }
    metadata_payload.update(metadata or {})
    metadata_payload["input_video"] = metadata_payload.get("input_video") or ""
    metadata_payload["video_id"] = metadata_payload.get("video_id") or run_name
    metadata_payload["artifact_paths"] = dict(ARTIFACT_PATHS)

    center = VideoAnalysisCenter(base_dir)
    run_dir = center.create_run(run_name, metadata_payload)
    shutil.copyfile(detections_path, run_dir / ARTIFACT_PATHS["detections_csv"])
    shutil.copyfile(tracks_path, run_dir / ARTIFACT_PATHS["tracks_csv"])

    # Re-write metadata after copies so artifact_paths are explicit in the final run.
    center.write_metadata(run_name, metadata_payload)
    detections = load_csv_rows(run_dir / ARTIFACT_PATHS["detections_csv"])
    tracks = load_csv_rows(run_dir / ARTIFACT_PATHS["tracks_csv"])
    summary = build_video_analysis_summary(
        run_name=run_name,
        metadata=metadata_payload,
        detections=detections,
        tracks=tracks,
        artifact_paths=dict(ARTIFACT_PATHS),
    )
    center.write_summary(run_name, summary)
    return summary


def _existing_file(path: str | Path, name: str) -> Path:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"{name} not found: {file_path}")
    return file_path


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
