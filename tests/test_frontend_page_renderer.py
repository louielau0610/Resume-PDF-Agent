"""Tests for the M11 frontend page renderer."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.models.frontend import (
    FrontendPageOptions,
    FrontendPageResult,
    FrontendPageStatus,
)
from resume_pdf_agent.models.workflow import ResumeWorkflowInput
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.frontend import render_frontend_workflow_page
from resume_pdf_agent.workflow import run_resume_workflow


def test_render_frontend_workflow_page_can_be_imported():
    """render_frontend_workflow_page is importable."""
    assert callable(render_frontend_workflow_page)


def test_render_frontend_workflow_page_writes_index_html(tmp_path: Path):
    """Renders an index.html file at the output path."""
    output_dir = tmp_path / "outputs" / "page_test"
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

    assert page_result.status in (
        FrontendPageStatus.RENDERED,
        FrontendPageStatus.RENDERED_WITH_WARNINGS,
    )
    assert (output_dir / "index.html").is_file()
    assert page_result.output_path is not None


def test_rendered_page_contains_workflow_status(tmp_path: Path):
    """Rendered page HTML contains workflow status."""
    output_dir = tmp_path / "outputs" / "status_check"
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

    html = page_result.html
    assert "Workflow Status" in html
    assert result.status.value in html.lower()


def test_rendered_page_contains_criteria_profile_id(tmp_path: Path):
    """Rendered page contains selected criteria profile id."""
    output_dir = tmp_path / "outputs" / "cp_check"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        target_role="Data Science Intern",
        output_dir=str(output_dir),
    )
    result = run_resume_workflow(workflow_input)

    page_result = render_frontend_workflow_page(
        workflow_input=workflow_input,
        workflow_result=result,
        output_path=output_dir / "index.html",
    )

    html = page_result.html
    assert result.selected_criteria_profile_id in html


def test_rendered_page_contains_primary_resume_type(tmp_path: Path):
    """Rendered page contains primary resume type."""
    output_dir = tmp_path / "outputs" / "rt_check"
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

    html = page_result.html
    assert result.primary_resume_type.value in html.lower()


def test_rendered_page_contains_selected_template_id(tmp_path: Path):
    """Rendered page contains selected template id."""
    output_dir = tmp_path / "outputs" / "tmpl_check"
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

    html = page_result.html
    assert result.selected_template_id in html


def test_rendered_page_contains_stage_timeline(tmp_path: Path):
    """Rendered page contains stage timeline section."""
    output_dir = tmp_path / "outputs" / "timeline_check"
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

    html = page_result.html
    assert "Stage Timeline" in html


def test_rendered_page_links_to_resume_html(tmp_path: Path):
    """Rendered page links to resume.html when available."""
    output_dir = tmp_path / "outputs" / "link_check"
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

    html = page_result.html
    assert "resume.html" in html


def test_rendered_page_links_to_resume_pdf(tmp_path: Path):
    """Rendered page links to resume.pdf when available."""
    output_dir = tmp_path / "outputs" / "pdf_link"
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

    html = page_result.html
    assert "resume.pdf" in html


def test_rendered_page_contains_conversion_reminder(tmp_path: Path):
    """Rendered page includes conversion reminder outside resume body."""
    output_dir = tmp_path / "outputs" / "cr_check"
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

    html = page_result.html
    assert "Format Conversion" in html
    # The reminder is in the dashboard, not the resume body


def test_rendered_page_escapes_malicious_text(tmp_path: Path):
    """Rendered page escapes <script> from user input."""
    output_dir = tmp_path / "outputs" / "xss_check"
    profile = SAMPLE_USER_PROFILE.model_copy(deep=True)
    profile.full_name = "<script>alert('xss')</script>"

    workflow_input = ResumeWorkflowInput(
        user_profile=profile,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
    )
    result = run_resume_workflow(workflow_input)

    page_result = render_frontend_workflow_page(
        workflow_input=workflow_input,
        workflow_result=result,
        output_path=output_dir / "index.html",
    )

    html = page_result.html
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html


def test_rendered_page_creates_parent_dirs(tmp_path: Path):
    """Page renderer creates parent directories as needed."""
    output_dir = tmp_path / "outputs" / "deep" / "nested"
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

    assert (output_dir / "index.html").is_file()
    assert page_result.output_path is not None
