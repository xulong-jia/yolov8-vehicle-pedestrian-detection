import json
from types import SimpleNamespace

import pytest

from src import predict_video
from src.run_video_analysis_smoke import (
    default_smoke_analytics_config,
    main,
    parse_args,
    run_four_step_smoke,
)


def test_parse_args_requires_model_source_and_output_dir():
    args = parse_args(
        [
            "--model",
            "fake_model.pt",
            "--source",
            "fake_video.mp4",
            "--output-dir",
            "/tmp/smoke",
        ]
    )

    assert args.model == "fake_model.pt"
    assert args.source == "fake_video.mp4"
    assert str(args.output_dir) == "/tmp/smoke"
    assert args.video_id == "demo"
    assert args.run_name == "demo_run"
    assert args.conf == 0.25
    assert args.imgsz == 640
    assert args.device == "cpu"

    with pytest.raises(SystemExit):
        parse_args([])


def test_default_smoke_analytics_config_is_inline_contract():
    config = default_smoke_analytics_config()

    assert isinstance(config, dict)
    assert config["line"]["id"] == "line_main"
    assert config["roi"]["id"] == "roi_main"
    assert "event_rules" in config
    assert "long_stay" in config["event_rules"]
    assert config["event_rules"]["long_stay"]["enabled"] is True


def test_run_four_step_smoke_writes_outputs_and_returns_summary(tmp_path, monkeypatch):
    monkeypatch.setattr(predict_video, "YOLO", FakeYOLO)
    output_dir = tmp_path / "smoke"

    summary = run_four_step_smoke(
        model_path="fake_model.pt",
        source="fake_video.mp4",
        output_dir=output_dir,
        video_id="demo",
        conf=0.25,
        imgsz=640,
        device="cpu",
        run_name="demo_run",
    )

    _assert_smoke_outputs(output_dir, "demo_run")
    _assert_summary(summary, output_dir)
    events = _read_events(output_dir / "video_analysis" / "demo_run" / "events.jsonl")
    assert events
    assert all(isinstance(event["evidence"], dict) for event in events)
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()
    assert not (tmp_path / "runs").exists()


def test_main_prints_json_summary_and_writes_outputs(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(predict_video, "YOLO", FakeYOLO)
    output_dir = tmp_path / "smoke"

    result = main(
        [
            "--model",
            "fake_model.pt",
            "--source",
            "fake_video.mp4",
            "--output-dir",
            str(output_dir),
            "--video-id",
            "demo",
            "--run-name",
            "demo_run",
        ]
    )

    printed_summary = json.loads(capsys.readouterr().out)
    assert result == 0
    _assert_smoke_outputs(output_dir, "demo_run")
    _assert_summary(printed_summary, output_dir)
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()
    assert not (tmp_path / "runs").exists()


def _assert_smoke_outputs(output_dir, run_name):
    run_dir = output_dir / "video_analysis" / run_name
    expected_files = [
        output_dir / "detections.csv",
        output_dir / "tracking" / "tracks.csv",
        run_dir / "metadata.json",
        run_dir / "detections.csv",
        run_dir / "tracks.csv",
        run_dir / "count_events.csv",
        run_dir / "roi_frame_counts.csv",
        run_dir / "events.jsonl",
        run_dir / "video_analysis_summary.json",
    ]
    for path in expected_files:
        assert path.exists()


def _assert_summary(summary, output_dir):
    assert summary["video_id"] == "demo"
    assert summary["run_name"] == "demo_run"
    assert summary["mode"] == "four_step_smoke_runner"
    assert summary["detection_count"] > 0
    assert summary["track_row_count"] > 0
    assert summary["track_count"] >= 1
    assert summary["count_summary"]["total_count"] >= 1
    assert summary["roi_summary"]["frames_observed"] >= 1
    assert summary["event_summary"]["total_events"] >= 1
    assert summary["detections_csv"] == str(output_dir / "detections.csv")
    assert summary["tracks_csv"] == str(output_dir / "tracking" / "tracks.csv")
    assert summary["video_analysis_dir"] == str(output_dir / "video_analysis")


def _read_events(events_jsonl):
    return [
        json.loads(line)
        for line in events_jsonl.read_text(encoding="utf-8").splitlines()
        if line
    ]


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
