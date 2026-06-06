"""Safety helpers for M20 browser confirmation UI."""

from __future__ import annotations

import html
from pathlib import Path

from resume_pdf_agent.models.confirmation import ConfirmationPacket


def escape_confirmation_ui_text(value: str) -> str:
    """Escape user-provided text for safe HTML rendering.

    Parameters
    ----------
    value : str
        Text to escape.

    Returns
    -------
    str
        HTML-escaped text.
    """
    return html.escape(value, quote=True)


def safe_confirmation_output_path(path: str | Path) -> Path:
    """Validate and normalize a confirmation UI output path.

    Parameters
    ----------
    path : str | Path
        Desired output path.

    Returns
    -------
    Path
        Normalized absolute path.
    """
    p = Path(path).resolve()
    return p


def validate_confirmation_packet_for_ui(packet: ConfirmationPacket) -> list[str]:
    """Validate that a confirmation packet is suitable for UI rendering.

    Parameters
    ----------
    packet : ConfirmationPacket
        The packet to validate.

    Returns
    -------
    list[str]
        List of issues found. Empty means valid.
    """
    issues: list[str] = []
    if not packet.items:
        issues.append("Confirmation packet contains no items.")
    if not packet.packet_id:
        issues.append("Packet ID is empty.")
    return issues
