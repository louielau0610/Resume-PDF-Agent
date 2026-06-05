"""Placeholder pipeline module kept for backward compatibility.

For the real deterministic local workflow, use:

    from resume_pdf_agent.workflow import run_resume_workflow

For the static frontend dashboard page, use:

    from resume_pdf_agent.frontend import render_frontend_workflow_page

M10 added a full end-to-end workflow orchestrator.
M11 added a static HTML workflow dashboard page renderer.
"""

from resume_pdf_agent.config import SUPPORTED_EXPORT_FORMATS


def run_resume_pipeline(input_data: dict) -> dict:
    """Return a structured M11 placeholder response pointing to the real workflow.

    The production workflow lives in ``resume_pdf_agent.workflow.run_resume_workflow``.
    The frontend dashboard lives in ``resume_pdf_agent.frontend.render_frontend_workflow_page``.
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
            "M11 added a static frontend workflow dashboard page. "
            "Use 'resume_pdf_agent.workflow.run_resume_workflow' for programmatic "
            "access or the CLI ('py -m resume_pdf_agent run-sample --write-frontend-page') "
            "for command-line use. Use 'resume_pdf_agent.frontend.render_frontend_workflow_page' "
            "to generate a static index.html dashboard. "
            "No LLM calls, no online template search, no frontend framework (React/FastAPI), "
            "no web server. PDF is the only supported export format for v0."
        ),
        "supported_export_formats": SUPPORTED_EXPORT_FORMATS,
        "input_received": bool(input_data),
    }
