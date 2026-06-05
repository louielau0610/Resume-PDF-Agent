"""Tests for M14 confirmation gate helpers."""

from __future__ import annotations

from resume_pdf_agent.confirmation.gate import (
    build_confirmation_gate_warning,
    should_block_final_pdf,
)
from resume_pdf_agent.models.confirmation import (
    ConfirmationItem,
    ConfirmationItemType,
    ConfirmationPacket,
    ConfirmationPriority,
)


def _make_packet(blocking: bool) -> ConfirmationPacket:
    items: list[ConfirmationItem] = []
    if blocking:
        items.append(
            ConfirmationItem(
                item_id="b1",
                item_type=ConfirmationItemType.UNSUPPORTED_CLAIM,
                priority=ConfirmationPriority.BLOCKING,
                source_stage="test",
                claim_text="Blocking claim",
                reason="No evidence",
                suggested_user_action="Verify",
                blocks_final_pdf=True,
                requires_user_decision=True,
            )
        )
    return ConfirmationPacket(
        packet_id="test",
        items=items,
        blocking_count=1 if blocking else 0,
        high_priority_count=0,
        pending_count=len(items),
        can_generate_final_pdf=not blocking,
        summary="Test packet",
    )


class TestShouldBlockFinalPdf:

    def test_empty_packet_does_not_block(self):
        """Empty packet should not block PDF."""
        packet = ConfirmationPacket(
            packet_id="empty",
            items=[],
            blocking_count=0,
            high_priority_count=0,
            pending_count=0,
            can_generate_final_pdf=True,
            summary="Empty",
        )
        assert should_block_final_pdf(packet) is False

    def test_blocking_packet_blocks(self):
        """Packet with blocking items blocks PDF."""
        packet = _make_packet(blocking=True)
        assert should_block_final_pdf(packet) is True

    def test_non_blocking_packet_does_not_block(self):
        """Packet without blocking items does not block PDF."""
        packet = _make_packet(blocking=False)
        assert should_block_final_pdf(packet) is False


class TestBuildConfirmationGateWarning:

    def test_no_warning_when_no_blocking(self):
        """No warning when PDF can be generated."""
        packet = _make_packet(blocking=False)
        assert build_confirmation_gate_warning(packet) is None

    def test_warning_when_blocking(self):
        """Warning produced when blocking items exist."""
        packet = _make_packet(blocking=True)
        warning = build_confirmation_gate_warning(packet)
        assert warning is not None
        assert "阻塞" in warning
