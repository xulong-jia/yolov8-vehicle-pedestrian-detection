"""FastAPI scaffold for future YOLOv8 inference service."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, status


SERVICE_NAME = "yolov8-vehicle-pedestrian-api"
DEFAULT_CONFIG_PATH = Path("configs/default.yaml")
FALLBACK_MODEL_PATH = "local_weights/yolov8n_640_50epochs/best.pt"
FALLBACK_IMAGE_SIZE = 640
FALLBACK_CONFIDENCE = 0.25
FALLBACK_DEVICE = "cpu"

_model: Any | None = None
_model_path: str | None = None


def short_error(exc: Exception, max_length: int = 180) -> str:
    message = str(exc).strip() or exc.__class__.__name__
    return message if len(message) <= max_length else f"{message[:max_length]}..."


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    if not config_path.is_file():
        return {}

    try:
        import yaml
    except ImportError:
        return {}

    try:
        with config_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
    except Exception:
        return {}

    return data if isinstance(data, dict) else {}


def get_config_value(
    config: dict[str, Any],
    section: str,
    key: str,
    fallback: Any,
) -> Any:
    section_value = config.get(section, {})
    if isinstance(section_value, dict):
        return section_value.get(key, fallback)
    return fallback


def get_default_model_path(config: dict[str, Any] | None = None) -> str:
    config = config if config is not None else load_config()
    return str(get_config_value(config, "paths", "default_model", FALLBACK_MODEL_PATH))


def get_effective_model_path(config: dict[str, Any] | None = None) -> str:
    return os.environ.get("MODEL_PATH") or get_default_model_path(config)


def get_inference_config(config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config if config is not None else load_config()
    return {
        "default_model_path": get_default_model_path(config),
        "model_path_env": os.environ.get("MODEL_PATH", ""),
        "image_size": int(
            get_config_value(config, "inference", "image_size", FALLBACK_IMAGE_SIZE)
        ),
        "confidence": float(
            get_config_value(config, "inference", "confidence", FALLBACK_CONFIDENCE)
        ),
        "device": str(get_config_value(config, "inference", "device", FALLBACK_DEVICE)),
    }


def get_or_load_model(model_path: str) -> Any:
    """Lazy model loader reserved for a future real inference endpoint."""

    global _model, _model_path
    if _model is not None and _model_path == model_path:
        return _model

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise RuntimeError(
            "ultralytics is required for real inference but is not available"
        ) from exc

    try:
        _model = YOLO(model_path)
    except Exception as exc:
        raise RuntimeError(f"model loading failed: {short_error(exc)}") from exc

    _model_path = model_path
    return _model


def create_app() -> FastAPI:
    app = FastAPI(title=SERVICE_NAME)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": SERVICE_NAME}

    @app.get("/config")
    def config() -> dict[str, Any]:
        return get_inference_config()

    @app.get("/model-status")
    def model_status() -> dict[str, Any]:
        model_path = get_effective_model_path()
        return {
            "model_path": model_path,
            "exists": Path(model_path).is_file(),
            "loaded": _model is not None and _model_path == model_path,
        }

    @app.post("/predict")
    def predict() -> None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=(
                "Prediction endpoint scaffolded but real inference is intentionally "
                "disabled in this version."
            ),
        )

    return app


app = create_app()
