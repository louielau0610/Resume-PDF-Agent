"""Tests for the M11 frontend context builder."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.models.frontend import FrontendPageOptions
from resume_pdf_agent.models.workflow import ResumeWorkflowInput
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.frontend.context import build_frontend_page_context
from resume_pdf_agent.workflow import run_resume_workflow


def test_build_frontend_page_context_can_be_imported():
    """build_frontend_page_context is importable."""
    assert callable(build_frontend_page_context)


def test_build_frontend_page_context_returns_dict(tmp_path: Path):
    """Context builder returns a dict with expected keys."""
    output_dir = tmp_path / "outputs" / "ctx_test"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
    )
    result = run_resume_workflow(workflow_input)

    ctx = build_frontend_page_context(workflow_input, result)
    assert isinstance(ctx, dict)
    assert "page_title" in ctx
    assert "status" in ctx
    assert "stage_views" in ctx
    assert "warnings" in ctx
    assert "errors" in ctx


def test_context_contains_workflow_status(tmp_path: Path):
    """Context contains the workflow status string."""
    output_dir = tmp_path / "outputs" / "status_test"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
    )
    result = run_resume_workflow(workflow_input)

    ctx = build_frontend_page_context(workflow_input, result)
    assert ctx["status"] in ("completed", "completed_with_warnings")


def test_context_contains_criteria_profile_id(tmp_path: Path):
    """Context contains the selected criteria profile id."""
    output_dir = tmp_path / "outputs" / "cp_test"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
    )
    result = run_resume_workflow(workflow_input)

    ctx = build_frontend_page_context(workflow_input, result)
    assert ctx["selected_criteria_profile_id"] is not None
    assert len(ctx["selected_criteria_profile_id"]) > 0


def test_context_contains_primary_resume_type(tmp_path: Path):
    """Context contains the primary resume type."""
    output_dir = tmp_path / "outputs" / "rt_test"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
    )
    result = run_resume_workflow(workflow_input)

    ctx = build_frontend_page_context(workflow_input, result)
    assert ctx["primary_resume_type"] is not None
    assert len(ctx["primary_resume_type"]) > 0


def test_context_contains_template_id(tmp_path: Path):
    """Context contains the selected template id."""
    output_dir = tmp_path / "outputs" / "tmpl_test"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
    )
    result = run_resume_workflow(workflow_input)

    ctx = build_frontend_page_context(workflow_input, result)
    assert ctx["selected_template_id"] is not None
    assert len(ctx["selected_template_id"]) > 0


def test_context_contains_stage_views(tmp_path: Path):
    """Context contains stage timeline views."""
    output_dir = tmp_path / "outputs" / "stages_test"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
    )
    result = run_resume_workflow(workflow_input)

    ctx = build_frontend_page_context(workflow_input, result)
    assert len(ctx["stage_views"]) > 0
    for sv in ctx["stage_views"]:
        assert "stage" in sv
        assert "status" in sv
        assert "message" in sv


def test_context_escapes_malicious_text(tmp_path: Path):
    """Context escapes <script> tags in user-supplied values."""
    output_dir = tmp_path / "outputs" / "xss_test"
    profile = SAMPLE_USER_PROFILE.model_copy(deep=True)
    profile.full_name = "<script>alert('xss')</script>"

    workflow_input = ResumeWorkflowInput(
        user_profile=profile,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
    )
    result = run_resume_workflow(workflow_input)

    ctx = build_frontend_page_context(workflow_input, result)
    # The full_name should be escaped
    name_in_context = ctx["input_summary"]["full_name"]
    assert "<script>" not in name_in_context
    assert "&lt;" in name_in_context


def test_context_has_conversion_reminder(tmp_path: Path):
    """Context includes conversion reminder when available."""
    output_dir = tmp_path / "outputs" / "reminder_test"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
    )
    result = run_resume_workflow(workflow_input)

    ctx = build_frontend_page_context(workflow_input, result)
    reminder = ctx.get("conversion_reminder", "")
    # Conversion reminder should exist (even if empty string when PDF wasn't generated)
    assert "conversion_reminder" in ctx


def test_context_has_input_summary(tmp_path: Path):
    """Context contains input summary with expected counts."""
    output_dir = tmp_path / "outputs" / "input_test"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
    )
    result = run_resume_workflow(workflow_input)

    ctx = build_frontend_page_context(workflow_input, result)
    summary = ctx["input_summary"]
    assert summary["education_count"] == 1
    assert summary["experience_count"] == 2
    assert summary["skill_group_count"] == 3
    assert summary["full_name"] == "Alex Chen"
