"""Safety helpers for M25 manual application preview UI."""

from __future__ import annotations

import html as _html
from pathlib import Path

from resume_pdf_agent.models.llm_application_plan import LLMCandidateApplicationPlan


def escape_llm_application_preview_text(value: str) -> str:
    """Escape text for tests and explicit callers; templates also autoescape."""

    return _html.escape(value, quote=True)


def safe_llm_application_preview_output_path(path: str | Path) -> Path:
    """Resolve the preview output path without creating files."""

    return Path(path).resolve()


def validate_llm_application_plan_for_preview(
    plan: LLMCandidateApplicationPlan,
) -> list[str]:
    """Return non-fatal issues that should be surfaced in the preview page."""

    issues: list[str] = []
    if plan.plan_only is not True:
        issues.append("Application plan must be plan_only=true.")
    if not plan.items:
        issues.append("No items in application plan; preview page will show an empty list.")
    for i, item in enumerate(plan.items):
        if not item.candidate_id.strip():
            issues.append(f"Plan item {i} has empty candidate_id.")
        if item.plan_status.value == "planned" and not item.target_item_id:
            issues.append(f"Planned item {item.candidate_id} has no target_item_id.")
        if item.plan_status.value == "planned" and item.needs_confirmation:
            issues.append(f"Planned item {item.candidate_id} still needs confirmation.")
    return issues


def get_preview_safety_labels() -> list[str]:
    """Shared safety labels shown on every candidate."""

    return [
        "Plan only",
        "Manual review required",
        "Not factually verified",
        "M5/M14 safeguards still apply",
    ]
