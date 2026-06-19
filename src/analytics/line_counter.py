"""Line crossing counter for synthetic video analytics tracks."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.analytics.geometry import crossing_direction


VEHICLE_CLASSES = {"Bus", "Car", "Motorcycle", "Truck", "mini-truck"}
PEDESTRIAN_CLASSES = {"Person"}


def count_line_crossings(
    track_rows: list[dict[str, Any]],
    line_config: dict[str, Any],
    min_displacement_px: float = 0.0,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    line_id = str(line_config.get("id", ""))
    line_points = line_config.get("points", [])
    if len(line_points) != 2:
        raise ValueError("line_config.points must contain exactly two points")

    if line_config.get("enabled", True) is False:
        return [], summarize_count_events([])

    line_start = _to_point(line_points[0])
    line_end = _to_point(line_points[1])
    directions = line_config.get("directions", {})
    positive_direction = str(directions.get("positive", "positive"))
    negative_direction = str(directions.get("negative", "negative"))
    target_classes = line_config.get("target_classes")
    target_class_set = set(target_classes) if target_classes else None

    events: list[dict[str, Any]] = []
    seen_keys: set[tuple[Any, str, Any, str]] = set()

    for track_id, rows in _group_rows_by_track(track_rows).items():
        sorted_rows = sorted(
            rows,
            key=lambda row: (
                row.get("frame_index", 0),
                row.get("timestamp_sec", 0.0),
            ),
        )

        for prev_row, curr_row in zip(sorted_rows, sorted_rows[1:]):
            if not _is_confirmed(prev_row) or not _is_confirmed(curr_row):
                continue
            if target_class_set is not None and curr_row.get("class_name") not in target_class_set:
                continue

            direction = crossing_direction(
                _row_point(prev_row),
                _row_point(curr_row),
                line_start,
                line_end,
                positive_label=positive_direction,
                negative_label=negative_direction,
                min_displacement_px=min_displacement_px,
            )
            if direction is None:
                continue

            video_id = curr_row.get("video_id", prev_row.get("video_id", ""))
            dedupe_key = (video_id, line_id, track_id, direction)
            if dedupe_key in seen_keys:
                continue

            seen_keys.add(dedupe_key)
            events.append(
                {
                    "video_id": video_id,
                    "line_id": line_id,
                    "frame_index": curr_row.get("frame_index"),
                    "timestamp_sec": curr_row.get("timestamp_sec"),
                    "track_id": track_id,
                    "class_id": curr_row.get("class_id"),
                    "class_name": curr_row.get("class_name"),
                    "direction": direction,
                    "center_x": curr_row.get("center_x"),
                    "center_y": curr_row.get("center_y"),
                }
            )

    return events, summarize_count_events(events)


def summarize_count_events(count_events: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {
        "total_count": len(count_events),
        "by_direction": {},
        "by_class": {},
        "by_line": {},
        "vehicle_total": 0,
        "pedestrian_total": 0,
    }

    for event in count_events:
        direction = event.get("direction")
        class_name = event.get("class_name")
        line_id = event.get("line_id")

        _increment(summary["by_direction"], direction)
        _increment(summary["by_class"], class_name)
        _increment(summary["by_line"], line_id)

        if class_name in VEHICLE_CLASSES:
            summary["vehicle_total"] += 1
        elif class_name in PEDESTRIAN_CLASSES:
            summary["pedestrian_total"] += 1

    return summary


def _group_rows_by_track(
    track_rows: list[dict[str, Any]],
) -> dict[Any, list[dict[str, Any]]]:
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in track_rows:
        grouped[row.get("track_id")].append(row)
    return dict(grouped)


def _is_confirmed(row: dict[str, Any]) -> bool:
    return row.get("state", "confirmed") == "confirmed"


def _row_point(row: dict[str, Any]) -> tuple[float, float]:
    return (float(row["center_x"]), float(row["center_y"]))


def _to_point(value: Any) -> tuple[float, float]:
    return (float(value[0]), float(value[1]))


def _increment(counter: dict[Any, int], key: Any) -> None:
    if key is None:
        return
    counter[key] = counter.get(key, 0) + 1
