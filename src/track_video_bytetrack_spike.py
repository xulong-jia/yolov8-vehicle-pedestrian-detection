"""Short Ultralytics ByteTrack spike for exporting tracks.csv.

This is a controlled spike tool, not the final ByteTrackAdapter integration.
Ultralytics is imported lazily only when the spike is executed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from src.tracking.bytetrack_discovery import normalize_ultralytics_track_result
from src.tracking.track_writer import TRACKS_FIELDS


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a max-frame-limited Ultralytics ByteTrack spike."
    )
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--video-id", default="demo")
    parser.add_argument("--tracker", default="bytetrack.yaml")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--max-frames", type=int, default=300)
    parser.add_argument("--render-preview", action="store_true")
    parser.add_argument("--config-json", type=Path)
    parser.add_argument("--overlay-plan-json", type=Path)
    return parser.parse_args(argv)


def require_file(path: str | Path, label: str) -> Path:
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"{label} not found: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"{label} must be a file: {resolved}")
    return resolved


def ensure_output_dir(path: str | Path) -> Path:
    resolved = Path(path).expanduser().resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def lazy_load_yolo_model(model_path: str | Path) -> Any:
    from ultralytics import YOLO  # noqa: PLC0415

    return YOLO(str(model_path))


def iter_ultralytics_track_results(
    model: Any,
    source: str | Path,
    tracker: str = "bytetrack.yaml",
    conf: float = 0.25,
    imgsz: int = 640,
    device: str = "cpu",
    stream: bool = True,
) -> Any:
    return model.track(
        source=str(source),
        tracker=tracker,
        conf=conf,
        imgsz=imgsz,
        device=device,
        stream=stream,
        persist=True,
        verbose=False,
    )


def normalize_result_rows(
    result: Any,
    video_id: str = "demo",
    frame_index: int | None = None,
    fps: float | None = None,
) -> list[dict[str, Any]]:
    if frame_index is not None and not hasattr(result, "frame_index"):
        setattr(result, "frame_index", frame_index)
    effective_frame_index = getattr(result, "frame_index", frame_index)
    if fps and effective_frame_index is not None and not hasattr(result, "timestamp_sec"):
        setattr(result, "timestamp_sec", float(effective_frame_index) / fps)
    return normalize_ultralytics_track_result(result, video_id=video_id)


def write_tracks_csv(rows: list[dict[str, Any]], output_csv: str | Path) -> Path:
    import csv

    output_path = Path(output_csv).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=TRACKS_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def run_bytetrack_spike(
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
    config_json: str | Path | None = None,
    overlay_plan_json: str | Path | None = None,
) -> dict[str, Any]:
    if max_frames <= 0:
        raise ValueError("max_frames must be greater than 0")

    model_file = require_file(model_path, "model")
    video_file = require_file(video_path, "video")
    output_path = ensure_output_dir(output_dir)
    tracks_csv = output_path / "bytetrack_tracks.csv"

    model = lazy_load_yolo_model(model_file)
    rows: list[dict[str, Any]] = []
    frames_seen = 0
    for frame_index, result in enumerate(
        iter_ultralytics_track_results(
            model,
            video_file,
            tracker=tracker,
            conf=conf,
            imgsz=imgsz,
            device=device,
            stream=True,
        )
    ):
        if frames_seen >= max_frames:
            break
        rows.extend(normalize_result_rows(result, video_id=video_id, frame_index=frame_index))
        frames_seen += 1

    write_tracks_csv(rows, tracks_csv)
    unique_tracks = {str(row.get("track_id")) for row in rows if row.get("track_id") not in ("", None)}
    frames_with_tracks = {
        str(row.get("frame_index")) for row in rows if row.get("frame_index") not in ("", None)
    }
    summary: dict[str, Any] = {
        "ok": True,
        "mode": "ultralytics_bytetrack_short_video_spike",
        "model_path": str(model_file),
        "video_path": str(video_file),
        "output_dir": str(output_path),
        "tracks_csv": str(tracks_csv),
        "tracker": tracker,
        "max_frames": max_frames,
        "frames_seen": frames_seen,
        "track_rows": len(rows),
        "unique_tracks": len(unique_tracks),
        "frames_with_tracks": len(frames_with_tracks),
        "render_preview": render_preview,
        "preview_video": "",
        "notes": [
            "This is a short-video spike, not full production integration.",
            "Outputs are local-only and must not be committed.",
            "Synthetic tracker fallback remains unchanged.",
        ],
    }

    if render_preview:
        preview_video = output_path / f"bytetrack_tracked_preview_{max_frames}.mp4"
        render_summary = _render_tracked_preview(
            video_file,
            tracks_csv,
            preview_video,
            config_json=config_json,
            overlay_plan_json=overlay_plan_json,
            max_frames=max_frames,
        )
        summary["preview_video"] = str(preview_video)
        summary["render_summary"] = render_summary

    return summary


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = run_bytetrack_spike(
            model_path=args.model,
            video_path=args.video,
            output_dir=args.output_dir,
            video_id=args.video_id,
            tracker=args.tracker,
            conf=args.conf,
            imgsz=args.imgsz,
            device=args.device,
            max_frames=args.max_frames,
            render_preview=args.render_preview,
            config_json=args.config_json,
            overlay_plan_json=args.overlay_plan_json,
        )
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1

    print(json.dumps(summary, ensure_ascii=False))
    return 0


def _render_tracked_preview(
    video_path: str | Path,
    tracks_csv: str | Path,
    output_video: str | Path,
    config_json: str | Path | None,
    overlay_plan_json: str | Path | None,
    max_frames: int,
) -> dict[str, Any]:
    from src.render_tracked_video import render_tracked_video  # noqa: PLC0415

    return render_tracked_video(
        video_path=video_path,
        tracks_csv=tracks_csv,
        output_video=output_video,
        config_json=config_json,
        overlay_plan_json=overlay_plan_json,
        max_frames=max_frames,
    )


if __name__ == "__main__":
    raise SystemExit(main())
