"""M20 Browser-based Confirmation UI package."""

from resume_pdf_agent.confirmation_ui.context import build_confirmation_ui_context
from resume_pdf_agent.confirmation_ui.renderer import (
    render_confirmation_ui_from_packet_file,
    render_confirmation_ui_page,
)

__all__ = [
    "build_confirmation_ui_context",
    "render_confirmation_ui_from_packet_file",
    "render_confirmation_ui_page",
]
