"""Markdown renderer for M24 LLM candidate application plans."""

from __future__ import annotations

from resume_pdf_agent.models.llm_application_plan import (
    LLMApplicationPlanStatus,
    LLMCandidateApplicationPlan,
    LLMCandidateApplicationPlanItem,
)


def _item_line(item: LLMCandidateApplicationPlanItem) -> str:
    reasons = ", ".join(r.value for r in item.block_reasons) or "none"
    target = item.target_item_id or "unmapped"
    return f"- `{item.candidate_id}` -> `{target}` ({item.source_action}); reasons: {reasons}"


def _section(
    lines: list[str],
    title: str,
    items: list[LLMCandidateApplicationPlanItem],
) -> None:
    lines.append(f"## {title}")
    lines.append("")
    if items:
        for item in items:
            lines.append(_item_line(item))
            if item.decision_note:
                lines.append(f"  - note: {item.decision_note}")
            lines.append(f"  - instruction: {item.application_instruction}")
    else:
        lines.append("None")
    lines.append("")


def render_llm_application_plan_markdown(plan: LLMCandidateApplicationPlan) -> str:
    """Render a Chinese-first plan-only Markdown artifact."""

    lines: list[str] = []
    lines.append("# LLM Candidate Application Plan")
    lines.append("")
    lines.append("## Plan-only Safety Notice")
    lines.append("")
    lines.append(
        "本文件只是 application plan，不是 resume patch。No candidate has been applied, "
        "and the final resume has not been modified."
    )
    lines.append("")
    lines.append(
        "Approval does not mean factual verification. M5 truthfulness checks and "
        "the M14 confirmation gate still apply before any future manual application."
    )
    lines.append("")
    lines.append(plan.safety_notice)
    lines.append("")
    lines.append("## Source Files")
    lines.append("")
    for key, value in plan.source_files.items():
        lines.append(f"- `{key}`: {value or 'not provided'}")
    lines.append("")
    lines.append("## Count Summary")
    lines.append("")
    lines.append(f"- **Total candidates**: {plan.total_candidates}")
    lines.append(f"- **Total decisions**: {plan.total_decisions}")
    lines.append(f"- **Planned**: {plan.planned_count}")
    lines.append(f"- **Blocked**: {plan.blocked_count}")
    lines.append(f"- **Needs manual edit**: {plan.needs_manual_edit_count}")
    lines.append(f"- **Excluded**: {plan.excluded_count}")
    lines.append(f"- **Unmapped**: {plan.unmapped_count}")
    lines.append("")

    _section(
        lines,
        "Planned Candidates",
        [i for i in plan.items if i.plan_status == LLMApplicationPlanStatus.PLANNED],
    )
    _section(
        lines,
        "Needs Manual Edit",
        [i for i in plan.items if i.plan_status == LLMApplicationPlanStatus.NEEDS_MANUAL_EDIT],
    )
    _section(
        lines,
        "Blocked Candidates",
        [i for i in plan.items if i.plan_status == LLMApplicationPlanStatus.BLOCKED],
    )
    _section(
        lines,
        "Excluded Candidates",
        [i for i in plan.items if i.plan_status == LLMApplicationPlanStatus.EXCLUDED],
    )
    _section(
        lines,
        "Unmapped Candidates",
        [i for i in plan.items if i.plan_status == LLMApplicationPlanStatus.UNMAPPED],
    )

    lines.append("## Warnings")
    lines.append("")
    if plan.warnings:
        for warning in plan.warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("None")
    lines.append("")
    lines.append("## Next Manual Steps")
    lines.append("")
    lines.append("1. Review each planned item against the original resume source.")
    lines.append("2. Resolve M5 truthfulness and M14 confirmation requirements manually.")
    lines.append("3. Treat this artifact as audit guidance only; it is not an application engine.")
    lines.append("")
    return "\n".join(lines)
