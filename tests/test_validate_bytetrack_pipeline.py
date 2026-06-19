import csv
import json
from pathlib import Path

import pytest

from src import validate_bytetrack_pipeline as pipeline


DETECTION_FIELDS = [
    "video_id",
    "frame_index",
    "timestamp_sec",
    "detection_id",
    "class_id",
    "class_name",
    "confidence",
    "xmin",
    "ymin",
    "xmax",
    "ymax",
]

TRACK_FIELDS = [
    "video_id",
    "frame_index",
    "timestamp_sec",
    "track_id",
    "class_id",
    "class_name",
    "confidence",
    "xmin",
    "ymin",
    "xmax",
    "ymax",
    "center_x",
    "center_y",
    "box_width",
    "box_height",
    "box_area",
    "state",
    "tracker_name",
    "roi_id",
]


def test_summarize_tracks_csv_counts_rows_tracks_frames_and_classes(tmp_path):
    tracks_csv = _write_tracks_csv(tmp_path / "tracks.csv")

    summary = pipeline.summarize_tracks_csv(tracks_csv)

    assert summary == {
        "track_rows": 4,
        "unique_tracks": 2,
        "frames_with_tracks": 3,
        "class_counts": {"Person": 3, "Bus": 1},
    }


def test_run_bytetrack_pipeline_validation_analytics_only(tmp_path):
    detections_csv = _write_detections_csv(tmp_path / "inputs" / "detections.csv")
    tracks_csv = _write_tracks_csv(tmp_path / "inputs" / "tracks.csv")
    config_json = _write_config_json(tmp_path / "inputs" / "config.json")
    output_dir = tmp_path / "validation"

    summary = pipeline.run_bytetrack_pipeline_validation(
        detections_csv=detections_csv,
        tracks_csv=tracks_csv,
        config_json=config_json,
        video_path=None,
        output_dir=output_dir,
        run_name="bytetrack_validation",
        video_id="demo",
        render_preview=False,
    )

    run_dir = output_dir / "analytics" / "bytetrack_validation"
    assert summary["ok"] is True
    assert summary["mode"] == "bytetrack_pipeline_validation"
    assert summary["tracks_summary"]["track_rows"] == 4
    assert summary["analytics_summary"]["mode"] == "analytics_only_rerun"
    assert summary["analytics_summary"]["count_summary"]["total_count"] >= 1
    assert summary["analytics_summary"]["roi_summary"]["frames_observed"] >= 1
    assert "event_summary" in summary["analytics_summary"]
    assert summary["render_summary"] == {}
    assert summary["outputs"]["preview_video"] == ""
    assert (run_dir / "count_events.csv").exists()
    assert (run_dir / "roi_frame_counts.csv").exists()
    assert (run_dir / "events.jsonl").exists()
    assert not (output_dir / "bytetrack_tracked_preview_300.mp4").exists()


def test_run_bytetrack_pipeline_validation_can_render_preview_with_monkeypatch(tmp_path, monkeypatch):
    detections_csv = _write_detections_csv(tmp_path / "inputs" / "detections.csv")
    tracks_csv = _write_tracks_csv(tmp_path / "inputs" / "tracks.csv")
    config_json = _write_config_json(tmp_path / "inputs" / "config.json")
    overlay_plan_json = _write_overlay_plan_json(tmp_path / "inputs" / "overlay_plan.json")
    video_path = _touch(tmp_path / "inputs" / "source.mp4")
    calls = {}

    def fake_render_tracked_video(**kwargs):
        calls.update(kwargs)
        Path(kwargs["output_video"]).write_bytes(b"fake-video")
        return {
            "ok": True,
            "mode": "tracked_video_rendering",
            "frames_written": 2,
            "output_video": str(kwargs["output_video"]),
        }

    monkeypatch.setattr(pipeline, "render_tracked_video", fake_render_tracked_video)

    summary = pipeline.run_bytetrack_pipeline_validation(
        detections_csv=detections_csv,
        tracks_csv=tracks_csv,
        config_json=config_json,
        video_path=video_path,
        output_dir=tmp_path / "validation",
        render_preview=True,
        overlay_plan_json=overlay_plan_json,
        max_frames=2,
    )

    assert calls["video_path"] == video_path.resolve()
    assert calls["tracks_csv"] == tracks_csv.resolve()
    assert calls["max_frames"] == 2
    assert Path(calls["output_video"]).name == "bytetrack_tracked_preview_300.mp4"
    assert calls["overlay_plan_json"] == overlay_plan_json.resolve()
    assert summary["render_summary"]["frames_written"] == 2
    assert summary["outputs"]["preview_video"].endswith("bytetrack_tracked_preview_300.mp4")


def test_run_bytetrack_pipeline_validation_fills_blank_timestamps_for_analytics(tmp_path):
    detections_csv = _write_detections_csv(tmp_path / "inputs" / "detections.csv")
    tracks_csv = _write_tracks_csv(tmp_path / "inputs" / "tracks.csv")
    config_json = _write_config_json(tmp_path / "inputs" / "config.json")
    text = tracks_csv.read_text(encoding="utf-8").replace(",0.5,", ",,", 1)
    tracks_csv.write_text(text, encoding="utf-8")

    summary = pipeline.run_bytetrack_pipeline_validation(
        detections_csv=detections_csv,
        tracks_csv=tracks_csv,
        config_json=config_json,
        video_path=None,
        output_dir=tmp_path / "validation",
    )

    analytics_tracks = Path(summary["outputs"]["tracks_csv_for_analytics"])
    assert analytics_tracks.name == "bytetrack_tracks_for_analytics.csv"
    assert analytics_tracks.exists()
    assert ",1.000000," in analytics_tracks.read_text(encoding="utf-8")
    assert summary["analytics_summary"]["track_row_count"] == 4


