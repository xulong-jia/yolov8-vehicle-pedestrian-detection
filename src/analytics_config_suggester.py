"""Suggest analytics config from existing tracks.csv coordinate distributions.

This helper reads an existing tracks.csv file and proposes line, ROI, and event
rule settings for follow-up smoke analytics tuning. It does not run YOLO, does
not run tracking, and does not validate visual geometry.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any


PERCENTILE_KEYS = (10, 25, 50, 75, 90)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Suggest analytics config from an existing tracks.csv file."
    )
    parser.add_argument("--tracks-csv", required=True, type=Path, help="Path to tracks.csv.")
    parser.add_argument("--video-id", default="demo", help="Video id for the suggestion output.")
    parser.add_argument("--output-json", type=Path, help="Optional JSON output path.")
    parser.add_argument("--line-id", default="line_main", help="Suggested line id.")
    parser.add_argument("--roi-id", default="roi_main", help="Suggested ROI id.")
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Print compact JSON instead of pretty indented JSON.",
    )
    return parser.parse_args(argv)


def load_track_rows(tracks_csv: str | Path) -> list[dict[str, str]]:
    path = Path(tracks_csv)
    if not path.exists():
        raise FileNotFoundError(f"tracks_csv does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"tracks_csv must be a file: {path}")

    with path.open("r", encoding="utf-8", newline="") as file_obj:
        return list(csv.DictReader(file_obj))


def parse_float(value: Any, default: float | None = None) -> float | None:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def bottom_center(row: dict[str, Any]) -> tuple[float, float] | None:
    xmin = parse_float(row.get("xmin"))
    xmax = parse_float(row.get("xmax"))
    ymax = parse_float(row.get("ymax"))
    if xmin is None or xmax is None or ymax is None:
        return None
    return ((xmin + xmax) / 2.0, ymax)


def bbox_center(row: dict[str, Any]) -> tuple[float, float] | None:
    xmin = parse_float(row.get("xmin"))
    ymin = parse_float(row.get("ymin"))
    xmax = parse_float(row.get("xmax"))
    ymax = parse_float(row.get("ymax"))
    if xmin is None or ymin is None or xmax is None or ymax is None:
        return None
    return ((xmin + xmax) / 2.0, (ymin + ymax) / 2.0)


def percentile(values: list[float] | tuple[float, ...], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    bounded_q = min(100.0, max(0.0, float(q)))
    position = (len(ordered) - 1) * bounded_q / 100.0
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(ordered) - 1)
    fraction = position - lower_index
    return ordered[lower_index] + (ordered[upper_index] - ordered[lower_index]) * fraction


def summarize_tracks(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid_rows = []
    class_counts: Counter[str] = Counter()
    track_counts: OrderedDict[str, dict[str, Any]] = OrderedDict()

    frame_values: list[float] = []
    timestamp_values: list[float] = []
    xmin_values: list[float] = []
    ymin_values: list[float] = []
    xmax_values: list[float] = []
    ymax_values: list[float] = []
    center_x_values: list[float] = []
    center_y_values: list[float] = []
    bottom_x_values: list[float] = []
    bottom_y_values: list[float] = []

    for row in rows:
        class_name = row.get("class_name") or "unknown"
        class_counts[class_name] += 1
        track_id = str(row.get("track_id") or "")
        if track_id and track_id not in track_counts:
            track_counts[track_id] = {"track_id": track_id, "row_count": 0, "class_name": class_name}
        if track_id:
            track_counts[track_id]["row_count"] += 1

        frame = parse_float(row.get("frame_index"))
        timestamp = parse_float(row.get("timestamp_sec"))
        xmin = parse_float(row.get("xmin"))
        ymin = parse_float(row.get("ymin"))
        xmax = parse_float(row.get("xmax"))
        ymax = parse_float(row.get("ymax"))
        center = bbox_center(row)
        bottom = bottom_center(row)

        if frame is not None:
            frame_values.append(frame)
        if timestamp is not None:
            timestamp_values.append(timestamp)
        if xmin is not None:
            xmin_values.append(xmin)
        if ymin is not None:
            ymin_values.append(ymin)
        if xmax is not None:
            xmax_values.append(xmax)
        if ymax is not None:
            ymax_values.append(ymax)
        if center is not None:
            center_x_values.append(center[0])
            center_y_values.append(center[1])
        if bottom is not None:
            bottom_x_values.append(bottom[0])
            bottom_y_values.append(bottom[1])
            valid_rows.append(row)

    return {
        "row_count": len(rows),
        "track_count": len(track_counts),
        "class_counts": dict(sorted(class_counts.items())),
        "frame_min": _maybe_int(_min_or_none(frame_values)),
        "frame_max": _maybe_int(_max_or_none(frame_values)),
        "timestamp_min": _min_or_none(timestamp_values),
        "timestamp_max": _max_or_none(timestamp_values),
        "xmin_min": _min_or_none(xmin_values),
        "xmin_max": _max_or_none(xmin_values),
        "ymin_min": _min_or_none(ymin_values),
        "ymin_max": _max_or_none(ymin_values),
        "xmax_min": _min_or_none(xmax_values),
        "xmax_max": _max_or_none(xmax_values),
        "ymax_min": _min_or_none(ymax_values),
        "ymax_max": _max_or_none(ymax_values),
        "center_x_min": _min_or_none(center_x_values),
        "center_x_max": _max_or_none(center_x_values),
        "center_y_min": _min_or_none(center_y_values),
        "center_y_max": _max_or_none(center_y_values),
        "bottom_x_min": _min_or_none(bottom_x_values),
        "bottom_x_max": _max_or_none(bottom_x_values),
        "bottom_y_min": _min_or_none(bottom_y_values),
        "bottom_y_max": _max_or_none(bottom_y_values),
        "percentiles": {
            "center_x": _percentile_map(center_x_values),
            "center_y": _percentile_map(center_y_values),
            "bottom_x": _percentile_map(bottom_x_values),
            "bottom_y": _percentile_map(bottom_y_values),
        },
        "sample_tracks": list(track_counts.values())[:5],
        "valid_geometry_row_count": len(valid_rows),
    }


def suggest_line_config(summary: dict[str, Any], line_id: str = "line_main") -> dict[str, Any]:
    bottom_x = summary.get("percentiles", {}).get("bottom_x", {})
    bottom_y = summary.get("percentiles", {}).get("bottom_y", {})
    x1 = _round_coord(bottom_x.get("p10") or summary.get("bottom_x_min") or 0.0)
    x2 = _round_coord(bottom_x.get("p90") or summary.get("bottom_x_max") or x1)
    y = _round_coord(bottom_y.get("p50") or summary.get("bottom_y_min") or 0.0)
    return {
        "line_id": line_id,
        "name": "Suggested middle crossing line",
        "points": [[x1, y], [x2, y]],
        "target_classes": _target_classes(summary),
        "state": "confirmed",
    }


def suggest_roi_config(summary: dict[str, Any], roi_id: str = "roi_main") -> dict[str, Any]:
    bottom_x = summary.get("percentiles", {}).get("bottom_x", {})
    bottom_y = summary.get("percentiles", {}).get("bottom_y", {})
    x1 = _round_coord(bottom_x.get("p10") or summary.get("bottom_x_min") or 0.0)
    x2 = _round_coord(bottom_x.get("p90") or summary.get("bottom_x_max") or x1)
    y1 = _round_coord(bottom_y.get("p10") or summary.get("bottom_y_min") or 0.0)
    y2 = _round_coord(bottom_y.get("p90") or summary.get("bottom_y_max") or y1)
    return {
        "roi_id": roi_id,
        "name": "Suggested active-area ROI",
        "polygon": [[x1, y1], [x2, y1], [x2, y2], [x1, y2]],
        "point_mode": "bottom_center",
        "target_classes": _target_classes(summary),
    }


def suggest_event_rules_config(summary: dict[str, Any]) -> dict[str, Any]:
    target_classes = _target_classes(summary)
    person_targets = ["Person"] if "Person" in target_classes else []
    return {
        "long_stay": {
            "enabled": True,
            "min_duration_sec": 1.0,
            "target_classes": target_classes,
            "parameters": {"min_duration_sec": 1.0},
            "note": "Heuristic suggestion; tune after visual inspection.",
        },
        "crowd_warning": {
            "enabled": True,
            "min_count": 5,
            "target_classes": person_targets,
            "parameters": {"min_count": 5},
            "note": "Person-only if Person appears in tracks.csv.",
        },
        "wrong_direction": {
            "enabled": False,
            "target_classes": target_classes,
            "note": "Disabled by default because direction needs line semantics.",
        },
    }


def suggest_analytics_config(rows: list[dict[str, Any]], video_id: str = "demo") -> dict[str, Any]:
    summary = summarize_tracks(rows)
    return {
        "video_id": video_id,
        "summary": summary,
        "suggested_config": {
            "lines": [suggest_line_config(summary)],
            "rois": [suggest_roi_config(summary)],
            "event_rules": suggest_event_rules_config(summary),
        },
        "notes": [
            "Suggested config is heuristic.",
            "It is based on existing tracks.csv coordinate distribution.",
            "It does not validate real-world geometry.",
            "It still uses synthetic tracks unless tracks.csv came from a real tracker.",
            "Tune manually after visual inspection.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        rows = load_track_rows(args.tracks_csv)
        result = suggest_analytics_config(rows, video_id=args.video_id)
        result["suggested_config"]["lines"] = [
            suggest_line_config(result["summary"], line_id=args.line_id)
        ]
        result["suggested_config"]["rois"] = [suggest_roi_config(result["summary"], roi_id=args.roi_id)]
    except (FileNotFoundError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    indent = None if args.compact else 2
    text = json.dumps(result, ensure_ascii=False, indent=indent)
    print(text)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text + "\n", encoding="utf-8")
    return 0


def _percentile_map(values: list[float]) -> dict[str, float | None]:
    return {f"p{q}": _round_coord(percentile(values, q)) for q in PERCENTILE_KEYS}


def _target_classes(summary: dict[str, Any]) -> list[str]:
    return sorted(summary.get("class_counts", {}).keys())


def _min_or_none(values: list[float]) -> float | None:
    return _round_coord(min(values)) if values else None


def _max_or_none(values: list[float]) -> float | None:
    return _round_coord(max(values)) if values else None


def _maybe_int(value: float | None) -> int | float | None:
    if value is None:
        return None
    if float(value).is_integer():
        return int(value)
    return value


def _round_coord(value: float | None) -> float | None:
    if value is None:
        return None
    rounded = round(float(value), 2)
    if rounded.is_integer():
        return int(rounded)
    return rounded


if __name__ == "__main__":
    raise SystemExit(main())
