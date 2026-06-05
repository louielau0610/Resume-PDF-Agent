"""Tests for M14 confirmation decisions."""

from __future__ import annotations

from pathlib import Path

import pytest

from resume_pdf_agent.confirmation.decisions import (
    apply_confirmation_decisions,
    load_confirmation_decisions,
)
from resume_pdf_agent.models.confirmation import (
    ConfirmationDecision,
    ConfirmationDecisionSet,
    ConfirmationDecisionType,
    ConfirmationItem,
    ConfirmationItemStatus,
    ConfirmationItemType,
    ConfirmationPacket,
    ConfirmationPriority,
)


# ── Helpers ────────────────────────────────────────────────────────────────

def _make_packet(with_blocking: bool = True) -> ConfirmationPacket:
    items = [
        ConfirmationItem(
            item_id="item1",
            item_type=ConfirmationItemType.UNSUPPORTED_CLAIM,
            priority=ConfirmationPriority.BLOCKING if with_blocking else ConfirmationPriority.LOW,
            source_stage="test",
            claim_text="Test claim",
            reason="Test reason",
            suggested_user_action="Verify",
            blocks_final_pdf=with_blocking,
            requires_user_decision=True,
        ),
        ConfirmationItem(
            item_id="item2",
            item_type=ConfirmationItemType.GAP_ANALYSIS_WARNING,
            priority=ConfirmationPriority.LOW,
            source_stage="test",
            claim_text="Test warning",
            reason="Test reason",
            suggested_user_action="Check",
            blocks_final_pdf=False,
            requires_user_decision=False,
        ),
    ]
    blocking = sum(1 for i in items if i.blocks_final_pdf)
    return ConfirmationPacket(
        packet_id="test_packet",
        items=items,
        blocking_count=blocking,
        high_priority_count=0,
        pending_count=len(items),
        can_generate_final_pdf=not with_blocking,
        summary="Test packet",
    )


# ── Tests ──────────────────────────────────────────────────────────────────


