from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MACOS_SCRIPT = ROOT / "scripts" / "start_app_macos.command"
WINDOWS_SCRIPT = ROOT / "scripts" / "start_app_windows.bat"
USER_GUIDE = ROOT / "docs" / "non_technical_user_guide.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_non_technical_launcher_files_exist() -> None:
    assert MACOS_SCRIPT.is_file()
    assert WINDOWS_SCRIPT.is_file()
    assert USER_GUIDE.is_file()


def test_launcher_scripts_avoid_dangerous_commands() -> None:
    combined = "\n".join([_read(MACOS_SCRIPT), _read(WINDOWS_SCRIPT)]).lower()
    forbidden_terms = [
        "rm -rf",
        "git add",
        "git commit",
        "curl | sh",
        "del local_weights",
        "rmdir local_weights",
        "del local_outputs",
        "rmdir local_outputs",
    ]

    for term in forbidden_terms:
        assert term not in combined


def test_launcher_scripts_include_required_checks_and_urls() -> None:
    combined = "\n".join([_read(MACOS_SCRIPT), _read(WINDOWS_SCRIPT)])
    required_terms = [
        "local_weights/best.pt",
        "local_weights\\best.pt",
        ".venv",
        "uvicorn",
        "streamlit",
        "localhost:8000",
        "localhost:8501",
        "MODEL_PATH",
    ]

    for term in required_terms:
        assert term in combined


def test_readme_links_non_technical_user_guide() -> None:
    text = _read(ROOT / "README.md")

    assert "For non-technical users" in text
    assert "docs/non_technical_user_guide.md" in text
    assert "scripts/start_app_macos.command" in text
    assert "scripts/start_app_windows.bat" in text


def test_non_technical_user_guide_is_plain_language_and_safe() -> None:
    text = _read(USER_GUIDE)
    required_terms = [
        "普通用户",
        ".venv",
        "local_weights/best.pt",
        "scripts/start_app_macos.command",
        "scripts/start_app_windows.bat",
        "http://localhost:8501",
        "http://localhost:8000",
        "图片检测",
        "视频分析",
        "结果文件",
        "端口被占用",
        "如何停止",
    ]
    forbidden_terms = [
        "git add",
        "git commit",
        "rm -rf",
    ]

    for term in required_terms:
        assert term in text
    for term in forbidden_terms:
        assert term not in text
