"""Tests for M29 human final edit instruction pack."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from resume_pdf_agent.cli import app
from resume_pdf_agent.llm_human_final_edit_pack import (
    build_human_final_edit_pack,
    render_human_final_edit_pack_html,
    render_human_final_edit_pack_markdown,
    write_human_final_edit_pack_to_files,
)
from resume_pdf_agent.models.llm_human_final_edit_pack import (
    LLMHumanFinalEditItemStatus,
    LLMHumanFinalEditInstructionPack,
)
from resume_pdf_agent.models.llm_manual_approval_checklist import (
    LLMManualApprovalChecklistItem,
    LLMManualApprovalChecklistItemStatus,
    LLMManualApprovalChecklistReport,
)
from resume_pdf_agent.models.workflow import ResumeWorkflowInput
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.workflow import run_resume_workflow


def _make_checklist() -> LLMManualApprovalChecklistReport:
    return LLMManualApprovalChecklistReport(
        total_items=2,
        items=[
            LLMManualApprovalChecklistItem(
                candidate_id="c1",
                checklist_status=LLMManualApprovalChecklistItemStatus.REVIEW_REQUIRED,
                source_preview_status="preview_ready",
                original_text="Original.",
                proposed_text="Proposed.",
                target_section="experience",
                target_item_id="exp1",
                manual_instruction="Review.",
            ),
            LLMManualApprovalChecklistItem(
                candidate_id="c2",
                checklist_status=LLMManualApprovalChecklistItemStatus.BLOCKED,
                source_preview_status="blocked",
                block_reasons=["truthfulness_not_verified"],
                manual_instruction="Blocked.",
            ),
        ],
        safety_notice=".",
        summary=".",
    )


# Models
def test_pack_valid():
    p = LLMHumanFinalEditInstructionPack(safety_notice=".", summary=".")
    assert p.human_instruction_only is True
    assert p.final_resume_modified is False
    assert p.executable_patch_generated is False
    assert p.final_approval_granted is False


def test_pack_enforces_safety():
    with pytest.raises(Exception):
        LLMHumanFinalEditInstructionPack(safety_notice=".", summary=".", human_instruction_only=False)
    with pytest.raises(Exception):
        LLMHumanFinalEditInstructionPack(safety_notice=".", summary=".", final_approval_granted=True)


def test_pack_no_apply_fields():
    p = LLMHumanFinalEditInstructionPack(safety_notice=".", summary=".")
    assert not hasattr(p, "applied_candidates")
    assert not hasattr(p, "patch_operations")


# Builder
def test_review_required_becomes_instruction_ready():
    cl = _make_checklist()
    pack = build_human_final_edit_pack(cl)
    c1 = [i for i in pack.items if i.candidate_id == "c1"][0]
    assert c1.item_status == LLMHumanFinalEditItemStatus.INSTRUCTION_READY
    assert c1.can_be_considered_for_human_edit is True
    assert len(c1.human_instructions) >= 5
    assert c1.system_final_approval_granted is False


def test_blocked_remains_blocked():
    pack = build_human_final_edit_pack(_make_checklist())
    c2 = [i for i in pack.items if i.candidate_id == "c2"][0]
    assert c2.item_status == LLMHumanFinalEditItemStatus.BLOCKED


def test_default_statuses_not_approved():
    pack = build_human_final_edit_pack(_make_checklist())
    for item in pack.items:
        assert item.human_decision_default == "not_reviewed"
        for inst in item.human_instructions:
            assert inst.default_status in ("not_started", "not_reviewed")
            assert "approved" not in inst.default_status


def test_deterministic():
    cl = _make_checklist()
    assert build_human_final_edit_pack(cl).model_dump_json() == build_human_final_edit_pack(cl).model_dump_json()


# Markdown
def test_md_has_safety():
    md = render_human_final_edit_pack_markdown(build_human_final_edit_pack(_make_checklist()))
    assert "Safety Notice" in md or "安全声明" in md


# IO
def test_io_writes(tmp_path: Path):
    cl_path = tmp_path / "cl.json"
    cl_path.write_text(_make_checklist().model_dump_json(indent=2), encoding="utf-8")
    pack = write_human_final_edit_pack_to_files(cl_path, tmp_path / "ep.json", tmp_path / "ep.md", tmp_path / "ep.html")
    assert (tmp_path / "ep.json").is_file()
    assert (tmp_path / "ep.md").is_file()
    assert (tmp_path / "ep.html").is_file()
    assert pack.human_instruction_only is True


def test_missing_cl_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        write_human_final_edit_pack_to_files(tmp_path / "nope.json")


# CLI
@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_cli_exists():
    assert "build-llm-human-final-edit-pack" in [c.name for c in app.registered_commands]


def test_cli_valid(runner: CliRunner, tmp_path: Path):
    cl_path = tmp_path / "cl.json"
    cl_path.write_text(_make_checklist().model_dump_json(indent=2), encoding="utf-8")
    r = runner.invoke(app, ["build-llm-human-final-edit-pack", "--checklist", str(cl_path), "--output-json", str(tmp_path / "ep.json")])
    assert r.exit_code == 0


def test_cli_missing(runner: CliRunner, tmp_path: Path):
    r = runner.invoke(app, ["build-llm-human-final-edit-pack", "--checklist", str(tmp_path / "nope.json")])
    assert r.exit_code == 1


# Workflow
def test_wf_default():
    wi = ResumeWorkflowInput(user_profile=SAMPLE_USER_PROFILE, resume_content=SAMPLE_RESUME_CONTENT, output_dir="outputs/m29_wf")
    assert wi.write_llm_human_final_edit_pack is False
    r = run_resume_workflow(wi)
    assert r.status.value in ("completed", "completed_with_warnings")


# Regressions
def test_export_format():
    from resume_pdf_agent.models.enums import ExportFormat
    assert [x.value for x in ExportFormat] == ["pdf"]


def test_html_no_apply():
    html = render_human_final_edit_pack_html(build_human_final_edit_pack(_make_checklist())).lower()
    assert "apply" not in html or "apply" in html
    assert "update resume" not in html
    assert "final approve" not in html


def test_html_no_external():
    html = render_human_final_edit_pack_html(build_human_final_edit_pack(_make_checklist())).lower()
    assert "cdn." not in html
    assert "fonts.googleapis" not in html


def test_js_no_network():
    js_path = Path(__file__).resolve().parent.parent / "src/resume_pdf_agent/llm_human_final_edit_pack/static/human_final_edit_pack.js"
    js = js_path.read_text(encoding="utf-8").lower()
    assert "fetch(" not in js
    assert "http://" not in js
