"""FastAPI service for YOLOv8 image inference."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, status

from src.core.config import (
    PROJECT_NAME,
    SUPPORTED_IMAGE_TYPES,
    get_default_config,
)
from src.core.model_loader import model_loader
from src.core.schemas import (
    ConfigResponse,
    HealthResponse,
    ModelStatusResponse,
    PredictResponse,
)
from src.services import image_inference_service
from src.services.image_inference_service import decode_image_size, format_detections


SERVICE_NAME = "yolov8-vehicle-pedestrian-api"


def short_error(exc: Exception, max_length: int = 180) -> str:
    message = str(exc).strip() or exc.__class__.__name__
    return message if len(message) <= max_length else f"{message[:max_length]}..."


def load_image_from_bytes(data: bytes) -> Any:
    """Compatibility helper for tests: validate bytes and return a PIL image."""

    from io import BytesIO

    from PIL import Image, UnidentifiedImageError

    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image is empty.",
        )
    try:
        image = Image.open(BytesIO(data))
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported or corrupted image.",
        ) from exc
    return image.convert("RGB")


def _is_supported_image(filename: str | None) -> bool:
    suffix = Path(filename or "").suffix.lower().lstrip(".")
    return bool(suffix) and suffix in SUPPORTED_IMAGE_TYPES


def _validate_runtime_options(conf: float, imgsz: int, device: str) -> None:
    if not 0.0 <= conf <= 1.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="conf must be between 0.0 and 1.0",
        )
    if imgsz <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="imgsz must be a positive integer",
        )
    if not device.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="device must not be empty",
        )


def _http_error_for_prediction(exc: Exception) -> HTTPException:
    if isinstance(exc, FileNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=short_error(exc))
    if isinstance(exc, ValueError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=short_error(exc))
    if isinstance(exc, RuntimeError):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=short_error(exc),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Inference failed: {short_error(exc)}",
    )


def create_app() -> FastAPI:
    app = FastAPI(title=PROJECT_NAME)

    @app.get("/health", response_model=HealthResponse)
    def health() -> dict[str, str]:
        return {"status": "ok", "service": SERVICE_NAME}

    @app.get("/config", response_model=ConfigResponse)
    def config() -> dict[str, Any]:
        return get_default_config()

    @app.get("/model-status", response_model=ModelStatusResponse)
    def model_status() -> dict[str, Any]:
        config_data = get_default_config()
        model_path = str(config_data["model_path"])
        return {
            "model_path": model_path,
            "exists": Path(model_path).is_file(),
            "loaded": model_loader.is_loaded()
            and model_loader.get_cached_model_path() == model_path,
            "device": str(config_data["device"]),
            "confidence_threshold": float(config_data["confidence_threshold"]),
            "image_size": int(config_data["image_size"]),
        }

    @app.post("/predict", response_model=PredictResponse)
    async def predict(
        file: UploadFile = File(...),
        model_path: str | None = Query(default=None),
        conf: float | None = Query(default=None),
        imgsz: int | None = Query(default=None),
        device: str | None = Query(default=None),
    ) -> dict[str, Any]:
        if not _is_supported_image(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported image type",
            )

        try:
            image_bytes = await file.read()
        finally:
            await file.close()

        if not image_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded image is empty",
            )

        try:
            decode_image_size(image_bytes)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=short_error(exc),
            ) from exc

        config_data = get_default_config()
        effective_model_path = model_path or str(config_data["model_path"])
        effective_conf = float(
            config_data["confidence_threshold"] if conf is None else conf
        )
        effective_imgsz = int(config_data["image_size"] if imgsz is None else imgsz)
        effective_device = str(config_data["device"] if device is None else device)
        _validate_runtime_options(effective_conf, effective_imgsz, effective_device)

        try:
            return image_inference_service.run_image_prediction(
                image_bytes=image_bytes,
                image_name=file.filename or "uploaded_image",
                model_path=effective_model_path,
                conf=effective_conf,
                imgsz=effective_imgsz,
                device=effective_device,
            )
        except Exception as exc:
            raise _http_error_for_prediction(exc) from exc

    return app


app = create_app()
