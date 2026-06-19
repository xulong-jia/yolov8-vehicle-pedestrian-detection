import csv
import json

import pytest

from src.tracking.track_writer import COUNT_EVENTS_FIELDS, ROI_FRAME_COUNTS_FIELDS
from src.services.video_analysis_job import (
    build_video_analysis_summary,
    create_video_analysis_job_run,
    load_csv_rows,
)


def test_load_csv_rows_returns_dict_rows_and_empty_for_header_only(tmp_path):
    detections_csv = tmp_path / "detections.csv"
    _write_csv(
        detections_csv,
        ["video_id", "frame_index", "detection_id"],
        [
            {"video_id": "demo", "frame_index": 0, "detection_id": "1"},
            {"video_id": "demo", "frame_index": 1, "detection_id": "1"},
        ],
    )
    empty_csv = tmp_path / "empty.csv"
    _write_csv(empty_csv, ["video_id", "frame_index", "detection_id"], [])

    rows = load_csv_rows(detections_csv)

    assert rows == [
        {"video_id": "demo", "frame_index": "0", "detection_id": "1"},
        {"video_id": "demo", "frame_index": "1", "detection_id": "1"},
    ]
    assert load_csv_rows(empty_csv) == []


def test_load_csv_rows_raises_for_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_csv_rows(tmp_path / "missing.csv")


def test_build_video_analysis_summary_counts_rows_and_unique_tracks():
    detections = [
        {"video_id": "demo", "detection_id": "1"},
        {"video_id": "demo", "detection_id": "2"},
    ]
    tracks = [
        {"video_id": "demo", "track_id": "1"},
        {"video_id": "demo", "track_id": "1"},
    ]
    metadata = {
        "video_id": "demo",
        "input_video": "synthetic://demo",
        "mode": "two_command_smoke",
    }
    artifact_paths = {
        "detections_csv": "detections.csv",
        "tracks_csv": "tracks.csv",
    }

    summary = build_video_analysis_summary(
        run_name="demo_run",
        metadata=metadata,
        detections=detections,
        tracks=tracks,
        artifact_paths=artifact_paths,
    )

    assert summary["video_id"] == "demo"
    assert summary["run_name"] == "demo_run"
    assert summary["created_at"]
    assert summary["input_video"] == "synthetic://demo"
    assert summary["mode"] == "two_command_smoke"
    assert summary["artifact_paths"] == artifact_paths
    assert summary["detection_count"] == 2
    assert summary["track_row_count"] == 2
    assert summary["track_count"] == 1
    assert summary["count_summary"] == {}
    assert summary["roi_summary"] == {}
    assert summary["event_summary"] == {}
    assert summary["bad_case_links"] == []


def test_create_video_analysis_job_run_copies_artifacts_and_writes_summary(tmp_path):
    source_dir = tmp_path / "source"
    detections_csv = source_dir / "detections.csv"
    tracks_csv = source_dir / "tracks.csv"
    _write_csv(
        detections_csv,
        ["video_id", "frame_index", "detection_id", "class_name"],
        [
            {"video_id": "demo", "frame_index": 0, "detection_id": "1", "class_name": "Car"},
            {"video_id": "demo", "frame_index": 1, "detection_id": "1", "class_name": "Car"},
        ],
    )
    _write_csv(
        tracks_csv,
        ["video_id", "frame_index", "track_id", "class_name", "tracker_name"],
        [
            {
                "video_id": "demo",
                "frame_index": 0,
                "track_id": "1",
                "class_name": "Car",
                "tracker_name": "synthetic",
            },
            {
                "video_id": "demo",
                "frame_index": 1,
                "track_id": "1",
                "class_name": "Car",
                "tracker_name": "synthetic",
            },
        ],
    )
    base_dir = tmp_path / "video_analysis"

    summary = create_video_analysis_job_run(
        run_name="demo_run",
        base_dir=base_dir,
        detections_csv=detections_csv,
        tracks_csv=tracks_csv,
        metadata={
            "video_id": "demo",
            "input_video": "synthetic://demo",
            "mode": "two_command_smoke",
        },
    )

    run_dir = base_dir / "demo_run"
    metadata_json = run_dir / "metadata.json"
    copied_detections = run_dir / "detections.csv"
    copied_tracks = run_dir / "tracks.csv"
    summary_json = run_dir / "video_analysis_summary.json"
    assert metadata_json.exists()
    assert copied_detections.exists()
    assert copied_tracks.exists()
    assert summary_json.exists()
    assert "demo,0,1,Car" in copied_detections.read_text(encoding="utf-8")
    assert "demo,0,1,Car,synthetic" in copied_tracks.read_text(encoding="utf-8")
    assert summary["artifact_paths"] == {
        "metadata_json": "metadata.json",
        "detections_csv": "detections.csv",
        "tracks_csv": "tracks.csv",
        "video_analysis_summary_json": "video_analysis_summary.json",
    }
    assert summary["detection_count"] == 2
    assert summary["track_row_count"] == 2
    assert summary["track_count"] == 1
    assert json.loads(summary_json.read_text(encoding="utf-8")) == summary
    metadata = json.loads(metadata_json.read_text(encoding="utf-8"))
    assert metadata["artifact_paths"] == summary["artifact_paths"]
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()
    assert not (tmp_path / "runs").exists()


