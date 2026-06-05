"""Placeholder workflow pipeline for the M9 PDF generation foundation."""

from resume_pdf_agent.config import SUPPORTED_EXPORT_FORMATS


def run_resume_pipeline(input_data: dict) -> dict:
    """Return a structured M9 placeholder response for the planned pipeline.

    M9 adds PDF generation helpers for M8 HTML output. This placeholder still
    does not run the full production workflow.
    """

    return {
        "status": "skeleton",
        "stages": [
            "user_intake",
            "criteria_selection",
            "profile_structuring",
            "gap_analysis",
            "truthfulness_check",
            "criteria_aware_content_enhancement",
            "resume_type_classification",
            "internal_template_matching",
            "html_rendering",
            "pdf_generation",
            "reminder_panel",
        ],
        "message": (
            "M7 deterministic internal template selector can choose internal "
            "template metadata, and M8 deterministic HTML renderer can render "
            "structured resume content with that selected metadata. M9 PDF "
            "generation pipeline can convert rendered HTML to local PDF files. "
            "The pipeline is still a placeholder: no online template search, "
            "LLM calls, live JD analysis, or frontend UI is implemented. "
            "PDF is the only supported target export format for v0."
        ),
        "supported_export_formats": SUPPORTED_EXPORT_FORMATS,
        "input_received": bool(input_data),
    }
