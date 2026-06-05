"""Tests for the M10 workflow orchestrator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from resume_pdf_agent.models import (
    EvidenceLevel,
    ExperienceEntry,
    ExperienceType,
    MetricStatus,
    PDFBackend,
    ResumeBullet,
    ResumeContent,
    ResumeSection,
    ResumeType,
    UserProfile,
)
from resume_pdf_agent.models.workflow import (
    ResumeWorkflowInput,
    WorkflowRunStatus,
    WorkflowStageName,
    WorkflowStageStatus,
)
from resume_pdf_agent.sample_data import (
    SAMPLE_RESUME_CONTENT,
    SAMPLE_USER_PROFILE,
)
from resume_pdf_agent.workflow import run_resume_workflow


def test_import_run_resume_workflow():
    """run_resume_workflow can be imported."""
    assert callable(run_resume_workflow)


def test_workflow_with_sample_data_completes(tmp_path: Path):
    """Workflow with sample data and mock PDF backend completes."""
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        target_role="Data Science Intern",
        output_dir=str(tmp_path / "outputs" / "sample_run"),
        pdf_backend=PDFBackend.MOCK,
        write_intermediate_json=True,
    )
    result = run_resume_workflow(workflow_input)
    assert result.status in (
        WorkflowRunStatus.COMPLETED,
        WorkflowRunStatus.COMPLETED_WITH_WARNINGS,
    )


def test_workflow_creates_output_directory(tmp_path: Path):
    """Workflow creates the output directory."""
    output_dir = tmp_path / "outputs" / "test_run"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
        pdf_backend=PDFBackend.MOCK,
    )
    result = run_resume_workflow(workflow_input)
    assert output_dir.is_dir()
    assert result.output_dir == str(output_dir)


def test_workflow_writes_intermediate_json_artifacts(tmp_path: Path):
    """Workflow writes intermediate JSON when enabled."""
    output_dir = tmp_path / "outputs" / "json_test"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
        pdf_backend=PDFBackend.MOCK,
        write_intermediate_json=True,
    )
    run_resume_workflow(workflow_input)

    expected = [
        "criteria_profile.json",
        "classification.json",
        "gap_analysis.json",
        "truthfulness.json",
        "enhancement.json",
        "template_selection.json",
    ]
    for filename in expected:
        path = output_dir / filename
        assert path.is_file(), f"Expected {filename} to exist"
        content = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(content, (dict, list))


def test_workflow_writes_resume_html(tmp_path: Path):
    """Workflow writes resume.html."""
    output_dir = tmp_path / "outputs" / "html_test"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
        pdf_backend=PDFBackend.MOCK,
    )
    result = run_resume_workflow(workflow_input)
    html_file = output_dir / "resume.html"
    assert html_file.is_file()
    assert result.html_output_path is not None


def test_workflow_writes_resume_pdf_with_mock_backend(tmp_path: Path):
    """Workflow writes resume.pdf using mock backend."""
    output_dir = tmp_path / "outputs" / "pdf_test"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
        pdf_backend=PDFBackend.MOCK,
    )
    result = run_resume_workflow(workflow_input)
    pdf_file = output_dir / "resume.pdf"
    assert pdf_file.is_file()
    assert result.pdf_output_path is not None
    # Verify it starts with %PDF header
    content = pdf_file.read_bytes()
    assert content.startswith(b"%PDF")


def test_workflow_result_records_selected_criteria_profile_id(tmp_path: Path):
    """Workflow result records the selected criteria profile id."""
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        target_role="Data Science Intern",
        output_dir=str(tmp_path / "outputs" / "criteria_test"),
        pdf_backend=PDFBackend.MOCK,
    )
    result = run_resume_workflow(workflow_input)
    assert result.selected_criteria_profile_id is not None
    assert len(result.selected_criteria_profile_id) > 0


def test_workflow_result_records_primary_resume_type(tmp_path: Path):
    """Workflow result records the primary resume type."""
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(tmp_path / "outputs" / "type_test"),
        pdf_backend=PDFBackend.MOCK,
    )
    result = run_resume_workflow(workflow_input)
    assert result.primary_resume_type is not None
    assert isinstance(result.primary_resume_type, ResumeType)


def test_workflow_result_records_selected_template_id(tmp_path: Path):
    """Workflow result records the selected template id."""
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(tmp_path / "outputs" / "tmpl_test"),
        pdf_backend=PDFBackend.MOCK,
    )
    result = run_resume_workflow(workflow_input)
    assert result.selected_template_id is not None
    assert len(result.selected_template_id) > 0


def test_workflow_result_records_html_output_path(tmp_path: Path):
    """Workflow result records the html output path."""
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(tmp_path / "outputs" / "path_test"),
        pdf_backend=PDFBackend.MOCK,
    )
    result = run_resume_workflow(workflow_input)
    assert result.html_output_path is not None
    assert "resume.html" in result.html_output_path


def test_workflow_result_records_pdf_output_path(tmp_path: Path):
    """Workflow result records pdf output path when PDF generated."""
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(tmp_path / "outputs" / "pdfpath_test"),
        pdf_backend=PDFBackend.MOCK,
    )
    result = run_resume_workflow(workflow_input)
    assert result.pdf_output_path is not None
    assert "resume.pdf" in result.pdf_output_path


def test_workflow_does_not_generate_non_pdf_files(tmp_path: Path):
    """Workflow does not generate Word/JPG/PNG files."""
    output_dir = tmp_path / "outputs" / "format_test"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
        pdf_backend=PDFBackend.MOCK,
    )
    run_resume_workflow(workflow_input)

    forbidden_extensions = [".doc", ".docx", ".jpg", ".jpeg", ".png"]
    for ext in forbidden_extensions:
        matches = list(output_dir.glob(f"**/*{ext}"))
        assert not matches, f"Found forbidden file with extension {ext}"


def test_workflow_has_all_stages(tmp_path: Path):
    """Workflow result includes all expected stage names."""
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(tmp_path / "outputs" / "stages_test"),
        pdf_backend=PDFBackend.MOCK,
    )
    result = run_resume_workflow(workflow_input)

    stage_names = {s.stage for s in result.stages}
    expected_stages = {
        WorkflowStageName.USER_INTAKE,
        WorkflowStageName.CRITERIA_SELECTION,
        WorkflowStageName.RESUME_TYPE_CLASSIFICATION,
        WorkflowStageName.GAP_ANALYSIS,
        WorkflowStageName.TRUTHFULNESS_CHECK,
        WorkflowStageName.CRITERIA_AWARE_CONTENT_ENHANCEMENT,
        WorkflowStageName.INTERNAL_TEMPLATE_MATCHING,
        WorkflowStageName.HTML_RENDERING,
        WorkflowStageName.PDF_GENERATION,
        WorkflowStageName.ARTIFACT_WRITING,
        WorkflowStageName.REMINDER_PANEL,
    }
    assert stage_names == expected_stages


def test_workflow_with_explicit_criteria_profile_id(tmp_path: Path):
    """Workflow can use an explicit criteria_profile_id."""
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        criteria_profile_id="data_science_intern",
        output_dir=str(tmp_path / "outputs" / "explicit_test"),
        pdf_backend=PDFBackend.MOCK,
    )
    result = run_resume_workflow(workflow_input)
    assert result.selected_criteria_profile_id == "data_science_intern"
    assert result.status in (
        WorkflowRunStatus.COMPLETED,
        WorkflowRunStatus.COMPLETED_WITH_WARNINGS,
    )


def test_workflow_result_has_summary(tmp_path: Path):
    """Workflow result has a non-empty summary."""
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(tmp_path / "outputs" / "summary_test"),
        pdf_backend=PDFBackend.MOCK,
    )
    result = run_resume_workflow(workflow_input)
    assert result.summary
    assert "Workflow" in result.summary


def test_workflow_artifacts_have_deterministic_paths(tmp_path: Path):
    """All artifact paths are under the output directory."""
    output_dir = tmp_path / "outputs" / "det_test"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
        pdf_backend=PDFBackend.MOCK,
        write_intermediate_json=True,
    )
    result = run_resume_workflow(workflow_input)
    for artifact in result.artifacts:
        assert output_dir.as_posix() in Path(artifact.path).as_posix()


def test_workflow_no_intermediate_json_when_disabled(tmp_path: Path):
    """When write_intermediate_json is false, no JSON artifacts are written."""
    output_dir = tmp_path / "outputs" / "nojson_test"
    workflow_input = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
        pdf_backend=PDFBackend.MOCK,
        write_intermediate_json=False,
    )
    run_resume_workflow(workflow_input)

    # Only resume.html and resume.pdf should exist (no intermediate JSON)
    json_files = list(output_dir.glob("*.json"))
    assert len(json_files) == 0