class TestApplyConfirmationDecisions:
    """Tests for apply_confirmation_decisions."""

    def test_approve_resolves_item(self):
        """Approve decision resolves an item."""
        packet = _make_packet()
        ds = ConfirmationDecisionSet(
            decisions=[
                ConfirmationDecision(
                    item_id="item1", decision=ConfirmationDecisionType.APPROVE,
                )
            ]
        )
        result = apply_confirmation_decisions(packet, ds)
        assert len(result.resolved_items) == 1
        assert result.resolved_items[0].item_id == "item1"
        assert result.resolved_items[0].status == ConfirmationItemStatus.RESOLVED

    def test_reject_marks_rejected(self):
        """Reject decision marks an item rejected."""
        packet = _make_packet()
        ds = ConfirmationDecisionSet(
            decisions=[
                ConfirmationDecision(
                    item_id="item1", decision=ConfirmationDecisionType.REJECT,
                )
            ]
        )
        result = apply_confirmation_decisions(packet, ds)
        assert len(result.rejected_items) == 1
        assert result.rejected_items[0].status == ConfirmationItemStatus.REJECTED

    def test_needs_editing_marks_accordingly(self):
        """needs_editing decision marks item for editing."""
        packet = _make_packet()
        ds = ConfirmationDecisionSet(
            decisions=[
                ConfirmationDecision(
                    item_id="item1",
                    decision=ConfirmationDecisionType.NEEDS_EDITING,
                    replacement_text="Fixed text",
                )
            ]
        )
        result = apply_confirmation_decisions(packet, ds)
        assert len(result.needs_editing_items) == 1
        assert result.needs_editing_items[0].status == ConfirmationItemStatus.NEEDS_EDITING

    def test_provide_evidence_resolves_with_evidence(self):
        """provide_evidence with evidence resolves the item."""
        packet = _make_packet()
        ds = ConfirmationDecisionSet(
            decisions=[
                ConfirmationDecision(
                    item_id="item1",
                    decision=ConfirmationDecisionType.PROVIDE_EVIDENCE,
                    provided_evidence="Evidence document attached.",
                )
            ]
        )
        result = apply_confirmation_decisions(packet, ds)
        assert len(result.resolved_items) == 1

    def test_ignore_for_now_does_not_resolve_blocking(self):
        """ignore_for_now on a blocking item keeps it unresolved."""
        packet = _make_packet(with_blocking=True)
        ds = ConfirmationDecisionSet(
            decisions=[
                ConfirmationDecision(
                    item_id="item1",
                    decision=ConfirmationDecisionType.IGNORE_FOR_NOW,
                )
            ]
        )
        result = apply_confirmation_decisions(packet, ds)
        assert len(result.unresolved_items) >= 1
        assert result.can_generate_final_pdf is False

    def test_ignore_for_now_on_non_blocking(self):
        """ignore_for_now on a non-blocking item is fine."""
        packet = _make_packet(with_blocking=True)
        ds = ConfirmationDecisionSet(
            decisions=[
                ConfirmationDecision(
                    item_id="item2",
                    decision=ConfirmationDecisionType.IGNORE_FOR_NOW,
                )
            ]
        )
        result = apply_confirmation_decisions(packet, ds)
        # item2 is non-blocking, so can_generate may still be false due to item1
        # but item2 should be in resolved (ignored)
        assert len(result.resolved_items) >= 1

    def test_does_not_mutate_original_packet(self):
        """Applying decisions should not mutate the original packet items."""
        packet = _make_packet()
        original_status = packet.items[0].status
        ds = ConfirmationDecisionSet(
            decisions=[
                ConfirmationDecision(
                    item_id="item1", decision=ConfirmationDecisionType.APPROVE,
                )
            ]
        )
        apply_confirmation_decisions(packet, ds)
        # Original packet item status should be unchanged
        # (Note: we pass copies implicitly via dict/list unpacking)
        assert packet.items[0].status == original_status

    def test_unknown_item_id_creates_warning(self):
        """Decision on unknown item_id creates a warning."""
        packet = _make_packet()
        ds = ConfirmationDecisionSet(
            decisions=[
                ConfirmationDecision(
                    item_id="nonexistent",
                    decision=ConfirmationDecisionType.APPROVE,
                )
            ]
        )
        result = apply_confirmation_decisions(packet, ds)
        assert len(result.warnings) >= 1
        assert "unknown" in result.warnings[0].lower()

    def test_can_generate_final_pdf_with_all_resolved(self):
        """When all blocking items are resolved, can_generate_final_pdf is True."""
        packet = _make_packet(with_blocking=True)
        ds = ConfirmationDecisionSet(
            decisions=[
                ConfirmationDecision(
                    item_id="item1", decision=ConfirmationDecisionType.APPROVE,
                ),
                ConfirmationDecision(
                    item_id="item2",
                    decision=ConfirmationDecisionType.IGNORE_FOR_NOW,
                ),
            ]
        )
        result = apply_confirmation_decisions(packet, ds)
        assert result.can_generate_final_pdf is True


class TestLoadConfirmationDecisions:
    """Tests for load_confirmation_decisions."""

    def test_load_sample_decisions(self):
        """Can load the sample confirmation decisions file."""
        sample_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "sample_inputs"
            / "sample_confirmation_decisions.json"
        )
        if not sample_path.is_file():
            pytest.skip("Sample confirmation decisions file not found.")
        ds = load_confirmation_decisions(sample_path)
        assert isinstance(ds, ConfirmationDecisionSet)
        assert len(ds.decisions) > 0


class TestConfirmationDecisionValidation:
    """Tests for ConfirmationDecision model validators."""

    def test_provide_evidence_requires_evidence(self):
        """provide_evidence without evidence raises error."""
        with pytest.raises(ValueError):
            ConfirmationDecision(
                item_id="test",
                decision=ConfirmationDecisionType.PROVIDE_EVIDENCE,
            )

    def test_needs_editing_requires_detail(self):
        """needs_editing without replacement or note raises error."""
        with pytest.raises(ValueError):
            ConfirmationDecision(
                item_id="test",
                decision=ConfirmationDecisionType.NEEDS_EDITING,
            )

    def test_needs_editing_with_replacement_ok(self):
        """needs_editing with replacement_text is valid."""
        d = ConfirmationDecision(
            item_id="test",
            decision=ConfirmationDecisionType.NEEDS_EDITING,
            replacement_text="New text",
        )
        assert d.decision == ConfirmationDecisionType.NEEDS_EDITING
