from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "docker_actual_smoke_plan.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_docker_actual_smoke_plan_exists() -> None:
    assert PLAN.exists()


def test_required_sections_exist() -> None:
    text = _read(PLAN)
    required_sections = [
        "Purpose",
        "Current preflight result",
        "Manual prerequisite checklist",
        "Dockerfile static review",
        ".dockerignore asset safety review",
        "Exact build command",
        "FastAPI container smoke command",
        "Streamlit container smoke command",
        "Mounted-weight /predict smoke command",
        "Video job skeleton smoke command",
        "Stop/cleanup instructions",
        "Expected success criteria",
        "Failure handling",
        "Go/no-go for actual build",
    ]

    for section in required_sections:
        assert f"## {section}" in text


def test_plan_includes_exact_smoke_commands() -> None:
    text = _read(PLAN)
    required_terms = [
        "docker build -t yolov8-vehicle-pedestrian:latest .",
        "docker run",
        "uvicorn src.api:app",
        "streamlit run app.py",
        "MODEL_PATH",
        "local_weights",
        "/health",
        "/config",
        "/model-status",
        "/predict",
        "/api/videos/analyze",
    ]

    for term in required_terms:
        assert term in text


def test_plan_records_docker_unavailable_blocker() -> None:
    text = _read(PLAN)
    required_terms = [
        "docker_info_exit=127",
        "Docker CLI/daemon unavailable",
        "No-Go",
    ]

    for term in required_terms:
        assert term in text


def test_plan_states_v0143_does_not_run_docker_build_or_run() -> None:
    text = _read(PLAN)
    assert "`v0.14.3` does not execute `docker build` or `docker run`" in text


def test_plan_references_asset_safety() -> None:
    text = _read(PLAN)
    required_terms = [
        "no weights copied",
        "no local video/output copied",
        "local_outputs",
        "runs",
        "*.pt",
        "*.mp4",
        "*.zip",
    ]

    for term in required_terms:
        assert term in text


def test_primary_docs_link_docker_actual_smoke_plan() -> None:
    docs = [
        ROOT / "README.md",
        ROOT / "docs" / "docker_deployment.md",
        ROOT / "docs" / "final_acceptance_checklist.md",
        ROOT / "docs" / "final_project_report.md",
        ROOT / "docs" / "project_task_board.md",
    ]

    for doc in docs:
        assert "docs/docker_actual_smoke_plan.md" in _read(doc)
