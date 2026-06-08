"""Renderer for M25 manual LLM candidate application preview UI."""

from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup
from pydantic import ValidationError

from resume_pdf_agent.llm_application_preview_ui.context import (
    build_llm_application_preview_context,
)
from resume_pdf_agent.models.llm_application_plan import LLMCandidateApplicationPlan
from resume_pdf_agent.models.llm_application_preview_ui import (
    LLMApplicationPreviewUIResult,
    LLMApplicationPreviewUIStatus,
)

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
_STATIC_DIR = Path(__file__).resolve().parent / "static"


def _create_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=select_autoescape(
            enabled_extensions=("html", "j2", "html.j2"),
            default_for_string=True,
            default=True,
        ),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _read_static(filename: str) -> str:
    p = _STATIC_DIR / filename
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def render_llm_application_preview_ui_page(
    plan: LLMCandidateApplicationPlan,
    output_path: str | Path,
    *,
    plan_path: str | None = None,
) -> LLMApplicationPreviewUIResult:
    """Render an M24 application plan to a local static HTML preview page."""

    output_path = Path(output_path)
    try:
        env = _create_env()
        template = env.get_template("llm_application_preview_page.html.j2")
        context = build_llm_application_preview_context(
            plan,
            plan_path=plan_path,
            static_css=_read_static("llm_application_preview_page.css"),
            static_js=_read_static("llm_application_preview_page.js"),
        )
        payload = context.model_dump(mode="json")
        payload["static_css"] = Markup(context.static_css)
        payload["static_js"] = Markup(context.static_js)
        payload["items_json"] = [item.model_dump(mode="json") for item in context.items]

        html = template.render(**payload)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")

        return LLMApplicationPreviewUIResult(
            status=LLMApplicationPreviewUIStatus.RENDERED,
            output_path=str(output_path),
            html=html,
            warnings=list(context.warnings),
            total_candidates=context.total_candidates,
            planned_count=context.planned_count,
            blocked_count=context.blocked_count,
            needs_manual_edit_count=context.needs_manual_edit_count,
            excluded_count=context.excluded_count,
            unmapped_count=context.unmapped_count,
            summary=f"LLM application preview UI rendered to {output_path}",
        )
    except Exception as exc:
        return LLMApplicationPreviewUIResult(
            status=LLMApplicationPreviewUIStatus.FAILED,
            errors=[str(exc)],
            summary=f"Failed to render LLM application preview UI: {exc}",
        )


def render_llm_application_preview_ui_from_plan_file(
    plan_path: str | Path,
    output_path: str | Path,
) -> LLMApplicationPreviewUIResult:
    """Load an M24 plan JSON file and render the M25 static preview page."""

    plan_path = Path(plan_path)
    if not plan_path.is_file():
        return LLMApplicationPreviewUIResult(
            status=LLMApplicationPreviewUIStatus.FAILED,
            errors=[f"Plan file not found: {plan_path}"],
            summary=f"Plan file not found: {plan_path}",
        )

    try:
        data = json.loads(plan_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return LLMApplicationPreviewUIResult(
            status=LLMApplicationPreviewUIStatus.FAILED,
            errors=[f"Invalid JSON in {plan_path}: {exc}"],
            summary=f"Invalid JSON in {plan_path}: {exc}",
        )

    try:
        plan = LLMCandidateApplicationPlan(**data)
    except ValidationError as exc:
        return LLMApplicationPreviewUIResult(
            status=LLMApplicationPreviewUIStatus.FAILED,
            errors=[f"Invalid LLM application plan file: {exc}"],
            summary=f"Invalid LLM application plan file: {exc}",
        )

    return render_llm_application_preview_ui_page(
        plan,
        output_path,
        plan_path=str(plan_path),
    )
