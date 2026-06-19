import csv
import json

import pytest

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
