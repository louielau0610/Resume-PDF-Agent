"""Context builder for M25 manual LLM application preview UI."""

from __future__ import annotations

from resume_pdf_agent.llm_application_preview_ui.safety import (
    get_preview_safety_labels,
    validate_llm_application_plan_for_preview,
)
from resume_pdf_agent.models.llm_application_plan import (
    LLMApplicationPlanStatus,
    LLMCandidateApplicationPlan,
    LLMCandidateApplicationPlanItem,
)
from resume_pdf_agent.models.llm_application_preview_ui import (
    LLMApplicationPreviewItemView,
    LLMApplicationPreviewPageContext,
    LLMApplicationPreviewStatusGroup,
)

_STATUS_TITLES = {
    LLMApplicationPlanStatus.PLANNED.value: "Planned / 已规划",
    LLMApplicationPlanStatus.BLOCKED.value: "Blocked / 已阻止",
    LLMApplicationPlanStatus.NEEDS_MANUAL_EDIT.value: "Needs Manual Edit / 需要人工编辑",
    LLMApplicationPlanStatus.EXCLUDED.value: "Excluded / 已排除",
    LLMApplicationPlanStatus.UNMAPPED.value: "Unmapped / 未映射",
}

_STATUS_DESCRIPTIONS = {
    LLMApplicationPlanStatus.PLANNED.value: (
        "Eligible for manual inspection only. Nothing is written to the resume."
    ),
    LLMApplicationPlanStatus.BLOCKED.value: (
        "Blocked by safety, validation, confirmation, or decision constraints."
    ),
    LLMApplicationPlanStatus.NEEDS_MANUAL_EDIT.value: (
        "Reviewer requested editing before any future manual consideration."
    ),
    LLMApplicationPlanStatus.EXCLUDED.value: (
        "Rejected or ignored by reviewer; shown for audit visibility."
    ),
    LLMApplicationPlanStatus.UNMAPPED.value: (
        "No safe target item mapping was available; do not invent a target."
    ),
}


def _status_value(item: LLMCandidateApplicationPlanItem) -> str:
    return item.plan_status.value if hasattr(item.plan_status, "value") else str(item.plan_status)


def _reason_values(item: LLMCandidateApplicationPlanItem) -> list[str]:
    return [r.value if hasattr(r, "value") else str(r) for r in item.block_reasons]


def _build_item_view(item: LLMCandidateApplicationPlanItem) -> LLMApplicationPreviewItemView:
    status = _status_value(item)
    return LLMApplicationPreviewItemView(
        candidate_id=item.candidate_id,
        plan_status=status,
        source_action=item.source_action,
        target_section=item.target_section,
        target_item_id=item.target_item_id,
        original_text=item.original_text,
        candidate_text=item.candidate_text,
        provider=item.provider,
        risk_level=item.risk_level,
        needs_confirmation=item.needs_confirmation,
        validation_warnings=list(item.validation_warnings),
        block_reasons=_reason_values(item),
        manual_review_notes=list(item.manual_review_notes),
        decision_note=item.decision_note,
        application_instruction=item.application_instruction,
        can_copy_candidate_text=bool(item.candidate_text and item.candidate_text.strip()),
        safety_labels=get_preview_safety_labels(),
    )


def _build_status_groups(
    items: list[LLMApplicationPreviewItemView],
) -> list[LLMApplicationPreviewStatusGroup]:
    groups: list[LLMApplicationPreviewStatusGroup] = []
    for status in [
        LLMApplicationPlanStatus.PLANNED.value,
        LLMApplicationPlanStatus.BLOCKED.value,
        LLMApplicationPlanStatus.NEEDS_MANUAL_EDIT.value,
        LLMApplicationPlanStatus.EXCLUDED.value,
        LLMApplicationPlanStatus.UNMAPPED.value,
    ]:
        ids = [item.candidate_id for item in items if item.plan_status == status]
        groups.append(
            LLMApplicationPreviewStatusGroup(
                status=status,
                title=_STATUS_TITLES[status],
                description=_STATUS_DESCRIPTIONS[status],
                count=len(ids),
                item_ids=ids,
            )
        )
    return groups


def build_llm_application_preview_context(
    plan: LLMCandidateApplicationPlan,
    *,
    plan_path: str | None = None,
    static_css: str = "",
    static_js: str = "",
) -> LLMApplicationPreviewPageContext:
    """Build a deterministic static preview context from an M24 plan."""

    item_views = [_build_item_view(item) for item in plan.items]
    warnings = list(plan.warnings) + validate_llm_application_plan_for_preview(plan)
    source_files = dict(plan.source_files)
    if plan_path:
        source_files["llm_rewrite_application_plan"] = plan_path

    return LLMApplicationPreviewPageContext(
        page_title="LLM Candidate Application Preview / LLM 候选应用预览",
        generated_from=plan_path or "LLM application plan",
        plan_only=True,
        source_files=source_files,
        total_candidates=plan.total_candidates,
        planned_count=plan.planned_count,
        blocked_count=plan.blocked_count,
        needs_manual_edit_count=plan.needs_manual_edit_count,
        excluded_count=plan.excluded_count,
        unmapped_count=plan.unmapped_count,
        warnings=warnings,
        safety_notice=plan.safety_notice,
        status_groups=_build_status_groups(item_views),
        items=item_views,
        static_css=static_css,
        static_js=static_js,
    )
