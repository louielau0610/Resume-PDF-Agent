"""Markdown renderer for M23 LLM review decision summaries."""

from __future__ import annotations

from resume_pdf_agent.models.llm_review_decisions import LLMReviewDecisionSummary


def _list_or_none(values: list[str]) -> str:
    return ", ".join(f"`{v}`" for v in values) if values else "None"


def render_llm_review_decision_summary_markdown(
    summary: LLMReviewDecisionSummary,
) -> str:
    """Render a Chinese-first human-readable Markdown summary."""

    lines: list[str] = []
    lines.append("# LLM Rewrite Review Decision Summary")
    lines.append("")
    lines.append("## 摘要 / Summary")
    lines.append("")
    lines.append(f"- **LLM 候选总数**: {summary.total_candidates}")
    lines.append(f"- **审阅决策总数**: {summary.total_decisions}")
    lines.append(f"- **Approved**: {summary.approved_count}")
    lines.append(f"- **Rejected**: {summary.rejected_count}")
    lines.append(f"- **Needs edit**: {summary.needs_edit_count}")
    lines.append(f"- **Notes**: {summary.note_count}")
    lines.append(f"- **Ignored**: {summary.ignored_count}")
    lines.append("")
    lines.append("## Source Files")
    lines.append("")
    lines.append(f"- `llm_rewrite_result.json`: {summary.result_path or 'not provided'}")
    lines.append(f"- `llm_rewrite_review_decisions.json`: {summary.decisions_path or 'not provided'}")
    lines.append("")

    lines.append("## Approved Candidates")
    lines.append("")
    lines.append(_list_or_none(summary.approved_candidate_ids))
    lines.append("")
    lines.append("## Rejected Candidates")
    lines.append("")
    lines.append(_list_or_none(summary.rejected_candidate_ids))
    lines.append("")
    lines.append("## Needs-Edit Candidates")
    lines.append("")
    lines.append(_list_or_none(summary.needs_edit_candidate_ids))
    lines.append("")
    lines.append("## Ignored Candidates")
    lines.append("")
    lines.append(_list_or_none(summary.ignored_candidate_ids))
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    note_rows = [c for c in summary.candidate_summaries if c.has_note]
    if note_rows:
        for row in note_rows:
            lines.append(f"- `{row.candidate_id}`: {row.note}")
    else:
        lines.append("None")
    lines.append("")
    lines.append("## Undecided Candidates")
    lines.append("")
    lines.append(_list_or_none(summary.undecided_candidate_ids))
    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    if summary.warnings:
        for warning in summary.warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("None")
    lines.append("")
    lines.append("## Safety Notice")
    lines.append("")
    lines.append(
        "本摘要只读取本地审阅决策并生成 advisory artifact；不会应用候选，"
        "不会把 approved candidates 自动插入 `resume.html` 或 `resume.pdf`。"
    )
    lines.append("")
    lines.append(
        "Approval does not mean a claim is factually verified. "
        "M5 truthfulness checks and the M14 confirmation gate still apply."
    )
    lines.append("")
    lines.append(summary.safety_notice)
    lines.append("")
    return "\n".join(lines)
