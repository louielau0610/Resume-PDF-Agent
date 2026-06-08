"""HTML renderer for M29 human final edit instruction pack (static local page)."""

from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from resume_pdf_agent.models.llm_human_final_edit_pack import LLMHumanFinalEditInstructionPack

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
_STATIC_DIR = Path(__file__).resolve().parent / "static"


def _create_env() -> Environment:
    return Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)), autoescape=True, trim_blocks=True, lstrip_blocks=True)


def _read_static(filename: str) -> str:
    p = _STATIC_DIR / filename
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def render_human_final_edit_pack_html(pack: LLMHumanFinalEditInstructionPack) -> str:
    env = _create_env()
    template = env.get_template("human_final_edit_pack.html.j2")
    ctx = {
        "pack": pack,
        "css": _read_static("human_final_edit_pack.css"),
        "js": _read_static("human_final_edit_pack.js"),
        "items_json": json.dumps([i.model_dump() for i in pack.items], ensure_ascii=False),
    }
    return template.render(**ctx)
