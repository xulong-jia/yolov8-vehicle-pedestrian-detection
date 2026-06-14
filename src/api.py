"""FastAPI service for local YOLOv8 image inference."""

from __future__ import annotations

from io import BytesIO
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError


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


def get_model_path(config: dict[str, Any] | None = None) -> str:
    """Return the effective model path without loading the model."""

    return get_effective_model_path(config)


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
    """Load and cache a YOLO model only when inference is requested."""

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


def load_image_from_bytes(data: bytes) -> Image.Image:
    """Decode uploaded image bytes into a RGB PIL image."""

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


def _to_scalar(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    return value


def _to_list(value: Any) -> list[Any]:
    if hasattr(value, "tolist"):
        result = value.tolist()
        return result if isinstance(result, list) else [result]
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, list):
        return value
    return [value]


def _class_name(class_names: dict[Any, str] | list[str] | tuple[str, ...], class_id: int) -> str:
    if isinstance(class_names, dict):
        return str(class_names.get(class_id, class_names.get(str(class_id), class_id)))
    if 0 <= class_id < len(class_names):
        return str(class_names[class_id])
    return str(class_id)


def format_detections(
    result: Any,
    class_names: dict[Any, str] | list[str] | tuple[str, ...],
) -> list[dict[str, Any]]:
    """Convert a YOLO result object into API response detections."""

    boxes = getattr(result, "boxes", None)
    if boxes is None:
        return []

    xyxy_values = _to_list(getattr(boxes, "xyxy", []))
    cls_values = _to_list(getattr(boxes, "cls", []))
    conf_values = _to_list(getattr(boxes, "conf", []))

    detections: list[dict[str, Any]] = []
    for xyxy, cls_value, conf_value in zip(xyxy_values, cls_values, conf_values):
        coords = _to_list(xyxy)
        if len(coords) < 4:
            continue

        class_id = int(_to_scalar(cls_value))
        detections.append(
            {
                "class_id": class_id,
                "class_name": _class_name(class_names, class_id),
                "confidence": float(_to_scalar(conf_value)),
                "bbox": {
                    "xmin": float(_to_scalar(coords[0])),
                    "ymin": float(_to_scalar(coords[1])),
                    "xmax": float(_to_scalar(coords[2])),
                    "ymax": float(_to_scalar(coords[3])),
                },
            }
        )

    return detections


def resolve_inference_options(
    config: dict[str, Any],
    conf: float | None,
    imgsz: int | None,
    device: str | None,
) -> tuple[float, int, str]:
    defaults = get_inference_config(config)
    confidence = float(defaults["confidence"] if conf is None else conf)
    image_size = int(defaults["image_size"] if imgsz is None else imgsz)
    inference_device = str(defaults["device"] if device is None else device)

    if not 0.0 <= confidence <= 1.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="conf must be between 0.0 and 1.0.",
        )
    if image_size <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="imgsz must be a positive integer.",
        )
    if not inference_device.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="device must not be empty.",
        )

    return confidence, image_size, inference_device


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
    async def predict(
        file: UploadFile = File(...),
        conf: float | None = None,
        imgsz: int | None = None,
        device: str | None = None,
    ) -> dict[str, Any]:
        config = load_config()
        confidence, image_size, inference_device = resolve_inference_options(
            config, conf, imgsz, device
        )
        model_path = get_model_path(config)
        if not Path(model_path).is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Model weight not found at {model_path}. Provide MODEL_PATH or "
                    f"place best.pt at {FALLBACK_MODEL_PATH}."
                ),
            )

        try:
            image = load_image_from_bytes(await file.read())
        finally:
            await file.close()

        try:
            model = get_or_load_model(model_path)
        except RuntimeError as exc:
            detail = short_error(exc)
            status_code = (
                status.HTTP_500_INTERNAL_SERVER_ERROR
                if "ultralytics is required" in detail
                else status.HTTP_400_BAD_REQUEST
            )
            raise HTTPException(status_code=status_code, detail=detail) from exc

        try:
            results = model(
                image,
                imgsz=image_size,
                conf=confidence,
                device=inference_device,
                verbose=False,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Inference failed: {short_error(exc)}",
            ) from exc

        result = results[0] if results else None
        class_names = getattr(model, "names", None) or getattr(result, "names", {}) or {}
        detections = format_detections(result, class_names) if result is not None else []

        return {
            "image_name": file.filename or "uploaded_image",
            "image_size": {"width": image.width, "height": image.height},
            "model_path": model_path,
            "confidence_threshold": confidence,
            "image_size_requested": image_size,
            "device": inference_device,
            "num_detections": len(detections),
            "detections": detections,
        }

    return app


app = create_app()
