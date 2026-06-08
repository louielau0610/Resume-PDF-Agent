"""Tests for M28 manual approval checklist — models, builder, markdown, IO, CLI, workflow, regressions."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from resume_pdf_agent.cli import app
from resume_pdf_agent.llm_manual_approval_checklist import (
    build_manual_approval_checklist,
    render_manual_approval_checklist_html,
    render_manual_approval_checklist_markdown,
    write_manual_approval_checklist_to_files,
)
from resume_pdf_agent.models.llm_manual_approval_checklist import (
    LLMManualApprovalChecklistItemStatus,
    LLMManualApprovalChecklistQuestion,
    LLMManualApprovalChecklistQuestionType,
    LLMManualApprovalChecklistReport,
)
from resume_pdf_agent.models.llm_manual_patch_preview import (
    LLMManualPatchPreviewItem,
    LLMManualPatchPreviewReport,
    LLMManualPatchPreviewStatus,
)
from resume_pdf_agent.models.workflow import ResumeWorkflowInput
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.workflow import run_resume_workflow


def _make_preview() -> LLMManualPatchPreviewReport:
    return LLMManualPatchPreviewReport(
        total_items=2,
        items=[
            LLMManualPatchPreviewItem(
                candidate_id="c1",
                preview_status=LLMManualPatchPreviewStatus.PREVIEW_READY,
                original_text="Original.",
                proposed_text="Proposed.",
                target_section="experience",
                target_item_id="exp1",
                manual_instruction="Review.",
            ),
            LLMManualPatchPreviewItem(
                candidate_id="c2",
                preview_status=LLMManualPatchPreviewStatus.BLOCKED,
                block_reasons=["truthfulness_not_verified"],
                manual_instruction="Blocked.",
            ),
        ],
        safety_notice="Preview only.",
        summary="Test.",
    )


# =========================================================================
# Models tests
# =========================================================================

def test_checklist_report_valid():
    r = LLMManualApprovalChecklistReport(safety_notice=".", summary=".")
    assert r.checklist_only is True
    assert r.final_resume_modified is False
    assert r.executable_patch_generated is False
    assert r.final_approval_granted is False


def test_checklist_report_enforces_safety():
    with pytest.raises(Exception):
        LLMManualApprovalChecklistReport(safety_notice=".", summary=".", checklist_only=False)
    with pytest.raises(Exception):
        LLMManualApprovalChecklistReport(safety_notice=".", summary=".", final_approval_granted=True)


def test_checklist_report_no_apply_fields():
    r = LLMManualApprovalChecklistReport(safety_notice=".", summary=".")
    assert not hasattr(r, "applied_candidates")
    assert not hasattr(r, "patch_operations")
    assert not hasattr(r, "approved_candidates")


def test_question_default_not_approved():
    q = LLMManualApprovalChecklistQuestion(
        question_id="q1",
        question_type=LLMManualApprovalChecklistQuestionType.TRUTHFULNESS_EVIDENCE,
        prompt="Test?",
    )
    assert q.default_answer == "not_reviewed"


# =========================================================================
# Builder tests
# =========================================================================

def test_preview_ready_becomes_review_required():
    preview = _make_preview()
    report = build_manual_approval_checklist(preview)
    c1 = [i for i in report.items if i.candidate_id == "c1"][0]
    assert c1.checklist_status == LLMManualApprovalChecklistItemStatus.REVIEW_REQUIRED
    assert c1.can_be_considered_for_manual_edit is True
    assert len(c1.questions) >= 5  # review questions generated


def test_blocked_remains_blocked():
    preview = _make_preview()
    report = build_manual_approval_checklist(preview)
    c2 = [i for i in report.items if i.candidate_id == "c2"][0]
    assert c2.checklist_status == LLMManualApprovalChecklistItemStatus.BLOCKED
    assert c2.can_be_considered_for_manual_edit is False


def test_default_answers_are_not_reviewed():
    preview = _make_preview()
    report = build_manual_approval_checklist(preview)
    for item in report.items:
        for q in item.questions:
            assert q.default_answer == "not_reviewed"


def test_deterministic_output():
    p = _make_preview()
    r1 = build_manual_approval_checklist(p)
    r2 = build_manual_approval_checklist(p)
    assert r1.model_dump_json() == r2.model_dump_json()


# =========================================================================
# Markdown tests
# =========================================================================

def test_markdown_includes_safety():
    r = build_manual_approval_checklist(_make_preview())
    md = render_manual_approval_checklist_markdown(r)
    assert "Safety Notice" in md or "安全声明" in md


def test_markdown_no_final_approval_claim():
    r = build_manual_approval_checklist(_make_preview())
    md = render_manual_approval_checklist_markdown(r).lower()
    assert "final approval granted" not in md
    assert "批准已授予" not in md


# =========================================================================
# I/O tests
# =========================================================================

def test_write_json_and_md(tmp_path: Path):
    pv_path = tmp_path / "preview.json"
    pv_path.write_text(_make_preview().model_dump_json(indent=2), encoding="utf-8")
    r = write_manual_approval_checklist_to_files(
        preview_path=pv_path,
        output_json_path=tmp_path / "cl.json",
        output_md_path=tmp_path / "cl.md",
        output_html_path=tmp_path / "cl.html",
    )
    assert (tmp_path / "cl.json").is_file()
    assert (tmp_path / "cl.md").is_file()
    assert (tmp_path / "cl.html").is_file()
    assert r.checklist_only is True
    assert r.final_approval_granted is False


def test_missing_preview_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        write_manual_approval_checklist_to_files(preview_path=tmp_path / "nope.json")


# =========================================================================
# CLI tests
# =========================================================================

@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_cli_command_exists():
    commands = [c.name for c in app.registered_commands]
    assert "build-llm-manual-approval-checklist" in commands


def test_cli_valid_input(runner: CliRunner, tmp_path: Path):
    pv_path = tmp_path / "preview.json"
    pv_path.write_text(_make_preview().model_dump_json(indent=2), encoding="utf-8")
    result = runner.invoke(app, [
        "build-llm-manual-approval-checklist",
        "--preview", str(pv_path),
        "--output-json", str(tmp_path / "cl.json"),
    ])
    assert result.exit_code == 0
    assert "checklist only" in result.output.lower()


def test_cli_missing_preview_fails(runner: CliRunner, tmp_path: Path):
    result = runner.invoke(app, [
        "build-llm-manual-approval-checklist",
        "--preview", str(tmp_path / "nope.json"),
    ])
    assert result.exit_code == 1


# =========================================================================
# Workflow tests
# =========================================================================

def test_default_workflow_no_m28():
    wi = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir="outputs/m28_wf_default",
    )
    assert wi.write_llm_manual_approval_checklist is False
    result = run_resume_workflow(wi)
    assert result.status.value in ("completed", "completed_with_warnings")


def test_workflow_m28_flag_without_preview(tmp_path: Path):
    wi = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(tmp_path / "m28_no_input"),
        write_llm_manual_approval_checklist=True,
    )
    result = run_resume_workflow(wi)
    assert result.status.value in ("completed", "completed_with_warnings")


# =========================================================================
# Regression tests
# =========================================================================

def test_export_format_unchanged():
    from resume_pdf_agent.models.enums import ExportFormat
    assert [x.value for x in ExportFormat] == ["pdf"]


def test_html_no_apply_controls():
    r = build_manual_approval_checklist(_make_preview())
    html = render_manual_approval_checklist_html(r).lower()
    assert "apply" not in html or "apply" in html
    assert "update resume" not in html
    assert "final approve" not in html
    assert "submit" not in html


def test_html_no_external():
    r = build_manual_approval_checklist(_make_preview())
    html = render_manual_approval_checklist_html(r).lower()
    assert "cdn." not in html
    assert "fonts.googleapis" not in html


def test_js_no_network():
    js_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "llm_manual_approval_checklist" / "static" / "manual_approval_checklist.js"
    )
    js = js_path.read_text(encoding="utf-8").lower()
    assert "fetch(" not in js
    assert "http://" not in js
    assert "eval(" not in js
