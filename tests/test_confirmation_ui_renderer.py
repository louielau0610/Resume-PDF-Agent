"""Tests for M20 confirmation UI renderer."""

from __future__ import annotations

import json
from pathlib import Path

from resume_pdf_agent.confirmation_ui.renderer import (
    render_confirmation_ui_from_packet_file,
    render_confirmation_ui_page,
)
from resume_pdf_agent.models.confirmation import (
    ConfirmationItem,
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
            suggested_user_action="Please provide evidence or revise claim.",
            blocks_final_pdf=True,
            requires_user_decision=True,
            risk_flags=["unsupported_evidence"],
        ),
    ]
    return ConfirmationPacket(
        packet_id="test_render",
        items=items,
        blocking_count=1,
        high_priority_count=0,
        pending_count=1,
        can_generate_final_pdf=False,
        summary="Test render packet",
    )


class TestRenderConfirmationUiPage:

    def test_renders_html(self, tmp_path):
        packet = _make_packet()
        out = tmp_path / "confirmation.html"
        result = render_confirmation_ui_page(packet, out)
        assert result.output_path is not None
        assert out.is_file()
        assert len(result.html) > 0
        assert result.item_count == 1
        assert result.blocking_count == 1

    def test_html_contains_packet_id(self, tmp_path):
        packet = _make_packet()
        out = tmp_path / "confirmation.html"
        result = render_confirmation_ui_page(packet, out)
        assert "test_render" in result.html

    def test_html_contains_item_id(self, tmp_path):
        packet = _make_packet()
        out = tmp_path / "confirmation.html"
        result = render_confirmation_ui_page(packet, out)
        assert "b1" in result.html

    def test_html_contains_claim_text(self, tmp_path):
        packet = _make_packet()
        out = tmp_path / "confirmation.html"
        result = render_confirmation_ui_page(packet, out)
        assert "Led a team of 50 people" in result.html

    def test_html_contains_decision_controls(self, tmp_path):
        packet = _make_packet()
        out = tmp_path / "confirmation.html"
        result = render_confirmation_ui_page(packet, out)
        assert "decision-select" in result.html
        assert "approve" in result.html.lower()

    def test_html_contains_safety_notice(self, tmp_path):
        packet = _make_packet()
        out = tmp_path / "confirmation.html"
        result = render_confirmation_ui_page(packet, out)
        assert "personally verify" in result.html.lower() or "亲自" in result.html

    def test_html_no_hiring_probability(self, tmp_path):
        packet = _make_packet()
        out = tmp_path / "confirmation.html"
        result = render_confirmation_ui_page(packet, out)
        html_lower = result.html.lower()
        # The safety disclaimer may mention "predict hiring probability" in a negative context
        # But should never AFFIRM it
        assert "predicts hiring probability" not in html_lower
        assert "guarantees hiring" not in html_lower

    def test_html_no_internal_screening(self, tmp_path):
        packet = _make_packet()
        out = tmp_path / "confirmation.html"
        result = render_confirmation_ui_page(packet, out)
        assert "internal screening" not in result.html.lower()

    def test_html_no_external_cdn(self, tmp_path):
        packet = _make_packet()
        out = tmp_path / "confirmation.html"
        result = render_confirmation_ui_page(packet, out)
        # Should not reference external CDN URLs
        assert "cdn." not in result.html.lower()

    def test_html_no_external_fonts(self, tmp_path):
        packet = _make_packet()
        out = tmp_path / "confirmation.html"
        result = render_confirmation_ui_page(packet, out)
        assert "fonts.googleapis.com" not in result.html.lower()

    def test_html_escapes_script_tag_in_claim(self, tmp_path):
        packet = ConfirmationPacket(
            packet_id="xss_test",
            items=[
                ConfirmationItem(
                    item_id="x1",
                    item_type=ConfirmationItemType.UNSUPPORTED_CLAIM,
                    priority=ConfirmationPriority.BLOCKING,
                    source_stage="test",
                    claim_text="<script>alert(1)</script>",
                    reason="Malicious claim",
                    suggested_user_action="Remove this claim",
                    blocks_final_pdf=True,
                    requires_user_decision=True,
                ),
            ],
            blocking_count=1,
            high_priority_count=0,
            pending_count=1,
            can_generate_final_pdf=False,
            summary="XSS test",
        )
        out = tmp_path / "xss_test.html"
        result = render_confirmation_ui_page(packet, out)
        # Raw script tag should not appear in HTML
        assert "<script>alert(1)</script>" not in result.html
        # The escaped version should appear as text
        assert "&lt;script&gt;" in result.html or "alert(1)" in result.html

    def test_html_has_json_preview(self, tmp_path):
        packet = _make_packet()
        out = tmp_path / "confirmation.html"
        result = render_confirmation_ui_page(packet, out)
        assert "decisions-json" in result.html
        assert "confirmation_decisions.json" in result.html


class TestRenderConfirmationUiFromPacketFile:

    def test_renders_from_file(self, tmp_path):
        packet = _make_packet()
        pkt_path = tmp_path / "confirmation_packet.json"
        pkt_path.write_text(packet.model_dump_json(indent=2), encoding="utf-8")
        out = tmp_path / "confirmation.html"
        result = render_confirmation_ui_from_packet_file(pkt_path, out)
        assert result.output_path is not None
        assert out.is_file()

    def test_missing_packet_returns_error(self, tmp_path):
        result = render_confirmation_ui_from_packet_file(
            tmp_path / "nonexistent.json",
            tmp_path / "out.html",
        )
        assert result.status.value == "failed"
        assert len(result.errors) > 0
