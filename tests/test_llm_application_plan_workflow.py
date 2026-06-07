"""Workflow integration tests for M24 application planning."""

from __future__ import annotations

import json
from pathlib import Path

from resume_pdf_agent.models.workflow import ResumeWorkflowInput
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.workflow import run_resume_workflow


def _input(output_dir: Path, **kwargs) -> ResumeWorkflowInput:
    data = dict(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
        enable_llm_rewriting=True,
        llm_provider="mock",
    )
    data.update(kwargs)
    return ResumeWorkflowInput(**data)


def _write_decisions(path: Path) -> None:
    path.write_text(
        json.dumps(
            {"decisions": [{"candidate_id": "unknown_for_workflow", "decision": "approve_candidate"}]},
            indent=2,
        ),
        encoding="utf-8",
    )


def test_default_workflow_produces_no_application_plan(tmp_path: Path):
    result = run_resume_workflow(_input(tmp_path / "default", enable_llm_rewriting=False))
    assert result.llm_application_plan_json_path is None
    assert result.llm_application_plan_md_path is None


def test_write_llm_application_plan_false_produces_no_plan(tmp_path: Path):
    decisions_path = tmp_path / "decisions.json"
    _write_decisions(decisions_path)
    result = run_resume_workflow(
        _input(
            tmp_path / "no_plan",
            llm_review_decisions_path=str(decisions_path),
            write_llm_application_plan=False,
        )
    )
    assert result.llm_application_plan_json_path is None


def test_write_llm_application_plan_true_produces_plan_if_inputs_exist(tmp_path: Path):
    decisions_path = tmp_path / "decisions.json"
    _write_decisions(decisions_path)
    result = run_resume_workflow(
        _input(
            tmp_path / "with_plan",
            llm_review_decisions_path=str(decisions_path),
            write_llm_application_plan=True,
        )
    )
    assert result.llm_application_plan_json_path is not None
    assert result.llm_application_plan_md_path is not None
    assert Path(result.llm_application_plan_json_path).is_file()
    assert Path(result.llm_application_plan_md_path).is_file()
    assert any(a.artifact_type == "llm_application_plan_json" for a in result.artifacts)


def test_missing_decisions_warns_and_continues(tmp_path: Path):
    result = run_resume_workflow(
        _input(tmp_path / "missing_decisions", write_llm_application_plan=True)
    )
    assert result.status.value in ("completed", "completed_with_warnings")
    assert result.llm_application_plan_json_path is None
    assert any("no LLM review decisions path" in w for w in result.warnings)


def test_resume_artifacts_unchanged_by_planning(tmp_path: Path):
    decisions_path = tmp_path / "decisions.json"
    _write_decisions(decisions_path)
    base = run_resume_workflow(_input(tmp_path / "base"))
    planned = run_resume_workflow(
        _input(
            tmp_path / "planned",
            llm_review_decisions_path=str(decisions_path),
            write_llm_application_plan=True,
        )
    )
    assert Path(base.html_output_path or "").read_text(encoding="utf-8") == Path(
        planned.html_output_path or ""
    ).read_text(encoding="utf-8")
    assert Path(planned.pdf_output_path or "").is_file()