def test_main_returns_error_when_render_preview_video_is_missing(tmp_path, capsys):
    result = pipeline.main(
        [
            "--detections-csv",
            str(_write_detections_csv(tmp_path / "detections.csv")),
            "--tracks-csv",
            str(_write_tracks_csv(tmp_path / "tracks.csv")),
            "--config-json",
            str(_write_config_json(tmp_path / "config.json")),
            "--video",
            str(tmp_path / "missing.mp4"),
            "--output-dir",
            str(tmp_path / "validation"),
            "--render-preview",
        ]
    )

    captured = capsys.readouterr()
    assert result == 1
    assert "video not found" in captured.err


def test_main_prints_parseable_json_with_monkeypatched_renderer(tmp_path, monkeypatch, capsys):
    video_path = _touch(tmp_path / "source.mp4")

    def fake_render_tracked_video(**kwargs):
        Path(kwargs["output_video"]).write_bytes(b"fake-video")
        return {"ok": True, "frames_written": 3}

    monkeypatch.setattr(pipeline, "render_tracked_video", fake_render_tracked_video)

    result = pipeline.main(
        [
            "--detections-csv",
            str(_write_detections_csv(tmp_path / "detections.csv")),
            "--tracks-csv",
            str(_write_tracks_csv(tmp_path / "tracks.csv")),
            "--config-json",
            str(_write_config_json(tmp_path / "config.json")),
            "--video",
            str(video_path),
            "--output-dir",
            str(tmp_path / "validation"),
            "--run-name",
            "validation",
            "--video-id",
            "demo",
            "--render-preview",
            "--max-frames",
            "3",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert result == 0
    assert payload["ok"] is True
    assert payload["tracks_summary"]["unique_tracks"] == 2
    assert payload["render_summary"]["frames_written"] == 3


def test_source_does_not_run_yolo_or_tracker_runtime():
    source = Path("src/validate_bytetrack_pipeline.py").read_text(encoding="utf-8")

    assert "ultralytics" not in source
    assert "track_video_bytetrack_spike" not in source
    assert "model.track" not in source
    assert "predict_video" not in source
    assert "from src.track_video" not in source
    assert "import src.track_video" not in source


def _write_detections_csv(path: Path) -> Path:
    rows = [
        {
            "video_id": "demo",
            "frame_index": "0",
            "timestamp_sec": "0.0",
            "detection_id": "det_1",
            "class_id": "0",
            "class_name": "Person",
            "confidence": "0.90",
            "xmin": "0",
            "ymin": "40",
            "xmax": "20",
            "ymax": "60",
        }
    ]
    _write_csv(path, DETECTION_FIELDS, rows)
    return path


def _write_tracks_csv(path: Path) -> Path:
    rows = [
        _track_row(frame=0, timestamp=0.0, track_id="1", class_name="Person", xmin=0, ymin=35, xmax=20, ymax=55),
        _track_row(frame=1, timestamp=0.5, track_id="1", class_name="Person", xmin=0, ymin=45, xmax=20, ymax=65),
        _track_row(frame=2, timestamp=1.2, track_id="1", class_name="Person", xmin=0, ymin=55, xmax=20, ymax=75),
        _track_row(frame=2, timestamp=1.2, track_id="2", class_name="Bus", xmin=40, ymin=45, xmax=80, ymax=80),
    ]
    _write_csv(path, TRACK_FIELDS, rows)
    return path


def _track_row(
    frame: int,
    timestamp: float,
    track_id: str,
    class_name: str,
    xmin: int,
    ymin: int,
    xmax: int,
    ymax: int,
) -> dict[str, str]:
    width = xmax - xmin
    height = ymax - ymin
    class_id = "0" if class_name == "Person" else "1"
    return {
        "video_id": "demo",
        "frame_index": str(frame),
        "timestamp_sec": str(timestamp),
        "track_id": track_id,
        "class_id": class_id,
        "class_name": class_name,
        "confidence": "0.90",
        "xmin": str(xmin),
        "ymin": str(ymin),
        "xmax": str(xmax),
        "ymax": str(ymax),
        "center_x": str((xmin + xmax) / 2),
        "center_y": str((ymin + ymax) / 2),
        "box_width": str(width),
        "box_height": str(height),
        "box_area": str(width * height),
        "state": "confirmed",
        "tracker_name": "bytetrack",
        "roi_id": "roi_main",
    }


def _write_config_json(path: Path) -> Path:
    payload = {
        "suggested_config": {
            "lines": [
                {
                    "line_id": "line_main",
                    "name": "Middle line",
                    "points": [[0, 50], [100, 50]],
                    "target_classes": ["Person"],
                    "directions": {"positive": "down", "negative": "up"},
                }
            ],
            "rois": [
                {
                    "roi_id": "roi_main",
                    "name": "Main ROI",
                    "polygon": [[0, 40], [100, 40], [100, 90], [0, 90]],
                    "point_mode": "bottom_center",
                    "target_classes": ["Person", "Bus"],
                }
            ],
            "event_rules": {
                "long_stay": {
                    "enabled": True,
                    "event_type": "long_stay",
                    "roi_id": "roi_main",
                    "target_classes": ["Person"],
                    "severity": "warning",
                    "parameters": {"min_duration_sec": 1.0},
                }
            },
        }
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _write_overlay_plan_json(path: Path) -> Path:
    payload = {
        "line_plans": [{"line_id": "line_main", "points": [[0, 50], [100, 50]]}],
        "roi_plans": [{"roi_id": "roi_main", "polygon": [[0, 40], [100, 40], [100, 90], [0, 90]]}],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"video")
    return path
