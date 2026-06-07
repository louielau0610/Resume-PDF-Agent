"""UI context builder for M22 browser LLM rewrite review UI."""

from __future__ import annotations

from resume_pdf_agent.llm_review_ui.safety import (
    get_llm_review_decision_options,
    validate_llm_rewrite_result_for_ui,
)
from resume_pdf_agent.models.llm import LLMRewriteResult
from resume_pdf_agent.models.llm_review_ui import (
    LLMReviewCandidateView,
    LLMReviewUIOptions,
)


def _build_candidate_view(c) -> LLMReviewCandidateView:
    return LLMReviewCandidateView(
        candidate_id=c.candidate_id,
        source_experience_id=c.source_experience_id if c.source_experience_id else None,
        original_text=c.original_text,
        rewritten_text=c.rewritten_text,
        provider=c.provider.value if hasattr(c.provider, "value") else str(c.provider),
        mode=c.mode.value if hasattr(c.mode, "value") else str(c.mode),
        status=c.status.value if hasattr(c.status, "value") else str(c.status),
        evidence_level=c.evidence_level.value if hasattr(c.evidence_level, "value") else str(c.evidence_level),
        metric_status=c.metric_status.value if hasattr(c.metric_status, "value") else str(c.metric_status),
        needs_confirmation=c.needs_confirmation,
        validation_warnings=list(c.validation_warnings),
        risk_flags=list(c.risk_flags),
        rationale=c.rationale if c.rationale else None,
    )


def _group_candidates(
    views: list[LLMReviewCandidateView],
) -> dict:
    requires_confirmation: list[dict] = []
    with_warnings: list[dict] = []
    with_risks: list[dict] = []
    clean: list[dict] = []

    for v in views:
        d = v.model_dump()
        if v.needs_confirmation:
            requires_confirmation.append(d)
        elif v.risk_flags:
            with_risks.append(d)
        elif v.validation_warnings:
            with_warnings.append(d)
        else:
            clean.append(d)
    # Also add confirmations that have risks/warnings to those groups
    for v in views:
        d = v.model_dump()
        if v.needs_confirmation:
            if v.risk_flags and d not in with_risks:
                with_risks.append(d)
            if v.validation_warnings and d not in with_warnings:
                with_warnings.append(d)

    return {
        "requires_confirmation": requires_confirmation,
        "validation_warnings": with_warnings,
        "risk_flags": with_risks,
        "clean_candidates": clean,
    }


def build_llm_review_ui_context(
    rewrite_result: LLMRewriteResult,
    options: LLMReviewUIOptions | None = None,
) -> dict:
    opts = options or LLMReviewUIOptions()

    ui_warnings = validate_llm_rewrite_result_for_ui(rewrite_result)
    all_warnings = list(rewrite_result.warnings) + ui_warnings

    candidate_views = [_build_candidate_view(c) for c in rewrite_result.candidates]
    groups = _group_candidates(candidate_views)

    decision_options = get_llm_review_decision_options()

    return {
        "page_title": "LLM Rewrite Review / LLM改写审阅",
        "provider": (
            rewrite_result.provider.value
            if hasattr(rewrite_result.provider, "value")
            else str(rewrite_result.provider)
        ),
        "rewrite_status": (
            rewrite_result.status.value
            if hasattr(rewrite_result.status, "value")
            else str(rewrite_result.status)
        ),
        "candidate_count": rewrite_result.candidates_generated,
        "candidates_requiring_confirmation": rewrite_result.candidates_requiring_confirmation,
        "warnings": all_warnings,
        "errors": rewrite_result.errors,
        "summary": rewrite_result.summary,
        "groups": groups,
        "decision_options": decision_options,
        "safety_notice": (
            "LLM rewrite candidates are wording suggestions only. "
            "Approve only text you can personally verify. "
            "This page does not apply candidates automatically, "
            "does not verify real-world truth, "
            "and does not bypass M14 confirmation. "
            "M5 truthfulness checks and M14 confirmation gate remain authoritative."
        ),
        "cli_instructions": [
            "Generate mock LLM candidates: py -m resume_pdf_agent run-sample --output-dir outputs/llm_review_demo --pdf-backend mock --enable-llm-rewriting --llm-provider mock --write-frontend-page",
            "Render review UI: py -m resume_pdf_agent render-llm-review-ui --result outputs/llm_review_demo/llm_rewrite_result.json --output outputs/llm_review_demo/llm_review.html",
            "The generated llm_rewrite_review_decisions.json is advisory only and not automatically applied.",
        ],
        "options": {
            "include_copy_buttons": opts.include_copy_buttons,
            "include_download_buttons": opts.include_download_buttons,
            "include_risk_filters": opts.include_risk_filters,
            "include_decision_controls": opts.include_decision_controls,
            "include_cli_instructions": opts.include_cli_instructions,
            "include_safety_notice": opts.include_safety_notice,
            "language": opts.language,
        },
    }
