from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "docs" / "final_acceptance_checklist.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_final_acceptance_checklist_exists() -> None:
    assert CHECKLIST.exists()


def test_required_sections_exist() -> None:
    text = _read(CHECKLIST)
    required_sections = [
        "Project metadata",
        "Version/tag history",
        "Environment assumptions",
        "Dataset acceptance",
        "Training/evaluation acceptance",
        "Image prediction acceptance",
        "Video prediction acceptance",
        "Tracking acceptance",
        "Analytics acceptance",
        "Tracked video rendering acceptance",
        "Streamlit acceptance",
        "FastAPI acceptance",
        "Bad Case acceptance",
        "Docker/deployment static acceptance",
        "Manual pending acceptance",
        "Asset safety checks",
        "Test command matrix",
        "Known limitations",
        "Final go/no-go status",
    ]

    for section in required_sections:
        assert f"## {section}" in text


def test_references_required_evidence_files() -> None:
    text = _read(CHECKLIST)
    required_references = [
        "README.md",
        "docs/final_project_report.md",
        "docs/project_task_board.md",
        "docs/api_usage.md",
        "docs/docker_deployment.md",
        "docs/deployment_guide.md",
        "docs/bad_case_report.md",
        "docs/bad_cases_schema.md",
        "docs/video_analytics_mvp.md",
        "docs/streamlit_video_demo.md",
        "Dockerfile",
        ".dockerignore",
        "src/api.py",
        "src/track_video.py",
        "src/render_tracked_video.py",
    ]

    for reference in required_references:
        assert reference in text


def test_references_critical_fastapi_endpoints() -> None:
    text = _read(CHECKLIST)
    endpoints = [
        "/health",
        "/config",
        "/model-status",
        "/predict",
        "/api/videos/analyze",
        "/api/videos/jobs",
    ]

    for endpoint in endpoints:
        assert endpoint in text


def test_references_manual_pending_docker_items() -> None:
    text = _read(CHECKLIST)
    required_terms = [
        "docker build",
        "docker run FastAPI",
        "docker run Streamlit",
        "mounted-weight",
        "MODEL_PATH",
    ]

    for term in required_terms:
        assert term in text


def test_does_not_claim_docker_actual_build_or_run_completed() -> None:
    text = _read(CHECKLIST)
    forbidden_claims = [
        "Docker actual build completed",
        "Docker build passed",
        "docker run verified",
    ]

    for claim in forbidden_claims:
        assert claim not in text


def test_references_asset_safety_checks() -> None:
    text = _read(CHECKLIST)
    required_terms = [
        "make danger-check",
        "make list-large-docs",
        "no weights in git",
        "no local videos in git",
        "runs/local_outputs not committed",
    ]

    for term in required_terms:
        assert term in text


def test_primary_docs_link_final_acceptance_checklist() -> None:
    docs = [
        ROOT / "README.md",
        ROOT / "docs" / "final_project_report.md",
        ROOT / "docs" / "project_task_board.md",
    ]

    for doc in docs:
        assert "docs/final_acceptance_checklist.md" in _read(doc)
