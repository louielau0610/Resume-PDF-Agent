"""Tests for M22 LLM review UI context builder."""

from __future__ import annotations

from resume_pdf_agent.llm_review_ui.context import build_llm_review_ui_context
from resume_pdf_agent.models.llm import (
    LLMProviderType,
    LLMRewriteCandidate,
    LLMRewriteMode,
    LLMRewriteResult,
    LLMRewriteStatus,
)
from resume_pdf_agent.models.llm_review_ui import LLMReviewUIOptions


def _make_mock_result() -> LLMRewriteResult:
    candidates = [
        LLMRewriteCandidate(
            candidate_id="c1",
            source_experience_id="exp1",
            original_text="Built data pipelines.",
            rewritten_text="Designed and implemented scalable data pipelines processing 1M+ records daily.",
            provider=LLMProviderType.MOCK,
            mode=LLMRewriteMode.CONSERVATIVE_POLISH,
            status=LLMRewriteStatus.REWRITTEN,
            needs_confirmation=True,
            validation_warnings=["Missing metric verification"],
        ),
        LLMRewriteCandidate(
            candidate_id="c2",
            source_experience_id="exp2",
            original_text="Used Python for analysis.",
            rewritten_text="Leveraged Python for statistical analysis and modeling.",
            provider=LLMProviderType.MOCK,
            mode=LLMRewriteMode.CONSERVATIVE_POLISH,
            status=LLMRewriteStatus.REWRITTEN_WITH_WARNINGS,
            needs_confirmation=False,
            risk_flags=["vague_improvement"],
        ),
        LLMRewriteCandidate(
            candidate_id="c3",
            source_experience_id="exp3",
            original_text="Worked on team projects.",
            rewritten_text="Collaborated on cross-functional team projects.",
            provider=LLMProviderType.MOCK,
            mode=LLMRewriteMode.CONSERVATIVE_POLISH,
            status=LLMRewriteStatus.REWRITTEN,
            needs_confirmation=False,
        ),
    ]
    return LLMRewriteResult(
        status=LLMRewriteStatus.REWRITTEN_WITH_WARNINGS,
        provider=LLMProviderType.MOCK,
        candidates=candidates,
        candidates_generated=3,
        candidates_requiring_confirmation=1,
        summary="Mock rewrite result.",
    )


def test_build_llm_review_ui_context_importable():
    """build_llm_review_ui_context is importable and callable."""
    assert callable(build_llm_review_ui_context)


def test_context_returns_dict_with_required_keys():
    """Context returns a dict with all expected top-level keys."""
    result = _make_mock_result()
    ctx = build_llm_review_ui_context(result)
    assert isinstance(ctx, dict)
    assert "page_title" in ctx
    assert "provider" in ctx
    assert "rewrite_status" in ctx
    assert "candidate_count" in ctx
    assert "candidates_requiring_confirmation" in ctx
    assert "warnings" in ctx
    assert "errors" in ctx
    assert "groups" in ctx
    assert "decision_options" in ctx
    assert "safety_notice" in ctx
    assert "cli_instructions" in ctx
    assert "options" in ctx


def test_context_includes_safety_notice():
    """Context includes safety notice about suggestions only."""
    result = _make_mock_result()
    ctx = build_llm_review_ui_context(result)
    notice = ctx["safety_notice"].lower()
    assert "suggestions" in notice
    assert "personally verify" in notice
    assert "does not apply" in notice or "not apply" in notice
    assert "m14" in notice or "confirmation" in notice


def test_context_decision_options_include_approve():
    """Decision options include approve_candidate."""
    result = _make_mock_result()
    ctx = build_llm_review_ui_context(result)
    values = [d["value"] for d in ctx["decision_options"]]
    assert "approve_candidate" in values


def test_context_decision_options_include_reject():
    """Decision options include reject_candidate."""
    result = _make_mock_result()
    ctx = build_llm_review_ui_context(result)
    values = [d["value"] for d in ctx["decision_options"]]
    assert "reject_candidate" in values


def test_context_decision_options_include_needs_editing():
    """Decision options include needs_editing."""
    result = _make_mock_result()
    ctx = build_llm_review_ui_context(result)
    values = [d["value"] for d in ctx["decision_options"]]
    assert "needs_editing" in values


def test_context_decision_options_include_provide_note():
    """Decision options include provide_note."""
    result = _make_mock_result()
    ctx = build_llm_review_ui_context(result)
    values = [d["value"] for d in ctx["decision_options"]]
    assert "provide_note" in values


def test_context_decision_options_include_ignore_for_now():
    """Decision options include ignore_for_now."""
    result = _make_mock_result()
    ctx = build_llm_review_ui_context(result)
    values = [d["value"] for d in ctx["decision_options"]]
    assert "ignore_for_now" in values


def test_context_groups_has_requires_confirmation():
    """Context groups include requires_confirmation."""
    result = _make_mock_result()
    ctx = build_llm_review_ui_context(result)
    assert "requires_confirmation" in ctx["groups"]
    assert len(ctx["groups"]["requires_confirmation"]) >= 1


def test_context_groups_has_validation_warnings():
    """Context groups include validation_warnings."""
    result = _make_mock_result()
    ctx = build_llm_review_ui_context(result)
    assert "validation_warnings" in ctx["groups"]


def test_context_groups_has_risk_flags():
    """Context groups include risk_flags."""
    result = _make_mock_result()
    ctx = build_llm_review_ui_context(result)
    assert "risk_flags" in ctx["groups"]


def test_context_groups_has_clean_candidates():
    """Context groups include clean_candidates."""
    result = _make_mock_result()
    ctx = build_llm_review_ui_context(result)
    assert "clean_candidates" in ctx["groups"]


def test_context_no_hiring_probability():
    """Context does not claim hiring probability prediction."""
    result = _make_mock_result()
    ctx = build_llm_review_ui_context(result)
    all_text = _flatten_context(ctx).lower()
    assert "hiring probability" not in all_text
    assert "offer probability" not in all_text


def test_context_no_internal_screening():
    """Context does not claim internal screening access."""
    result = _make_mock_result()
    ctx = build_llm_review_ui_context(result)
    all_text = _flatten_context(ctx).lower()
    assert "internal screening" not in all_text


def test_context_accepts_none_options():
    """Context builder works with None options."""
    result = _make_mock_result()
    ctx = build_llm_review_ui_context(result, None)
    assert ctx["options"]["include_safety_notice"] is True


def test_context_accepts_custom_options():
    """Context builder accepts custom options."""
    result = _make_mock_result()
    opts = LLMReviewUIOptions(include_safety_notice=False, language="en")
    ctx = build_llm_review_ui_context(result, opts)
    assert ctx["options"]["include_safety_notice"] is False
    assert ctx["options"]["language"] == "en"


def _flatten_context(ctx: dict) -> str:
    parts: list[str] = []
    for v in ctx.values():
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    for sv in item.values():
                        if isinstance(sv, str):
                            parts.append(sv)
        elif isinstance(v, dict):
            for sv in v.values():
                if isinstance(sv, str):
                    parts.append(sv)
                elif isinstance(sv, list):
                    for si in sv:
                        if isinstance(si, dict):
                            for ssv in si.values():
                                if isinstance(ssv, str):
                                    parts.append(ssv)
    return " ".join(parts)
