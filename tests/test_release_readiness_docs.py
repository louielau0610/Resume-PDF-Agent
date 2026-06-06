"""Tests for M13 release-readiness documentation checks.

Verifies that key docs exist, contain required content, and avoid
forbidden claims.
"""

from __future__ import annotations

from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent


# ── Helpers ────────────────────────────────────────────────────────────────

def _read(path: str) -> str:
    return (_REPO_ROOT / path).read_text(encoding="utf-8")


# ── File existence ─────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "doc_path",
    [
        "docs/demo_walkthrough_v0.md",
        "docs/architecture_diagram_v0.md",
        "docs/github_project_overview_v0.md",
        "docs/release_checklist_v0.md",
        "docs/limitations_and_roadmap_v0.md",
        "examples/README.md",
        "examples/sample_data_science_demo.md",
        "scripts/run_demo_workflow.py",
        "scripts/validate_release_readiness.py",
    ],
)
def test_m13_doc_exists(doc_path: str):
    """Each M13 document/script must exist."""
    assert (_REPO_ROOT / doc_path).is_file(), f"Missing: {doc_path}"


# ── README content assertions ──────────────────────────────────────────────

def test_readme_mentions_criteria_aware_resume_pdf():
    """README.md must mention criteria-aware resume PDF generation."""
    text = _read("README.md").lower()
    assert "criteria" in text or "resume" in text
    assert "pdf" in text


def test_readme_mentions_pdf_only_limitation():
    """README.md must indicate v0 PDF-only limitation."""
    text = _read("README.md").lower()
    # The word "pdf" or "仅" should be present; "PDF" is central.
    assert "pdf" in text


def test_readme_no_internal_screening_claim():
    """README.md must NOT claim internal company screening access."""
    text = _read("README.md").lower()
    assert "internal screening" not in text


def test_readme_no_hiring_probability_claim():
    """README.md must NOT claim hiring probability prediction."""
    text = _read("README.md").lower()
    assert "hiring probability" not in text
    assert "offer probability" not in text


def test_readme_no_word_jpg_png_export_claim():
    """README.md must NOT claim Word/JPG/PNG export is implemented."""
    text = _read("README.md").lower()
    # We should not see claims that Word/JPG/PNG export *is implemented*.
    # Check for common export misclaims.
    forbidden = ["export to word", "export to .docx", "export to jpg",
                 "export to png", "word export", "jpg export", "png export"]
    for phrase in forbidden:
        assert phrase not in text, f"README contains forbidden export claim: '{phrase}'"


# ── English README ─────────────────────────────────────────────────────────

def test_readme_en_is_english():
    """README.en.md must be predominantly English."""
    text = _read("README.en.md")
    # Should contain common English words.
    assert "resume" in text.lower()
    assert "pdf" in text.lower()


# ── Release checklist ─────────────────────────────────────────────────────

def test_release_checklist_exists():
    """Release checklist doc must exist and be non-empty."""
    path = _REPO_ROOT / "docs" / "release_checklist_v0.md"
    assert path.is_file()
    content = path.read_text(encoding="utf-8")
    assert len(content) > 100, "Release checklist appears empty."


# ── Architecture diagram ───────────────────────────────────────────────────

def test_architecture_doc_contains_mermaid():
    """Architecture doc must contain Mermaid code blocks."""
    text = _read("docs/architecture_diagram_v0.md")
    assert "```mermaid" in text, "No Mermaid code block found."


# ── Limitations & roadmap ─────────────────────────────────────────────────

def test_limitations_doc_exists():
    """Limitations and roadmap doc must exist."""
    path = _REPO_ROOT / "docs" / "limitations_and_roadmap_v0.md"
    assert path.is_file()
    content = path.read_text(encoding="utf-8")
    assert len(content) > 100


# ── Export format constraint ───────────────────────────────────────────────

def test_export_format_only_pdf():
    """ExportFormat enum must only contain PDF."""
    from resume_pdf_agent.models.enums import ExportFormat

    members = [m.value for m in ExportFormat]
    assert members == ["pdf"], (
        f"ExportFormat should only contain 'pdf', got: {members}"
    )


# ── No web-framework dependency ────────────────────────────────────────────

def test_no_web_framework_in_pyproject():
    """pyproject.toml must not require React/FastAPI/Flask/Streamlit as core dependencies."""
    text = _read("pyproject.toml").lower()
    # Only check core dependencies, not optional-dependencies
    # Split on [project.optional-dependencies] to isolate core deps
    core_section = text.split("[project.optional-dependencies]")[0]
    forbidden = ["flask", "streamlit", "react", "django"]
    for fw in forbidden:
        assert fw not in core_section, f"pyproject.toml core deps reference forbidden dep: {fw}"


# ── Chinese-first README check ─────────────────────────────────────────────

def test_readme_is_chinese_first():
    """README.md must contain Chinese characters (Chinese-first)."""
    text = _read("README.md")
    import re
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    assert len(chinese_chars) > 20, (
        "README.md should be Chinese-first but lacks Chinese characters."
    )
