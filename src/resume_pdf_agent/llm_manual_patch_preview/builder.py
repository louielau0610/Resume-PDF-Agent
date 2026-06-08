"""Deterministic M27 manual patch-preview builder. Generates preview artifacts only — no resume mutation."""

from __future__ import annotations

from resume_pdf_agent.llm_manual_patch_preview.diffing import (
    compute_diff_preview_lines,
    compute_unified_diff_preview,
)
from resume_pdf_agent.models.llm_application_plan import (
    LLMCandidateApplicationPlan,
    LLMCandidateApplicationPlanItem,
)
from resume_pdf_agent.models.llm_manual_patch_preview import (
    LLMManualPatchPreviewBlockReason,
    LLMManualPatchPreviewItem,
    LLMManualPatchPreviewReport,
    LLMManualPatchPreviewStatus,
)
from resume_pdf_agent.models.llm_pre_application_validation import (
    LLMPreApplicationValidationItem,
    LLMPreApplicationValidationReport,
    LLMPreApplicationValidationStatus,
)

_SAFETY_NOTICE = (
    "This is a preview-only artifact. No LLM candidates were applied. "
    "No executable patch was generated. The final resume was not modified. "
    "Passing validation does not mean factual verification. "
    "M5 truthfulness and M14 confirmation safeguards still apply. "
    "A human must manually inspect every original and proposed text before any future manual replacement."
)


def _build_preview_item(
    plan_item: LLMCandidateApplicationPlanItem,
    val_item: LLMPreApplicationValidationItem | None,
) -> LLMManualPatchPreviewItem:
    cid = plan_item.candidate_id
    reasons: list[str] = []
    safety_notes: list[str] = [
        "Preview only — no candidate has been applied.",
        "A human must manually inspect and decide.",
        "M5 truthfulness and M14 confirmation still apply.",
    ]

    # Default: skipped
    status = LLMManualPatchPreviewStatus.SKIPPED
    can_copy = False
    original = plan_item.original_text or ""
    proposed = plan_item.candidate_text or ""
    diff_lines: list[str] = []
    unified_diff: str | None = None

    # Gate: validation item must exist
    if val_item is None:
        reasons.append(LLMManualPatchPreviewBlockReason.MISSING_VALIDATION_ITEM.value)
        return LLMManualPatchPreviewItem(
            candidate_id=cid,
            preview_status=LLMManualPatchPreviewStatus.SKIPPED,
            block_reasons=reasons,
            safety_notes=safety_notes,
            manual_instruction="Missing validation item — cannot generate preview.",
        )

    # Gate: validation status
    vstatus = val_item.validation_status
    if vstatus == LLMPreApplicationValidationStatus.BLOCKED:
        reasons.append(LLMManualPatchPreviewBlockReason.CANDIDATE_BLOCKED_BY_M26.value)
        status = LLMManualPatchPreviewStatus.BLOCKED
    elif vstatus == LLMPreApplicationValidationStatus.NEEDS_MANUAL_EDIT:
        reasons.append(LLMManualPatchPreviewBlockReason.CANDIDATE_NEEDS_CONFIRMATION.value)
        status = LLMManualPatchPreviewStatus.NEEDS_MANUAL_EDIT
    elif vstatus == LLMPreApplicationValidationStatus.EXCLUDED:
        status = LLMManualPatchPreviewStatus.EXCLUDED
    elif vstatus == LLMPreApplicationValidationStatus.UNMAPPED:
        status = LLMManualPatchPreviewStatus.UNMAPPED
    elif vstatus == LLMPreApplicationValidationStatus.SKIPPED:
        status = LLMManualPatchPreviewStatus.SKIPPED
    elif vstatus == LLMPreApplicationValidationStatus.WARNING:
        reasons.append(LLMManualPatchPreviewBlockReason.CANDIDATE_HAS_VALIDATION_WARNINGS.value)
        status = LLMManualPatchPreviewStatus.BLOCKED
    elif vstatus == LLMPreApplicationValidationStatus.PASSED:
        # passed — check if can proceed
        if not val_item.can_proceed_to_patch_preview:
            reasons.append(LLMManualPatchPreviewBlockReason.VALIDATION_NOT_PASSED.value)
            status = LLMManualPatchPreviewStatus.BLOCKED
        else:
            # Data completeness checks
            if not original.strip():
                reasons.append(LLMManualPatchPreviewBlockReason.MISSING_ORIGINAL_TEXT.value)
                status = LLMManualPatchPreviewStatus.BLOCKED
            if not proposed.strip():
                reasons.append(LLMManualPatchPreviewBlockReason.MISSING_CANDIDATE_TEXT.value)
                status = LLMManualPatchPreviewStatus.BLOCKED
            if not plan_item.target_section:
                reasons.append(LLMManualPatchPreviewBlockReason.MISSING_TARGET_SECTION.value)
                if status.value != "blocked":
                    status = LLMManualPatchPreviewStatus.UNMAPPED
            if not plan_item.target_item_id:
                reasons.append(LLMManualPatchPreviewBlockReason.MISSING_TARGET_ITEM_ID.value)
                if status.value != "blocked":
                    status = LLMManualPatchPreviewStatus.UNMAPPED
            if original.strip() == proposed.strip():
                reasons.append(LLMManualPatchPreviewBlockReason.CANDIDATE_TEXT_SAME_AS_ORIGINAL.value)

            if status not in (LLMManualPatchPreviewStatus.BLOCKED, LLMManualPatchPreviewStatus.UNMAPPED):
                # Generate diff preview
                diff_lines = compute_diff_preview_lines(original, proposed)
                unified_diff = compute_unified_diff_preview(original, proposed)
                status = LLMManualPatchPreviewStatus.PREVIEW_READY
                can_copy = True

    # Always add truthfulness/confirmation notice
    reasons.append(LLMManualPatchPreviewBlockReason.TRUTHFULNESS_NOT_VERIFIED.value)
    reasons.append(LLMManualPatchPreviewBlockReason.CONFIRMATION_REQUIRED.value)
    reasons.append(LLMManualPatchPreviewBlockReason.EXECUTABLE_PATCH_FORBIDDEN.value)
    reasons.append(LLMManualPatchPreviewBlockReason.MANUAL_REVIEW_REQUIRED.value)

    instruction = (
        f"候选 {cid}：请手动比较原文与建议文本。"
        if status == LLMManualPatchPreviewStatus.PREVIEW_READY
        else f"候选 {cid}：被阻塞，原因是 {', '.join(reasons[:3])}。"
    )

    return LLMManualPatchPreviewItem(
        candidate_id=cid,
        preview_status=status,
        target_section=plan_item.target_section,
        target_item_id=plan_item.target_item_id,
        original_text=original or None,
        proposed_text=proposed or None,
        diff_preview=diff_lines,
        unified_diff_preview=unified_diff,
        validation_status=vstatus.value,
        block_reasons=reasons,
        safety_notes=safety_notes,
        manual_instruction=instruction,
        can_copy_for_manual_review=can_copy,
    )


