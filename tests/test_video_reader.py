import csv
import json

import pytest

from src.video_reader import (
    build_frame_index,
    read_video_metadata,
    validate_video_path,
    write_frame_index_csv,
    write_video_metadata_json,
)


def test_validate_video_path_returns_existing_file(tmp_path):
    video_path = tmp_path / "tiny.mp4"
    video_path.write_bytes(b"placeholder")

    assert validate_video_path(video_path) == video_path


def test_validate_video_path_rejects_missing_path(tmp_path):
    with pytest.raises(FileNotFoundError):
        validate_video_path(tmp_path / "missing.mp4")


def test_validate_video_path_rejects_directory(tmp_path):
    with pytest.raises(ValueError):
        validate_video_path(tmp_path)


def test_read_video_metadata_from_tiny_video(tmp_path):
    cv2 = pytest.importorskip("cv2")
    video_path = tmp_path / "tiny.avi"
    _write_tiny_video(cv2, video_path, width=64, height=48, fps=5, frames=10)

    metadata = read_video_metadata(video_path)

    assert metadata["video_path"] == str(video_path)
    assert metadata["filename"] == "tiny.avi"
    assert metadata["width"] == 64
    assert metadata["height"] == 48
    assert metadata["frame_count"] == 10
    assert metadata["fps"] > 0
    assert metadata["duration_sec"] > 0
    assert metadata["backend"] == "opencv"


def test_build_frame_index_uses_frame_timestamps():
    metadata = {"filename": "demo.avi", "fps": 5, "frame_count": 10}

    frame_index = build_frame_index(metadata)

    assert len(frame_index) == 10
    assert set(frame_index[0]) == {"video_id", "filename", "frame_index", "timestamp_sec"}
    assert frame_index[0] == {
        "video_id": "demo.avi",
        "filename": "demo.avi",
        "frame_index": 0,
        "timestamp_sec": 0.0,
    }
    assert frame_index[9]["timestamp_sec"] == 9 / 5


def test_build_frame_index_sampling_and_max_frames():
    metadata = {"filename": "demo.avi", "fps": 5, "frame_count": 10}

    sampled = build_frame_index(metadata, sample_every_n=2)
    limited = build_frame_index(metadata, sample_every_n=2, max_frames=3)

    assert [row["frame_index"] for row in sampled] == [0, 2, 4, 6, 8]
    assert [row["frame_index"] for row in limited] == [0, 2, 4]


def test_build_frame_index_uses_video_id_when_available():
    metadata = {"video_id": "video-1", "filename": "demo.avi", "fps": 5, "frame_count": 1}

    assert build_frame_index(metadata)[0]["video_id"] == "video-1"


@pytest.mark.parametrize(
    "metadata",
    [
        {"filename": "demo.avi", "fps": 0, "frame_count": 10},
        {"filename": "demo.avi", "fps": -1, "frame_count": 10},
        {"filename": "demo.avi", "fps": 5, "frame_count": -1},
    ],
)
def test_build_frame_index_rejects_invalid_metadata(metadata):
    with pytest.raises(ValueError):
        build_frame_index(metadata)


def test_build_frame_index_rejects_invalid_sample_every_n():
    metadata = {"filename": "demo.avi", "fps": 5, "frame_count": 10}

    with pytest.raises(ValueError):
        build_frame_index(metadata, sample_every_n=0)


def test_write_frame_index_csv_writes_header_and_rows(tmp_path):
    output_path = tmp_path / "nested" / "frame_index.csv"
    frame_index = [
        {"video_id": "video-1", "filename": "demo.avi", "frame_index": 0, "timestamp_sec": 0.0},
        {"video_id": "video-1", "filename": "demo.avi", "frame_index": 1, "timestamp_sec": 0.2},
    ]

    written_path = write_frame_index_csv(frame_index, output_path)

    assert written_path == output_path
    with output_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        assert reader.fieldnames == ["video_id", "filename", "frame_index", "timestamp_sec"]
        assert len(list(reader)) == 2


def test_write_frame_index_csv_writes_header_for_empty_rows(tmp_path):
    output_path = tmp_path / "frame_index.csv"

    write_frame_index_csv([], output_path)

    assert output_path.read_text(encoding="utf-8").splitlines()[0].split(",") == [
        "video_id",
        "filename",
        "frame_index",
        "timestamp_sec",
    ]


def test_write_video_metadata_json_round_trips_metadata(tmp_path):
    output_path = tmp_path / "nested" / "video_metadata.json"
    metadata = {
        "filename": "demo.avi",
        "width": 64,
        "height": 48,
        "fps": 5,
        "frame_count": 10,
    }

    written_path = write_video_metadata_json(metadata, output_path)

    assert written_path == output_path
    assert json.loads(output_path.read_text(encoding="utf-8")) == metadata


def test_video_reader_outputs_use_tmp_path_only(tmp_path):
    write_frame_index_csv([], tmp_path / "frame_index.csv")
    write_video_metadata_json({"fps": 5, "frame_count": 0}, tmp_path / "video_metadata.json")

    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()
    assert not (tmp_path / "runs").exists()


def _write_tiny_video(cv2, video_path, width, height, fps, frames):
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    writer = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))
    if not writer.isOpened():
        pytest.skip("OpenCV cannot create a tiny test video in this environment")
    try:
        frame = _black_frame(height, width)
        for _ in range(frames):
            writer.write(frame)
    finally:
        writer.release()


def _black_frame(height, width):
    np = pytest.importorskip("numpy")
    return np.zeros((height, width, 3), dtype=np.uint8)
