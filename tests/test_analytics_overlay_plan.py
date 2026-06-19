import csv
import json
import subprocess
import sys
from pathlib import Path

from src.analytics_overlay_plan import (
    bottom_center,
    bbox_center,
    build_overlay_plan,
    extract_analytics_config,
    load_json,
    point_in_bounds,
    summarize_coordinate_space,
    validate_line,
    validate_roi,
)


TRACK_FIELDS = [
    "video_id",
    "frame_index",
    "timestamp_sec",
    "track_id",
    "class_name",
    "xmin",
    "ymin",
    "xmax",
    "ymax",
]


def test_extract_analytics_config_supports_full_suggester_json():
    config = extract_analytics_config(
        {
            "summary": {"row_count": 3},
            "suggested_config": {
                "lines": [{"line_id": "line_main", "points": [[10, 80], [90, 80]]}],
                "rois": [{"roi_id": "roi_main", "polygon": [[10, 50], [90, 50], [90, 120]]}],
                "event_rules": {"long_stay": {"enabled": True}},
            },
        }
    )

    assert config["lines"][0]["line_id"] == "line_main"
    assert config["rois"][0]["roi_id"] == "roi_main"
    assert config["event_rules"]["long_stay"]["enabled"] is True


def test_extract_analytics_config_supports_direct_config():
    config = extract_analytics_config(
        {
            "lines": [{"id": "line_direct", "points": [[10, 80], [90, 80]]}],
            "rois": [{"id": "roi_direct", "polygon": [[10, 50], [90, 50], [90, 120]]}],
            "event_rules": {},
        }
    )

    assert config["lines"][0]["id"] == "line_direct"
    assert config["rois"][0]["id"] == "roi_direct"
    assert config["event_rules"] == {}


def test_coordinate_helpers_and_summary(tmp_path):
    tracks_csv = _write_tracks_csv(tmp_path / "tracks.csv")
    rows = _load_rows(tracks_csv)

    assert bbox_center(rows[0]) == (20, 50)
    assert bottom_center(rows[0]) == (20, 70)

    summary = summarize_coordinate_space(rows)
    assert summary["row_count"] == 4
    assert summary["track_count"] == 2
    assert summary["class_counts"] == {"Car": 1, "Person": 3}
    assert summary["frame_min"] == 0
    assert summary["frame_max"] == 3
    assert summary["bbox_bounds"] == {
        "xmin_min": 10,
        "ymin_min": 30,
        "xmax_max": 100,
        "ymax_max": 120,
    }
    assert summary["center_bounds"] == {"x_min": 20, "x_max": 90, "y_min": 50, "y_max": 100}
    assert summary["bottom_bounds"] == {"x_min": 20, "x_max": 90, "y_min": 70, "y_max": 120}
    assert summary["percentiles"]["bottom_y"]["p50"] == 100
    assert summary["inferred_frame_bounds"] == {
        "width_hint": 100,
        "height_hint": 120,
        "note": "inferred from detection boxes, not actual video metadata",
    }


def test_point_in_bounds_accepts_bbox_and_xy_bounds():
    assert point_in_bounds((50, 50), {"xmin_min": 0, "xmax_max": 100, "ymin_min": 0, "ymax_max": 100})
    assert point_in_bounds((50, 50), {"x_min": 0, "x_max": 100, "y_min": 0, "y_max": 100})
    assert not point_in_bounds((120, 50), {"x_min": 0, "x_max": 100, "y_min": 0, "y_max": 100})


def test_validate_line_reports_orientation_and_recommendation(tmp_path):
    summary = summarize_coordinate_space(_load_rows(_write_tracks_csv(tmp_path / "tracks.csv")))

    horizontal = validate_line({"line_id": "line_h", "points": [[20, 100], [90, 100]]}, summary)
    vertical = validate_line({"line_id": "line_v", "points": [[50, 50], [50, 110]]}, summary)
    diagonal = validate_line({"line_id": "line_d", "points": [[10, 50], [100, 110]]}, summary)
    outside = validate_line({"line_id": "line_out", "points": [[500, 500], [700, 500]]}, summary)

    assert horizontal["orientation"] == "horizontal"
    assert horizontal["recommendation"] == "ok"
    assert "line_y_near_bottom_p50" in horizontal["position_notes"]
    assert vertical["orientation"] == "vertical"
    assert diagonal["orientation"] == "diagonal"
    assert outside["recommendation"] == "review"
    assert "line_outside_detected_bottom_bounds" in outside["position_notes"]


