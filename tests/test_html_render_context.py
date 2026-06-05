from resume_pdf_agent.rendering import build_render_sections, build_resume_render_context
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.templates import select_internal_template


def test_build_resume_render_context_can_be_imported():
    assert callable(build_resume_render_context)


def test_build_render_sections_can_be_imported():
    assert callable(build_render_sections)


def test_render_context_includes_public_header_template_and_sections():
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)

    context = build_resume_render_context(
        SAMPLE_USER_PROFILE,
        SAMPLE_RESUME_CONTENT,
        selection,
    )

    assert context["full_name"] == "Alex Chen"
    assert context["selected_template_id"] == selection.selected_template_id
    assert context["template_display_name"] == selection.selected_template.display_name
    assert [section.section_id for section in context["sections"]]


def test_sections_follow_selected_template_order_and_include_content():
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)

    sections = build_render_sections(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT, selection)
    rendered_ids = [section.section_id for section in sections]

    assert rendered_ids[:2] == [
        selection.selected_template.sections[0].section_id,
        selection.selected_template.sections[1].section_id,
    ]
    assert "education" in rendered_ids
    assert any(section.section_id in {"skills", "technical_skills"} for section in sections)


def test_publications_and_portfolio_are_not_rendered_without_evidence():
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)

    sections = build_render_sections(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT, selection)
    rendered_ids = [section.section_id for section in sections if section.items]

    assert "publications_or_presentations" not in rendered_ids
    assert "portfolio" not in rendered_ids


def test_preview_reminder_is_only_added_when_option_enabled():
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)

    default_context = build_resume_render_context(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT, selection)

    assert default_context["reminder_panel_text"] is None
    assert default_context["include_preview_reminder_panel"] is False
