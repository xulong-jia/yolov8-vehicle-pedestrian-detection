import csv
import json
from pathlib import Path

import pytest

import src.track_video_bytetrack_spike as spike


def test_require_file_accepts_existing_file_and_rejects_missing_or_directory(tmp_path):
    file_path = tmp_path / "model.pt"
    file_path.write_text("fake", encoding="utf-8")

    assert spike.require_file(file_path, "model") == file_path.resolve()

    with pytest.raises(FileNotFoundError, match="video not found"):
        spike.require_file(tmp_path / "missing.mp4", "video")
    with pytest.raises(ValueError, match="model must be a file"):
        spike.require_file(tmp_path, "model")


def test_write_tracks_csv_writes_header_and_rows(tmp_path):
    output_csv = tmp_path / "tracks.csv"
    rows = [
        {
            "video_id": "demo",
            "frame_index": 0,
            "timestamp_sec": 0.0,
            "track_id": "1",
            "class_id": 0,
            "class_name": "Person",
            "confidence": 0.9,
            "xmin": 10,
            "ymin": 20,
            "xmax": 30,
            "ymax": 40,
            "center_x": 20,
            "center_y": 30,
            "box_width": 20,
            "box_height": 20,
            "box_area": 400,
            "state": "confirmed",
            "tracker_name": "bytetrack",
        }
    ]

    spike.write_tracks_csv(rows, output_csv)

    with output_csv.open(newline="", encoding="utf-8") as file:
        written = list(csv.DictReader(file))
    assert len(written) == 1
    assert written[0]["track_id"] == "1"
    assert written[0]["class_name"] == "Person"


def test_normalize_result_rows_with_fake_result_and_missing_ids():
    result = FakeResult(
        boxes=FakeBoxes(
            xyxy=[[10, 20, 30, 40], [50, 60, 70, 80]],
            ids=[101, None],
            cls=[0, 1],
            conf=[0.9, 0.8],
        ),
        names={0: "Person", 1: "Car"},
    )

    rows = spike.normalize_result_rows(result, video_id="demo", frame_index=2, fps=10.0)

    assert len(rows) == 1
    assert rows[0]["video_id"] == "demo"
    assert rows[0]["frame_index"] == 2
    assert rows[0]["timestamp_sec"] == 0.2
    assert rows[0]["track_id"] == "101"
    assert rows[0]["class_name"] == "Person"
    assert rows[0]["confidence"] == 0.9
    assert rows[0]["xmin"] == 10.0
    assert rows[0]["ymax"] == 40.0


def test_run_bytetrack_spike_uses_fake_model_and_stops_at_max_frames(tmp_path, monkeypatch):
    model_path = _touch(tmp_path / "best.pt")
    video_path = _touch(tmp_path / "source.mp4")
    fake_model = FakeModel(frame_count=3)
    monkeypatch.setattr(spike, "lazy_load_yolo_model", lambda _: fake_model)

    summary = spike.run_bytetrack_spike(
        model_path=model_path,
        video_path=video_path,
        output_dir=tmp_path / "out",
        video_id="demo",
        max_frames=2,
    )

    assert summary["ok"] is True
    assert summary["frames_seen"] == 2
    assert summary["track_rows"] == 2
    assert summary["unique_tracks"] == 2
    assert summary["frames_with_tracks"] == 2
    assert summary["render_preview"] is False
    assert Path(summary["tracks_csv"]).exists()
    assert fake_model.track_kwargs["tracker"] == "bytetrack.yaml"
    assert fake_model.track_kwargs["stream"] is True
    assert fake_model.track_kwargs["persist"] is True


def test_run_bytetrack_spike_can_call_preview_renderer(tmp_path, monkeypatch):
    model_path = _touch(tmp_path / "best.pt")
    video_path = _touch(tmp_path / "source.mp4")
    monkeypatch.setattr(spike, "lazy_load_yolo_model", lambda _: FakeModel(frame_count=1))
    calls = {}

    def fake_render(video_path, tracks_csv, output_video, config_json, overlay_plan_json, max_frames):
        calls["video_path"] = str(video_path)
        calls["tracks_csv"] = str(tracks_csv)
        calls["output_video"] = str(output_video)
        calls["config_json"] = str(config_json)
        calls["overlay_plan_json"] = str(overlay_plan_json)
        calls["max_frames"] = max_frames
        return {"ok": True, "frames_written": max_frames}

    monkeypatch.setattr(spike, "_render_tracked_preview", fake_render)

    summary = spike.run_bytetrack_spike(
        model_path=model_path,
        video_path=video_path,
        output_dir=tmp_path / "out",
        render_preview=True,
        config_json=tmp_path / "config.json",
        overlay_plan_json=tmp_path / "overlay.json",
        max_frames=1,
    )

    assert summary["render_preview"] is True
    assert summary["preview_video"].endswith("bytetrack_tracked_preview_1.mp4")
    assert summary["render_summary"] == {"ok": True, "frames_written": 1}
    assert calls["max_frames"] == 1


def test_main_outputs_json_with_fake_model(tmp_path, monkeypatch, capsys):
    model_path = _touch(tmp_path / "best.pt")
    video_path = _touch(tmp_path / "source.mp4")
    monkeypatch.setattr(spike, "lazy_load_yolo_model", lambda _: FakeModel(frame_count=1))

    result = spike.main(
        [
            "--model",
            str(model_path),
            "--video",
            str(video_path),
            "--output-dir",
            str(tmp_path / "out"),
            "--max-frames",
            "1",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["ok"] is True
    assert payload["track_rows"] == 1


def test_main_missing_input_returns_error_without_output(tmp_path, capsys):
    output_dir = tmp_path / "out"

    result = spike.main(
        [
            "--model",
            str(tmp_path / "missing.pt"),
            "--video",
            str(tmp_path / "missing.mp4"),
            "--output-dir",
            str(output_dir),
        ]
    )

    payload = json.loads(capsys.readouterr().err)
    assert result == 1
    assert payload["ok"] is False
    assert not output_dir.exists()


def test_source_has_no_forbidden_top_level_runtime_imports():
    source = Path("src/track_video_bytetrack_spike.py").read_text(encoding="utf-8")
    first_lines = "\n".join(source.splitlines()[:30])

    assert "from ultralytics" not in first_lines
    assert "import cv2" not in first_lines
    assert "import torch" not in source
    assert "import numpy" not in source
    assert "from ultralytics import YOLO" in source


class FakeBoxes:
    def __init__(self, xyxy, ids, cls, conf):
        self.xyxy = xyxy
        self.id = ids
        self.cls = cls
        self.conf = conf


class FakeResult:
    def __init__(self, boxes, names=None):
        self.boxes = boxes
        self.names = names or {0: "Person", 1: "Car"}


class FakeModel:
    def __init__(self, frame_count):
        self.frame_count = frame_count
        self.track_kwargs = {}

    def track(self, **kwargs):
        self.track_kwargs = kwargs
        for frame_index in range(self.frame_count):
            yield FakeResult(
                boxes=FakeBoxes(
                    xyxy=[[10 + frame_index, 20, 30 + frame_index, 40]],
                    ids=[100 + frame_index],
                    cls=[0],
                    conf=[0.9],
                )
            )


def _touch(path):
    path.write_text("fake", encoding="utf-8")
    return path
