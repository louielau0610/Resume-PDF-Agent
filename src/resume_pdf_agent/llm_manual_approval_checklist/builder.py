"""Deterministic M28 manual approval checklist builder. Human-only — no application, no patch."""

from __future__ import annotations

from resume_pdf_agent.models.llm_manual_approval_checklist import (
    LLMManualApprovalChecklistItem,
    LLMManualApprovalChecklistItemStatus,
    LLMManualApprovalChecklistQuestion,
    LLMManualApprovalChecklistQuestionType,
    LLMManualApprovalChecklistReport,
)
from resume_pdf_agent.models.llm_manual_patch_preview import (
    LLMManualPatchPreviewItem,
    LLMManualPatchPreviewReport,
    LLMManualPatchPreviewStatus,
)

_SAFETY_NOTICE = (
    "This is a checklist-only artifact. No LLM candidates were applied. "
    "No final approval has been granted by the system. "
    "No executable patch was generated. The final resume was not modified. "
    "Checklist completion does not mean factual verification. "
    "M5 truthfulness and M14 confirmation safeguards still apply. "
    "A human must manually answer every question and make the final decision."
)


def _questions_for_review(candidate_id: str) -> list[LLMManualApprovalChecklistQuestion]:
    return [
        LLMManualApprovalChecklistQuestion(
            question_id=f"{candidate_id}_truth_evidence",
            question_type=LLMManualApprovalChecklistQuestionType.TRUTHFULNESS_EVIDENCE,
            prompt="建议替换文本是否与用户真实经验中的可验证事实相符？",
            required=True,
            safety_note="M5 真实性检查仅供参考 — 仍需人工验证。",
        ),
        LLMManualApprovalChecklistQuestion(
            question_id=f"{candidate_id}_target_mapping",
            question_type=LLMManualApprovalChecklistQuestionType.TARGET_MAPPING,
            prompt="目标段落和条目ID是否正确？",
            required=True,
        ),
        LLMManualApprovalChecklistQuestion(
            question_id=f"{candidate_id}_original_match",
            question_type=LLMManualApprovalChecklistQuestionType.ORIGINAL_TEXT_MATCH,
            prompt="原文是否与预期的目标 bullet 完全匹配？",
            required=True,
        ),
        LLMManualApprovalChecklistQuestion(
            question_id=f"{candidate_id}_quality",
            question_type=LLMManualApprovalChecklistQuestionType.PROPOSED_TEXT_QUALITY,
            prompt="建议替换文本是否适合简历风格且无语法错误？",
            required=True,
        ),
        LLMManualApprovalChecklistQuestion(
            question_id=f"{candidate_id}_claim_risk",
            question_type=LLMManualApprovalChecklistQuestionType.UNSUPPORTED_CLAIM_RISK,
            prompt="建议替换文本是否引入了不可支持的声明（如 guaranteed、100%、top 1%）？",
            required=True,
            safety_note="如果引入了不可支持的声明，请不要进行任何手动编辑。",
        ),
        LLMManualApprovalChecklistQuestion(
            question_id=f"{candidate_id}_confirmation",
            question_type=LLMManualApprovalChecklistQuestionType.CONFIRMATION_GATE,
            prompt="此更改是否需要通过 M14 用户确认？",
            required=True,
            allowed_answers=["not_reviewed", "yes", "no"],
        ),
        LLMManualApprovalChecklistQuestion(
            question_id=f"{candidate_id}_formatting",
            question_type=LLMManualApprovalChecklistQuestionType.FORMATTING_CONSISTENCY,
            prompt="建议替换文本的格式是否与现有简历风格一致？",
            required=True,
        ),
        LLMManualApprovalChecklistQuestion(
            question_id=f"{candidate_id}_final_decision",
            question_type=LLMManualApprovalChecklistQuestionType.HUMAN_FINAL_DECISION,
            prompt="人工最终决定：保留原文 / 手动编辑 / 拒绝 / 推迟。",
            required=True,
            allowed_answers=["not_reviewed", "keep_original", "manually_edit", "reject", "defer"],
            safety_note="此决定不会自动应用任何候选。它仅用于您自己的记录。",
        ),
    ]


def _questions_for_blocked(candidate_id: str) -> list[LLMManualApprovalChecklistQuestion]:
    return [
        LLMManualApprovalChecklistQuestion(
            question_id=f"{candidate_id}_blocked_reason",
            question_type=LLMManualApprovalChecklistQuestionType.HUMAN_FINAL_DECISION,
            prompt="此候选已被阻塞。在审阅阻塞原因后，您是否仍然希望考虑在将来手动编辑？",
            required=False,
            allowed_answers=["not_reviewed", "defer", "ignore"],
            safety_note="阻塞的候选不应手动编辑 — 首先解决阻塞原因。",
        ),
    ]


