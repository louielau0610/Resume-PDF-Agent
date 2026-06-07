"""Tests for M24 application plan models."""

from __future__ import annotations

import pytest

from resume_pdf_agent.models.llm_application_plan import (
    LLMApplicationBlockReason,
    LLMApplicationPlanStatus,
    LLMCandidateApplicationPlan,
    LLMCandidateApplicationPlanItem,
)


def test_allowed_plan_statuses():
    assert [s.value for s in LLMApplicationPlanStatus] == [
        "planned",
        "blocked",
        "needs_manual_edit",
        "excluded",
        "unmapped",
    ]


def test_block_reasons_include_safety_gates():
    values = [r.value for r in LLMApplicationBlockReason]
    assert "truthfulness_not_verified" in values
    assert "confirmation_required" in values
    assert "needs_confirmation" in values


def test_valid_plan_item():
    item = LLMCandidateApplicationPlanItem(
        candidate_id="c1",
        source_action="approve_candidate",
        plan_status=LLMApplicationPlanStatus.PLANNED,
        needs_confirmation=False,
        application_instruction="Plan only.",
    )
    assert item.candidate_id == "c1"
    assert item.plan_status == LLMApplicationPlanStatus.PLANNED


def test_valid_plan_summary_plan_only_true():
    plan = LLMCandidateApplicationPlan(
        total_candidates=1,
        total_decisions=1,
        planned_count=1,
        items=[
            LLMCandidateApplicationPlanItem(
                candidate_id="c1",
                source_action="approve_candidate",
                plan_status=LLMApplicationPlanStatus.PLANNED,
                needs_confirmation=False,
                application_instruction="Plan only.",
            )
        ],
        safety_notice="Plan only.",
        summary="Plan.",
    )
    assert plan.plan_only is True


def test_plan_only_cannot_be_false():
    with pytest.raises(ValueError):
        LLMCandidateApplicationPlan(
            safety_notice="Plan only.",
            summary="Plan.",
            plan_only=False,
        )


def test_no_applied_candidates_field():
    plan = LLMCandidateApplicationPlan(safety_notice="Plan only.", summary="Plan.")
    assert not hasattr(plan, "applied_candidates")