def build_manual_patch_preview(
    plan: LLMCandidateApplicationPlan,
    validation: LLMPreApplicationValidationReport,
) -> LLMManualPatchPreviewReport:
    """Build a deterministic manual patch-preview report from M24 plan and M26 validation."""

    global_warnings: list[str] = []

    # Gate: validation report must be validation-only
    if not validation.validation_only:
        global_warnings.append("M26 validation report is not validation_only=True. All items blocked.")
        # Block all items
        blocked_items: list[LLMManualPatchPreviewItem] = []
        for plan_item in plan.items:
            blocked_items.append(LLMManualPatchPreviewItem(
                candidate_id=plan_item.candidate_id,
                preview_status=LLMManualPatchPreviewStatus.BLOCKED,
                block_reasons=[LLMManualPatchPreviewBlockReason.VALIDATION_REPORT_NOT_VALIDATION_ONLY.value],
                safety_notes=["Validation report is not validation-only."],
                manual_instruction=f"候选 {plan_item.candidate_id}：M26 验证报告不是 validation_only=True，已阻塞。",
            ))
        return LLMManualPatchPreviewReport(
            total_items=len(blocked_items),
            blocked_count=len(blocked_items),
            items=blocked_items,
            global_warnings=global_warnings,
            safety_notice=_SAFETY_NOTICE,
            source_files={"plan": "provided via --plan", "validation": "provided via --validation"},
            summary="All items blocked: validation report is not validation_only=True.",
        )

    if validation.final_resume_modified:
        global_warnings.append("M26 validation report indicates final_resume_modified=True. All items blocked.")

    if validation.patch_generated:
        global_warnings.append("M26 validation report indicates patch_generated=True. All items blocked.")

    # Build validation item lookup
    val_map: dict[str, LLMPreApplicationValidationItem] = {}
    for vi in validation.items:
        val_map[vi.candidate_id] = vi

    items: list[LLMManualPatchPreviewItem] = []
    for plan_item in plan.items:
        val_item = val_map.get(plan_item.candidate_id)
        if val_item is None:
            global_warnings.append(f"Plan item '{plan_item.candidate_id}' has no matching validation item.")

        pv = _build_preview_item(plan_item, val_item)
        items.append(pv)

    # Counts
    ready = sum(1 for i in items if i.preview_status == LLMManualPatchPreviewStatus.PREVIEW_READY)
    blocked = sum(1 for i in items if i.preview_status == LLMManualPatchPreviewStatus.BLOCKED)
    needs_edit = sum(1 for i in items if i.preview_status == LLMManualPatchPreviewStatus.NEEDS_MANUAL_EDIT)
    excluded = sum(1 for i in items if i.preview_status == LLMManualPatchPreviewStatus.EXCLUDED)
    unmapped = sum(1 for i in items if i.preview_status == LLMManualPatchPreviewStatus.UNMAPPED)
    skipped = sum(1 for i in items if i.preview_status == LLMManualPatchPreviewStatus.SKIPPED)

    return LLMManualPatchPreviewReport(
        total_items=len(items),
        preview_ready_count=ready,
        blocked_count=blocked,
        needs_manual_edit_count=needs_edit,
        excluded_count=excluded,
        unmapped_count=unmapped,
        skipped_count=skipped,
        items=items,
        global_warnings=global_warnings,
        safety_notice=_SAFETY_NOTICE,
        source_files={"plan": "provided via --plan", "validation": "provided via --validation"},
        summary=(
            f"Manual patch preview: {ready} ready, {blocked} blocked, "
            f"{needs_edit} needs edit, {excluded} excluded, "
            f"{unmapped} unmapped, {skipped} skipped. "
            f"Preview only — no candidates applied, no executable patch generated."
        ),
    )
