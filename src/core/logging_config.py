"""Structured logging helpers for the FastAPI service."""

from __future__ import annotations

from datetime import UTC, datetime
import json
import logging
from typing import Any


API_LOGGER_NAME = "yolov8.api"
JOB_LOGGER_NAME = "yolov8.video_jobs"


def get_api_logger() -> logging.Logger:
    return logging.getLogger(API_LOGGER_NAME)


def get_job_logger() -> logging.Logger:
    return logging.getLogger(JOB_LOGGER_NAME)


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    payload = {
        "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "event": event,
        **fields,
    }
    logger.info(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str))
