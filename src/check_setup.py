"""Check local project setup without training, inference, or file generation."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = "configs/default.yaml"
DEFAULTS = {
    "paths": {
        "dataset_yaml": "dataset/data.yaml",
        "default_model": "local_weights/yolov8n_640_50epochs/best.pt",
        "sample_images_dir": "docs/error_case_gallery/images",
    }
}
RISK_SUFFIXES = (".pt", ".pth", ".onnx", ".mp4", ".avi", ".mov", ".mkv")
RISK_PREFIXES = (
    "local_weights/",
    "local_videos/source/",
    "dataset/train/",
    "dataset/valid/",
    "dataset/test/",
    "runs/",
    ".venv/",
)
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check local project setup.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Path to YAML config.")
    parser.add_argument("--model", help="Override default model path.")
    parser.add_argument("--dataset-yaml", help="Override dataset YAML path.")
    parser.add_argument("--samples-dir", help="Override sample images directory.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if key files or paths are missing.",
    )
    return parser.parse_args()


def load_config(config_path: Path) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    if not config_path.is_file():
        warnings.append(f"Config file not found: {config_path}. Using built-in defaults.")
        return DEFAULTS, warnings

    try:
        import yaml
    except ImportError:
        warnings.append(
            "PyYAML is not installed, so the config file was not parsed. "
            "Install dependencies with `pip install -r requirements.txt` or use CLI overrides."
        )
        return DEFAULTS, warnings

    try:
        with config_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
    except Exception as exc:
        warnings.append(f"Could not parse config file {config_path}: {short_error(exc)}")
        return DEFAULTS, warnings

    return data, warnings


def short_error(exc: Exception, max_length: int = 180) -> str:
    message = str(exc).strip() or exc.__class__.__name__
    return message if len(message) <= max_length else f"{message[:max_length]}..."


def get_nested(config: dict[str, Any], section: str, key: str, default: str) -> str:
    value = config.get(section, {})
    if isinstance(value, dict):
        return str(value.get(key, default))
    return default


def print_item(status: str, message: str) -> None:
    print(f"[{status}] {message}")


def git_tracked_risk_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print_item("WARNING", f"Could not run git ls-files: {short_error(exc)}")
        return []

    risk_files = []
    for line in result.stdout.splitlines():
        if line.endswith(RISK_SUFFIXES) or line.startswith(RISK_PREFIXES):
            risk_files.append(line)
    return risk_files


def count_sample_images(samples_dir: Path) -> int:
    return sum(
        1
        for path in samples_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def main() -> int:
    args = parse_args()
    config, config_warnings = load_config(Path(args.config))

    dataset_yaml = Path(
        args.dataset_yaml
        or get_nested(config, "paths", "dataset_yaml", DEFAULTS["paths"]["dataset_yaml"])
    )
    model_path = Path(
        args.model
        or get_nested(config, "paths", "default_model", DEFAULTS["paths"]["default_model"])
    )
    samples_dir = Path(
        args.samples_dir
        or get_nested(
            config,
            "paths",
            "sample_images_dir",
            DEFAULTS["paths"]["sample_images_dir"],
        )
    )

    warnings: list[str] = list(config_warnings)
    errors: list[str] = []

    root_markers = ["README.md", "dataset/data.yaml", "app.py"]
    missing_root_markers = [marker for marker in root_markers if not Path(marker).exists()]
    if missing_root_markers:
        errors.append(
            "Current directory does not look like the project root. "
            f"Missing: {', '.join(missing_root_markers)}"
        )
    else:
        print_item("OK", "Current directory looks like the project root.")

    if dataset_yaml.is_file():
        print_item("OK", f"Dataset YAML found: {dataset_yaml}")
    else:
        errors.append(f"Dataset YAML not found: {dataset_yaml}")

    if model_path.is_file():
        print_item("OK", f"Model weight found: {model_path}")
    else:
        message = (
            f"Model weight not found: {model_path}. This is expected on machines "
            "without local weights, but inference will not run until the weight is present."
        )
        if args.strict:
            errors.append(message)
        else:
            warnings.append(message)

    if samples_dir.is_dir():
        print_item("OK", f"Sample images directory found: {samples_dir}")
        print_item("OK", f"Sample image count: {count_sample_images(samples_dir)}")
    else:
        message = f"Sample images directory not found: {samples_dir}"
        if args.strict:
            errors.append(message)
        else:
            warnings.append(message)

    risk_files = git_tracked_risk_files()
    if risk_files:
        errors.append("Risk files are tracked by Git:\n  " + "\n  ".join(risk_files))
    else:
        print_item("OK", "No tracked risk files found.")

    for warning in warnings:
        print_item("WARNING", warning)
    for error in errors:
        print_item("ERROR", error)

    if errors:
        print_item("ERROR", "Final status: setup check failed.")
        return 1

    print_item("OK", "Final status: setup check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
