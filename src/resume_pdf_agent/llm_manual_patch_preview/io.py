"""I/O helpers for M27 manual patch preview."""

from __future__ import annotations

import json
from pathlib import Path

from resume_pdf_agent.llm_manual_patch_preview.builder import (
    build_manual_patch_preview,
)
from resume_pdf_agent.llm_manual_patch_preview.markdown import (
    render_manual_patch_preview_markdown,
)
from resume_pdf_agent.llm_manual_patch_preview.renderer import (
    render_manual_patch_preview_html,
)
from resume_pdf_agent.models.llm_application_plan import LLMCandidateApplicationPlan
from resume_pdf_agent.models.llm_manual_patch_preview import (
    LLMManualPatchPreviewReport,
)
from resume_pdf_agent.models.llm_pre_application_validation import (
    LLMPreApplicationValidationReport,
)


def write_manual_patch_preview_to_files(
    plan_path: str | Path,
    validation_path: str | Path,
    output_json_path: str | Path | None = None,
    output_md_path: str | Path | None = None,
    output_html_path: str | Path | None = None,
) -> LLMManualPatchPreviewReport:
    plan_path = Path(plan_path)
    validation_path = Path(validation_path)

    if not plan_path.is_file():
        raise FileNotFoundError(f"Plan file not found: {plan_path}")
    if not validation_path.is_file():
        raise FileNotFoundError(f"Validation file not found: {validation_path}")

    plan = LLMCandidateApplicationPlan(**json.loads(plan_path.read_text(encoding="utf-8")))
    validation = LLMPreApplicationValidationReport(**json.loads(validation_path.read_text(encoding="utf-8")))

    report = build_manual_patch_preview(plan, validation)

    if output_json_path:
        jp = Path(output_json_path)
        jp.parent.mkdir(parents=True, exist_ok=True)
        jp.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    if output_md_path:
        mp = Path(output_md_path)
        mp.parent.mkdir(parents=True, exist_ok=True)
        mp.write_text(render_manual_patch_preview_markdown(report), encoding="utf-8")

    if output_html_path:
        hp = Path(output_html_path)
        hp.parent.mkdir(parents=True, exist_ok=True)
        html = render_manual_patch_preview_html(report)
        hp.write_text(html, encoding="utf-8")

    return report
