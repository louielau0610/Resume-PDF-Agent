"""Option helpers for PDF generation."""

from resume_pdf_agent.models import PDFGenerationOptions

CONVERSION_REMINDER_TEXT = (
    "Current v0 output is PDF. If you need Word, JPG, or PNG, use an external "
    "PDF conversion tool after export."
)


def default_pdf_generation_options() -> PDFGenerationOptions:
    """Return default PDF generation options."""

    return PDFGenerationOptions()


def build_conversion_reminder(include: bool = True) -> str | None:
    """Return neutral export conversion reminder metadata when enabled."""

    if not include:
        return None
    return CONVERSION_REMINDER_TEXT
