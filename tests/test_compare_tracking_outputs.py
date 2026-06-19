import csv
import json
import subprocess
import sys
from pathlib import Path

from src.compare_tracking_outputs import (
    build_tracking_comparison,
    compare_track_summaries,
    load_optional_analysis_summary,
    summarize_tracks,
)


TRACK_FIELDS = [
    "video_id",
    "frame_index",
    "timestamp_sec",
    "track_id",
    "class_name",
    "confidence",
    "xmin",
    "ymin",
    "xmax",
    "ymax",
    "state",
]


def test_summarize_tracks_counts_rows_tracks_frames_classes_states_and_distributions():
    rows = [
        _track_row(frame=0, track_id="s1", class_name="Person", confidence="0.9", xmin=0, ymin=0, xmax=10, ymax=10),
        _track_row(frame=1, track_id="s1", class_name="Person", confidence="0.8", xmin=0, ymin=0, xmax=20, ymax=10),
        _track_row(frame=1, track_id="s2", class_name="Bus", confidence="", xmin=5, ymin=5, xmax=15, ymax=15),
    ]

    summary = summarize_tracks(rows)

    assert summary["row_count"] == 3
    assert summary["unique_tracks"] == 2
    assert summary["frames_with_rows"] == 2
    assert summary["frame_min"] == 0
    assert summary["frame_max"] == 1
    assert summary["class_counts"] == {"Person": 2, "Bus": 1}
    assert summary["state_counts"] == {"confirmed": 3}
    assert summary["rows_per_track"] == {"min": 1, "max": 2, "avg": 1.5}
    assert summary["rows_per_frame"] == {"min": 1, "max": 2, "avg": 1.5}
    assert summary["bbox_area"]["min"] == 100
    assert summary["bbox_area"]["max"] == 200
    assert summary["confidence"] == {"min": 0.8, "max": 0.9, "avg": 0.8500000000000001}


def test_compare_track_summaries_returns_deltas_ratio_and_interpretation():
    comparison = compare_track_summaries(
        synthetic_summary={
            "row_count": 100,
            "unique_tracks": 10,
            "frames_with_rows": 50,
            "class_counts": {"Person": 90, "Bus": 10},
        },
        bytetrack_summary={
            "row_count": 25,
            "unique_tracks": 8,
            "frames_with_rows": 20,
            "class_counts": {"Person": 20, "Car": 5},
        },
    )

    assert comparison["row_count_delta"] == -75
    assert comparison["row_count_ratio_bytetrack_to_synthetic"] == 0.25
    assert comparison["unique_tracks_delta"] == -2
    assert comparison["frames_with_rows_delta"] == -30
    assert comparison["class_count_deltas"] == {"Bus": -10, "Car": 5, "Person": -70}
    interpretation = " ".join(comparison["interpretation"])
    assert "Synthetic tracks may overrepresent" in interpretation
    assert "ByteTrack tracks are sparser" in interpretation


def test_load_optional_analysis_summary_extracts_known_keys(tmp_path):
    path = tmp_path / "summary.json"
    path.write_text(
        json.dumps(
            {
                "detection_count": 10,
                "track_count": 2,
                "count_summary": {"total_count": 1},
                "roi_summary": {"frames_observed": 3},
                "event_summary": {"total_events": 4},
                "ignored": "value",
            }
        ),
        encoding="utf-8",
    )

    assert load_optional_analysis_summary(None) == {}
    assert load_optional_analysis_summary(path) == {
        "detection_count": 10,
        "track_count": 2,
        "count_summary": {"total_count": 1},
        "roi_summary": {"frames_observed": 3},
        "event_summary": {"total_events": 4},
    }


