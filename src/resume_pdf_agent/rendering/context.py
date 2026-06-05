"""Render context builders for deterministic HTML resume rendering."""

from resume_pdf_agent.models import (
    BulletEnhancementResult,
    HTMLRenderOptions,
    ResumeContent,
    TemplateSelectionResult,
    UserProfile,
)
from resume_pdf_agent.rendering.safety import collect_render_warnings_from_bullets, escape_html_text
from resume_pdf_agent.rendering.sections import build_render_sections

REMINDER_PANEL_TEXT = (
    "Current v0 output is designed for PDF generation. If you need Word, JPG, or PNG later, "
    "use an external PDF conversion tool after PDF export."
)


def _optional_contact_line(label: str, value: str | None) -> str | None:
    if not value:
        return None
    return f"{label}: {value}"


def build_resume_header_context(
    user_profile: UserProfile,
) -> dict:
    """Build safe public header context for the rendered resume."""

    contact_lines = [
        line
        for line in [
            _optional_contact_line("Email", user_profile.contact.email),
            _optional_contact_line("Phone", user_profile.contact.phone),
            _optional_contact_line("Location", user_profile.contact.location),
            _optional_contact_line("LinkedIn", user_profile.contact.linkedin),
            _optional_contact_line("GitHub", user_profile.contact.github),
            _optional_contact_line("Portfolio", user_profile.contact.portfolio),
        ]
        if line
    ]
    return {
        "full_name": escape_html_text(user_profile.full_name),
        "contact_lines": [escape_html_text(line) for line in contact_lines],
    }


def build_resume_render_context(
    user_profile: UserProfile,
    resume_content: ResumeContent,
    template_selection_result: TemplateSelectionResult,
    bullet_enhancement_result: BulletEnhancementResult | None = None,
    options: HTMLRenderOptions | None = None,
) -> dict:
    """Build the Jinja render context without exposing hidden internal data."""

    render_options = options or HTMLRenderOptions()
    sections = build_render_sections(
        user_profile=user_profile,
        resume_content=resume_content,
        template_selection_result=template_selection_result,
        bullet_enhancement_result=bullet_enhancement_result,
        options=render_options,
    )
    warnings = list(template_selection_result.warnings)
    warnings.extend(collect_render_warnings_from_bullets(sections))
    if bullet_enhancement_result:
        warnings.extend(bullet_enhancement_result.global_warnings)
        warnings.extend(bullet_enhancement_result.truthfulness_blockers)

    context = {
        **build_resume_header_context(user_profile),
        "selected_template_id": escape_html_text(template_selection_result.selected_template_id),
        "template_display_name": escape_html_text(template_selection_result.selected_template.display_name),
        "sections": sections,
        "warnings": [escape_html_text(warning) for warning in warnings],
        "include_truthfulness_warnings": render_options.include_truthfulness_warnings,
        "include_preview_reminder_panel": render_options.include_preview_reminder_panel,
        "reminder_panel_text": (
            escape_html_text(REMINDER_PANEL_TEXT)
            if render_options.include_preview_reminder_panel
            else None
        ),
        "css": "",
        "language": escape_html_text(render_options.language),
    }
    return context
