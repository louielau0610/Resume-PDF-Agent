"""PDF generation public API."""

from resume_pdf_agent.pdf.diagnostics import (
    check_mock_backend_diagnostics,
    check_playwright_diagnostics,
    check_weasyprint_diagnostics,
    get_all_pdf_backend_diagnostics,
    get_pdf_backend_diagnostics,
    summarize_pdf_backend_status,
)
from resume_pdf_agent.pdf.generator import (
    generate_pdf_from_html_result,
    generate_resume_pdf,
    is_pdf_backend_available,
)
from resume_pdf_agent.pdf.options import default_pdf_generation_options
from resume_pdf_agent.pdf.validation import validate_pdf_output

__all__ = [
    "check_mock_backend_diagnostics",
    "check_playwright_diagnostics",
    "check_weasyprint_diagnostics",
    "default_pdf_generation_options",
    "generate_pdf_from_html_result",
    "generate_resume_pdf",
    "get_all_pdf_backend_diagnostics",
    "get_pdf_backend_diagnostics",
    "is_pdf_backend_available",
    "summarize_pdf_backend_status",
    "validate_pdf_output",
]
