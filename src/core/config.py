"""Configuration helpers for the FastAPI service.

The API layer intentionally reads simple environment-backed defaults here
without validating model files or importing YOLO.
"""

from __future__ import annotations

import os
from typing import Any


PROJECT_NAME = "YOLOv8 Vehicle and Pedestrian Detection System"
DEFAULT_MODEL_PATH = "local_weights/yolov8s_640_50epochs/best.pt"
DEFAULT_DEVICE = "cpu"
DEFAULT_CONFIDENCE_THRESHOLD = 0.25
DEFAULT_IMAGE_SIZE = 640
SUPPORTED_IMAGE_TYPES = ["jpg", "jpeg", "png", "bmp", "webp"]


def get_model_path() -> str:
    return os.environ.get("MODEL_PATH", DEFAULT_MODEL_PATH)


def get_device() -> str:
    return os.environ.get("YOLO_DEVICE", DEFAULT_DEVICE)


def get_confidence_threshold() -> float:
    value = os.environ.get("YOLO_CONF")
    if value is None:
        return DEFAULT_CONFIDENCE_THRESHOLD
    try:
        return float(value)
    except ValueError:
        return DEFAULT_CONFIDENCE_THRESHOLD


def get_image_size() -> int:
    value = os.environ.get("YOLO_IMGSZ")
    if value is None:
        return DEFAULT_IMAGE_SIZE
    try:
        return int(value)
    except ValueError:
        return DEFAULT_IMAGE_SIZE


def get_default_config() -> dict[str, Any]:
    return {
        "project_name": PROJECT_NAME,
        "model_path": get_model_path(),
        "device": get_device(),
        "confidence_threshold": get_confidence_threshold(),
        "image_size": get_image_size(),
        "supported_image_types": list(SUPPORTED_IMAGE_TYPES),
    }
