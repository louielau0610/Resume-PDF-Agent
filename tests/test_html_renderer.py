from pathlib import Path

from resume_pdf_agent.models import (
    HTMLRenderOptions,
    HTMLRenderStatus,
    TemplateScore,
    TemplateSelectionResult,
)
from resume_pdf_agent.rendering import render_resume_html, write_rendered_html
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.templates import select_internal_template


def test_render_resume_html_and_write_rendered_html_can_be_imported():
    assert callable(render_resume_html)
    assert callable(write_rendered_html)


def test_render_resume_html_returns_result_with_expected_content():
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)

    result = render_resume_html(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT, selection)

    assert result.status in {
        HTMLRenderStatus.RENDERED,
        HTMLRenderStatus.RENDERED_WITH_WARNINGS,
    }
    assert "Alex Chen" in result.html
    assert "Education" in result.html
    assert "Skills" in result.html or "Technical Skills" in result.html
    assert "Cleaned anonymized course review data" in result.html
    assert result.template_id == selection.selected_template_id


def test_write_rendered_html_writes_local_file_and_stores_output_path(tmp_path):
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)
    result = render_resume_html(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT, selection)
    output_path = tmp_path / "nested" / "resume.html"

    written = write_rendered_html(result, output_path)

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8") == result.html
    assert written.output_path == str(output_path)
    assert not list(tmp_path.rglob("*.pdf"))


def test_missing_template_file_falls_back_to_ats_student_basic():
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)
    missing_selection = TemplateSelectionResult(
        selected_template_id="missing_template",
        selected_template=selection.selected_template,
        ranked_templates=[TemplateScore(template_id="missing_template", score=1.0)],
        recommended_sections=selection.recommended_sections,
        warnings=[],
        summary="Test missing template selection.",
    )

    result = render_resume_html(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT, missing_selection)

    assert result.template_id == "ats_student_basic"
    assert result.status == HTMLRenderStatus.RENDERED_WITH_WARNINGS
    assert "fell back to" in " ".join(result.warnings)


def test_preview_wrapper_can_include_reminder_outside_resume_document():
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)

    default_result = render_resume_html(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT, selection)
    preview_result = render_resume_html(
        SAMPLE_USER_PROFILE,
        SAMPLE_RESUME_CONTENT,
        selection,
        options=HTMLRenderOptions(include_preview_reminder_panel=True),
    )

    assert "Word, JPG, or PNG" not in default_result.html
    assert "Word, JPG, or PNG" in preview_result.html
    assert preview_result.html.index("preview-panel") < preview_result.html.index('id="resume-document"')


def test_renderer_does_not_report_hiring_probability_or_internal_screening_access():
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)

    result = render_resume_html(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT, selection)
    combined = f"{result.html} {result.summary}".lower()

    assert "hiring probability" not in combined
    assert "interview probability" not in combined
    assert "internal company screening" not in combined


def test_no_pdf_file_is_generated_in_m8(tmp_path):
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)
    result = render_resume_html(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT, selection)

    write_rendered_html(result, tmp_path / "resume.html")

    assert not list(Path(tmp_path).rglob("*.pdf"))
