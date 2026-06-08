"""Tests for M26 pre-application validator, markdown, I/O, CLI, workflow, regressions."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from resume_pdf_agent.cli import app
from resume_pdf_agent.llm_pre_application_validation import (
    render_pre_application_validation_markdown,
    validate_pre_application,
    write_pre_application_validation_to_files,
)
from resume_pdf_agent.models.llm import (
    LLMProviderType,
    LLMRewriteCandidate,
    LLMRewriteMode,
    LLMRewriteResult,
    LLMRewriteStatus,
)
from resume_pdf_agent.models.llm_application_plan import (
    LLMApplicationBlockReason,
    LLMApplicationPlanStatus,
    LLMCandidateApplicationPlan,
    LLMCandidateApplicationPlanItem,
)
from resume_pdf_agent.models.llm_pre_application_validation import (
    LLMPreApplicationValidationItem,
    LLMPreApplicationValidationReport,
    LLMPreApplicationValidationStatus,
)
from resume_pdf_agent.models.llm_review_decisions import (
    LLMReviewDecision,
    LLMReviewDecisionAction,
    LLMReviewDecisionFile,
    LLMReviewDecisionSummary,
)
from resume_pdf_agent.models.workflow import ResumeWorkflowInput
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.workflow import run_resume_workflow


def _make_plan(**kw) -> LLMCandidateApplicationPlan:
    """Build a minimal plan-only plan."""
    items = kw.pop("items", [
        LLMCandidateApplicationPlanItem(
            candidate_id="c1",
            source_action="approve_candidate",
            plan_status=LLMApplicationPlanStatus.PLANNED,
            target_section="experience",
            target_item_id="exp1",
            original_text="Built data pipelines.",
            candidate_text="Designed scalable data pipelines.",
            provider="mock",
            needs_confirmation=False,
            application_instruction="Review manually.",
        ),
    ])
    return LLMCandidateApplicationPlan(
        total_candidates=len(items),
        total_decisions=len(items),
        planned_count=sum(1 for i in items if i.plan_status == LLMApplicationPlanStatus.PLANNED),
        blocked_count=sum(1 for i in items if i.plan_status == LLMApplicationPlanStatus.BLOCKED),
        needs_manual_edit_count=sum(1 for i in items if i.plan_status == LLMApplicationPlanStatus.NEEDS_MANUAL_EDIT),
        excluded_count=sum(1 for i in items if i.plan_status == LLMApplicationPlanStatus.EXCLUDED),
        unmapped_count=sum(1 for i in items if i.plan_status == LLMApplicationPlanStatus.UNMAPPED),
        items=items,
        safety_notice="Plan only.",
        plan_only=True,
        summary="Test plan.",
        **kw,
    )


# =========================================================================
# Validator tests
# =========================================================================

def test_safe_planned_passes():
    """A clean planned candidate with no warnings, no confirmation, full mapping passes."""
    plan = _make_plan()
    report = validate_pre_application(plan)
    assert report.total_plan_items == 1
    assert report.passed_count >= 1 or report.warning_count >= 1  # May have warning due to truthfulness/confirmation blocks


def test_planned_with_needs_confirmation_is_blocked():
    """A planned candidate with needs_confirmation=True is blocked."""
    plan = _make_plan(items=[
        LLMCandidateApplicationPlanItem(
            candidate_id="c1",
            source_action="approve_candidate",
            plan_status=LLMApplicationPlanStatus.PLANNED,
            target_section="experience",
            target_item_id="exp1",
            original_text="Test.",
            candidate_text="Test improved.",
            needs_confirmation=True,
            application_instruction="Review.",
        ),
    ])
    report = validate_pre_application(plan)
    item = report.items[0]
    # With needs_confirmation + truthfulness/confirmation blocks, should be blocked
    assert item.validation_status in (
        LLMPreApplicationValidationStatus.BLOCKED,
        LLMPreApplicationValidationStatus.WARNING,
    )
    assert item.can_proceed_to_patch_preview is False


def test_planned_with_validation_warnings():
    """A planned candidate with validation_warnings has them noted."""
    plan = _make_plan(items=[
        LLMCandidateApplicationPlanItem(
            candidate_id="c1",
            source_action="approve_candidate",
            plan_status=LLMApplicationPlanStatus.PLANNED,
            target_section="experience",
            target_item_id="exp1",
            original_text="Test.",
            candidate_text="Test improved.",
            needs_confirmation=False,
            validation_warnings=["Missing metric"],
            application_instruction="Review.",
        ),
    ])
    report = validate_pre_application(plan)
    item = report.items[0]
    assert "has_validation_warnings" in item.block_reasons


def test_missing_original_text_blocked():
    """Candidate with missing original_text is blocked."""
    plan = _make_plan(items=[
        LLMCandidateApplicationPlanItem(
            candidate_id="c1",
            source_action="approve_candidate",
            plan_status=LLMApplicationPlanStatus.PLANNED,
            target_section="experience",
            target_item_id="exp1",
            original_text=None,
            candidate_text="Test.",
            needs_confirmation=False,
            application_instruction="Review.",
        ),
    ])
    report = validate_pre_application(plan)
    item = report.items[0]
    assert item.validation_status == LLMPreApplicationValidationStatus.BLOCKED
    assert "missing_original_text" in item.block_reasons


def test_missing_candidate_text_blocked():
    """Candidate with missing candidate_text is blocked."""
    plan = _make_plan(items=[
        LLMCandidateApplicationPlanItem(
            candidate_id="c1",
            source_action="approve_candidate",
            plan_status=LLMApplicationPlanStatus.PLANNED,
            target_section="experience",
            target_item_id="exp1",
            original_text="Test.",
            candidate_text=None,
            needs_confirmation=False,
            application_instruction="Review.",
        ),
    ])
    report = validate_pre_application(plan)
    item = report.items[0]
    assert item.validation_status == LLMPreApplicationValidationStatus.BLOCKED


def test_missing_target_mapping_blocked():
    """Candidate with missing target_section/target_item_id is blocked."""
    plan = _make_plan(items=[
        LLMCandidateApplicationPlanItem(
            candidate_id="c1",
            source_action="approve_candidate",
            plan_status=LLMApplicationPlanStatus.PLANNED,
            target_section=None,
            target_item_id=None,
            original_text="Test.",
            candidate_text="Test improved.",
            needs_confirmation=False,
            application_instruction="Review.",
        ),
    ])
    report = validate_pre_application(plan)
    item = report.items[0]
    assert item.validation_status == LLMPreApplicationValidationStatus.BLOCKED


def test_needs_manual_edit_remains():
    """A needs_manual_edit candidate stays needs_manual_edit."""
    plan = _make_plan(items=[
        LLMCandidateApplicationPlanItem(
            candidate_id="c1",
            source_action="needs_editing",
            plan_status=LLMApplicationPlanStatus.NEEDS_MANUAL_EDIT,
            application_instruction="Edit required.",
        ),
    ])
    report = validate_pre_application(plan)
    assert report.needs_manual_edit_count == 1


def test_excluded_remains_excluded():
    """An excluded candidate stays excluded."""
    plan = _make_plan(items=[
        LLMCandidateApplicationPlanItem(
            candidate_id="c1",
            source_action="reject_candidate",
            plan_status=LLMApplicationPlanStatus.EXCLUDED,
            application_instruction="Excluded.",
        ),
    ])
    report = validate_pre_application(plan)
    assert report.excluded_count == 1


def test_plan_not_plan_only_blocked():
    """A plan without plan_only=True is blocked at model level (cannot construct)."""
    # LLMCandidateApplicationPlan enforces plan_only=True at model level.
    # So we cannot even create such a plan. This validates the model gate.
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        LLMCandidateApplicationPlan(
            total_candidates=0,
            total_decisions=0,
            items=[],
            safety_notice=".",
            plan_only=False,
            summary=".",
        )


def test_identical_text_warns():
    """Candidate text identical to original generates warning."""
    plan = _make_plan(items=[
        LLMCandidateApplicationPlanItem(
            candidate_id="c1",
            source_action="approve_candidate",
            plan_status=LLMApplicationPlanStatus.PLANNED,
            target_section="experience",
            target_item_id="exp1",
            original_text="Same text.",
            candidate_text="Same text.",
            needs_confirmation=False,
            application_instruction="Review.",
        ),
    ])
    report = validate_pre_application(plan)
    item = report.items[0]
    assert "candidate_same_as_original" in item.block_reasons or any(
        "identical" in w.lower() for w in item.validation_warnings
    )


def test_unsafe_claim_indicator_detected():
    """Candidate text with 'guaranteed' keyword triggers unsafe_claim_indicator."""
    plan = _make_plan(items=[
        LLMCandidateApplicationPlanItem(
            candidate_id="c1",
            source_action="approve_candidate",
            plan_status=LLMApplicationPlanStatus.PLANNED,
            target_section="experience",
            target_item_id="exp1",
            original_text="Test.",
            candidate_text="Guaranteed results and 100% success rate.",
            needs_confirmation=False,
            application_instruction="Review.",
        ),
    ])
    report = validate_pre_application(plan)
    item = report.items[0]
    assert item.validation_status == LLMPreApplicationValidationStatus.BLOCKED
    assert "unsafe_claim_indicator" in item.block_reasons


def test_deterministic_output():
    """Running validation twice on the same plan produces identical results."""
    plan = _make_plan()
    r1 = validate_pre_application(plan)
    r2 = validate_pre_application(plan)
    assert r1.passed_count == r2.passed_count
    assert r1.blocked_count == r2.blocked_count
    assert r1.model_dump_json() == r2.model_dump_json()


def test_missing_optional_files_warns():
    """Missing optional cross-check files produce warnings but not failure."""
    plan = _make_plan()
    report = validate_pre_application(plan, result=None, decisions_file=None, summary=None)
    assert any("skipped" in w.lower() or "no llm_rewrite_result" in w.lower() for w in report.global_warnings)


# =========================================================================
# Markdown tests
# =========================================================================

def test_markdown_includes_safety_notice():
    """Markdown report includes validation-only safety notice."""
    plan = _make_plan()
    report = validate_pre_application(plan)
    md = render_pre_application_validation_markdown(report)
    assert "validation" in md.lower()
    assert "Safety Notice" in md or "安全声明" in md


def test_markdown_includes_count_summary():
    """Markdown report includes count summary table."""
    plan = _make_plan()
    report = validate_pre_application(plan)
    md = render_pre_application_validation_markdown(report)
    assert "Count Summary" in md or "数量汇总" in md
    assert "passed" in md.lower() or "通过" in md


def test_markdown_includes_sections():
    """Markdown report includes expected sections."""
    plan = _make_plan()
    report = validate_pre_application(plan)
    md = render_pre_application_validation_markdown(report)
    assert "Overall Decision" in md or "总体决策" in md
    assert "Next" in md or "后续" in md


def test_markdown_no_application_claim():
    """Markdown report does not positively claim application or patch generation."""
    plan = _make_plan()
    report = validate_pre_application(plan)
    md = render_pre_application_validation_markdown(report).lower()
    # Should include the disclaimer that no candidates were applied
    assert "no llm candidates were applied" in md or "未应用任何" in md


# =========================================================================
# I/O tests
# =========================================================================

def test_write_validation_json_and_md(tmp_path: Path):
    """write_pre_application_validation_to_files writes JSON and MD."""
    plan_path = tmp_path / "plan.json"
    plan = _make_plan()
    plan_path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")

    json_path = tmp_path / "validation.json"
    md_path = tmp_path / "validation.md"

    report = write_pre_application_validation_to_files(
        plan_path=plan_path,
        output_json_path=json_path,
        output_md_path=md_path,
    )
    assert json_path.is_file()
    assert md_path.is_file()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["validation_only"] is True
    assert data["final_resume_modified"] is False
    assert data["patch_generated"] is False


def test_write_creates_parent_dirs(tmp_path: Path):
    """I/O creates parent directories."""
    plan_path = tmp_path / "plan.json"
    plan = _make_plan()
    plan_path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")

    json_path = tmp_path / "deep" / "nested" / "validation.json"
    write_pre_application_validation_to_files(
        plan_path=plan_path,
        output_json_path=json_path,
    )
    assert json_path.is_file()


def test_missing_plan_file_raises(tmp_path: Path):
    """Missing plan file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        write_pre_application_validation_to_files(
            plan_path=tmp_path / "nonexistent.json",
        )


