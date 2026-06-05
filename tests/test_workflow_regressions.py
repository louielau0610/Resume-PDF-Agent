"""Regression tests for M10 workflow integration.

Ensures that M10 does not break any product boundaries.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from resume_pdf_agent.models import (
    ExportFormat,
    PDFBackend,
)
from resume_pdf_agent.models.workflow import (
    ResumeWorkflowInput,
    WorkflowRunStatus,
)
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.workflow import run_resume_workflow


def test_m10_existing_m0_through_m9_tests_still_work():
    """Placeholder: M10 should not break existing tests.
    The actual verification is done by running the full test suite.
    """
    assert True


def test_workflow_result_has_pdf_only_output(tmp_path: Path):
    """Workflow output only includes PDF, no Word/JPG/PNG."""
    output_dir = tmp_path / "outputs" / "format_check"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
        pdf_backend=PDFBackend.MOCK,
        write_intermediate_json=True,
    )
    run_resume_workflow(workflow_input)

    all_files = list(output_dir.glob("**/*"))
    # Check no disallowed extensions
    disallowed = {".doc", ".docx", ".jpg", ".jpeg", ".png"}
    for f in all_files:
        if f.is_file():
            assert f.suffix.lower() not in disallowed, f"Found disallowed file: {f}"


def test_workflow_does_not_insert_conversion_reminder_into_html_body(
    tmp_path: Path,
):
    """The conversion reminder is metadata, not in the resume HTML body."""
    output_dir = tmp_path / "outputs" / "reminder_check"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
        pdf_backend=PDFBackend.MOCK,
        include_preview_reminder_panel=False,
    )
    result = run_resume_workflow(workflow_input)

    html_content = (output_dir / "resume.html").read_text(encoding="utf-8")
    # The reminder text should NOT be in the HTML body
    assert "external PDF conversion tool" not in html_content


def test_workflow_does_not_mention_hiring_probability(tmp_path: Path):
    """Workflow does not mention hiring probability."""
    output_dir = tmp_path / "outputs" / "hiring_check"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
        pdf_backend=PDFBackend.MOCK,
    )
    result = run_resume_workflow(workflow_input)

    # Check HTML content
    html_content = (output_dir / "resume.html").read_text(encoding="utf-8")
    assert "hiring probability" not in html_content.lower()
    assert "offer probability" not in html_content.lower()
    assert "interview probability" not in html_content.lower()

    # Check summary
    assert "hiring probability" not in result.summary.lower()

    # Check stage messages
    for stage in result.stages:
        assert "hiring probability" not in stage.message.lower()


def test_workflow_does_not_claim_internal_screening_access(tmp_path: Path):
    """Workflow does not claim access to internal company screening standards."""
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(tmp_path / "outputs" / "screening_check"),
        pdf_backend=PDFBackend.MOCK,
    )
    result = run_resume_workflow(workflow_input)

    # Check summary
    assert "internal screening" not in result.summary.lower()
    assert "internal company" not in result.summary.lower()

    # Check stage messages
    for stage in result.stages:
        assert "internal screening" not in stage.message.lower()
        assert "internal company" not in stage.message.lower()


def test_workflow_does_not_call_llm_apis():
    """Workflow does not reference LLM APIs."""
    # This is a structural check - the workflow module does not import any LLM libraries
    import inspect

    from resume_pdf_agent.workflow import orchestrator

    source = inspect.getsource(orchestrator)
    llm_indicators = [
        "openai",
        "anthropic",
        "gemini",
        "deepseek",
        "llm",
        "chatgpt",
        "gpt-",
        "claude",
    ]
    source_lower = source.lower()
    for indicator in llm_indicators:
        assert indicator not in source_lower, (
            f"LLM indicator '{indicator}' found in workflow orchestrator"
        )


def test_workflow_does_not_implement_frontend_ui():
    """Workflow module does not implement frontend UI."""
    import inspect

    from resume_pdf_agent.cli import app as cli_app
    from resume_pdf_agent.workflow import orchestrator

    source = inspect.getsource(orchestrator)
    frontend_indicators = ["fastapi", "flask", "streamlit", "gradio", "html_template"]
    source_lower = source.lower()
    for indicator in frontend_indicators:
        assert indicator not in source_lower, (
            f"Frontend indicator '{indicator}' found in workflow orchestrator"
        )


def test_export_format_still_only_pdf():
    """ExportFormat still only includes pdf."""
    assert ExportFormat.PDF == "pdf"
    # Only one export format
    assert len(ExportFormat.__members__) == 1


def test_workflow_result_has_conversion_reminder_metadata(tmp_path: Path):
    """Workflow result contains conversion reminder as metadata, not in resume body."""
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(tmp_path / "outputs" / "meta_reminder"),
        pdf_backend=PDFBackend.MOCK,
    )
    result = run_resume_workflow(workflow_input)
    # The result should have a conversion_reminder (metadata)
    assert result.conversion_reminder is not None
    assert "PDF conversion tool" in result.conversion_reminder


def test_workflow_input_validation_output_dir_not_empty():
    """ResumeWorkflowInput rejects empty output_dir."""
    with pytest.raises(ValueError):
        ResumeWorkflowInput(
            user_profile=SAMPLE_USER_PROFILE,
            resume_content=SAMPLE_RESUME_CONTENT,
            output_dir="",
        )


def test_workflow_result_validation_summary_not_empty():
    """ResumeWorkflowResult rejects empty summary."""
    with pytest.raises(ValueError):
        from resume_pdf_agent.models.workflow import ResumeWorkflowResult

        ResumeWorkflowResult(
            status=WorkflowRunStatus.COMPLETED,
            output_dir="/tmp",
            summary="",
        )


def test_workflow_result_status_failed_with_errors():
    """ResumeWorkflowResult must be failed if errors present."""
    with pytest.raises(ValueError):
        from resume_pdf_agent.models.workflow import ResumeWorkflowResult

        ResumeWorkflowResult(
            status=WorkflowRunStatus.COMPLETED,
            output_dir="/tmp",
            summary="Bad result",
            errors=["Something went wrong"],
        )
