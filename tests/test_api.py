"""Tests for the FastAPI inference service without running real YOLO."""

from __future__ import annotations

from io import BytesIO
import importlib
from pathlib import Path
import sys

from fastapi import HTTPException
from fastapi.testclient import TestClient
from PIL import Image
import pytest


def _png_bytes(size: tuple[int, int] = (8, 6)) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", size, color="white").save(buffer, format="PNG")
    return buffer.getvalue()


def test_api_import_does_not_import_ultralytics():
    sys.modules.pop("src.api", None)
    sys.modules.pop("ultralytics", None)

    module = importlib.import_module("src.api")

    assert module.app is not None
    assert module.model_loader.is_loaded() is False
    assert "ultralytics" not in sys.modules


def test_health_config_and_model_status_do_not_load_model(monkeypatch, tmp_path):
    from src import api

    calls = []

    def fail_load_model(model_path):
        calls.append(model_path)
        raise AssertionError("load_model should not be called")

    missing_model = tmp_path / "missing.pt"
    monkeypatch.setenv("MODEL_PATH", str(missing_model))
    monkeypatch.setattr(api.model_loader, "load_model", fail_load_model)
    monkeypatch.setattr(api.model_loader, "is_loaded", lambda: False)
    monkeypatch.setattr(api.model_loader, "get_cached_model_path", lambda: None)
    client = TestClient(api.create_app())

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "service": api.SERVICE_NAME}

    config = client.get("/config")
    assert config.status_code == 200
    config_json = config.json()
    assert config_json["project_name"]
    assert config_json["model_path"] == str(missing_model)
    assert config_json["device"] == "cpu"
    assert config_json["confidence_threshold"] == 0.25
    assert config_json["image_size"] == 640

    model_status = client.get("/model-status")
    assert model_status.status_code == 200
    assert model_status.json()["exists"] is False
    assert model_status.json()["loaded"] is False
    assert calls == []


def test_load_image_from_valid_bytes():
    from src.api import load_image_from_bytes

    image = load_image_from_bytes(_png_bytes())

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

    detections = format_detections(
        FakeResult(), ["Bus", "Car", "Motorcycle", "Person", "Truck"]
    )

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


def test_predict_rejects_unsupported_extension():
    from src.api import create_app

    client = TestClient(create_app())

    response = client.post(
        "/predict",
        files={"file": ("sample.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert "Unsupported image type" in response.json()["detail"]


def test_predict_rejects_empty_image():
    from src.api import create_app

    client = TestClient(create_app())

    response = client.post(
        "/predict",
        files={"file": ("sample.jpg", b"", "image/jpeg")},
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_predict_success_uses_service_once(monkeypatch, tmp_path):
    from src import api

    calls = []
    output_dir = tmp_path / "outputs"

    def fake_run_image_prediction(**kwargs):
        calls.append(kwargs)
        return {
            "image_name": kwargs["image_name"],
            "image_size": {"width": 8, "height": 6},
            "model_path": kwargs["model_path"],
            "confidence_threshold": kwargs["conf"],
            "image_size_requested": kwargs["imgsz"],
            "device": kwargs["device"],
            "num_detections": 1,
            "detections": [
                {
                    "class_id": 1,
                    "class_name": "Car",
                    "confidence": 0.88,
                    "bbox": {"xmin": 1.0, "ymin": 2.0, "xmax": 3.0, "ymax": 4.0},
                }
            ],
        }

    monkeypatch.setattr(
        api.image_inference_service, "run_image_prediction", fake_run_image_prediction
    )
    client = TestClient(api.create_app())

    response = client.post(
        "/predict?model_path=/tmp/fake.pt&conf=0.4&imgsz=320&device=cpu",
        files={"file": ("sample.png", _png_bytes(), "image/png")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["num_detections"] == 1
    assert body["detections"][0]["class_name"] == "Car"
    assert body["detections"][0]["bbox"]["xmax"] == 3.0
    assert calls[0]["model_path"] == "/tmp/fake.pt"
    assert calls[0]["conf"] == 0.4
    assert calls[0]["imgsz"] == 320
    assert calls[0]["device"] == "cpu"
    assert not output_dir.exists()


def test_predict_no_detections(monkeypatch):
    from src import api

    def fake_run_image_prediction(**kwargs):
        return {
            "image_name": kwargs["image_name"],
            "image_size": {"width": 8, "height": 6},
            "model_path": kwargs["model_path"],
            "confidence_threshold": kwargs["conf"],
            "image_size_requested": kwargs["imgsz"],
            "device": kwargs["device"],
            "num_detections": 0,
            "detections": [],
        }

    monkeypatch.setattr(
        api.image_inference_service, "run_image_prediction", fake_run_image_prediction
    )
    client = TestClient(api.create_app())

    response = client.post(
        "/predict",
        files={"file": ("sample.png", _png_bytes(), "image/png")},
    )

    assert response.status_code == 200
    assert response.json()["num_detections"] == 0
    assert response.json()["detections"] == []


def test_predict_missing_model_returns_404(monkeypatch):
    from src import api

    def fake_run_image_prediction(**kwargs):
        raise FileNotFoundError(f"Model weight not found: {kwargs['model_path']}")

    monkeypatch.setattr(
        api.image_inference_service, "run_image_prediction", fake_run_image_prediction
    )
    client = TestClient(api.create_app())

    response = client.post(
        "/predict?model_path=missing/model.pt",
        files={"file": ("sample.png", _png_bytes(), "image/png")},
    )

    assert response.status_code == 404
    assert "Model weight not found" in response.json()["detail"]


def test_model_loader_lazy_import(monkeypatch, tmp_path):
    from src.core.model_loader import ModelLoader

    model_path = tmp_path / "best.pt"
    model_path.write_bytes(b"fake")

    class FakeYOLO:
        def __init__(self, path):
            self.path = path

    class FakeUltralytics:
        YOLO = FakeYOLO

    sys.modules.pop("ultralytics", None)
    monkeypatch.setitem(sys.modules, "ultralytics", FakeUltralytics)

    loader = ModelLoader()
    model = loader.load_model(str(model_path))

    assert isinstance(model, FakeYOLO)
    assert loader.is_loaded() is True
    assert loader.get_cached_model_path() == str(model_path)
    assert loader.load_model(str(model_path)) is model


def test_source_keeps_yolo_import_lazy():
    api_source = Path("src/api.py").read_text(encoding="utf-8")
    loader_source = Path("src/core/model_loader.py").read_text(encoding="utf-8")

    assert "from ultralytics import YOLO" not in api_source
    assert "from ultralytics import YOLO" in loader_source
    assert "def load_model" in loader_source
