import csv
import json

import pytest

from src.track_video import (
    detections_to_synthetic_tracks,
    main,
    parse_args,
    run_video_metadata_skeleton,
    run_track_video_skeleton,
)
from src.tracking.track_writer import TRACKS_FIELDS


DETECTIONS_FIELDS = [
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


def test_parse_args_supports_required_paths_and_default_tracker(tmp_path):
    args = parse_args(
        [
            "--detections-csv",
            str(tmp_path / "detections.csv"),
            "--output-dir",
            str(tmp_path / "tracks"),
        ]
    )

    assert args.detections_csv == tmp_path / "detections.csv"
    assert args.output_dir == tmp_path / "tracks"
    assert args.tracker == "synthetic"
    assert args.metadata_only is False
    assert args.sample_every_n == 1
    assert args.max_frames is None


def test_parse_args_supports_metadata_only_video_mode(tmp_path):
    args = parse_args(
        [
            "--video-source",
            str(tmp_path / "demo.mp4"),
            "--output-dir",
            str(tmp_path / "metadata"),
            "--metadata-only",
            "--sample-every-n",
            "2",
            "--max-frames",
            "3",
        ]
    )

    assert args.video_source == tmp_path / "demo.mp4"
    assert args.output_dir == tmp_path / "metadata"
    assert args.metadata_only is True
    assert args.sample_every_n == 2
    assert args.max_frames == 3


def test_parse_args_requires_input_and_output_paths():
    with pytest.raises(SystemExit):
        parse_args([])


def test_parse_args_rejects_video_source_without_metadata_only(tmp_path):
    with pytest.raises(SystemExit):
        parse_args(
            [
                "--video-source",
                str(tmp_path / "demo.mp4"),
                "--output-dir",
                str(tmp_path / "metadata"),
            ]
        )


def test_parse_args_rejects_non_positive_sample_every_n(tmp_path):
    with pytest.raises(SystemExit):
        parse_args(
            [
                "--video-source",
                str(tmp_path / "demo.mp4"),
                "--output-dir",
                str(tmp_path / "metadata"),
                "--metadata-only",
                "--sample-every-n",
                "0",
            ]
        )


def test_detections_to_synthetic_tracks_builds_tracks_contract_rows():
    rows = [
        {
            "video_id": "video-1",
            "frame_index": "3",
            "timestamp_sec": "0.12",
            "detection_id": "det-7",
            "class_id": "0",
            "class_name": "Car",
            "confidence": "0.91",
            "xmin": "10",
            "ymin": "20",
            "xmax": "30",
            "ymax": "60",
        },
        {
            "video_id": "video-1",
            "frame_index": "4",
            "timestamp_sec": "0.16",
            "detection_id": "det-7",
            "class_id": "0",
            "class_name": "Car",
            "confidence": "0.93",
            "xmin": "12",
            "ymin": "22",
            "xmax": "32",
            "ymax": "62",
        },
    ]

    tracks = detections_to_synthetic_tracks(rows, tracker_name="synthetic")

    assert len(tracks) == 2
    assert all(field in tracks[0] for field in TRACKS_FIELDS)
    assert tracks[0]["track_id"] == "det-7"
    assert tracks[1]["track_id"] == "det-7"
    assert tracks[0]["class_id"] == 0
    assert tracks[0]["confidence"] == 0.91
    assert tracks[0]["center_x"] == 20.0
    assert tracks[0]["center_y"] == 40.0
    assert tracks[0]["box_width"] == 20.0
    assert tracks[0]["box_height"] == 40.0
    assert tracks[0]["box_area"] == 800.0
    assert tracks[0]["state"] == "confirmed"
    assert tracks[0]["tracker_name"] == "synthetic"


def test_detections_to_synthetic_tracks_generates_stable_track_id_when_missing():
    tracks = detections_to_synthetic_tracks(
        [
            {
                "video_id": "video-1",
                "frame_index": "1",
                "timestamp_sec": "0.04",
                "class_id": "person",
                "class_name": "Person",
                "confidence": "0.8",
                "xmin": "1",
                "ymin": "2",
                "xmax": "5",
                "ymax": "10",
            }
        ]
    )

    assert tracks[0]["track_id"] == "synthetic_1"
    assert tracks[0]["class_id"] == "person"


def test_run_track_video_skeleton_writes_tracks_csv(tmp_path):
    detections_csv = tmp_path / "detections.csv"
    output_dir = tmp_path / "out"
    _write_detections_csv(
        detections_csv,
        [
            {
                "video_id": "video-1",
                "frame_index": 1,
                "timestamp_sec": 0.04,
                "detection_id": "det-1",
                "class_id": 0,
                "class_name": "Car",
                "confidence": 0.9,
                "xmin": 0,
                "ymin": 0,
                "xmax": 10,
                "ymax": 20,
            }
        ],
    )

    summary = run_track_video_skeleton(detections_csv, output_dir)

    tracks_csv = output_dir / "tracks.csv"
    assert tracks_csv.exists()
    assert summary == {
        "tracker_name": "synthetic",
        "input_rows": 1,
        "track_rows": 1,
        "output_tracks_csv": str(tracks_csv),
    }
    with tracks_csv.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        assert reader.fieldnames == TRACKS_FIELDS
        assert list(reader)[0]["track_id"] == "det-1"


def test_run_track_video_skeleton_uses_tracker_adapter_factory(tmp_path, monkeypatch):
    detections_csv = tmp_path / "detections.csv"
    output_dir = tmp_path / "out"
    _write_detections_csv(
        detections_csv,
        [
            {
                "video_id": "video-1",
                "frame_index": 1,
                "timestamp_sec": 0.04,
                "detection_id": "det-1",
                "class_id": 0,
                "class_name": "Car",
                "confidence": 0.9,
                "xmin": 0,
                "ymin": 0,
                "xmax": 10,
                "ymax": 20,
            }
        ],
    )
    calls = {"factory_tracker_name": None, "update_rows": None}

    class FakeAdapter:
        def update(self, detection_rows):
            calls["update_rows"] = detection_rows
            return [
                {
                    "video_id": "video-1",
                    "frame_index": 1,
                    "timestamp_sec": 0.04,
                    "track_id": "fake-track-1",
                    "class_id": 0,
                    "class_name": "Car",
                    "confidence": 0.9,
                    "xmin": 0,
                    "ymin": 0,
                    "xmax": 10,
                    "ymax": 20,
                    "center_x": 5,
                    "center_y": 10,
                    "box_width": 10,
                    "box_height": 20,
                    "box_area": 200,
                    "state": "confirmed",
                    "tracker_name": "synthetic",
                }
            ]

    def fake_factory(tracker_name):
        calls["factory_tracker_name"] = tracker_name
        return FakeAdapter()

    monkeypatch.setattr("src.track_video.create_tracker_adapter", fake_factory)

    summary = run_track_video_skeleton(detections_csv, output_dir, tracker_name="synthetic")

    assert calls["factory_tracker_name"] == "synthetic"
    assert calls["update_rows"][0]["detection_id"] == "det-1"
    assert summary["tracker_name"] == "synthetic"
    assert summary["track_rows"] == 1
    with (output_dir / "tracks.csv").open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    assert rows[0]["track_id"] == "fake-track-1"


def test_run_track_video_skeleton_writes_header_for_empty_detections(tmp_path):
    detections_csv = tmp_path / "empty_detections.csv"
    output_dir = tmp_path / "out"
    _write_detections_csv(detections_csv, [])

    summary = run_track_video_skeleton(detections_csv, output_dir)

    tracks_csv = output_dir / "tracks.csv"
    assert summary["input_rows"] == 0
    assert summary["track_rows"] == 0
    assert tracks_csv.read_text(encoding="utf-8").splitlines()[0].split(",") == TRACKS_FIELDS


def test_run_track_video_skeleton_rejects_unknown_tracker(tmp_path):
    detections_csv = tmp_path / "detections.csv"
    _write_detections_csv(detections_csv, [])

    with pytest.raises(ValueError, match="Unsupported tracker_type"):
        run_track_video_skeleton(detections_csv, tmp_path / "out", tracker_name="unknown")


@pytest.mark.parametrize("tracker_name", ["bytetrack", "deepsort"])
def test_run_track_video_skeleton_propagates_placeholder_tracker_errors(
    tmp_path,
    tracker_name,
):
    detections_csv = tmp_path / "detections.csv"
    _write_detections_csv(detections_csv, [])

    with pytest.raises(NotImplementedError, match="not integrated"):
        run_track_video_skeleton(detections_csv, tmp_path / "out", tracker_name=tracker_name)


def test_run_video_metadata_skeleton_writes_metadata_and_frame_index(tmp_path, monkeypatch):
    video_path = tmp_path / "demo.mp4"
    video_path.write_bytes(b"")
    output_dir = tmp_path / "metadata"
    monkeypatch.setattr("src.track_video.read_video_metadata", _fake_read_video_metadata)

    summary = run_video_metadata_skeleton(
        video_path,
        output_dir,
        sample_every_n=2,
    )

    metadata_json = output_dir / "video_metadata.json"
    frame_index_csv = output_dir / "frame_index.csv"
    assert metadata_json.exists()
    assert frame_index_csv.exists()
    assert summary["mode"] == "metadata_only"
    assert summary["video_source"] == str(video_path)
    assert summary["output_metadata_json"] == str(metadata_json)
    assert summary["output_frame_index_csv"] == str(frame_index_csv)
    assert summary["frame_index_rows"] == 5
    assert summary["fps"] == 5.0
    assert summary["width"] == 64
    assert summary["height"] == 48
    assert summary["frame_count"] == 10
    assert summary["duration_sec"] == 2.0

    with frame_index_csv.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    assert [int(row["frame_index"]) for row in rows] == [0, 2, 4, 6, 8]


def test_run_video_metadata_skeleton_honors_max_frames(tmp_path, monkeypatch):
    video_path = tmp_path / "demo.mp4"
    video_path.write_bytes(b"")
    output_dir = tmp_path / "metadata"
    monkeypatch.setattr("src.track_video.read_video_metadata", _fake_read_video_metadata)

    summary = run_video_metadata_skeleton(
        video_path,
        output_dir,
        sample_every_n=2,
        max_frames=3,
    )

    assert summary["frame_index_rows"] == 3
    with (output_dir / "frame_index.csv").open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    assert [int(row["frame_index"]) for row in rows] == [0, 2, 4]


def test_main_metadata_only_writes_artifacts_and_prints_summary(tmp_path, monkeypatch, capsys):
    video_path = tmp_path / "demo.mp4"
    video_path.write_bytes(b"")
    output_dir = tmp_path / "metadata"
    monkeypatch.setattr("src.track_video.read_video_metadata", _fake_read_video_metadata)

    result = main(
        [
            "--video-source",
            str(video_path),
            "--output-dir",
            str(output_dir),
            "--metadata-only",
            "--sample-every-n",
            "2",
            "--max-frames",
            "3",
        ]
    )

    assert result == 0
    assert (output_dir / "video_metadata.json").exists()
    assert (output_dir / "frame_index.csv").exists()
    printed_summary = json.loads(capsys.readouterr().out)
    assert printed_summary["mode"] == "metadata_only"
    assert printed_summary["frame_index_rows"] == 3


def test_main_writes_tracks_csv_and_prints_summary(tmp_path, capsys):
    detections_csv = tmp_path / "detections.csv"
    output_dir = tmp_path / "out"
    _write_detections_csv(
        detections_csv,
        [
            {
                "video_id": "video-1",
                "frame_index": 1,
                "timestamp_sec": 0.04,
                "detection_id": "det-1",
                "class_id": 0,
                "class_name": "Car",
                "confidence": 0.9,
                "xmin": 0,
                "ymin": 0,
                "xmax": 10,
                "ymax": 20,
            }
        ],
    )

    result = main(
        [
            "--detections-csv",
            str(detections_csv),
            "--output-dir",
            str(output_dir),
        ]
    )

    assert result == 0
    assert (output_dir / "tracks.csv").exists()
    printed_summary = json.loads(capsys.readouterr().out)
    assert printed_summary["track_rows"] == 1


def test_main_accepts_explicit_synthetic_tracker(tmp_path, capsys):
    detections_csv = tmp_path / "detections.csv"
    output_dir = tmp_path / "out"
    _write_detections_csv(detections_csv, [])

    result = main(
        [
            "--detections-csv",
            str(detections_csv),
            "--output-dir",
            str(output_dir),
            "--tracker",
            "synthetic",
        ]
    )

    assert result == 0
    printed_summary = json.loads(capsys.readouterr().out)
    assert printed_summary["tracker_name"] == "synthetic"


def test_main_propagates_placeholder_tracker_errors(tmp_path):
    detections_csv = tmp_path / "detections.csv"
    _write_detections_csv(detections_csv, [])

    with pytest.raises(NotImplementedError, match="not integrated"):
        main(
            [
                "--detections-csv",
                str(detections_csv),
                "--output-dir",
                str(tmp_path / "out"),
                "--tracker",
                "bytetrack",
            ]
        )


def test_metadata_only_mode_does_not_call_tracker_adapter_factory(tmp_path, monkeypatch):
    video_path = tmp_path / "demo.mp4"
    video_path.write_bytes(b"")
    monkeypatch.setattr("src.track_video.read_video_metadata", _fake_read_video_metadata)

    def fail_factory(tracker_name):
        raise AssertionError(f"metadata-only mode called tracker factory: {tracker_name}")

    monkeypatch.setattr("src.track_video.create_tracker_adapter", fail_factory)

    summary = run_video_metadata_skeleton(video_path, tmp_path / "metadata")

    assert summary["mode"] == "metadata_only"


def test_track_video_skeleton_uses_tmp_path_only(tmp_path):
    detections_csv = tmp_path / "detections.csv"
    _write_detections_csv(detections_csv, [])

    run_track_video_skeleton(detections_csv, tmp_path / "out")

    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()
    assert not (tmp_path / "runs").exists()


def test_video_metadata_skeleton_uses_tmp_path_only(tmp_path, monkeypatch):
    video_path = tmp_path / "demo.mp4"
    video_path.write_bytes(b"")
    monkeypatch.setattr("src.track_video.read_video_metadata", _fake_read_video_metadata)

    run_video_metadata_skeleton(video_path, tmp_path / "metadata")

    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()
    assert not (tmp_path / "runs").exists()


def _write_detections_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=DETECTIONS_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _fake_read_video_metadata(video_path):
    return {
        "video_path": "/tmp/demo.mp4",
        "filename": "demo.mp4",
        "fps": 5.0,
        "width": 64,
        "height": 48,
        "frame_count": 10,
        "duration_sec": 2.0,
        "backend": "opencv",
    }
