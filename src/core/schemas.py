"""Pydantic response schemas for the FastAPI service."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class ConfigResponse(BaseModel):
    project_name: str
    model_path: str
    device: str
    confidence_threshold: float
    image_size: int
    supported_image_types: list[str]


class ModelStatusResponse(BaseModel):
    model_path: str
    exists: bool
    loaded: bool
    device: str
    confidence_threshold: float
    image_size: int


class BoundingBox(BaseModel):
    xmin: float
    ymin: float
    xmax: float
    ymax: float


class DetectionResult(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox


class PredictResponse(BaseModel):
    image_name: str
    image_size: dict[str, int]
    model_path: str
    confidence_threshold: float
    image_size_requested: int
    device: str
    num_detections: int
    detections: list[DetectionResult]


class ErrorResponse(BaseModel):
    detail: str | dict[str, Any]
