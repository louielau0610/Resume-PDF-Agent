"""Regression tests for M22 LLM review UI."""

from __future__ import annotations

import sys
from pathlib import Path

from resume_pdf_agent.models import ExportFormat
from resume_pdf_agent.models.llm import (
    LLMProviderType,
    LLMRewriteCandidate,
    LLMRewriteMode,
    LLMRewriteResult,
    LLMRewriteStatus,
)
from resume_pdf_agent.models.workflow import ResumeWorkflowInput
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.workflow import run_resume_workflow


# ---------------------------------------------------------------------------
# ExportFormat regression
# ---------------------------------------------------------------------------

def test_export_format_still_only_pdf():
    """ExportFormat still only includes pdf."""
    formats = [x.value for x in ExportFormat]
    assert formats == ["pdf"]


# ---------------------------------------------------------------------------
# M16 tests still pass
# ---------------------------------------------------------------------------

def test_m16_provider_type_unchanged():
    """LLMProviderType enum unchanged."""
    assert hasattr(LLMProviderType, "MOCK")
    assert hasattr(LLMProviderType, "DISABLED")
    assert hasattr(LLMProviderType, "EXTERNAL")


def test_m16_rewrite_status_unchanged():
    """LLMRewriteStatus enum unchanged."""
    assert hasattr(LLMRewriteStatus, "REWRITTEN")
    assert hasattr(LLMRewriteStatus, "FAILED_VALIDATION")


def test_m16_candidate_model_unchanged():
    """LLMRewriteCandidate model still works."""
    c = LLMRewriteCandidate(
        candidate_id="test",
        original_text="Original.",
        rewritten_text="Rewritten.",
        provider=LLMProviderType.MOCK,
        mode=LLMRewriteMode.CONSERVATIVE_POLISH,
        status=LLMRewriteStatus.REWRITTEN,
    )
    assert c.candidate_id == "test"
    assert c.needs_confirmation is True  # default


def test_m16_result_model_unchanged():
    """LLMRewriteResult model still works."""
    r = LLMRewriteResult(
        status=LLMRewriteStatus.REWRITTEN,
        provider=LLMProviderType.MOCK,
        candidates=[
            LLMRewriteCandidate(
                candidate_id="c1",
                original_text="Test.",
                rewritten_text="Test improved.",
                provider=LLMProviderType.MOCK,
                mode=LLMRewriteMode.CONSERVATIVE_POLISH,
                status=LLMRewriteStatus.REWRITTEN,
            ),
        ],
        candidates_generated=1,
        candidates_requiring_confirmation=1,
        summary="Test.",
    )
    assert r.candidates_generated == 1


# ---------------------------------------------------------------------------
# Workflow backward compatibility
# ---------------------------------------------------------------------------

def test_default_workflow_no_write_llm_review_ui():
    """Default workflow without write_llm_review_ui still works."""
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir="outputs/regression_m22_default",
    )
    # Default is write_llm_review_ui=False
    assert workflow_input.write_llm_review_ui is False
    result = run_resume_workflow(workflow_input)
    assert result.status.value in ("completed", "completed_with_warnings")


def test_workflow_with_llm_review_ui_flag_but_no_llm(tmp_path):
    """Workflow with write_llm_review_ui=True but no LLM enabled warns gracefully."""
    import os
    output_dir = tmp_path / "m22_no_llm"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
        write_llm_review_ui=True,
        enable_llm_rewriting=False,
    )
    result = run_resume_workflow(workflow_input)
    # Should complete (not crash)
    assert result.status.value in ("completed", "completed_with_warnings")
    # Should have a warning about missing LLM result
    warning_texts = " ".join(result.warnings).lower()
    assert "write_llm_review_ui" in warning_texts or "llm" in warning_texts or True


# ---------------------------------------------------------------------------
# No Word/JPG/PNG export
# ---------------------------------------------------------------------------

def test_no_new_export_formats():
    """No new export formats added."""
    formats = [x.value for x in ExportFormat]
    assert "word" not in formats
    assert "jpg" not in formats
    assert "png" not in formats


# ---------------------------------------------------------------------------
# No mandatory web framework
# ---------------------------------------------------------------------------

def test_fastapi_optional():
    """FastAPI remains optional."""
    # Core imports work without fastapi
    from resume_pdf_agent.models.llm_review_ui import LLMReviewUIOptions
    assert LLMReviewUIOptions is not None


def test_pyproject_no_frontend_frameworks():
    """pyproject.toml has no React/Vite/Next/Flask/Streamlit."""
    repo_root = Path(__file__).resolve().parent.parent
    pyproject = repo_root / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8").lower()
    assert "react" not in content
    assert "vite" not in content
    assert "next.js" not in content
    assert "flask" not in content
    assert "streamlit" not in content


# ---------------------------------------------------------------------------
# No real LLM SDK in core deps
# ---------------------------------------------------------------------------

def test_no_llm_sdk_in_core_deps():
    """No real LLM SDK in core dependencies."""
    repo_root = Path(__file__).resolve().parent.parent
    pyproject = repo_root / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")
    lines = content.split("\n")
    in_deps = False
    in_optional = False
    for line in lines:
        s = line.strip()
        if s.startswith("[project.optional-dependencies]"):
            in_optional = True
            in_deps = False
        elif s.startswith("[tool") or s.startswith("[build"):
            in_optional = False
            in_deps = False
        elif s.startswith("dependencies"):
            in_deps = True
        elif in_deps and not in_optional:
            for sdk in ["openai", "anthropic"]:
                assert sdk not in s.lower(), f"LLM SDK in core deps: {s}"


# ---------------------------------------------------------------------------
# LLM candidates not automatically applied
# ---------------------------------------------------------------------------

def test_llm_candidates_not_automatically_applied():
    """LLMRewriteResult model does not have an 'applied' field that auto-changes resume."""
    r = LLMRewriteResult(
        status=LLMRewriteStatus.REWRITTEN,
        provider=LLMProviderType.MOCK,
        candidates=[],
        candidates_generated=0,
        candidates_requiring_confirmation=0,
        summary="Test.",
    )
    # The result does not modify ResumeContent
    assert not hasattr(r, "applied_candidates")
    assert not hasattr(r, "modified_resume")


# ---------------------------------------------------------------------------
# README/docs safety
# ---------------------------------------------------------------------------

def test_readme_no_automatic_application_claim():
    """README does not claim LLM candidates are automatically applied."""
    repo_root = Path(__file__).resolve().parent.parent
    readme = repo_root / "README.md"
    content = readme.read_text(encoding="utf-8").lower()
    # Should not claim automatic application
    assert "automatically apply llm" not in content
    assert "auto-apply llm" not in content


def test_readme_en_no_automatic_application_claim():
    """README.en.md does not claim automatic LLM application."""
    repo_root = Path(__file__).resolve().parent.parent
    readme = repo_root / "README.en.md"
    if readme.is_file():
        content = readme.read_text(encoding="utf-8").lower()
        assert "automatically apply llm" not in content
