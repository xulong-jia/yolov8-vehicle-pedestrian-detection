"""Render a tracked preview video from existing tracks.csv rows.

This module reads an existing source video and existing tracks.csv, then draws
track boxes and optional line/ROI overlays. It does not run YOLO, does not run a
tracker, and does not integrate ByteTrack/DeepSORT.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render tracked preview video from existing tracks.csv rows."
    )
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--tracks-csv", required=True, type=Path)
    parser.add_argument("--output-video", required=True, type=Path)
    parser.add_argument("--config-json", type=Path)
    parser.add_argument("--overlay-plan-json", type=Path)
    parser.add_argument("--max-frames", type=int)
    parser.add_argument("--no-tracks", action="store_true")
    parser.add_argument("--no-overlays", action="store_true")
    parser.add_argument("--codec", default="mp4v")
    return parser.parse_args(argv)


def load_csv_rows(path: str | Path) -> list[dict[str, str]]:
    csv_path = _existing_file(path, "tracks_csv")
    with csv_path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def load_json(path: str | Path) -> dict[str, Any]:
    json_path = _existing_file(path, "json")
    with json_path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"JSON file must contain an object: {json_path}")
    return data


def parse_float(value: Any, default: float | None = None) -> float | None:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_int(value: Any, default: int | None = None) -> int | None:
    if value in (None, ""):
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def group_tracks_by_frame(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        track = normalize_track_row(row)
        grouped.setdefault(track["frame_index"], []).append(track)
    return grouped


def normalize_track_row(row: dict[str, Any]) -> dict[str, Any]:
    frame_index = parse_int(row.get("frame_index"))
    if frame_index is None:
        raise ValueError(f"track row missing frame_index: {row}")

    bbox_values = [
        parse_float(row.get("xmin")),
        parse_float(row.get("ymin")),
        parse_float(row.get("xmax")),
        parse_float(row.get("ymax")),
    ]
    if any(value is None for value in bbox_values):
        raise ValueError(f"track row missing bbox fields: {row}")

    return {
        "frame_index": frame_index,
        "track_id": str(row.get("track_id") or ""),
        "class_name": str(row.get("class_name") or "unknown"),
        "confidence": parse_float(row.get("confidence")),
        "bbox": [float(value) for value in bbox_values if value is not None],
    }


def color_for_track_id(track_id: Any) -> tuple[int, int, int]:
    text = str(track_id)
    total = sum((index + 1) * ord(char) for index, char in enumerate(text))
    return (
        50 + total % 206,
        50 + (total * 3) % 206,
        50 + (total * 7) % 206,
    )


def draw_label(frame: Any, text: str, x: int, y: int, cv2_module: Any) -> None:
    cv2_module.putText(
        frame,
        text,
        (max(0, x), max(12, y)),
        cv2_module.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
    )


def draw_track_box(frame: Any, track: dict[str, Any], cv2_module: Any) -> None:
    xmin, ymin, xmax, ymax = [int(round(value)) for value in track["bbox"]]
    color = color_for_track_id(track["track_id"])
    cv2_module.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
    label = f"#{track['track_id']} {track['class_name']}"
    if track.get("confidence") is not None:
        label = f"{label} {track['confidence']:.2f}"
    draw_label(frame, label, xmin, ymin - 5, cv2_module)


def extract_overlay_config(
    config_json: dict[str, Any] | None = None,
    overlay_plan_json: dict[str, Any] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    if config_json:
        config = config_json.get("suggested_config", config_json)
        if isinstance(config, dict):
            return {
                "lines": list(config.get("lines") or []),
                "rois": list(config.get("rois") or []),
            }

    if overlay_plan_json:
        return {
            "lines": [
                {"line_id": plan.get("line_id"), "points": plan.get("points")}
                for plan in overlay_plan_json.get("line_plans", [])
                if plan.get("points")
            ],
            "rois": [
                {"roi_id": plan.get("roi_id"), "polygon": plan.get("polygon")}
                for plan in overlay_plan_json.get("roi_plans", [])
                if plan.get("polygon")
            ],
        }

    return {"lines": [], "rois": []}


def draw_line_overlays(frame: Any, lines: list[dict[str, Any]], cv2_module: Any) -> None:
    for line in lines:
        points = line.get("points") or []
        if len(points) != 2:
            continue
        start = _to_int_point(points[0])
        end = _to_int_point(points[1])
        cv2_module.line(frame, start, end, (0, 255, 255), 2)
        label = str(line.get("line_id") or line.get("id") or "")
        if label:
            draw_label(frame, label, start[0], start[1] - 5, cv2_module)


def draw_roi_overlays(frame: Any, rois: list[dict[str, Any]], cv2_module: Any) -> None:
    for roi in rois:
        polygon = roi.get("polygon") or []
        if len(polygon) < 3:
            continue
        int_points = [_to_int_point(point) for point in polygon]
        for start, end in zip(int_points, int_points[1:] + int_points[:1]):
            cv2_module.line(frame, start, end, (0, 200, 0), 2)
        label = str(roi.get("roi_id") or roi.get("id") or "")
        if label:
            draw_label(frame, label, int_points[0][0], int_points[0][1] - 5, cv2_module)


def render_tracked_video(
    video_path: str | Path,
    tracks_csv: str | Path,
    output_video: str | Path,
    config_json: str | Path | dict[str, Any] | None = None,
    overlay_plan_json: str | Path | dict[str, Any] | None = None,
    max_frames: int | None = None,
    draw_tracks: bool = True,
    draw_overlays: bool = True,
    codec: str = "mp4v",
) -> dict[str, Any]:
    import cv2  # noqa: PLC0415

    video_file = _existing_file(video_path, "video")
    tracks_file = _existing_file(tracks_csv, "tracks_csv")
    output_path = Path(output_video).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    track_rows = load_csv_rows(tracks_file)
    tracks_by_frame = group_tracks_by_frame(track_rows)
    unique_tracks = {track["track_id"] for tracks in tracks_by_frame.values() for track in tracks}
    overlay_config = extract_overlay_config(
        _json_arg(config_json),
        _json_arg(overlay_plan_json),
    )

    capture = cv2.VideoCapture(str(video_file))
    writer = None
    frames_read = 0
    frames_written = 0
    try:
        if not capture.isOpened():
            raise ValueError(f"video cannot be opened: {video_file}")

        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0) or 25.0
        if width <= 0 or height <= 0:
            ok, frame = capture.read()
            if not ok:
                raise ValueError(f"video has no readable frames: {video_file}")
            frames_read += 1
            height, width = _frame_size(frame)
            capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frames_read = 0

        fourcc = cv2.VideoWriter_fourcc(*codec)
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        frame_index = 0
        while True:
            if max_frames is not None and frames_written >= max_frames:
                break
            ok, frame = capture.read()
            if not ok:
                break
            frames_read += 1

            if draw_tracks:
                for track in tracks_by_frame.get(frame_index, []):
                    draw_track_box(frame, track, cv2)
            if draw_overlays:
                draw_line_overlays(frame, overlay_config["lines"], cv2)
                draw_roi_overlays(frame, overlay_config["rois"], cv2)

            writer.write(frame)
            frames_written += 1
            frame_index += 1
    finally:
        capture.release()
        if writer is not None:
            writer.release()

    return {
        "ok": True,
        "mode": "tracked_video_rendering",
        "video_path": str(video_file),
        "tracks_csv": str(tracks_file),
        "output_video": str(output_path),
        "frames_read": frames_read,
        "frames_written": frames_written,
        "track_rows_loaded": len(track_rows),
        "unique_tracks": len(unique_tracks),
        "frames_with_tracks": len(tracks_by_frame),
        "draw_tracks": draw_tracks,
        "draw_overlays": draw_overlays,
        "line_overlay_count": len(overlay_config["lines"]) if draw_overlays else 0,
        "roi_overlay_count": len(overlay_config["rois"]) if draw_overlays else 0,
        "fps": fps,
        "width": width,
        "height": height,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = render_tracked_video(
            video_path=args.video,
            tracks_csv=args.tracks_csv,
            output_video=args.output_video,
            config_json=args.config_json,
            overlay_plan_json=args.overlay_plan_json,
            max_frames=args.max_frames,
            draw_tracks=not args.no_tracks,
            draw_overlays=not args.no_overlays,
            codec=args.codec,
        )
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _json_arg(value: str | Path | dict[str, Any] | None) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    return load_json(value)


def _to_int_point(point: Any) -> tuple[int, int]:
    return (int(round(float(point[0]))), int(round(float(point[1]))))


def _frame_size(frame: Any) -> tuple[int, int]:
    shape = getattr(frame, "shape", None)
    if shape is not None and len(shape) >= 2:
        return int(shape[0]), int(shape[1])
    if isinstance(frame, list) and frame and isinstance(frame[0], list):
        return len(frame), len(frame[0])
    raise ValueError("cannot infer frame size")


def _existing_file(path: str | Path, name: str) -> Path:
    file_path = Path(path).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"{name} not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"{name} must be a file: {file_path}")
    return file_path


if __name__ == "__main__":
    raise SystemExit(main())
