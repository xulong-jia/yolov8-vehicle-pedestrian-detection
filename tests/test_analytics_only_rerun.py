import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.analytics_only_rerun import (
    extract_analytics_config,
    load_json,
    run_analytics_only_rerun,
)


DETECTION_FIELDS = [
    "video_id",
    "frame_index",
    "timestamp_sec",
    "detection_id",
    "class_id",
    "class_name",
    "confidence",
    "xmin",
    "ymin",
    "xmax",
    "ymax",
]

TRACK_FIELDS = [
    "video_id",
    "frame_index",
    "timestamp_sec",
    "track_id",
    "class_id",
    "class_name",
    "confidence",
    "xmin",
    "ymin",
    "xmax",
    "ymax",
    "center_x",
    "center_y",
    "box_width",
    "box_height",
    "box_area",
    "state",
    "tracker_name",
    "roi_id",
]


def test_extract_analytics_config_from_full_suggester_json():
    config = extract_analytics_config(
        {
            "summary": {"row_count": 2},
            "suggested_config": {
                "lines": [{"line_id": "line_main", "points": [[0, 50], [100, 50]]}],
                "rois": [{"roi_id": "roi_main", "polygon": [[0, 0], [100, 0], [100, 100]]}],
                "event_rules": {"long_stay": {"enabled": True}},
            },
        }
    )

    assert config["lines"][0]["id"] == "line_main"
    assert config["rois"][0]["id"] == "roi_main"
    assert config["event_rules"]["long_stay"]["enabled"] is True


def test_extract_analytics_config_from_direct_config():
    config = extract_analytics_config(
        {
            "lines": [{"id": "line_a", "points": [[0, 50], [100, 50]]}],
            "rois": [{"id": "roi_a", "polygon": [[0, 0], [100, 0], [100, 100]]}],
            "event_rules": {},
        }
    )

    assert config["lines"][0]["id"] == "line_a"
    assert config["rois"][0]["id"] == "roi_a"
    assert config["event_rules"] == {}


def test_extract_analytics_config_fills_missing_optional_keys():
    assert extract_analytics_config({}) == {"lines": [], "rois": [], "event_rules": {}}


def test_extract_analytics_config_rejects_wrong_shapes():
    with pytest.raises(ValueError, match="lines must be a list"):
        extract_analytics_config({"lines": {"id": "line"}})


