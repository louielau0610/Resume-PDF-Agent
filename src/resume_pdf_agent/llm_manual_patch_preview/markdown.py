"""Markdown report for M27 manual patch preview."""

from __future__ import annotations

from resume_pdf_agent.models.llm_manual_patch_preview import (
    LLMManualPatchPreviewItem,
    LLMManualPatchPreviewReport,
    LLMManualPatchPreviewStatus,
)


def _status_icon(status: LLMManualPatchPreviewStatus) -> str:
    icons = {
        LLMManualPatchPreviewStatus.PREVIEW_READY: "✅",
        LLMManualPatchPreviewStatus.BLOCKED: "🚫",
        LLMManualPatchPreviewStatus.NEEDS_MANUAL_EDIT: "✏️",
        LLMManualPatchPreviewStatus.EXCLUDED: "❌",
        LLMManualPatchPreviewStatus.UNMAPPED: "❓",
        LLMManualPatchPreviewStatus.SKIPPED: "⏭️",
    }
    return icons.get(status, "❓")


def _item_md(item: LLMManualPatchPreviewItem) -> str:
    icon = _status_icon(item.preview_status)
    lines = [
        f"### {icon} {item.candidate_id} — {item.preview_status.value}",
        "",
    ]
    if item.target_section:
        lines.append(f"- **目标段落**: {item.target_section}")
    if item.target_item_id:
        lines.append(f"- **目标条目ID**: {item.target_item_id}")
    if item.validation_status:
        lines.append(f"- **M26 验证状态**: {item.validation_status}")

    if item.original_text:
        lines.append("")
        lines.append("**原文**:")
        lines.append(f"> {item.original_text}")

    if item.proposed_text:
        lines.append("")
        lines.append("**建议替换文本**:")
        lines.append(f"> {item.proposed_text}")

    if item.diff_preview:
        lines.append("")
        lines.append("**显示差异预览 (仅用于人工查看)**:")
        lines.append("```diff")
        for dl in item.diff_preview:
            lines.append(dl)
        lines.append("```")

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


def render_manual_patch_preview_markdown(report: LLMManualPatchPreviewReport) -> str:
    sections: list[str] = []

    sections.append("# LLM Manual Patch Preview / LLM人工补丁预览")
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
    sections.append(f"| 预览就绪 | {report.preview_ready_count} |")
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

    # Preview-ready
    ready = [i for i in report.items if i.preview_status == LLMManualPatchPreviewStatus.PREVIEW_READY]
    if ready:
        sections.append("## Preview-Ready Candidates / 预览就绪的候选")
        sections.append("")
        for item in ready:
            sections.append(_item_md(item))

    # Blocked
    blocked = [i for i in report.items if i.preview_status == LLMManualPatchPreviewStatus.BLOCKED]
    if blocked:
        sections.append("## Blocked Candidates / 阻塞的候选")
        sections.append("")
        for item in blocked:
            sections.append(_item_md(item))

    # Needs edit
    needs_edit = [i for i in report.items if i.preview_status == LLMManualPatchPreviewStatus.NEEDS_MANUAL_EDIT]
    if needs_edit:
        sections.append("## Needs Manual Edit / 需要人工编辑")
        sections.append("")
        for item in needs_edit:
            sections.append(_item_md(item))

    # Excluded
    excluded = [i for i in report.items if i.preview_status == LLMManualPatchPreviewStatus.EXCLUDED]
    if excluded:
        sections.append("## Excluded / 已排除")
        sections.append("")
        for item in excluded:
            sections.append(_item_md(item))

    # Unmapped
    unmapped = [i for i in report.items if i.preview_status == LLMManualPatchPreviewStatus.UNMAPPED]
    if unmapped:
        sections.append("## Unmapped / 未映射")
        sections.append("")
        for item in unmapped:
            sections.append(_item_md(item))

    sections.append("## Required Manual Next Steps / 需要的人工后续步骤")
    sections.append("")
    sections.append("1. 人工逐条比较原文与建议替换文本。")
    sections.append("2. 确认每条建议替换文本均可在真实简历中验证。")
    sections.append("3. 不要直接复制粘贴 — 每条替换必须经过人工判断。")
    sections.append("4. 在进行任何手动修改前，重新运行 M5 真实性检查。")
    sections.append("5. 在进行任何手动修改前，确认 M14 确认门控。")
    sections.append("6. 此预览不是可执行补丁 — 不能自动应用。")
    sections.append("")

    sections.append("---")
    sections.append("")
    sections.append("*此预览仅用于人工查看。未应用任何候选。未生成任何可执行补丁。最终简历未被修改。*")
    sections.append("")

    return "\n".join(sections)
