"""File IO for M24 LLM candidate application plans."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from resume_pdf_agent.llm_application_plan.markdown import (
    render_llm_application_plan_markdown,
)
from resume_pdf_agent.llm_application_plan.planner import plan_llm_candidate_application
from resume_pdf_agent.llm_review_decisions.loader import (
    load_llm_review_decision_file,
    load_llm_rewrite_result_file,
)
from resume_pdf_agent.models.llm_application_plan import LLMCandidateApplicationPlan
from resume_pdf_agent.models.llm_review_decisions import LLMReviewDecisionSummary
from resume_pdf_agent.workflow.serialization import write_json_artifact


def load_llm_review_decision_summary_file(
    path: str | Path,
) -> LLMReviewDecisionSummary:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {p}: {exc}") from exc
    try:
        return LLMReviewDecisionSummary(**raw)
    except ValidationError as exc:
        raise ValueError(f"Invalid LLM review decision summary file: {exc}") from exc


def plan_llm_candidate_application_to_files(
    *,
    result_path: str | Path,
    decisions_path: str | Path,
    summary_path: str | Path | None = None,
    output_json_path: str | Path | None = None,
    output_md_path: str | Path | None = None,
    strict: bool = False,
) -> LLMCandidateApplicationPlan:
    """Load inputs, create a plan-only artifact, and optionally write files."""

    rewrite_result = load_llm_rewrite_result_file(result_path)
    decision_file = load_llm_review_decision_file(decisions_path, strict=strict)
    decision_summary = (
        load_llm_review_decision_summary_file(summary_path)
        if summary_path
        else None
    )

    plan = plan_llm_candidate_application(
        rewrite_result,
        decision_file,
        decision_summary,
        result_path=str(result_path),
        decisions_path=str(decisions_path),
        summary_path=str(summary_path) if summary_path else None,
    )

    if output_json_path:
        write_json_artifact(plan, output_json_path)

    if output_md_path:
        md_path = Path(output_md_path)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(render_llm_application_plan_markdown(plan), encoding="utf-8")

    return plan
