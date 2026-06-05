"""Regression tests for M11 frontend workflow page."""

from __future__ import annotations

from pathlib import Path

import pytest

from resume_pdf_agent.models import ExportFormat
from resume_pdf_agent.models.frontend import (
    FrontendPageOptions,
    FrontendPageResult,
    FrontendPageStatus,
)
from resume_pdf_agent.models.workflow import ResumeWorkflowInput
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.frontend import render_frontend_workflow_page
from resume_pdf_agent.workflow import run_resume_workflow


def test_frontend_page_does_not_mention_hiring_probability(tmp_path: Path):
    """Frontend page does not mention hiring probability."""
    output_dir = tmp_path / "outputs" / "hp_check"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
    )
    result = run_resume_workflow(workflow_input)

    page_result = render_frontend_workflow_page(
        workflow_input=workflow_input,
        workflow_result=result,
        output_path=output_dir / "index.html",
    )

    html = page_result.html.lower()
    assert "hiring probability" not in html
    assert "offer probability" not in html
    assert "interview probability" not in html


def test_frontend_page_does_not_claim_internal_screening(tmp_path: Path):
    """Frontend page does not claim internal company screening access."""
    output_dir = tmp_path / "outputs" / "is_check"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
    )
    result = run_resume_workflow(workflow_input)

    page_result = render_frontend_workflow_page(
        workflow_input=workflow_input,
        workflow_result=result,
        output_path=output_dir / "index.html",
    )

    html = page_result.html.lower()
    assert "internal screening" not in html
    assert "internal company" not in html


def test_frontend_page_does_not_implement_web_server():
    """Frontend module does not start a web server."""
    import inspect
    from resume_pdf_agent.frontend import page_renderer

    source = inspect.getsource(page_renderer)
    server_indicators = ["run(", "app.run", "uvicorn", "fastapi", "flask", "streamlit"]
    source_lower = source.lower()
    for indicator in server_indicators:
        assert indicator not in source_lower, (
            f"Server indicator '{indicator}' found in page renderer"
        )


def test_frontend_does_not_add_react_or_fastapi_deps():
    """Frontend module does not import React/FastAPI/Streamlit."""
    import inspect
    from resume_pdf_agent.frontend import page_renderer
    from resume_pdf_agent.frontend import context

    for mod in (page_renderer, context):
        source = inspect.getsource(mod).lower()
        for dep in ["react", "fastapi", "flask", "streamlit", "vite"]:
            assert f"import {dep}" not in source, f"'{dep}' import in {mod.__name__}"
            assert f"from {dep}" not in source, f"'{dep}' from in {mod.__name__}"


def test_frontend_page_does_not_use_external_cdn():
    """Frontend CSS/JS do not reference external CDN URLs."""
    frontend_dir = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "resume_pdf_agent"
        / "frontend"
        / "static"
    )
    css = (frontend_dir / "frontend_basic.css").read_text(encoding="utf-8")
    js = (frontend_dir / "frontend_basic.js").read_text(encoding="utf-8")

    for content in [css, js]:
        assert "http://" not in content
        assert "https://" not in content
        assert "cdn." not in content


def test_no_word_jpg_png_generated_by_frontend(tmp_path: Path):
    """Frontend page does not generate Word/JPG/PNG files."""
    output_dir = tmp_path / "outputs" / "format_check"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
    )
    result = run_resume_workflow(workflow_input)

    render_frontend_workflow_page(
        workflow_input=workflow_input,
        workflow_result=result,
        output_path=output_dir / "index.html",
    )

    disallowed = {".doc", ".docx", ".jpg", ".jpeg", ".png"}
    for ext in disallowed:
        matches = list(output_dir.glob(f"**/*{ext}"))
        assert not matches, f"Found disallowed file with extension {ext}"


def test_export_format_still_only_pdf():
    """ExportFormat still only includes pdf."""
    assert ExportFormat.PDF == "pdf"
    assert len(ExportFormat.__members__) == 1


def test_frontend_page_result_validation():
    """FrontendPageResult validates correctly."""
    # Valid
    result = FrontendPageResult(
        status=FrontendPageStatus.RENDERED,
        output_path="/tmp/index.html",
        html="<html></html>",
        summary="OK",
    )
    assert result.status == FrontendPageStatus.RENDERED

    # Invalid: html empty when rendered
    with pytest.raises(ValueError):
        FrontendPageResult(
            status=FrontendPageStatus.RENDERED,
            output_path="/tmp/index.html",
            html="",
            summary="Bad",
        )

    # Invalid: output_path missing when rendered
    with pytest.raises(ValueError):
        FrontendPageResult(
            status=FrontendPageStatus.RENDERED,
            output_path=None,
            html="<html></html>",
            summary="Bad",
        )

    # Invalid: summary empty
    with pytest.raises(ValueError):
        FrontendPageResult(
            status=FrontendPageStatus.RENDERED,
            output_path="/tmp/index.html",
            html="<html></html>",
            summary="",
        )


def test_frontend_artifact_link_path_not_empty():
    """FrontendArtifactLink requires non-empty path."""
    from resume_pdf_agent.models.frontend import FrontendArtifactLink

    with pytest.raises(ValueError):
        FrontendArtifactLink(label="test", path="", artifact_type="json")


def test_frontend_stage_view_message_not_empty():
    """FrontendStageView requires non-empty message."""
    from resume_pdf_agent.models.frontend import FrontendStageView

    with pytest.raises(ValueError):
        FrontendStageView(stage="test", status="completed", message="")


def test_no_llm_api_calls_in_frontend():
    """Frontend module does not call LLM APIs."""
    import inspect
    from resume_pdf_agent.frontend import page_renderer
    from resume_pdf_agent.frontend import context as ctx_mod
    from resume_pdf_agent.frontend import safety

    for mod in (page_renderer, ctx_mod, safety):
        source = inspect.getsource(mod).lower()
        llm_indicators = ["openai", "anthropic", "gemini", "deepseek", "chatgpt"]
        for indicator in llm_indicators:
            assert indicator not in source, f"'{indicator}' in {mod.__name__}"
