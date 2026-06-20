"""Lazy YOLO model loading for API inference."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class ModelLoader:
    """Cache one YOLO model instance and import ultralytics only on demand."""

    def __init__(self) -> None:
        self._model: Any | None = None
        self._model_path: str | None = None

    def load_model(self, model_path: str) -> Any:
        if self._model is not None and self._model_path == model_path:
            return self._model

        if not Path(model_path).is_file():
            raise FileNotFoundError(f"Model weight not found: {model_path}")

        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError(
                "ultralytics is required for /predict but is not installed"
            ) from exc

        self._model = YOLO(model_path)
        self._model_path = model_path
        return self._model

    def get_cached_model_path(self) -> str | None:
        return self._model_path

    def is_loaded(self) -> bool:
        return self._model is not None

    def clear(self) -> None:
        self._model = None
        self._model_path = None


model_loader = ModelLoader()
