"""I/O helpers for M29 human final edit instruction pack."""

from __future__ import annotations

import json
from pathlib import Path

from resume_pdf_agent.llm_human_final_edit_pack.builder import build_human_final_edit_pack
from resume_pdf_agent.llm_human_final_edit_pack.markdown import render_human_final_edit_pack_markdown
from resume_pdf_agent.llm_human_final_edit_pack.renderer import render_human_final_edit_pack_html
from resume_pdf_agent.models.llm_human_final_edit_pack import LLMHumanFinalEditInstructionPack
from resume_pdf_agent.models.llm_manual_approval_checklist import LLMManualApprovalChecklistReport


def write_human_final_edit_pack_to_files(
    checklist_path: str | Path,
    output_json_path: str | Path | None = None,
    output_md_path: str | Path | None = None,
    output_html_path: str | Path | None = None,
) -> LLMHumanFinalEditInstructionPack:
    checklist_path = Path(checklist_path)
    if not checklist_path.is_file():
        raise FileNotFoundError(f"Checklist file not found: {checklist_path}")

    checklist = LLMManualApprovalChecklistReport(**json.loads(checklist_path.read_text(encoding="utf-8")))
    pack = build_human_final_edit_pack(checklist)

    if output_json_path:
        jp = Path(output_json_path)
        jp.parent.mkdir(parents=True, exist_ok=True)
        jp.write_text(pack.model_dump_json(indent=2), encoding="utf-8")

    if output_md_path:
        mp = Path(output_md_path)
        mp.parent.mkdir(parents=True, exist_ok=True)
        mp.write_text(render_human_final_edit_pack_markdown(pack), encoding="utf-8")

    if output_html_path:
        hp = Path(output_html_path)
        hp.parent.mkdir(parents=True, exist_ok=True)
        html = render_human_final_edit_pack_html(pack)
        hp.write_text(html, encoding="utf-8")

    return pack
