import json

import pytest

from src.tracking.track_writer import TRACKS_FIELDS
from src.services.synthetic_video_analysis_pipeline import (
    build_synthetic_tracks,
    run_synthetic_video_analysis,
)


def test_build_synthetic_tracks_returns_contract_rows_for_pipeline_scenarios():
    rows = build_synthetic_tracks()

    assert rows
    for row in rows:
        for field in TRACKS_FIELDS:
            assert field in row

    assert any(row["class_name"] == "Car" and row["track_id"] == "car_cross" for row in rows)
    assert any(row["class_name"] == "Person" and row.get("roi_id") == "roi_main" for row in rows)
    assert any(
        row["class_name"] == "Car"
        and row.get("direction") == "out"
        and row.get("line_id") == "line_main"
        for row in rows
    )
    assert any(row.get("roi_id") == "roi_main" and row["timestamp_sec"] >= 5.0 for row in rows)


def test_run_synthetic_video_analysis_writes_expected_artifacts(tmp_path):
    run_name = "synthetic_run"
    base_dir = tmp_path / "video_analysis"

    summary = run_synthetic_video_analysis(run_name, base_dir)

    run_dir = base_dir / run_name
    assert (run_dir / "metadata.json").exists()
    assert (run_dir / "tracks.csv").exists()
    assert (run_dir / "count_events.csv").exists()
    assert (run_dir / "roi_frame_counts.csv").exists()
    assert (run_dir / "events.jsonl").exists()
    assert (run_dir / "video_analysis_summary.json").exists()
    assert summary == json.loads((run_dir / "video_analysis_summary.json").read_text(encoding="utf-8"))


def test_run_synthetic_video_analysis_summary_contains_expected_contract(tmp_path):
    summary = run_synthetic_video_analysis("summary_run", tmp_path / "video_analysis")

    for field in (
        "video_id",
        "run_name",
        "created_at",
        "input_video",
        "config_paths",
        "artifact_paths",
        "detection_count",
        "track_count",
        "count_summary",
        "roi_summary",
        "event_summary",
        "bad_case_links",
    ):
        assert field in summary

    assert summary["video_id"] == "synthetic_demo"
    assert summary["run_name"] == "summary_run"
    assert summary["input_video"] == "synthetic://toy_tracks"
    assert summary["config_paths"] == {"analytics": "synthetic_default"}
    assert summary["detection_count"] == 0
    assert summary["track_count"] > 0
    assert summary["count_summary"]["total_count"] >= 1
    assert summary["roi_summary"]["frames_observed"] >= 1
    assert summary["event_summary"]["total_events"] >= 1
    assert summary["bad_case_links"] == []
    assert summary["artifact_paths"]["tracks_csv"] == "tracks.csv"
    assert summary["artifact_paths"]["count_events_csv"] == "count_events.csv"
    assert summary["artifact_paths"]["roi_frame_counts_csv"] == "roi_frame_counts.csv"
    assert summary["artifact_paths"]["events_jsonl"] == "events.jsonl"


def test_run_synthetic_video_analysis_events_jsonl_contains_evidence(tmp_path):
    run_name = "events_run"
    base_dir = tmp_path / "video_analysis"

    run_synthetic_video_analysis(run_name, base_dir)

    events_path = base_dir / run_name / "events.jsonl"
    lines = events_path.read_text(encoding="utf-8").splitlines()
    assert lines
    events = [json.loads(line) for line in lines]
    assert all(isinstance(event["evidence"], dict) for event in events)
    event_types = {event["event_type"] for event in events}
    assert event_types & {"long_stay", "wrong_direction"}


def test_run_synthetic_video_analysis_uses_tmp_path_only(tmp_path):
    run_name = "tmp_only_run"
    base_dir = tmp_path / "video_analysis"

    run_synthetic_video_analysis(run_name, base_dir)

    assert base_dir.exists()
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()
    assert not (tmp_path / "runs").exists()


def test_run_synthetic_video_analysis_rejects_unsafe_run_name(tmp_path):
    with pytest.raises(ValueError):
        run_synthetic_video_analysis("../bad", tmp_path / "video_analysis")
