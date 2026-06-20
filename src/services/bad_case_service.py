"""Bad Case metadata collection service.

The service stores lightweight review metadata only. It does not copy snapshots,
videos, model weights, or generated artifacts into the repository.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4


DEFAULT_BAD_CASE_CSV_PATH = Path("local_outputs/bad_cases/bad_cases.csv")
DEFAULT_BAD_CASE_JSONL_PATH = Path("local_outputs/bad_cases/bad_cases.jsonl")

BAD_CASE_FIELDS = [
    "case_id",
    "module",
    "case_type",
    "video_id",
    "image_name",
    "frame_index",
    "timestamp_sec",
    "track_id",
    "expected_result",
    "actual_result",
    "root_cause",
    "tags",
    "snapshot_path",
    "added_to_eval_set",
    "created_at",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(slots=True)
class BadCaseRecord:
    """Serializable Bad Case metadata record."""

    module: str
    case_type: str
    expected_result: str
    actual_result: str
    root_cause: str
    case_id: str = ""
    video_id: str = ""
    image_name: str = ""
    frame_index: int | str | None = ""
    timestamp_sec: float | str | None = ""
    track_id: int | str | None = ""
    tags: list[str] | str = field(default_factory=list)
    snapshot_path: str = ""
    added_to_eval_set: bool | str = False
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.case_id:
            self.case_id = f"BC-{uuid4().hex[:8]}"
        if not self.created_at:
            self.created_at = utc_now_iso()

    def to_dict(self) -> dict[str, str]:
        tags = self.tags
        if isinstance(tags, list):
            tags_value = ",".join(str(tag) for tag in tags if str(tag).strip())
        else:
            tags_value = str(tags)

        added = self.added_to_eval_set
        if isinstance(added, bool):
            added_value = "yes" if added else "no"
        else:
            added_value = str(added).strip().lower() or "no"

        data = asdict(self)
        data["tags"] = tags_value
        data["added_to_eval_set"] = added_value
        return {field_name: _stringify(data.get(field_name, "")) for field_name in BAD_CASE_FIELDS}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BadCaseRecord":
        return cls(
            case_id=str(data.get("case_id", "")),
            module=str(data.get("module", "")),
            case_type=str(data.get("case_type", "")),
            video_id=str(data.get("video_id", "")),
            image_name=str(data.get("image_name", "")),
            frame_index=data.get("frame_index", ""),
            timestamp_sec=data.get("timestamp_sec", ""),
            track_id=data.get("track_id", ""),
            expected_result=str(data.get("expected_result", "")),
            actual_result=str(data.get("actual_result", "")),
            root_cause=str(data.get("root_cause", "")),
            tags=_parse_tags(data.get("tags", "")),
            snapshot_path=str(data.get("snapshot_path", "")),
            added_to_eval_set=str(data.get("added_to_eval_set", "no")),
            created_at=str(data.get("created_at", "")),
        )


class BadCaseService:
    """Append/read Bad Case metadata in CSV and optional JSONL formats."""

    def __init__(
        self,
        csv_path: str | Path = DEFAULT_BAD_CASE_CSV_PATH,
        jsonl_path: str | Path | None = DEFAULT_BAD_CASE_JSONL_PATH,
    ) -> None:
        self.csv_path = Path(csv_path)
        self.jsonl_path = Path(jsonl_path) if jsonl_path is not None else None

    def add_case(self, record: BadCaseRecord | dict[str, Any]) -> dict[str, str]:
        normalized = _coerce_record(record).to_dict()
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        write_header = not self.csv_path.exists() or self.csv_path.stat().st_size == 0
        with self.csv_path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=BAD_CASE_FIELDS)
            if write_header:
                writer.writeheader()
            writer.writerow(normalized)

        if self.jsonl_path is not None:
            self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)
            with self.jsonl_path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(normalized, ensure_ascii=False, sort_keys=True) + "\n")

        return normalized

    def list_cases(self) -> list[dict[str, str]]:
        if not self.csv_path.exists():
            return []
        with self.csv_path.open(newline="", encoding="utf-8") as file:
            return [
                {field_name: row.get(field_name, "") for field_name in BAD_CASE_FIELDS}
                for row in csv.DictReader(file)
            ]

    def write_jsonl(self, records: Iterable[BadCaseRecord | dict[str, Any]], path: str | Path) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as file:
            for record in records:
                file.write(
                    json.dumps(
                        _coerce_record(record).to_dict(),
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                    + "\n"
                )
        return output_path

    @staticmethod
    def read_jsonl(path: str | Path) -> list[dict[str, str]]:
        input_path = Path(path)
        if not input_path.exists():
            return []
        rows: list[dict[str, str]] = []
        with input_path.open(encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    rows.append(BadCaseRecord.from_dict(json.loads(line)).to_dict())
        return rows


def _coerce_record(record: BadCaseRecord | dict[str, Any]) -> BadCaseRecord:
    return record if isinstance(record, BadCaseRecord) else BadCaseRecord.from_dict(record)


def _parse_tags(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value)
