"""Validate that existing ByteTrack tracks feed analytics and rendering.

This module is a pure orchestration layer. It does not run YOLO, does not run a
tracker, and does not call the standard track-video runtime.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from src.analytics_only_rerun import load_json, run_analytics_only_rerun
from src.render_tracked_video import render_tracked_video


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate existing ByteTrack tracks with analytics-only rerun and optional rendering."
    )
    parser.add_argument("--detections-csv", required=True, type=Path)
    parser.add_argument("--tracks-csv", required=True, type=Path)
    parser.add_argument("--config-json", required=True, type=Path)
    parser.add_argument("--video", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--run-name", default="bytetrack_validation")
    parser.add_argument("--video-id", default="demo")
    parser.add_argument("--render-preview", action="store_true")
    parser.add_argument("--overlay-plan-json", type=Path)
    parser.add_argument("--max-frames", default=300, type=int)
    return parser.parse_args(argv)


def require_file(path: str | Path, label: str) -> Path:
    file_path = Path(path).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"{label} not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"{label} must be a file: {file_path}")
    return file_path


def ensure_output_dir(path: str | Path) -> Path:
    output_dir = Path(path).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def summarize_tracks_csv(tracks_csv: str | Path) -> dict[str, Any]:
    tracks_path = require_file(tracks_csv, "tracks_csv")
    with tracks_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    unique_tracks = {
        str(row.get("track_id"))
        for row in rows
        if row.get("track_id") not in (None, "")
    }
    frames_with_tracks = {
        str(row.get("frame_index"))
        for row in rows
        if row.get("frame_index") not in (None, "")
    }
    class_counts: dict[str, int] = {}
    for row in rows:
        class_name = str(row.get("class_name") or "unknown")
        class_counts[class_name] = class_counts.get(class_name, 0) + 1

    return {
        "track_rows": len(rows),
        "unique_tracks": len(unique_tracks),
        "frames_with_tracks": len(frames_with_tracks),
        "class_counts": class_counts,
    }


def run_bytetrack_pipeline_validation(
    detections_csv: str | Path,
    tracks_csv: str | Path,
    config_json: str | Path,
    video_path: str | Path | None,
    output_dir: str | Path,
    run_name: str = "bytetrack_validation",
    video_id: str = "demo",
    render_preview: bool = False,
    overlay_plan_json: str | Path | None = None,
    max_frames: int = 300,
) -> dict[str, Any]:
    detections_path = require_file(detections_csv, "detections_csv")
    tracks_path = require_file(tracks_csv, "tracks_csv")
    config_path = require_file(config_json, "config_json")
    overlay_plan_path = (
        require_file(overlay_plan_json, "overlay_plan_json") if overlay_plan_json else None
    )
    video_file = require_file(video_path, "video") if render_preview else None
    if render_preview and video_file is None:
        raise ValueError("video is required when render_preview is enabled")

    output_path = ensure_output_dir(output_dir)
    analytics_output_dir = output_path / "analytics"
    tracks_summary = summarize_tracks_csv(tracks_path)
    analytics_tracks_path = _prepare_tracks_csv_for_analytics(
        tracks_path=tracks_path,
        output_dir=output_path,
    )
    analytics_summary = run_analytics_only_rerun(
        detections_csv=detections_path,
        tracks_csv=analytics_tracks_path,
        config_json=load_json(config_path),
        output_dir=analytics_output_dir,
        run_name=run_name,
        video_id=video_id,
        source_run_dir=tracks_path.parent,
        config_path=config_path,
    )

    render_summary: dict[str, Any] = {}
    preview_video = ""
    if render_preview:
        preview_path = output_path / "bytetrack_tracked_preview_300.mp4"
        preview_video = str(preview_path)
        render_summary = render_tracked_video(
            video_path=video_file,
            tracks_csv=tracks_path,
            output_video=preview_path,
            config_json=config_path,
            overlay_plan_json=overlay_plan_path,
            max_frames=max_frames,
        )

    return {
        "ok": True,
        "mode": "bytetrack_pipeline_validation",
        "tracks_summary": tracks_summary,
        "analytics_summary": analytics_summary,
        "render_summary": render_summary,
        "outputs": {
            "analytics_dir": str(analytics_output_dir),
            "tracks_csv_for_analytics": str(analytics_tracks_path),
            "preview_video": preview_video,
        },
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = run_bytetrack_pipeline_validation(
            detections_csv=args.detections_csv,
            tracks_csv=args.tracks_csv,
            config_json=args.config_json,
            video_path=args.video,
            output_dir=args.output_dir,
            run_name=args.run_name,
            video_id=args.video_id,
            render_preview=args.render_preview,
            overlay_plan_json=args.overlay_plan_json,
            max_frames=args.max_frames,
        )
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _prepare_tracks_csv_for_analytics(tracks_path: Path, output_dir: Path) -> Path:
    """Create a local compatibility copy when ByteTrack rows omit timestamps."""
    with tracks_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if "timestamp_sec" not in fieldnames:
        fieldnames.insert(2, "timestamp_sec")
    needs_copy = any(row.get("timestamp_sec") in (None, "") for row in rows)
    if not needs_copy:
        return tracks_path

    output_path = output_dir / "bytetrack_tracks_for_analytics.csv"
    for row in rows:
        if row.get("timestamp_sec") in (None, ""):
            row["timestamp_sec"] = _timestamp_from_frame_index(row.get("frame_index"))

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def _timestamp_from_frame_index(frame_index: Any) -> str:
    try:
        return f"{float(frame_index):.6f}"
    except (TypeError, ValueError):
        return "0.000000"


if __name__ == "__main__":
    raise SystemExit(main())
