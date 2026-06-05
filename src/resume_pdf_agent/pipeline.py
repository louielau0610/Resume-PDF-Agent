"""Placeholder pipeline module kept for backward compatibility.

For the real deterministic local workflow, use:

    from resume_pdf_agent.workflow import run_resume_workflow

M10 added a full end-to-end workflow orchestrator connected to all existing
M0–M9 modules. The CLI entry point is in ``resume_pdf_agent.cli``.
"""

from resume_pdf_agent.config import SUPPORTED_EXPORT_FORMATS


def run_resume_pipeline(input_data: dict) -> dict:
    """Return a structured M10 placeholder response pointing to the real workflow.

    The production workflow lives in ``resume_pdf_agent.workflow.run_resume_workflow``.
    """

    return {
        "status": "redirect",
        "stages": [
            "user_intake",
            "criteria_selection",
            "resume_type_classification",
            "gap_analysis",
            "truthfulness_check",
            "criteria_aware_content_enhancement",
            "internal_template_matching",
            "html_rendering",
            "pdf_generation",
            "artifact_writing",
            "reminder_panel",
        ],
        "message": (
            "M10 integrated the deterministic local workflow. Use "
            "'resume_pdf_agent.workflow.run_resume_workflow' for programmatic access "
            "or the CLI ('py -m resume_pdf_agent run-sample') for command-line use. "
            "No LLM calls, no online template search, no frontend UI. "
            "PDF is the only supported export format for v0."
        ),
        "supported_export_formats": SUPPORTED_EXPORT_FORMATS,
        "input_received": bool(input_data),
    }
