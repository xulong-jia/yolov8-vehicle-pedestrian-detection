"""Re-run analytics on existing detections.csv and tracks.csv artifacts.

This module only organizes existing CSV inputs and re-executes analytics with a
provided config. It does not run YOLO, does not run a tracker, and does not
render tracked video.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from src.services.video_analysis_job import create_video_analysis_job_run


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Re-run analytics on existing detections.csv and tracks.csv artifacts."
    )
    parser.add_argument("--detections-csv", required=True, type=Path)
    parser.add_argument("--tracks-csv", required=True, type=Path)
    parser.add_argument("--config-json", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--video-id", default="demo")
    parser.add_argument("--run-name", default="analytics_rerun")
    parser.add_argument("--source-run-dir", type=Path)
    return parser.parse_args(argv)


def load_json(path: str | Path) -> dict[str, Any]:
    json_path = _existing_file(path, "config_json")
    with json_path.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"config_json must contain a JSON object: {json_path}")
    return data


def extract_analytics_config(config_json: dict[str, Any]) -> dict[str, Any]:
    candidate = config_json.get("suggested_config", config_json)
    if not isinstance(candidate, dict):
        raise ValueError("analytics config must be a JSON object")

    lines = candidate.get("lines", [])
    rois = candidate.get("rois", [])
    event_rules = candidate.get("event_rules", {})
    if lines is None:
        lines = []
    if rois is None:
        rois = []
    if event_rules is None:
        event_rules = {}
    if not isinstance(lines, list):
        raise ValueError("analytics config lines must be a list")
    if not isinstance(rois, list):
        raise ValueError("analytics config rois must be a list")
    if not isinstance(event_rules, dict):
        raise ValueError("analytics config event_rules must be an object")

    normalized_lines = [_normalize_line_config(line) for line in lines]
    normalized_rois = [_normalize_roi_config(roi) for roi in rois]
    normalized: dict[str, Any] = {
        "lines": normalized_lines,
        "rois": normalized_rois,
        "event_rules": event_rules,
    }
    if normalized_lines:
        normalized["line"] = normalized_lines[0]
    if normalized_rois:
        normalized["roi"] = normalized_rois[0]
    return normalized


def build_rerun_metadata(
    video_id: str,
    source_run_dir: str | Path | None = None,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    return {
        "video_id": video_id,
        "mode": "analytics_only_rerun",
        "input_video": "",
        "source_run_dir": str(source_run_dir) if source_run_dir else "",
        "config_json": str(config_path) if config_path else "",
        "tracker": "from_existing_tracks",
    }


def run_analytics_only_rerun(
    detections_csv: str | Path,
    tracks_csv: str | Path,
    config_json: dict[str, Any],
    output_dir: str | Path,
    run_name: str = "analytics_rerun",
    video_id: str = "demo",
    source_run_dir: str | Path | None = None,
    config_path: str | Path | None = None,
) -> dict[str, Any]:
    detections_path = _existing_file(detections_csv, "detections_csv")
    tracks_path = _existing_file(tracks_csv, "tracks_csv")
    output_path = Path(output_dir).expanduser().resolve()
    _validate_output_dir(output_path, detections_path, tracks_path)

    analytics_config = extract_analytics_config(config_json)
    metadata = build_rerun_metadata(
        video_id=video_id,
        source_run_dir=source_run_dir,
        config_path=config_path,
    )
    summary = create_video_analysis_job_run(
        run_name=run_name,
        base_dir=output_path,
        detections_csv=detections_path,
        tracks_csv=tracks_path,
        metadata=metadata,
        analytics_config=analytics_config,
        run_analytics=True,
    )
    summary.update(
        {
            "mode": "analytics_only_rerun",
            "config_json": str(config_path or ""),
            "detections_csv": str(detections_path),
            "tracks_csv": str(tracks_path),
            "output_dir": str(output_path),
        }
    )
    summary_path = output_path / run_name / "video_analysis_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config_json = load_json(args.config_json)
        summary = run_analytics_only_rerun(
            detections_csv=args.detections_csv,
            tracks_csv=args.tracks_csv,
            config_json=config_json,
            output_dir=args.output_dir,
            run_name=args.run_name,
            video_id=args.video_id,
            source_run_dir=args.source_run_dir,
            config_path=args.config_json,
        )
    except (FileNotFoundError, ValueError) as exc:
        error = {"ok": False, "error": str(exc)}
        print(json.dumps(error, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def _existing_file(path: str | Path, name: str) -> Path:
    file_path = Path(path).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(f"{name} not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"{name} must be a file: {file_path}")
    return file_path


def _validate_output_dir(output_dir: Path, detections_csv: Path, tracks_csv: Path) -> None:
    if output_dir == detections_csv.parent:
        raise ValueError("output_dir must not be the detections_csv input directory")
    if output_dir == tracks_csv.parent:
        raise ValueError("output_dir must not be the tracks_csv input directory")


def _normalize_line_config(line: Any) -> dict[str, Any]:
    if not isinstance(line, dict):
        raise ValueError("each line config must be an object")
    normalized = dict(line)
    if "id" not in normalized and "line_id" in normalized:
        normalized["id"] = normalized["line_id"]
    return normalized


def _normalize_roi_config(roi: Any) -> dict[str, Any]:
    if not isinstance(roi, dict):
        raise ValueError("each ROI config must be an object")
    normalized = dict(roi)
    if "id" not in normalized and "roi_id" in normalized:
        normalized["id"] = normalized["roi_id"]
    return normalized


if __name__ == "__main__":
    raise SystemExit(main())
