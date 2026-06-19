"""Organize existing video detection/tracking artifacts into analysis runs.

This module organizes existing detections.csv and tracks.csv into a
VideoAnalysisCenter run. It can optionally run analytics on an existing
tracks.csv. It does not run YOLO, does not run a tracker, and does not render
tracked video.
"""

from __future__ import annotations

import csv
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.analytics.event_rules import (
    detect_crowd_warning,
    detect_long_stay,
    detect_wrong_direction,
    summarize_events,
)
from src.analytics.line_counter import count_line_crossings, summarize_count_events
from src.analytics.roi_counter import count_roi_occupancy, summarize_roi_counts
from src.services.video_analysis_center import VideoAnalysisCenter


ARTIFACT_PATHS = {
    "metadata_json": "metadata.json",
    "detections_csv": "detections.csv",
    "tracks_csv": "tracks.csv",
    "video_analysis_summary_json": "video_analysis_summary.json",
}
ANALYTICS_ARTIFACT_PATHS = {
    "count_events_csv": "count_events.csv",
    "roi_frame_counts_csv": "roi_frame_counts.csv",
    "events_jsonl": "events.jsonl",
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
    count_summary: dict[str, Any] | None = None,
    roi_summary: dict[str, Any] | None = None,
    event_summary: dict[str, Any] | None = None,
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
        "count_summary": count_summary if count_summary is not None else {},
        "roi_summary": roi_summary if roi_summary is not None else {},
        "event_summary": event_summary if event_summary is not None else {},
        "bad_case_links": [],
    }


def create_video_analysis_job_run(
    run_name: str,
    base_dir: str | Path,
    detections_csv: str | Path,
    tracks_csv: str | Path,
    metadata: dict[str, Any] | None = None,
    analytics_config: dict[str, Any] | None = None,
    run_analytics: bool = False,
) -> dict[str, Any]:
    detections_path = _existing_file(detections_csv, "detections_csv")
    tracks_path = _existing_file(tracks_csv, "tracks_csv")
    artifact_paths = dict(ARTIFACT_PATHS)
    if run_analytics:
        artifact_paths.update(ANALYTICS_ARTIFACT_PATHS)

    metadata_payload = {
        "mode": "two_command_smoke",
        "input_video": "",
        "video_id": run_name,
    }
    metadata_payload.update(metadata or {})
    metadata_payload["input_video"] = metadata_payload.get("input_video") or ""
    metadata_payload["video_id"] = metadata_payload.get("video_id") or run_name
    metadata_payload["artifact_paths"] = artifact_paths

    center = VideoAnalysisCenter(base_dir)
    run_dir = center.create_run(run_name, metadata_payload)
    shutil.copyfile(detections_path, run_dir / ARTIFACT_PATHS["detections_csv"])
    shutil.copyfile(tracks_path, run_dir / ARTIFACT_PATHS["tracks_csv"])

    detections = load_csv_rows(run_dir / ARTIFACT_PATHS["detections_csv"])
    tracks = load_csv_rows(run_dir / ARTIFACT_PATHS["tracks_csv"])
    count_summary = None
    roi_summary = None
    event_summary = None

    if run_analytics:
        analytics_result = _run_analytics_on_tracks(
            center=center,
            run_name=run_name,
            track_rows=tracks,
            analytics_config=analytics_config or {},
        )
        count_summary = analytics_result["count_summary"]
        roi_summary = analytics_result["roi_summary"]
        event_summary = analytics_result["event_summary"]

    # Re-write metadata after copies and optional analytics so artifact_paths are final.
    center.write_metadata(run_name, metadata_payload)
    summary = build_video_analysis_summary(
        run_name=run_name,
        metadata=metadata_payload,
        detections=detections,
        tracks=tracks,
        artifact_paths=artifact_paths,
        count_summary=count_summary,
        roi_summary=roi_summary,
        event_summary=event_summary,
    )
    center.write_summary(run_name, summary)
    return summary


def _run_analytics_on_tracks(
    center: VideoAnalysisCenter,
    run_name: str,
    track_rows: list[dict[str, Any]],
    analytics_config: dict[str, Any],
) -> dict[str, Any]:
    line_config = _select_named_config(analytics_config, "line", "lines")
    roi_config = _select_named_config(analytics_config, "roi", "rois")
    event_rules = analytics_config.get("event_rules", {})

    count_events: list[dict[str, Any]] = []
    count_summary = summarize_count_events([])
    if line_config is not None:
        count_events, count_summary = count_line_crossings(track_rows, line_config)
    center.write_count_events(run_name, count_events)

    roi_frame_counts: list[dict[str, Any]] = []
    roi_summary = summarize_roi_counts([])
    if roi_config is not None:
        roi_frame_counts, roi_summary = count_roi_occupancy(track_rows, roi_config)
    center.write_roi_counts(run_name, roi_frame_counts)

    events: list[dict[str, Any]] = []
    crowd_rule = event_rules.get("crowd_warning")
    if crowd_rule is not None:
        events.extend(detect_crowd_warning(roi_frame_counts, crowd_rule))
    long_stay_rule = event_rules.get("long_stay")
    if long_stay_rule is not None:
        events.extend(detect_long_stay(track_rows, long_stay_rule))
    wrong_direction_rule = event_rules.get("wrong_direction")
    if wrong_direction_rule is not None:
        events.extend(detect_wrong_direction(track_rows, wrong_direction_rule))
    event_summary = summarize_events(events)
    center.write_events(run_name, events)

    return {
        "count_summary": count_summary,
        "roi_summary": roi_summary,
        "event_summary": event_summary,
    }


def _select_named_config(
    config: dict[str, Any],
    singular_key: str,
    plural_key: str,
) -> dict[str, Any] | None:
    singular_value = config.get(singular_key)
    if isinstance(singular_value, dict):
        return singular_value

    plural_value = config.get(plural_key)
    if isinstance(plural_value, dict):
        for value in plural_value.values():
            if isinstance(value, dict):
                return value
    return None


def _existing_file(path: str | Path, name: str) -> Path:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"{name} not found: {file_path}")
    return file_path


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
