"""Tests for M23 LLM review decision models."""

from __future__ import annotations

import pytest

from resume_pdf_agent.models.llm_review_decisions import (
    LLMReviewDecision,
    LLMReviewDecisionAction,
    LLMReviewDecisionFile,
    normalize_llm_review_decision_action,
)


def test_allowed_decision_actions_match_m22_ui_values():
    values = [x.value for x in LLMReviewDecisionAction]
    assert values == [
        "approve_candidate",
        "reject_candidate",
        "needs_editing",
        "provide_note",
        "ignore_for_now",
    ]


def test_valid_decision_model_accepts_browser_shape():
    decision = LLMReviewDecision(
        candidate_id="c1",
        decision="approve_candidate",
        reviewer_note="Looks accurate.",
        extra_flag=True,
    )
    assert decision.action == "approve_candidate"
    assert decision.normalized_action == LLMReviewDecisionAction.APPROVE_CANDIDATE
    assert decision.note == "Looks accurate."
    assert decision.metadata["extra_flag"] is True


def test_valid_decision_file_model_propagates_reviewer_fields():
    decision_file = LLMReviewDecisionFile(
        reviewer_name="reviewer",
        reviewed_at="2026-06-08T00:00:00Z",
        decisions=[{"candidate_id": "c1", "decision": "reject_candidate"}],
    )
    assert decision_file.decisions[0].reviewer == "reviewer"
    assert decision_file.decisions[0].reviewed_at == "2026-06-08T00:00:00Z"


def test_decision_file_accepts_list_shape():
    decision_file = LLMReviewDecisionFile(
        decisions=[LLMReviewDecision(candidate_id="c1", action="ignore_for_now")]
    )
    assert len(decision_file.decisions) == 1


def test_action_aliases_are_normalized():
    assert normalize_llm_review_decision_action("approve") == LLMReviewDecisionAction.APPROVE_CANDIDATE
    assert normalize_llm_review_decision_action("needs_edit") == LLMReviewDecisionAction.NEEDS_EDITING
    assert normalize_llm_review_decision_action("note") == LLMReviewDecisionAction.PROVIDE_NOTE
    assert normalize_llm_review_decision_action("ignore") == LLMReviewDecisionAction.IGNORE_FOR_NOW


def test_unknown_action_is_preserved_for_non_strict_analysis():
    decision = LLMReviewDecision(candidate_id="c1", action="custom_action")
    assert decision.normalized_action is None


def test_empty_candidate_id_is_invalid():
    with pytest.raises(ValueError):
        LLMReviewDecision(candidate_id="", action="approve_candidate")
