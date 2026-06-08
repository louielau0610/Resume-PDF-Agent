"""Markdown report for M29 human-only final edit instruction pack."""

from __future__ import annotations

from resume_pdf_agent.models.llm_human_final_edit_pack import (
    LLMHumanFinalEditInstructionPack,
    LLMHumanFinalEditItem,
    LLMHumanFinalEditItemStatus,
)


def _status_icon(status: LLMHumanFinalEditItemStatus) -> str:
    return {
        LLMHumanFinalEditItemStatus.INSTRUCTION_READY: "📋",
        LLMHumanFinalEditItemStatus.BLOCKED: "🚫",
        LLMHumanFinalEditItemStatus.NEEDS_MANUAL_EDIT: "✏️",
        LLMHumanFinalEditItemStatus.EXCLUDED: "❌",
        LLMHumanFinalEditItemStatus.UNMAPPED: "❓",
        LLMHumanFinalEditItemStatus.SKIPPED: "⏭️",
    }.get(status, "❓")


def _item_md(item: LLMHumanFinalEditItem) -> str:
    icon = _status_icon(item.item_status)
    lines = [
        f"### {icon} {item.candidate_id} — {item.item_status.value}",
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

    if item.required_evidence:
        lines.append("")
        lines.append("**需要收集的证据**:")
        for e in item.required_evidence:
            lines.append(f"  - {e}")

    if item.human_instructions:
        lines.append("")
        lines.append("**人工操作指引**:")
        for inst in item.human_instructions:
            lines.append(f"  - **{inst.title}** [{inst.default_status}]")
            lines.append(f"    {inst.description}")
            if inst.safety_note:
                lines.append(f"    ⚠️ {inst.safety_note}")

    if item.manual_copy_text:
        lines.append("")
        lines.append("*以下文本仅供人工审阅使用 — 不是已批准的替换文本，不是补丁文本。*")
        lines.append(f"> {item.manual_copy_text}")

    if item.block_reasons:
        lines.append("")
        for r in item.block_reasons:
            lines.append(f"  - 🚫 {r}")

    lines.append("")
    return "\n".join(lines)


def render_human_final_edit_pack_markdown(pack: LLMHumanFinalEditInstructionPack) -> str:
    sections: list[str] = []

    sections.append("# LLM Human-Only Final Edit Instruction Pack / LLM人工最终编辑指引包")
    sections.append("")
    sections.append("## Safety Notice / 安全声明")
    sections.append("")
    sections.append(pack.safety_notice)
    sections.append("")

    sections.append("## Source Files / 源文件")
    sections.append("")
    for k, v in pack.source_files.items():
        sections.append(f"- **{k}**: {v}")
    sections.append("")

    sections.append("## Count Summary / 数量汇总")
    sections.append("")
    sections.append("| 类别 | 数量 |")
    sections.append("|------|------|")
    sections.append(f"| 总项目数 | {pack.total_items} |")
    sections.append(f"| 指引就绪 | {pack.instruction_ready_count} |")
    sections.append(f"| 阻塞 | {pack.blocked_count} |")
    sections.append(f"| 需要人工编辑 | {pack.needs_manual_edit_count} |")
    sections.append(f"| 已排除 | {pack.excluded_count} |")
    sections.append(f"| 未映射 | {pack.unmapped_count} |")
    sections.append(f"| 已跳过 | {pack.skipped_count} |")
    sections.append("")

    if pack.global_warnings:
        sections.append("## Global Warnings / 全局警告")
        for w in pack.global_warnings:
            sections.append(f"- ⚠️ {w}")
        sections.append("")

    for status_group, label in [
        (LLMHumanFinalEditItemStatus.INSTRUCTION_READY, "Instruction Ready / 指引就绪"),
        (LLMHumanFinalEditItemStatus.BLOCKED, "Blocked / 阻塞"),
        (LLMHumanFinalEditItemStatus.NEEDS_MANUAL_EDIT, "Needs Manual Edit / 需要人工编辑"),
        (LLMHumanFinalEditItemStatus.EXCLUDED, "Excluded / 已排除"),
        (LLMHumanFinalEditItemStatus.UNMAPPED, "Unmapped / 未映射"),
    ]:
        group_items = [i for i in pack.items if i.item_status == status_group]
        if group_items:
            sections.append(f"## {label}")
            for item in group_items:
                sections.append(_item_md(item))

    sections.append("## Required Manual Next Steps / 需要的人工后续步骤")
    sections.append("")
    sections.append("1. 逐条完成每个 `instruction_ready` 候选的人工操作指引。")
    sections.append("2. 所有默认状态均为 `not_started` — 这并非完成或批准。")
    sections.append("3. 任何实际编辑必须由人类在系统外部手动完成。")
    sections.append("4. 在考虑任何手动编辑之前，重新运行 M5 真实性检查。")
    sections.append("5. 在考虑任何手动编辑之前，确认 M14 确认门控。")
    sections.append("6. 最终决定由人类做出 — 系统不会授予最终批准。")
    sections.append("")

    sections.append("---")
    sections.append("*此指引包仅用于人工操作。未授予任何最终批准。未应用任何候选。未生成任何可执行补丁。最终简历未被修改。*")

    return "\n".join(sections)
