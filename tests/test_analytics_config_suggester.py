import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from src.analytics_config_suggester import (
    bbox_center,
    bottom_center,
    load_track_rows,
    percentile,
    suggest_analytics_config,
    suggest_event_rules_config,
    suggest_line_config,
    suggest_roi_config,
    summarize_tracks,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_load_track_rows_reads_tracks_csv(tmp_path):
    tracks_csv = _write_tracks_csv(tmp_path)

    rows = load_track_rows(tracks_csv)

    assert len(rows) == 6
    assert rows[0]["video_id"] == "demo"
    assert rows[0]["track_id"] == "1"


def test_geometry_helpers_compute_centers():
    row = {"xmin": "10", "ymin": "20", "xmax": "30", "ymax": "60"}

    assert bbox_center(row) == (20.0, 40.0)
    assert bottom_center(row) == (20.0, 60.0)


def test_percentile_handles_empty_and_interpolates():
    assert percentile([], 50) is None
    assert percentile([10], 50) == 10
    assert percentile([0, 10, 20, 30, 40], 50) == 20
    assert percentile([0, 10, 20, 30, 40], 10) == pytest.approx(4)
    assert percentile([0, 10, 20, 30, 40], 90) == pytest.approx(36)


def test_summarize_tracks_returns_ranges_counts_percentiles_and_samples(tmp_path):
    rows = load_track_rows(_write_tracks_csv(tmp_path))

    summary = summarize_tracks(rows)

    assert summary["row_count"] == 6
    assert summary["track_count"] == 3
    assert summary["class_counts"] == {"Car": 2, "Person": 2, "Bus": 2}
    assert summary["frame_min"] == 0
    assert summary["frame_max"] == 2
    assert summary["xmin_min"] == 10
    assert summary["xmax_max"] == 330
    assert summary["center_x_min"] == 20
    assert summary["center_x_max"] == 315
    assert summary["bottom_y_min"] == 110
    assert summary["bottom_y_max"] == 310
    assert summary["percentiles"]["center_x"]["p50"] is not None
    assert summary["percentiles"]["bottom_y"]["p90"] is not None
    assert len(summary["sample_tracks"]) == 3
    assert summary["sample_tracks"][0]["row_count"] == 2


def test_suggest_line_config_uses_bottom_distribution_and_classes(tmp_path):
    summary = summarize_tracks(load_track_rows(_write_tracks_csv(tmp_path)))

    line = suggest_line_config(summary, line_id="line_custom")

    assert line["line_id"] == "line_custom"
    assert line["name"] == "Suggested middle crossing line"
    assert len(line["points"]) == 2
    assert summary["bottom_x_min"] <= line["points"][0][0] <= summary["bottom_x_max"]
    assert summary["bottom_x_min"] <= line["points"][1][0] <= summary["bottom_x_max"]
    assert summary["bottom_y_min"] <= line["points"][0][1] <= summary["bottom_y_max"]
    assert line["target_classes"] == ["Bus", "Car", "Person"]
    assert line["state"] == "confirmed"


def test_suggest_roi_config_uses_bottom_distribution(tmp_path):
    summary = summarize_tracks(load_track_rows(_write_tracks_csv(tmp_path)))

    roi = suggest_roi_config(summary, roi_id="roi_custom")

    assert roi["roi_id"] == "roi_custom"
    assert roi["name"] == "Suggested active-area ROI"
    assert roi["point_mode"] == "bottom_center"
    assert len(roi["polygon"]) == 4
    for x, y in roi["polygon"]:
        assert summary["bottom_x_min"] <= x <= summary["bottom_x_max"]
        assert summary["bottom_y_min"] <= y <= summary["bottom_y_max"]


def test_suggest_event_rules_config_is_conservative(tmp_path):
    summary = summarize_tracks(load_track_rows(_write_tracks_csv(tmp_path)))

    rules = suggest_event_rules_config(summary)

    assert rules["long_stay"]["enabled"] is True
    assert rules["long_stay"]["parameters"]["min_duration_sec"] == 1.0
    assert "Person" in rules["crowd_warning"]["target_classes"]
    assert rules["crowd_warning"]["parameters"]["min_count"] == 5
    assert rules["wrong_direction"]["enabled"] is False


def test_suggest_analytics_config_returns_summary_config_and_notes(tmp_path):
    rows = load_track_rows(_write_tracks_csv(tmp_path))

    result = suggest_analytics_config(rows, video_id="demo")

    assert result["video_id"] == "demo"
    assert result["summary"]["row_count"] == 6
    assert result["suggested_config"]["lines"]
    assert result["suggested_config"]["rois"]
    assert "long_stay" in result["suggested_config"]["event_rules"]
    assert any("heuristic" in note for note in result["notes"])
    assert any("synthetic tracks" in note for note in result["notes"])


def test_cli_stdout_prints_json_without_creating_outputs(tmp_path):
    tracks_csv = _write_tracks_csv(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.analytics_config_suggester",
            "--tracks-csv",
            str(tracks_csv),
            "--video-id",
            "demo",
        ],
        cwd=PROJECT_ROOT,
        env=_test_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(result.stdout)

    assert result.returncode == 0
    assert payload["video_id"] == "demo"
    assert payload["summary"]["row_count"] == 6
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "runs").exists()
    assert not (tmp_path / "suggested_config.json").exists()


def test_cli_output_json_writes_requested_file_only(tmp_path):
    tracks_csv = _write_tracks_csv(tmp_path)
    output_json = tmp_path / "suggested_config.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.analytics_config_suggester",
            "--tracks-csv",
            str(tracks_csv),
            "--video-id",
            "demo",
            "--output-json",
            str(output_json),
        ],
        cwd=PROJECT_ROOT,
        env=_test_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(output_json.read_text(encoding="utf-8"))

    assert result.returncode == 0
    assert output_json.exists()
    assert payload["summary"]["track_count"] == 3
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "runs").exists()


def test_cli_missing_file_returns_error_without_outputs(tmp_path):
    output_json = tmp_path / "should_not_exist.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.analytics_config_suggester",
            "--tracks-csv",
            str(tmp_path / "missing_tracks.csv"),
            "--output-json",
            str(output_json),
        ],
        cwd=PROJECT_ROOT,
        env=_test_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(result.stdout)

    assert result.returncode == 1
    assert payload["ok"] is False
    assert "does not exist" in payload["error"]
    assert not output_json.exists()


def _write_tracks_csv(tmp_path):
    tracks_csv = tmp_path / "tracks.csv"
    tracks_csv.write_text(
        "\n".join(
            [
                "video_id,frame_index,timestamp_sec,track_id,class_id,class_name,confidence,xmin,ymin,xmax,ymax",
                "demo,0,0.0,1,1,Car,0.90,10,50,30,110",
                "demo,1,0.1,1,1,Car,0.91,20,70,40,140",
                "demo,0,0.0,2,3,Person,0.80,100,100,140,220",
                "demo,1,0.1,2,3,Person,0.81,110,120,150,240",
                "demo,1,0.1,3,0,Bus,0.70,300,150,330,300",
                "demo,2,0.2,3,0,Bus,0.71,300,160,330,310",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return tracks_csv


def _test_env():
    env = os.environ.copy()
    env["PYTHONPYCACHEPREFIX"] = "/private/tmp/yolov8_pycache"
    return env
