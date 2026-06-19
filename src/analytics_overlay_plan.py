"""Build an overlay plan from existing tracks and analytics config.

This module validates suggested line and ROI geometry against tracks.csv
coordinate distributions. It does not read video frames, run YOLO, run a
tracker, render video, or create tracked video.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PERCENTILE_KEYS = (10, 25, 50, 75, 90)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a JSON overlay plan from tracks.csv and analytics config."
    )
    parser.add_argument("--tracks-csv", required=True, type=Path)
    parser.add_argument("--config-json", required=True, type=Path)
    parser.add_argument("--video-id", default="demo")
    parser.add_argument("--output-json", type=Path)
    return parser.parse_args(argv)


def load_csv_rows(path: str | Path) -> list[dict[str, str]]:
    csv_path = _existing_file(path, "tracks_csv")
    with csv_path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def load_json(path: str | Path) -> dict[str, Any]:
    json_path = _existing_file(path, "config_json")
    with json_path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"config_json must contain a JSON object: {json_path}")
    return data


def extract_analytics_config(config_json: dict[str, Any]) -> dict[str, Any]:
    candidate = config_json.get("suggested_config", config_json)
    if not isinstance(candidate, dict):
        raise ValueError("analytics config must be a JSON object")

    lines = candidate.get("lines", [])
    rois = candidate.get("rois", [])
    event_rules = candidate.get("event_rules", {})
    if lines is None:
        lines = []
    if rois is None:
        rois = []
    if event_rules is None:
        event_rules = {}
    if not isinstance(lines, list):
        raise ValueError("analytics config lines must be a list")
    if not isinstance(rois, list):
        raise ValueError("analytics config rois must be a list")
    if not isinstance(event_rules, dict):
        raise ValueError("analytics config event_rules must be an object")

    return {"lines": list(lines), "rois": list(rois), "event_rules": event_rules}


def parse_float(value: Any, default: float | None = None) -> float | None:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def bbox_center(row: dict[str, Any]) -> tuple[float, float] | None:
    xmin = parse_float(row.get("xmin"))
    ymin = parse_float(row.get("ymin"))
    xmax = parse_float(row.get("xmax"))
    ymax = parse_float(row.get("ymax"))
    if xmin is None or ymin is None or xmax is None or ymax is None:
        return None
    return ((xmin + xmax) / 2.0, (ymin + ymax) / 2.0)


def bottom_center(row: dict[str, Any]) -> tuple[float, float] | None:
    xmin = parse_float(row.get("xmin"))
    xmax = parse_float(row.get("xmax"))
    ymax = parse_float(row.get("ymax"))
    if xmin is None or xmax is None or ymax is None:
        return None
    return ((xmin + xmax) / 2.0, ymax)


def percentile(values: list[float] | tuple[float, ...], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    bounded_q = min(100.0, max(0.0, float(q)))
    position = (len(ordered) - 1) * bounded_q / 100.0
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def summarize_coordinate_space(track_rows: list[dict[str, Any]]) -> dict[str, Any]:
    track_ids: set[str] = set()
    class_counts: Counter[str] = Counter()
    frames: list[float] = []
    xmin_values: list[float] = []
    ymin_values: list[float] = []
    xmax_values: list[float] = []
    ymax_values: list[float] = []
    center_x_values: list[float] = []
    center_y_values: list[float] = []
    bottom_x_values: list[float] = []
    bottom_y_values: list[float] = []

    for row in track_rows:
        track_id = str(row.get("track_id") or "")
        if track_id:
            track_ids.add(track_id)
        class_counts[str(row.get("class_name") or "unknown")] += 1

        frame = parse_float(row.get("frame_index"))
        xmin = parse_float(row.get("xmin"))
        ymin = parse_float(row.get("ymin"))
        xmax = parse_float(row.get("xmax"))
        ymax = parse_float(row.get("ymax"))
        center = bbox_center(row)
        bottom = bottom_center(row)

        if frame is not None:
            frames.append(frame)
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

    xmax_max = _max_or_none(xmax_values)
    ymax_max = _max_or_none(ymax_values)
    return {
        "row_count": len(track_rows),
        "track_count": len(track_ids),
        "class_counts": dict(sorted(class_counts.items())),
        "frame_min": _maybe_int(_min_or_none(frames)),
        "frame_max": _maybe_int(_max_or_none(frames)),
        "bbox_bounds": {
            "xmin_min": _min_or_none(xmin_values),
            "ymin_min": _min_or_none(ymin_values),
            "xmax_max": xmax_max,
            "ymax_max": ymax_max,
        },
        "center_bounds": {
            "x_min": _min_or_none(center_x_values),
            "x_max": _max_or_none(center_x_values),
            "y_min": _min_or_none(center_y_values),
            "y_max": _max_or_none(center_y_values),
        },
        "bottom_bounds": {
            "x_min": _min_or_none(bottom_x_values),
            "x_max": _max_or_none(bottom_x_values),
            "y_min": _min_or_none(bottom_y_values),
            "y_max": _max_or_none(bottom_y_values),
        },
        "percentiles": {
            "center_x": _percentile_map(center_x_values),
            "center_y": _percentile_map(center_y_values),
            "bottom_x": _percentile_map(bottom_x_values),
            "bottom_y": _percentile_map(bottom_y_values),
        },
        "inferred_frame_bounds": {
            "width_hint": math.ceil(xmax_max) if xmax_max is not None else 0,
            "height_hint": math.ceil(ymax_max) if ymax_max is not None else 0,
            "note": "inferred from detection boxes, not actual video metadata",
        },
    }


def point_in_bounds(
    point: tuple[float, float] | list[float],
    bounds: dict[str, Any],
    margin: float = 0.0,
) -> bool:
    x, y = float(point[0]), float(point[1])
    x_min = _bound_value(bounds, "x_min", "xmin_min")
    x_max = _bound_value(bounds, "x_max", "xmax_max")
    y_min = _bound_value(bounds, "y_min", "ymin_min")
    y_max = _bound_value(bounds, "y_max", "ymax_max")
    if None in (x_min, x_max, y_min, y_max):
        return False
    x_margin = (float(x_max) - float(x_min)) * margin
    y_margin = (float(y_max) - float(y_min)) * margin
    return (
        float(x_min) - x_margin <= x <= float(x_max) + x_margin
        and float(y_min) - y_margin <= y <= float(y_max) + y_margin
    )


def line_bounds(line: dict[str, Any]) -> dict[str, float]:
    points = line.get("points", [])
    if len(points) != 2:
        raise ValueError("line points must contain exactly two points")
    x_values = [float(points[0][0]), float(points[1][0])]
    y_values = [float(points[0][1]), float(points[1][1])]
    return {"x_min": min(x_values), "x_max": max(x_values), "y_min": min(y_values), "y_max": max(y_values)}


def polygon_bounds(polygon: list[Any]) -> dict[str, float]:
    if len(polygon) < 3:
        raise ValueError("ROI polygon must contain at least three points")
    x_values = [float(point[0]) for point in polygon]
    y_values = [float(point[1]) for point in polygon]
    return {"x_min": min(x_values), "x_max": max(x_values), "y_min": min(y_values), "y_max": max(y_values)}


def validate_line(line_config: dict[str, Any], coordinate_summary: dict[str, Any]) -> dict[str, Any]:
    points = line_config.get("points", [])
    bounds = line_bounds(line_config)
    bbox_bounds = coordinate_summary.get("bbox_bounds", {})
    bottom_bounds = coordinate_summary.get("bottom_bounds", {})
    percentiles = coordinate_summary.get("percentiles", {})
    orientation = _line_orientation(points)
    within_bbox = all(point_in_bounds(point, bbox_bounds) for point in points)
    within_bottom = all(point_in_bounds(point, bottom_bounds, margin=0.05) for point in points)

    notes: list[str] = []
    bottom_y_p50 = percentiles.get("bottom_y", {}).get("p50")
    bottom_y_p10 = percentiles.get("bottom_y", {}).get("p10")
    bottom_y_p90 = percentiles.get("bottom_y", {}).get("p90")
    bottom_x_p10 = percentiles.get("bottom_x", {}).get("p10")
    bottom_x_p90 = percentiles.get("bottom_x", {}).get("p90")
    if orientation == "horizontal" and _between(bounds["y_min"], bottom_y_p10, bottom_y_p90):
        notes.append("line_y_within_bottom_p10_to_p90")
    if orientation == "horizontal" and bottom_y_p50 is not None and abs(bounds["y_min"] - bottom_y_p50) <= _range_size(bottom_bounds, "y") * 0.1:
        notes.append("line_y_near_bottom_p50")
    if bottom_x_p10 is not None and bottom_x_p90 is not None and bounds["x_min"] <= bottom_x_p10 and bounds["x_max"] >= bottom_x_p90:
        notes.append("line_spans_bottom_x_p10_to_p90")
    if not within_bottom:
        notes.append("line_outside_detected_bottom_bounds")
    if not within_bbox:
        notes.append("line_outside_detected_bbox_bounds")

    return {
        "line_id": str(line_config.get("line_id") or line_config.get("id") or ""),
        "points": points,
        "bounds": bounds,
        "within_bbox_bounds": within_bbox,
        "within_bottom_bounds": within_bottom,
        "orientation": orientation,
        "position_notes": notes,
        "recommendation": "ok" if within_bbox and within_bottom else "review",
    }


def validate_roi(roi_config: dict[str, Any], coordinate_summary: dict[str, Any]) -> dict[str, Any]:
    polygon = roi_config.get("polygon", [])
    bounds = polygon_bounds(polygon)
    bbox_bounds = coordinate_summary.get("bbox_bounds", {})
    center_region = _percentile_region(coordinate_summary, "center")
    bottom_region = _percentile_region(coordinate_summary, "bottom")
    within_bbox = all(point_in_bounds(point, bbox_bounds) for point in polygon)
    covers_center = _bounds_intersect(bounds, center_region)
    covers_bottom = _bounds_intersect(bounds, bottom_region)

    notes: list[str] = []
    if covers_center:
        notes.append("roi_intersects_center_p10_to_p90")
    else:
        notes.append("roi_outside_center_distribution")
    if covers_bottom:
        notes.append("roi_intersects_bottom_p10_to_p90")
    else:
        notes.append("roi_outside_bottom_distribution")
    if not within_bbox:
        notes.append("roi_outside_detected_bbox_bounds")

    return {
        "roi_id": str(roi_config.get("roi_id") or roi_config.get("id") or ""),
        "polygon": polygon,
        "bounds": bounds,
        "within_bbox_bounds": within_bbox,
        "covers_center_distribution": covers_center,
        "covers_bottom_distribution": covers_bottom,
        "point_mode": roi_config.get("point_mode", "bottom_center"),
        "position_notes": notes,
        "recommendation": "ok" if within_bbox and (covers_center or covers_bottom) else "review",
    }


def build_overlay_plan(
    tracks_csv: str | Path,
    config_json: dict[str, Any],
    video_id: str = "demo",
) -> dict[str, Any]:
    tracks_path = _existing_file(tracks_csv, "tracks_csv")
    track_rows = load_csv_rows(tracks_path)
    analytics_config = extract_analytics_config(config_json)
    coordinate_summary = summarize_coordinate_space(track_rows)
    line_plans = [
        validate_line(line_config, coordinate_summary)
        for line_config in analytics_config.get("lines", [])
    ]
    roi_plans = [
        validate_roi(roi_config, coordinate_summary)
        for roi_config in analytics_config.get("rois", [])
    ]
    event_rules = analytics_config.get("event_rules", {})
    recommendations = _overlay_recommendations(line_plans, roi_plans)

    return {
        "video_id": video_id,
        "mode": "analytics_overlay_plan",
        "tracks_csv": str(tracks_path),
        "config_source": "suggested_config" if "suggested_config" in config_json else "direct_config",
        "coordinate_summary": coordinate_summary,
        "line_plans": line_plans,
        "roi_plans": roi_plans,
        "event_rules_summary": {
            "rule_count": len(event_rules),
            "rule_names": sorted(event_rules.keys()),
        },
        "overlay_recommendations": recommendations,
        "notes": [
            "Does not render video.",
            "Does not validate true video frame size.",
            "Inferred frame bounds come from tracks.csv bbox max coordinates.",
            "Synthetic tracks do not represent real MOT quality.",
            "Manually inspect overlay before using metrics as final.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        _existing_file(args.tracks_csv, "tracks_csv")
        config_json = load_json(args.config_json)
        plan = build_overlay_plan(args.tracks_csv, config_json, video_id=args.video_id)
        plan["config_json"] = str(args.config_json.expanduser().resolve())
    except (FileNotFoundError, ValueError, KeyError, IndexError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    text = json.dumps(plan, ensure_ascii=False, indent=2)
    print(text)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text + "\n", encoding="utf-8")
    return 0


def _overlay_recommendations(
    line_plans: list[dict[str, Any]],
    roi_plans: list[dict[str, Any]],
) -> list[str]:
    recommendations = [
        "draw sampled bbox centers or bottom centers",
        "draw line segments with line_id labels",
        "draw ROI polygons with roi_id labels",
    ]
    if any(plan.get("recommendation") == "review" for plan in line_plans + roi_plans):
        recommendations.append("review geometry before relying on analytics metrics")
    return recommendations


def _line_orientation(points: list[Any]) -> str:
    x1, y1 = float(points[0][0]), float(points[0][1])
    x2, y2 = float(points[1][0]), float(points[1][1])
    if abs(y1 - y2) <= 1e-6:
        return "horizontal"
    if abs(x1 - x2) <= 1e-6:
        return "vertical"
    return "diagonal"


def _percentile_region(summary: dict[str, Any], prefix: str) -> dict[str, float | None]:
    percentiles = summary.get("percentiles", {})
    return {
        "x_min": percentiles.get(f"{prefix}_x", {}).get("p10"),
        "x_max": percentiles.get(f"{prefix}_x", {}).get("p90"),
        "y_min": percentiles.get(f"{prefix}_y", {}).get("p10"),
        "y_max": percentiles.get(f"{prefix}_y", {}).get("p90"),
    }


def _bounds_intersect(first: dict[str, Any], second: dict[str, Any]) -> bool:
    if any(second.get(key) is None for key in ("x_min", "x_max", "y_min", "y_max")):
        return False
    return not (
        float(first["x_max"]) < float(second["x_min"])
        or float(first["x_min"]) > float(second["x_max"])
        or float(first["y_max"]) < float(second["y_min"])
        or float(first["y_min"]) > float(second["y_max"])
    )


def _between(value: float, lower: Any, upper: Any) -> bool:
    if lower is None or upper is None:
        return False
    return float(lower) <= float(value) <= float(upper)


def _range_size(bounds: dict[str, Any], axis: str) -> float:
    min_value = bounds.get(f"{axis}_min")
    max_value = bounds.get(f"{axis}_max")
    if min_value is None or max_value is None:
        return 0.0
    return max(0.0, float(max_value) - float(min_value))


def _bound_value(bounds: dict[str, Any], primary: str, fallback: str) -> Any:
    return bounds.get(primary, bounds.get(fallback))


def _percentile_map(values: list[float]) -> dict[str, float | None]:
    return {f"p{q}": _round_number(percentile(values, q)) for q in PERCENTILE_KEYS}


def _min_or_none(values: list[float]) -> float | None:
    return _round_number(min(values)) if values else None


def _max_or_none(values: list[float]) -> float | None:
    return _round_number(max(values)) if values else None


def _maybe_int(value: float | None) -> int | float | None:
    if value is None:
        return None
    if float(value).is_integer():
        return int(value)
    return value


def _round_number(value: float | None) -> float | None:
    if value is None:
        return None
    rounded = round(float(value), 2)
    if rounded.is_integer():
        return int(rounded)
    return rounded


def _existing_file(path: str | Path, name: str) -> Path:
    file_path = Path(path).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"{name} not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"{name} must be a file: {file_path}")
    return file_path


if __name__ == "__main__":
    raise SystemExit(main())
