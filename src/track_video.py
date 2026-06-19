"""Skeleton CLI for video tracking contract development.

Supported skeleton modes:

- detections.csv to tracks.csv conversion through the tracking adapter factory
- metadata-only video mode for video path validation and frame indexing
- video-source ByteTrack runtime through Ultralytics model.track

The synthetic tracker is available for contract tests. The ByteTrack video
runtime is opt-in and max-frame-limited. DeepSORT remains a placeholder.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from src import track_video_bytetrack_spike as bytetrack_spike
from src.tracking.bytetrack_runtime_contract import parse_frame_limit, summarize_track_rows
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
    parser.add_argument("--model", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--tracker", default="synthetic")
    parser.add_argument("--video-id", default="demo")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--metadata-only", action="store_true")
    parser.add_argument("--sample-every-n", type=int, default=1)
    parser.add_argument("--max-frames", type=int)
    args = parser.parse_args(argv)

    has_detections = args.detections_csv is not None
    has_video_source = args.video_source is not None
    if has_detections == has_video_source:
        parser.error("provide exactly one of --detections-csv or --video-source")
    if has_video_source and not args.metadata_only and args.tracker != "bytetrack":
        parser.error("video-source mode currently supports --metadata-only or --tracker bytetrack")
    if has_video_source and not args.metadata_only and args.tracker == "bytetrack" and args.model is None:
        parser.error("--tracker bytetrack with --video-source requires --model")
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


def run_track_video_bytetrack_runtime(
    model_path: str | Path,
    video_source: str | Path,
    output_dir: str | Path,
    video_id: str = "demo",
    tracker: str = "bytetrack.yaml",
    conf: float = 0.25,
    imgsz: int = 640,
    device: str = "cpu",
    max_frames: int | None = 300,
) -> dict[str, Any]:
    frame_limit = parse_frame_limit(max_frames, default=300)
    try:
        model_file = bytetrack_spike.require_file(model_path, "model")
        video_file = bytetrack_spike.require_file(video_source, "video")
        output_path = bytetrack_spike.ensure_output_dir(output_dir)
        tracks_csv = output_path / "tracks.csv"
        model = bytetrack_spike.lazy_load_yolo_model(model_file)

        rows: list[dict[str, Any]] = []
        frames_seen = 0
        for frame_index, result in enumerate(
            bytetrack_spike.iter_ultralytics_track_results(
                model,
                video_file,
                tracker=tracker,
                conf=conf,
                imgsz=imgsz,
                device=device,
                stream=True,
            )
        ):
            if frames_seen >= frame_limit:
                break
            rows.extend(
                bytetrack_spike.normalize_result_rows(
                    result,
                    video_id=video_id,
                    frame_index=frame_index,
                )
            )
            frames_seen += 1
    except ModuleNotFoundError as exc:
        raise RuntimeError(_bytetrack_dependency_error()) from exc
    except Exception as exc:
        message = str(exc).lower()
        if "lap" in message or "ultralytics" in message:
            raise RuntimeError(_bytetrack_dependency_error()) from exc
        raise

    bytetrack_spike.write_tracks_csv(rows, tracks_csv)
    track_summary = summarize_track_rows(rows)
    return {
        "mode": "track_video_bytetrack_runtime",
        "tracker": "bytetrack",
        "tracks_csv": str(tracks_csv),
        "frames_seen": frames_seen,
        "track_rows": track_summary["track_rows"],
        "unique_tracks": track_summary["unique_tracks"],
        "frames_with_tracks": track_summary["frames_with_tracks"],
        "max_frames": frame_limit,
        "video_id": video_id,
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
    elif args.video_source is not None and args.tracker == "bytetrack":
        summary = run_track_video_bytetrack_runtime(
            model_path=args.model,
            video_source=args.video_source,
            output_dir=args.output_dir,
            video_id=args.video_id,
            conf=args.conf,
            imgsz=args.imgsz,
            device=args.device,
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


def _bytetrack_dependency_error() -> str:
    return (
        "ByteTrack runtime requires ultralytics and lap. Install lap in the active "
        "environment or see docs/bytetrack_integration_plan.md"
    )


if __name__ == "__main__":
    raise SystemExit(main())
