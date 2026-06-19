import csv
import json
from types import SimpleNamespace

from src import predict_video
from src.predict_video import (
    DETECTION_FIELDS,
    main,
    parse_args,
    run_video_detection_csv,
    yolo_result_to_detection_rows,
)


def test_parse_args_supports_csv_first_options(tmp_path):
    args = parse_args(
        [
            "--model",
            "local_weights/demo.pt",
            "--source",
            "local_videos/source/demo.mp4",
            "--output-csv",
            str(tmp_path / "detections.csv"),
            "--conf",
            "0.4",
            "--imgsz",
            "512",
            "--device",
            "cpu",
            "--video-id",
            "demo-video",
        ]
    )

    assert args.model == "local_weights/demo.pt"
    assert args.source == "local_videos/source/demo.mp4"
    assert args.output_csv == tmp_path / "detections.csv"
    assert args.conf == 0.4
    assert args.imgsz == 512
    assert args.device == "cpu"
    assert args.video_id == "demo-video"


def test_parse_args_keeps_csv_defaults(tmp_path):
    args = parse_args(
        [
            "--model",
            "local_weights/demo.pt",
            "--source",
            "demo.mp4",
            "--output-csv",
            str(tmp_path / "detections.csv"),
        ]
    )

    assert args.conf == 0.25
    assert args.imgsz == 640
    assert args.device == "cpu"
    assert args.video_id is None


def test_yolo_result_to_detection_rows_converts_boxes():
    result = fake_result(
        xyxy=[[0, 1, 10, 20], [5, 6, 15, 26]],
        conf=[0.9, 0.8],
        cls=[1, 3],
        names={1: "Car", 3: "Person"},
    )

    rows = yolo_result_to_detection_rows(
        result,
        video_id="demo",
        frame_index=7,
        timestamp_sec=1.4,
    )

    assert rows == [
        {
            "video_id": "demo",
            "frame_index": 7,
            "timestamp_sec": 1.4,
            "detection_id": 1,
            "class_id": 1,
            "class_name": "Car",
            "confidence": 0.9,
            "xmin": 0.0,
            "ymin": 1.0,
            "xmax": 10.0,
            "ymax": 20.0,
        },
        {
            "video_id": "demo",
            "frame_index": 7,
            "timestamp_sec": 1.4,
            "detection_id": 2,
            "class_id": 3,
            "class_name": "Person",
            "confidence": 0.8,
            "xmin": 5.0,
            "ymin": 6.0,
            "xmax": 15.0,
            "ymax": 26.0,
        },
    ]


def test_yolo_result_to_detection_rows_returns_empty_for_empty_boxes():
    result = fake_result(xyxy=[], conf=[], cls=[], names={})

    assert yolo_result_to_detection_rows(result, "demo", 0, 0.0) == []


def test_run_video_detection_csv_writes_csv_and_summary(tmp_path, monkeypatch):
    output_csv = tmp_path / "nested" / "detections.csv"
    monkeypatch.setattr(predict_video, "YOLO", FakeYOLO)

    summary = run_video_detection_csv(
        model_path="local_weights/demo.pt",
        source="local_videos/source/demo.mp4",
        output_csv=output_csv,
        conf=0.4,
        imgsz=512,
        device="cpu",
        video_id="demo-video",
    )

    assert output_csv.exists()
    assert summary == {
        "model_path": "local_weights/demo.pt",
        "source": "local_videos/source/demo.mp4",
        "output_csv": str(output_csv),
        "rows": 3,
        "conf": 0.4,
        "imgsz": 512,
        "device": "cpu",
    }

    with output_csv.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    assert reader.fieldnames == DETECTION_FIELDS
    assert len(rows) == 3
    assert rows[0]["video_id"] == "demo-video"
    assert rows[0]["frame_index"] == "0"
    assert rows[0]["class_name"] == "Car"
    assert rows[2]["frame_index"] == "1"
    assert rows[2]["class_name"] == "Bus"
    assert not (tmp_path / "runs").exists()
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()


def test_run_video_detection_csv_writes_header_for_empty_results(tmp_path, monkeypatch):
    output_csv = tmp_path / "detections.csv"
    monkeypatch.setattr(predict_video, "YOLO", EmptyYOLO)

    summary = run_video_detection_csv(
        model_path="model.pt",
        source="demo.mp4",
        output_csv=output_csv,
    )

    assert summary["rows"] == 0
    assert output_csv.read_text(encoding="utf-8").splitlines()[0].split(",") == DETECTION_FIELDS


def test_main_writes_csv_and_prints_json_summary(tmp_path, monkeypatch, capsys):
    output_csv = tmp_path / "detections.csv"
    monkeypatch.setattr(predict_video, "YOLO", FakeYOLO)

    result = main(
        [
            "--model",
            "model.pt",
            "--source",
            "demo.mp4",
            "--output-csv",
            str(output_csv),
            "--video-id",
            "demo",
        ]
    )

    assert result == 0
    assert output_csv.exists()
    printed = json.loads(capsys.readouterr().out)
    assert printed["rows"] == 3
    assert printed["output_csv"] == str(output_csv)


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

    def astype(self, _dtype):
        return self

    def tolist(self):
        return self.values

    def __len__(self):
        return len(self.values)


class FakeYOLO:
    def __init__(self, model_path):
        self.model_path = model_path

    def predict(self, **kwargs):
        assert kwargs["source"] in {"local_videos/source/demo.mp4", "demo.mp4"}
        assert kwargs["conf"] in {0.4, 0.25}
        assert kwargs["imgsz"] in {512, 640}
        assert kwargs["device"] == "cpu"
        assert kwargs["stream"] is False
        assert kwargs["verbose"] is False
        assert kwargs["save"] is False
        return [
            fake_result(
                xyxy=[[0, 1, 10, 20], [5, 6, 15, 26]],
                conf=[0.9, 0.8],
                cls=[1, 3],
                names={1: "Car", 3: "Person"},
            ),
            fake_result(
                xyxy=[[2, 3, 12, 23]],
                conf=[0.7],
                cls=[4],
                names={4: "Bus"},
            ),
        ]


class EmptyYOLO:
    def __init__(self, model_path):
        self.model_path = model_path

    def predict(self, **_kwargs):
        return [fake_result(xyxy=[], conf=[], cls=[], names={})]
