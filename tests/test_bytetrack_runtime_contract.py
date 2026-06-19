from pathlib import Path

import pytest

from src.tracking.bytetrack_runtime_contract import (
    build_bytetrack_output_paths,
    build_bytetrack_runtime_metadata,
    build_track_video_bytetrack_plan,
    parse_frame_limit,
    summarize_track_rows,
    validate_bytetrack_runtime_config,
)


def test_parse_frame_limit_accepts_default_string_and_int():
    assert parse_frame_limit(None) == 300
    assert parse_frame_limit(None, default=120) == 120
    assert parse_frame_limit("300") == 300
    assert parse_frame_limit(42) == 42


@pytest.mark.parametrize("value", [0, -1, "0", "-5", "abc", object()])
def test_parse_frame_limit_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        parse_frame_limit(value)


def test_build_bytetrack_output_paths_does_not_create_output_dir(tmp_path):
    output_dir = tmp_path / "bytetrack"

    paths = build_bytetrack_output_paths(output_dir)

    assert paths == {
        "output_dir": str(output_dir),
        "tracks_csv": str(output_dir / "bytetrack_tracks.csv"),
        "preview_video": str(output_dir / "bytetrack_tracked_preview_300.mp4"),
        "summary_json": str(output_dir / "bytetrack_spike_summary.json"),
    }
    assert not output_dir.exists()


def test_build_bytetrack_runtime_metadata_mentions_lap():
    metadata = build_bytetrack_runtime_metadata(
        video_id="demo",
        model_path="best.pt",
        video_path="source.mp4",
        max_frames=300,
    )

    assert metadata["mode"] == "ultralytics_bytetrack_runtime"
    assert metadata["video_id"] == "demo"
    assert metadata["tracker"] == "bytetrack.yaml"
    assert metadata["model_path"] == "best.pt"
    assert metadata["video_path"] == "source.mp4"
    assert metadata["max_frames"] == 300
    assert "lap" in metadata["dependency_note"]


def test_summarize_track_rows_counts_tracks_frames_classes_and_errors():
    rows = [
        {
            "track_id": "1",
            "frame_index": 0,
            "class_name": "Person",
            "xmin": 0,
            "ymin": 0,
            "xmax": 10,
            "ymax": 20,
        },
        {
            "track_id": "1",
            "frame_index": 1,
            "class_name": "Person",
            "xmin": 1,
            "ymin": 0,
            "xmax": 11,
            "ymax": 20,
        },
        {
            "track_id": "2",
            "frame_index": 1,
            "class_name": "Bus",
            "xmin": 30,
            "ymin": 10,
            "xmax": 20,
            "ymax": 40,
        },
        {
            "track_id": "",
            "frame_index": "",
            "class_name": "",
            "xmin": "bad",
            "ymin": 0,
            "xmax": 1,
            "ymax": 1,
        },
    ]

    summary = summarize_track_rows(rows)

    assert summary == {
        "track_rows": 4,
        "unique_tracks": 2,
        "frames_with_tracks": 2,
        "class_counts": {"Person": 2, "Bus": 1, "unknown": 1},
        "missing_track_id_count": 1,
        "invalid_bbox_count": 2,
    }


def test_validate_bytetrack_runtime_config_accepts_existing_inputs_without_creating_output(
    tmp_path,
):
    model = _touch(tmp_path / "best.pt")
    video = _touch(tmp_path / "source.mp4")
    output_dir = tmp_path / "out"

    result = validate_bytetrack_runtime_config(model, video, output_dir, max_frames=300)

    assert result["ok"] is True
    assert result["checks"]["model_exists"] is True
    assert result["checks"]["video_exists"] is True
    assert result["checks"]["output_parent_ready"] is True
    assert result["checks"]["max_frames_positive"] is True
    assert result["checks"]["tracker_non_empty"] is True
    assert result["errors"] == []
    assert not output_dir.exists()


def test_validate_bytetrack_runtime_config_reports_missing_model_and_video(tmp_path):
    result = validate_bytetrack_runtime_config(
        tmp_path / "missing.pt",
        tmp_path / "missing.mp4",
        tmp_path / "out",
    )

    assert result["ok"] is False
    assert result["checks"]["model_exists"] is False
    assert result["checks"]["video_exists"] is False
    assert any("model_path" in error for error in result["errors"])
    assert any("video_path" in error for error in result["errors"])


@pytest.mark.parametrize("max_frames", [0, -1, "bad"])
def test_validate_bytetrack_runtime_config_reports_invalid_max_frames(tmp_path, max_frames):
    model = _touch(tmp_path / "best.pt")
    video = _touch(tmp_path / "source.mp4")

    result = validate_bytetrack_runtime_config(model, video, tmp_path / "out", max_frames=max_frames)

    assert result["ok"] is False
    assert result["checks"]["max_frames_positive"] is False
    assert "max_frames must be greater than 0" in result["errors"]


def test_build_track_video_bytetrack_plan_describes_future_runtime(tmp_path):
    plan = build_track_video_bytetrack_plan(
        model_path=tmp_path / "best.pt",
        video_path=tmp_path / "source.mp4",
        output_dir=tmp_path / "out",
        video_id="demo",
        max_frames="300",
        render_preview=True,
    )

    assert plan["mode"] == "track_video_bytetrack_runtime_plan"
    assert plan["command_intent"] == "future track_video.py --tracker bytetrack runtime"
    assert plan["inputs"]["max_frames"] == 300
    assert plan["inputs"]["render_preview"] is True
    assert plan["outputs"]["tracks_csv"].endswith("bytetrack_tracks.csv")
    assert plan["metadata"]["video_id"] == "demo"
    assert any("model.track" in step for step in plan["runtime_steps"])
    assert any("tracks.csv" in step for step in plan["runtime_steps"])
    assert any("do not commit output" in item for item in plan["no_go_items"])
    assert plan["next_version"] == "v0.11.4-track-video-bytetrack-runtime"


def test_source_has_no_forbidden_runtime_imports():
    source = Path("src/tracking/bytetrack_runtime_contract.py").read_text(encoding="utf-8")

    assert "import ultralytics" not in source
    assert "from ultralytics" not in source
    assert "import cv2" not in source
    assert "import torch" not in source
    assert "import numpy" not in source


def _touch(path: Path) -> Path:
    path.write_text("fake", encoding="utf-8")
    return path
