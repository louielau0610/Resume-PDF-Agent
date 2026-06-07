"""UI context builder for M21 browser JD upload UI."""

from __future__ import annotations

from resume_pdf_agent.jd_ui.safety import get_client_side_jd_risk_markers
from resume_pdf_agent.models.jd_ui import JDUploadUIOptions


def build_jd_upload_ui_context(options: JDUploadUIOptions | None = None) -> dict:
    opts = options or JDUploadUIOptions()
    markers = get_client_side_jd_risk_markers()

    return {
        "page_title": "JD Intake / 岗位描述输入",
        "safety_notice": (
            "Only paste public job descriptions that you are allowed to use. "
            "This browser page provides local hints only; the backend M15 "
            "compliance check remains authoritative."
        ),
        "compliance_markers": [
            {
                "marker": m.marker,
                "severity": m.severity,
                "explanation": m.explanation,
                "suggested_action": m.suggested_action,
            }
            for m in markers
        ],
        "cli_instructions": [
            "Save the JD text as jd_text.txt",
            "Run: py -m resume_pdf_agent run-sample --output-dir outputs/jd_run --pdf-backend mock --jd-file jd_text.txt --use-user-provided-jd --write-frontend-page",
            "The backend M15 compliance check will validate your JD before parsing.",
        ],
        "options": {
            "include_copy_buttons": opts.include_copy_buttons,
            "include_download_buttons": opts.include_download_buttons,
            "include_compliance_hints": opts.include_compliance_hints,
            "include_workflow_json_generator": opts.include_workflow_json_generator,
            "include_cli_instructions": opts.include_cli_instructions,
            "language": opts.language,
        },
    }