def test_validate_roi_reports_distribution_coverage(tmp_path):
    summary = summarize_coordinate_space(_load_rows(_write_tracks_csv(tmp_path / "tracks.csv")))

    inside = validate_roi(
        {
            "roi_id": "roi_main",
            "polygon": [[10, 40], [100, 40], [100, 120], [10, 120]],
            "point_mode": "bottom_center",
        },
        summary,
    )
    outside = validate_roi(
        {
            "roi_id": "roi_out",
            "polygon": [[300, 300], [400, 300], [400, 400], [300, 400]],
            "point_mode": "bottom_center",
        },
        summary,
    )

    assert inside["recommendation"] == "ok"
    assert inside["covers_center_distribution"] is True
    assert inside["covers_bottom_distribution"] is True
    assert outside["recommendation"] == "review"
    assert outside["covers_center_distribution"] is False
    assert outside["covers_bottom_distribution"] is False


def test_build_overlay_plan_contains_geometry_and_notes(tmp_path):
    tracks_csv = _write_tracks_csv(tmp_path / "tracks.csv")
    config_json = load_json(_write_config_json(tmp_path / "config.json"))

    plan = build_overlay_plan(tracks_csv, config_json, video_id="demo")

    assert plan["mode"] == "analytics_overlay_plan"
    assert plan["video_id"] == "demo"
    assert plan["coordinate_summary"]["row_count"] == 4
    assert plan["line_plans"][0]["line_id"] == "line_main"
    assert plan["roi_plans"][0]["roi_id"] == "roi_main"
    assert plan["event_rules_summary"] == {"rule_count": 1, "rule_names": ["long_stay"]}
    assert "draw line segments with line_id labels" in plan["overlay_recommendations"]
    assert "Does not render video." in plan["notes"]


def test_cli_stdout_is_json_and_does_not_create_output_file_by_default(tmp_path):
    tracks_csv = _write_tracks_csv(tmp_path / "tracks.csv")
    config_json = _write_config_json(tmp_path / "config.json")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.analytics_overlay_plan",
            "--tracks-csv",
            str(tracks_csv),
            "--config-json",
            str(config_json),
            "--video-id",
            "demo",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["mode"] == "analytics_overlay_plan"
    assert not (tmp_path / "analytics_overlay_plan.json").exists()


def test_cli_output_json_writes_only_requested_file(tmp_path):
    tracks_csv = _write_tracks_csv(tmp_path / "tracks.csv")
    config_json = _write_config_json(tmp_path / "config.json")
    output_json = tmp_path / "overlay_plan.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.analytics_overlay_plan",
            "--tracks-csv",
            str(tracks_csv),
            "--config-json",
            str(config_json),
            "--output-json",
            str(output_json),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert json.loads(output_json.read_text(encoding="utf-8"))["mode"] == "analytics_overlay_plan"
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "runs").exists()


def test_cli_missing_input_returns_error_without_partial_output(tmp_path):
    output_json = tmp_path / "overlay_plan.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.analytics_overlay_plan",
            "--tracks-csv",
            str(tmp_path / "missing.csv"),
            "--config-json",
            str(tmp_path / "missing.json"),
            "--output-json",
            str(output_json),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "tracks_csv not found" in result.stderr
    assert not output_json.exists()


def test_module_has_no_forbidden_runtime_dependencies():
    source = Path("src/analytics_overlay_plan.py").read_text(encoding="utf-8")
    assert "cv2" not in source
    assert "numpy" not in source
    assert "torch" not in source
    assert "ultralytics" not in source


def _write_tracks_csv(path: Path) -> Path:
    rows = [
        _track_row(0, "1", "Person", 10, 30, 30, 70),
        _track_row(1, "1", "Person", 20, 50, 40, 90),
        _track_row(2, "1", "Person", 30, 70, 50, 110),
        _track_row(3, "2", "Car", 80, 80, 100, 120),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=TRACK_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _track_row(
    frame: int,
    track_id: str,
    class_name: str,
    xmin: int,
    ymin: int,
    xmax: int,
    ymax: int,
) -> dict[str, str]:
    return {
        "video_id": "demo",
        "frame_index": str(frame),
        "timestamp_sec": str(frame / 2),
        "track_id": track_id,
        "class_name": class_name,
        "xmin": str(xmin),
        "ymin": str(ymin),
        "xmax": str(xmax),
        "ymax": str(ymax),
    }


def _write_config_json(path: Path) -> Path:
    payload = {
        "summary": {"row_count": 4},
        "suggested_config": {
            "lines": [
                {
                    "line_id": "line_main",
                    "points": [[10, 80], [100, 80]],
                }
            ],
            "rois": [
                {
                    "roi_id": "roi_main",
                    "polygon": [[10, 40], [100, 40], [100, 125], [10, 125]],
                    "point_mode": "bottom_center",
                }
            ],
            "event_rules": {"long_stay": {"enabled": True}},
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))
