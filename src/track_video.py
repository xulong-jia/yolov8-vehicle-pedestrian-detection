"""Skeleton CLI for video tracking contract development.

Supported skeleton modes:

- detections.csv to tracks.csv conversion through the tracking adapter factory
- metadata-only video mode for video path validation and frame indexing

The synthetic tracker is available for contract tests. ByteTrack/DeepSORT are
placeholder adapters only. This still does not run YOLO, read frames for
inference, integrate real ByteTrack/DeepSORT dependencies, or render tracked
videos.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from src.tracking.adapters import SyntheticTrackerAdapter, create_tracker_adapter
from src.tracking.track_writer import write_tracks_csv
from src.video_reader import (
    build_frame_index,
    read_video_metadata,
    write_frame_index_csv,
    write_video_metadata_json,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run track_video skeleton modes without YOLO or real tracker integration.",
    )
    parser.add_argument("--detections-csv", type=Path)
    parser.add_argument("--video-source", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--tracker", default="synthetic")
    parser.add_argument("--metadata-only", action="store_true")
    parser.add_argument("--sample-every-n", type=int, default=1)
    parser.add_argument("--max-frames", type=int)
    args = parser.parse_args(argv)

    has_detections = args.detections_csv is not None
    has_video_source = args.video_source is not None
    if has_detections == has_video_source:
        parser.error("provide exactly one of --detections-csv or --video-source")
    if has_video_source and not args.metadata_only:
        parser.error("video-source mode currently supports only --metadata-only")
    if has_detections and args.metadata_only:
        parser.error("--metadata-only requires --video-source")
    if args.sample_every_n <= 0:
        parser.error("--sample-every-n must be greater than 0")

    return args


def detections_to_synthetic_tracks(
    detection_rows: list[dict[str, Any]],
    tracker_name: str = "synthetic",
) -> list[dict[str, Any]]:
    """Compatibility wrapper around the synthetic tracking adapter."""
    adapter = SyntheticTrackerAdapter()
    track_rows = adapter.update(detection_rows)
    if tracker_name == "synthetic":
        return track_rows
    return [{**row, "tracker_name": tracker_name} for row in track_rows]


def run_track_video_skeleton(
    input_csv: str | Path,
    output_dir: str | Path,
    tracker_name: str = "synthetic",
) -> dict[str, Any]:
    input_path = Path(input_csv)
    if not input_path.exists():
        raise FileNotFoundError(f"detections CSV not found: {input_path}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    detection_rows = _read_detections_csv(input_path)
    adapter = create_tracker_adapter(tracker_name)
    track_rows = adapter.update(detection_rows)
    tracks_csv = write_tracks_csv(track_rows, output_path / "tracks.csv")

    return {
        "tracker_name": tracker_name,
        "input_rows": len(detection_rows),
        "track_rows": len(track_rows),
        "output_tracks_csv": str(tracks_csv),
    }


def run_video_metadata_skeleton(
    video_source: str | Path,
    output_dir: str | Path,
    sample_every_n: int = 1,
    max_frames: int | None = None,
) -> dict[str, Any]:
    if sample_every_n <= 0:
        raise ValueError("sample_every_n must be greater than 0")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    metadata = read_video_metadata(video_source)
    frame_index = build_frame_index(
        metadata,
        sample_every_n=sample_every_n,
        max_frames=max_frames,
    )
    metadata_json = write_video_metadata_json(metadata, output_path / "video_metadata.json")
    frame_index_csv = write_frame_index_csv(frame_index, output_path / "frame_index.csv")

    return {
        "mode": "metadata_only",
        "video_source": str(video_source),
        "output_metadata_json": str(metadata_json),
        "output_frame_index_csv": str(frame_index_csv),
        "frame_index_rows": len(frame_index),
        "fps": metadata.get("fps"),
        "width": metadata.get("width"),
        "height": metadata.get("height"),
        "frame_count": metadata.get("frame_count"),
        "duration_sec": metadata.get("duration_sec"),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.metadata_only:
        summary = run_video_metadata_skeleton(
            args.video_source,
            args.output_dir,
            sample_every_n=args.sample_every_n,
            max_frames=args.max_frames,
        )
    else:
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


if __name__ == "__main__":
    raise SystemExit(main())
