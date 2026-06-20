from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_SUMMARY = ROOT / "docs" / "release_summary.md"
DELIVERY_NOTES = ROOT / "docs" / "delivery_notes.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_release_summary_exists() -> None:
    assert RELEASE_SUMMARY.exists()


def test_delivery_notes_exists() -> None:
    assert DELIVERY_NOTES.exists()


def test_release_summary_includes_final_release_contract() -> None:
    text = _read(RELEASE_SUMMARY)
    required_terms = [
        "v1.0.0-final-release-summary",
        "Go for final local/Docker acceptance",
        "YOLOv8s",
        "Docker Actual Smoke Passed",
        "Mounted-weight `/predict` passed",
        "No `.pt` files committed",
        "No `runs/` or `local_outputs/` committed",
        "SQLite-backed video job/result metadata index",
        "video_jobs.sqlite3",
        "v1.3.0-badcase-gt-eval-scaffold",
        "v1.3.2-sqlite-job-restart-smoke",
        "v1.4.0-artifact-download-endpoints",
        "v1.4.1-docker-v1-api-smoke-refresh",
        "v1.5.0-api-key-and-structured-logging",
        "v1.8.1-final-polish-and-frontend-audit-note",
        "v1.8.2-non-technical-user-launcher",
        "real local FastAPI process restart smoke",
        "Docker runtime smoke refresh",
        "Optional API key authentication",
        "X-Request-ID",
        "artifact download endpoints",
        "GT evaluation scaffold",
        "npm audit",
        "Vite 8",
        "scripts/start_app_macos.command",
        "docs/non_technical_user_guide.md",
    ]

    for term in required_terms:
        assert term in text


def test_delivery_notes_include_handoff_commands_and_asset_policy() -> None:
    text = _read(DELIVERY_NOTES)
    required_terms = [
        "local_weights/best.pt",
        "Do not git add",
        "streamlit run app.py",
        "uvicorn src.api:app",
        "docker build",
        "docker run",
        "MODEL_PATH",
        "make danger-check",
        "scripts/start_app_macos.command",
        "scripts/start_app_windows.bat",
    ]

    for term in required_terms:
        assert term in text


def test_primary_docs_link_release_and_delivery_notes() -> None:
    docs = [
        ROOT / "README.md",
        ROOT / "docs" / "final_project_report.md",
        ROOT / "docs" / "final_acceptance_checklist.md",
        ROOT / "docs" / "project_task_board.md",
    ]

    for doc in docs:
        text = _read(doc)
        assert "docs/release_summary.md" in text or "release_summary.md" in text
        assert "docs/delivery_notes.md" in text or "delivery_notes.md" in text


def test_release_docs_do_not_keep_outdated_status() -> None:
    combined = "\n".join(
        _read(path)
        for path in [
            ROOT / "README.md",
            ROOT / "docs" / "final_project_report.md",
            ROOT / "docs" / "final_acceptance_checklist.md",
            ROOT / "docs" / "project_task_board.md",
            RELEASE_SUMMARY,
            DELIVERY_NOTES,
        ]
    )
    forbidden_terms = [
        "No real Docker build/run validation " + "yet",
        "No production API inference endpoint " + "yet",
        "mounted-weight /predict " + "pending",
        "actual build/run smoke remains " + "pending",
    ]

    for term in forbidden_terms:
        assert term not in combined
