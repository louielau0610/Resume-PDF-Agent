"""I/O helpers for M26 strict pre-application validation."""

from __future__ import annotations

import json
from pathlib import Path

from resume_pdf_agent.llm_pre_application_validation.markdown import (
    render_pre_application_validation_markdown,
)
from resume_pdf_agent.llm_pre_application_validation.validator import (
    validate_pre_application,
)
from resume_pdf_agent.models.llm import LLMRewriteResult
from resume_pdf_agent.models.llm_application_plan import LLMCandidateApplicationPlan
from resume_pdf_agent.models.llm_pre_application_validation import (
    LLMPreApplicationValidationReport,
)
from resume_pdf_agent.models.llm_review_decisions import (
    LLMReviewDecisionFile,
    LLMReviewDecisionSummary,
)


def write_pre_application_validation_to_files(
    plan_path: str | Path,
    output_json_path: str | Path | None = None,
    output_md_path: str | Path | None = None,
    result_path: str | Path | None = None,
    decisions_path: str | Path | None = None,
    summary_path: str | Path | None = None,
    strict: bool = False,
) -> LLMPreApplicationValidationReport:
    """Load plan, run validation, and write JSON/MD outputs."""

    plan_path = Path(plan_path)
    if not plan_path.is_file():
        raise FileNotFoundError(f"Plan file not found: {plan_path}")

    plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
    plan = LLMCandidateApplicationPlan(**plan_data)

    result: LLMRewriteResult | None = None
    if result_path:
        rp = Path(result_path)
        if rp.is_file():
            result = LLMRewriteResult(**json.loads(rp.read_text(encoding="utf-8")))
        elif strict:
            raise FileNotFoundError(f"Result file not found: {rp}")

    decisions_file: LLMReviewDecisionFile | None = None
    if decisions_path:
        dp = Path(decisions_path)
        if dp.is_file():
            raw = json.loads(dp.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and "decisions" in raw:
                decisions_file = LLMReviewDecisionFile(**raw)
            elif isinstance(raw, list):
                decisions_file = LLMReviewDecisionFile(decisions=raw)
        elif strict:
            raise FileNotFoundError(f"Decisions file not found: {dp}")

    summary: LLMReviewDecisionSummary | None = None
    if summary_path:
        sp = Path(summary_path)
        if sp.is_file():
            summary = LLMReviewDecisionSummary(**json.loads(sp.read_text(encoding="utf-8")))
        elif strict:
            raise FileNotFoundError(f"Summary file not found: {sp}")

    report = validate_pre_application(
        plan=plan,
        result=result,
        decisions_file=decisions_file,
        summary=summary,
        strict=strict,
    )

    # Write JSON
    if output_json_path:
        jp = Path(output_json_path)
        jp.parent.mkdir(parents=True, exist_ok=True)
        jp.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    # Write Markdown
    if output_md_path:
        mp = Path(output_md_path)
        mp.parent.mkdir(parents=True, exist_ok=True)
        md_content = render_pre_application_validation_markdown(report)
        mp.write_text(md_content, encoding="utf-8")

    return report
