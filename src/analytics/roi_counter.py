"""ROI occupancy counter for synthetic video analytics tracks."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.analytics.geometry import bbox_bottom_center, bbox_center, point_in_polygon


SUPPORTED_POINT_MODES = {"bottom_center", "center"}


def count_roi_occupancy(
    track_rows: list[dict[str, Any]],
    roi_config: dict[str, Any],
    point_mode: str = "bottom_center",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    _validate_roi_config(roi_config)
    if point_mode not in SUPPORTED_POINT_MODES:
        raise ValueError("point_mode must be 'bottom_center' or 'center'")

    if roi_config.get("enabled", True) is False:
        return [], summarize_roi_counts([])

    roi_id = str(roi_config["id"])
    roi_name = str(roi_config.get("name", roi_id))
    polygon = [_to_point(point) for point in roi_config["polygon"]]
    target_classes = roi_config.get("target_classes")
    target_class_set = set(target_classes) if target_classes else None

    grouped: dict[tuple[Any, Any, str], dict[str, Any]] = {}

    for row in track_rows:
        if not _is_confirmed(row):
            continue
        if target_class_set is not None and row.get("class_name") not in target_class_set:
            continue

        point = _row_point(row, point_mode)
        if not point_in_polygon(point, polygon, include_boundary=True):
            continue

        key = (row.get("frame_index"), row.get("timestamp_sec"), row.get("class_name"))
        if key not in grouped:
            grouped[key] = {
                "video_id": row.get("video_id", ""),
                "frame_index": row.get("frame_index"),
                "timestamp_sec": row.get("timestamp_sec"),
                "roi_id": roi_id,
                "roi_name": roi_name,
                "class_name": row.get("class_name"),
                "object_count": 0,
                "unique_track_count": 0,
                "_track_ids": set(),
            }

        grouped[key]["object_count"] += 1
        grouped[key]["_track_ids"].add(row.get("track_id"))
        grouped[key]["unique_track_count"] = len(grouped[key]["_track_ids"])

    counts = [
        _public_count_row(row)
        for row in sorted(
            grouped.values(),
            key=lambda item: (
                item.get("frame_index", 0),
                item.get("timestamp_sec", 0.0),
                str(item.get("class_name", "")),
            ),
        )
    ]
    summary = summarize_roi_counts(list(grouped.values()))
    return counts, summary


def summarize_roi_counts(roi_frame_counts: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize observed frame-class rows without zero-filling the full timeline."""

    if not roi_frame_counts:
        return {
            "roi_id": "",
            "roi_name": "",
            "frames_observed": 0,
            "max_count": 0,
            "avg_count": 0.0,
            "by_class": {},
        }

    frames = {row.get("frame_index") for row in roi_frame_counts}
    object_counts = [int(row.get("object_count", 0)) for row in roi_frame_counts]
    by_class: dict[str, dict[str, Any]] = {}

    for class_name, rows in _group_rows_by_class(roi_frame_counts).items():
        class_counts = [int(row.get("object_count", 0)) for row in rows]
        unique_tracks: set[Any] = set()
        for row in rows:
            if "_track_ids" in row:
                unique_tracks.update(row["_track_ids"])
            else:
                unique_tracks.update(range(int(row.get("unique_track_count", 0))))

        by_class[class_name] = {
            "max_count": max(class_counts),
            "avg_count": sum(class_counts) / len(class_counts),
            "unique_tracks": len(unique_tracks),
        }

    return {
        "roi_id": str(roi_frame_counts[0].get("roi_id", "")),
        "roi_name": str(roi_frame_counts[0].get("roi_name", "")),
        "frames_observed": len(frames),
        "max_count": max(object_counts),
        "avg_count": sum(object_counts) / len(object_counts),
        "by_class": by_class,
    }


def _validate_roi_config(roi_config: dict[str, Any]) -> None:
    if not roi_config.get("id"):
        raise ValueError("roi_config.id is required")
    polygon = roi_config.get("polygon")
    if polygon is None:
        raise ValueError("roi_config.polygon is required")
    if len(polygon) < 3:
        raise ValueError("roi_config.polygon must contain at least 3 points")


def _is_confirmed(row: dict[str, Any]) -> bool:
    return row.get("state", "confirmed") == "confirmed"


def _row_point(row: dict[str, Any], point_mode: str) -> tuple[float, float]:
    bbox = (
        float(row["xmin"]),
        float(row["ymin"]),
        float(row["xmax"]),
        float(row["ymax"]),
    )
    if point_mode == "bottom_center":
        return bbox_bottom_center(*bbox)
    if point_mode == "center":
        return bbox_center(*bbox)
    raise ValueError("point_mode must be 'bottom_center' or 'center'")


def _to_point(value: Any) -> tuple[float, float]:
    return (float(value[0]), float(value[1]))


def _public_count_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "video_id": row.get("video_id"),
        "frame_index": row.get("frame_index"),
        "timestamp_sec": row.get("timestamp_sec"),
        "roi_id": row.get("roi_id"),
        "roi_name": row.get("roi_name"),
        "class_name": row.get("class_name"),
        "object_count": row.get("object_count"),
        "unique_track_count": row.get("unique_track_count"),
    }


def _group_rows_by_class(
    rows: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("class_name", ""))].append(row)
    return dict(grouped)
