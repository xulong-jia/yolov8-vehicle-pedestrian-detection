"""Tests for batch prediction path handling without loading YOLO."""

import importlib
import sys
from pathlib import Path

import pytest


def test_batch_predict_import_does_not_import_ultralytics():
    sys.modules.pop("src.batch_predict", None)
    sys.modules.pop("ultralytics", None)

    module = importlib.import_module("src.batch_predict")

    assert module.DEFAULT_OUTPUT_DIR == "local_outputs/batch_predictions"
    assert "ultralytics" not in sys.modules


@pytest.mark.parametrize("suffix", [".jpg", ".jpeg", ".png", ".bmp", ".webp"])
def test_supported_image_suffixes(tmp_path: Path, suffix: str):
    from src.batch_predict import is_image_file

    image_path = tmp_path / f"sample{suffix}"
    image_path.write_text("placeholder", encoding="utf-8")

    assert is_image_file(image_path)


@pytest.mark.parametrize("suffix", [".txt", ".csv", ".pt"])
def test_non_image_suffixes_are_not_images(tmp_path: Path, suffix: str):
    from src.batch_predict import is_image_file

    file_path = tmp_path / f"sample{suffix}"
    file_path.write_text("placeholder", encoding="utf-8")

    assert not is_image_file(file_path)


def test_collect_single_image_source(tmp_path: Path):
    from src.batch_predict import collect_image_paths

    image_path = tmp_path / "sample.jpg"
    image_path.write_text("placeholder", encoding="utf-8")

    assert collect_image_paths(image_path) == [image_path]


def test_collect_directory_source(tmp_path: Path):
    from src.batch_predict import collect_image_paths

    image_a = tmp_path / "a.jpg"
    image_b = tmp_path / "nested" / "b.png"
    non_image = tmp_path / "notes.txt"
    image_b.parent.mkdir()
    image_a.write_text("placeholder", encoding="utf-8")
    image_b.write_text("placeholder", encoding="utf-8")
    non_image.write_text("placeholder", encoding="utf-8")

    assert collect_image_paths(tmp_path) == [image_a, image_b]


def test_collect_empty_directory_returns_empty_list(tmp_path: Path):
    from src.batch_predict import collect_image_paths

    assert collect_image_paths(tmp_path) == []


def test_collect_non_image_file_raises_clear_error(tmp_path: Path):
    from src.batch_predict import collect_image_paths

    file_path = tmp_path / "sample.txt"
    file_path.write_text("placeholder", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported image file extension"):
        collect_image_paths(file_path)
