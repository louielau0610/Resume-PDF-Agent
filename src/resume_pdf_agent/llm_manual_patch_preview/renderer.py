"""HTML renderer for M27 manual patch preview (static local page)."""

from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from resume_pdf_agent.models.llm_manual_patch_preview import (
    LLMManualPatchPreviewReport,
)

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
_STATIC_DIR = Path(__file__).resolve().parent / "static"


def _create_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _read_static(filename: str) -> str:
    p = _STATIC_DIR / filename
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def render_manual_patch_preview_html(report: LLMManualPatchPreviewReport) -> str:
    env = _create_env()
    template = env.get_template("manual_patch_preview.html.j2")
    ctx = {
        "report": report,
        "css": _read_static("manual_patch_preview.css"),
        "js": _read_static("manual_patch_preview.js"),
        "items_json": json.dumps([i.model_dump() for i in report.items], ensure_ascii=False),
    }
    return template.render(**ctx)
