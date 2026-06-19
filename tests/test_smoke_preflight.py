import json

import pytest

from src import smoke_preflight
from src.smoke_preflight import (
    build_smoke_commands,
    check_file_path,
    check_optional_module,
    check_output_dir,
    main,
    parse_args,
    run_preflight,
)


def test_check_file_path_requires_existing_file(tmp_path):
    model_path = tmp_path / "best.pt"
    model_path.write_text("fake weights", encoding="utf-8")
    directory = tmp_path / "directory"
    directory.mkdir()

    assert check_file_path(model_path, "model") == model_path
    with pytest.raises(FileNotFoundError):
        check_file_path(tmp_path / "missing.pt", "model")
    with pytest.raises(ValueError):
        check_file_path(directory, "model")


def test_check_output_dir_does_not_create_directory(tmp_path):
    output_dir = tmp_path / "smoke"
    existing_dir = tmp_path / "existing"
    existing_dir.mkdir()
    existing_file = tmp_path / "file.txt"
    existing_file.write_text("not a dir", encoding="utf-8")

    assert check_output_dir(output_dir) == output_dir
    assert not output_dir.exists()
    assert check_output_dir(existing_dir) == existing_dir
    with pytest.raises(ValueError):
        check_output_dir(existing_file)


def test_check_output_dir_requires_existing_parent(tmp_path):
    output_dir = tmp_path / "missing_parent" / "smoke"

    with pytest.raises(FileNotFoundError):
        check_output_dir(output_dir)
    assert not output_dir.exists()


def test_check_optional_module_uses_find_spec_without_import(monkeypatch):
    def fake_find_spec(name):
        return object() if name in {"ultralytics", "cv2"} else None

    monkeypatch.setattr(smoke_preflight.importlib.util, "find_spec", fake_find_spec)

    assert check_optional_module("ultralytics") == {
        "name": "ultralytics",
        "available": True,
    }
    assert check_optional_module("cv2") == {"name": "cv2", "available": True}
    assert check_optional_module("missing") == {"name": "missing", "available": False}


def test_build_smoke_commands_quotes_paths_and_outputs_under_output_dir(tmp_path):
    commands = build_smoke_commands(
        model_path=tmp_path / "best model.pt",
        video_path=tmp_path / "source video.mp4",
        output_dir=tmp_path / "smoke output",
        video_id="demo",
        run_name="demo_run",
        conf=0.25,
        imgsz=640,
        device="cpu",
    )

    assert set(commands) == {
        "predict_video_csv",
        "track_video_synthetic",
        "four_step_runner",
    }
    assert "src/predict_video.py" in commands["predict_video_csv"]
    assert "src/track_video.py" in commands["track_video_synthetic"]
    assert "src/run_video_analysis_smoke.py" in commands["four_step_runner"]
    for command in (commands["predict_video_csv"], commands["four_step_runner"]):
        assert "best model.pt" in command
        assert "source video.mp4" in command
    for command in commands.values():
        assert "smoke output" in command
    for command in (commands["predict_video_csv"], commands["four_step_runner"]):
        assert "--video-id demo" in command
        assert "--conf 0.25" in command
        assert "--imgsz 640" in command
        assert "--device cpu" in command
    assert "detections.csv" in commands["predict_video_csv"]
    assert "tracking" in commands["track_video_synthetic"]
    assert "--run-name demo_run" in commands["four_step_runner"]


def test_run_preflight_success_does_not_create_outputs(tmp_path, monkeypatch):
    model_path, video_path, output_dir = _make_inputs(tmp_path)
    _fake_modules(monkeypatch, available={"ultralytics", "cv2"})

    result = run_preflight(model_path, video_path, output_dir)

    assert result["ok"] is True
    assert result["model_path"] == str(model_path)
    assert result["video_path"] == str(video_path)
    assert result["output_dir"] == str(output_dir)
    assert result["checks"]["model_path"]["ok"] is True
    assert result["checks"]["video_path"]["ok"] is True
    assert result["checks"]["output_dir"]["ok"] is True
    assert result["checks"]["ultralytics"]["available"] is True
    assert result["checks"]["cv2"]["available"] is True
    assert set(result["commands"]) == {
        "predict_video_csv",
        "track_video_synthetic",
        "four_step_runner",
    }
    _assert_no_outputs_created(tmp_path, output_dir)


def test_run_preflight_missing_modules_returns_not_ok_with_commands(tmp_path, monkeypatch):
    model_path, video_path, output_dir = _make_inputs(tmp_path)
    _fake_modules(monkeypatch, available={"cv2"})

    result = run_preflight(model_path, video_path, output_dir)

    assert result["ok"] is False
    assert result["checks"]["ultralytics"]["available"] is False
    assert result["checks"]["cv2"]["available"] is True
    assert result["commands"]["predict_video_csv"]
    _assert_no_outputs_created(tmp_path, output_dir)


def test_parse_args_defaults_and_required_arguments():
    args = parse_args(
        [
            "--model",
            "best.pt",
            "--video",
            "video.mp4",
            "--output-dir",
            "/tmp/smoke",
        ]
    )

    assert args.model == "best.pt"
    assert args.video == "video.mp4"
    assert str(args.output_dir) == "/tmp/smoke"
    assert args.video_id == "demo"
    assert args.run_name == "demo_run"
    assert args.conf == 0.25
    assert args.imgsz == 640
    assert args.device == "cpu"
    with pytest.raises(SystemExit):
        parse_args([])


def test_main_prints_json_and_returns_status(tmp_path, monkeypatch, capsys):
    model_path, video_path, output_dir = _make_inputs(tmp_path)
    _fake_modules(monkeypatch, available={"ultralytics", "cv2"})

    exit_code = main(
        [
            "--model",
            str(model_path),
            "--video",
            str(video_path),
            "--output-dir",
            str(output_dir),
        ]
    )
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert result["ok"] is True
    _assert_no_outputs_created(tmp_path, output_dir)

    _fake_modules(monkeypatch, available={"cv2"})
    exit_code = main(
        [
            "--model",
            str(model_path),
            "--video",
            str(video_path),
            "--output-dir",
            str(output_dir),
        ]
    )
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert result["ok"] is False
    assert result["checks"]["ultralytics"]["available"] is False
    _assert_no_outputs_created(tmp_path, output_dir)


def _make_inputs(tmp_path):
    model_path = tmp_path / "best.pt"
    video_path = tmp_path / "video.mp4"
    output_dir = tmp_path / "smoke"
    model_path.write_text("fake weights", encoding="utf-8")
    video_path.write_text("fake video", encoding="utf-8")
    return model_path, video_path, output_dir


def _fake_modules(monkeypatch, available):
    monkeypatch.setattr(
        smoke_preflight.importlib.util,
        "find_spec",
        lambda name: object() if name in available else None,
    )


def _assert_no_outputs_created(tmp_path, output_dir):
    assert not output_dir.exists()
    assert not (tmp_path / "detections.csv").exists()
    assert not (tmp_path / "tracks.csv").exists()
    assert not (tmp_path / "video_analysis").exists()
    assert not (tmp_path / "frame_index.csv").exists()
    assert not (tmp_path / "metadata.json").exists()
    assert not (tmp_path / "local_outputs").exists()
    assert not (tmp_path / "results").exists()
    assert not (tmp_path / "runs").exists()