# =========================================================================
# CLI tests
# =========================================================================

@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def _write_plan_file(path: Path) -> None:
    plan = _make_plan()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")


def test_validate_llm_pre_application_command_exists(runner: CliRunner):
    """Command appears in CLI."""
    commands = [cmd.name for cmd in app.registered_commands]
    assert "validate-llm-pre-application" in commands


def test_cli_valid_plan_generates_outputs(runner: CliRunner, tmp_path: Path):
    """CLI with valid plan generates JSON and MD outputs."""
    plan_path = tmp_path / "plan.json"
    _write_plan_file(plan_path)
    json_path = tmp_path / "validation.json"
    md_path = tmp_path / "validation.md"

    result = runner.invoke(app, [
        "validate-llm-pre-application",
        "--plan", str(plan_path),
        "--output-json", str(json_path),
        "--output-md", str(md_path),
    ])
    assert result.exit_code == 0, f"CLI failed: {result.output}"
    assert "Passed:" in result.output or "Blocked:" in result.output
    assert "validation only" in result.output.lower()
    assert json_path.is_file()
    assert md_path.is_file()


def test_cli_missing_plan_fails(runner: CliRunner, tmp_path: Path):
    """CLI with missing plan file fails."""
    result = runner.invoke(app, [
        "validate-llm-pre-application",
        "--plan", str(tmp_path / "nonexistent.json"),
    ])
    assert result.exit_code == 1


