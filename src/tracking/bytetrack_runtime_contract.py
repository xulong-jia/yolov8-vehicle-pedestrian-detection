"""Pure-Python ByteTrack runtime planning helpers.

This module prepares the contract for a future ``track_video.py --tracker
bytetrack`` runtime. It does not import or run tracker, detection, or video
libraries.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def parse_frame_limit(value: Any, default: int = 300) -> int:
    if value is None:
        parsed = default
    else:
        try:
            parsed = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"frame limit must be a positive integer: {value}") from exc

    if parsed <= 0:
        raise ValueError("frame limit must be greater than 0")
    return parsed


def build_bytetrack_output_paths(output_dir: str | Path) -> dict[str, str]:
    output_path = Path(output_dir)
    return {
        "output_dir": str(output_path),
        "tracks_csv": str(output_path / "bytetrack_tracks.csv"),
        "preview_video": str(output_path / "bytetrack_tracked_preview_300.mp4"),
        "summary_json": str(output_path / "bytetrack_spike_summary.json"),
    }


def build_bytetrack_runtime_metadata(
    video_id: str,
    tracker: str = "bytetrack.yaml",
    model_path: str | Path | None = None,
    video_path: str | Path | None = None,
    max_frames: int | None = None,
) -> dict[str, Any]:
    return {
        "mode": "ultralytics_bytetrack_runtime",
        "video_id": video_id,
        "tracker": tracker,
        "model_path": str(model_path or ""),
        "video_path": str(video_path or ""),
        "max_frames": max_frames,
        "dependency_note": "requires ultralytics and lap for bytetrack.yaml",
    }


def summarize_track_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    unique_tracks: set[str] = set()
    frames_with_tracks: set[str] = set()
    class_counts: dict[str, int] = {}
    missing_track_id_count = 0
    invalid_bbox_count = 0

    for row in rows:
        track_id = row.get("track_id")
        if track_id in (None, ""):
            missing_track_id_count += 1
        else:
            unique_tracks.add(str(track_id))

        frame_index = row.get("frame_index")
        if frame_index not in (None, ""):
            frames_with_tracks.add(str(frame_index))

        class_name = str(row.get("class_name") or "unknown")
        class_counts[class_name] = class_counts.get(class_name, 0) + 1

        if not _valid_bbox(row):
            invalid_bbox_count += 1

    return {
        "track_rows": len(rows),
        "unique_tracks": len(unique_tracks),
        "frames_with_tracks": len(frames_with_tracks),
        "class_counts": class_counts,
        "missing_track_id_count": missing_track_id_count,
        "invalid_bbox_count": invalid_bbox_count,
    }


def validate_bytetrack_runtime_config(
    model_path: str | Path,
    video_path: str | Path,
    output_dir: str | Path,
    max_frames: int = 300,
    tracker: str = "bytetrack.yaml",
) -> dict[str, Any]:
    errors: list[str] = []
    model_file = Path(model_path).expanduser()
    video_file = Path(video_path).expanduser()
    output_path = Path(output_dir).expanduser()

    checks = {
        "model_exists": model_file.exists() and model_file.is_file(),
        "video_exists": video_file.exists() and video_file.is_file(),
        "output_parent_ready": _output_parent_ready(output_path),
        "max_frames_positive": _is_positive_int(max_frames),
        "tracker_non_empty": bool(str(tracker).strip()),
    }

    if not checks["model_exists"]:
        errors.append(f"model_path must be an existing file: {model_file}")
    if not checks["video_exists"]:
        errors.append(f"video_path must be an existing file: {video_file}")
    if not checks["output_parent_ready"]:
        errors.append(f"output_dir parent is not available: {output_path.parent}")
    if not checks["max_frames_positive"]:
        errors.append("max_frames must be greater than 0")
    if not checks["tracker_non_empty"]:
        errors.append("tracker must be non-empty")

    return {
        "ok": not errors,
        "checks": checks,
        "errors": errors,
    }


def build_track_video_bytetrack_plan(
    model_path: str | Path,
    video_path: str | Path,
    output_dir: str | Path,
    video_id: str = "demo",
    tracker: str = "bytetrack.yaml",
    conf: float = 0.25,
    imgsz: int = 640,
    device: str = "cpu",
    max_frames: int = 300,
    render_preview: bool = False,
) -> dict[str, Any]:
    parsed_max_frames = parse_frame_limit(max_frames)
    return {
        "mode": "track_video_bytetrack_runtime_plan",
        "command_intent": "future track_video.py --tracker bytetrack runtime",
        "inputs": {
            "model_path": str(model_path),
            "video_path": str(video_path),
            "output_dir": str(output_dir),
            "video_id": video_id,
            "tracker": tracker,
            "conf": conf,
            "imgsz": imgsz,
            "device": device,
            "max_frames": parsed_max_frames,
            "render_preview": render_preview,
        },
        "outputs": build_bytetrack_output_paths(output_dir),
        "metadata": build_bytetrack_runtime_metadata(
            video_id=video_id,
            tracker=tracker,
            model_path=model_path,
            video_path=video_path,
            max_frames=parsed_max_frames,
        ),
        "runtime_steps": [
            "load YOLO model",
            "call model.track(..., tracker='bytetrack.yaml', stream=True, persist=True)",
            "normalize boxes.id into tracks.csv",
            "optionally render tracked preview",
        ],
        "no_go_items": [
            "do not commit output CSV/MP4",
            "do not run full-length by default",
            "keep synthetic tracker fallback",
        ],
        "next_version": "v0.11.4-track-video-bytetrack-runtime",
    }


def _output_parent_ready(output_path: Path) -> bool:
    parent = output_path.parent
    if parent.exists():
        return parent.is_dir()
    ancestor = parent.parent
    return ancestor.exists() and ancestor.is_dir()


def _is_positive_int(value: Any) -> bool:
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


def _valid_bbox(row: dict[str, Any]) -> bool:
    try:
        xmin = float(row.get("xmin"))
        ymin = float(row.get("ymin"))
        xmax = float(row.get("xmax"))
        ymax = float(row.get("ymax"))
    except (TypeError, ValueError):
        return False
    return xmax >= xmin and ymax >= ymin
