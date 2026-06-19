"""Lightweight video metadata reader for future analytics runtime.

This module reads video metadata and builds frame indexes only. It does not
run YOLO, connect trackers, save frame images, or render annotated videos.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


FRAME_INDEX_FIELDS = ["video_id", "filename", "frame_index", "timestamp_sec"]


def validate_video_path(video_path: str | Path) -> Path:
    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(f"video path does not exist: {path}")
    if path.is_dir():
        raise ValueError(f"video path must be a file, got directory: {path}")
    return path


def read_video_metadata(video_path: str | Path) -> dict[str, Any]:
    path = validate_video_path(video_path)
    cv2 = _import_cv2()

    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise ValueError(f"unable to open video: {path}")

        fps = float(capture.get(cv2.CAP_PROP_FPS))
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    finally:
        capture.release()

    return {
        "video_path": str(path),
        "filename": path.name,
        "fps": fps,
        "width": width,
        "height": height,
        "frame_count": frame_count,
        "duration_sec": frame_count / fps if fps > 0 else 0,
        "backend": "opencv",
    }


def build_frame_index(
    metadata: dict[str, Any],
    sample_every_n: int = 1,
    max_frames: int | None = None,
) -> list[dict[str, Any]]:
    fps = float(metadata.get("fps", 0))
    frame_count = int(metadata.get("frame_count", 0))
    if fps <= 0:
        raise ValueError("metadata.fps must be greater than 0")
    if frame_count < 0:
        raise ValueError("metadata.frame_count must be greater than or equal to 0")
    if sample_every_n <= 0:
        raise ValueError("sample_every_n must be greater than 0")

    filename = str(metadata.get("filename", ""))
    video_id = metadata.get("video_id") or filename
    rows: list[dict[str, Any]] = []

    for frame_index in range(0, frame_count, sample_every_n):
        if max_frames is not None and len(rows) >= max_frames:
            break
        rows.append(
            {
                "video_id": video_id,
                "filename": filename,
                "frame_index": frame_index,
                "timestamp_sec": frame_index / fps,
            }
        )

    return rows


def write_frame_index_csv(frame_index: list[dict[str, Any]], output_path: str | Path) -> Path:
    path = _prepare_output_path(output_path)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FRAME_INDEX_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(frame_index)
    return path


def write_video_metadata_json(metadata: dict[str, Any], output_path: str | Path) -> Path:
    path = _prepare_output_path(output_path)
    with path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False, indent=2)
        file.write("\n")
    return path


def _import_cv2():
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("OpenCV is required to read video metadata") from exc
    return cv2


def _prepare_output_path(output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
