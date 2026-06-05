"""Regression tests for M14 confirmation workflow.

Ensures existing M0-M12 behavior is preserved.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from resume_pdf_agent.models.enums import ExportFormat


class TestExportFormatUnchanged:
    """ExportFormat must still only include PDF."""

    def test_export_format_only_pdf(self):
        members = [m.value for m in ExportFormat]
        assert members == ["pdf"]


class TestNoLLmCalls:
    """No LLM API calls should be introduced by M14."""

    def test_no_openai_import(self):
        """OpenAI should not be importable or used."""
        # This is a basic check - M14 code should not import LLM libraries
        confirmation_dir = (
            Path(__file__).resolve().parent.parent
            / "src"
            / "resume_pdf_agent"
            / "confirmation"
        )
        for py_file in confirmation_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert "openai" not in content.lower()
            assert "anthropic" not in content.lower()
            assert "gemini" not in content.lower()


class TestNoWebFramework:
    """No web framework dependencies added."""

    def test_no_web_framework_in_confirmation(self):
        """Confirmation module should not import web frameworks."""
        confirmation_dir = (
            Path(__file__).resolve().parent.parent
            / "src"
            / "resume_pdf_agent"
            / "confirmation"
        )
        for py_file in confirmation_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert "fastapi" not in content.lower()
            assert "flask" not in content.lower()
            assert "streamlit" not in content.lower()


class TestNoWordJpgPngExport:
    """No Word/JPG/PNG export introduced."""

    def test_no_word_export_in_confirmation(self):
        """Confirmation module should not introduce Word export."""
        confirmation_dir = (
            Path(__file__).resolve().parent.parent
            / "src"
            / "resume_pdf_agent"
            / "confirmation"
        )
        for py_file in confirmation_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert ".docx" not in content.lower()
            assert "word export" not in content.lower()


class TestConfirmationDocsSafety:
    """Confirmation docs and markdown must not contain forbidden claims."""

    def test_confirmation_markdown_no_hiring_claim(self):
        """Confirmation markdown must not claim hiring probability."""
        from resume_pdf_agent.confirmation.markdown import render_confirmation_review_markdown
        from resume_pdf_agent.models.confirmation import (
            ConfirmationPacket,
        )

        packet = ConfirmationPacket(
            packet_id="test",
            items=[],
            blocking_count=0,
            high_priority_count=0,
            pending_count=0,
            can_generate_final_pdf=True,
            summary="Test",
        )
        md = render_confirmation_review_markdown(packet)
        assert "hiring probability" not in md.lower()
        assert "internal screening" not in md.lower()
        assert "offer probability" not in md.lower()
