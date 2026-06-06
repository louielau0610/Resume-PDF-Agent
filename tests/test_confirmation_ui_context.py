"""Tests for M20 confirmation UI context builder."""

from __future__ import annotations

from resume_pdf_agent.confirmation_ui.context import build_confirmation_ui_context
from resume_pdf_agent.models.confirmation import (
    ConfirmationItem,
    ConfirmationItemStatus,
    ConfirmationItemType,
    ConfirmationPacket,
    ConfirmationPriority,
)


def _make_packet() -> ConfirmationPacket:
    items = [
        ConfirmationItem(
            item_id="b1",
            item_type=ConfirmationItemType.UNSUPPORTED_CLAIM,
            priority=ConfirmationPriority.BLOCKING,
            source_stage="truthfulness_check",
            claim_text="Led a team of 50 people",
            reason="No evidence for team size",
            suggested_user_action="Provide evidence or revise",
            blocks_final_pdf=True,
            requires_user_decision=True,
        ),
        ConfirmationItem(
            item_id="h1",
            item_type=ConfirmationItemType.RISKY_ENHANCED_BULLET,
            priority=ConfirmationPriority.HIGH,
            source_stage="enhancement",
            claim_text="Improved efficiency significantly",
            reason="No metric support",
            suggested_user_action="Add quantitative evidence",
            blocks_final_pdf=False,
            requires_user_decision=True,
        ),
    ]
    return ConfirmationPacket(
        packet_id="test_packet",
        items=items,
        blocking_count=1,
        high_priority_count=1,
        pending_count=2,
        can_generate_final_pdf=False,
        summary="Test packet",
    )


class TestBuildConfirmationUiContext:

    def test_returns_required_keys(self):
        ctx = build_confirmation_ui_context(_make_packet())
        required = [
            "packet_id", "item_count", "blocking_count",
            "high_priority_count", "pending_count",
            "can_generate_final_pdf", "groups", "decision_options",
        ]
        for key in required:
            assert key in ctx, f"Missing key: {key}"

    def test_packet_id_present(self):
        ctx = build_confirmation_ui_context(_make_packet())
        assert "test_packet" in ctx["packet_id"]

    def test_item_count_correct(self):
        ctx = build_confirmation_ui_context(_make_packet())
        assert ctx["item_count"] == 2

    def test_blocking_count_correct(self):
        ctx = build_confirmation_ui_context(_make_packet())
        assert ctx["blocking_count"] == 1

    def test_groups_items_by_priority(self):
        ctx = build_confirmation_ui_context(_make_packet())
        assert len(ctx["groups"]["blocking"]) == 1
        assert len(ctx["groups"]["high"]) == 1

    def test_decision_options_present(self):
        ctx = build_confirmation_ui_context(_make_packet())
        opts = ctx["decision_options"]
        decisions = [o["value"] for o in opts]
        assert "approve" in decisions
        assert "reject" in decisions
        assert "needs_editing" in decisions
        assert "provide_evidence" in decisions
        assert "ignore_for_now" in decisions

    def test_no_hiring_probability(self):
        ctx = build_confirmation_ui_context(_make_packet())
        ctx_str = str(ctx).lower()
        assert "hiring probability" not in ctx_str

    def test_no_internal_screening(self):
        ctx = build_confirmation_ui_context(_make_packet())
        ctx_str = str(ctx).lower()
        assert "internal screening" not in ctx_str

    def test_no_raw_html_in_context(self):
        ctx = build_confirmation_ui_context(_make_packet())
        ctx_str = str(ctx)
        assert "<script>" not in ctx_str
