"""Context tests for M25 application preview UI."""

from __future__ import annotations

from resume_pdf_agent.llm_application_preview_ui.context import (
    build_llm_application_preview_context,
)
from resume_pdf_agent.models.llm_application_plan import (
    LLMApplicationBlockReason,
    LLMApplicationPlanStatus,
    LLMCandidateApplicationPlan,
    LLMCandidateApplicationPlanItem,
)


def _item(cid: str, status: LLMApplicationPlanStatus) -> LLMCandidateApplicationPlanItem:
    return LLMCandidateApplicationPlanItem(
        candidate_id=cid,
        source_action="approve_candidate",
        plan_status=status,
        target_section="experience" if status != LLMApplicationPlanStatus.UNMAPPED else None,
        target_item_id="exp1" if status != LLMApplicationPlanStatus.UNMAPPED else None,
        original_text=f"Original {cid}.",
        candidate_text=f"Rewrite {cid}.",
        provider="mock",
        needs_confirmation=status != LLMApplicationPlanStatus.PLANNED,
        validation_warnings=["warning"] if status == LLMApplicationPlanStatus.BLOCKED else [],
        block_reasons=[LLMApplicationBlockReason.NEEDS_CONFIRMATION]
        if status != LLMApplicationPlanStatus.PLANNED
        else [],
        manual_review_notes=["manual note"],
        decision_note="decision note",
        application_instruction="Inspect manually.",
    )


def _plan() -> LLMCandidateApplicationPlan:
    items = [
        _item("c1", LLMApplicationPlanStatus.PLANNED),
        _item("c2", LLMApplicationPlanStatus.BLOCKED),
        _item("c3", LLMApplicationPlanStatus.NEEDS_MANUAL_EDIT),
        _item("c4", LLMApplicationPlanStatus.EXCLUDED),
        _item("c5", LLMApplicationPlanStatus.UNMAPPED),
    ]
    return LLMCandidateApplicationPlan(
        total_candidates=5,
        total_decisions=5,
        planned_count=1,
        blocked_count=1,
        needs_manual_edit_count=1,
        excluded_count=1,
        unmapped_count=1,
        items=items,
        warnings=["plan warning"],
        safety_notice="Plan only; safeguards still apply.",
        source_files={"llm_rewrite_result": "result.json"},
        summary="Plan summary.",
    )


def test_context_groups_all_plan_statuses():
    context = build_llm_application_preview_context(_plan(), plan_path="plan.json")
    counts = {group.status: group.count for group in context.status_groups}
    assert counts == {
        "planned": 1,
        "blocked": 1,
        "needs_manual_edit": 1,
        "excluded": 1,
        "unmapped": 1,
    }


def test_context_preserves_text_warnings_reasons_and_sources():
    context = build_llm_application_preview_context(_plan(), plan_path="plan.json")
    blocked = next(item for item in context.items if item.candidate_id == "c2")
    assert blocked.original_text == "Original c2."
    assert blocked.candidate_text == "Rewrite c2."
    assert blocked.validation_warnings == ["warning"]
    assert "needs_confirmation" in blocked.block_reasons
    assert context.source_files["llm_rewrite_result"] == "result.json"
    assert context.source_files["llm_rewrite_application_plan"] == "plan.json"


def test_context_includes_safety_notice_and_labels():
    context = build_llm_application_preview_context(_plan())
    assert "Plan only" in context.safety_notice
    assert "Manual review required" in context.items[0].safety_labels
    assert "Not factually verified" in context.items[0].safety_labels


def test_context_does_not_invent_missing_target_mapping():
    context = build_llm_application_preview_context(_plan())
    unmapped = next(item for item in context.items if item.plan_status == "unmapped")
    assert unmapped.target_section is None
    assert unmapped.target_item_id is None


def test_context_does_not_mark_candidates_as_applied():
    context = build_llm_application_preview_context(_plan())
    dumped = context.model_dump()
    assert "applied_candidates" not in dumped
    assert all("applied" not in item for item in dumped["items"])
