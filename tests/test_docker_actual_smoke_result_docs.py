from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "docs" / "docker_actual_smoke_result.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_docker_actual_smoke_result_exists() -> None:
    assert RESULT.exists()


def test_result_contains_required_summary() -> None:
    text = _read(RESULT)
    required_terms = [
        "Docker Actual Smoke Result",
        "v0.14.4-docker-actual-build-smoke",
        "Final status",
        "Partial Docker Actual Smoke Passed",
        "After dependency fix",
        "docker build -t yolov8-vehicle-pedestrian:latest .",
        "requirements-api.txt",
    ]

    for term in required_terms:
        assert term in text


def test_result_contains_fastapi_and_streamlit_smoke_details() -> None:
    text = _read(RESULT)
    required_terms = [
        "docker run",
        "uvicorn src.api:app",
        "/health",
        "/config",
        "/model-status",
        "/api/videos/analyze",
        "job_id",
        "status=created",
        "Streamlit container smoke",
        "streamlit run app.py",
    ]

    for term in required_terms:
        assert term in text


def test_result_contains_asset_safety_and_cleanup() -> None:
    text = _read(RESULT)
    required_terms = [
        "Asset safety",
        "no weights",
        "No repository outputs were committed",
        "local_outputs",
        "runs",
        "CSV",
        "JSON",
        "MP4",
    ]

    for term in required_terms:
        assert term in text


def test_primary_docs_link_docker_actual_smoke_result() -> None:
    docs = [
        ROOT / "README.md",
        ROOT / "docs" / "docker_deployment.md",
        ROOT / "docs" / "final_acceptance_checklist.md",
        ROOT / "docs" / "final_project_report.md",
        ROOT / "docs" / "project_task_board.md",
    ]

    for doc in docs:
        assert "docs/docker_actual_smoke_result.md" in _read(doc)


def test_result_does_not_suggest_committing_assets() -> None:
    text = _read(RESULT).lower()
    forbidden_phrases = [
        "commit weights",
        "commit videos",
        "commit local_outputs",
        "commit runs",
        "commit docker image",
    ]

    for phrase in forbidden_phrases:
        assert phrase not in text
