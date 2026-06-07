"""File IO for M23 LLM review decision summaries."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.llm_review_decisions.analyzer import analyze_llm_review_decisions
from resume_pdf_agent.llm_review_decisions.loader import (
    load_llm_review_decision_file,
    load_llm_rewrite_result_file,
)
from resume_pdf_agent.llm_review_decisions.markdown import (
    render_llm_review_decision_summary_markdown,
)
from resume_pdf_agent.models.llm_review_decisions import LLMReviewDecisionSummary
from resume_pdf_agent.workflow.serialization import write_json_artifact


def summarize_llm_review_decisions_to_files(
    *,
    decisions_path: str | Path,
    result_path: str | Path | None = None,
    output_json_path: str | Path | None = None,
    output_md_path: str | Path | None = None,
    strict: bool = False,
) -> LLMReviewDecisionSummary:
    """Load decisions, optionally cross-check a rewrite result, and write summaries."""

    decision_file = load_llm_review_decision_file(decisions_path, strict=strict)
    rewrite_result = load_llm_rewrite_result_file(result_path) if result_path else None

    summary = analyze_llm_review_decisions(
        decision_file,
        rewrite_result,
        result_path=str(result_path) if result_path else None,
        decisions_path=str(decisions_path),
    )

    if output_json_path:
        write_json_artifact(summary, output_json_path)

    if output_md_path:
        md_path = Path(output_md_path)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md = render_llm_review_decision_summary_markdown(summary)
        md_path.write_text(md, encoding="utf-8")

    return summary
