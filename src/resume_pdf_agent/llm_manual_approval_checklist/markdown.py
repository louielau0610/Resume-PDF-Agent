"""Markdown report for M28 manual approval checklist."""

from __future__ import annotations

from resume_pdf_agent.models.llm_manual_approval_checklist import (
    LLMManualApprovalChecklistItem,
    LLMManualApprovalChecklistItemStatus,
    LLMManualApprovalChecklistReport,
)


def _status_icon(status: LLMManualApprovalChecklistItemStatus) -> str:
    return {
        LLMManualApprovalChecklistItemStatus.REVIEW_REQUIRED: "📋",
        LLMManualApprovalChecklistItemStatus.BLOCKED: "🚫",
        LLMManualApprovalChecklistItemStatus.NEEDS_MANUAL_EDIT: "✏️",
        LLMManualApprovalChecklistItemStatus.EXCLUDED: "❌",
        LLMManualApprovalChecklistItemStatus.UNMAPPED: "❓",
        LLMManualApprovalChecklistItemStatus.SKIPPED: "⏭️",
    }.get(status, "❓")


def _item_md(item: LLMManualApprovalChecklistItem) -> str:
    icon = _status_icon(item.checklist_status)
    lines = [
        f"### {icon} {item.candidate_id} — {item.checklist_status.value}",
        "",
    ]
    if item.target_section:
        lines.append(f"- **目标段落**: {item.target_section}")
    if item.target_item_id:
        lines.append(f"- **目标条目ID**: {item.target_item_id}")
    if item.original_text:
        lines.append(f"- **原文**: {item.original_text}")
    if item.proposed_text:
        lines.append(f"- **建议文本**: {item.proposed_text}")

    if item.questions:
        lines.append("")
        lines.append("**检查清单问题**:")
        lines.append("")
        for q in item.questions:
            req = "(必答)" if q.required else "(可选)"
            lines.append(f"- [{q.default_answer}] **{q.question_type.value}** {req}: {q.prompt}")
            if q.safety_note:
                lines.append(f"  - ⚠️ {q.safety_note}")

    if item.block_reasons:
        lines.append("")
        lines.append("**阻塞原因**:")
        for r in item.block_reasons:
            lines.append(f"  - {r}")

    if item.safety_notes:
        lines.append("")
        lines.append("**安全提示**:")
        for s in item.safety_notes:
            lines.append(f"  - {s}")

    lines.append("")
    lines.append(f"**人工操作指引**: {item.manual_instruction}")
    lines.append("")
    return "\n".join(lines)


def render_manual_approval_checklist_markdown(report: LLMManualApprovalChecklistReport) -> str:
    sections: list[str] = []

    sections.append("# LLM Manual Approval Checklist / LLM人工审批检查清单")
    sections.append("")
    sections.append("## Safety Notice / 安全声明")
    sections.append("")
    sections.append(report.safety_notice)
    sections.append("")

    sections.append("## Source Files / 源文件")
    sections.append("")
    for k, v in report.source_files.items():
        sections.append(f"- **{k}**: {v}")
    sections.append("")

    sections.append("## Count Summary / 数量汇总")
    sections.append("")
    sections.append("| 类别 | 数量 |")
    sections.append("|------|------|")
    sections.append(f"| 总项目数 | {report.total_items} |")
    sections.append(f"| 需要审阅 | {report.review_required_count} |")
    sections.append(f"| 阻塞 | {report.blocked_count} |")
    sections.append(f"| 需要人工编辑 | {report.needs_manual_edit_count} |")
    sections.append(f"| 已排除 | {report.excluded_count} |")
    sections.append(f"| 未映射 | {report.unmapped_count} |")
    sections.append(f"| 已跳过 | {report.skipped_count} |")
    sections.append("")

    if report.global_warnings:
        sections.append("## Global Warnings / 全局警告")
        sections.append("")
        for w in report.global_warnings:
            sections.append(f"- ⚠️ {w}")
        sections.append("")

    for status_group, label in [
        (LLMManualApprovalChecklistItemStatus.REVIEW_REQUIRED, "Review Required / 需要审阅"),
        (LLMManualApprovalChecklistItemStatus.BLOCKED, "Blocked / 阻塞"),
        (LLMManualApprovalChecklistItemStatus.NEEDS_MANUAL_EDIT, "Needs Manual Edit / 需要人工编辑"),
        (LLMManualApprovalChecklistItemStatus.EXCLUDED, "Excluded / 已排除"),
        (LLMManualApprovalChecklistItemStatus.UNMAPPED, "Unmapped / 未映射"),
    ]:
        group_items = [i for i in report.items if i.checklist_status == status_group]
        if group_items:
            sections.append(f"## {label}")
            sections.append("")
            for item in group_items:
                sections.append(_item_md(item))

    sections.append("## Required Manual Next Steps / 需要的人工后续步骤")
    sections.append("")
    sections.append("1. 逐条回答每个 `review_required` 候选的检查清单问题。")
    sections.append("2. 默认答案均为 `not_reviewed` — 这并非批准。")
    sections.append("3. 此检查清单不会自动应用任何候选。")
    sections.append("4. 在考虑任何手动编辑之前，重新运行 M5 真实性检查。")
    sections.append("5. 在考虑任何手动编辑之前，确认 M14 确认门控。")
    sections.append("6. 最终决定由人类做出 — 系统不会授予最终批准。")
    sections.append("")

    sections.append("---")
    sections.append("")
    sections.append("*此检查清单仅用于人工审阅。未授予任何最终批准。未应用任何候选。未生成任何可执行补丁。最终简历未被修改。*")
    sections.append("")

    return "\n".join(sections)
