"""Documentation contract tests for the Bad Case schema foundation."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "docs" / "bad_cases_schema.md"
REPORT = ROOT / "docs" / "bad_case_report.md"
GALLERY_CSV = ROOT / "docs" / "error_case_gallery" / "cases.csv"
REVIEWED_CSV = ROOT / "docs" / "error_case_gallery" / "reviewed_bad_cases.csv"

REQUIRED_FIELDS = [
    "case_id",
    "module",
    "case_type",
    "image_name",
    "video_id",
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

REVIEWED_EXTRA_FIELDS = [
    "review_status",
    "reviewer_note",
]

ALLOWED_MODULES = [
    "detector",
    "tracker",
    "counter",
    "roi",
    "event",
    "api",
    "streamlit",
    "dataset",
    "deployment",
    "documentation",
]

ALLOWED_CASE_TYPES = [
    "false_positive",
    "false_negative",
    "class_confusion",
    "localization_error",
    "duplicate_detection",
    "missed_track",
    "track_lost",
    "id_switch",
    "fragmented_track",
    "count_error",
    "line_crossing_error",
    "roi_membership_error",
    "roi_config_error",
    "rule_error",
    "threshold_error",
    "api_contract_error",
    "data_quality_issue",
    "deployment_issue",
    "documentation_gap",
]

FORBIDDEN_OUTPUT_MARKERS = [
    "runs/",
    ".pt",
    ".onnx",
    ".mp4",
    ".avi",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_bad_cases_schema_exists_and_documents_required_fields():
    assert SCHEMA.is_file()
    text = _read(SCHEMA)

    assert "# Bad Case Schema" in text
    for field in REQUIRED_FIELDS:
        assert f"`{field}`" in text


def test_bad_cases_schema_documents_allowed_modules_and_case_types():
    text = _read(SCHEMA)

    for module in ALLOWED_MODULES:
        assert f"`{module}`" in text
    for case_type in ALLOWED_CASE_TYPES:
        assert f"`{case_type}`" in text


def test_bad_case_report_links_schema_taxonomy_hard_examples_and_gallery():
    assert REPORT.is_file()
    text = _read(REPORT)

    assert "docs/bad_cases_schema.md" in text
    assert "docs/error_taxonomy.md" in text
    assert "docs/hard_examples.md" in text
    assert "docs/error_case_gallery/README.md" in text
    assert "docs/error_case_gallery/cases.csv" in text


def test_readme_and_final_report_mention_bad_case_schema_and_report():
    readme = _read(ROOT / "README.md")
    final_report = _read(ROOT / "docs" / "final_project_report.md")

    for text in [readme, final_report]:
        assert "Bad Case" in text
        assert "bad_cases_schema.md" in text
        assert "bad_case_report.md" in text


def test_gallery_cases_csv_uses_schema_header_and_stays_small():
    assert GALLERY_CSV.is_file()
    assert GALLERY_CSV.stat().st_size < 50_000

    with GALLERY_CSV.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        assert reader.fieldnames is not None
        for field in REQUIRED_FIELDS:
            assert field in reader.fieldnames
        rows = list(reader)

    assert rows
    for row in rows:
        for value in row.values():
            lowered = (value or "").lower()
            assert ".mp4" not in lowered
            assert ".avi" not in lowered
            assert ".pt" not in lowered
            assert ".onnx" not in lowered
            assert "runs/" not in lowered
            assert "local_outputs/" not in lowered


def test_reviewed_bad_cases_csv_is_small_reviewed_collection():
    assert REVIEWED_CSV.is_file()
    assert REVIEWED_CSV.stat().st_size < 75_000

    with REVIEWED_CSV.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        assert reader.fieldnames is not None
        for field in REQUIRED_FIELDS + REVIEWED_EXTRA_FIELDS:
            assert field in reader.fieldnames
        rows = list(reader)

    assert 20 <= len(rows) <= 50
    case_ids = [row["case_id"] for row in rows]
    assert len(case_ids) == len(set(case_ids))

    modules = {row["module"] for row in rows}
    assert {"detector", "tracker", "counter", "roi", "event"}.issubset(modules)

    case_types = {row["case_type"] for row in rows}
    assert {
        "false_positive",
        "false_negative",
        "class_confusion",
        "id_switch",
        "track_lost",
        "count_error",
        "roi_membership_error",
        "roi_config_error",
        "rule_error",
        "threshold_error",
    }.issubset(case_types)

    for row in rows:
        assert row["review_status"] == "reviewed"
        assert row["reviewer_note"]
        snapshot_path = row["snapshot_path"]
        assert snapshot_path.startswith("docs/error_case_gallery/images/")
        assert not snapshot_path.startswith("/")
        for value in row.values():
            lowered = (value or "").lower()
            assert ".mp4" not in lowered
            assert ".avi" not in lowered
            assert ".mov" not in lowered
            assert ".mkv" not in lowered
            assert ".pt" not in lowered
            assert ".pth" not in lowered
            assert ".onnx" not in lowered
            assert ".zip" not in lowered
            assert "runs/" not in lowered
            assert "local_outputs/" not in lowered
            assert "local_weights/" not in lowered


def test_schema_and_report_do_not_reference_forbidden_generated_outputs():
    combined = "\n".join([_read(SCHEMA), _read(REPORT)])

    for marker in FORBIDDEN_OUTPUT_MARKERS:
        assert marker not in combined

    assert "local_outputs/bad_cases/bad_cases.csv" in combined
    assert "must not be committed" in combined
