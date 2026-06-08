"""Deterministic M29 human-only final edit instruction pack builder."""

from __future__ import annotations

from resume_pdf_agent.models.llm_human_final_edit_pack import (
    LLMHumanFinalEditInstruction,
    LLMHumanFinalEditInstructionPack,
    LLMHumanFinalEditInstructionType,
    LLMHumanFinalEditItem,
    LLMHumanFinalEditItemStatus,
)
from resume_pdf_agent.models.llm_manual_approval_checklist import (
    LLMManualApprovalChecklistItem,
    LLMManualApprovalChecklistItemStatus,
    LLMManualApprovalChecklistReport,
)

_SAFETY_NOTICE = (
    "This is a human-instruction-only artifact. No LLM candidates were applied. "
    "No final approval has been granted by the system. No executable patch was generated. "
    "The final resume was not modified. Instructions do not mean factual verification. "
    "M5 truthfulness and M14 confirmation safeguards still apply. "
    "Any actual edit must be made manually by a human outside this system."
)


def _instructions_for_ready(candidate_id: str) -> list[LLMHumanFinalEditInstruction]:
    return [
        LLMHumanFinalEditInstruction(
            instruction_id=f"{candidate_id}_evidence",
            instruction_type=LLMHumanFinalEditInstructionType.EVIDENCE_COLLECTION,
            title="收集证据 / Collect Evidence",
            description="为建议替换文本中的每一条声明收集来源证据。提供量化成果的源文件、项目记录或用户确认。",
            required=True,
            safety_note="不要推断证据 — 必须由用户亲自确认。",
        ),
        LLMHumanFinalEditInstruction(
            instruction_id=f"{candidate_id}_target",
            instruction_type=LLMHumanFinalEditInstructionType.TARGET_VERIFICATION,
            title="核实目标 / Verify Target",
            description="手动确认目标段落和条目ID是否正确。在简历文件中找到对应的原文位置。",
            required=True,
        ),
        LLMHumanFinalEditInstruction(
            instruction_id=f"{candidate_id}_original_check",
            instruction_type=LLMHumanFinalEditInstructionType.ORIGINAL_TEXT_CHECK,
            title="检查原文 / Check Original",
            description="确认原文与目标 bullet 完全匹配。如果不匹配，请勿继续编辑。",
            required=True,
        ),
        LLMHumanFinalEditInstruction(
            instruction_id=f"{candidate_id}_proposed_review",
            instruction_type=LLMHumanFinalEditInstructionType.PROPOSED_TEXT_REVIEW,
            title="审阅建议文本 / Review Proposed Text",
            description="仔细阅读建议替换文本。检查语法、时态、长度和整体简历风格是否一致。",
            required=True,
        ),
        LLMHumanFinalEditInstruction(
            instruction_id=f"{candidate_id}_claim_check",
            instruction_type=LLMHumanFinalEditInstructionType.UNSUPPORTED_CLAIM_REVIEW,
            title="检查不支持声明 / Check Unsupported Claims",
            description="确认建议文本没有引入不可支持的声明（如 guaranteed、100%、top 1%、revenue increased）。如果存在不支持声明，请拒绝此候选。",
            required=True,
            safety_note="如果检测到不支持声明，请勿进行任何手动编辑。",
        ),
        LLMHumanFinalEditInstruction(
            instruction_id=f"{candidate_id}_formatting",
            instruction_type=LLMHumanFinalEditInstructionType.FORMATTING_REVIEW,
            title="格式审阅 / Formatting Review",
            description="检查格式一致性：时态、bullet 风格、长度（不超过 2-3 行）、ATS 可读性。",
            required=True,
        ),
        LLMHumanFinalEditInstruction(
            instruction_id=f"{candidate_id}_guidance",
            instruction_type=LLMHumanFinalEditInstructionType.MANUAL_EDIT_GUIDANCE,
            title="手动编辑指引 / Manual Edit Guidance",
            description="如果您决定进行手动编辑：请在系统外部手动修改简历。不要在 resume.html 或 resume.pdf 上使用任何自动工具。此系统不会执行编辑。",
            required=True,
            safety_note="任何编辑必须由人类手动完成。此系统不提供编辑功能。",
        ),
        LLMHumanFinalEditInstruction(
            instruction_id=f"{candidate_id}_final_decision",
            instruction_type=LLMHumanFinalEditInstructionType.FINAL_HUMAN_DECISION,
            title="人工最终决定 / Human Final Decision",
            description="做出最终决定：保留原文 / 手动编辑 / 拒绝 / 推迟。此决定不会自动应用任何更改。",
            required=True,
            safety_note="此决定仅用于您的个人记录 — 系统不会授予任何批准。",
        ),
    ]


def _required_evidence() -> list[str]:
    return [
        "提供量化成果的源文件或项目记录。",
        "提供责任声明的用户确认。",
        "提供目标 bullet 是预期编辑位置的手动确认。",
        "提供建议文本未被夸大的手动确认。",
    ]


