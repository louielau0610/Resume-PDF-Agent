"""Deterministic M26 strict pre-application validator."""

from __future__ import annotations

from resume_pdf_agent.models.llm import LLMRewriteResult
from resume_pdf_agent.models.llm_application_plan import (
    LLMApplicationPlanStatus,
    LLMCandidateApplicationPlan,
    LLMCandidateApplicationPlanItem,
)
from resume_pdf_agent.models.llm_pre_application_validation import (
    LLMPreApplicationBlockReason,
    LLMPreApplicationValidationItem,
    LLMPreApplicationValidationReport,
    LLMPreApplicationValidationStatus,
)
from resume_pdf_agent.models.llm_review_decisions import (
    LLMReviewDecisionFile,
    LLMReviewDecisionSummary,
)

_SAFETY_NOTICE = (
    "This is a validation-only artifact. No LLM candidates were applied. "
    "No patch was generated. The final resume was not modified. "
    "Passing validation does not mean factual verification. "
    "M5 truthfulness and M14 confirmation safeguards still apply."
)

_UNSAFE_CLAIM_INDICATORS: list[str] = [
    "guaranteed",
    "100%",
    "top 1%",
    "officially certified",
    "led the entire company",
    "revenue increased",
    "saved $",
    "hired",
    "admitted",
    "accepted",
    "offer guaranteed",
]

_CANDIDATE_TEXT_MIN_LENGTH = 2
_CANDIDATE_TEXT_MAX_LENGTH = 2000


def _build_source_files(
    result: LLMRewriteResult | None,
    decisions_file: LLMReviewDecisionFile | None,
    summary: LLMReviewDecisionSummary | None,
) -> dict[str, str]:
    """Build source_files dict with only string values."""
    src: dict[str, str] = {"plan": "provided via --plan"}
    if result:
        src["result"] = "provided via --result"
    if decisions_file:
        src["decisions"] = "provided via --decisions"
    if summary:
        src["summary"] = "provided via --summary"
    return src


def _has_unsafe_claim_indicators(text: str) -> list[str]:
    """Return matching unsafe claim indicator keywords (deterministic only)."""
    lower = text.lower()
    return [kw for kw in _UNSAFE_CLAIM_INDICATORS if kw in lower]