def _map_status(pv_status: LLMManualPatchPreviewStatus) -> LLMManualApprovalChecklistItemStatus:
    mapping = {
        LLMManualPatchPreviewStatus.PREVIEW_READY: LLMManualApprovalChecklistItemStatus.REVIEW_REQUIRED,
        LLMManualPatchPreviewStatus.BLOCKED: LLMManualApprovalChecklistItemStatus.BLOCKED,
        LLMManualPatchPreviewStatus.NEEDS_MANUAL_EDIT: LLMManualApprovalChecklistItemStatus.NEEDS_MANUAL_EDIT,
        LLMManualPatchPreviewStatus.EXCLUDED: LLMManualApprovalChecklistItemStatus.EXCLUDED,
        LLMManualPatchPreviewStatus.UNMAPPED: LLMManualApprovalChecklistItemStatus.UNMAPPED,
        LLMManualPatchPreviewStatus.SKIPPED: LLMManualApprovalChecklistItemStatus.SKIPPED,
    }
    return mapping.get(pv_status, LLMManualApprovalChecklistItemStatus.SKIPPED)


def _build_checklist_item(pv_item: LLMManualPatchPreviewItem) -> LLMManualApprovalChecklistItem:
    status = _map_status(pv_item.preview_status)
    can_consider = status == LLMManualApprovalChecklistItemStatus.REVIEW_REQUIRED

    if status == LLMManualApprovalChecklistItemStatus.REVIEW_REQUIRED:
        questions = _questions_for_review(pv_item.candidate_id)
        instruction = f"候选 {pv_item.candidate_id}：请逐条回答以下检查清单问题。这不是批准 — 仅用于人工记录。"
    elif status == LLMManualApprovalChecklistItemStatus.NEEDS_MANUAL_EDIT:
        questions = _questions_for_review(pv_item.candidate_id)[:4]  # shorter set
        instruction = f"候选 {pv_item.candidate_id}：需要人工编辑。在编辑完成后回答以下问题。"
    else:
        questions = _questions_for_blocked(pv_item.candidate_id)
        instruction = f"候选 {pv_item.candidate_id}：已被阻塞/排除/跳过 — 请先解决阻塞原因。"

    return LLMManualApprovalChecklistItem(
        candidate_id=pv_item.candidate_id,
        checklist_status=status,
        source_preview_status=pv_item.preview_status.value,
        target_section=pv_item.target_section,
        target_item_id=pv_item.target_item_id,
        original_text=pv_item.original_text,
        proposed_text=pv_item.proposed_text,
        diff_preview=list(pv_item.diff_preview),
        block_reasons=list(pv_item.block_reasons),
        safety_notes=list(pv_item.safety_notes),
        questions=questions,
        human_decision_default="not_reviewed",
        can_be_considered_for_manual_edit=can_consider,
        manual_instruction=instruction,
    )


def build_manual_approval_checklist(
    preview: LLMManualPatchPreviewReport,
) -> LLMManualApprovalChecklistReport:
    global_warnings: list[str] = []

    if not preview.preview_only:
        global_warnings.append("Source preview is not preview_only=True. Checklist blocked.")
    if preview.final_resume_modified:
        global_warnings.append("Source preview indicates final_resume_modified=True. Checklist blocked.")
    if preview.executable_patch_generated:
        global_warnings.append("Source preview indicates executable_patch_generated=True. Checklist blocked.")
    if hasattr(preview, "applied_candidates") and getattr(preview, "applied_candidates", None):
        global_warnings.append("Source preview contains applied_candidates. Checklist blocked.")
    if hasattr(preview, "patch_operations") and getattr(preview, "patch_operations", None):
        global_warnings.append("Source preview contains patch_operations. Checklist blocked.")

    items = [_build_checklist_item(pv_item) for pv_item in preview.items]

    review = sum(1 for i in items if i.checklist_status == LLMManualApprovalChecklistItemStatus.REVIEW_REQUIRED)
    blocked = sum(1 for i in items if i.checklist_status == LLMManualApprovalChecklistItemStatus.BLOCKED)
    needs_edit = sum(1 for i in items if i.checklist_status == LLMManualApprovalChecklistItemStatus.NEEDS_MANUAL_EDIT)
    excluded = sum(1 for i in items if i.checklist_status == LLMManualApprovalChecklistItemStatus.EXCLUDED)
    unmapped = sum(1 for i in items if i.checklist_status == LLMManualApprovalChecklistItemStatus.UNMAPPED)
    skipped = sum(1 for i in items if i.checklist_status == LLMManualApprovalChecklistItemStatus.SKIPPED)

    return LLMManualApprovalChecklistReport(
        total_items=len(items),
        review_required_count=review,
        blocked_count=blocked,
        needs_manual_edit_count=needs_edit,
        excluded_count=excluded,
        unmapped_count=unmapped,
        skipped_count=skipped,
        items=items,
        global_warnings=global_warnings,
        safety_notice=_SAFETY_NOTICE,
        source_files={"preview": "provided via --preview"},
        summary=(
            f"Manual approval checklist: {review} review required, {blocked} blocked, "
            f"{needs_edit} needs edit, {excluded} excluded, {unmapped} unmapped, {skipped} skipped. "
            f"Checklist only — no final approval granted, no candidates applied, no executable patch generated."
        ),
    )
