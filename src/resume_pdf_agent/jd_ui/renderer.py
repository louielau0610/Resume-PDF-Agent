"""Renderer for M21 browser JD upload UI page."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from resume_pdf_agent.jd_ui.context import build_jd_upload_ui_context
from resume_pdf_agent.models.jd_ui import (
    JDUploadUIOptions,
    JDUploadUIResult,
    JDUploadUIStatus,
)

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
_STATIC_DIR = Path(__file__).resolve().parent / "static"


def _create_env() -> Environment:
    return Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)), autoescape=False, trim_blocks=True, lstrip_blocks=True)


def _read_static(filename: str) -> str:
    p = _STATIC_DIR / filename
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def render_jd_upload_ui_page(
    output_path: str | Path,
    options: JDUploadUIOptions | None = None,
) -> JDUploadUIResult:
    output_path = Path(output_path)
    opts = options or JDUploadUIOptions()

    try:
        env = _create_env()
        template = env.get_template("jd_upload_page.html.j2")
        context = build_jd_upload_ui_context(opts)
        context["css"] = _read_static("jd_upload_page.css")
        context["js"] = _read_static("jd_upload_page.js")

        html = template.render(**context)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")

        return JDUploadUIResult(
            status=JDUploadUIStatus.RENDERED,
            output_path=str(output_path),
            html=html,
            summary=f"JD upload UI rendered to {output_path}",
        )
    except Exception as exc:
        return JDUploadUIResult(
            status=JDUploadUIStatus.FAILED,
            errors=[str(exc)],
            summary=f"Failed to render JD upload UI: {exc}",
        )
