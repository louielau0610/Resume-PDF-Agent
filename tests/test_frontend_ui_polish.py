"""Tests for M12 frontend UI polish."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.models.workflow import ResumeWorkflowInput
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.frontend import render_frontend_workflow_page
from resume_pdf_agent.workflow import run_resume_workflow


def test_rendered_page_contains_app_shell(tmp_path: Path):
    """Polished page uses app-shell class."""
    output_dir = tmp_path / "outputs" / "shell_test"
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
    assert "app-shell" in page_result.html


def test_rendered_page_contains_hero_panel(tmp_path: Path):
    """Polished page uses hero-panel class."""
    output_dir = tmp_path / "outputs" / "hero_test"
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
    assert "hero-panel" in page_result.html


def test_rendered_page_contains_metric_grid(tmp_path: Path):
    """Polished page uses metric-grid class."""
    output_dir = tmp_path / "outputs" / "metric_test"
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
    assert "metric-grid" in page_result.html


def test_rendered_page_contains_stage_timeline(tmp_path: Path):
    """Polished page uses stage-timeline class."""
    output_dir = tmp_path / "outputs" / "stage_test"
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
    assert "stage-timeline" in page_result.html


def test_rendered_page_contains_section_panel(tmp_path: Path):
    """Polished page uses section-panel class."""
    output_dir = tmp_path / "outputs" / "panel_test"
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
    assert "section-panel" in page_result.html


def test_rendered_page_contains_artifact_panel(tmp_path: Path):
    """Polished page uses artifact-grid for artifacts."""
    output_dir = tmp_path / "outputs" / "art_test"
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
    assert "artifact-button" in page_result.html


def test_rendered_page_contains_resume_intelligence_console(tmp_path: Path):
    """Polished page shows 'Resume Intelligence Console' title."""
    output_dir = tmp_path / "outputs" / "title_test"
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
    assert "Resume Intelligence Console" in page_result.html


def test_rendered_page_has_dark_background_css(tmp_path: Path):
    """Polished CSS includes dark background colors."""
    output_dir = tmp_path / "outputs" / "dark_test"
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
    # The CSS should define dark background variables
    assert "--bg-deep" in html
    assert "0a0a0c" in html


def test_rendered_page_contains_pill_styles(tmp_path: Path):
    """Polished page uses pill styles for status indicators."""
    output_dir = tmp_path / "outputs" / "pill_test"
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
    assert "pill-" in page_result.html


def test_rendered_page_contains_footer_note(tmp_path: Path):
    """Polished page uses footer-note class."""
    output_dir = tmp_path / "outputs" / "footer_test"
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
    assert "footer-note" in page_result.html


def test_rendered_page_no_old_wf_prefix_classes(tmp_path: Path):
    """Polished page does NOT use old wf-* class names."""
    output_dir = tmp_path / "outputs" / "nolegacy_test"
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
    # Old M11 classes should not appear
    assert "wf-header" not in page_result.html
    assert "wf-status-banner" not in page_result.html
    assert "wf-summary-cards" not in page_result.html
    assert "wf-footer" not in page_result.html
