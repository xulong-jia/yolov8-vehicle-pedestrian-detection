import csv
import json

from src.tracking.track_writer import (
    COUNT_EVENTS_FIELDS,
    ROI_FRAME_COUNTS_FIELDS,
    TRACKS_FIELDS,
    read_json,
    write_count_events_csv,
    write_events_jsonl,
    write_json,
    write_roi_frame_counts_csv,
    write_tracks_csv,
)


def test_write_tracks_csv_uses_contract_header_and_rows(tmp_path):
    output_path = tmp_path / "nested" / "tracks.csv"
    rows = [
        {
            "video_id": "video-1",
            "frame_index": 1,
            "timestamp_sec": 0.04,
            "track_id": "t-1",
            "class_id": 0,
            "class_name": "vehicle",
            "confidence": 0.91,
            "xmin": 10,
            "ymin": 20,
            "xmax": 50,
            "ymax": 80,
            "center_x": 30,
            "center_y": 50,
            "box_width": 40,
            "box_height": 60,
            "box_area": 2400,
            "state": "confirmed",
            "tracker_name": "synthetic",
            "ignored_extra": "not written",
        },
        {
            "video_id": "video-1",
            "frame_index": 2,
            "timestamp_sec": 0.08,
            "track_id": "t-1",
            "class_id": 0,
            "class_name": "vehicle",
            "confidence": 0.93,
            "xmin": 12,
            "ymin": 22,
            "xmax": 52,
            "ymax": 82,
            "center_x": 32,
            "center_y": 52,
            "box_width": 40,
            "box_height": 60,
            "box_area": 2400,
            "state": "confirmed",
            "tracker_name": "synthetic",
        },
    ]

    written_path = write_tracks_csv(rows, output_path)

    assert written_path == output_path
    assert output_path.exists()
    with output_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        assert reader.fieldnames == TRACKS_FIELDS
        written_rows = list(reader)
    assert len(written_rows) == 2
    assert written_rows[0]["track_id"] == "t-1"
    assert "ignored_extra" not in written_rows[0]


def test_write_count_events_csv_uses_contract_header(tmp_path):
    output_path = tmp_path / "count_events.csv"
    rows = [
        {
            "video_id": "video-1",
            "line_id": "entry_line",
            "frame_index": 5,
            "timestamp_sec": 0.2,
            "track_id": "t-2",
            "class_id": 1,
            "class_name": "pedestrian",
            "direction": "in",
            "center_x": 100,
            "center_y": 200,
        }
    ]

    write_count_events_csv(rows, output_path)

    with output_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        assert reader.fieldnames == COUNT_EVENTS_FIELDS
        written_rows = list(reader)
    assert written_rows == [
        {
            "video_id": "video-1",
            "line_id": "entry_line",
            "frame_index": "5",
            "timestamp_sec": "0.2",
            "track_id": "t-2",
            "class_id": "1",
            "class_name": "pedestrian",
            "direction": "in",
            "center_x": "100",
            "center_y": "200",
        }
    ]


def test_write_roi_frame_counts_csv_uses_contract_header(tmp_path):
    output_path = tmp_path / "roi_frame_counts.csv"
    rows = [
        {
            "video_id": "video-1",
            "frame_index": 10,
            "timestamp_sec": 0.4,
            "roi_id": "crosswalk",
            "roi_name": "Crosswalk",
            "class_name": "pedestrian",
            "object_count": 3,
            "unique_track_count": 3,
        }
    ]

    write_roi_frame_counts_csv(rows, output_path)

    with output_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        assert reader.fieldnames == ROI_FRAME_COUNTS_FIELDS
        assert list(reader)[0]["roi_name"] == "Crosswalk"


def test_write_events_jsonl_keeps_one_event_per_line_and_nested_evidence(tmp_path):
    output_path = tmp_path / "events.jsonl"
    events = [
        {
            "event_id": "event-1",
            "event_type": "crowd_warning",
            "video_id": "video-1",
            "frame_index": 20,
            "timestamp_sec": 0.8,
            "track_id": None,
            "class_name": "pedestrian",
            "roi_id": "crosswalk",
            "line_id": None,
            "severity": "warning",
            "evidence": {"max_count": 5, "duration_sec": 2.0},
        },
        {
            "event_id": "event-2",
            "event_type": "wrong_direction",
            "video_id": "video-1",
            "frame_index": 30,
            "timestamp_sec": 1.2,
            "track_id": "t-3",
            "class_name": "vehicle",
            "roi_id": None,
            "line_id": "entry_line",
            "severity": "critical",
            "evidence": {"expected_direction": "in", "actual_direction": "out"},
        },
    ]

    write_events_jsonl(events, output_path)

    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    decoded_events = [json.loads(line) for line in lines]
    assert decoded_events[0]["evidence"] == {"max_count": 5, "duration_sec": 2.0}
    assert decoded_events[1]["event_type"] == "wrong_direction"


def test_write_and_read_json_round_trips_summary(tmp_path):
    output_path = tmp_path / "summary" / "video_analysis_summary.json"
    summary = {
        "video_id": "video-1",
        "run_name": "demo_run",
        "artifact_paths": {"tracks": "tracks.csv"},
    }

    written_path = write_json(summary, output_path)

    assert written_path == output_path
    assert read_json(output_path) == summary


def test_empty_outputs_still_create_contract_files(tmp_path):
    tracks_path = tmp_path / "empty" / "tracks.csv"
    counts_path = tmp_path / "empty" / "count_events.csv"
    roi_path = tmp_path / "empty" / "roi_frame_counts.csv"
    events_path = tmp_path / "empty" / "events.jsonl"

    write_tracks_csv([], tracks_path)
    write_count_events_csv([], counts_path)
    write_roi_frame_counts_csv([], roi_path)
    write_events_jsonl([], events_path)

    assert tracks_path.read_text(encoding="utf-8").splitlines()[0].split(",") == TRACKS_FIELDS
    assert counts_path.read_text(encoding="utf-8").splitlines()[0].split(",") == COUNT_EVENTS_FIELDS
    assert roi_path.read_text(encoding="utf-8").splitlines()[0].split(",") == ROI_FRAME_COUNTS_FIELDS
    assert events_path.exists()
    assert events_path.read_text(encoding="utf-8") == ""
