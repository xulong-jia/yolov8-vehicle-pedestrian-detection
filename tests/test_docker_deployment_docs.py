"""Static acceptance checks for Docker and deployment documentation."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_dockerfile_exists_and_has_runtime_entrypoint() -> None:
    dockerfile = ROOT / "Dockerfile"

    assert dockerfile.is_file()
    text = _read("Dockerfile")
    assert "FROM python:" in text
    assert "WORKDIR /app" in text
    assert "MODEL_PATH" in text
    assert "requirements-api.txt" in text
    assert "-r requirements-api.txt" in text
    assert "apt-get install" in text
    assert "libxcb1" in text
    assert "COPY app.py" in text
    assert "COPY src" in text
    assert "EXPOSE 8501" in text or "EXPOSE 8000" in text
    assert "streamlit" in text or "uvicorn" in text


def test_dockerignore_excludes_local_assets_and_large_files() -> None:
    dockerignore = ROOT / ".dockerignore"

    assert dockerignore.is_file()
    text = _read(".dockerignore")
    required_patterns = [
        ".venv",
        "__pycache__",
        "runs",
        "local_outputs",
        "local_weights",
        "local_videos/source",
        "dataset/train",
        "dataset/valid",
        "dataset/test",
        "*.pt",
        "*.pth",
        "*.onnx",
        "*.mp4",
        "*.avi",
        "*.mov",
        "*.mkv",
        "*.zip",
    ]
    for pattern in required_patterns:
        assert pattern in text


def test_docker_deployment_docs_cover_manual_acceptance_commands() -> None:
    text = _read("docs/docker_deployment.md")
    required_terms = [
        "Docker Deployment",
        "v0.14.1 static acceptance",
        "v0.14.4",
        "requirements-api.txt",
        "docker build",
        "docker run",
        "uvicorn src.api:app",
        "streamlit run app.py",
        "MODEL_PATH",
        "local_weights",
        "volume mount",
        "/health",
        "/config",
        "/model-status",
        "/predict",
        "/api/videos/analyze",
        "run_dir",
        "read-only",
    ]
    for term in required_terms:
        assert term in text


def test_deployment_guide_mentions_local_and_docker_paths() -> None:
    text = _read("docs/deployment_guide.md")
    required_terms = [
        "uvicorn src.api:app",
        "streamlit run app.py",
        "docker build",
        "docker run",
        "MODEL_PATH",
        "/health",
        "/predict",
        "/api/videos/analyze",
        "/api/videos/jobs",
        "/detections",
        "/tracks",
        "/analytics",
        "/events",
        "Bad Case",
        "async video analysis jobs",
        "video_jobs.sqlite3",
        "Actual Docker build/run smoke later passed",
        "mounted-weight container `/predict` passed",
    ]
    for term in required_terms:
        assert term in text


def test_docker_docs_reflect_final_passed_status() -> None:
    combined = "\n".join(
        _read(path)
        for path in [
            "README.md",
            "docs/docker_deployment.md",
            "docs/deployment_guide.md",
            "docs/final_acceptance_checklist.md",
        ]
    )
    required_terms = [
        "docs/docker_actual_smoke_result.md",
        "Docker Actual Smoke Passed",
        "mounted-weight `/predict` passed",
        "v0.14.5",
    ]
    forbidden_terms = [
        "actual build/run smoke remains " + "pending",
        "mounted-weight container inference " + "pending",
        "No real Docker build/run validation " + "yet",
    ]

    for term in required_terms:
        assert term in combined
    for term in forbidden_terms:
        assert term not in combined


def test_readme_links_deployment_docs_and_runtime_commands() -> None:
    text = _read("README.md")
    required_terms = [
        "Docker",
        "docs/docker_deployment.md",
        "docs/deployment_guide.md",
        "uvicorn src.api:app",
        "streamlit run app.py",
        "MODEL_PATH",
        "v0.14.1",
        "static acceptance",
    ]
    for term in required_terms:
        assert term in text


def test_docs_do_not_instruct_committing_large_assets() -> None:
    combined = "\n".join(
        _read(path)
        for path in [
            "README.md",
            "docs/docker_deployment.md",
            "docs/deployment_guide.md",
            "docs/final_project_report.md",
            "docs/project_task_board.md",
        ]
    ).lower()
    forbidden_phrases = [
        "git add local_weights",
        "git add *.pt",
        "git add *.mp4",
        "git commit local_weights",
        "git commit *.pt",
        "git commit *.mp4",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in combined
