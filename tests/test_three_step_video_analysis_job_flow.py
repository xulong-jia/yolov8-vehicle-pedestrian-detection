import csv
from types import SimpleNamespace

from src import predict_video, track_video
from src.predict_video import DETECTION_FIELDS, run_video_detection_csv
from src.services.video_analysis_job import create_video_analysis_job_run
from src.tracking.track_writer import TRACKS_FIELDS


def test_three_step_video_analysis_job_flow(tmp_path, monkeypatch):
    monkeypatch.setattr(predict_video, "YOLO", FakeYOLO)
    detections_csv = tmp_path / "detections.csv"

    detection_summary = run_video_detection_csv(
        model_path="fake_model.pt",
        source="fake_video.mp4",
        output_csv=detections_csv,
        video_id="demo",
    )

    assert detections_csv.exists()
    assert detection_summary["rows"] > 0

    tracking_dir = tmp_path / "tracking"
    tracking_summary = track_video.run_track_video_skeleton(
        input_csv=detections_csv,
        output_dir=tracking_dir,
        tracker_name="synthetic",
    )
    tracks_csv = tracking_dir / "tracks.csv"

    assert tracks_csv.exists()
    assert tracking_summary["track_rows"] > 0

    summary = create_video_analysis_job_run(
        run_name="demo_run",
        base_dir=tmp_path / "video_analysis",
        detections_csv=detections_csv,
        tracks_csv=tracks_csv,
        metadata={
            "video_id": "demo",
            "input_video": "fake_video.mp4",
            "mode": "three_step_smoke",
        },
    )

    run_dir = tmp_path / "video_analysis" / "demo_run"
    run_metadata = run_dir / "metadata.json"
    run_detections = run_dir / "detections.csv"
    run_tracks = run_dir / "tracks.csv"
    run_summary = run_dir / "video_analysis_summary.json"
    assert run_metadata.exists()
    assert run_detections.exists()
    assert run_tracks.exists()
    assert run_summary.exists()

    assert summary["video_id"] == "demo"
    assert summary["run_name"] == "demo_run"
    assert summary["mode"] == "three_step_smoke"
    assert summary["detection_count"] > 0
    assert summary["track_row_count"] > 0
    assert summary["track_count"] >= 1
    assert summary["bad_case_links"] == []
    assert {
        "detections_csv",
        "tracks_csv",
        "metadata_json",
        "video_analysis_summary_json",
    }.issubset(summary["artifact_paths"])

    with run_detections.open(newline="", encoding="utf-8") as file:
        detection_reader = csv.DictReader(file)
        detection_rows = list(detection_reader)
    with run_tracks.open(newline="", encoding="utf-8") as file:
        track_reader = csv.DictReader(file)
        track_rows = list(track_reader)

    assert detection_reader.fieldnames == DETECTION_FIELDS
    assert track_reader.fieldnames == TRACKS_FIELDS
    assert detection_rows[0]["class_name"] == "Car"
    assert track_rows[0]["class_name"] == "Car"
    assert track_rows[0]["tracker_name"] == "synthetic"
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()
    assert not (tmp_path / "runs").exists()


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
        return [
            fake_result(
                xyxy=[[0, 0, 10, 20]],
                conf=[0.91],
                cls=[1],
                names={1: "Car"},
            ),
            fake_result(
                xyxy=[[1, 0, 11, 20]],
                conf=[0.89],
                cls=[1],
                names={1: "Car"},
            ),
        ]
