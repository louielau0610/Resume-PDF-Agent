"""Tests for M23 LLM review decision analyzer."""

from __future__ import annotations

from resume_pdf_agent.llm_review_decisions.analyzer import analyze_llm_review_decisions
from resume_pdf_agent.models.llm import (
    LLMProviderType,
    LLMRewriteCandidate,
    LLMRewriteMode,
    LLMRewriteResult,
    LLMRewriteStatus,
)
from resume_pdf_agent.models.llm_review_decisions import LLMReviewDecisionFile


def _result(candidate_ids: list[str] | None = None) -> LLMRewriteResult:
    ids = candidate_ids or ["c1", "c2", "c3"]
    return LLMRewriteResult(
        status=LLMRewriteStatus.REWRITTEN,
        provider=LLMProviderType.MOCK,
        candidates=[
            LLMRewriteCandidate(
                candidate_id=cid,
                original_text=f"Original {cid}.",
                rewritten_text=f"Rewrite {cid}.",
                provider=LLMProviderType.MOCK,
                mode=LLMRewriteMode.CONSERVATIVE_POLISH,
                status=LLMRewriteStatus.REWRITTEN,
            )
            for cid in ids
        ],
        candidates_generated=len(ids),
        candidates_requiring_confirmation=len(ids),
        summary="Mock.",
    )


def _decisions(rows: list[dict]) -> LLMReviewDecisionFile:
    return LLMReviewDecisionFile(decisions=rows)


def test_all_candidates_decided_counts_actions():
    summary = analyze_llm_review_decisions(
        _decisions([
            {"candidate_id": "c1", "decision": "approve_candidate"},
            {"candidate_id": "c2", "decision": "reject_candidate"},
            {"candidate_id": "c3", "decision": "ignore_for_now"},
        ]),
        _result(),
    )
    assert summary.total_candidates == 3
    assert summary.approved_count == 1
    assert summary.rejected_count == 1
    assert summary.ignored_count == 1
    assert summary.undecided_candidate_ids == []


def test_some_candidates_undecided_warning():
    summary = analyze_llm_review_decisions(
        _decisions([{"candidate_id": "c1", "decision": "approve_candidate"}]),
        _result(),
    )
    assert summary.undecided_candidate_ids == ["c2", "c3"]
    assert any("do not have decisions" in w for w in summary.warnings)


def test_unknown_candidate_id_warning():
    summary = analyze_llm_review_decisions(
        _decisions([{"candidate_id": "unknown", "decision": "reject_candidate"}]),
        _result(["c1"]),
    )
    assert summary.unknown_candidate_ids == ["unknown"]
    assert any("unknown candidate IDs" in w for w in summary.warnings)


def test_duplicate_candidate_decision_warning():
    summary = analyze_llm_review_decisions(
        _decisions([
            {"candidate_id": "c1", "decision": "approve_candidate"},
            {"candidate_id": "c1", "decision": "reject_candidate"},
        ]),
        _result(["c1"]),
    )
    assert summary.duplicate_candidate_ids == ["c1"]
    assert any("Duplicate" in w for w in summary.warnings)


def test_note_only_decision_counts_as_note():
    summary = analyze_llm_review_decisions(
        _decisions([{"candidate_id": "c1", "decision": "provide_note", "reviewer_note": "Check wording."}]),
        _result(["c1"]),
    )
    assert summary.note_count == 1
    assert summary.note_candidate_ids == ["c1"]
    assert summary.candidate_summaries[0].note == "Check wording."


def test_no_result_file_partial_summary_warns():
    summary = analyze_llm_review_decisions(
        _decisions([{"candidate_id": "c1", "decision": "approve_candidate"}]),
        None,
    )
    assert summary.total_candidates == 0
    assert summary.approved_count == 1
    assert any("cross-checking was skipped" in w for w in summary.warnings)


def test_invalid_decision_warning_and_safety_notice():
    summary = analyze_llm_review_decisions(
        _decisions([{"candidate_id": "c1", "decision": "custom"}]),
        _result(["c1"]),
    )
    assert summary.invalid_decisions == ["c1: unknown action 'custom'"]
    assert "does not apply candidates" in summary.safety_notice
    assert "M5 truthfulness" in summary.safety_notice
