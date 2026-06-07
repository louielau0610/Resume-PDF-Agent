"""Deterministic M24 LLM candidate application planner."""

from __future__ import annotations

from collections import Counter

from resume_pdf_agent.models.llm import LLMRewriteCandidate, LLMRewriteResult
from resume_pdf_agent.models.llm_application_plan import (
    LLMApplicationBlockReason,
    LLMApplicationPlanStatus,
    LLMCandidateApplicationPlan,
    LLMCandidateApplicationPlanItem,
)
from resume_pdf_agent.models.llm_review_decisions import (
    LLMReviewDecision,
    LLMReviewDecisionAction,
    LLMReviewDecisionFile,
    LLMReviewDecisionSummary,
)

_SAFETY_NOTICE = (
    "This is a plan-only artifact. No LLM candidates were applied, the final "
    "resume was not modified, approval does not verify factual truth, and M5 "
    "truthfulness checks plus the M14 confirmation gate still apply before any "
    "future manual application."
)


def _decision_map(decision_file: LLMReviewDecisionFile) -> dict[str, LLMReviewDecision]:
    result: dict[str, LLMReviewDecision] = {}
    for decision in decision_file.decisions:
        if decision.candidate_id not in result:
            result[decision.candidate_id] = decision
    return result


def _risk_level(candidate: LLMRewriteCandidate) -> str | None:
    if candidate.risk_flags:
        return "risk_flags:" + ",".join(candidate.risk_flags)
    if candidate.validation_warnings:
        return "validation_warnings"
    if candidate.needs_confirmation:
        return "needs_confirmation"
    return None


def _base_item(
    candidate: LLMRewriteCandidate,
    decision: LLMReviewDecision | None,
    status: LLMApplicationPlanStatus,
    reasons: list[LLMApplicationBlockReason],
    notes: list[str],
    instruction: str,
) -> LLMCandidateApplicationPlanItem:
    target_id = candidate.source_experience_id
    return LLMCandidateApplicationPlanItem(
        candidate_id=candidate.candidate_id,
        source_action=(
            decision.normalized_action.value
            if decision and decision.normalized_action
            else (decision.action if decision else "undecided")
        ),
        plan_status=status,
        target_section="experience" if target_id else None,
        target_item_id=target_id,
        original_text=candidate.original_text,
        candidate_text=candidate.rewritten_text,
        provider=candidate.provider.value if hasattr(candidate.provider, "value") else str(candidate.provider),
        risk_level=_risk_level(candidate),
        needs_confirmation=candidate.needs_confirmation,
        validation_warnings=list(candidate.validation_warnings),
        block_reasons=reasons,
        manual_review_notes=notes,
        decision_note=decision.note if decision else None,
        application_instruction=instruction,
    )


def _classify_candidate(
    candidate: LLMRewriteCandidate,
    decision: LLMReviewDecision | None,
    duplicate_ids: set[str],
) -> LLMCandidateApplicationPlanItem:
    reasons: list[LLMApplicationBlockReason] = [
        LLMApplicationBlockReason.TRUTHFULNESS_NOT_VERIFIED,
        LLMApplicationBlockReason.CONFIRMATION_REQUIRED,
    ]
    notes: list[str] = [
        "Plan only: do not apply this candidate without manual review.",
        "M5 truthfulness and M14 confirmation safeguards still apply.",
    ]

    if not decision:
        reasons.append(LLMApplicationBlockReason.UNDECIDED)
        return _base_item(
            candidate,
            None,
            LLMApplicationPlanStatus.BLOCKED,
            reasons,
            notes,
            "No review decision exists; do not apply.",
        )

    action = decision.normalized_action
    if candidate.candidate_id in duplicate_ids:
        reasons.append(LLMApplicationBlockReason.DUPLICATE_DECISION)
    if not candidate.original_text or not candidate.original_text.strip():
        reasons.append(LLMApplicationBlockReason.MISSING_ORIGINAL_TEXT)
    if not candidate.rewritten_text or not candidate.rewritten_text.strip():
        reasons.append(LLMApplicationBlockReason.MISSING_CANDIDATE_TEXT)
    if not candidate.source_experience_id:
        reasons.append(LLMApplicationBlockReason.UNSAFE_OR_UNMAPPED_TARGET)
    if candidate.validation_warnings:
        reasons.append(LLMApplicationBlockReason.HAS_VALIDATION_WARNINGS)
    if candidate.needs_confirmation:
        reasons.append(LLMApplicationBlockReason.NEEDS_CONFIRMATION)

    if action is None:
        reasons.append(LLMApplicationBlockReason.UNSUPPORTED_ACTION)
        return _base_item(
            candidate,
            decision,
            LLMApplicationPlanStatus.BLOCKED,
            reasons,
            notes,
            "Unsupported decision action; do not apply.",
        )

    if action == LLMReviewDecisionAction.REJECT_CANDIDATE:
        return _base_item(
            candidate,
            decision,
            LLMApplicationPlanStatus.EXCLUDED,
            [LLMApplicationBlockReason.REJECTED],
            ["Rejected by reviewer; exclude from application planning."],
            "Excluded because the candidate was rejected.",
        )
    if action == LLMReviewDecisionAction.IGNORE_FOR_NOW:
        return _base_item(
            candidate,
            decision,
            LLMApplicationPlanStatus.EXCLUDED,
            [LLMApplicationBlockReason.IGNORED],
            ["Ignored by reviewer; exclude from application planning."],
            "Excluded because the candidate was ignored.",
        )
    if action == LLMReviewDecisionAction.NEEDS_EDITING:
        reasons.append(LLMApplicationBlockReason.NEEDS_EDIT)
        return _base_item(
            candidate,
            decision,
            LLMApplicationPlanStatus.NEEDS_MANUAL_EDIT,
            reasons,
            notes,
            "Manual edit is required before any future application.",
        )
    if action == LLMReviewDecisionAction.PROVIDE_NOTE:
        reasons.append(LLMApplicationBlockReason.NOT_APPROVED)
        return _base_item(
            candidate,
            decision,
            LLMApplicationPlanStatus.BLOCKED,
            reasons,
            notes,
            "Reviewer note is not approval; do not apply.",
        )

    # Approved candidates are still planned only when mapping and safety are clean.
    blocking = {
        LLMApplicationBlockReason.DUPLICATE_DECISION,
        LLMApplicationBlockReason.MISSING_ORIGINAL_TEXT,
        LLMApplicationBlockReason.MISSING_CANDIDATE_TEXT,
        LLMApplicationBlockReason.UNSAFE_OR_UNMAPPED_TARGET,
        LLMApplicationBlockReason.HAS_VALIDATION_WARNINGS,
        LLMApplicationBlockReason.NEEDS_CONFIRMATION,
    }
    active_blockers = [r for r in reasons if r in blocking]
    if active_blockers:
        status = (
            LLMApplicationPlanStatus.UNMAPPED
            if LLMApplicationBlockReason.UNSAFE_OR_UNMAPPED_TARGET in active_blockers
            else LLMApplicationPlanStatus.BLOCKED
        )
        return _base_item(
            candidate,
            decision,
            status,
            reasons,
            notes,
            "Approved but blocked for manual safety review; do not apply automatically.",
        )

    return _base_item(
        candidate,
        decision,
        LLMApplicationPlanStatus.PLANNED,
        [LLMApplicationBlockReason.TRUTHFULNESS_NOT_VERIFIED],
        ["Eligible for future manual application planning only."],
        "Plan-only: compare original_text and candidate_text manually before any future application.",
    )


