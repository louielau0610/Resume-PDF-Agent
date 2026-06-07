"""Tests for M23 LLM review decision Markdown output."""

from __future__ import annotations

from resume_pdf_agent.llm_review_decisions.markdown import (
    render_llm_review_decision_summary_markdown,
)
from resume_pdf_agent.models.llm_review_decisions import (
    LLMReviewCandidateDecisionSummary,
    LLMReviewDecisionSummary,
)


def _summary() -> LLMReviewDecisionSummary:
    return LLMReviewDecisionSummary(
        total_candidates=4,
        total_decisions=4,
        approved_count=1,
        rejected_count=1,
        needs_edit_count=1,
        note_count=1,
        ignored_count=1,
        approved_candidate_ids=["c1"],
        rejected_candidate_ids=["c2"],
        needs_edit_candidate_ids=["c3"],
        note_candidate_ids=["c3"],
        ignored_candidate_ids=["c4"],
        undecided_candidate_ids=[],
        warnings=["Approved LLM candidates remain advisory."],
        safety_notice="This summary does not apply candidates or verify truth.",
        candidate_summaries=[
            LLMReviewCandidateDecisionSummary(
                candidate_id="c3",
                action="needs_editing",
                normalized_action="needs_editing",
                has_note=True,
                note="Needs manual edit.",
            )
        ],
        summary="Test summary.",
    )


def test_markdown_includes_count_summary():
    md = render_llm_review_decision_summary_markdown(_summary())
    assert "LLM 候选总数" in md
    assert "Approved" in md
    assert "Rejected" in md


def test_markdown_includes_action_groups_and_notes():
    md = render_llm_review_decision_summary_markdown(_summary())
    assert "Approved Candidates" in md
    assert "`c1`" in md
    assert "Rejected Candidates" in md
    assert "`c2`" in md
    assert "Needs-Edit Candidates" in md
    assert "Needs manual edit." in md
    assert "Ignored Candidates" in md


def test_markdown_includes_warnings_and_safety_notice():
    md = render_llm_review_decision_summary_markdown(_summary())
    assert "Warnings" in md
    assert "Approved LLM candidates remain advisory." in md
    assert "Safety Notice" in md
    assert "不会应用候选" in md
    assert "does not apply candidates" in md


def test_markdown_does_not_claim_auto_application_or_fact_verification():
    md = render_llm_review_decision_summary_markdown(_summary()).lower()
    assert "automatically inserted" not in md
    assert "factually verified" not in md.replace("does not mean a claim is factually verified", "")
    assert "does not mean a claim is factually verified" in md
