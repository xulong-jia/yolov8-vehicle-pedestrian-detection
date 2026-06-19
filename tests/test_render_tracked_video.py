import csv
import json
import sys
from pathlib import Path

import pytest

from src.render_tracked_video import (
    color_for_track_id,
    extract_overlay_config,
    group_tracks_by_frame,
    main,
    normalize_track_row,
    render_tracked_video,
)


TRACK_FIELDS = [
    "frame_index",
    "track_id",
    "class_name",
    "confidence",
    "xmin",
    "ymin",
    "xmax",
    "ymax",
]


def test_normalize_track_row_converts_types_and_defaults_class():
    track = normalize_track_row(
        {
            "frame_index": "3",
            "track_id": 7,
            "xmin": "10.2",
            "ymin": "20",
            "xmax": "30",
            "ymax": "40.7",
        }
    )

    assert track == {
        "frame_index": 3,
        "track_id": "7",
        "class_name": "unknown",
        "confidence": None,
        "bbox": [10.2, 20.0, 30.0, 40.7],
    }


def test_group_tracks_by_frame_groups_normalized_rows():
    grouped = group_tracks_by_frame(
        [
            _track_row(frame=1, track_id="a", class_name="Person", confidence="0.9"),
            _track_row(frame=1, track_id="b", class_name="Car", confidence="0.8"),
            _track_row(frame=2, track_id="a", class_name="Person", confidence="0.9"),
        ]
    )

    assert sorted(grouped) == [1, 2]
    assert [track["track_id"] for track in grouped[1]] == ["a", "b"]


def test_color_for_track_id_is_deterministic_bgr_tuple():
    first = color_for_track_id("42")
    second = color_for_track_id("42")

    assert first == second
    assert len(first) == 3
    assert all(isinstance(value, int) and 0 <= value <= 255 for value in first)


def test_extract_overlay_config_supports_direct_suggested_and_plan():
    direct = extract_overlay_config(
        config_json={
            "lines": [{"id": "line_a", "points": [[0, 10], [100, 10]]}],
            "rois": [{"id": "roi_a", "polygon": [[0, 0], [10, 0], [10, 10]]}],
        }
    )
    suggested = extract_overlay_config(
        config_json={
            "suggested_config": {
                "lines": [{"line_id": "line_s", "points": [[0, 20], [100, 20]]}],
                "rois": [{"roi_id": "roi_s", "polygon": [[0, 0], [20, 0], [20, 20]]}],
            }
        }
    )
    planned = extract_overlay_config(
        overlay_plan_json={
            "line_plans": [{"line_id": "line_p", "points": [[0, 30], [100, 30]]}],
            "roi_plans": [{"roi_id": "roi_p", "polygon": [[0, 0], [30, 0], [30, 30]]}],
        }
    )

    assert direct["lines"][0]["id"] == "line_a"
    assert suggested["lines"][0]["line_id"] == "line_s"
    assert planned["lines"][0]["line_id"] == "line_p"
    assert planned["rois"][0]["roi_id"] == "roi_p"


def test_render_tracked_video_with_fake_cv2_draws_tracks_and_overlays(tmp_path, monkeypatch):
    fake_cv2 = FakeCV2(frame_count=3)
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)
    video_path = _touch(tmp_path / "source.mp4")
    tracks_csv = _write_tracks_csv(tmp_path / "tracks.csv")
    config_json = _write_config_json(tmp_path / "config.json")
    output_video = tmp_path / "tracked.mp4"

    summary = render_tracked_video(
        video_path=video_path,
        tracks_csv=tracks_csv,
        output_video=output_video,
        config_json=config_json,
        max_frames=None,
    )

    assert summary["ok"] is True
    assert summary["mode"] == "tracked_video_rendering"
    assert summary["frames_written"] == 3
    assert summary["track_rows_loaded"] == 3
    assert summary["unique_tracks"] == 2
    assert summary["frames_with_tracks"] == 2
    assert summary["line_overlay_count"] == 1
    assert summary["roi_overlay_count"] == 1
    assert summary["fps"] == 30.0
    assert summary["width"] == 640
    assert summary["height"] == 480
    assert fake_cv2.writer.frames_written == 3
    assert fake_cv2.calls["rectangle"] == 3
    assert fake_cv2.calls["putText"] >= 3
    assert fake_cv2.calls["line"] >= 6


def test_render_tracked_video_respects_max_frames(tmp_path, monkeypatch):
    fake_cv2 = FakeCV2(frame_count=5)
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)
    summary = render_tracked_video(
        video_path=_touch(tmp_path / "source.mp4"),
        tracks_csv=_write_tracks_csv(tmp_path / "tracks.csv"),
        output_video=tmp_path / "tracked.mp4",
        max_frames=2,
    )

    assert summary["frames_read"] == 2
    assert summary["frames_written"] == 2


def test_render_tracked_video_can_disable_tracks_and_overlays(tmp_path, monkeypatch):
    fake_cv2 = FakeCV2(frame_count=2)
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)

    summary = render_tracked_video(
        video_path=_touch(tmp_path / "source.mp4"),
        tracks_csv=_write_tracks_csv(tmp_path / "tracks.csv"),
        output_video=tmp_path / "tracked.mp4",
        config_json=_write_config_json(tmp_path / "config.json"),
        draw_tracks=False,
        draw_overlays=False,
    )

    assert summary["draw_tracks"] is False
    assert summary["draw_overlays"] is False
    assert summary["line_overlay_count"] == 0
    assert summary["roi_overlay_count"] == 0
    assert fake_cv2.calls["rectangle"] == 0
    assert fake_cv2.calls["line"] == 0


