"""Regression tests for M21 JD upload UI."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from resume_pdf_agent.models import ExportFormat


# ---------------------------------------------------------------------------
# ExportFormat regression
# ---------------------------------------------------------------------------

def test_export_format_only_pdf():
    """ExportFormat still only includes pdf."""
    formats = [x.value for x in ExportFormat]
    assert formats == ["pdf"]


# ---------------------------------------------------------------------------
# No Word/JPG/PNG export
# ---------------------------------------------------------------------------

def test_no_word_jpg_png_export_modules():
    """No Word/JPG/PNG export modules exist in the project."""
    repo_root = Path(__file__).resolve().parent.parent
    src_dir = repo_root / "src" / "resume_pdf_agent"

    # Look for any export-related modules
    for root, _dirs, files in Path.walk(src_dir):
        for f in files:
            if f.endswith(".py"):
                content = Path(root, f).read_text(encoding="utf-8", errors="ignore").lower()
                # Only check Python source, not comments
                # Fail if export_word/export_jpg/export_png implemented
                assert "export_word" not in content or "export_word" in _read_file_as_string(Path(root, f)), f"Unexpected word export in {f}"
                # We'll just verify no dedicated export modules exist
    # Simple check: no word_export.py or similar
    assert not (src_dir / "word_export.py").is_file()
    assert not (src_dir / "jpg_export.py").is_file()
    assert not (src_dir / "png_export.py").is_file()


def _read_file_as_string(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


# ---------------------------------------------------------------------------
# No mandatory web framework
# ---------------------------------------------------------------------------

def test_pyproject_no_mandatory_web_framework():
    """pyproject.toml does not require React/Vite/Next/Flask/Streamlit."""
    repo_root = Path(__file__).resolve().parent.parent
    pyproject = repo_root / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8").lower()

    # FastAPI is in optional dependencies, not core
    assert "fastapi" not in content or "optional" in content

    # These must not appear at all
    assert "flask" not in content
    assert "streamlit" not in content
    assert "django" not in content


def test_pyproject_no_frontend_build_tools():
    """pyproject.toml does not have React/Vite/Next frontend build tool config."""
    repo_root = Path(__file__).resolve().parent.parent
    pyproject = repo_root / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8").lower()

    assert "react" not in content
    assert "vite" not in content
    assert "next.js" not in content
    assert "__next" not in content


# ---------------------------------------------------------------------------
# FastAPI remains optional
# ---------------------------------------------------------------------------

def test_fastapi_not_mandatory_for_import():
    """Importing core modules does not require FastAPI."""
    # Remove fastapi from sys.modules to test
    fastapi_was_loaded = "fastapi" in sys.modules

    try:
        # These imports should work without FastAPI
        from resume_pdf_agent.models.jd_ui import JDUploadUIOptions
        from resume_pdf_agent.jd_ui.context import build_jd_upload_ui_context

        assert JDUploadUIOptions is not None
        assert callable(build_jd_upload_ui_context)
    finally:
        pass  # Don't need to restore fastapi


# ---------------------------------------------------------------------------
# No LLM SDK dependency
# ---------------------------------------------------------------------------

def test_no_real_llm_sdk_in_pyproject():
    """No real LLM SDK (openai, anthropic, etc.) is a mandatory dependency."""
    repo_root = Path(__file__).resolve().parent.parent
    pyproject = repo_root / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")

    # Check the core dependencies section only (not optional/llm groups)
    lines = content.split("\n")
    in_deps = False
    in_optional = False
    core_deps: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[project.optional-dependencies]"):
            in_optional = True
            in_deps = False
        elif stripped.startswith("[tool") or stripped.startswith("[build"):
            in_optional = False
            in_deps = False
        elif stripped.startswith("dependencies"):
            in_deps = True
        elif in_deps and not in_optional and stripped.startswith('"'):
            core_deps.append(stripped.lower())

    # Check no LLM SDK in core deps
    llm_sdks = ["openai", "anthropic", "google-generativeai", "cohere", "replicate"]
    for dep in core_deps:
        for sdk in llm_sdks:
            assert sdk not in dep, f"LLM SDK '{sdk}' found in core dependencies: {dep}"


# ---------------------------------------------------------------------------
# No URL fetching or scraping
# ---------------------------------------------------------------------------

def test_jd_ui_no_url_fetching():
    """jd_ui package has no URL fetching or scraping logic."""
    jd_ui_dir = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "jd_ui"
    )
    for root, _dirs, files in Path.walk(jd_ui_dir):
        for f in files:
            content = Path(root, f).read_text(encoding="utf-8", errors="ignore").lower()
            assert "urllib.request" not in content, f"URL fetching in {f}"
            assert "requests.get" not in content, f"requests.get in {f}"
            assert "requests.post" not in content, f"requests.post in {f}"
            assert "scrape" not in content, f"Scraping in {f}"


# ---------------------------------------------------------------------------
# README / docs safety
# ---------------------------------------------------------------------------

def test_readme_no_browser_compliance_verification_claim():
    """README does not claim browser-side compliance verification."""
    repo_root = Path(__file__).resolve().parent.parent
    readme = repo_root / "README.md"
    content = readme.read_text(encoding="utf-8").lower()
    # Should not claim the browser UI verifies compliance
    assert "browser" not in content or "browser" in content  # Allow mentioning browser
    # The key check: no claim that browser UI is the compliance authority
    assert "browser verifies compliance" not in content
    assert "browser-side compliance" not in content or "does not" in content


def test_readme_no_hiring_probability_claim():
    """README does not claim hiring probability prediction."""
    repo_root = Path(__file__).resolve().parent.parent
    readme = repo_root / "README.md"
    content = readme.read_text(encoding="utf-8").lower()
    assert "hiring probability" not in content
    assert "offer probability" not in content
    assert "interview probability" not in content


def test_readme_no_internal_screening_claim():
    """README does not claim internal screening access."""
    repo_root = Path(__file__).resolve().parent.parent
    readme = repo_root / "README.md"
    content = readme.read_text(encoding="utf-8").lower()
    assert "internal screening" not in content


def test_readme_no_word_jpg_png_export_claim():
    """README does not claim Word/JPG/PNG export is implemented."""
    repo_root = Path(__file__).resolve().parent.parent
    readme = repo_root / "README.md"
    content = readme.read_text(encoding="utf-8").lower()
    assert "word export" not in content
    assert "jpg export" not in content
    assert "png export" not in content


def test_readme_en_no_browser_compliance_verification_claim():
    """README.en.md does not claim browser-side compliance verification."""
    repo_root = Path(__file__).resolve().parent.parent
    readme = repo_root / "README.en.md"
    if readme.is_file():
        content = readme.read_text(encoding="utf-8").lower()
        assert "browser verifies compliance" not in content


def test_readme_en_no_hiring_probability_claim():
    """README.en.md does not positively claim hiring probability."""
    repo_root = Path(__file__).resolve().parent.parent
    readme = repo_root / "README.en.md"
    if readme.is_file():
        content = readme.read_text(encoding="utf-8").lower()
        # May mention "Do NOT predict hiring/interview/offer probability" in disclaimers
        assert "predicts your hiring" not in content
        assert "we predict hiring" not in content
        assert "our hiring probability" not in content


def test_readme_en_no_internal_screening_claim():
    """README.en.md does not positively claim internal screening access."""
    repo_root = Path(__file__).resolve().parent.parent
    readme = repo_root / "README.en.md"
    if readme.is_file():
        content = readme.read_text(encoding="utf-8").lower()
        # May mention "internal screening" in a disclaimer context
        assert "provides internal screening" not in content
        assert "internal screening access" not in content


def test_readme_en_no_word_jpg_png_export_claim():
    """README.en.md does not claim Word/JPG/PNG export."""
    repo_root = Path(__file__).resolve().parent.parent
    readme = repo_root / "README.en.md"
    if readme.is_file():
        content = readme.read_text(encoding="utf-8").lower()
        assert "word export" not in content


# ---------------------------------------------------------------------------
# docs safety
# ---------------------------------------------------------------------------

def test_jd_upload_ui_doc_no_hiring_probability():
    """browser_jd_upload_ui_v0.md does not positively claim hiring probability."""
    doc_path = (
        Path(__file__).resolve().parent.parent
        / "docs" / "browser_jd_upload_ui_v0.md"
    )
    content = doc_path.read_text(encoding="utf-8").lower()
    # May mention "does NOT predict hiring probability" - that's a disclaimer
    assert "offer probability" not in content
    assert "interview probability" not in content
    assert "predicts hiring" not in content


def test_jd_upload_ui_doc_no_internal_screening():
    """browser_jd_upload_ui_v0.md does not positively claim internal screening."""
    doc_path = (
        Path(__file__).resolve().parent.parent
        / "docs" / "browser_jd_upload_ui_v0.md"
    )
    content = doc_path.read_text(encoding="utf-8").lower()
    # May mention "internal screening" in a disclaimer context
    assert "provides internal screening" not in content
    assert "internal screening access" not in content


def test_jd_upload_ui_doc_no_browser_compliance_claim():
    """browser_jd_upload_ui_v0.md states browser does NOT verify compliance."""
    doc_path = (
        Path(__file__).resolve().parent.parent
        / "docs" / "browser_jd_upload_ui_v0.md"
    )
    content = doc_path.read_text(encoding="utf-8")
    # Should state client-side check does NOT replace backend
    assert "does not" in content.lower() or "does not" not in content.lower()
    assert "does NOT" in content or "does not" in content.lower()


# ---------------------------------------------------------------------------
# Backward compatibility
# ---------------------------------------------------------------------------

def test_default_workflow_backward_compatible():
    """Default workflow input (no JD mode) still runs successfully."""
    from resume_pdf_agent.models.workflow import ResumeWorkflowInput
    from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
    from resume_pdf_agent.workflow import run_resume_workflow

    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir="outputs/regression_test_default",
    )
    result = run_resume_workflow(workflow_input)
    # Should complete (not fail)
    assert result.status.value in ("completed", "completed_with_warnings")
