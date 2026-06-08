"""Markdown report generator for M26 strict pre-application validation."""

from __future__ import annotations

from resume_pdf_agent.models.llm_pre_application_validation import (
    LLMPreApplicationValidationItem,
    LLMPreApplicationValidationReport,
    LLMPreApplicationValidationStatus,
)


def _status_icon(status: LLMPreApplicationValidationStatus) -> str:
    icons = {
        LLMPreApplicationValidationStatus.PASSED: "✅",
        LLMPreApplicationValidationStatus.BLOCKED: "🚫",
        LLMPreApplicationValidationStatus.NEEDS_MANUAL_EDIT: "✏️",
        LLMPreApplicationValidationStatus.EXCLUDED: "❌",
        LLMPreApplicationValidationStatus.UNMAPPED: "❓",
        LLMPreApplicationValidationStatus.WARNING: "⚠️",
        LLMPreApplicationValidationStatus.SKIPPED: "⏭️",
    }
    return icons.get(status, "❓")


def _item_md(item: LLMPreApplicationValidationItem) -> str:
    icon = _status_icon(item.validation_status)
    lines = [
        f"### {icon} {item.candidate_id} — {item.validation_status.value}",
        "",
        f"- **计划状态**: {item.source_plan_status}",
        f"- **验证状态**: {item.validation_status.value}",
        f"- **可进入补丁预览**: {'是' if item.can_proceed_to_patch_preview else '否'}",
    ]
    if item.target_section:
        lines.append(f"- **目标段落**: {item.target_section}")
    if item.target_item_id:
        lines.append(f"- **目标条目ID**: {item.target_item_id}")
    lines.append(f"- **原文存在**: {'是' if item.original_text_present else '否'}")
    lines.append(f"- **候选文本存在**: {'是' if item.candidate_text_present else '否'}")
    lines.append(f"- **需要确认**: {'是' if item.needs_confirmation else '否'}")

    if item.validation_warnings:
        lines.append("")
        lines.append("**验证警告**:")
        for w in item.validation_warnings:
            lines.append(f"  - {w}")

    if item.block_reasons:
        lines.append("")
        lines.append("**阻塞原因**:")
        for r in item.block_reasons:
            lines.append(f"  - {r}")

    if item.manual_review_notes:
        lines.append("")
        lines.append("**人工审阅备注**:")
        for n in item.manual_review_notes:
            lines.append(f"  - {n}")

    if item.safety_notes:
        lines.append("")
        lines.append("**安全提示**:")
        for s in item.safety_notes:
            lines.append(f"  - {s}")

    lines.append("")
    return "\n".join(lines)


def render_pre_application_validation_markdown(
    report: LLMPreApplicationValidationReport,
) -> str:
    """Render a human-readable Markdown validation report."""

    sections: list[str] = []

    # Title
    sections.append("# LLM Pre-Application Validation Report / LLM预应用验证报告")
    sections.append("")

    # Safety notice
    sections.append("## Safety Notice / 安全声明")
    sections.append("")
    sections.append(report.safety_notice)
    sections.append("")

    # Source files
    sections.append("## Source Files / 源文件")
    sections.append("")
    for key, val in report.source_files.items():
        if val:
            sections.append(f"- **{key}**: {val}")
    sections.append("")

    # Overall decision
    sections.append("## Overall Decision / 总体决策")
    sections.append("")
    if report.can_proceed_to_patch_preview:
        sections.append("✅ **可以进入补丁预览阶段** — 所有候选均通过严格预应用验证。")
    else:
        sections.append("🚫 **不可进入补丁预览阶段** — 存在阻塞项需要解决。")
    sections.append("")

    # Count summary
    sections.append("## Count Summary / 数量汇总")
    sections.append("")
    sections.append(f"| 类别 | 数量 |")
    sections.append(f"|------|------|")
    sections.append(f"| 计划项总数 | {report.total_plan_items} |")
    sections.append(f"| 通过 | {report.passed_count} |")
    sections.append(f"| 阻塞 | {report.blocked_count} |")
    sections.append(f"| 需要人工编辑 | {report.needs_manual_edit_count} |")
    sections.append(f"| 已排除 | {report.excluded_count} |")
    sections.append(f"| 未映射 | {report.unmapped_count} |")
    sections.append(f"| 警告 | {report.warning_count} |")
    sections.append("")

    # Global warnings
    if report.global_warnings:
        sections.append("## Global Warnings / 全局警告")
        sections.append("")
        for w in report.global_warnings:
            sections.append(f"- ⚠️ {w}")
        sections.append("")

    # Passed candidates
    passed = [i for i in report.items if i.validation_status == LLMPreApplicationValidationStatus.PASSED]
    if passed:
        sections.append("## Passed Candidates / 通过的候选")
        sections.append("")
        for item in passed:
            sections.append(_item_md(item))

    # Blocked candidates
    blocked = [i for i in report.items if i.validation_status == LLMPreApplicationValidationStatus.BLOCKED]
    if blocked:
        sections.append("## Blocked Candidates / 阻塞的候选")
        sections.append("")
        for item in blocked:
            sections.append(_item_md(item))

    # Needs manual edit
    needs_edit = [i for i in report.items if i.validation_status == LLMPreApplicationValidationStatus.NEEDS_MANUAL_EDIT]
    if needs_edit:
        sections.append("## Needs Manual Edit / 需要人工编辑")
        sections.append("")
        for item in needs_edit:
            sections.append(_item_md(item))

    # Excluded
    excluded = [i for i in report.items if i.validation_status == LLMPreApplicationValidationStatus.EXCLUDED]
    if excluded:
        sections.append("## Excluded Candidates / 已排除的候选")
        sections.append("")
        for item in excluded:
            sections.append(_item_md(item))

    # Unmapped
    unmapped = [i for i in report.items if i.validation_status == LLMPreApplicationValidationStatus.UNMAPPED]
    if unmapped:
        sections.append("## Unmapped Candidates / 未映射的候选")
        sections.append("")
        for item in unmapped:
            sections.append(_item_md(item))

    # Warning items
    warning_items = [i for i in report.items if i.validation_status == LLMPreApplicationValidationStatus.WARNING]
    if warning_items:
        sections.append("## Warning Items / 警告项")
        sections.append("")
        for item in warning_items:
            sections.append(_item_md(item))

    # Next steps
    sections.append("## Required Next Manual Steps / 需要的人工后续步骤")
    sections.append("")
    sections.append("1. 审阅所有阻塞项并解决阻塞原因。")
    sections.append("2. 对需要人工编辑的候选进行手动修改。")
    sections.append("3. 确认所有通过的候选文本均可由您亲自验证。")
    sections.append("4. 在进行任何手动补丁之前，重新运行 M5 真实性检查。")
    sections.append("5. 在进行任何手动补丁之前，确认 M14 确认门控。")
    sections.append("6. 此验证报告不应用于自动应用候选。")
    sections.append("")

    # Footer
    sections.append("---")
    sections.append("")
    sections.append("*此验证报告仅用于验证目的。未应用任何候选。未生成任何补丁。最终简历未被修改。*")
    sections.append("")

    return "\n".join(sections)
