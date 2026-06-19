"""Synthetic end-to-end pipeline for the video analytics core."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.analytics.event_rules import (
    detect_crowd_warning,
    detect_long_stay,
    detect_wrong_direction,
    summarize_events,
)
from src.analytics.geometry import bbox_size_and_area
from src.analytics.line_counter import count_line_crossings
from src.analytics.roi_counter import count_roi_occupancy
from src.services.video_analysis_center import VideoAnalysisCenter


def build_synthetic_tracks(video_id: str = "synthetic_demo") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    rows.extend(
        [
            _track_row(video_id, 0, 0.0, "car_cross", 0, "Car", 5.0, -1.0),
            _track_row(video_id, 1, 1.0, "car_cross", 0, "Car", 5.0, 1.0),
        ]
    )

    for frame_index, timestamp_sec in enumerate([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]):
        rows.append(
            _track_row(
                video_id,
                frame_index,
                timestamp_sec,
                "person_long",
                1,
                "Person",
                3.0,
                4.0,
                roi_id="roi_main",
            )
        )

    for frame_index, timestamp_sec in enumerate([0.0, 1.0, 2.0]):
        rows.append(
            _track_row(
                video_id,
                frame_index,
                timestamp_sec,
                "person_crowd",
                1,
                "Person",
                7.0,
                4.0,
                roi_id="roi_main",
            )
        )

    for frame_index, (timestamp_sec, center_x) in enumerate([(0.0, 1.0), (1.0, 4.0), (2.0, 8.0)]):
        rows.append(
            _track_row(
                video_id,
                frame_index,
                timestamp_sec,
                "car_wrong",
                0,
                "Car",
                center_x,
                6.0,
                line_id="line_main",
                direction="out",
            )
        )

    return rows


def default_synthetic_analytics_config() -> dict[str, Any]:
    return {
        "lines": {
            "line_main": {
                "id": "line_main",
                "points": [[0, 0], [10, 0]],
                "directions": {"positive": "in", "negative": "out"},
                "target_classes": ["Car", "Person"],
                "enabled": True,
            }
        },
        "rois": {
            "roi_main": {
                "id": "roi_main",
                "name": "ROI Main",
                "polygon": [[0, 0], [10, 0], [10, 10], [0, 10]],
                "target_classes": ["Car", "Person"],
                "enabled": True,
            }
        },
        "event_rules": {
            "crowd_warning": {
                "enabled": True,
                "event_type": "crowd_warning",
                "roi_id": "roi_main",
                "severity": "warning",
                "target_classes": ["Person"],
                "parameters": {
                    "min_count": 2,
                    "min_duration_sec": 1.0,
                    "cooldown_sec": 10,
                },
            },
            "long_stay": {
                "enabled": True,
                "event_type": "long_stay",
                "roi_id": "roi_main",
                "severity": "warning",
                "target_classes": ["Car", "Person"],
                "parameters": {
                    "min_duration_sec": 5.0,
                    "cooldown_sec": 10,
                },
            },
            "wrong_direction": {
                "enabled": True,
                "event_type": "wrong_direction",
                "line_id": "line_main",
                "severity": "warning",
                "target_classes": ["Car"],
                "parameters": {
                    "expected_direction": "in",
                    "min_track_length": 3,
                    "min_displacement_px": 2.0,
                    "cooldown_sec": 10,
                },
            },
        },
    }


def run_synthetic_video_analysis(
    run_name: str,
    base_dir: str | Path,
    track_rows: list[dict[str, Any]] | None = None,
    analytics_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rows = track_rows if track_rows is not None else build_synthetic_tracks()
    config = analytics_config if analytics_config is not None else default_synthetic_analytics_config()
    video_id = str(rows[0].get("video_id", "synthetic_demo")) if rows else "synthetic_demo"

    center = VideoAnalysisCenter(base_dir)
    center.create_run(
        run_name,
        metadata={
            "input_video": "synthetic://toy_tracks",
            "config_paths": {"analytics": "synthetic_default"},
            "mode": "synthetic",
        },
    )

    tracks_path = center.write_tracks(run_name, rows)

    line_config = config["lines"]["line_main"]
    count_events, count_summary = count_line_crossings(rows, line_config)
    count_events_path = center.write_count_events(run_name, count_events)

    roi_config = config["rois"]["roi_main"]
    roi_frame_counts, roi_summary = count_roi_occupancy(rows, roi_config)
    roi_counts_path = center.write_roi_counts(run_name, roi_frame_counts)

    event_rules = config["event_rules"]
    events = []
    events.extend(detect_crowd_warning(roi_frame_counts, event_rules["crowd_warning"]))
    events.extend(detect_long_stay(rows, event_rules["long_stay"]))
    events.extend(detect_wrong_direction(rows, event_rules["wrong_direction"]))
    event_summary = summarize_events(events)
    events_path = center.write_events(run_name, events)

    # This synthetic pipeline starts from track rows, not detector outputs.
    summary = {
        "video_id": video_id,
        "run_name": run_name,
        "created_at": _utc_now_iso(),
        "input_video": "synthetic://toy_tracks",
        "config_paths": {"analytics": "synthetic_default"},
        "artifact_paths": {
            "tracks_csv": tracks_path.name,
            "count_events_csv": count_events_path.name,
            "roi_frame_counts_csv": roi_counts_path.name,
            "events_jsonl": events_path.name,
            "video_analysis_summary_json": "video_analysis_summary.json",
        },
        "detection_count": 0,
        "track_count": _unique_track_count(rows),
        "count_summary": count_summary,
        "roi_summary": roi_summary,
        "event_summary": event_summary,
        "bad_case_links": [],
    }
    center.write_summary(run_name, summary)
    return summary


def _track_row(
    video_id: str,
    frame_index: int,
    timestamp_sec: float,
    track_id: str,
    class_id: int,
    class_name: str,
    center_x: float,
    center_y: float,
    roi_id: str | None = None,
    line_id: str | None = None,
    direction: str | None = None,
) -> dict[str, Any]:
    xmin = center_x - 0.25
    ymin = center_y - 0.25
    xmax = center_x + 0.25
    ymax = center_y + 0.25
    width, height, area = bbox_size_and_area(xmin, ymin, xmax, ymax)
    row = {
        "video_id": video_id,
        "frame_index": frame_index,
        "timestamp_sec": timestamp_sec,
        "track_id": track_id,
        "class_id": class_id,
        "class_name": class_name,
        "confidence": 0.99,
        "xmin": xmin,
        "ymin": ymin,
        "xmax": xmax,
        "ymax": ymax,
        "center_x": center_x,
        "center_y": center_y,
        "box_width": width,
        "box_height": height,
        "box_area": area,
        "state": "confirmed",
        "tracker_name": "synthetic",
    }
    if roi_id is not None:
        row["roi_id"] = roi_id
    if line_id is not None:
        row["line_id"] = line_id
    if direction is not None:
        row["direction"] = direction
    return row


def _unique_track_count(track_rows: list[dict[str, Any]]) -> int:
    return len({row.get("track_id") for row in track_rows})


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
