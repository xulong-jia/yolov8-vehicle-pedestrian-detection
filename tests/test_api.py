"""Tests for FastAPI inference helpers without running YOLO inference."""

from io import BytesIO
import importlib
import sys

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from PIL import Image


def test_api_import_does_not_import_ultralytics():
    sys.modules.pop("src.api", None)
    sys.modules.pop("ultralytics", None)

    module = importlib.import_module("src.api")

    assert module.SERVICE_NAME == "yolov8-vehicle-pedestrian-api"
    assert "ultralytics" not in sys.modules


def test_create_app_and_basic_endpoints(monkeypatch):
    from src.api import create_app

    monkeypatch.setenv("MODEL_PATH", "missing/model.pt")
    client = TestClient(create_app())

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    config = client.get("/config")
    assert config.status_code == 200
    assert config.json()["image_size"] == 640

    model_status = client.get("/model-status")
    assert model_status.status_code == 200
    assert model_status.json()["exists"] is False
    assert model_status.json()["loaded"] is False


def test_load_image_from_valid_bytes():
    from src.api import load_image_from_bytes

    buffer = BytesIO()
    Image.new("RGB", (8, 6), color="white").save(buffer, format="JPEG")

    image = load_image_from_bytes(buffer.getvalue())

    assert image.mode == "RGB"
    assert image.size == (8, 6)


def test_load_image_from_invalid_bytes_raises_http_exception():
    from src.api import load_image_from_bytes

    with pytest.raises(HTTPException) as exc_info:
        load_image_from_bytes(b"not-an-image")

    assert exc_info.value.status_code == 400
    assert "Unsupported or corrupted image" in exc_info.value.detail


def test_format_detections_with_fake_result():
    from src.api import format_detections

    class FakeBoxes:
        xyxy = [[1, 2, 3, 4], [10, 20, 30, 40]]
        cls = [1, 4]
        conf = [0.9, 0.75]

    class FakeResult:
        boxes = FakeBoxes()

    detections = format_detections(FakeResult(), ["Bus", "Car", "Motorcycle", "Person", "Truck"])

    assert detections == [
        {
            "class_id": 1,
            "class_name": "Car",
            "confidence": 0.9,
            "bbox": {"xmin": 1.0, "ymin": 2.0, "xmax": 3.0, "ymax": 4.0},
        },
        {
            "class_id": 4,
            "class_name": "Truck",
            "confidence": 0.75,
            "bbox": {"xmin": 10.0, "ymin": 20.0, "xmax": 30.0, "ymax": 40.0},
        },
    ]


def test_predict_missing_model_returns_404_without_ultralytics(monkeypatch):
    from src.api import create_app

    sys.modules.pop("ultralytics", None)
    monkeypatch.setenv("MODEL_PATH", "missing/model.pt")
    client = TestClient(create_app())

    buffer = BytesIO()
    Image.new("RGB", (4, 4), color="white").save(buffer, format="PNG")

    response = client.post(
        "/predict?conf=0.25&imgsz=640&device=cpu",
        files={"file": ("sample.png", buffer.getvalue(), "image/png")},
    )

    assert response.status_code == 404
    assert "Model weight not found" in response.json()["detail"]
    assert "ultralytics" not in sys.modules
