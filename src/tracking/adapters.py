"""Tracking adapter contracts for video analytics runtime.

This module defines tracking adapter contracts. ByteTrack/DeepSORT are
placeholders in v0.9.0 Step 2. No external tracker dependency is imported here.
"""

from __future__ import annotations

from typing import Any

from src.analytics.geometry import bbox_center, bbox_size_and_area


BYTETRACK_DISCOVERY_NOTE = (
    "ByteTrackAdapter is not implemented yet; real ByteTrack dependency is not "
    "integrated yet. See docs/bytetrack_integration_plan.md and "
    "src/tracking/bytetrack_discovery.py."
)
DEEPSORT_DISCOVERY_NOTE = (
    "DeepSORTAdapter is not implemented yet; real DeepSORT dependency is not "
    "integrated yet. See docs/bytetrack_integration_plan.md and "
    "src/tracking/bytetrack_discovery.py."
)


class BaseTrackerAdapter:
    def __init__(self, tracker_type: str) -> None:
        self.tracker_type = tracker_type

    def update(
        self,
        detections: list[dict[str, Any]],
        frame_index: int | None = None,
        timestamp_sec: float | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError("Tracker adapter update must be implemented by subclasses")


class SyntheticTrackerAdapter(BaseTrackerAdapter):
    def __init__(self) -> None:
        super().__init__("synthetic")

    def update(
        self,
        detections: list[dict[str, Any]],
        frame_index: int | None = None,
        timestamp_sec: float | None = None,
    ) -> list[dict[str, Any]]:
        tracker_inputs = detections_to_tracker_input(detections)
        outputs: list[dict[str, Any]] = []
        for row_index, item in enumerate(tracker_inputs, start=1):
            detection_id = item.get("detection_id")
            track_id = detection_id or f"synthetic_{row_index}"
            outputs.append(
                {
                    "video_id": item.get("video_id", ""),
                    "track_id": track_id,
                    "bbox": item["bbox"],
                    "class_id": item.get("class_id"),
                    "class_name": item.get("class_name", ""),
                    "confidence": item.get("confidence"),
                    "frame_index": frame_index
                    if frame_index is not None
                    else item.get("frame_index"),
                    "timestamp_sec": timestamp_sec
                    if timestamp_sec is not None
                    else item.get("timestamp_sec"),
                    "state": "confirmed",
                }
            )
        return tracker_outputs_to_track_rows(outputs, tracker_name=self.tracker_type)


class ByteTrackAdapter(BaseTrackerAdapter):
    def __init__(self, **_: Any) -> None:
        super().__init__("bytetrack")

    def update(
        self,
        detections: list[dict[str, Any]],
        frame_index: int | None = None,
        timestamp_sec: float | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError(BYTETRACK_DISCOVERY_NOTE)


class DeepSORTAdapter(BaseTrackerAdapter):
    def __init__(self, **_: Any) -> None:
        super().__init__("deepsort")

    def update(
        self,
        detections: list[dict[str, Any]],
        frame_index: int | None = None,
        timestamp_sec: float | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError(DEEPSORT_DISCOVERY_NOTE)


def create_tracker_adapter(tracker_type: str, **kwargs: Any) -> BaseTrackerAdapter:
    normalized = tracker_type.lower()
    if normalized == "synthetic":
        return SyntheticTrackerAdapter()
    if normalized == "bytetrack":
        return ByteTrackAdapter(**kwargs)
    if normalized == "deepsort":
        return DeepSORTAdapter(**kwargs)
    raise ValueError(f"Unsupported tracker_type: {tracker_type}")


def detections_to_tracker_input(detection_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tracker_inputs: list[dict[str, Any]] = []
    for row in detection_rows:
        tracker_inputs.append(
            {
                "bbox": [
                    float(row["xmin"]),
                    float(row["ymin"]),
                    float(row["xmax"]),
                    float(row["ymax"]),
                ],
                "confidence": _to_float_if_possible(row.get("confidence")),
                "class_id": _to_int_if_possible(row.get("class_id")),
                "class_name": row.get("class_name", ""),
                "frame_index": _to_int_if_possible(row.get("frame_index")),
                "timestamp_sec": _to_float_if_possible(row.get("timestamp_sec")),
                "detection_id": row.get("detection_id"),
                "video_id": row.get("video_id", ""),
            }
        )
    return tracker_inputs


def tracker_outputs_to_track_rows(
    tracker_outputs: list[dict[str, Any]],
    video_id: str | None = None,
    tracker_name: str = "synthetic",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for output in tracker_outputs:
        xmin, ymin, xmax, ymax = [float(value) for value in output["bbox"]]
        center_x, center_y = bbox_center(xmin, ymin, xmax, ymax)
        box_width, box_height, box_area = bbox_size_and_area(xmin, ymin, xmax, ymax)
        rows.append(
            {
                "video_id": video_id if video_id is not None else output.get("video_id", ""),
                "frame_index": output.get("frame_index"),
                "timestamp_sec": output.get("timestamp_sec"),
                "track_id": output.get("track_id"),
                "class_id": output.get("class_id"),
                "class_name": output.get("class_name", ""),
                "confidence": output.get("confidence"),
                "xmin": xmin,
                "ymin": ymin,
                "xmax": xmax,
                "ymax": ymax,
                "center_x": center_x,
                "center_y": center_y,
                "box_width": box_width,
                "box_height": box_height,
                "box_area": box_area,
                "state": output.get("state", "confirmed"),
                "tracker_name": tracker_name,
            }
        )
    return rows


def _to_int_if_possible(value: Any) -> Any:
    if value in (None, ""):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def _to_float_if_possible(value: Any) -> Any:
    if value in (None, ""):
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return value
