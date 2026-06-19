"""Rule-based events for synthetic video analytics outputs."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.analytics.geometry import euclidean_distance


def detect_crowd_warning(
    roi_frame_counts: list[dict[str, Any]],
    rule_config: dict[str, Any],
) -> list[dict[str, Any]]:
    if rule_config.get("enabled", True) is False:
        return []

    params = rule_config.get("parameters", {})
    min_count = int(params.get("min_count", 0))
    min_duration_sec = float(params.get("min_duration_sec", 0.0))
    roi_id = rule_config.get("roi_id")
    target_classes = _target_classes(rule_config)
    events: list[dict[str, Any]] = []

    for (_video_id, _roi_id, _class_name), rows in _group_rows(
        _filter_roi_count_rows(roi_frame_counts, roi_id, target_classes),
        ("video_id", "roi_id", "class_name"),
    ).items():
        sorted_rows = _sort_rows(rows)
        segment: list[dict[str, Any]] = []

        for row in sorted_rows:
            if int(row.get("object_count", 0)) >= min_count:
                segment.append(row)
                continue

            event = _crowd_event_from_segment(segment, rule_config, min_count, min_duration_sec)
            if event is not None:
                events.append(event)
                segment = []
                break
            segment = []

        if segment:
            event = _crowd_event_from_segment(segment, rule_config, min_count, min_duration_sec)
            if event is not None:
                events.append(event)

    return events


def detect_long_stay(
    track_rows: list[dict[str, Any]],
    rule_config: dict[str, Any],
) -> list[dict[str, Any]]:
    if rule_config.get("enabled", True) is False:
        return []

    params = rule_config.get("parameters", {})
    min_duration_sec = float(params.get("min_duration_sec", 0.0))
    roi_id = rule_config.get("roi_id")
    target_classes = _target_classes(rule_config)
    events: list[dict[str, Any]] = []

    filtered_rows = [
        row
        for row in track_rows
        if row.get("roi_id") == roi_id and _class_matches(row, target_classes)
    ]

    for (_video_id, _track_id, _roi_id), rows in _group_rows(
        filtered_rows,
        ("video_id", "track_id", "roi_id"),
    ).items():
        sorted_rows = _sort_rows(rows)
        if not sorted_rows:
            continue

        start_row = sorted_rows[0]
        end_row = sorted_rows[-1]
        start_time = float(start_row.get("timestamp_sec", 0.0))
        end_time = float(end_row.get("timestamp_sec", 0.0))
        duration_sec = end_time - start_time
        if duration_sec < min_duration_sec:
            continue

        events.append(
            _event(
                event_type=rule_config.get("event_type", "long_stay"),
                video_id=end_row.get("video_id", ""),
                frame_index=end_row.get("frame_index"),
                timestamp_sec=end_row.get("timestamp_sec"),
                track_id=end_row.get("track_id"),
                class_name=end_row.get("class_name"),
                roi_id=roi_id,
                line_id=None,
                severity=rule_config.get("severity", "warning"),
                evidence={
                    "duration_sec": duration_sec,
                    "min_duration_sec": min_duration_sec,
                    "start_time_sec": start_time,
                    "end_time_sec": end_time,
                },
            )
        )

    return events


def detect_wrong_direction(
    track_rows: list[dict[str, Any]],
    rule_config: dict[str, Any],
) -> list[dict[str, Any]]:
    if rule_config.get("enabled", True) is False:
        return []

    params = rule_config.get("parameters", {})
    expected_direction = params.get("expected_direction")
    min_track_length = int(params.get("min_track_length", 0))
    min_displacement_px = float(params.get("min_displacement_px", 0.0))
    line_id = rule_config.get("line_id")
    target_classes = _target_classes(rule_config)
    events: list[dict[str, Any]] = []

    filtered_rows = [
        row
        for row in track_rows
        if row.get("line_id") == line_id and _class_matches(row, target_classes)
    ]

    for (_video_id, _track_id, _line_id), rows in _group_rows(
        filtered_rows,
        ("video_id", "track_id", "line_id"),
    ).items():
        sorted_rows = _sort_rows(rows)
        if len(sorted_rows) < min_track_length:
            continue

        actual_direction = _last_non_empty_value(sorted_rows, "direction")
        if actual_direction is None or actual_direction == expected_direction:
            continue

        first_row = sorted_rows[0]
        end_row = sorted_rows[-1]
        displacement_px = euclidean_distance(_row_center(first_row), _row_center(end_row))
        if displacement_px < min_displacement_px:
            continue

        events.append(
            _event(
                event_type=rule_config.get("event_type", "wrong_direction"),
                video_id=end_row.get("video_id", ""),
                frame_index=end_row.get("frame_index"),
                timestamp_sec=end_row.get("timestamp_sec"),
                track_id=end_row.get("track_id"),
                class_name=end_row.get("class_name"),
                roi_id=None,
                line_id=line_id,
                severity=rule_config.get("severity", "warning"),
                evidence={
                    "expected_direction": expected_direction,
                    "actual_direction": actual_direction,
                    "track_length": len(sorted_rows),
                    "displacement_px": displacement_px,
                    "min_displacement_px": min_displacement_px,
                },
            )
        )

    return events


def summarize_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {
        "total_events": len(events),
        "by_type": {},
        "by_severity": {},
        "by_roi": {},
        "by_line": {},
    }

    for event in events:
        _increment(summary["by_type"], event.get("event_type"))
        _increment(summary["by_severity"], event.get("severity"))
        _increment(summary["by_roi"], event.get("roi_id"))
        _increment(summary["by_line"], event.get("line_id"))

    return summary


def _crowd_event_from_segment(
    segment: list[dict[str, Any]],
    rule_config: dict[str, Any],
    min_count: int,
    min_duration_sec: float,
) -> dict[str, Any] | None:
    if not segment:
        return None

    start_row = segment[0]
    end_row = segment[-1]
    start_time = float(start_row.get("timestamp_sec", 0.0))
    end_time = float(end_row.get("timestamp_sec", 0.0))
    duration_sec = end_time - start_time
    if duration_sec < min_duration_sec:
        return None

    return _event(
        event_type=rule_config.get("event_type", "crowd_warning"),
        video_id=end_row.get("video_id", ""),
        frame_index=end_row.get("frame_index"),
        timestamp_sec=end_row.get("timestamp_sec"),
        track_id=None,
        class_name=end_row.get("class_name"),
        roi_id=end_row.get("roi_id"),
        line_id=None,
        severity=rule_config.get("severity", "warning"),
        evidence={
            "max_count": max(int(row.get("object_count", 0)) for row in segment),
            "min_count": min_count,
            "duration_sec": duration_sec,
            "min_duration_sec": min_duration_sec,
        },
    )


def _event(
    event_type: Any,
    video_id: Any,
    frame_index: Any,
    timestamp_sec: Any,
    track_id: Any,
    class_name: Any,
    roi_id: Any,
    line_id: Any,
    severity: Any,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    target = track_id if track_id is not None else roi_id if roi_id is not None else line_id
    return {
        "event_id": f"{event_type}_{video_id}_{target}_{frame_index}",
        "event_type": event_type,
        "video_id": video_id,
        "frame_index": frame_index,
        "timestamp_sec": timestamp_sec,
        "track_id": track_id,
        "class_name": class_name,
        "roi_id": roi_id,
        "line_id": line_id,
        "severity": severity,
        "evidence": evidence,
    }


def _filter_roi_count_rows(
    rows: list[dict[str, Any]],
    roi_id: Any,
    target_classes: set[Any] | None,
) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if row.get("roi_id") == roi_id and _class_matches(row, target_classes)
    ]


def _target_classes(rule_config: dict[str, Any]) -> set[Any] | None:
    target_classes = rule_config.get("target_classes")
    return set(target_classes) if target_classes else None


def _class_matches(row: dict[str, Any], target_classes: set[Any] | None) -> bool:
    return target_classes is None or row.get("class_name") in target_classes


def _group_rows(
    rows: list[dict[str, Any]],
    fields: tuple[str, ...],
) -> dict[tuple[Any, ...], list[dict[str, Any]]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row.get(field) for field in fields)].append(row)
    return dict(grouped)


def _sort_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            row.get("timestamp_sec", 0.0),
            row.get("frame_index", 0),
        ),
    )


def _last_non_empty_value(rows: list[dict[str, Any]], field: str) -> Any:
    for row in reversed(rows):
        value = row.get(field)
        if value not in (None, ""):
            return value
    return None


def _row_center(row: dict[str, Any]) -> tuple[float, float]:
    return (float(row.get("center_x", 0.0)), float(row.get("center_y", 0.0)))


def _increment(counter: dict[Any, int], key: Any) -> None:
    if key is None:
        return
    counter[key] = counter.get(key, 0) + 1
