"""Unified smoke runner for the existing four-step local video analysis flow.

This is a smoke runner for the current local chain:

1. predict_video exports detections.csv.
2. track_video converts detections.csv to synthetic tracks.csv.
3. video_analysis_job creates a Video Analysis Center run.
4. video_analysis_job runs analytics with run_analytics=True.

When used with a real model and source video, this script may run YOLO through
predict_video. It still uses the synthetic tracker, does not integrate real
ByteTrack/DeepSORT, does not render tracked video, and writes outputs only under
the user-provided output_dir.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.predict_video import run_video_detection_csv
from src.services.video_analysis_job import create_video_analysis_job_run
from src.track_video import run_track_video_skeleton


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the four-step video analysis smoke flow.")
    parser.add_argument("--model", required=True, help="Path to YOLO model weights.")
    parser.add_argument("--source", required=True, help="Path to input video.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Output directory.")
    parser.add_argument("--video-id", default="demo", help="Stable video_id for output rows.")
    parser.add_argument("--run-name", default="demo_run", help="Video Analysis Center run name.")
    parser.add_argument("--conf", type=float, default=0.25, help="YOLO confidence threshold.")
    parser.add_argument("--imgsz", type=int, default=640, help="YOLO image size.")
    parser.add_argument("--device", default="cpu", help="YOLO inference device.")
    return parser.parse_args(argv)


def default_smoke_analytics_config() -> dict[str, Any]:
    return {
        "line": {
            "id": "line_main",
            "name": "Main Line",
            "points": [[0, 0], [10, 0]],
            "directions": {"positive": "in", "negative": "out"},
            "target_classes": ["Car", "Person"],
            "enabled": True,
        },
        "roi": {
            "id": "roi_main",
            "name": "Main ROI",
            "polygon": [[0, 0], [20, 0], [20, 30], [0, 30]],
            "target_classes": ["Car", "Person"],
            "enabled": True,
        },
        "event_rules": {
            "crowd_warning": {
                "id": "crowd_warning_main",
                "event_type": "crowd_warning",
                "enabled": True,
                "roi_id": "roi_main",
                "target_classes": ["Car", "Person"],
                "parameters": {"min_count": 1, "min_duration_sec": 0.1, "cooldown_sec": 10.0},
            },
            "long_stay": {
                "id": "long_stay_main",
                "event_type": "long_stay",
                "enabled": True,
                "roi_id": "roi_main",
                "target_classes": ["Car", "Person"],
                "parameters": {"min_duration_sec": 0.1, "cooldown_sec": 10.0},
            },
        },
    }


def run_four_step_smoke(
    model_path: str | Path,
    source: str | Path,
    output_dir: str | Path,
    video_id: str = "demo",
    conf: float = 0.25,
    imgsz: int = 640,
    device: str = "cpu",
    run_name: str = "demo_run",
    analytics_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    detections_csv = output_path / "detections.csv"
    tracking_dir = output_path / "tracking"
    video_analysis_dir = output_path / "video_analysis"

    run_video_detection_csv(
        model_path=model_path,
        source=source,
        output_csv=detections_csv,
        conf=conf,
        imgsz=imgsz,
        device=device,
        video_id=video_id,
    )
    run_track_video_skeleton(
        input_csv=detections_csv,
        output_dir=tracking_dir,
        tracker_name="synthetic",
    )

    summary = create_video_analysis_job_run(
        run_name=run_name,
        base_dir=video_analysis_dir,
        detections_csv=detections_csv,
        tracks_csv=tracking_dir / "tracks.csv",
        metadata={
            "video_id": video_id,
            "input_video": str(source),
            "mode": "four_step_smoke_runner",
            "tracker": "synthetic",
        },
        analytics_config=analytics_config or default_smoke_analytics_config(),
        run_analytics=True,
    )
    summary.update(
        {
            "detections_csv": str(detections_csv),
            "tracks_csv": str(tracking_dir / "tracks.csv"),
            "video_analysis_dir": str(video_analysis_dir),
        }
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    summary = run_four_step_smoke(
        model_path=args.model,
        source=args.source,
        output_dir=args.output_dir,
        video_id=args.video_id,
        conf=args.conf,
        imgsz=args.imgsz,
        device=args.device,
        run_name=args.run_name,
    )
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
