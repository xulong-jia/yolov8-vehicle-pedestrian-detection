"""Tests for video analytics GT evaluation scaffold."""

from __future__ import annotations

import csv
import json
import subprocess
import sys


def _write_csv(path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row) + "\n")


def test_counting_eval_computes_abs_error_and_mae():
    from src.evaluation.video_eval_scaffold import evaluate_counting

    metrics = evaluate_counting(
        pred_rows=[{"count": "3"}, {"count": "2"}],
        gt_rows=[{"count": "4"}],
    )

    assert metrics == {
        "gt_count": 4,
        "pred_count": 5,
        "abs_error": 1,
        "MAE": 1.0,
    }


def test_roi_eval_computes_frame_count_mae():
    from src.evaluation.video_eval_scaffold import evaluate_roi

    metrics = evaluate_roi(
        pred_rows=[
            {"video_id": "demo", "roi_id": "crosswalk", "frame_index": "1", "count": "3"},
            {"video_id": "demo", "roi_id": "crosswalk", "frame_index": "2", "count": "1"},
        ],
        gt_rows=[
            {"video_id": "demo", "roi_id": "crosswalk", "frame_index": "1", "count": "2"},
            {"video_id": "demo", "roi_id": "crosswalk", "frame_index": "2", "count": "3"},
        ],
    )

    assert metrics["compared_rows"] == 2
    assert metrics["frame_count_mae"] == 1.5


def test_event_eval_matches_event_type_with_time_window():
    from src.evaluation.video_eval_scaffold import evaluate_events

    metrics = evaluate_events(
        pred_rows=[
            {"event_type": "wrong_direction", "timestamp_sec": 10.4},
            {"event_type": "crowd_warning", "timestamp_sec": 20.0},
        ],
        gt_rows=[
            {"event_type": "wrong_direction", "timestamp_sec": 10.0},
            {"event_type": "long_stay", "timestamp_sec": 30.0},
        ],
        time_window_sec=0.5,
    )

    assert metrics["gt_events"] == 2
    assert metrics["pred_events"] == 2
    assert metrics["matched_events"] == 1
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5


def test_tracking_engineering_metrics_without_gt():
    from src.evaluation.video_eval_scaffold import evaluate_tracking_engineering

    metrics = evaluate_tracking_engineering(
        [
            {"track_id": "1"},
            {"track_id": "1"},
            {"track_id": "1"},
            {"track_id": "2"},
        ]
    )

    assert metrics["track_count"] == 2
    assert metrics["avg_track_length"] == 2.0
    assert metrics["short_track_ratio"] == 0.5
    assert metrics["gt_required_for_idf1"] is True


def test_video_eval_scaffold_writes_outputs_and_creates_output_dir(tmp_path):
    from src.evaluation.video_eval_scaffold import run_video_eval_scaffold

    pred_count = tmp_path / "pred_count_events.csv"
    gt_count = tmp_path / "gt_count_events.csv"
    pred_roi = tmp_path / "pred_roi_frame_counts.csv"
    gt_roi = tmp_path / "gt_roi_frame_counts.csv"
    pred_tracks = tmp_path / "tracks.csv"
    pred_events = tmp_path / "events.jsonl"
    gt_events = tmp_path / "gt_events.jsonl"
    output_dir = tmp_path / "nested" / "eval"

    _write_csv(pred_count, ["count"], [{"count": "5"}])
    _write_csv(gt_count, ["count"], [{"count": "3"}])
    _write_csv(
        pred_roi,
        ["video_id", "roi_id", "frame_index", "count"],
        [{"video_id": "demo", "roi_id": "r1", "frame_index": "1", "count": "2"}],
    )
    _write_csv(
        gt_roi,
        ["video_id", "roi_id", "frame_index", "count"],
        [{"video_id": "demo", "roi_id": "r1", "frame_index": "1", "count": "1"}],
    )
    _write_csv(
        pred_tracks,
        ["track_id", "frame_index"],
        [{"track_id": "1", "frame_index": "1"}, {"track_id": "1", "frame_index": "2"}],
    )
    _write_jsonl(pred_events, [{"event_type": "wrong_direction", "timestamp_sec": 1.0}])
    _write_jsonl(gt_events, [{"event_type": "wrong_direction", "timestamp_sec": 1.2}])

    summary = run_video_eval_scaffold(
        pred_tracks=pred_tracks,
        pred_count_events=pred_count,
        pred_roi_counts=pred_roi,
        pred_events=pred_events,
        gt_count_events=gt_count,
        gt_roi_counts=gt_roi,
        gt_events=gt_events,
        output_dir=output_dir,
    )

    assert summary["counting"]["MAE"] == 2.0
    assert summary["roi"]["frame_count_mae"] == 1.0
    assert summary["event"]["matched_events"] == 1
    for filename in [
        "evaluation_summary.json",
        "counting_metrics.csv",
        "roi_metrics.csv",
        "event_metrics.csv",
        "tracking_metrics.csv",
    ]:
        assert (output_dir / filename).is_file()


def test_video_eval_scaffold_cli_help_runs():
    result = subprocess.run(
        [sys.executable, "-m", "src.evaluation.video_eval_scaffold", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--pred-tracks" in result.stdout
    assert "--gt-events" in result.stdout
    assert "--output-dir" in result.stdout
