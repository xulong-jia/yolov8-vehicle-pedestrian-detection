"""Preflight checker for local video analysis smoke runs.

This is a preflight checker for local smoke runs. It does not run YOLO, does
not create outputs, does not run tracking, and does not run child commands. It
only validates paths/modules and prints command previews.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shlex
from pathlib import Path
from typing import Any


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preflight local video analysis smoke run.")
    parser.add_argument("--model", required=True, help="Path to YOLO model weights.")
    parser.add_argument("--video", required=True, help="Path to input video.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Output directory preview.")
    parser.add_argument("--video-id", default="demo", help="Stable video_id for output rows.")
    parser.add_argument("--run-name", default="demo_run", help="Video Analysis Center run name.")
    parser.add_argument("--conf", type=float, default=0.25, help="YOLO confidence threshold.")
    parser.add_argument("--imgsz", type=int, default=640, help="YOLO image size.")
    parser.add_argument("--device", default="cpu", help="YOLO inference device.")
    return parser.parse_args(argv)


def check_file_path(path: str | Path, label: str) -> Path:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"{label} does not exist: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"{label} must be a file: {file_path}")
    return file_path


def check_output_dir(path: str | Path) -> Path:
    output_path = Path(path)
    if output_path.exists() and not output_path.is_dir():
        raise ValueError(f"output_dir must be a directory path: {output_path}")
    parent = output_path.parent
    if not parent.exists():
        raise FileNotFoundError(f"output_dir parent does not exist: {parent}")
    return output_path


def check_optional_module(module_name: str) -> dict[str, Any]:
    return {
        "name": module_name,
        "available": importlib.util.find_spec(module_name) is not None,
    }


def build_smoke_commands(
    model_path: str | Path,
    video_path: str | Path,
    output_dir: str | Path,
    video_id: str = "demo",
    run_name: str = "demo_run",
    conf: float = 0.25,
    imgsz: int = 640,
    device: str = "cpu",
) -> dict[str, str]:
    output_path = Path(output_dir)
    detections_csv = output_path / "detections.csv"
    tracking_dir = output_path / "tracking"
    return {
        "predict_video_csv": " ".join(
            [
                "python3",
                "src/predict_video.py",
                "--model",
                _quote(model_path),
                "--source",
                _quote(video_path),
                "--output-csv",
                _quote(detections_csv),
                "--conf",
                str(conf),
                "--imgsz",
                str(imgsz),
                "--device",
                _quote(device),
                "--video-id",
                _quote(video_id),
            ]
        ),
        "track_video_synthetic": " ".join(
            [
                "python3",
                "src/track_video.py",
                "--detections-csv",
                _quote(detections_csv),
                "--output-dir",
                _quote(tracking_dir),
                "--tracker",
                "synthetic",
            ]
        ),
        "four_step_runner": " ".join(
            [
                "python3",
                "src/run_video_analysis_smoke.py",
                "--model",
                _quote(model_path),
                "--source",
                _quote(video_path),
                "--output-dir",
                _quote(output_path),
                "--video-id",
                _quote(video_id),
                "--run-name",
                _quote(run_name),
                "--conf",
                str(conf),
                "--imgsz",
                str(imgsz),
                "--device",
                _quote(device),
            ]
        ),
    }


def run_preflight(
    model_path: str | Path,
    video_path: str | Path,
    output_dir: str | Path,
    video_id: str = "demo",
    run_name: str = "demo_run",
    conf: float = 0.25,
    imgsz: int = 640,
    device: str = "cpu",
) -> dict[str, Any]:
    checks: dict[str, Any] = {}

    model_result = _path_check(lambda: check_file_path(model_path, "model_path"))
    video_result = _path_check(lambda: check_file_path(video_path, "video_path"))
    output_result = _path_check(lambda: check_output_dir(output_dir))
    checks["model_path"] = model_result
    checks["video_path"] = video_result
    checks["output_dir"] = output_result
    checks["ultralytics"] = check_optional_module("ultralytics")
    checks["cv2"] = check_optional_module("cv2")

    commands = build_smoke_commands(
        model_path=model_path,
        video_path=video_path,
        output_dir=output_dir,
        video_id=video_id,
        run_name=run_name,
        conf=conf,
        imgsz=imgsz,
        device=device,
    )
    ok = (
        checks["model_path"]["ok"]
        and checks["video_path"]["ok"]
        and checks["output_dir"]["ok"]
        and checks["ultralytics"]["available"]
        and checks["cv2"]["available"]
    )
    return {
        "ok": ok,
        "model_path": str(model_path),
        "video_path": str(video_path),
        "output_dir": str(output_dir),
        "checks": checks,
        "commands": commands,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_preflight(
        model_path=args.model,
        video_path=args.video,
        output_dir=args.output_dir,
        video_id=args.video_id,
        run_name=args.run_name,
        conf=args.conf,
        imgsz=args.imgsz,
        device=args.device,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


def _path_check(callback) -> dict[str, Any]:
    try:
        path = callback()
    except (FileNotFoundError, ValueError) as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "path": str(path)}


def _quote(value: str | Path) -> str:
    return shlex.quote(str(value))


if __name__ == "__main__":
    raise SystemExit(main())
