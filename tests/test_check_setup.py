"""Tests for setup-check helper functions."""

import importlib


def test_check_setup_importable():
    module = importlib.import_module("src.check_setup")
    assert module.DEFAULT_CONFIG == "configs/default.yaml"


def test_risk_paths_are_detected():
    from src.check_setup import is_risk_path

    risk_paths = [
        "local_weights/model.pt",
        "runs/detect/result.jpg",
        "dataset/train/images/a.jpg",
        "local_videos/source/demo.mp4",
    ]

    for path in risk_paths:
        assert is_risk_path(path), path


def test_safe_paths_are_not_detected_as_risk():
    from src.check_setup import is_risk_path

    safe_paths = [
        "docs/model_card.md",
        "app.py",
        "src/train.py",
    ]

    for path in safe_paths:
        assert not is_risk_path(path), path
