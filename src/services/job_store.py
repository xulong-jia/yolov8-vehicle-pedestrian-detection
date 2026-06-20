"""SQLite-backed metadata store for FastAPI video analysis jobs."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any


DEFAULT_VIDEO_JOB_DB_PATH = Path("local_outputs/api_video_jobs/video_jobs.sqlite3")


VIDEO_JOB_COLUMNS = [
    "job_id",
    "status",
    "video_id",
    "run_name",
    "run_dir",
    "output_dir",
    "summary_path",
    "artifact_paths_json",
    "error",
    "message",
    "created_at",
    "updated_at",
    "started_at",
    "finished_at",
    "model_path",
    "video_path",
    "conf",
    "imgsz",
    "device",
]


class SQLiteVideoJobStore:
    """Persist video job metadata without storing artifact contents."""

    def __init__(self, db_path: str | Path = DEFAULT_VIDEO_JOB_DB_PATH) -> None:
        self.db_path = Path(db_path)

    def upsert_job(self, job: dict[str, Any]) -> dict[str, Any]:
        normalized = _normalize_for_storage(job)
        self._ensure_schema()
        placeholders = ", ".join("?" for _ in VIDEO_JOB_COLUMNS)
        update_columns = [column for column in VIDEO_JOB_COLUMNS if column != "job_id"]
        update_clause = ", ".join(f"{column}=excluded.{column}" for column in update_columns)
        values = [_to_db_value(normalized.get(column), column) for column in VIDEO_JOB_COLUMNS]
        with self._connect() as connection:
            connection.execute(
                f"""
                INSERT INTO video_jobs ({", ".join(VIDEO_JOB_COLUMNS)})
                VALUES ({placeholders})
                ON CONFLICT(job_id) DO UPDATE SET {update_clause}
                """,
                values,
            )
        stored = dict(normalized)
        stored.pop("artifact_paths_json", None)
        return stored

    def get_job(self, job_id: str) -> dict[str, Any]:
        self._ensure_schema()
        with self._connect() as connection:
            row = connection.execute(
                f"SELECT {', '.join(VIDEO_JOB_COLUMNS)} FROM video_jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Video job not found: {job_id}")
        return _row_to_job(row)

    def clear(self) -> None:
        self._ensure_schema()
        with self._connect() as connection:
            connection.execute("DELETE FROM video_jobs")

    def _ensure_schema(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS video_jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    video_id TEXT NOT NULL,
                    run_name TEXT NOT NULL,
                    run_dir TEXT NOT NULL,
                    output_dir TEXT NOT NULL,
                    summary_path TEXT,
                    artifact_paths_json TEXT NOT NULL DEFAULT '{}',
                    error TEXT,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT,
                    model_path TEXT,
                    video_path TEXT,
                    conf REAL,
                    imgsz INTEGER,
                    device TEXT
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection


def _normalize_job(job: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(job)
    normalized.setdefault("output_dir", "")
    normalized.setdefault("summary_path", None)
    normalized.setdefault("artifact_paths", {})
    normalized.setdefault("error", None)
    normalized.setdefault("started_at", None)
    normalized.setdefault("finished_at", None)
    normalized.setdefault("model_path", "")
    normalized.setdefault("video_path", "")
    normalized.setdefault("conf", None)
    normalized.setdefault("imgsz", None)
    normalized.setdefault("device", "")
    normalized.setdefault("updated_at", normalized.get("created_at", ""))
    normalized["artifact_paths"] = _decode_artifact_paths(normalized.get("artifact_paths"))
    return normalized


def _to_db_value(value: Any, column: str) -> Any:
    if column == "artifact_paths_json":
        return value if isinstance(value, str) and value else "{}"
    if column in {"conf", "imgsz"} and value is None:
        return None
    if column == "conf" and value is not None:
        return float(value)
    if column == "imgsz" and value is not None:
        return int(value)
    if column in {"summary_path", "error", "started_at", "finished_at", "model_path", "video_path", "device"}:
        return None if value is None else str(value)
    return "" if value is None else value


def _row_to_job(row: sqlite3.Row) -> dict[str, Any]:
    job = {column: row[column] for column in VIDEO_JOB_COLUMNS}
    job["artifact_paths"] = _decode_artifact_paths(job.pop("artifact_paths_json"))
    return job


def _decode_artifact_paths(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {str(key): str(item) for key, item in value.items()}
    if not value:
        return {}
    try:
        data = json.loads(str(value))
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(key): str(item) for key, item in data.items()}


def artifact_paths_to_json(value: Any) -> str:
    return json.dumps(_decode_artifact_paths(value), ensure_ascii=False, sort_keys=True)


def _normalize_for_storage(job: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_job(job)
    normalized["artifact_paths_json"] = artifact_paths_to_json(normalized["artifact_paths"])
    return normalized
