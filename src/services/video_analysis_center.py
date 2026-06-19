"""Result directory helper for video analytics MVP artifacts."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.tracking.track_writer import (
    read_json,
    write_count_events_csv,
    write_events_jsonl,
    write_json,
    write_roi_frame_counts_csv,
    write_tracks_csv,
)


class VideoAnalysisCenter:
    """Manage a local result directory for one or more synthetic analysis runs."""

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)

    def create_run(self, run_name: str, metadata: dict[str, Any] | None = None) -> Path:
        run_dir = self.get_run_dir(run_name)
        run_dir.mkdir(parents=True, exist_ok=True)
        self.write_metadata(run_name, metadata or {})
        return run_dir

    def write_metadata(self, run_name: str, metadata: dict[str, Any]) -> Path:
        run_dir = self.get_run_dir(run_name)
        run_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "run_name": run_name,
            "created_at": _utc_now_iso(),
            "artifact_paths": {},
        }
        payload.update(metadata)
        payload.setdefault("artifact_paths", {})
        return write_json(payload, run_dir / "metadata.json")

    def write_tracks(self, run_name: str, track_rows: list[dict[str, Any]]) -> Path:
        return write_tracks_csv(track_rows, self.get_run_dir(run_name) / "tracks.csv")

    def write_count_events(self, run_name: str, count_events: list[dict[str, Any]]) -> Path:
        return write_count_events_csv(
            count_events,
            self.get_run_dir(run_name) / "count_events.csv",
        )

    def write_roi_counts(self, run_name: str, roi_frame_counts: list[dict[str, Any]]) -> Path:
        return write_roi_frame_counts_csv(
            roi_frame_counts,
            self.get_run_dir(run_name) / "roi_frame_counts.csv",
        )

    def write_events(self, run_name: str, events: list[dict[str, Any]]) -> Path:
        return write_events_jsonl(events, self.get_run_dir(run_name) / "events.jsonl")

    def write_summary(self, run_name: str, summary: dict[str, Any]) -> Path:
        return write_json(summary, self.get_run_dir(run_name) / "video_analysis_summary.json")

    def read_summary(self, run_name: str) -> dict[str, Any]:
        return read_json(self.get_run_dir(run_name) / "video_analysis_summary.json")

    def list_runs(self) -> list[str]:
        if not self.base_dir.exists():
            return []
        return sorted(path.name for path in self.base_dir.iterdir() if path.is_dir())

    def get_run_dir(self, run_name: str) -> Path:
        _validate_run_name(run_name)
        return self.base_dir / run_name


def _validate_run_name(run_name: str) -> None:
    if not run_name or "/" in run_name or "\\" in run_name or ".." in run_name:
        raise ValueError("run_name must be non-empty and must not contain path traversal")


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
