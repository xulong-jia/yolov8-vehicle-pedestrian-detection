import pytest

from src.tracking.adapters import (
    BaseTrackerAdapter,
    ByteTrackAdapter,
    DeepSORTAdapter,
    SyntheticTrackerAdapter,
    create_tracker_adapter,
    detections_to_tracker_input,
    tracker_outputs_to_track_rows,
)
from src.tracking.track_writer import TRACKS_FIELDS


def test_synthetic_tracker_adapter_converts_detections_to_tracks():
    adapter = SyntheticTrackerAdapter()

    tracks = adapter.update(
        [
            detection_row(detection_id="det-1", xmin=0, ymin=1, xmax=10, ymax=21),
            detection_row(detection_id="", xmin=2, ymin=3, xmax=12, ymax=23),
        ]
    )

    assert len(tracks) == 2
    assert all(field in tracks[0] for field in TRACKS_FIELDS)
    assert tracks[0]["track_id"] == "det-1"
    assert tracks[1]["track_id"] == "synthetic_2"
    assert tracks[0]["state"] == "confirmed"
    assert tracks[0]["tracker_name"] == "synthetic"
    assert tracks[0]["center_x"] == 5.0
    assert tracks[0]["center_y"] == 11.0
    assert tracks[0]["box_width"] == 10.0
    assert tracks[0]["box_height"] == 20.0
    assert tracks[0]["box_area"] == 200.0


def test_synthetic_tracker_adapter_handles_empty_input():
    assert SyntheticTrackerAdapter().update([]) == []


def test_create_tracker_adapter_returns_supported_adapters():
    assert isinstance(create_tracker_adapter("synthetic"), SyntheticTrackerAdapter)
    assert isinstance(create_tracker_adapter("ByteTrack"), ByteTrackAdapter)
    assert isinstance(create_tracker_adapter("deepsort"), DeepSORTAdapter)


def test_create_tracker_adapter_rejects_unknown_tracker_type():
    with pytest.raises(ValueError, match="Unsupported tracker_type"):
        create_tracker_adapter("unknown")


def test_placeholder_adapters_raise_not_implemented():
    bytetrack = ByteTrackAdapter()
    deepsort = DeepSORTAdapter()

    assert bytetrack.tracker_type == "bytetrack"
    assert deepsort.tracker_type == "deepsort"
    with pytest.raises(NotImplementedError, match="real ByteTrack dependency is not integrated yet"):
        bytetrack.update([detection_row()])
    with pytest.raises(NotImplementedError, match="real DeepSORT dependency is not integrated yet"):
        deepsort.update([detection_row()])


def test_base_tracker_adapter_update_is_abstract_contract():
    adapter = BaseTrackerAdapter("base")

    with pytest.raises(NotImplementedError):
        adapter.update([])


def test_detections_to_tracker_input_preserves_required_fields():
    rows = [detection_row(detection_id="det-7", class_id=3, class_name="Person")]

    tracker_input = detections_to_tracker_input(rows)

    assert tracker_input == [
        {
            "bbox": [0.0, 1.0, 10.0, 21.0],
            "confidence": 0.91,
            "class_id": 3,
            "class_name": "Person",
            "frame_index": 5,
            "timestamp_sec": 1.0,
            "detection_id": "det-7",
            "video_id": "video-1",
        }
    ]


def test_detections_to_tracker_input_handles_empty_input():
    assert detections_to_tracker_input([]) == []


def test_tracker_outputs_to_track_rows_uses_tracks_contract():
    outputs = [
        {
            "video_id": "video-1",
            "track_id": "track-1",
            "bbox": [0, 1, 10, 21],
            "class_id": 1,
            "class_name": "Car",
            "confidence": 0.91,
            "frame_index": 5,
            "timestamp_sec": 1.0,
        }
    ]

    rows = tracker_outputs_to_track_rows(outputs, tracker_name="fake_tracker")

    assert len(rows) == 1
    assert all(field in rows[0] for field in TRACKS_FIELDS)
    assert rows[0]["video_id"] == "video-1"
    assert rows[0]["track_id"] == "track-1"
    assert rows[0]["center_x"] == 5.0
    assert rows[0]["center_y"] == 11.0
    assert rows[0]["box_width"] == 10.0
    assert rows[0]["box_height"] == 20.0
    assert rows[0]["box_area"] == 200.0
    assert rows[0]["state"] == "confirmed"
    assert rows[0]["tracker_name"] == "fake_tracker"


def test_tracker_outputs_to_track_rows_uses_video_id_override():
    outputs = [
        {
            "track_id": "track-1",
            "bbox": [0, 0, 2, 4],
            "class_id": 1,
            "class_name": "Car",
            "confidence": 0.5,
            "frame_index": 0,
            "timestamp_sec": 0.0,
        }
    ]

    rows = tracker_outputs_to_track_rows(outputs, video_id="override", tracker_name="synthetic")

    assert rows[0]["video_id"] == "override"


def test_tracker_outputs_to_track_rows_handles_empty_input():
    assert tracker_outputs_to_track_rows([]) == []


def detection_row(
    detection_id="det-1",
    class_id=1,
    class_name="Car",
    xmin=0,
    ymin=1,
    xmax=10,
    ymax=21,
):
    return {
        "video_id": "video-1",
        "frame_index": 5,
        "timestamp_sec": 1.0,
        "detection_id": detection_id,
        "class_id": class_id,
        "class_name": class_name,
        "confidence": 0.91,
        "xmin": xmin,
        "ymin": ymin,
        "xmax": xmax,
        "ymax": ymax,
    }
