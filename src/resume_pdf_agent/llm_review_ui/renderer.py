"""Renderer for M22 browser LLM rewrite review UI page."""

from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from resume_pdf_agent.llm_review_ui.context import build_llm_review_ui_context
from resume_pdf_agent.models.llm import LLMRewriteResult
from resume_pdf_agent.models.llm_review_ui import (
    LLMReviewUIOptions,
    LLMReviewUIResult,
    LLMReviewUIStatus,
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


def render_llm_review_ui_page(
    rewrite_result: LLMRewriteResult,
    output_path: str | Path,
    options: LLMReviewUIOptions | None = None,
) -> LLMReviewUIResult:
    output_path = Path(output_path)
    opts = options or LLMReviewUIOptions()

    try:
        env = _create_env()
        template = env.get_template("llm_review_page.html.j2")
        context = build_llm_review_ui_context(rewrite_result, opts)
        context["css"] = Markup(_read_static("llm_review_page.css"))
        context["js"] = Markup(_read_static("llm_review_page.js"))
        # Embed candidates through Jinja's tojson filter in the template.
        all_candidates = []
        for group_name in ["requires_confirmation", "validation_warnings", "risk_flags", "clean_candidates"]:
            all_candidates.extend(context["groups"].get(group_name, []))
        context["candidates"] = all_candidates

        html = template.render(**context)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")

        return LLMReviewUIResult(
            status=LLMReviewUIStatus.RENDERED,
            output_path=str(output_path),
            html=html,
            warnings=list(context.get("warnings", [])),
            candidate_count=context["candidate_count"],
            candidates_requiring_confirmation=context["candidates_requiring_confirmation"],
            summary=f"LLM review UI rendered to {output_path} with {context['candidate_count']} candidates",
        )
    except Exception as exc:
        return LLMReviewUIResult(
            status=LLMReviewUIStatus.FAILED,
            errors=[str(exc)],
            summary=f"Failed to render LLM review UI: {exc}",
        )


def render_llm_review_ui_from_result_file(
    result_path: str | Path,
    output_path: str | Path,
    options: LLMReviewUIOptions | None = None,
) -> LLMReviewUIResult:
    result_path = Path(result_path)
    if not result_path.is_file():
        return LLMReviewUIResult(
            status=LLMReviewUIStatus.FAILED,
            errors=[f"Result file not found: {result_path}"],
            summary=f"Result file not found: {result_path}",
        )

    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
        rewrite_result = LLMRewriteResult(**data)
        return render_llm_review_ui_page(rewrite_result, output_path, options)
    except Exception as exc:
        return LLMReviewUIResult(
            status=LLMReviewUIStatus.FAILED,
            errors=[str(exc)],
            summary=f"Failed to load result file: {exc}",
        )