def test_create_video_analysis_job_run_executes_analytics_on_existing_tracks(tmp_path):
    source_dir = tmp_path / "source"
    detections_csv = source_dir / "detections.csv"
    tracks_csv = source_dir / "tracks.csv"
    _write_csv(
        detections_csv,
        ["video_id", "frame_index", "detection_id", "class_name"],
        [
            {"video_id": "demo", "frame_index": 0, "detection_id": "car-0", "class_name": "Car"},
            {"video_id": "demo", "frame_index": 0, "detection_id": "person-0", "class_name": "Person"},
        ],
    )
    _write_csv(tracks_csv, _track_fieldnames(), _analytics_track_rows())

    summary = create_video_analysis_job_run(
        run_name="analytics_run",
        base_dir=tmp_path / "video_analysis",
        detections_csv=detections_csv,
        tracks_csv=tracks_csv,
        metadata={
            "video_id": "demo",
            "input_video": "synthetic://analytics",
            "mode": "three_step_smoke",
        },
        analytics_config=_analytics_config(),
        run_analytics=True,
    )

    run_dir = tmp_path / "video_analysis" / "analytics_run"
    metadata_json = run_dir / "metadata.json"
    count_events_csv = run_dir / "count_events.csv"
    roi_frame_counts_csv = run_dir / "roi_frame_counts.csv"
    events_jsonl = run_dir / "events.jsonl"
    summary_json = run_dir / "video_analysis_summary.json"

    for artifact in [
        metadata_json,
        run_dir / "detections.csv",
        run_dir / "tracks.csv",
        count_events_csv,
        roi_frame_counts_csv,
        events_jsonl,
        summary_json,
    ]:
        assert artifact.exists()

    count_rows = load_csv_rows(count_events_csv)
    assert count_rows
    with count_events_csv.open(newline="", encoding="utf-8") as file:
        assert next(csv.reader(file)) == COUNT_EVENTS_FIELDS

    roi_rows = load_csv_rows(roi_frame_counts_csv)
    assert roi_rows
    with roi_frame_counts_csv.open(newline="", encoding="utf-8") as file:
        assert next(csv.reader(file)) == ROI_FRAME_COUNTS_FIELDS

    events = [
        json.loads(line)
        for line in events_jsonl.read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert events
    assert all(isinstance(event["evidence"], dict) for event in events)
    assert {"long_stay", "wrong_direction"} & {event["event_type"] for event in events}

    assert summary["count_summary"]["total_count"] >= 1
    assert summary["roi_summary"]["frames_observed"] >= 1
    assert summary["event_summary"]["total_events"] >= 1
    assert summary["artifact_paths"] == {
        "metadata_json": "metadata.json",
        "detections_csv": "detections.csv",
        "tracks_csv": "tracks.csv",
        "count_events_csv": "count_events.csv",
        "roi_frame_counts_csv": "roi_frame_counts.csv",
        "events_jsonl": "events.jsonl",
        "video_analysis_summary_json": "video_analysis_summary.json",
    }
    assert json.loads(summary_json.read_text(encoding="utf-8")) == summary
    assert json.loads(metadata_json.read_text(encoding="utf-8"))["artifact_paths"] == summary[
        "artifact_paths"
    ]
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()
    assert not (tmp_path / "runs").exists()


def test_create_video_analysis_job_run_keeps_analytics_disabled_by_default(tmp_path):
    detections_csv = tmp_path / "detections.csv"
    tracks_csv = tmp_path / "tracks.csv"
    _write_csv(detections_csv, ["video_id", "frame_index", "detection_id"], [])
    _write_csv(tracks_csv, _track_fieldnames(), _analytics_track_rows())

    summary = create_video_analysis_job_run(
        run_name="no_analytics",
        base_dir=tmp_path / "video_analysis",
        detections_csv=detections_csv,
        tracks_csv=tracks_csv,
        analytics_config=_analytics_config(),
    )

    run_dir = tmp_path / "video_analysis" / "no_analytics"
    assert not (run_dir / "count_events.csv").exists()
    assert not (run_dir / "roi_frame_counts.csv").exists()
    assert not (run_dir / "events.jsonl").exists()
    assert summary["count_summary"] == {}
    assert summary["roi_summary"] == {}
    assert summary["event_summary"] == {}


def test_create_video_analysis_job_run_handles_empty_tracks_with_analytics(tmp_path):
    detections_csv = tmp_path / "detections.csv"
    tracks_csv = tmp_path / "tracks.csv"
    _write_csv(detections_csv, ["video_id", "frame_index", "detection_id"], [])
    _write_csv(tracks_csv, _track_fieldnames(), [])

    summary = create_video_analysis_job_run(
        run_name="empty_tracks",
        base_dir=tmp_path / "video_analysis",
        detections_csv=detections_csv,
        tracks_csv=tracks_csv,
        analytics_config=_analytics_config(),
        run_analytics=True,
    )

    run_dir = tmp_path / "video_analysis" / "empty_tracks"
    assert load_csv_rows(run_dir / "count_events.csv") == []
    assert load_csv_rows(run_dir / "roi_frame_counts.csv") == []
    assert (run_dir / "events.jsonl").read_text(encoding="utf-8") == ""
    assert summary["count_summary"]["total_count"] == 0
    assert summary["roi_summary"]["frames_observed"] == 0
    assert summary["event_summary"]["total_events"] == 0
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()
    assert not (tmp_path / "runs").exists()


@pytest.mark.parametrize("run_name", ["../bad", ""])
def test_create_video_analysis_job_run_rejects_unsafe_run_name(tmp_path, run_name):
    detections_csv = tmp_path / "detections.csv"
    tracks_csv = tmp_path / "tracks.csv"
    _write_csv(detections_csv, ["video_id"], [])
    _write_csv(tracks_csv, ["video_id"], [])

    with pytest.raises(ValueError):
        create_video_analysis_job_run(run_name, tmp_path / "base", detections_csv, tracks_csv)


def _write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _track_fieldnames():
    return [
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
        "line_id",
        "direction",
    ]


def _analytics_track_rows():
    return [
        _track_row("car-1", 0, 0.0, 5, -1, class_id=1, class_name="Car", line_id="line_main"),
        _track_row(
            "car-1",
            1,
            1.0,
            5,
            1,
            class_id=1,
            class_name="Car",
            line_id="line_main",
            direction="out",
        ),
        _track_row("person-1", 0, 0.0, 5, 5, class_id=3, class_name="Person", roi_id="roi_main"),
        _track_row("person-1", 1, 1.0, 5, 5, class_id=3, class_name="Person", roi_id="roi_main"),
        _track_row("person-1", 2, 2.0, 5, 5, class_id=3, class_name="Person", roi_id="roi_main"),
    ]


def _track_row(
    track_id,
    frame_index,
    timestamp_sec,
    center_x,
    center_y,
    class_id,
    class_name,
    roi_id="",
    line_id="",
    direction="",
):
    return {
        "video_id": "demo",
        "frame_index": frame_index,
        "timestamp_sec": timestamp_sec,
        "track_id": track_id,
        "class_id": class_id,
        "class_name": class_name,
        "confidence": 0.9,
        "xmin": center_x - 0.5,
        "ymin": center_y - 0.5,
        "xmax": center_x + 0.5,
        "ymax": center_y + 0.5,
        "center_x": center_x,
        "center_y": center_y,
        "box_width": 1.0,
        "box_height": 1.0,
        "box_area": 1.0,
        "state": "confirmed",
        "tracker_name": "synthetic",
        "roi_id": roi_id,
        "line_id": line_id,
        "direction": direction,
    }


def _analytics_config():
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
            "polygon": [[0, 0], [10, 0], [10, 10], [0, 10]],
            "target_classes": ["Car", "Person"],
            "enabled": True,
        },
        "event_rules": {
            "long_stay": {
                "id": "long_stay_main",
                "event_type": "long_stay",
                "enabled": True,
                "roi_id": "roi_main",
                "target_classes": ["Car", "Person"],
                "parameters": {"min_duration_sec": 2.0, "cooldown_sec": 10.0},
            },
            "wrong_direction": {
                "id": "wrong_direction_main",
                "event_type": "wrong_direction",
                "enabled": True,
                "line_id": "line_main",
                "target_classes": ["Car"],
                "parameters": {
                    "expected_direction": "in",
                    "min_track_length": 2,
                    "min_displacement_px": 1.0,
                    "cooldown_sec": 10.0,
                },
            },
        },
    }
