"""Image decoding and YOLO inference service for FastAPI."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from PIL import Image, UnidentifiedImageError

from src.core.model_loader import model_loader


def decode_image_size(image_bytes: bytes) -> dict[str, int]:
    if not image_bytes:
        raise ValueError("Uploaded image is empty")

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image.load()
            return {"width": int(image.width), "height": int(image.height)}
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Unsupported or corrupted image") from exc


def _decode_image(image_bytes: bytes) -> Image.Image:
    if not image_bytes:
        raise ValueError("Uploaded image is empty")

    try:
        image = Image.open(BytesIO(image_bytes))
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Unsupported or corrupted image") from exc

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


def run_image_prediction(
    image_bytes: bytes,
    image_name: str,
    model_path: str,
    conf: float,
    imgsz: int,
    device: str,
    loader: Any = model_loader,
) -> dict[str, Any]:
    image = _decode_image(image_bytes)
    model = loader.load_model(model_path)

    results = model(
        image,
        imgsz=imgsz,
        conf=conf,
        device=device,
        verbose=False,
    )
    result = results[0] if results else None
    class_names = getattr(model, "names", None) or getattr(result, "names", {}) or {}
    detections = format_detections(result, class_names) if result is not None else []

    return {
        "image_name": image_name or "uploaded_image",
        "image_size": {"width": int(image.width), "height": int(image.height)},
        "model_path": model_path,
        "confidence_threshold": conf,
        "image_size_requested": imgsz,
        "device": device,
        "num_detections": len(detections),
        "detections": detections,
    }
