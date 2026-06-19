"""Read-only catalog helpers for the Streamlit video demo page."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def parse_int(value: Any, default: int = 0) -> int:
    """Parse an integer-like value without raising for empty CSV cells."""
    if value is None:
        return default
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def load_json(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    if not json_path.is_file():
        return {}
    with json_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data if isinstance(data, dict) else {"data": data}


def count_file_lines(path: str | Path) -> int:
    file_path = Path(path)
    if not file_path.is_file():
        return 0
    with file_path.open("r", encoding="utf-8", newline="") as file:
        return sum(1 for _ in file)


def read_csv_head(path: str | Path, max_rows: int = 5) -> list[dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.is_file():
        return []
    rows: list[dict[str, str]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append(dict(row))
            if len(rows) >= max_rows:
                break
    return rows


def read_jsonl_head(path: str | Path, max_rows: int = 5) -> list[dict[str, Any]]:
    jsonl_path = Path(path)
    if not jsonl_path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    with jsonl_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as exc:
                value = {"line_number": line_number, "raw": stripped, "error": str(exc)}
            rows.append(value if isinstance(value, dict) else {"value": value})
            if len(rows) >= max_rows:
                break
    return rows


def _csv_file_summary(path: Path, max_rows: int = 5) -> dict[str, Any]:
    return {
        "exists": path.is_file(),
        "path": str(path),
        "line_count": count_file_lines(path),
        "head": read_csv_head(path, max_rows=max_rows),
    }


def _json_file_summary(path: Path) -> dict[str, Any]:
    return {"exists": path.is_file(), "path": str(path), "data": load_json(path)}


def summarize_tracks_csv(path: str | Path) -> dict[str, Any]:
    csv_path = Path(path)
    summary: dict[str, Any] = {
        "exists": csv_path.is_file(),
        "path": str(csv_path),
        "row_count": 0,
        "unique_tracks": 0,
        "frames_with_rows": 0,
        "class_counts": {},
        "head": [],
    }
    if not csv_path.is_file():
        return summary

    track_ids: set[str] = set()
    frame_indexes: set[str] = set()
    class_counts: dict[str, int] = {}
    head: list[dict[str, str]] = []

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            summary["row_count"] += 1
            if len(head) < 5:
                head.append(dict(row))
            track_id = str(row.get("track_id", "")).strip()
            if track_id:
                track_ids.add(track_id)
            frame_index = str(row.get("frame_index", "")).strip()
            if frame_index:
                frame_indexes.add(frame_index)
            class_name = str(row.get("class_name", "")).strip() or "unknown"
            class_counts[class_name] = class_counts.get(class_name, 0) + 1

    summary["unique_tracks"] = len(track_ids)
    summary["frames_with_rows"] = len(frame_indexes)
    summary["class_counts"] = dict(sorted(class_counts.items()))
    summary["head"] = head
    return summary


def summarize_event_jsonl(path: str | Path) -> dict[str, Any]:
    jsonl_path = Path(path)
    return {
        "exists": jsonl_path.is_file(),
        "path": str(jsonl_path),
        "line_count": count_file_lines(jsonl_path),
        "head": read_jsonl_head(jsonl_path),
    }


def summarize_video_file(path: str | Path | None) -> dict[str, Any]:
    if not path:
        return {"exists": False, "path": "", "size_bytes": 0, "size_mb": 0.0}
    video_path = Path(path)
    size_bytes = video_path.stat().st_size if video_path.is_file() else 0
    return {
        "exists": video_path.is_file(),
        "path": str(video_path),
        "size_bytes": size_bytes,
        "size_mb": round(size_bytes / (1024 * 1024), 3),
    }


def discover_video_analysis_run(run_dir: str | Path | None) -> dict[str, Any]:
    if not run_dir:
        return {"exists": False, "run_dir": "", "summary": {}, "files": {}}

    root = Path(run_dir)
    summary_path = root / "video_analysis_summary.json"
    files = {
        "metadata": _json_file_summary(root / "metadata.json"),
        "detections_csv": _csv_file_summary(root / "detections.csv"),
        "tracks_csv": summarize_tracks_csv(root / "tracks.csv"),
        "count_events_csv": _csv_file_summary(root / "count_events.csv"),
        "roi_frame_counts_csv": _csv_file_summary(root / "roi_frame_counts.csv"),
        "events_jsonl": summarize_event_jsonl(root / "events.jsonl"),
        "video_analysis_summary": _json_file_summary(summary_path),
    }

    return {
        "exists": root.is_dir(),
        "run_dir": str(root),
        "summary": load_json(summary_path),
        "files": files,
    }


def build_demo_catalog(
    base_dir: str | Path | None = None,
    tracked_video: str | Path | None = None,
    comparison_json: str | Path | None = None,
) -> dict[str, Any]:
    comparison_path = Path(comparison_json) if comparison_json else None
    comparison = load_json(comparison_path) if comparison_path and comparison_path.is_file() else {}
    return {
        "mode": "streamlit_video_demo_catalog",
        "base_dir": str(base_dir or ""),
        "tracked_video": summarize_video_file(tracked_video),
        "video_analysis_run": discover_video_analysis_run(base_dir),
        "comparison": comparison,
        "notes": [
            "Demo catalog is read-only.",
            "Streamlit page should not run YOLO or tracker.",
            "Artifacts remain local-only and should not be committed.",
        ],
    }
