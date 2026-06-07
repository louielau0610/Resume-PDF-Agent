"""Tests for M24 deterministic application planner."""

from __future__ import annotations

from copy import deepcopy

from resume_pdf_agent.llm_application_plan.planner import plan_llm_candidate_application
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
)
from resume_pdf_agent.models.llm_review_decisions import (
    LLMReviewDecisionFile,
    LLMReviewDecisionSummary,
)


def _candidate(
    cid: str,
    *,
    needs_confirmation: bool = False,
    source_experience_id: str | None = "exp1",
    validation_warnings: list[str] | None = None,
) -> LLMRewriteCandidate:
    return LLMRewriteCandidate(
        candidate_id=cid,
        source_experience_id=source_experience_id,
        original_text=f"Original {cid}.",
        rewritten_text=f"Rewrite {cid}.",
        provider=LLMProviderType.MOCK,
        mode=LLMRewriteMode.CONSERVATIVE_POLISH,
        status=LLMRewriteStatus.REWRITTEN,
        needs_confirmation=needs_confirmation,
        validation_warnings=validation_warnings or [],
    )


def _result(candidates: list[LLMRewriteCandidate]) -> LLMRewriteResult:
    return LLMRewriteResult(
        status=LLMRewriteStatus.REWRITTEN,
        provider=LLMProviderType.MOCK,
        candidates=candidates,
        candidates_generated=len(candidates),
        candidates_requiring_confirmation=sum(1 for c in candidates if c.needs_confirmation),
        summary="Mock.",
    )


def _decisions(rows: list[dict]) -> LLMReviewDecisionFile:
    return LLMReviewDecisionFile(decisions=rows)


def _summary() -> LLMReviewDecisionSummary:
    return LLMReviewDecisionSummary(
        safety_notice="Advisory.",
        summary="Summary.",
    )


def test_approved_safe_candidate_becomes_planned():
    plan = plan_llm_candidate_application(
        _result([_candidate("c1")]),
        _decisions([{"candidate_id": "c1", "decision": "approve_candidate"}]),
        _summary(),
    )
    assert plan.planned_count == 1
    assert plan.items[0].plan_status == LLMApplicationPlanStatus.PLANNED


def test_approved_with_validation_warnings_becomes_blocked():
    plan = plan_llm_candidate_application(
        _result([_candidate("c1", validation_warnings=["warn"])]),
        _decisions([{"candidate_id": "c1", "decision": "approve_candidate"}]),
        _summary(),
    )
    assert plan.items[0].plan_status == LLMApplicationPlanStatus.BLOCKED
    assert LLMApplicationBlockReason.HAS_VALIDATION_WARNINGS in plan.items[0].block_reasons


def test_approved_needs_confirmation_becomes_blocked():
    plan = plan_llm_candidate_application(
        _result([_candidate("c1", needs_confirmation=True)]),
        _decisions([{"candidate_id": "c1", "decision": "approve_candidate"}]),
        _summary(),
    )
    assert plan.items[0].plan_status == LLMApplicationPlanStatus.BLOCKED
    assert LLMApplicationBlockReason.NEEDS_CONFIRMATION in plan.items[0].block_reasons


def test_needs_edit_decision_becomes_needs_manual_edit():
    plan = plan_llm_candidate_application(
        _result([_candidate("c1")]),
        _decisions([{"candidate_id": "c1", "decision": "needs_editing"}]),
        _summary(),
    )
    assert plan.needs_manual_edit_count == 1
    assert plan.items[0].plan_status == LLMApplicationPlanStatus.NEEDS_MANUAL_EDIT


def test_rejected_and_ignored_are_excluded():
    plan = plan_llm_candidate_application(
        _result([_candidate("c1"), _candidate("c2")]),
        _decisions([
            {"candidate_id": "c1", "decision": "reject_candidate"},
            {"candidate_id": "c2", "decision": "ignore_for_now"},
        ]),
        _summary(),
    )
    assert plan.excluded_count == 2
    assert {i.plan_status for i in plan.items} == {LLMApplicationPlanStatus.EXCLUDED}


def test_undecided_candidate_becomes_blocked():
    plan = plan_llm_candidate_application(_result([_candidate("c1")]), _decisions([]), _summary())
    assert plan.items[0].plan_status == LLMApplicationPlanStatus.BLOCKED
    assert LLMApplicationBlockReason.UNDECIDED in plan.items[0].block_reasons


def test_unknown_candidate_decision_generates_warning():
    plan = plan_llm_candidate_application(
        _result([_candidate("c1")]),
        _decisions([{"candidate_id": "unknown", "decision": "approve_candidate"}]),
        _summary(),
    )
    assert any("unknown candidate IDs" in w for w in plan.warnings)


def test_duplicate_decision_blocks_candidate():
    plan = plan_llm_candidate_application(
        _result([_candidate("c1")]),
        _decisions([
            {"candidate_id": "c1", "decision": "approve_candidate"},
            {"candidate_id": "c1", "decision": "approve_candidate"},
        ]),
        _summary(),
    )
    assert plan.items[0].plan_status == LLMApplicationPlanStatus.BLOCKED
    assert LLMApplicationBlockReason.DUPLICATE_DECISION in plan.items[0].block_reasons


def test_missing_original_text_blocks_candidate():
    candidate = _candidate("c1").model_copy(update={"original_text": ""})
    plan = plan_llm_candidate_application(
        _result([candidate]),
        _decisions([{"candidate_id": "c1", "decision": "approve_candidate"}]),
        _summary(),
    )
    assert LLMApplicationBlockReason.MISSING_ORIGINAL_TEXT in plan.items[0].block_reasons


def test_missing_candidate_text_blocks_candidate():
    candidate = _candidate("c1").model_copy(update={"rewritten_text": ""})
    plan = plan_llm_candidate_application(
        _result([candidate]),
        _decisions([{"candidate_id": "c1", "decision": "approve_candidate"}]),
        _summary(),
    )
    assert LLMApplicationBlockReason.MISSING_CANDIDATE_TEXT in plan.items[0].block_reasons


def test_unmapped_candidate_is_unmapped():
    plan = plan_llm_candidate_application(
        _result([_candidate("c1", source_experience_id=None)]),
        _decisions([{"candidate_id": "c1", "decision": "approve_candidate"}]),
        _summary(),
    )
    assert plan.items[0].plan_status == LLMApplicationPlanStatus.UNMAPPED


def test_no_summary_input_still_works_with_warning():
    plan = plan_llm_candidate_application(
        _result([_candidate("c1")]),
        _decisions([{"candidate_id": "c1", "decision": "approve_candidate"}]),
        None,
    )
    assert plan.planned_count == 1
    assert any("No M23 decision summary" in w for w in plan.warnings)


def test_deterministic_output_across_repeated_runs():
    result = _result([_candidate("c1"), _candidate("c2", needs_confirmation=True)])
    decisions = _decisions([
        {"candidate_id": "c1", "decision": "approve_candidate"},
        {"candidate_id": "c2", "decision": "needs_editing"},
    ])
    a = plan_llm_candidate_application(deepcopy(result), deepcopy(decisions), _summary())
    b = plan_llm_candidate_application(deepcopy(result), deepcopy(decisions), _summary())
    assert a.model_dump(mode="python") == b.model_dump(mode="python")
