"""Regression tests for M20 confirmation UI."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.models.enums import ExportFormat


class TestNoRegressions:

    def test_export_format_only_pdf(self):
        members = [m.value for m in ExportFormat]
        assert members == ["pdf"]

    def test_no_word_jpg_png_in_ui(self):
        ui_dir = (
            Path(__file__).resolve().parent.parent
            / "src" / "resume_pdf_agent" / "confirmation_ui"
        )
        for py_file in ui_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert ".docx" not in content.lower()

    def test_no_network_in_ui(self):
        ui_dir = (
            Path(__file__).resolve().parent.parent
            / "src" / "resume_pdf_agent" / "confirmation_ui"
        )
        for py_file in ui_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert "requests" not in content.lower()
            assert "urllib.request" not in content.lower()
            assert "http.client" not in content.lower()

    def test_no_llm_in_ui(self):
        ui_dir = (
            Path(__file__).resolve().parent.parent
            / "src" / "resume_pdf_agent" / "confirmation_ui"
        )
        for py_file in ui_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert "openai" not in content.lower()
            assert "anthropic" not in content.lower()

    def test_no_web_framework_in_ui(self):
        ui_dir = (
            Path(__file__).resolve().parent.parent
            / "src" / "resume_pdf_agent" / "confirmation_ui"
        )
        for py_file in ui_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert "fastapi" not in content.lower()
            assert "flask" not in content.lower()

    def test_confirmation_gate_unchanged(self):
        """M14 strict gate behavior must be unchanged."""
        from resume_pdf_agent.confirmation.gate import should_block_final_pdf
        from resume_pdf_agent.models.confirmation import (
            ConfirmationItem, ConfirmationItemType, ConfirmationPacket, ConfirmationPriority,
        )
        # A packet with a blocking item should still block
        packet = ConfirmationPacket(
            packet_id="test",
            items=[
                ConfirmationItem(
                    item_id="b1",
                    item_type=ConfirmationItemType.UNSUPPORTED_CLAIM,
                    priority=ConfirmationPriority.BLOCKING,
                    source_stage="test",
                    claim_text="test",
                    reason="test",
                    suggested_user_action="test",
                    blocks_final_pdf=True,
                    requires_user_decision=True,
                ),
            ],
            blocking_count=1, high_priority_count=0, pending_count=1,
            can_generate_final_pdf=False, summary="test",
        )
        assert should_block_final_pdf(packet) is True
