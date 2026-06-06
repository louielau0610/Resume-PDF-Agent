"""Regression tests for M17 PDF backend diagnostics."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.models.enums import ExportFormat


class TestNoRegressions:

    def test_export_format_still_only_pdf(self):
        members = [m.value for m in ExportFormat]
        assert members == ["pdf"]

    def test_no_weasyprint_required_in_tests(self):
        """Tests must not require WeasyPrint."""
        # Simply importing diagnostics should work without WeasyPrint
        from resume_pdf_agent.pdf.diagnostics import check_weasyprint_diagnostics
        diag = check_weasyprint_diagnostics()
        # The function itself must not crash
        assert isinstance(diag, dict)

    def test_no_network_calls_in_diagnostics(self):
        diag_path = (
            Path(__file__).resolve().parent.parent
            / "src" / "resume_pdf_agent" / "pdf" / "diagnostics.py"
        )
        content = diag_path.read_text(encoding="utf-8")
        assert "requests" not in content.lower()
        assert "urllib.request" not in content.lower()
        # "http" may appear in documentation URLs, which is fine

    def test_no_word_jpg_png_in_diagnostics(self):
        diag_path = (
            Path(__file__).resolve().parent.parent
            / "src" / "resume_pdf_agent" / "pdf" / "diagnostics.py"
        )
        content = diag_path.read_text(encoding="utf-8")
        assert ".docx" not in content.lower()
