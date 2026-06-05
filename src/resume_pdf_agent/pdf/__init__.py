"""PDF generation public API."""

from resume_pdf_agent.pdf.generator import (
    generate_pdf_from_html_result,
    generate_resume_pdf,
    is_pdf_backend_available,
)
from resume_pdf_agent.pdf.options import default_pdf_generation_options
from resume_pdf_agent.pdf.validation import validate_pdf_output

__all__ = [
    "default_pdf_generation_options",
    "generate_pdf_from_html_result",
    "generate_resume_pdf",
    "is_pdf_backend_available",
    "validate_pdf_output",
]
