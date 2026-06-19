"""Writers for video analytics tracking and event artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


TRACKS_FIELDS = [
    "video_id",
    "frame_index",
    "timestamp_sec",
    "track_id",
    "class_id",
    "class_name",
    "confidence",
    "xmin",
    "ymin",
    "xmax",
    "ymax",
    "center_x",
    "center_y",
    "box_width",
    "box_height",
    "box_area",
    "state",
    "tracker_name",
]

COUNT_EVENTS_FIELDS = [
    "video_id",
    "line_id",
    "frame_index",
    "timestamp_sec",
    "track_id",
    "class_id",
    "class_name",
    "direction",
    "center_x",
    "center_y",
]

ROI_FRAME_COUNTS_FIELDS = [
    "video_id",
    "frame_index",
    "timestamp_sec",
    "roi_id",
    "roi_name",
    "class_name",
    "object_count",
    "unique_track_count",
]


def write_tracks_csv(track_rows: list[dict[str, Any]], output_path: str | Path) -> Path:
    return _write_csv(track_rows, output_path, TRACKS_FIELDS)


def write_count_events_csv(count_events: list[dict[str, Any]], output_path: str | Path) -> Path:
    return _write_csv(count_events, output_path, COUNT_EVENTS_FIELDS)


def write_roi_frame_counts_csv(
    roi_frame_counts: list[dict[str, Any]],
    output_path: str | Path,
) -> Path:
    return _write_csv(roi_frame_counts, output_path, ROI_FRAME_COUNTS_FIELDS)


def write_events_jsonl(events: list[dict[str, Any]], output_path: str | Path) -> Path:
    path = _prepare_output_path(output_path)
    with path.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event, ensure_ascii=False))
            file.write("\n")
    return path


def write_json(data: dict[str, Any], output_path: str | Path) -> Path:
    path = _prepare_output_path(output_path)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
    return path


def read_json(output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    return data


def _write_csv(
    rows: list[dict[str, Any]],
    output_path: str | Path,
    fieldnames: list[str],
) -> Path:
    path = _prepare_output_path(output_path)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


def _prepare_output_path(output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
