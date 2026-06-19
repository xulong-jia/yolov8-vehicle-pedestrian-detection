"""Skeleton CLI for converting detections.csv to tracks.csv.

This does not run YOLO.
This does not read real videos.
This does not integrate ByteTrack/DeepSORT yet.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from src.analytics.geometry import bbox_center, bbox_size_and_area
from src.tracking.track_writer import write_tracks_csv


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert detections.csv rows to synthetic tracks.csv rows.",
    )
    parser.add_argument("--detections-csv", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--tracker", default="synthetic")
    return parser.parse_args(argv)


def detections_to_synthetic_tracks(
    detection_rows: list[dict[str, Any]],
    tracker_name: str = "synthetic",
) -> list[dict[str, Any]]:
    tracks: list[dict[str, Any]] = []

    for row_index, row in enumerate(detection_rows, start=1):
        xmin = float(row["xmin"])
        ymin = float(row["ymin"])
        xmax = float(row["xmax"])
        ymax = float(row["ymax"])
        center_x, center_y = bbox_center(xmin, ymin, xmax, ymax)
        box_width, box_height, box_area = bbox_size_and_area(xmin, ymin, xmax, ymax)
        track_id = row.get("detection_id") or f"synthetic_{row_index}"

        tracks.append(
            {
                "video_id": row.get("video_id", ""),
                "frame_index": _to_int_if_possible(row.get("frame_index")),
                "timestamp_sec": _to_float_if_possible(row.get("timestamp_sec")),
                "track_id": track_id,
                "class_id": _to_int_if_possible(row.get("class_id")),
                "class_name": row.get("class_name", ""),
                "confidence": _to_float_if_possible(row.get("confidence")),
                "xmin": xmin,
                "ymin": ymin,
                "xmax": xmax,
                "ymax": ymax,
                "center_x": center_x,
                "center_y": center_y,
                "box_width": box_width,
                "box_height": box_height,
                "box_area": box_area,
                "state": "confirmed",
                "tracker_name": tracker_name,
            }
        )

    return tracks


def run_track_video_skeleton(
    input_csv: str | Path,
    output_dir: str | Path,
    tracker_name: str = "synthetic",
) -> dict[str, Any]:
    if tracker_name != "synthetic":
        raise ValueError("track_video skeleton currently supports only tracker='synthetic'")

    input_path = Path(input_csv)
    if not input_path.exists():
        raise FileNotFoundError(f"detections CSV not found: {input_path}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    detection_rows = _read_detections_csv(input_path)
    track_rows = detections_to_synthetic_tracks(detection_rows, tracker_name=tracker_name)
    tracks_csv = write_tracks_csv(track_rows, output_path / "tracks.csv")

    return {
        "tracker_name": tracker_name,
        "input_rows": len(detection_rows),
        "track_rows": len(track_rows),
        "output_tracks_csv": str(tracks_csv),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    summary = run_track_video_skeleton(
        args.detections_csv,
        args.output_dir,
        tracker_name=args.tracker,
    )
    print(json.dumps(summary, ensure_ascii=False))
    return 0


def _read_detections_csv(input_path: Path) -> list[dict[str, Any]]:
    with input_path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


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


if __name__ == "__main__":
    raise SystemExit(main())