def test_missing_video_or_tracks_fails_without_output(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "cv2", FakeCV2(frame_count=1))
    output_video = tmp_path / "tracked.mp4"

    with pytest.raises(FileNotFoundError, match="video not found"):
        render_tracked_video(
            video_path=tmp_path / "missing.mp4",
            tracks_csv=_write_tracks_csv(tmp_path / "tracks.csv"),
            output_video=output_video,
        )

    with pytest.raises(FileNotFoundError, match="tracks_csv not found"):
        render_tracked_video(
            video_path=_touch(tmp_path / "source.mp4"),
            tracks_csv=tmp_path / "missing.csv",
            output_video=output_video,
        )

    assert not output_video.exists()


def test_main_prints_json_summary_with_fake_cv2(tmp_path, monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "cv2", FakeCV2(frame_count=2))
    result = main(
        [
            "--video",
            str(_touch(tmp_path / "source.mp4")),
            "--tracks-csv",
            str(_write_tracks_csv(tmp_path / "tracks.csv")),
            "--output-video",
            str(tmp_path / "tracked.mp4"),
            "--config-json",
            str(_write_config_json(tmp_path / "config.json")),
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert result == 0
    assert payload["ok"] is True
    assert payload["frames_written"] == 2


def test_source_has_no_forbidden_dependencies_and_cv2_is_lazy():
    source = Path("src/render_tracked_video.py").read_text(encoding="utf-8")

    assert "ultralytics" not in source
    assert "torch" not in source
    assert "numpy" not in source
    assert "import cv2" in source
    assert "import cv2" not in "\n".join(source.splitlines()[:20])


class FakeFrame:
    shape = (480, 640, 3)


class FakeCapture:
    def __init__(self, path, frame_count, opened=True):
        self.path = path
        self.frame_count = frame_count
        self.opened = opened
        self.index = 0
        self.released = False

    def isOpened(self):
        return self.opened

    def get(self, prop):
        if prop == FakeCV2.CAP_PROP_FRAME_WIDTH:
            return 640
        if prop == FakeCV2.CAP_PROP_FRAME_HEIGHT:
            return 480
        if prop == FakeCV2.CAP_PROP_FPS:
            return 30
        if prop == FakeCV2.CAP_PROP_FRAME_COUNT:
            return self.frame_count
        return 0

    def read(self):
        if self.index >= self.frame_count:
            return False, None
        self.index += 1
        return True, FakeFrame()

    def set(self, prop, value):
        if prop == FakeCV2.CAP_PROP_POS_FRAMES:
            self.index = int(value)
        return True

    def release(self):
        self.released = True


class FakeWriter:
    def __init__(self, path, fourcc, fps, size):
        self.path = path
        self.fourcc = fourcc
        self.fps = fps
        self.size = size
        self.frames_written = 0
        self.released = False

    def write(self, frame):
        self.frames_written += 1

    def release(self):
        self.released = True
        Path(self.path).write_bytes(b"fake-video")


class FakeCV2:
    CAP_PROP_FRAME_WIDTH = 3
    CAP_PROP_FRAME_HEIGHT = 4
    CAP_PROP_FPS = 5
    CAP_PROP_FRAME_COUNT = 7
    CAP_PROP_POS_FRAMES = 1
    FONT_HERSHEY_SIMPLEX = 0

    def __init__(self, frame_count):
        self.frame_count = frame_count
        self.calls = {"rectangle": 0, "putText": 0, "line": 0}
        self.writer = None

    def VideoCapture(self, path):
        return FakeCapture(path, self.frame_count)

    def VideoWriter_fourcc(self, *codec):
        return "".join(codec)

    def VideoWriter(self, path, fourcc, fps, size):
        self.writer = FakeWriter(path, fourcc, fps, size)
        return self.writer

    def rectangle(self, frame, start, end, color, thickness):
        self.calls["rectangle"] += 1

    def putText(self, frame, text, origin, font, scale, color, thickness):
        self.calls["putText"] += 1

    def line(self, frame, start, end, color, thickness):
        self.calls["line"] += 1


def _write_tracks_csv(path: Path) -> Path:
    rows = [
        _track_row(frame=0, track_id="1", class_name="Person", confidence="0.91"),
        _track_row(frame=1, track_id="1", class_name="Person", confidence="0.92"),
        _track_row(frame=1, track_id="2", class_name="Car", confidence=""),
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=TRACK_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _track_row(frame: int, track_id: str, class_name: str, confidence: str) -> dict[str, str]:
    return {
        "frame_index": str(frame),
        "track_id": track_id,
        "class_name": class_name,
        "confidence": confidence,
        "xmin": "10",
        "ymin": "20",
        "xmax": "60",
        "ymax": "80",
    }


def _write_config_json(path: Path) -> Path:
    payload = {
        "suggested_config": {
            "lines": [{"line_id": "line_main", "points": [[0, 100], [640, 100]]}],
            "rois": [{"roi_id": "roi_main", "polygon": [[10, 10], [100, 10], [100, 120], [10, 120]]}],
        }
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _touch(path: Path) -> Path:
    path.write_bytes(b"video")
    return path
