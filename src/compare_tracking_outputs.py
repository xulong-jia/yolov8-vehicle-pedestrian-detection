"""Compare synthetic tracking rows with ByteTrack tracking rows.

This module reads existing CSV/JSON artifacts only. It does not run YOLO, does
not run a tracker, and does not render video.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare synthetic tracks with ByteTrack tracks using existing artifacts."
    )
    parser.add_argument("--synthetic-tracks", required=True, type=Path)
    parser.add_argument("--bytetrack-tracks", required=True, type=Path)
    parser.add_argument("--synthetic-summary", type=Path)
    parser.add_argument("--bytetrack-summary", type=Path)
    parser.add_argument("--video-id", default="demo")
    parser.add_argument("--output-json", type=Path)
    return parser.parse_args(argv)


def load_csv_rows(path: str | Path) -> list[dict[str, str]]:
    csv_path = _require_file(path, "csv")
    with csv_path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def load_json(path: str | Path) -> dict[str, Any]:
    json_path = _require_file(path, "json")
    with json_path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"json must contain an object: {json_path}")
    return data


def parse_float(value: Any, default: float | None = None) -> float | None:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def summarize_tracks(rows: list[dict[str, Any]]) -> dict[str, Any]:
    track_ids = [str(row.get("track_id")) for row in rows if row.get("track_id") not in (None, "")]
    frame_indices = [_parse_int(row.get("frame_index")) for row in rows]
    frame_indices = [frame for frame in frame_indices if frame is not None]

    class_counts: dict[str, int] = {}
    state_counts: dict[str, int] = {}
    rows_by_track: dict[str, int] = {}
    rows_by_frame: dict[int, int] = {}
    bbox_areas: list[float] = []
    confidences: list[float] = []

    for row in rows:
        class_name = str(row.get("class_name") or "unknown")
        class_counts[class_name] = class_counts.get(class_name, 0) + 1

        state = str(row.get("state") or "unknown")
        state_counts[state] = state_counts.get(state, 0) + 1

        track_id = row.get("track_id")
        if track_id not in (None, ""):
            key = str(track_id)
            rows_by_track[key] = rows_by_track.get(key, 0) + 1

        frame_index = _parse_int(row.get("frame_index"))
        if frame_index is not None:
            rows_by_frame[frame_index] = rows_by_frame.get(frame_index, 0) + 1

        area = _bbox_area(row)
        if area is not None:
            bbox_areas.append(area)

        confidence = parse_float(row.get("confidence"))
        if confidence is not None:
            confidences.append(confidence)

    return {
        "row_count": len(rows),
        "unique_tracks": len(set(track_ids)),
        "frames_with_rows": len(set(frame_indices)),
        "frame_min": min(frame_indices) if frame_indices else None,
        "frame_max": max(frame_indices) if frame_indices else None,
        "class_counts": class_counts,
        "state_counts": state_counts,
        "rows_per_track": _distribution(list(rows_by_track.values())),
        "rows_per_frame": _distribution(list(rows_by_frame.values())),
        "bbox_area": _distribution(bbox_areas),
        "confidence": _distribution(confidences),
    }


def compare_track_summaries(
    synthetic_summary: dict[str, Any],
    bytetrack_summary: dict[str, Any],
) -> dict[str, Any]:
    synthetic_rows = int(synthetic_summary.get("row_count") or 0)
    bytetrack_rows = int(bytetrack_summary.get("row_count") or 0)
    class_names = sorted(
        set(synthetic_summary.get("class_counts", {}))
        | set(bytetrack_summary.get("class_counts", {}))
    )
    class_count_deltas = {
        class_name: int(bytetrack_summary.get("class_counts", {}).get(class_name, 0))
        - int(synthetic_summary.get("class_counts", {}).get(class_name, 0))
        for class_name in class_names
    }

    return {
        "row_count_delta": bytetrack_rows - synthetic_rows,
        "row_count_ratio_bytetrack_to_synthetic": _ratio(bytetrack_rows, synthetic_rows),
        "unique_tracks_delta": int(bytetrack_summary.get("unique_tracks") or 0)
        - int(synthetic_summary.get("unique_tracks") or 0),
        "frames_with_rows_delta": int(bytetrack_summary.get("frames_with_rows") or 0)
        - int(synthetic_summary.get("frames_with_rows") or 0),
        "class_count_deltas": class_count_deltas,
        "interpretation": [
            "Synthetic tracks may overrepresent per-detection continuity if built from detection rows.",
            "ByteTrack tracks are sparser but more temporally meaningful.",
            "Lower row_count does not imply worse tracking; it reflects tracker-confirmed IDs and missed/unmatched frames.",
            "Use ByteTrack tracks for demo/runtime where real MOT matters.",
            "Keep synthetic path for deterministic tests and fallback.",
        ],
    }


def load_optional_analysis_summary(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    data = load_json(path)
    keys = [
        "detection_count",
        "track_count",
        "count_summary",
        "roi_summary",
        "event_summary",
    ]
    return {key: data.get(key) for key in keys if key in data}


def build_tracking_comparison(
    synthetic_tracks_csv: str | Path,
    bytetrack_tracks_csv: str | Path,
    synthetic_analysis_summary: str | Path | None = None,
    bytetrack_analysis_summary: str | Path | None = None,
    video_id: str = "demo",
) -> dict[str, Any]:
    synthetic_path = _require_file(synthetic_tracks_csv, "synthetic_tracks")
    bytetrack_path = _require_file(bytetrack_tracks_csv, "bytetrack_tracks")
    synthetic_track_summary = summarize_tracks(load_csv_rows(synthetic_path))
    bytetrack_track_summary = summarize_tracks(load_csv_rows(bytetrack_path))
    comparison = compare_track_summaries(
        synthetic_summary=synthetic_track_summary,
        bytetrack_summary=bytetrack_track_summary,
    )

    return {
        "video_id": video_id,
        "mode": "synthetic_vs_bytetrack_tracking_comparison",
        "synthetic": {
            "tracks_csv": str(synthetic_path),
            "track_summary": synthetic_track_summary,
            "analysis_summary": load_optional_analysis_summary(synthetic_analysis_summary),
        },
        "bytetrack": {
            "tracks_csv": str(bytetrack_path),
            "track_summary": bytetrack_track_summary,
            "analysis_summary": load_optional_analysis_summary(bytetrack_analysis_summary),
        },
        "comparison": comparison,
        "recommendation": {
            "preferred_demo_tracks": "bytetrack",
            "keep_synthetic_for": [
                "deterministic unit tests",
                "fallback when optional tracker dependencies are unavailable",
                "CSV contract validation",
            ],
            "next_steps": [
                "run full-length ByteTrack validation",
                "review synthetic-vs-ByteTrack visual examples",
                "wire ByteTrack outputs into Streamlit/FastAPI demo surfaces",
                "consider MOT metrics such as MOTA and IDF1 only after ground-truth tracking labels exist",
            ],
        },
        "notes": [
            "This comparison reads existing artifacts only.",
            "It does not run YOLO, run ByteTrack, or render video.",
            "Synthetic row volume and ByteTrack row volume are not direct quality metrics.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = build_tracking_comparison(
            synthetic_tracks_csv=args.synthetic_tracks,
            bytetrack_tracks_csv=args.bytetrack_tracks,
            synthetic_analysis_summary=args.synthetic_summary,
            bytetrack_analysis_summary=args.bytetrack_summary,
            video_id=args.video_id,
        )
        if args.output_json:
            output_path = Path(args.output_json).expanduser().resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    except (FileNotFoundError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _require_file(path: str | Path, label: str) -> Path:
    file_path = Path(path).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"{label} not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"{label} must be a file: {file_path}")
    return file_path


def _parse_int(value: Any) -> int | None:
    parsed = parse_float(value)
    if parsed is None:
        return None
    return int(parsed)


def _bbox_area(row: dict[str, Any]) -> float | None:
    xmin = parse_float(row.get("xmin"))
    ymin = parse_float(row.get("ymin"))
    xmax = parse_float(row.get("xmax"))
    ymax = parse_float(row.get("ymax"))
    if None in (xmin, ymin, xmax, ymax):
        return None
    width = max(0.0, float(xmax) - float(xmin))
    height = max(0.0, float(ymax) - float(ymin))
    return width * height


def _distribution(values: list[float | int]) -> dict[str, float | int | None]:
    if not values:
        return {"min": None, "max": None, "avg": None}
    return {
        "min": min(values),
        "max": max(values),
        "avg": sum(values) / len(values),
    }


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


if __name__ == "__main__":
    raise SystemExit(main())
