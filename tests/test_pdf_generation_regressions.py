from pathlib import Path

from resume_pdf_agent.config import SUPPORTED_EXPORT_FORMATS
from resume_pdf_agent.models import ExportFormat, PDFBackend, PDFGenerationOptions
from resume_pdf_agent.pdf import generate_resume_pdf
from resume_pdf_agent.pipeline import run_resume_pipeline
from resume_pdf_agent.sample_data import SAMPLE_RESUME_CONTENT, SAMPLE_USER_PROFILE
from resume_pdf_agent.templates import select_internal_template


def test_no_word_jpg_png_files_are_generated(tmp_path):
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)

    generate_resume_pdf(
        SAMPLE_USER_PROFILE,
        SAMPLE_RESUME_CONTENT,
        selection,
        output_path=tmp_path / "resume.pdf",
        pdf_options=PDFGenerationOptions(backend=PDFBackend.MOCK),
    )

    assert not list(Path(tmp_path).rglob("*.docx"))
    assert not list(Path(tmp_path).rglob("*.jpg"))
    assert not list(Path(tmp_path).rglob("*.jpeg"))
    assert not list(Path(tmp_path).rglob("*.png"))


def test_frontend_is_static_only_no_react_or_fastapi():
    """M11 frontend exists but must be static HTML/CSS/JS only."""
    frontend_dir = Path("src/resume_pdf_agent/frontend")
    # The frontend dir now exists (M11) — verify it is static-only
    assert frontend_dir.exists()

    # Check no server/framework deps
    all_py = list(frontend_dir.rglob("*.py"))
    all_sources = "\n".join(f.read_text(encoding="utf-8").lower() for f in all_py)
    forbidden = ["fastapi", "flask", "react", "streamlit", "uvicorn"]
    for kw in forbidden:
        assert kw not in all_sources, f"'{kw}' found in frontend Python files"

    # Check no package.json or node_modules
    assert not (frontend_dir / "package.json").exists()
    assert not (frontend_dir / "node_modules").exists()


def test_pdf_generator_does_not_report_hiring_probability_or_internal_screening_access(tmp_path):
    selection = select_internal_template(SAMPLE_USER_PROFILE, SAMPLE_RESUME_CONTENT)

    result = generate_resume_pdf(
        SAMPLE_USER_PROFILE,
        SAMPLE_RESUME_CONTENT,
        selection,
        output_path=tmp_path / "resume.pdf",
        pdf_options=PDFGenerationOptions(backend=PDFBackend.MOCK),
    )
    combined = f"{result.summary} {result.conversion_reminder}".lower()

    assert "hiring probability" not in combined
    assert "interview probability" not in combined
    assert "internal company screening" not in combined


def test_pdf_generator_source_does_not_call_llm_apis_or_search_templates():
    pdf_dir = Path("src/resume_pdf_agent/pdf")
    source = "\n".join(path.read_text(encoding="utf-8") for path in pdf_dir.rglob("*.py"))
    lowered = source.lower()

    assert "openai" not in lowered
    assert "anthropic" not in lowered
    assert "gemini" not in lowered
    assert "search_query" not in lowered
    assert "requests" not in lowered
    assert "httpx" not in lowered


def test_pipeline_placeholder_still_includes_pdf_generation_and_reminder_panel():
    result = run_resume_pipeline({"target_role": "data science intern"})

    assert "pdf_generation" in result["stages"]
    assert "reminder_panel" in result["stages"]
    assert "M11 added" in result["message"]


def test_export_format_still_only_includes_pdf():
    assert list(ExportFormat) == [ExportFormat.PDF]
    assert SUPPORTED_EXPORT_FORMATS == ["pdf"]