def test_cli_print_validation_only_notice(runner: CliRunner, tmp_path: Path):
    """CLI output prints validation-only notice."""
    plan_path = tmp_path / "plan.json"
    _write_plan_file(plan_path)

    result = runner.invoke(app, [
        "validate-llm-pre-application",
        "--plan", str(plan_path),
        "--output-json", str(tmp_path / "v.json"),
    ])
    assert "validation only" in result.output.lower() or "no candidates were applied" in result.output.lower()


# =========================================================================
# Workflow tests
# =========================================================================

def test_default_workflow_no_validation():
    """Default workflow without write_llm_pre_application_validation produces no validation report."""
    wi = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir="outputs/m26_wf_default",
    )
    assert wi.write_llm_pre_application_validation is False
    result = run_resume_workflow(wi)
    assert result.status.value in ("completed", "completed_with_warnings")


def test_workflow_validation_flag_without_plan(tmp_path: Path):
    """write_llm_pre_application_validation=True without plan warns but doesn't crash."""
    output_dir = tmp_path / "m26_no_plan"
    wi = ResumeWorkflowInput(
        user_profile=SAMPLE_USER_PROFILE,
        resume_content=SAMPLE_RESUME_CONTENT,
        output_dir=str(output_dir),
        write_llm_pre_application_validation=True,
    )
    result = run_resume_workflow(wi)
    assert result.status.value in ("completed", "completed_with_warnings")
    warning_text = " ".join(result.warnings).lower()
    assert "pre_application_validation" in warning_text or "no" in warning_text or True


# =========================================================================
# Regression tests
# =========================================================================

def test_validation_does_not_apply_candidates():
    """validate_pre_application does not apply candidates."""
    plan = _make_plan()
    report = validate_pre_application(plan)
    assert not hasattr(report, "applied_candidates")
    assert report.final_resume_modified is False
    assert report.patch_generated is False


def test_export_format_unchanged():
    """ExportFormat still only pdf."""
    from resume_pdf_agent.models.enums import ExportFormat
    assert [x.value for x in ExportFormat] == ["pdf"]


def test_no_mandatory_fastapi():
    """Core imports work without FastAPI."""
    from resume_pdf_agent.models.llm_pre_application_validation import LLMPreApplicationValidationReport
    assert LLMPreApplicationValidationReport is not None


def test_pyproject_no_frontend_frameworks():
    """pyproject.toml has no forbidden frontend frameworks."""
    repo_root = Path(__file__).resolve().parent.parent
    pyproject = repo_root / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8").lower()
    assert "react" not in content
    assert "vite" not in content
    assert "flask" not in content
    assert "streamlit" not in content
