import json

import pytest

from src.services.video_analysis_center import VideoAnalysisCenter


def test_create_run_creates_run_directory_and_metadata(tmp_path):
    center = VideoAnalysisCenter(tmp_path / "video_analysis")

    run_dir = center.create_run(
        "demo_run",
        metadata={
            "input_video": "demo.mp4",
            "config_paths": {
                "tracking": "configs/tracking.yaml",
                "analytics": "configs/analytics.yaml",
            },
        },
    )

    assert run_dir == tmp_path / "video_analysis" / "demo_run"
    metadata_path = run_dir / "metadata.json"
    assert metadata_path.exists()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["run_name"] == "demo_run"
    assert metadata["created_at"]
    assert metadata["input_video"] == "demo.mp4"
    assert metadata["config_paths"]["tracking"] == "configs/tracking.yaml"
    assert metadata["artifact_paths"] == {}


def test_writers_use_fixed_artifact_filenames(tmp_path):
    center = VideoAnalysisCenter(tmp_path / "video_analysis")
    center.create_run("demo_run")

    tracks_path = center.write_tracks("demo_run", [{"video_id": "video-1", "track_id": "t-1"}])
    count_events_path = center.write_count_events(
        "demo_run",
        [{"video_id": "video-1", "line_id": "entry_line", "track_id": "t-1"}],
    )
    roi_counts_path = center.write_roi_counts(
        "demo_run",
        [{"video_id": "video-1", "roi_id": "crosswalk", "object_count": 1}],
    )
    events_path = center.write_events(
        "demo_run",
        [{"event_id": "event-1", "event_type": "crowd_warning", "evidence": {"max_count": 4}}],
    )
    summary_path = center.write_summary(
        "demo_run",
        {
            "video_id": "video-1",
            "run_name": "demo_run",
            "artifact_paths": {
                "tracks": "tracks.csv",
                "count_events": "count_events.csv",
                "roi_frame_counts": "roi_frame_counts.csv",
                "events": "events.jsonl",
            },
        },
    )

    assert tracks_path.name == "tracks.csv"
    assert count_events_path.name == "count_events.csv"
    assert roi_counts_path.name == "roi_frame_counts.csv"
    assert events_path.name == "events.jsonl"
    assert summary_path.name == "video_analysis_summary.json"
    assert (center.get_run_dir("demo_run") / "tracks.csv").exists()
    assert (center.get_run_dir("demo_run") / "events.jsonl").exists()


def test_read_summary_returns_written_summary(tmp_path):
    center = VideoAnalysisCenter(tmp_path / "video_analysis")
    center.create_run("demo_run")
    summary = {
        "video_id": "video-1",
        "run_name": "demo_run",
        "track_count": 2,
        "artifact_paths": {"tracks": "tracks.csv"},
    }

    center.write_summary("demo_run", summary)

    assert center.read_summary("demo_run") == summary


def test_list_runs_returns_sorted_directory_names(tmp_path):
    center = VideoAnalysisCenter(tmp_path / "video_analysis")
    center.create_run("z_run")
    center.create_run("a_run")
    center.write_metadata("b_run", {"input_video": "demo.mp4"})

    assert center.list_runs() == ["a_run", "b_run", "z_run"]


@pytest.mark.parametrize("run_name", ["", "nested/run", "nested\\run", "../escape", "bad..name"])
def test_run_name_must_be_safe(run_name, tmp_path):
    center = VideoAnalysisCenter(tmp_path / "video_analysis")

    with pytest.raises(ValueError):
        center.create_run(run_name)
