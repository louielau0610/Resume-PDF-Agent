import pytest
from pydantic import ValidationError

from resume_pdf_agent.models import PDFBackend, PDFGenerationOptions, PDFPageFormat
from resume_pdf_agent.pdf.options import build_conversion_reminder, default_pdf_generation_options


def test_pdf_generation_options_defaults_are_valid():
    options = default_pdf_generation_options()

    assert options.backend == PDFBackend.WEASYPRINT
    assert options.page_format == PDFPageFormat.A4
    assert options.margin_top_mm == 10.0
    assert options.print_background is True
    assert options.prefer_single_page is True
    assert options.include_conversion_reminder is True


def test_negative_margins_are_rejected():
    with pytest.raises(ValidationError):
        PDFGenerationOptions(margin_left_mm=-1.0)


def test_build_conversion_reminder_returns_neutral_text_when_enabled():
    reminder = build_conversion_reminder(True)

    assert reminder is not None
    assert "external PDF conversion tool" in reminder
    assert "Word, JPG, or PNG" in reminder


def test_build_conversion_reminder_returns_none_when_disabled():
    assert build_conversion_reminder(False) is None
