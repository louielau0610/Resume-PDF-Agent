"""Markdown review artifact generator for M14.

Produces a Chinese-first confirmation review document that users can
read to understand what items need their attention.
"""

from __future__ import annotations

from resume_pdf_agent.models.confirmation import (
    ConfirmationPacket,
    ConfirmationReviewResult,
)


def render_confirmation_review_markdown(
    packet: ConfirmationPacket,
    review_result: ConfirmationReviewResult | None = None,
) -> str:
    """Render a Chinese-first Markdown review document.

    Parameters
    ----------
    packet : ConfirmationPacket
        The confirmation packet to render.
    review_result : ConfirmationReviewResult | None
        Optional decision application results.

    Returns
    -------
    str
        Markdown-formatted review document.
    """
    lines: list[str] = []

    lines.append("# 简历确认审核报告")
    lines.append("")
    lines.append(
        "> **重要提示**：本系统不独立验证真实世界的事实。"
        "请仅批准您个人可以验证的声明。"
    )
    lines.append("")

    # ── Packet summary ─────────────────────────────────────────────────
    lines.append("## 确认包概览")
    lines.append("")
    lines.append(f"- **包 ID**: `{packet.packet_id}`")
    lines.append(f"- **总确认项**: {len(packet.items)}")
    lines.append(f"- **阻塞项**: {packet.blocking_count}")
    lines.append(f"- **高优先级**: {packet.high_priority_count}")
    lines.append(f"- **待处理**: {packet.pending_count}")
    lines.append(
        f"- **可以生成最终 PDF**: {'是' if packet.can_generate_final_pdf else '否'}"
    )
    lines.append("")
    lines.append(f"**摘要**: {packet.summary}")
    lines.append("")

    # ── Items table ────────────────────────────────────────────────────
    lines.append("## 确认项列表")
    lines.append("")
    lines.append(
        "| # | ID | 类型 | 优先级 | 阻塞PDF | 来源 | 声明 | 原因 | 建议操作 |"
    )
    lines.append(
        "|---|----|------|--------|---------|------|------|------|----------|"
    )

    for idx, item in enumerate(packet.items, start=1):
        item_type = item.item_type.value
        priority = item.priority.value
        blocks = "是" if item.blocks_final_pdf else "否"
        source = item.source_stage
        claim = item.claim_text[:80] + ("..." if len(item.claim_text) > 80 else "")
        reason = item.reason[:60] + ("..." if len(item.reason) > 60 else "")
        action = (
            item.suggested_user_action[:60] + ("..."
            if len(item.suggested_user_action) > 60
            else "")
        )

        # Escape pipe characters for markdown table
        claim = claim.replace("|", "\\|")
        reason = reason.replace("|", "\\|")
        action = action.replace("|", "\\|")

        lines.append(
            f"| {idx} | {item.item_id} | {item_type} | {priority} | {blocks} | {source} "
            f"| {claim} | {reason} | {action} |"
        )

    lines.append("")

    # ── Decision results (if review applied) ───────────────────────────
    if review_result is not None:
        lines.append("## 审核结果")
        lines.append("")
        lines.append(f"- **已应用决策数**: {review_result.decisions_applied}")
        lines.append(f"- **已解决**: {len(review_result.resolved_items)} 项")
        lines.append(f"- **已拒绝**: {len(review_result.rejected_items)} 项")
        lines.append(f"- **需编辑**: {len(review_result.needs_editing_items)} 项")
        lines.append(f"- **未处理**: {len(review_result.unresolved_items)} 项")
        lines.append(
            f"- **可以生成最终 PDF**: {'是' if review_result.can_generate_final_pdf else '否'}"
        )
        lines.append("")
        if review_result.warnings:
            lines.append("### 审核警告")
            lines.append("")
            for w in review_result.warnings:
                lines.append(f"- ⚠️ {w}")
            lines.append("")

    # ── Instructions ───────────────────────────────────────────────────
    lines.append("## 如何审核")
    lines.append("")
    lines.append("1. 逐项查看上表中的每个确认项。")
    lines.append("2. 对于每个声明，确认其是否真实反映了您的经历。")
    lines.append("3. 做出以下决策之一：")
    lines.append("   - `approve` — 批准该声明（您可验证其真实性）")
    lines.append("   - `reject` — 拒绝该声明（应删除或重写）")
    lines.append("   - `needs_editing` — 需要修改（提供修改文本）")
    lines.append("   - `provide_evidence` — 提供证据（附上支持材料）")
    lines.append("   - `ignore_for_now` — 暂不处理（仅限非阻塞项）")
    lines.append("4. 将您的决策写入 `confirmation_decisions.json` 文件。")
    lines.append("5. 重新运行工作流并加载决策文件。")
    lines.append("")

    lines.append("## 安全声明")
    lines.append("")
    lines.append("- 本系统**不独立验证真实世界事实**。")
    lines.append("- 本系统**不预测录用概率、面试概率或 offer 概率**。")
    lines.append("- 本系统**不声称知道任何公司的内部筛选标准**。")
    lines.append("- 本系统**不调用 LLM API 进行审核**。")
    lines.append("- 最终审核责任在用户。请仅批准您能亲自验证的声明。")
    lines.append("")

    return "\n".join(lines)
