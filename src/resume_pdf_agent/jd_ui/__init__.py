"""M21 Browser-based JD Upload UI package."""

from resume_pdf_agent.jd_ui.context import build_jd_upload_ui_context
from resume_pdf_agent.jd_ui.renderer import render_jd_upload_ui_page
from resume_pdf_agent.jd_ui.safety import get_client_side_jd_risk_markers

__all__ = ["build_jd_upload_ui_context", "get_client_side_jd_risk_markers", "render_jd_upload_ui_page"]
