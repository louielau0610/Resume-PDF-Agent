"""Confirmation gate helpers for M14.

Determines whether final PDF generation should be blocked based on
confirmation packet status.
"""

from __future__ import annotations

from resume_pdf_agent.models.confirmation import ConfirmationPacket


def should_block_final_pdf(packet: ConfirmationPacket) -> bool:
    """Check if the confirmation packet blocks final PDF generation.

    Parameters
    ----------
    packet : ConfirmationPacket
        The confirmation packet to check.

    Returns
    -------
    bool
        True if final PDF should be blocked.
    """
    if not packet.items:
        return False
    return not packet.can_generate_final_pdf


def build_confirmation_gate_warning(packet: ConfirmationPacket) -> str | None:
    """Build a warning message if final PDF is blocked.

    Parameters
    ----------
    packet : ConfirmationPacket
        The confirmation packet to check.

    Returns
    -------
    str | None
        Warning message, or None if PDF can be generated.
    """
    if not should_block_final_pdf(packet):
        return None

    return (
        f"确认门控已激活：存在 {packet.blocking_count} 个阻塞项。"
        f"在审核完成前无法生成最终 PDF。"
        f"请查看 confirmation_packet.json 和 confirmation_review.md 了解详情。"
        f"完成审核后，使用 --confirmation-decisions 加载您的决策文件。"
    )
