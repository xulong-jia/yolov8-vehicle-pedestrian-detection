import json
import os
import subprocess
import sys
from pathlib import Path

from src import run_video_analysis_smoke


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_smoke_preflight_module_help():
    result = subprocess.run(
        [sys.executable, "-m", "src.smoke_preflight", "--help"],
        cwd=PROJECT_ROOT,
        env=_test_env(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--model" in result.stdout
    assert "--video" in result.stdout
    assert "--output-dir" in result.stdout


def test_run_video_analysis_smoke_module_help():
    result = subprocess.run(
        [sys.executable, "-m", "src.run_video_analysis_smoke", "--help"],
        cwd=PROJECT_ROOT,
        env=_test_env(),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--model" in result.stdout
    assert "--source" in result.stdout
    assert "--output-dir" in result.stdout


def test_smoke_preflight_module_execution_does_not_create_outputs(tmp_path):
    model_path = tmp_path / "fake_model.pt"
    video_path = tmp_path / "fake_video.mp4"
    output_dir = tmp_path / "would_be_output"
    model_path.write_text("fake model", encoding="utf-8")
    video_path.write_text("fake video", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.smoke_preflight",
            "--model",
            str(model_path),
            "--video",
            str(video_path),
            "--output-dir",
            str(output_dir),
        ],
        cwd=PROJECT_ROOT,
        env=_test_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(result.stdout)

    assert result.returncode in {0, 1}
    assert set(payload) >= {"ok", "checks", "commands"}
    assert payload["checks"]["model_path"]["ok"] is True
    assert payload["checks"]["video_path"]["ok"] is True
    assert payload["checks"]["output_dir"]["ok"] is True
    assert not output_dir.exists()
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()
    assert not (tmp_path / "runs").exists()


def test_run_video_analysis_smoke_main_still_unit_testable(tmp_path, monkeypatch, capsys):
    output_dir = tmp_path / "smoke"

    monkeypatch.setattr(
        run_video_analysis_smoke,
        "run_video_detection_csv",
        _fake_run_video_detection_csv,
    )
    monkeypatch.setattr(
        run_video_analysis_smoke,
        "run_track_video_skeleton",
        _fake_run_track_video_skeleton,
    )
    monkeypatch.setattr(
        run_video_analysis_smoke,
        "create_video_analysis_job_run",
        _fake_create_video_analysis_job_run,
    )

    result = run_video_analysis_smoke.main(
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
    payload = json.loads(capsys.readouterr().out)

    assert result == 0
    assert payload["video_id"] == "demo"
    assert payload["run_name"] == "demo_run"
    assert payload["mode"] == "four_step_smoke_runner"
    assert payload["detection_count"] == 1
    assert payload["track_row_count"] == 1
    assert payload["detections_csv"] == str(output_dir / "detections.csv")
    assert payload["tracks_csv"] == str(output_dir / "tracking" / "tracks.csv")
    assert (output_dir / "detections.csv").exists()
    assert (output_dir / "tracking" / "tracks.csv").exists()
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()
    assert not (tmp_path / "runs").exists()


def _test_env():
    env = os.environ.copy()
    env["PYTHONPYCACHEPREFIX"] = "/private/tmp/yolov8_pycache"
    return env


def _fake_run_video_detection_csv(
    model_path,
    source,
    output_csv,
    conf,
    imgsz,
    device,
    video_id,
):
    assert model_path == "fake_model.pt"
    assert source == "fake_video.mp4"
    assert conf == 0.25
    assert imgsz == 640
    assert device == "cpu"
    assert video_id == "demo"
    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    Path(output_csv).write_text(
        "video_id,frame_index,timestamp_sec,detection_id,class_id,class_name,confidence,xmin,ymin,xmax,ymax\n"
        "demo,0,0.0,1,1,Car,0.9,0,0,10,10\n",
        encoding="utf-8",
    )


def _fake_run_track_video_skeleton(input_csv, output_dir, tracker_name):
    assert Path(input_csv).name == "detections.csv"
    assert tracker_name == "synthetic"
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "tracks.csv").write_text(
        "video_id,frame_index,timestamp_sec,track_id,class_id,class_name,confidence,xmin,ymin,xmax,ymax,center_x,center_y,box_width,box_height,box_area,state,tracker_name\n"
        "demo,0,0.0,1,1,Car,0.9,0,0,10,10,5,5,10,10,100,confirmed,synthetic\n",
        encoding="utf-8",
    )


def _fake_create_video_analysis_job_run(
    run_name,
    base_dir,
    detections_csv,
    tracks_csv,
    metadata,
    analytics_config,
    run_analytics,
):
    assert run_name == "demo_run"
    assert Path(detections_csv).name == "detections.csv"
    assert Path(tracks_csv).name == "tracks.csv"
    assert metadata["video_id"] == "demo"
    assert metadata["input_video"] == "fake_video.mp4"
    assert metadata["tracker"] == "synthetic"
    assert analytics_config["line"]["id"] == "line_main"
    assert run_analytics is True
    return {
        "video_id": "demo",
        "run_name": run_name,
        "mode": "four_step_smoke_runner",
        "detection_count": 1,
        "track_row_count": 1,
        "track_count": 1,
        "artifact_paths": {},
    }