def _map_status(cl_status: LLMManualApprovalChecklistItemStatus) -> LLMHumanFinalEditItemStatus:
    mapping = {
        LLMManualApprovalChecklistItemStatus.REVIEW_REQUIRED: LLMHumanFinalEditItemStatus.INSTRUCTION_READY,
        LLMManualApprovalChecklistItemStatus.BLOCKED: LLMHumanFinalEditItemStatus.BLOCKED,
        LLMManualApprovalChecklistItemStatus.NEEDS_MANUAL_EDIT: LLMHumanFinalEditItemStatus.NEEDS_MANUAL_EDIT,
        LLMManualApprovalChecklistItemStatus.EXCLUDED: LLMHumanFinalEditItemStatus.EXCLUDED,
        LLMManualApprovalChecklistItemStatus.UNMAPPED: LLMHumanFinalEditItemStatus.UNMAPPED,
        LLMManualApprovalChecklistItemStatus.SKIPPED: LLMHumanFinalEditItemStatus.SKIPPED,
    }
    return mapping.get(cl_status, LLMHumanFinalEditItemStatus.SKIPPED)


def _build_item(cl_item: LLMManualApprovalChecklistItem) -> LLMHumanFinalEditItem:
    status = _map_status(cl_item.checklist_status)
    can_consider = status == LLMHumanFinalEditItemStatus.INSTRUCTION_READY

    if status == LLMHumanFinalEditItemStatus.INSTRUCTION_READY:
        instructions = _instructions_for_ready(cl_item.candidate_id)
        evidence = _required_evidence()
        copy_text = cl_item.proposed_text
    elif status == LLMHumanFinalEditItemStatus.NEEDS_MANUAL_EDIT:
        instructions = _instructions_for_ready(cl_item.candidate_id)[:4]
        evidence = ["提供编辑所需的缺失信息。"]
        copy_text = cl_item.proposed_text
    else:
        instructions = [
            LLMHumanFinalEditInstruction(
                instruction_id=f"{cl_item.candidate_id}_blocked",
                instruction_type=LLMHumanFinalEditInstructionType.FINAL_HUMAN_DECISION,
                title="已被阻塞 / Blocked",
                description=f"此候选已被阻塞：{'; '.join(cl_item.block_reasons[:3])}。在解决阻塞原因之前，请勿编辑。",
                required=False,
                safety_note="阻塞的候选不应手动编辑 — 首先解决阻塞原因。",
            ),
        ]
        evidence = []
        copy_text = None

    return LLMHumanFinalEditItem(
        candidate_id=cl_item.candidate_id,
        item_status=status,
        source_checklist_status=cl_item.checklist_status.value,
        target_section=cl_item.target_section,
        target_item_id=cl_item.target_item_id,
        original_text=cl_item.original_text,
        proposed_text=cl_item.proposed_text,
        diff_preview=list(cl_item.diff_preview),
        block_reasons=list(cl_item.block_reasons),
        safety_notes=list(cl_item.safety_notes),
        required_evidence=evidence,
        human_instructions=instructions,
        manual_copy_text=copy_text,
        human_decision_default="not_reviewed",
        can_be_considered_for_human_edit=can_consider,
        system_final_approval_granted=False,
    )


def build_human_final_edit_pack(
    checklist: LLMManualApprovalChecklistReport,
) -> LLMHumanFinalEditInstructionPack:
    global_warnings: list[str] = []

    if not checklist.checklist_only:
        global_warnings.append("Source checklist is not checklist_only=True.")
    if checklist.final_resume_modified:
        global_warnings.append("Source checklist indicates final_resume_modified=True.")
    if checklist.executable_patch_generated:
        global_warnings.append("Source checklist indicates executable_patch_generated=True.")
    if checklist.final_approval_granted:
        global_warnings.append("Source checklist indicates final_approval_granted=True.")

    items = [_build_item(cl_item) for cl_item in checklist.items]

    ready = sum(1 for i in items if i.item_status == LLMHumanFinalEditItemStatus.INSTRUCTION_READY)
    blocked = sum(1 for i in items if i.item_status == LLMHumanFinalEditItemStatus.BLOCKED)
    needs_edit = sum(1 for i in items if i.item_status == LLMHumanFinalEditItemStatus.NEEDS_MANUAL_EDIT)
    excluded = sum(1 for i in items if i.item_status == LLMHumanFinalEditItemStatus.EXCLUDED)
    unmapped = sum(1 for i in items if i.item_status == LLMHumanFinalEditItemStatus.UNMAPPED)
    skipped = sum(1 for i in items if i.item_status == LLMHumanFinalEditItemStatus.SKIPPED)

    return LLMHumanFinalEditInstructionPack(
        total_items=len(items),
        instruction_ready_count=ready,
        blocked_count=blocked,
        needs_manual_edit_count=needs_edit,
        excluded_count=excluded,
        unmapped_count=unmapped,
        skipped_count=skipped,
        items=items,
        global_warnings=global_warnings,
        safety_notice=_SAFETY_NOTICE,
        source_files={"checklist": "provided via --checklist"},
        summary=(
            f"Human final edit instruction pack: {ready} instruction ready, {blocked} blocked, "
            f"{needs_edit} needs edit, {excluded} excluded, {unmapped} unmapped, {skipped} skipped. "
            f"Human-instruction-only — no candidates applied, no final approval granted, "
            f"no executable patch generated."
        ),
    )
