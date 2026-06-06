"""UI context builder for M20 browser confirmation UI."""

from __future__ import annotations

from resume_pdf_agent.confirmation_ui.safety import escape_confirmation_ui_text
from resume_pdf_agent.models.confirmation import (
    ConfirmationDecisionType,
    ConfirmationItem,
    ConfirmationItemStatus,
    ConfirmationPacket,
)
from resume_pdf_agent.models.confirmation_ui import (
    ConfirmationUIDecisionOption,
    ConfirmationUIOptions,
)


def _decision_options() -> list[ConfirmationUIDecisionOption]:
    """Return the standard decision options for the UI."""
    return [
        ConfirmationUIDecisionOption(
            decision=ConfirmationDecisionType.APPROVE,
            label="Approve / 批准",
            description="I can personally verify this claim is accurate.",
        ),
        ConfirmationUIDecisionOption(
            decision=ConfirmationDecisionType.REJECT,
            label="Reject / 拒绝",
            description="This claim should not appear on my resume.",
        ),
        ConfirmationUIDecisionOption(
            decision=ConfirmationDecisionType.NEEDS_EDITING,
            label="Needs Editing / 需要修改",
            description="The claim needs revision before it can be used.",
        ),
        ConfirmationUIDecisionOption(
            decision=ConfirmationDecisionType.PROVIDE_EVIDENCE,
            label="Provide Evidence / 提供证据",
            description="I have supporting evidence for this claim.",
        ),
        ConfirmationUIDecisionOption(
            decision=ConfirmationDecisionType.IGNORE_FOR_NOW,
            label="Ignore for Now / 暂不处理",
            description="Skip this item for now (not for blocking items).",
        ),
    ]


def build_confirmation_ui_context(
    packet: ConfirmationPacket,
    options: ConfirmationUIOptions | None = None,
) -> dict:
    """Build a Jinja2 context dict for the confirmation UI page.

    Parameters
    ----------
    packet : ConfirmationPacket
        The confirmation packet to render.
    options : ConfirmationUIOptions | None
        UI rendering options.

    Returns
    -------
    dict
        Jinja2 template context.
    """
    opts = options or ConfirmationUIOptions()

    # Group items by priority
    groups: dict[str, list[dict]] = {
        "blocking": [],
        "high": [],
        "medium": [],
        "low": [],
        "info": [],
    }

    for item in packet.items:
        priority = item.priority.value
        group_key = priority if priority in groups else "info"
        groups[group_key].append({
            "item_id": escape_confirmation_ui_text(item.item_id),
            "item_type": escape_confirmation_ui_text(item.item_type.value),
            "priority": escape_confirmation_ui_text(item.priority.value),
            "status": escape_confirmation_ui_text(item.status.value),
            "source_stage": escape_confirmation_ui_text(item.source_stage),
            "source_id": escape_confirmation_ui_text(item.source_id or ""),
            "source_experience_id": escape_confirmation_ui_text(item.source_experience_id or ""),
            "claim_text": escape_confirmation_ui_text(item.claim_text),
            "reason": escape_confirmation_ui_text(item.reason),
            "suggested_user_action": escape_confirmation_ui_text(item.suggested_user_action),
            "risk_flags": [escape_confirmation_ui_text(rf) for rf in item.risk_flags],
            "blocks_final_pdf": item.blocks_final_pdf,
            "requires_user_decision": item.requires_user_decision,
            "related_criteria_ids": [escape_confirmation_ui_text(c) for c in item.related_criteria_ids],
        })

    return {
        "page_title": "Confirmation Review / 确认审核",
        "packet_id": escape_confirmation_ui_text(packet.packet_id),
        "item_count": len(packet.items),
        "blocking_count": packet.blocking_count,
        "high_priority_count": packet.high_priority_count,
        "pending_count": packet.pending_count,
        "can_generate_final_pdf": packet.can_generate_final_pdf,
        "warnings": [escape_confirmation_ui_text(w) for w in packet.warnings],
        "summary": escape_confirmation_ui_text(packet.summary),
        "groups": groups,
        "group_labels": {
            "blocking": "Blocking / 阻塞",
            "high": "High Priority / 高优先级",
            "medium": "Medium Priority / 中优先级",
            "low": "Low Priority / 低优先级",
            "info": "Info / 信息",
        },
        "decision_options": [
            {
                "value": opt.decision.value,
                "label": escape_confirmation_ui_text(opt.label),
                "description": escape_confirmation_ui_text(opt.description),
            }
            for opt in _decision_options()
        ],
        "options": {
            "include_copy_button": opts.include_copy_button,
            "include_download_button": opts.include_download_button,
            "include_priority_filters": opts.include_priority_filters,
            "include_decision_controls": opts.include_decision_controls,
            "include_raw_packet_summary": opts.include_raw_packet_summary,
            "language": opts.language,
        },
    }
