"""Jinja2 HTML renderer for structured resume content."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from resume_pdf_agent.models import (
    BulletEnhancementResult,
    HTMLRenderOptions,
    HTMLRenderResult,
    HTMLRenderStatus,
    ResumeContent,
    TemplateSelectionResult,
    UserProfile,
)
from resume_pdf_agent.rendering.context import build_resume_render_context
from resume_pdf_agent.rendering.safety import collect_render_warnings_from_bullets, escape_html_text
from resume_pdf_agent.rendering.sections import build_render_sections

_RENDERING_DIR = Path(__file__).resolve().parent
_TEMPLATE_DIR = _RENDERING_DIR / "templates"
_STATIC_DIR = _RENDERING_DIR / "static"
_FALLBACK_TEMPLATE_ID = "ats_student_basic"


def _load_css(include_css: bool) -> str | None:
    if not include_css:
        return None
    return (_STATIC_DIR / "resume_base.css").read_text(encoding="utf-8")


def _template_name(template_id: str) -> str:
    return f"{template_id}.html.j2"


def _create_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_resume_html(
    user_profile: UserProfile,
    resume_content: ResumeContent,
    template_selection_result: TemplateSelectionResult,
    bullet_enhancement_result: BulletEnhancementResult | None = None,
    options: HTMLRenderOptions | None = None,
) -> HTMLRenderResult:
    """Render structured resume data into deterministic ATS-friendly HTML."""

    render_options = options or HTMLRenderOptions()
    sections = build_render_sections(
        user_profile=user_profile,
        resume_content=resume_content,
        template_selection_result=template_selection_result,
        bullet_enhancement_result=bullet_enhancement_result,
        options=render_options,
    )
    sections_with_content = [section for section in sections if section.items]
    selected_template_id = template_selection_result.selected_template_id
    warnings = list(template_selection_result.warnings)
    warnings.extend(collect_render_warnings_from_bullets(sections))
    if bullet_enhancement_result:
        warnings.extend(bullet_enhancement_result.global_warnings)
        warnings.extend(bullet_enhancement_result.truthfulness_blockers)

    if not sections_with_content:
        return HTMLRenderResult(
            status=HTMLRenderStatus.SKIPPED_DUE_TO_INSUFFICIENT_CONTENT,
            template_id=selected_template_id,
            html="",
            css=None,
            sections_rendered=[],
            warnings=warnings,
            output_path=None,
            summary="HTML rendering skipped because no resume section content was available.",
        )

    css = _load_css(render_options.include_css)
    context = build_resume_render_context(
        user_profile=user_profile,
        resume_content=resume_content,
        template_selection_result=template_selection_result,
        bullet_enhancement_result=bullet_enhancement_result,
        options=render_options,
    )
    context["css"] = css or ""
    context["warnings"] = [escape_html_text(warning) for warning in warnings]

    env = _create_environment()
    template_id_used = selected_template_id
    try:
        template = env.get_template(_template_name(selected_template_id))
    except TemplateNotFound:
        template_id_used = _FALLBACK_TEMPLATE_ID
        warnings.append(
            f"Template file for '{selected_template_id}' was not found; fell back to '{_FALLBACK_TEMPLATE_ID}'."
        )
        context["selected_template_id"] = escape_html_text(template_id_used)
        context["warnings"] = [escape_html_text(warning) for warning in warnings]
        template = env.get_template(_template_name(template_id_used))

    html = template.render(**context).strip()
    status = HTMLRenderStatus.RENDERED_WITH_WARNINGS if warnings else HTMLRenderStatus.RENDERED

    return HTMLRenderResult(
        status=status,
        template_id=template_id_used,
        html=html,
        css=css,
        sections_rendered=[section.section_id for section in sections_with_content],
        warnings=warnings,
        output_path=None,
        summary=(
            f"Rendered deterministic HTML resume using template '{template_id_used}'. "
            "No PDF, frontend UI, LLM call, or online template search was performed."
        ),
    )


def write_rendered_html(
    render_result: HTMLRenderResult,
    output_path: str | Path,
) -> HTMLRenderResult:
    """Write rendered HTML to a local file and return an updated result."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_result.html, encoding="utf-8")
    return render_result.model_copy(update={"output_path": str(path)})