def test_build_tracking_comparison_contains_sections_recommendation_and_notes(tmp_path):
    synthetic_tracks = _write_tracks_csv(tmp_path / "synthetic.csv", prefix="s", rows=3)
    bytetrack_tracks = _write_tracks_csv(tmp_path / "bytetrack.csv", prefix="b", rows=2)
    synthetic_summary = _write_analysis_summary(tmp_path / "synthetic_summary.json", track_count=3)
    bytetrack_summary = _write_analysis_summary(tmp_path / "bytetrack_summary.json", track_count=2)

    comparison = build_tracking_comparison(
        synthetic_tracks_csv=synthetic_tracks,
        bytetrack_tracks_csv=bytetrack_tracks,
        synthetic_analysis_summary=synthetic_summary,
        bytetrack_analysis_summary=bytetrack_summary,
        video_id="demo",
    )

    assert comparison["video_id"] == "demo"
    assert comparison["mode"] == "synthetic_vs_bytetrack_tracking_comparison"
    assert comparison["synthetic"]["track_summary"]["row_count"] == 3
    assert comparison["bytetrack"]["track_summary"]["row_count"] == 2
    assert comparison["comparison"]["row_count_delta"] == -1
    assert comparison["recommendation"]["preferred_demo_tracks"] == "bytetrack"
    assert "deterministic unit tests" in comparison["recommendation"]["keep_synthetic_for"]
    assert comparison["notes"]


def test_cli_stdout_json_without_output_file(tmp_path):
    synthetic_tracks = _write_tracks_csv(tmp_path / "synthetic.csv", prefix="s", rows=2)
    bytetrack_tracks = _write_tracks_csv(tmp_path / "bytetrack.csv", prefix="b", rows=1)
    output_json = tmp_path / "comparison.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.compare_tracking_outputs",
            "--synthetic-tracks",
            str(synthetic_tracks),
            "--bytetrack-tracks",
            str(bytetrack_tracks),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload["comparison"]["row_count_delta"] == -1
    assert not output_json.exists()


def test_cli_output_json_writes_requested_tmp_path_file(tmp_path):
    synthetic_tracks = _write_tracks_csv(tmp_path / "synthetic.csv", prefix="s", rows=2)
    bytetrack_tracks = _write_tracks_csv(tmp_path / "bytetrack.csv", prefix="b", rows=1)
    output_json = tmp_path / "nested" / "comparison.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.compare_tracking_outputs",
            "--synthetic-tracks",
            str(synthetic_tracks),
            "--bytetrack-tracks",
            str(bytetrack_tracks),
            "--video-id",
            "demo",
            "--output-json",
            str(output_json),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert output_json.exists()
    assert json.loads(output_json.read_text(encoding="utf-8"))["video_id"] == "demo"
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "runs").exists()


def test_cli_missing_file_returns_error_without_partial_output(tmp_path):
    output_json = tmp_path / "comparison.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.compare_tracking_outputs",
            "--synthetic-tracks",
            str(tmp_path / "missing.csv"),
            "--bytetrack-tracks",
            str(tmp_path / "missing2.csv"),
            "--output-json",
            str(output_json),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "not found" in result.stderr
    assert not output_json.exists()


def test_source_has_no_heavy_runtime_imports():
    source = Path("src/compare_tracking_outputs.py").read_text(encoding="utf-8")
    assert "ultralytics" not in source
    assert "cv2" not in source
    assert "torch" not in source
    assert "numpy" not in source


def _write_tracks_csv(path: Path, prefix: str, rows: int) -> Path:
    records = [
        _track_row(
            frame=index,
            track_id=f"{prefix}{index % 2}",
            class_name="Person" if index % 2 == 0 else "Bus",
            confidence="0.9",
            xmin=index,
            ymin=index,
            xmax=index + 10,
            ymax=index + 20,
        )
        for index in range(rows)
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=TRACK_FIELDS)
        writer.writeheader()
        writer.writerows(records)
    return path


def _track_row(
    frame: int,
    track_id: str,
    class_name: str,
    confidence: str,
    xmin: int,
    ymin: int,
    xmax: int,
    ymax: int,
) -> dict[str, str]:
    return {
        "video_id": "demo",
        "frame_index": str(frame),
        "timestamp_sec": str(frame / 30),
        "track_id": track_id,
        "class_name": class_name,
        "confidence": confidence,
        "xmin": str(xmin),
        "ymin": str(ymin),
        "xmax": str(xmax),
        "ymax": str(ymax),
        "state": "confirmed",
    }


def _write_analysis_summary(path: Path, track_count: int) -> Path:
    path.write_text(
        json.dumps(
            {
                "detection_count": 5,
                "track_count": track_count,
                "count_summary": {"total_count": 1},
                "roi_summary": {"frames_observed": 2},
                "event_summary": {"total_events": 3},
            }
        ),
        encoding="utf-8",
    )
    return path