def _validate_plan_item(
    item: LLMCandidateApplicationPlanItem,
    plan: LLMCandidateApplicationPlan,
    result: LLMRewriteResult | None,
    decision_map: dict[str, object] | None,
    summary: LLMReviewDecisionSummary | None,
    duplicate_ids: set[str],
    known_candidate_ids: set[str],
) -> LLMPreApplicationValidationItem:
    cid = item.candidate_id
    reasons: list[str] = []
    notes: list[str] = []
    warnings: list[str] = list(item.validation_warnings)
    can_proceed = True

    # Plan-level checks
    if not plan.plan_only:
        reasons.append(LLMPreApplicationBlockReason.PLAN_NOT_PLAN_ONLY.value)
        can_proceed = False

    # Candidate-level checks
    if not cid or not cid.strip():
        reasons.append(LLMPreApplicationBlockReason.MISSING_CANDIDATE_ID.value)
        can_proceed = False

    if not item.original_text or not item.original_text.strip():
        reasons.append(LLMPreApplicationBlockReason.MISSING_ORIGINAL_TEXT.value)
        can_proceed = False

    candidate_text = item.candidate_text or ""
    if not candidate_text.strip():
        reasons.append(LLMPreApplicationBlockReason.EMPTY_CANDIDATE_TEXT.value)
        can_proceed = False

    if item.original_text and candidate_text and item.original_text.strip() == candidate_text.strip():
        reasons.append(LLMPreApplicationBlockReason.CANDIDATE_SAME_AS_ORIGINAL.value)
        warnings.append("Candidate text is identical to original text.")
        # Not blocking, just warning

    if candidate_text:
        if len(candidate_text) > _CANDIDATE_TEXT_MAX_LENGTH:
            reasons.append(LLMPreApplicationBlockReason.CANDIDATE_TOO_LONG.value)
            warnings.append(f"Candidate text exceeds {_CANDIDATE_TEXT_MAX_LENGTH} characters.")
            can_proceed = False
        if len(candidate_text) < _CANDIDATE_TEXT_MIN_LENGTH:
            reasons.append(LLMPreApplicationBlockReason.CANDIDATE_TOO_SHORT.value)
            warnings.append(f"Candidate text is shorter than {_CANDIDATE_TEXT_MIN_LENGTH} characters.")
            can_proceed = False

    # Unsafe claim indicators (deterministic keyword check)
    if candidate_text:
        unsafe = _has_unsafe_claim_indicators(candidate_text)
        if unsafe:
            reasons.append(LLMPreApplicationBlockReason.UNSAFE_CLAIM_INDICATOR.value)
            warnings.append(f"Unsafe claim indicators detected: {', '.join(unsafe)}")
            can_proceed = False

    # Target mapping
    if not item.target_section:
        reasons.append(LLMPreApplicationBlockReason.MISSING_TARGET_SECTION.value)
        can_proceed = False
    if not item.target_item_id:
        reasons.append(LLMPreApplicationBlockReason.MISSING_TARGET_ITEM_ID.value)
        can_proceed = False

    # Plan status routing
    if item.plan_status == LLMApplicationPlanStatus.NEEDS_MANUAL_EDIT:
        status = LLMPreApplicationValidationStatus.NEEDS_MANUAL_EDIT
        reasons.append(LLMPreApplicationBlockReason.CANDIDATE_NEEDS_EDIT.value)
        can_proceed = False
        notes.append("Candidate requires manual editing before it can pass validation.")
    elif item.plan_status == LLMApplicationPlanStatus.EXCLUDED:
        status = LLMPreApplicationValidationStatus.EXCLUDED
        reasons.append(LLMPreApplicationBlockReason.CANDIDATE_REJECTED.value)
        can_proceed = False
    elif item.plan_status == LLMApplicationPlanStatus.UNMAPPED:
        status = LLMPreApplicationValidationStatus.UNMAPPED
        reasons.append(LLMPreApplicationBlockReason.CANDIDATE_UNMAPPED.value)
        can_proceed = False
    elif item.plan_status == LLMApplicationPlanStatus.BLOCKED:
        status = LLMPreApplicationValidationStatus.BLOCKED
        can_proceed = False
    elif item.plan_status == LLMApplicationPlanStatus.PLANNED:
        # planned candidates may still be blocked by other checks
        if item.needs_confirmation:
            reasons.append(LLMPreApplicationBlockReason.NEEDS_CONFIRMATION.value)
            can_proceed = False
        if item.validation_warnings:
            reasons.append(LLMPreApplicationBlockReason.HAS_VALIDATION_WARNINGS.value)
            # Not blocking by itself, but noted
        if not can_proceed:
            status = LLMPreApplicationValidationStatus.BLOCKED
        elif reasons:
            status = LLMPreApplicationValidationStatus.WARNING
        else:
            status = LLMPreApplicationValidationStatus.PASSED
    else:
        status = LLMPreApplicationValidationStatus.SKIPPED
        can_proceed = False

    # Truthfulness/confirmation always required
    reasons.append(LLMPreApplicationBlockReason.TRUTHFULNESS_NOT_VERIFIED.value)
    reasons.append(LLMPreApplicationBlockReason.CONFIRMATION_REQUIRED.value)
    notes.append("M5 truthfulness and M14 confirmation safeguards still apply.")

    # Cross-check with result if available
    if result and cid not in known_candidate_ids:
        warnings.append(f"Candidate ID '{cid}' not found in llm_rewrite_result.json.")
        reasons.append(LLMPreApplicationBlockReason.UNKNOWN_CANDIDATE_ID.value)
        can_proceed = False

    # Cross-check with decisions
    if decision_map is not None:
        if cid in duplicate_ids:
            reasons.append(LLMPreApplicationBlockReason.DUPLICATE_DECISION.value)
            warnings.append(f"Duplicate decision for candidate '{cid}'.")
            can_proceed = False

    # Cross-check with summary
    if summary:
        for sw in summary.warnings:
            if cid.lower() in sw.lower() or "candidate" in sw.lower():
                warnings.append(f"Summary warning: {sw}")

    return LLMPreApplicationValidationItem(
        candidate_id=cid,
        source_plan_status=item.plan_status.value,
        validation_status=status,
        target_section=item.target_section,
        target_item_id=item.target_item_id,
        original_text_present=bool(item.original_text and item.original_text.strip()),
        candidate_text_present=bool(candidate_text.strip()),
        needs_confirmation=item.needs_confirmation,
        validation_warnings=warnings,
        block_reasons=reasons,
        manual_review_notes=notes,
        can_proceed_to_patch_preview=can_proceed,
        safety_notes=[
            "Validation only: do not apply candidates.",
            "No patch was generated.",
            "The final resume was not modified.",
        ],
    )