def test_load_json_rejects_non_object(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("[]\n", encoding="utf-8")

    with pytest.raises(ValueError, match="JSON object"):
        load_json(path)


def test_run_analytics_only_rerun_writes_fresh_analysis_artifacts(tmp_path):
    detections_csv = tmp_path / "inputs" / "detections.csv"
    tracks_csv = tmp_path / "inputs" / "tracks.csv"
    config_json = _write_config(tmp_path / "inputs" / "suggested_config.json")
    _write_detections_csv(detections_csv)
    original_tracks_text = _write_tracks_csv(tracks_csv)

    output_dir = tmp_path / "rerun_output"
    summary = run_analytics_only_rerun(
        detections_csv=detections_csv,
        tracks_csv=tracks_csv,
        config_json=load_json(config_json),
        output_dir=output_dir,
        run_name="suggested_config_rerun",
        video_id="demo",
        source_run_dir=tmp_path / "source_run",
        config_path=config_json,
    )

    run_dir = output_dir / "suggested_config_rerun"
    assert summary["mode"] == "analytics_only_rerun"
    assert summary["config_json"] == str(config_json.resolve())
    assert summary["detections_csv"] == str(detections_csv.resolve())
    assert summary["tracks_csv"] == str(tracks_csv.resolve())
    assert summary["output_dir"] == str(output_dir.resolve())
    assert summary["count_summary"]["total_count"] >= 1
    assert summary["roi_summary"]["frames_observed"] >= 1
    assert summary["event_summary"]["total_events"] >= 1

    expected_files = [
        "metadata.json",
        "detections.csv",
        "tracks.csv",
        "count_events.csv",
        "roi_frame_counts.csv",
        "events.jsonl",
        "video_analysis_summary.json",
    ]
    for filename in expected_files:
        assert (run_dir / filename).exists()

    assert _line_count(run_dir / "detections.csv") == _line_count(detections_csv)
    assert _line_count(run_dir / "tracks.csv") == _line_count(tracks_csv)
    assert tracks_csv.read_text(encoding="utf-8") == original_tracks_text

    stored_summary = json.loads((run_dir / "video_analysis_summary.json").read_text(encoding="utf-8"))
    assert stored_summary["mode"] == "analytics_only_rerun"
    assert stored_summary["count_summary"]["total_count"] >= 1


def test_run_analytics_only_rerun_rejects_output_dir_matching_input_parent(tmp_path):
    detections_csv = tmp_path / "inputs" / "detections.csv"
    tracks_csv = tmp_path / "tracks" / "tracks.csv"
    config_json = _write_config(tmp_path / "config.json")
    _write_detections_csv(detections_csv)
    _write_tracks_csv(tracks_csv)

    with pytest.raises(ValueError, match="detections_csv input directory"):
        run_analytics_only_rerun(
            detections_csv=detections_csv,
            tracks_csv=tracks_csv,
            config_json=load_json(config_json),
            output_dir=detections_csv.parent,
        )

    with pytest.raises(ValueError, match="tracks_csv input directory"):
        run_analytics_only_rerun(
            detections_csv=detections_csv,
            tracks_csv=tracks_csv,
            config_json=load_json(config_json),
            output_dir=tracks_csv.parent,
        )


def test_cli_writes_summary_json_to_stdout_and_outputs(tmp_path):
    detections_csv = tmp_path / "inputs" / "detections.csv"
    tracks_csv = tmp_path / "inputs" / "tracks.csv"
    config_json = _write_config(tmp_path / "inputs" / "suggested_config.json")
    output_dir = tmp_path / "rerun_output"
    _write_detections_csv(detections_csv)
    _write_tracks_csv(tracks_csv)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.analytics_only_rerun",
            "--detections-csv",
            str(detections_csv),
            "--tracks-csv",
            str(tracks_csv),
            "--config-json",
            str(config_json),
            "--output-dir",
            str(output_dir),
            "--video-id",
            "demo",
            "--run-name",
            "rerun",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    summary = json.loads(result.stdout)
    assert summary["mode"] == "analytics_only_rerun"
    assert (output_dir / "rerun" / "video_analysis_summary.json").exists()
    assert (output_dir / "rerun" / "count_events.csv").exists()


def test_cli_missing_input_returns_error_without_creating_output(tmp_path):
    tracks_csv = tmp_path / "tracks.csv"
    config_json = _write_config(tmp_path / "config.json")
    _write_tracks_csv(tracks_csv)
    output_dir = tmp_path / "rerun_output"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.analytics_only_rerun",
            "--detections-csv",
            str(tmp_path / "missing.csv"),
            "--tracks-csv",
            str(tracks_csv),
            "--config-json",
            str(config_json),
            "--output-dir",
            str(output_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "detections_csv not found" in result.stderr
    assert not output_dir.exists()


def test_module_does_not_reference_yolo_or_tracker_runtimes():
    source = Path("src/analytics_only_rerun.py").read_text(encoding="utf-8")
    assert "ultralytics" not in source
    assert "cv2" not in source
    assert "predict_video" not in source
    assert "track_video" not in source


def _write_detections_csv(path: Path) -> str:
    rows = [
        {
            "video_id": "demo",
            "frame_index": "0",
            "timestamp_sec": "0.0",
            "detection_id": "det_1",
            "class_id": "0",
            "class_name": "Person",
            "confidence": "0.90",
            "xmin": "0",
            "ymin": "40",
            "xmax": "20",
            "ymax": "60",
        }
    ]
    return _write_csv(path, DETECTION_FIELDS, rows)


def _write_tracks_csv(path: Path) -> str:
    rows = [
        _track_row(frame=0, timestamp=0.0, track_id="1", xmin=0, ymin=35, xmax=20, ymax=55, roi_id="roi_main"),
        _track_row(frame=1, timestamp=0.5, track_id="1", xmin=0, ymin=45, xmax=20, ymax=65, roi_id="roi_main"),
        _track_row(frame=2, timestamp=1.2, track_id="1", xmin=0, ymin=55, xmax=20, ymax=75, roi_id="roi_main"),
    ]
    return _write_csv(path, TRACK_FIELDS, rows)


def _track_row(
    frame: int,
    timestamp: float,
    track_id: str,
    xmin: int,
    ymin: int,
    xmax: int,
    ymax: int,
    roi_id: str,
) -> dict[str, str]:
    width = xmax - xmin
    height = ymax - ymin
    return {
        "video_id": "demo",
        "frame_index": str(frame),
        "timestamp_sec": str(timestamp),
        "track_id": track_id,
        "class_id": "0",
        "class_name": "Person",
        "confidence": "0.90",
        "xmin": str(xmin),
        "ymin": str(ymin),
        "xmax": str(xmax),
        "ymax": str(ymax),
        "center_x": str((xmin + xmax) / 2),
        "center_y": str((ymin + ymax) / 2),
        "box_width": str(width),
        "box_height": str(height),
        "box_area": str(width * height),
        "state": "confirmed",
        "tracker_name": "synthetic",
        "roi_id": roi_id,
    }


def _write_config(path: Path) -> Path:
    payload = {
        "summary": {"row_count": 3},
        "suggested_config": {
            "lines": [
                {
                    "line_id": "line_main",
                    "name": "Middle line",
                    "points": [[0, 50], [100, 50]],
                    "target_classes": ["Person"],
                    "directions": {"positive": "down", "negative": "up"},
                }
            ],
            "rois": [
                {
                    "roi_id": "roi_main",
                    "name": "Main ROI",
                    "polygon": [[0, 40], [100, 40], [100, 90], [0, 90]],
                    "point_mode": "bottom_center",
                    "target_classes": ["Person"],
                }
            ],
            "event_rules": {
                "long_stay": {
                    "enabled": True,
                    "event_type": "long_stay",
                    "roi_id": "roi_main",
                    "target_classes": ["Person"],
                    "severity": "warning",
                    "parameters": {"min_duration_sec": 1.0},
                }
            },
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path.read_text(encoding="utf-8")


def _line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())
