from resume_pdf_agent.models import ExportFormat
from resume_pdf_agent.pipeline import run_resume_pipeline
from resume_pdf_agent.templates import select_internal_template


def test_selector_does_not_mention_probability_internal_access_or_rendering():
    result = select_internal_template()
    text = " ".join(
        [
            result.summary,
            *result.warnings,
            *[reason.message for score in result.ranked_templates for reason in score.reasons],
        ]
    ).lower()

    assert "hiring probability" not in text
    assert "offer probability" not in text
    assert "internal company screening" not in text
    assert "rendered html" not in text
    assert "generated pdf" not in text


def test_no_online_template_search_api_exists():
    import resume_pdf_agent.templates as templates

    assert not hasattr(templates, "search_online_templates")
    assert not hasattr(templates, "download_template")


def test_pipeline_placeholder_includes_template_and_later_rendering_stages():
    result = run_resume_pipeline({"target_role": "software engineer intern"})

    assert "internal_template_matching" in result["stages"]
    assert "html_rendering" in result["stages"]
    assert "pdf_generation" in result["stages"]
    assert "M11 added" in result["message"]


def test_export_format_still_only_includes_pdf():
    assert [item.value for item in ExportFormat] == ["pdf"]
