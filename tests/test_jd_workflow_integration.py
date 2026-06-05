"""Tests for M15 JD workflow integration."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.workflow.io import load_workflow_input_from_json
from resume_pdf_agent.workflow.orchestrator import run_resume_workflow

_SAMPLE_INPUT = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "sample_inputs"
    / "sample_data_science_user.json"
)
_SAMPLE_JD = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "sample_inputs"
    / "sample_data_science_jd.txt"
)


class TestWorkflowWithJd:

    def test_workflow_with_jd_uses_jd_criteria(self, tmp_path):
        """Workflow with JD should use JD-derived criteria."""
        inp = load_workflow_input_from_json(_SAMPLE_INPUT)
        inp.output_dir = str(tmp_path / "output")
        inp.use_user_provided_jd = True
        inp.jd_file_path = str(_SAMPLE_JD)

        result = run_resume_workflow(inp)
        assert result.used_user_provided_jd is True
        assert result.jd_compliance_status == "allowed"

    def test_workflow_without_jd_preserves_static_behavior(self, tmp_path):
        """Without JD, existing static criteria behavior is preserved."""
        inp = load_workflow_input_from_json(_SAMPLE_INPUT)
        inp.output_dir = str(tmp_path / "output")

        result = run_resume_workflow(inp)
        assert result.used_user_provided_jd is False
        assert result.pdf_output_path is not None

    def test_workflow_writes_parsed_jd(self, tmp_path):
        """JD artifacts should be written when enabled."""
        inp = load_workflow_input_from_json(_SAMPLE_INPUT)
        inp.output_dir = str(tmp_path / "output")
        inp.use_user_provided_jd = True
        inp.jd_file_path = str(_SAMPLE_JD)
        inp.write_jd_artifacts = True
        inp.write_intermediate_json = True

        result = run_resume_workflow(inp)
        assert result.parsed_jd_path is not None
        assert Path(result.parsed_jd_path).is_file()

    def test_workflow_writes_jd_criteria_profile(self, tmp_path):
        """JD criteria profile should be written."""
        inp = load_workflow_input_from_json(_SAMPLE_INPUT)
        inp.output_dir = str(tmp_path / "output")
        inp.use_user_provided_jd = True
        inp.jd_file_path = str(_SAMPLE_JD)
        inp.write_jd_artifacts = True
        inp.write_intermediate_json = True

        result = run_resume_workflow(inp)
        assert result.jd_criteria_profile_path is not None
        assert Path(result.jd_criteria_profile_path).is_file()
