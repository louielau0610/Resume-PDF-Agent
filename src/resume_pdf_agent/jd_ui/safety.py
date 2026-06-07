"""Safety helpers for M21 browser JD upload UI."""

from __future__ import annotations

import html
from pathlib import Path

from resume_pdf_agent.models.jd_ui import JDClientComplianceHint


def escape_jd_ui_text(value: str) -> str:
    return html.escape(value, quote=True)


def get_client_side_jd_risk_markers() -> list[JDClientComplianceHint]:
    return [
        JDClientComplianceHint(marker="confidential", severity="blocking", explanation="Contains confidential marker", suggested_action="Do not use — this may be internal/confidential material."),
        JDClientComplianceHint(marker="internal use only", severity="blocking", explanation="Marked for internal use", suggested_action="Do not use — this appears to be internal-only content."),
        JDClientComplianceHint(marker="do not distribute", severity="blocking", explanation="Distribution restricted", suggested_action="Do not use — this content has distribution restrictions."),
        JDClientComplianceHint(marker="proprietary hiring rubric", severity="blocking", explanation="May be internal hiring rubric", suggested_action="Do not use — this appears to be a proprietary hiring rubric."),
        JDClientComplianceHint(marker="private recruiter notes", severity="blocking", explanation="May be private recruiter notes", suggested_action="Do not use — this appears to be private recruiter content."),
        JDClientComplianceHint(marker="candidate evaluation form", severity="blocking", explanation="May be evaluation form", suggested_action="Do not use — this appears to be a candidate evaluation form."),
        JDClientComplianceHint(marker="interview scorecard", severity="blocking", explanation="May be interview scorecard", suggested_action="Do not use — this appears to be an interview scorecard."),
        JDClientComplianceHint(marker="scoring rubric", severity="blocking", explanation="May be scoring rubric", suggested_action="Do not use — this appears to be a scoring rubric."),
        JDClientComplianceHint(marker="leaked", severity="blocking", explanation="May be leaked content", suggested_action="Do not use — this content may be leaked."),
        JDClientComplianceHint(marker="not for public release", severity="blocking", explanation="Not for public release", suggested_action="Do not use — this is marked as not for public release."),
        JDClientComplianceHint(marker="restricted access", severity="blocking", explanation="Restricted access content", suggested_action="Do not use — this content has access restrictions."),
    ]


def safe_jd_ui_output_path(path: str | Path) -> Path:
    return Path(path).resolve()
