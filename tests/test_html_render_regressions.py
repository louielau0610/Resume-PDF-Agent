from pathlib import Path

from resume_pdf_agent.config import SUPPORTED_EXPORT_FORMATS
from resume_pdf_agent.models import ExportFormat
from resume_pdf_agent.pipeline import run_resume_pipeline


def test_pipeline_placeholder_still_includes_html_rendering_and_pdf_generation():
    result = run_resume_pipeline({"profile": True})

    assert "html_rendering" in result["stages"]
    assert "pdf_generation" in result["stages"]


def test_export_format_still_only_includes_pdf():
    assert list(ExportFormat) == [ExportFormat.PDF]
    assert SUPPORTED_EXPORT_FORMATS == [ExportFormat.PDF]


def test_renderer_source_does_not_implement_online_template_search_or_llm_calls():
    rendering_dir = Path("src/resume_pdf_agent/rendering")
    source = "\n".join(path.read_text(encoding="utf-8") for path in rendering_dir.rglob("*.py"))
    lowered = source.lower()

    assert "requests" not in lowered
    assert "httpx" not in lowered
    assert "openai" not in lowered
    assert "anthropic" not in lowered
    assert "gemini" not in lowered
    assert "search_query" not in lowered
