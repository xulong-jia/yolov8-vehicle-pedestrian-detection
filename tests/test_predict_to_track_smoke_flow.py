import csv
import json
from types import SimpleNamespace

from src import predict_video, track_video
from src.predict_video import DETECTION_FIELDS, run_video_detection_csv
from src.tracking.track_writer import TRACKS_FIELDS


def test_predict_video_csv_then_track_video_synthetic_tracker(tmp_path, monkeypatch):
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
    assert detection_summary["rows"] > 0
    with detections_csv.open(newline="", encoding="utf-8") as file:
        detection_reader = csv.DictReader(file)
        detection_rows = list(detection_reader)

    assert detection_reader.fieldnames == DETECTION_FIELDS
    assert len(detection_rows) == 2
    assert detection_rows[0]["video_id"] == "demo"
    assert detection_rows[0]["detection_id"] == "1"
    assert detection_rows[0]["class_name"] == "Car"

    tracking_dir = tmp_path / "tracking"
    tracking_summary = track_video.run_track_video_skeleton(
        input_csv=detections_csv,
        output_dir=tracking_dir,
        tracker_name="synthetic",
    )

    tracks_csv = tracking_dir / "tracks.csv"
    assert tracks_csv.exists()
    assert tracking_summary["tracker_name"] == "synthetic"
    assert tracking_summary["track_rows"] > 0
    with tracks_csv.open(newline="", encoding="utf-8") as file:
        track_reader = csv.DictReader(file)
        track_rows = list(track_reader)

    assert track_reader.fieldnames == TRACKS_FIELDS
    assert track_rows[0]["track_id"] == detection_rows[0]["detection_id"]
    assert track_rows[0]["class_name"] == "Car"
    assert track_rows[0]["tracker_name"] == "synthetic"
    assert track_rows[0]["state"] == "confirmed"
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()
    assert not (tmp_path / "runs").exists()


def test_predict_to_track_cli_main_smoke_flow(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(predict_video, "YOLO", FakeYOLO)
    detections_csv = tmp_path / "detections.csv"
    tracking_dir = tmp_path / "tracking"

    predict_result = predict_video.main(
        [
            "--model",
            "fake_model.pt",
            "--source",
            "fake_video.mp4",
            "--output-csv",
            str(detections_csv),
            "--conf",
            "0.25",
            "--imgsz",
            "640",
            "--device",
            "cpu",
            "--video-id",
            "demo",
        ]
    )
    predict_summary = json.loads(capsys.readouterr().out)

    track_result = track_video.main(
        [
            "--detections-csv",
            str(detections_csv),
            "--output-dir",
            str(tracking_dir),
            "--tracker",
            "synthetic",
        ]
    )
    track_summary = json.loads(capsys.readouterr().out)

    assert predict_result == 0
    assert track_result == 0
    assert predict_summary["output_csv"] == str(detections_csv)
    assert predict_summary["rows"] == 2
    assert track_summary["tracker_name"] == "synthetic"
    assert track_summary["track_rows"] == 2
    assert detections_csv.exists()
    assert (tracking_dir / "tracks.csv").exists()
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
