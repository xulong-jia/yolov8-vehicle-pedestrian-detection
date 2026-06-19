import csv
import json
from pathlib import Path

from src.services.video_demo_catalog import (
    build_demo_catalog,
    discover_video_analysis_run,
    summarize_event_jsonl,
    summarize_tracks_csv,
    summarize_video_file,
)


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fieldnames = list(rows[0].keys()) if rows else ["track_id"]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_summarize_tracks_csv_handles_missing_file(tmp_path: Path) -> None:
    summary = summarize_tracks_csv(tmp_path / "missing.csv")

    assert summary["exists"] is False
    assert summary["row_count"] == 0
    assert summary["unique_tracks"] == 0
    assert summary["frames_with_rows"] == 0
    assert summary["class_counts"] == {}
    assert summary["head"] == []


def test_summarize_tracks_csv_counts_tracks_frames_and_classes(tmp_path: Path) -> None:
    tracks_csv = tmp_path / "tracks.csv"
    _write_csv(
        tracks_csv,
        [
            {"frame_index": 0, "track_id": 1, "class_name": "Person"},
            {"frame_index": 1, "track_id": 1, "class_name": "Person"},
            {"frame_index": 1, "track_id": 2, "class_name": "Bus"},
        ],
    )

    summary = summarize_tracks_csv(tracks_csv)

    assert summary["exists"] is True
    assert summary["row_count"] == 3
    assert summary["unique_tracks"] == 2
    assert summary["frames_with_rows"] == 2
    assert summary["class_counts"] == {"Bus": 1, "Person": 2}
    assert len(summary["head"]) == 3


def test_summarize_event_jsonl_counts_and_reads_head(tmp_path: Path) -> None:
    events_jsonl = tmp_path / "events.jsonl"
    events_jsonl.write_text(
        "\n".join(
            [
                json.dumps({"event_id": "a", "event_type": "long_stay"}),
                json.dumps({"event_id": "b", "event_type": "crowd_warning"}),
                json.dumps({"event_id": "c", "event_type": "wrong_direction"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = summarize_event_jsonl(events_jsonl)

    assert summary["exists"] is True
    assert summary["line_count"] == 3
    assert [row["event_id"] for row in summary["head"]] == ["a", "b", "c"]


def test_summarize_video_file_reports_size_without_opening_video(tmp_path: Path) -> None:
    missing = summarize_video_file(tmp_path / "missing.mp4")
    assert missing["exists"] is False
    assert missing["size_bytes"] == 0

    fake_video = tmp_path / "preview.mp4"
    fake_video.write_bytes(b"fake-video")

    summary = summarize_video_file(fake_video)

    assert summary["exists"] is True
    assert summary["path"] == str(fake_video)
    assert summary["size_bytes"] == len(b"fake-video")
    assert summary["size_mb"] >= 0


def test_discover_video_analysis_run_reads_expected_artifacts(tmp_path: Path) -> None:
    run_dir = tmp_path / "video_analysis" / "demo"
    run_dir.mkdir(parents=True)
    (run_dir / "metadata.json").write_text(json.dumps({"run_name": "demo"}), encoding="utf-8")
    (run_dir / "video_analysis_summary.json").write_text(
        json.dumps({"video_id": "demo", "detection_count": 3, "track_count": 2}),
        encoding="utf-8",
    )
    _write_csv(run_dir / "detections.csv", [{"frame_index": 0, "detection_id": 1}])
    _write_csv(
        run_dir / "tracks.csv",
        [
            {"frame_index": 0, "track_id": 1, "class_name": "Person"},
            {"frame_index": 1, "track_id": 2, "class_name": "Bus"},
        ],
    )
    _write_csv(run_dir / "count_events.csv", [{"line_id": "main", "track_id": 1}])
    _write_csv(run_dir / "roi_frame_counts.csv", [{"roi_id": "crosswalk", "object_count": 1}])
    (run_dir / "events.jsonl").write_text(
        json.dumps({"event_id": "evt-1", "event_type": "long_stay"}) + "\n",
        encoding="utf-8",
    )

    catalog = discover_video_analysis_run(run_dir)

    assert catalog["exists"] is True
    assert catalog["summary"]["video_id"] == "demo"
    assert catalog["files"]["metadata"]["data"]["run_name"] == "demo"
    assert catalog["files"]["detections_csv"]["line_count"] == 2
    assert catalog["files"]["tracks_csv"]["unique_tracks"] == 2
    assert catalog["files"]["count_events_csv"]["head"][0]["line_id"] == "main"
    assert catalog["files"]["roi_frame_counts_csv"]["head"][0]["roi_id"] == "crosswalk"
    assert catalog["files"]["events_jsonl"]["head"][0]["event_id"] == "evt-1"
    assert catalog["files"]["video_analysis_summary"]["data"]["track_count"] == 2


def test_build_demo_catalog_combines_run_video_and_comparison(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "video_analysis_summary.json").write_text(
        json.dumps({"video_id": "demo", "track_count": 2}),
        encoding="utf-8",
    )
    tracked_video = tmp_path / "tracked.mp4"
    tracked_video.write_bytes(b"video")
    comparison_json = tmp_path / "comparison.json"
    comparison_json.write_text(json.dumps({"decision": "use ByteTrack"}), encoding="utf-8")

    catalog = build_demo_catalog(run_dir, tracked_video, comparison_json)

    assert catalog["mode"] == "streamlit_video_demo_catalog"
    assert catalog["video_analysis_run"]["summary"]["track_count"] == 2
    assert catalog["tracked_video"]["exists"] is True
    assert catalog["comparison"] == {"decision": "use ByteTrack"}
    assert "Demo catalog is read-only." in catalog["notes"]


def test_video_demo_catalog_has_no_heavy_or_ui_imports() -> None:
    source = Path("src/services/video_demo_catalog.py").read_text(encoding="utf-8")

    forbidden_imports = ["streamlit", "cv2", "ultralytics", "torch", "numpy"]
    for name in forbidden_imports:
        assert f"import {name}" not in source
        assert f"from {name}" not in source
