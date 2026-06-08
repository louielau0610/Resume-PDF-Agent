"""I/O helpers for M28 manual approval checklist."""

from __future__ import annotations

import json
from pathlib import Path

from resume_pdf_agent.llm_manual_approval_checklist.builder import (
    build_manual_approval_checklist,
)
from resume_pdf_agent.llm_manual_approval_checklist.markdown import (
    render_manual_approval_checklist_markdown,
)
from resume_pdf_agent.llm_manual_approval_checklist.renderer import (
    render_manual_approval_checklist_html,
)
from resume_pdf_agent.models.llm_manual_approval_checklist import (
    LLMManualApprovalChecklistReport,
)
from resume_pdf_agent.models.llm_manual_patch_preview import (
    LLMManualPatchPreviewReport,
)


def write_manual_approval_checklist_to_files(
    preview_path: str | Path,
    output_json_path: str | Path | None = None,
    output_md_path: str | Path | None = None,
    output_html_path: str | Path | None = None,
) -> LLMManualApprovalChecklistReport:
    preview_path = Path(preview_path)
    if not preview_path.is_file():
        raise FileNotFoundError(f"Preview file not found: {preview_path}")

    preview = LLMManualPatchPreviewReport(**json.loads(preview_path.read_text(encoding="utf-8")))
    report = build_manual_approval_checklist(preview)

    if output_json_path:
        jp = Path(output_json_path)
        jp.parent.mkdir(parents=True, exist_ok=True)
        jp.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    if output_md_path:
        mp = Path(output_md_path)
        mp.parent.mkdir(parents=True, exist_ok=True)
        mp.write_text(render_manual_approval_checklist_markdown(report), encoding="utf-8")

    if output_html_path:
        hp = Path(output_html_path)
        hp.parent.mkdir(parents=True, exist_ok=True)
        html = render_manual_approval_checklist_html(report)
        hp.write_text(html, encoding="utf-8")

    return report
