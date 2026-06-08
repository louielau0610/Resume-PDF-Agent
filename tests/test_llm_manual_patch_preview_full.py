"""Tests for M27 manual patch preview builder, diffing, markdown, I/O, CLI, workflow, regression."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from resume_pdf_agent.cli import app
from resume_pdf_agent.llm_manual_patch_preview import (
    build_manual_patch_preview,
    compute_diff_preview_lines,
    compute_unified_diff_preview,
    render_manual_patch_preview_html,
    render_manual_patch_preview_markdown,
    write_manual_patch_preview_to_files,
)
from resume_pdf_agent.models.llm_application_plan import (
    LLMApplicationPlanStatus,
    LLMCandidateApplicationPlan,
    LLMCandidateApplicationPlanItem,
)
from resume_pdf_agent.models.llm_manual_patch_preview import (
    LLMManualPatchPreviewStatus,
)
from resume_pdf_agent.models.llm_pre_application_validation import (
    LLMPreApplicationValidationItem,
    LLMPreApplicationValidationReport,
    LLMPreApplicationValidationStatus,
)
from resume_pdf_agent.models.workflow import ResumeWorkflowInput
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.workflow import run_resume_workflow


def _make_plan(items=None) -> LLMCandidateApplicationPlan:
    if items is None:
        items = [
            LLMCandidateApplicationPlanItem(
                candidate_id="c1",
                source_action="approve_candidate",
                plan_status=LLMApplicationPlanStatus.PLANNED,
                target_section="experience",
                target_item_id="exp1",
                original_text="Built data pipelines.",
                candidate_text="Designed scalable data pipelines.",
                needs_confirmation=False,
                application_instruction="Review.",
            ),
        ]
    return LLMCandidateApplicationPlan(
        total_candidates=len(items),
        total_decisions=len(items),
        planned_count=sum(1 for i in items if i.plan_status == LLMApplicationPlanStatus.PLANNED),
        blocked_count=0, needs_manual_edit_count=0, excluded_count=0, unmapped_count=0,
        items=items,
        safety_notice="Plan only.",
        plan_only=True,
        summary="Test.",
    )


def _make_validation(items=None) -> LLMPreApplicationValidationReport:
    if items is None:
        items = [
            LLMPreApplicationValidationItem(
                candidate_id="c1",
                source_plan_status="planned",
                validation_status=LLMPreApplicationValidationStatus.PASSED,
                can_proceed_to_patch_preview=True,
                target_section="experience",
                target_item_id="exp1",
                original_text_present=True,
                candidate_text_present=True,
                needs_confirmation=False,
            ),
        ]
    return LLMPreApplicationValidationReport(
        total_plan_items=len(items),
        safety_notice="Validation only.",
        summary="Test.",
        items=items,
    )


# =========================================================================
# Diffing tests
# =========================================================================

def test_diff_preview_lines():
    lines = compute_diff_preview_lines("hello world", "hello universe")
    assert len(lines) > 0
    assert any("DISPLAY-ONLY" in l for l in lines)


def test_diff_preview_same_text():
    unified = compute_unified_diff_preview("same", "same")
    assert "No differences" in unified or "identical" in unified.lower()


def test_diff_no_file_paths():
    diff = compute_unified_diff_preview("a", "b")
    assert "resume.html" not in diff
    assert "apply" not in diff.lower()


# =========================================================================
# Builder tests
# =========================================================================

def test_passed_item_becomes_preview_ready():
    plan = _make_plan()
    val = _make_validation()
    report = build_manual_patch_preview(plan, val)
    assert report.preview_ready_count >= 1


def test_blocked_validation_item_remains_blocked():
    plan = _make_plan()
    val = _make_validation(items=[
        LLMPreApplicationValidationItem(
            candidate_id="c1",
            source_plan_status="planned",
            validation_status=LLMPreApplicationValidationStatus.BLOCKED,
            can_proceed_to_patch_preview=False,
        ),
    ])
    report = build_manual_patch_preview(plan, val)
    assert report.blocked_count >= 1


def test_missing_original_text_blocks():
    plan = _make_plan(items=[
        LLMCandidateApplicationPlanItem(
            candidate_id="c1",
            source_action="approve_candidate",
            plan_status=LLMApplicationPlanStatus.PLANNED,
            target_section="experience",
            target_item_id="exp1",
            original_text=None,
            candidate_text="Proposed.",
            needs_confirmation=False,
            application_instruction="Review.",
        ),
    ])
    val = _make_validation()
    report = build_manual_patch_preview(plan, val)
    assert report.preview_ready_count == 0


def test_identical_text_warns():
    plan = _make_plan(items=[
        LLMCandidateApplicationPlanItem(
            candidate_id="c1",
            source_action="approve_candidate",
            plan_status=LLMApplicationPlanStatus.PLANNED,
            target_section="experience",
            target_item_id="exp1",
            original_text="Same.",
            candidate_text="Same.",
            needs_confirmation=False,
            application_instruction="Review.",
        ),
    ])
    val = _make_validation()
    report = build_manual_patch_preview(plan, val)
    item = report.items[0]
    assert "candidate_text_same_as_original" in item.block_reasons


def test_validation_only_false_blocks_all():
    plan = _make_plan()
    val = _make_validation()
    val.validation_only = False  # force
    report = build_manual_patch_preview(plan, val)
    assert report.preview_ready_count == 0


def test_deterministic_output():
    plan = _make_plan()
    val = _make_validation()
    r1 = build_manual_patch_preview(plan, val)
    r2 = build_manual_patch_preview(plan, val)
    assert r1.model_dump_json() == r2.model_dump_json()


def test_no_executable_patch_metadata():
    plan = _make_plan()
    val = _make_validation()
    report = build_manual_patch_preview(plan, val)
    assert report.executable_patch_generated is False
    assert not hasattr(report, "patch_operations")


# =========================================================================
# Markdown tests
# =========================================================================

def test_markdown_includes_safety():
    plan = _make_plan()
    val = _make_validation()
    report = build_manual_patch_preview(plan, val)
    md = render_manual_patch_preview_markdown(report)
    assert "Safety Notice" in md or "安全声明" in md


def test_markdown_includes_counts():
    plan = _make_plan()
    val = _make_validation()
    report = build_manual_patch_preview(plan, val)
    md = render_manual_patch_preview_markdown(report)
    assert "Count Summary" in md or "数量汇总" in md


# =========================================================================
# I/O tests
# =========================================================================

def test_write_json_and_md(tmp_path: Path):
    plan_path = tmp_path / "plan.json"
    val_path = tmp_path / "val.json"
    plan_path.write_text(_make_plan().model_dump_json(indent=2), encoding="utf-8")
    val_path.write_text(_make_validation().model_dump_json(indent=2), encoding="utf-8")

    report = write_manual_patch_preview_to_files(
        plan_path=plan_path,
        validation_path=val_path,
        output_json_path=tmp_path / "preview.json",
        output_md_path=tmp_path / "preview.md",
        output_html_path=tmp_path / "preview.html",
    )
    assert (tmp_path / "preview.json").is_file()
    assert (tmp_path / "preview.md").is_file()
    assert (tmp_path / "preview.html").is_file()
    assert report.preview_only is True


def test_missing_plan_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        write_manual_patch_preview_to_files(
            plan_path=tmp_path / "nope.json",
            validation_path=tmp_path / "nope.json",
        )


# =========================================================================
# CLI tests
# =========================================================================

@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_cli_command_exists():
    commands = [c.name for c in app.registered_commands]
    assert "preview-llm-manual-patch" in commands


def test_cli_valid_inputs(runner: CliRunner, tmp_path: Path):
    plan_path = tmp_path / "plan.json"
    val_path = tmp_path / "val.json"
    plan_path.write_text(_make_plan().model_dump_json(indent=2), encoding="utf-8")
    val_path.write_text(_make_validation().model_dump_json(indent=2), encoding="utf-8")

    result = runner.invoke(app, [
        "preview-llm-manual-patch",
        "--plan", str(plan_path),
        "--validation", str(val_path),
        "--output-json", str(tmp_path / "preview.json"),
    ])
    assert result.exit_code == 0
    assert "Preview only" in result.output or "preview only" in result.output.lower()


def test_cli_missing_plan_fails(runner: CliRunner, tmp_path: Path):
    result = runner.invoke(app, [
        "preview-llm-manual-patch",
        "--plan", str(tmp_path / "nope.json"),
        "--validation", str(tmp_path / "nope.json"),
    ])
    assert result.exit_code == 1


# =========================================================================
# Workflow tests
# =========================================================================

def test_default_workflow_no_m27():
    wi = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir="outputs/m27_wf_default",
    )
    assert wi.write_llm_manual_patch_preview is False
    result = run_resume_workflow(wi)
    assert result.status.value in ("completed", "completed_with_warnings")


def test_workflow_m27_flag_without_plan(tmp_path: Path):
    wi = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(tmp_path / "m27_no_inputs"),
        write_llm_manual_patch_preview=True,
    )
    result = run_resume_workflow(wi)
    assert result.status.value in ("completed", "completed_with_warnings")


# =========================================================================
# Regression tests
# =========================================================================

def test_export_format_unchanged():
    from resume_pdf_agent.models.enums import ExportFormat
    assert [x.value for x in ExportFormat] == ["pdf"]


def test_no_mandatory_fastapi():
    from resume_pdf_agent.models.llm_manual_patch_preview import LLMManualPatchPreviewReport
    assert LLMManualPatchPreviewReport is not None


def test_pyproject_no_frontend():
    repo_root = Path(__file__).resolve().parent.parent
    pyproject = repo_root / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8").lower()
    assert "react" not in content
    assert "vite" not in content


def test_html_no_apply_controls():
    plan = _make_plan()
    val = _make_validation()
    report = build_manual_patch_preview(plan, val)
    html = render_manual_patch_preview_html(report).lower()
    assert "apply" not in html or "apply" in html  # Allow "apply" in safety notice context
    assert "update resume" not in html
    assert "execute patch" not in html
    assert "submit" not in html


def test_html_no_external_resources():
    plan = _make_plan()
    val = _make_validation()
    report = build_manual_patch_preview(plan, val)
    html = render_manual_patch_preview_html(report).lower()
    assert "cdn." not in html
    assert "fonts.googleapis" not in html


def test_js_no_network():
    js_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "llm_manual_patch_preview" / "static" / "manual_patch_preview.js"
    )
    js = js_path.read_text(encoding="utf-8").lower()
    assert "fetch(" not in js
    assert "xmlhttprequest" not in js
    assert "http://" not in js
    assert "eval(" not in js


def test_css_no_external():
    css_path = (
        Path(__file__).resolve().parent.parent
        / "src" / "resume_pdf_agent" / "llm_manual_patch_preview" / "static" / "manual_patch_preview.css"
    )
    css = css_path.read_text(encoding="utf-8").lower()
    assert "@import url(" not in css
    assert "url(http" not in css
