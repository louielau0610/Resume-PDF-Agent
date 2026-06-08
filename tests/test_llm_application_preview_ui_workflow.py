"""Workflow tests for M25 application preview UI."""

from __future__ import annotations

import json
from pathlib import Path

from resume_pdf_agent.models.llm_application_plan import (
    LLMApplicationPlanStatus,
    LLMCandidateApplicationPlan,
    LLMCandidateApplicationPlanItem,
)
from resume_pdf_agent.models.workflow import ResumeWorkflowInput
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.workflow import run_resume_workflow


def _input(output_dir: Path, **kwargs) -> ResumeWorkflowInput:
    data = dict(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
    )
    data.update(kwargs)
    return ResumeWorkflowInput(**data)


def _write_plan(path: Path) -> None:
    plan = LLMCandidateApplicationPlan(
        total_candidates=1,
        planned_count=1,
        items=[
            LLMCandidateApplicationPlanItem(
                candidate_id="c1",
                source_action="approve_candidate",
                plan_status=LLMApplicationPlanStatus.PLANNED,
                target_section="experience",
                target_item_id="exp1",
                original_text="Original.",
                candidate_text="Rewrite.",
                needs_confirmation=False,
                application_instruction="Inspect manually.",
            )
        ],
        safety_notice="Plan only; no candidates were applied.",
        summary="Plan summary.",
    )
    path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")


def test_default_workflow_produces_no_preview_ui(tmp_path: Path):
    result = run_resume_workflow(_input(tmp_path / "default"))
    assert result.llm_application_preview_ui_path is None


def test_write_preview_false_produces_no_preview_ui(tmp_path: Path):
    plan_path = tmp_path / "plan.json"
    _write_plan(plan_path)
    result = run_resume_workflow(
        _input(
            tmp_path / "off",
            llm_application_plan_json_path=str(plan_path),
            write_llm_application_preview_ui=False,
        )
    )
    assert result.llm_application_preview_ui_path is None


def test_write_preview_true_with_existing_plan_produces_preview(tmp_path: Path):
    plan_path = tmp_path / "plan.json"
    _write_plan(plan_path)
    result = run_resume_workflow(
        _input(
            tmp_path / "on",
            llm_application_plan_json_path=str(plan_path),
            write_llm_application_preview_ui=True,
        )
    )
    assert result.llm_application_preview_ui_path is not None
    assert Path(result.llm_application_preview_ui_path).is_file()
    assert any(a.artifact_type == "llm_application_preview_ui" for a in result.artifacts)


def test_missing_plan_warns_and_continues(tmp_path: Path):
    result = run_resume_workflow(
        _input(tmp_path / "missing", write_llm_application_preview_ui=True)
    )
    assert result.status.value in ("completed", "completed_with_warnings")
    assert result.llm_application_preview_ui_path is None
    assert any("no LLM application plan JSON" in w for w in result.warnings)


def test_preview_does_not_change_resume_artifacts(tmp_path: Path):
    plan_path = tmp_path / "plan.json"
    _write_plan(plan_path)
    base = run_resume_workflow(_input(tmp_path / "base"))
    preview = run_resume_workflow(
        _input(
            tmp_path / "preview",
            llm_application_plan_json_path=str(plan_path),
            write_llm_application_preview_ui=True,
        )
    )
    assert Path(base.html_output_path or "").read_text(encoding="utf-8") == Path(
        preview.html_output_path or ""
    ).read_text(encoding="utf-8")
    assert Path(preview.pdf_output_path or "").read_bytes().startswith(b"%PDF")


def test_workflow_input_json_fields_are_supported(tmp_path: Path):
    from resume_pdf_agent.workflow.io import load_workflow_input_from_json

    plan_path = tmp_path / "plan.json"
    input_path = tmp_path / "input.json"
    _write_plan(plan_path)
    input_path.write_text(
        json.dumps(
            {
                "user_profile": SAMPLE_USER_PROFILE.model_dump(mode="json"),
                "resume_content": SAMPLE_RESUME_CONTENT.model_dump(mode="json"),
                "output_dir": str(tmp_path / "json_input"),
                "llm_application_plan_json_path": str(plan_path),
                "write_llm_application_preview_ui": True,
            }
        ),
        encoding="utf-8",
    )
    loaded = load_workflow_input_from_json(input_path)
    assert loaded.write_llm_application_preview_ui is True
    assert loaded.llm_application_plan_json_path == str(plan_path)