def plan_llm_candidate_application(
    rewrite_result: LLMRewriteResult,
    decision_file: LLMReviewDecisionFile,
    decision_summary: LLMReviewDecisionSummary | None = None,
    *,
    result_path: str | None = None,
    decisions_path: str | None = None,
    summary_path: str | None = None,
) -> LLMCandidateApplicationPlan:
    """Create a deterministic plan-only application artifact."""

    decision_ids = [d.candidate_id for d in decision_file.decisions]
    duplicate_ids = {cid for cid, count in Counter(decision_ids).items() if count > 1}
    decisions = _decision_map(decision_file)

    items = [
        _classify_candidate(candidate, decisions.get(candidate.candidate_id), duplicate_ids)
        for candidate in rewrite_result.candidates
    ]

    candidate_ids = {c.candidate_id for c in rewrite_result.candidates}
    unknown_decision_ids = sorted(set(decision_ids) - candidate_ids)
    warnings: list[str] = []
    if unknown_decision_ids:
        warnings.append(
            "Review decisions reference unknown candidate IDs: " + ", ".join(unknown_decision_ids)
        )
    if duplicate_ids:
        warnings.append(
            "Duplicate review decisions block affected candidates: " + ", ".join(sorted(duplicate_ids))
        )
    if decision_summary is None:
        warnings.append(
            "No M23 decision summary was provided; plan was generated directly from result and decisions."
        )
    elif decision_summary.warnings:
        warnings.extend("M23 summary warning: " + w for w in decision_summary.warnings)

    warnings.append("Application plan is advisory only; no resume artifacts were modified.")

    counts = Counter(item.plan_status for item in items)
    source_files = {
        "llm_rewrite_result": result_path or "",
        "llm_rewrite_review_decisions": decisions_path or "",
    }
    if summary_path:
        source_files["llm_rewrite_review_decision_summary"] = summary_path

    return LLMCandidateApplicationPlan(
        total_candidates=len(rewrite_result.candidates),
        total_decisions=len(decision_file.decisions),
        planned_count=counts[LLMApplicationPlanStatus.PLANNED],
        blocked_count=counts[LLMApplicationPlanStatus.BLOCKED],
        needs_manual_edit_count=counts[LLMApplicationPlanStatus.NEEDS_MANUAL_EDIT],
        excluded_count=counts[LLMApplicationPlanStatus.EXCLUDED],
        unmapped_count=counts[LLMApplicationPlanStatus.UNMAPPED],
        items=items,
        warnings=warnings,
        safety_notice=_SAFETY_NOTICE,
        source_files=source_files,
        plan_only=True,
        summary=(
            f"Plan-only LLM candidate application plan: {len(items)} candidates, "
            f"{counts[LLMApplicationPlanStatus.PLANNED]} planned, "
            f"{counts[LLMApplicationPlanStatus.BLOCKED]} blocked, "
            f"{counts[LLMApplicationPlanStatus.NEEDS_MANUAL_EDIT]} need manual edit, "
            f"{counts[LLMApplicationPlanStatus.EXCLUDED]} excluded, "
            f"{counts[LLMApplicationPlanStatus.UNMAPPED]} unmapped."
        ),
    )
