import csv
import json
from types import SimpleNamespace

from src import predict_video, track_video
from src.predict_video import DETECTION_FIELDS, run_video_detection_csv
from src.services.video_analysis_job import create_video_analysis_job_run
from src.tracking.track_writer import (
    COUNT_EVENTS_FIELDS,
    ROI_FRAME_COUNTS_FIELDS,
    TRACKS_FIELDS,
)


def test_four_step_local_video_analysis_flow(tmp_path, monkeypatch):
    monkeypatch.setattr(predict_video, "YOLO", FakeYOLO)

    detections_csv = tmp_path / "detections.csv"
    detection_summary = run_video_detection_csv(
        model_path="fake_model.pt",
        source="fake_video.mp4",
        output_csv=detections_csv,
        conf=0.25,
        imgsz=640,
        device="cpu",
        video_id="demo",
    )

    assert detections_csv.exists()
    assert detection_summary["rows"] >= 2
    with detections_csv.open(newline="", encoding="utf-8") as file:
        detection_reader = csv.DictReader(file)
        detection_rows = list(detection_reader)
    assert detection_reader.fieldnames == DETECTION_FIELDS
    assert len(detection_rows) >= 2

    tracking_dir = tmp_path / "tracking"
    tracking_summary = track_video.run_track_video_skeleton(
        input_csv=detections_csv,
        output_dir=tracking_dir,
        tracker_name="synthetic",
    )

    tracks_csv = tracking_dir / "tracks.csv"
    assert tracks_csv.exists()
    assert tracking_summary["track_rows"] >= 2
    with tracks_csv.open(newline="", encoding="utf-8") as file:
        track_reader = csv.DictReader(file)
        track_rows = list(track_reader)
    assert track_reader.fieldnames == TRACKS_FIELDS
    assert len(track_rows) >= 2
    assert {row["tracker_name"] for row in track_rows} == {"synthetic"}
    assert {row["state"] for row in track_rows} == {"confirmed"}

    _add_roi_ids_for_long_stay(tracks_csv)

    summary = create_video_analysis_job_run(
        run_name="demo_run",
        base_dir=tmp_path / "video_analysis",
        detections_csv=detections_csv,
        tracks_csv=tracks_csv,
        metadata={
            "video_id": "demo",
            "input_video": "fake_video.mp4",
            "mode": "four_step_smoke",
        },
        analytics_config=_analytics_config(),
        run_analytics=True,
    )

    run_dir = tmp_path / "video_analysis" / "demo_run"
    expected_artifacts = {
        "metadata_json": run_dir / "metadata.json",
        "detections_csv": run_dir / "detections.csv",
        "tracks_csv": run_dir / "tracks.csv",
        "count_events_csv": run_dir / "count_events.csv",
        "roi_frame_counts_csv": run_dir / "roi_frame_counts.csv",
        "events_jsonl": run_dir / "events.jsonl",
        "video_analysis_summary_json": run_dir / "video_analysis_summary.json",
    }
    for artifact_path in expected_artifacts.values():
        assert artifact_path.exists()

    with expected_artifacts["count_events_csv"].open(newline="", encoding="utf-8") as file:
        count_reader = csv.DictReader(file)
        count_rows = list(count_reader)
    assert count_reader.fieldnames == COUNT_EVENTS_FIELDS
    assert count_rows

    with expected_artifacts["roi_frame_counts_csv"].open(newline="", encoding="utf-8") as file:
        roi_reader = csv.DictReader(file)
        roi_rows = list(roi_reader)
    assert roi_reader.fieldnames == ROI_FRAME_COUNTS_FIELDS
    assert roi_rows

    events = [
        json.loads(line)
        for line in expected_artifacts["events_jsonl"].read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert events
    assert all(isinstance(event["evidence"], dict) for event in events)
    assert "long_stay" in {event["event_type"] for event in events}

    assert summary["video_id"] == "demo"
    assert summary["run_name"] == "demo_run"
    assert summary["mode"] == "four_step_smoke"
    assert summary["detection_count"] > 0
    assert summary["track_row_count"] > 0
    assert summary["track_count"] >= 1
    assert summary["count_summary"]["total_count"] >= 1
    assert summary["roi_summary"]["frames_observed"] >= 1
    assert summary["event_summary"]["total_events"] >= 1
    assert set(expected_artifacts).issubset(summary["artifact_paths"])
    assert json.loads(
        expected_artifacts["video_analysis_summary_json"].read_text(encoding="utf-8")
    ) == summary
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()
    assert not (tmp_path / "runs").exists()


def _add_roi_ids_for_long_stay(tracks_csv):
    with tracks_csv.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if "roi_id" not in fieldnames:
        fieldnames.append("roi_id")

    for row in rows:
        row["roi_id"] = "roi_main" if row["class_name"] == "Person" else ""

    with tracks_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


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
            "polygon": [[0, 0], [20, 0], [20, 30], [0, 30]],
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
                "parameters": {"min_duration_sec": 0.1, "cooldown_sec": 10.0},
            }
        },
    }


def fake_result(xyxy, conf, cls, names):
    return SimpleNamespace(
        boxes=SimpleNamespace(
            xyxy=FakeTensor(xyxy),
            conf=FakeTensor(conf),
            cls=FakeTensor(cls),
        ),
        names=names,
    )


class FakeTensor:
    def __init__(self, values):
        self.values = values

    def cpu(self):
        return self

    def numpy(self):
        return self

    def tolist(self):
        return self.values

    def __len__(self):
        return len(self.values)


class FakeYOLO:
    def __init__(self, model_path):
        assert model_path == "fake_model.pt"

    def predict(self, **kwargs):
        assert kwargs == {
            "source": "fake_video.mp4",
            "conf": 0.25,
            "imgsz": 640,
            "device": "cpu",
            "stream": False,
            "verbose": False,
            "save": False,
        }
        names = {1: "Car", 3: "Person"}
        return [
            fake_result(
                xyxy=[[4, -3, 6, -1], [4, 4, 6, 6]],
                conf=[0.91, 0.88],
                cls=[1, 3],
                names=names,
            ),
            fake_result(
                xyxy=[[4, 1, 6, 3], [4, 4, 6, 6]],
                conf=[0.92, 0.89],
                cls=[1, 3],
                names=names,
            ),
            fake_result(
                xyxy=[[4, 2, 6, 4], [4, 4, 6, 6]],
                conf=[0.9, 0.87],
                cls=[1, 3],
                names=names,
            ),
        ]
