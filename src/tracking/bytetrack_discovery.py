"""ByteTrack discovery helpers for a future real tracker integration.

This module is a pure-Python spike helper. It does not import or run
Ultralytics, OpenCV, torch, numpy, ByteTrack, or DeepSORT.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from typing import Any

from src.tracking.adapters import tracker_outputs_to_track_rows
from src.tracking.track_writer import TRACKS_FIELDS


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect ByteTrack integration options without running a tracker."
    )
    parser.add_argument("--video-id", default="demo")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def check_optional_module(module_name: str) -> dict[str, Any]:
    return {
        "module": module_name,
        "available": importlib.util.find_spec(module_name) is not None,
    }


def discover_bytetrack_options() -> dict[str, Any]:
    return {
        "ultralytics": check_optional_module("ultralytics"),
        "cv2": check_optional_module("cv2"),
        "recommended_path": "ultralytics_model_track_spike",
        "candidate_paths": [
            {
                "name": "ultralytics_model_track",
                "description": (
                    "Use Ultralytics YOLO.track with tracker='bytetrack.yaml', then "
                    "normalize boxes.id outputs into the existing tracks.csv contract."
                ),
                "pros": [
                    "fastest path to a real ByteTrack smoke spike",
                    "uses the existing Ultralytics runtime already needed for YOLO inference",
                    "may directly expose per-box track IDs through result.boxes.id",
                ],
                "cons": [
                    "couples detection and tracking in one runtime call",
                    "can bypass the existing detections.csv to adapter contract",
                    "requires a careful tracks.csv export wrapper and short-video validation",
                ],
                "status": "recommended_for_next_spike",
            },
            {
                "name": "external_bytetrack_adapter",
                "description": (
                    "Install and wrap a standalone ByteTrack implementation behind "
                    "BaseTrackerAdapter using detections.csv rows as input."
                ),
                "pros": [
                    "fits the adapter architecture more directly",
                    "can reuse existing detections.csv artifacts",
                    "keeps detection export and tracking separated",
                ],
                "cons": [
                    "new dependency and platform compatibility risk",
                    "input format and tracker state management are more complex",
                    "requires a separate dependency approval and installation step",
                ],
                "status": "later",
            },
        ],
        "track_csv_contract": list(TRACKS_FIELDS),
    }


def normalize_ultralytics_track_result(
    result: Any,
    video_id: str = "demo",
) -> list[dict[str, Any]]:
    return _normalize_ultralytics_track_result(result, video_id=video_id, default_frame_index=0)


def normalize_ultralytics_track_results(
    results: list[Any],
    video_id: str = "demo",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, result in enumerate(results):
        rows.extend(
            _normalize_ultralytics_track_result(
                result,
                video_id=video_id,
                default_frame_index=index,
            )
        )
    return rows


def track_objects_to_rows(
    objects: list[dict[str, Any]],
    video_id: str = "demo",
    frame_index: int = 0,
    timestamp_sec: float | None = None,
) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for item in objects:
        outputs.append(
            {
                "video_id": video_id,
                "frame_index": frame_index,
                "timestamp_sec": "" if timestamp_sec is None else timestamp_sec,
                "track_id": item.get("track_id", ""),
                "class_id": item.get("class_id", ""),
                "class_name": item.get("class_name", ""),
                "confidence": item.get("confidence", ""),
                "bbox": item["bbox"],
                "state": item.get("state", "confirmed"),
            }
        )
    return tracker_outputs_to_track_rows(outputs, tracker_name="bytetrack")


def validate_track_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    missing_required_fields: list[str] = []
    missing_track_id_count = 0
    invalid_bbox_count = 0
    unique_tracks: set[str] = set()

    for row in rows:
        for field in TRACKS_FIELDS:
            if field not in row and field not in missing_required_fields:
                missing_required_fields.append(field)

        track_id = row.get("track_id")
        if track_id in (None, ""):
            missing_track_id_count += 1
        else:
            unique_tracks.add(str(track_id))

        bbox_values = [row.get("xmin"), row.get("ymin"), row.get("xmax"), row.get("ymax")]
        if not _valid_bbox(bbox_values):
            invalid_bbox_count += 1

    return {
        "ok": not missing_required_fields
        and missing_track_id_count == 0
        and invalid_bbox_count == 0,
        "row_count": len(rows),
        "missing_required_fields": missing_required_fields,
        "missing_track_id_count": missing_track_id_count,
        "invalid_bbox_count": invalid_bbox_count,
        "unique_tracks": len(unique_tracks),
    }


def summarize_discovery() -> dict[str, Any]:
    summary = discover_bytetrack_options()
    summary["notes"] = [
        "This spike does not run real ByteTrack.",
        "This spike does not install dependencies.",
        "Next implementation should test model.track with a short local video only after approval.",
        "Current recommended next step: wrap Ultralytics model.track output into tracks.csv contract.",
        "Keep the synthetic tracker fallback until real ByteTrack quality is validated.",
    ]
    return summary


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    summary = summarize_discovery()
    summary["video_id"] = args.video_id
    print(json.dumps(summary, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


def _normalize_ultralytics_track_result(
    result: Any,
    video_id: str,
    default_frame_index: int,
) -> list[dict[str, Any]]:
    boxes = getattr(result, "boxes", None)
    if boxes is None:
        return []

    track_ids = _as_list(getattr(boxes, "id", None))
    if not track_ids:
        return []

    xyxy_rows = _as_list(getattr(boxes, "xyxy", []))
    class_ids = _as_list(getattr(boxes, "cls", []))
    confidences = _as_list(getattr(boxes, "conf", []))
    names = getattr(result, "names", {}) or {}
    frame_index = getattr(result, "frame_index", default_frame_index)
    timestamp_sec = getattr(result, "timestamp_sec", "")

    objects: list[dict[str, Any]] = []
    for box, track_id, class_id, confidence in zip(xyxy_rows, track_ids, class_ids, confidences):
        if track_id in (None, ""):
            continue
        parsed_class_id = _to_int(class_id)
        objects.append(
            {
                "track_id": str(_to_scalar(track_id)),
                "class_id": parsed_class_id,
                "class_name": _class_name(names, parsed_class_id),
                "confidence": _to_float(confidence),
                "bbox": [_to_float(value) for value in _as_list(box)[:4]],
            }
        )

    return track_objects_to_rows(
        objects,
        video_id=video_id,
        frame_index=_to_int(frame_index),
        timestamp_sec=None if timestamp_sec == "" else _to_float(timestamp_sec),
    )


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    for method_name in ("cpu", "numpy"):
        method = getattr(value, method_name, None)
        if callable(method):
            value = method()
    tolist = getattr(value, "tolist", None)
    if callable(tolist):
        value = tolist()
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _class_name(names: dict[Any, str] | list[str] | tuple[str, ...], class_id: int) -> str:
    if isinstance(names, dict):
        return str(names.get(class_id, names.get(str(class_id), class_id)))
    if 0 <= class_id < len(names):
        return str(names[class_id])
    return str(class_id)


def _to_scalar(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    return value


def _to_int(value: Any) -> int:
    return int(float(_to_scalar(value)))


def _to_float(value: Any) -> float:
    return float(_to_scalar(value))


def _valid_bbox(values: list[Any]) -> bool:
    try:
        xmin, ymin, xmax, ymax = [float(value) for value in values]
    except (TypeError, ValueError):
        return False
    return xmax >= xmin and ymax >= ymin


if __name__ == "__main__":
    raise SystemExit(main())
