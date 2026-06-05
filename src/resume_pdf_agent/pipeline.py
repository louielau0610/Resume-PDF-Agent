"""Placeholder workflow pipeline for the M4 gap analysis foundation."""

from resume_pdf_agent.config import SUPPORTED_EXPORT_FORMATS


def run_resume_pipeline(input_data: dict) -> dict:
    """Return a structured M4 placeholder response for the planned pipeline.

    M4 adds a deterministic criteria gap analysis engine only. It intentionally
    does not perform LLM rewriting, real job description analysis, resume
    rewriting, rendering, or PDF generation.
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
            "M4 deterministic gap analysis engine can compare candidate evidence "
            "against manually curated criteria profiles. The pipeline is still a "
            "placeholder: no real LLM rewriting, live JD analysis, resume rewriting, "
            "template matching, HTML rendering, or PDF generation is implemented. "
            "PDF is the only supported target export format for v0."
        ),
        "supported_export_formats": SUPPORTED_EXPORT_FORMATS,
        "input_received": bool(input_data),
    }
