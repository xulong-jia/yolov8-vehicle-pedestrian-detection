"""Pydantic response schemas for the FastAPI service."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


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


class BadCaseRequest(BaseModel):
    module: str
    case_type: str
    video_id: str = ""
    image_name: str = ""
    frame_index: int | str | None = ""
    timestamp_sec: float | str | None = ""
    track_id: int | str | None = ""
    expected_result: str
    actual_result: str
    root_cause: str
    tags: list[str] | str = Field(default_factory=list)
    snapshot_path: str = ""
    added_to_eval_set: bool = False


class BadCaseResponse(BaseModel):
    case_id: str
    module: str
    case_type: str
    video_id: str
    image_name: str
    frame_index: str
    timestamp_sec: str
    track_id: str
    expected_result: str
    actual_result: str
    root_cause: str
    tags: str
    snapshot_path: str
    added_to_eval_set: str
    created_at: str


class VideoAnalyzeRequest(BaseModel):
    video_id: str = "demo"
    run_name: str | None = None
    run_dir: str | None = None
    model_path: str | None = None
    source: str | None = None
    video_path: str | None = None
    conf: float = 0.25
    imgsz: int = 640
    device: str = "cpu"
    note: str | None = None


class VideoJobResponse(BaseModel):
    job_id: str
    status: str
    video_id: str
    run_name: str
    run_dir: str
    message: str
    output_dir: str | None = None
    summary_path: str | None = None
    artifact_paths: dict[str, str] | None = None
    error: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    model_path: str | None = None
    video_path: str | None = None
    conf: float | None = None
    imgsz: int | None = None
    device: str | None = None


class VideoArtifactResponse(BaseModel):
    job_id: str
    artifact_type: str
    exists: bool
    path: str
    data: Any
    row_count: int | None = None
