"""Tests for M24 application plan Markdown."""

from __future__ import annotations

from resume_pdf_agent.llm_application_plan.markdown import render_llm_application_plan_markdown
from resume_pdf_agent.models.llm_application_plan import (
    LLMApplicationBlockReason,
    LLMApplicationPlanStatus,
    LLMCandidateApplicationPlan,
    LLMCandidateApplicationPlanItem,
)


def _plan() -> LLMCandidateApplicationPlan:
    return LLMCandidateApplicationPlan(
        total_candidates=4,
        total_decisions=4,
        planned_count=1,
        blocked_count=1,
        needs_manual_edit_count=1,
        excluded_count=1,
        items=[
            LLMCandidateApplicationPlanItem(
                candidate_id="planned",
                source_action="approve_candidate",
                plan_status=LLMApplicationPlanStatus.PLANNED,
                target_item_id="exp1",
                needs_confirmation=False,
                block_reasons=[LLMApplicationBlockReason.TRUTHFULNESS_NOT_VERIFIED],
                application_instruction="Plan only.",
            ),
            LLMCandidateApplicationPlanItem(
                candidate_id="blocked",
                source_action="approve_candidate",
                plan_status=LLMApplicationPlanStatus.BLOCKED,
                block_reasons=[LLMApplicationBlockReason.NEEDS_CONFIRMATION],
                application_instruction="Do not apply.",
            ),
            LLMCandidateApplicationPlanItem(
                candidate_id="edit",
                source_action="needs_editing",
                plan_status=LLMApplicationPlanStatus.NEEDS_MANUAL_EDIT,
                block_reasons=[LLMApplicationBlockReason.NEEDS_EDIT],
                application_instruction="Manual edit.",
            ),
            LLMCandidateApplicationPlanItem(
                candidate_id="excluded",
                source_action="reject_candidate",
                plan_status=LLMApplicationPlanStatus.EXCLUDED,
                block_reasons=[LLMApplicationBlockReason.REJECTED],
                application_instruction="Excluded.",
            ),
        ],
        warnings=["Plan only warning."],
        safety_notice="No candidates were applied.",
        summary="Plan.",
    )


def test_markdown_includes_plan_only_safety_notice():
    md = render_llm_application_plan_markdown(_plan())
    assert "Plan-only Safety Notice" in md
    assert "No candidate has been applied" in md
    assert "final resume has not been modified" in md


def test_markdown_includes_count_and_status_sections():
    md = render_llm_application_plan_markdown(_plan())
    assert "Count Summary" in md
    assert "Planned Candidates" in md
    assert "Blocked Candidates" in md
    assert "Needs Manual Edit" in md
    assert "Excluded Candidates" in md


def test_markdown_includes_warnings():
    md = render_llm_application_plan_markdown(_plan())
    assert "Plan only warning." in md


def test_markdown_does_not_claim_application_or_fact_verification():
    md = render_llm_application_plan_markdown(_plan()).lower()
    assert "has been applied" not in md.replace("no candidate has been applied", "")
    assert "factually verified" not in md
    assert "approval does not mean factual verification" in md