def validate_pre_application(
    plan: LLMCandidateApplicationPlan,
    result: LLMRewriteResult | None = None,
    decisions_file: LLMReviewDecisionFile | None = None,
    summary: LLMReviewDecisionSummary | None = None,
    strict: bool = False,
) -> LLMPreApplicationValidationReport:
    """Validate an M24 application plan for M26 pre-application safety."""

    global_warnings: list[str] = []

    # Plan-level gate
    if not plan.plan_only:
        global_warnings.append("Plan does not have plan_only=True — this is not a valid plan-only artifact.")

    # Build decision map and detect duplicates
    decision_map: dict[str, object] | None = None
    duplicate_ids: set[str] = set()
    if decisions_file:
        decision_map = {}
        seen: dict[str, int] = {}
        for d in decisions_file.decisions:
            cid = d.candidate_id
            if cid in seen:
                duplicate_ids.add(cid)
                seen[cid] += 1
            else:
                seen[cid] = 1
            if cid not in decision_map:
                decision_map[cid] = d
        if duplicate_ids:
            global_warnings.append(f"Duplicate decisions detected for: {', '.join(sorted(duplicate_ids))}")

    # Build known candidate IDs from result
    known_candidate_ids: set[str] = set()
    if result:
        for c in result.candidates:
            known_candidate_ids.add(c.candidate_id)

    # Cross-check warnings
    if not result:
        global_warnings.append("No llm_rewrite_result.json provided; candidate ID cross-check skipped.")
    if not decisions_file:
        global_warnings.append("No llm_rewrite_review_decisions.json provided; decision cross-check skipped.")
    if not summary:
        global_warnings.append("No llm_rewrite_review_decision_summary.json provided; summary cross-check skipped.")

    if summary:
        for sw in summary.warnings:
            global_warnings.append(f"Summary: {sw}")

    items: list[LLMPreApplicationValidationItem] = []
    for item in plan.items:
        vi = _validate_plan_item(
            item, plan, result, decision_map, summary, duplicate_ids, known_candidate_ids
        )
        items.append(vi)

    # Counts
    passed = sum(1 for i in items if i.validation_status == LLMPreApplicationValidationStatus.PASSED)
    blocked = sum(1 for i in items if i.validation_status == LLMPreApplicationValidationStatus.BLOCKED)
    needs_edit = sum(1 for i in items if i.validation_status == LLMPreApplicationValidationStatus.NEEDS_MANUAL_EDIT)
    excluded = sum(1 for i in items if i.validation_status == LLMPreApplicationValidationStatus.EXCLUDED)
    unmapped = sum(1 for i in items if i.validation_status == LLMPreApplicationValidationStatus.UNMAPPED)
    warning = sum(1 for i in items if i.validation_status == LLMPreApplicationValidationStatus.WARNING)

    can_proceed = blocked == 0 and needs_edit == 0 and excluded == 0 and unmapped == 0

    if strict and global_warnings:
        can_proceed = False

    return LLMPreApplicationValidationReport(
        total_plan_items=len(items),
        passed_count=passed,
        blocked_count=blocked,
        needs_manual_edit_count=needs_edit,
        excluded_count=excluded,
        unmapped_count=unmapped,
        warning_count=warning,
        can_proceed_to_patch_preview=can_proceed,
        items=items,
        global_warnings=global_warnings,
        safety_notice=_SAFETY_NOTICE,
        source_files=_build_source_files(result, decisions_file, summary),
        validation_only=True,
        final_resume_modified=False,
        patch_generated=False,
        summary=(
            f"Pre-application validation: {passed} passed, {blocked} blocked, "
            f"{needs_edit} needs edit, {excluded} excluded, {unmapped} unmapped, "
            f"{warning} warnings. "
            f"{'Can' if can_proceed else 'Cannot'} proceed to patch preview."
        ),
    )
