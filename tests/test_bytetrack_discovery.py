import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from src.tracking.bytetrack_discovery import (
    check_optional_module,
    discover_bytetrack_options,
    normalize_ultralytics_track_result,
    normalize_ultralytics_track_results,
    track_objects_to_rows,
    validate_track_rows,
)
from src.tracking.track_writer import TRACKS_FIELDS


def test_check_optional_module_uses_find_spec(monkeypatch):
    calls = []

    def fake_find_spec(module_name):
        calls.append(module_name)
        return object() if module_name == "available_module" else None

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)

    assert check_optional_module("available_module") == {
        "module": "available_module",
        "available": True,
    }
    assert check_optional_module("missing_module") == {
        "module": "missing_module",
        "available": False,
    }
    assert calls == ["available_module", "missing_module"]


def test_discover_bytetrack_options_returns_recommended_candidate(monkeypatch):
    monkeypatch.setattr(importlib.util, "find_spec", lambda _: None)

    discovery = discover_bytetrack_options()

    assert discovery["recommended_path"] == "ultralytics_model_track_spike"
    assert discovery["candidate_paths"][0]["name"] == "ultralytics_model_track"
    assert discovery["candidate_paths"][0]["status"] == "recommended_for_next_spike"
    assert discovery["candidate_paths"][1]["name"] == "external_bytetrack_adapter"
    assert "track_id" in discovery["track_csv_contract"]


def test_track_objects_to_rows_outputs_tracks_contract():
    rows = track_objects_to_rows(
        [
            {
                "track_id": 1,
                "class_id": 0,
                "class_name": "Person",
                "confidence": 0.9,
                "bbox": [10, 20, 30, 40],
            }
        ],
        video_id="video-1",
        frame_index=7,
        timestamp_sec=0.7,
    )

    assert len(rows) == 1
    assert all(field in rows[0] for field in TRACKS_FIELDS)
    assert rows[0]["video_id"] == "video-1"
    assert rows[0]["frame_index"] == 7
    assert rows[0]["timestamp_sec"] == 0.7
    assert rows[0]["track_id"] == 1
    assert rows[0]["class_id"] == 0
    assert rows[0]["class_name"] == "Person"
    assert rows[0]["confidence"] == 0.9
    assert rows[0]["xmin"] == 10.0
    assert rows[0]["ymin"] == 20.0
    assert rows[0]["xmax"] == 30.0
    assert rows[0]["ymax"] == 40.0
    assert rows[0]["state"] == "confirmed"
    assert rows[0]["tracker_name"] == "bytetrack"


def test_normalize_ultralytics_track_result_with_fake_object():
    result = FakeResult(
        frame_index=3,
        timestamp_sec=0.1,
        boxes=FakeBoxes(
            xyxy=[[10, 20, 30, 40], [50, 60, 70, 80]],
            ids=[101, 102],
            cls=[0, 1],
            conf=[0.9, 0.8],
        ),
    )

    rows = normalize_ultralytics_track_result(result, video_id="demo")

    assert len(rows) == 2
    assert rows[0]["video_id"] == "demo"
    assert rows[0]["frame_index"] == 3
    assert rows[0]["timestamp_sec"] == 0.1
    assert rows[0]["track_id"] == "101"
    assert rows[0]["class_name"] == "Person"
    assert rows[1]["track_id"] == "102"
    assert rows[1]["class_name"] == "Car"


def test_normalize_ultralytics_track_result_skips_missing_ids():
    result = FakeResult(
        boxes=FakeBoxes(
            xyxy=[[10, 20, 30, 40]],
            ids=None,
            cls=[0],
            conf=[0.9],
        ),
    )

    rows = normalize_ultralytics_track_result(result, video_id="demo")

    assert rows == []
    assert validate_track_rows(rows)["ok"] is True
    assert validate_track_rows(rows)["row_count"] == 0


def test_normalize_ultralytics_track_results_preserves_or_enumerates_frame_index():
    first = FakeResult(
        frame_index=5,
        boxes=FakeBoxes([[0, 0, 10, 10]], [1], [0], [0.9]),
    )
    second = FakeResult(
        boxes=FakeBoxes([[10, 10, 20, 20]], [2], [1], [0.8]),
    )

    rows = normalize_ultralytics_track_results([first, second], video_id="demo")

    assert len(rows) == 2
    assert rows[0]["frame_index"] == 5
    assert rows[1]["frame_index"] == 1
    assert rows[0]["track_id"] == "1"
    assert rows[1]["track_id"] == "2"


def test_validate_track_rows_reports_valid_and_invalid_rows():
    valid_rows = track_objects_to_rows(
        [
            {
                "track_id": "a",
                "class_id": 0,
                "class_name": "Person",
                "confidence": 0.9,
                "bbox": [0, 0, 10, 20],
            },
            {
                "track_id": "b",
                "class_id": 1,
                "class_name": "Car",
                "confidence": 0.8,
                "bbox": [5, 5, 15, 25],
            },
        ]
    )

    valid_summary = validate_track_rows(valid_rows)
    assert valid_summary["ok"] is True
    assert valid_summary["row_count"] == 2
    assert valid_summary["unique_tracks"] == 2

    invalid_rows = [
        {**valid_rows[0], "track_id": "", "xmax": -1},
        {"track_id": "missing-fields"},
    ]
    invalid_summary = validate_track_rows(invalid_rows)
    assert invalid_summary["ok"] is False
    assert invalid_summary["missing_track_id_count"] == 1
    assert invalid_summary["invalid_bbox_count"] == 2
    assert "video_id" in invalid_summary["missing_required_fields"]


def test_cli_outputs_json_summary():
    result = subprocess.run(
        [sys.executable, "-m", "src.tracking.bytetrack_discovery"],
        check=False,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["recommended_path"] == "ultralytics_model_track_spike"
    assert payload["candidate_paths"]


def test_source_has_no_forbidden_runtime_imports():
    source = Path("src/tracking/bytetrack_discovery.py").read_text(encoding="utf-8")
    first_lines = "\n".join(source.splitlines()[:25])

    assert "import ultralytics" not in source
    assert "import cv2" not in source
    assert "import torch" not in source
    assert "import numpy" not in source
    assert "find_spec" in source
    assert "ultralytics" not in first_lines
    assert "cv2" not in first_lines


class FakeBoxes:
    def __init__(self, xyxy, ids, cls, conf):
        self.xyxy = xyxy
        self.id = ids
        self.cls = cls
        self.conf = conf


class FakeResult:
    names = {0: "Person", 1: "Car"}
    orig_shape = (720, 1280)

    def __init__(self, boxes, frame_index=None, timestamp_sec=None):
        self.boxes = boxes
        if frame_index is not None:
            self.frame_index = frame_index
        if timestamp_sec is not None:
            self.timestamp_sec = timestamp_sec
