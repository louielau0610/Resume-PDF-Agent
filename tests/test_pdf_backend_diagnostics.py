"""Tests for M17 PDF backend diagnostics."""

from __future__ import annotations

from resume_pdf_agent.pdf.diagnostics import (
    check_mock_backend_diagnostics,
    check_playwright_diagnostics,
    check_weasyprint_diagnostics,
    get_all_pdf_backend_diagnostics,
    get_pdf_backend_diagnostics,
    summarize_pdf_backend_status,
)
from resume_pdf_agent.models.pdf import PDFBackend


class TestMockBackendDiagnostics:

    def test_mock_always_available(self):
        diag = check_mock_backend_diagnostics()
        assert diag["available"] is True

    def test_mock_not_production(self):
        diag = check_mock_backend_diagnostics()
        assert diag["production_recommended"] is False

    def test_mock_mentions_test_only(self):
        diag = check_mock_backend_diagnostics()
        notes = " ".join(diag["notes"]).lower()
        assert "test" in notes or "deterministic" in notes


class TestWeasyPrintDiagnostics:

    def test_does_not_crash(self):
        """WeasyPrint diagnostics must not crash if unavailable."""
        diag = check_weasyprint_diagnostics()
        assert "backend" in diag
        assert "available" in diag

    def test_has_setup_hint(self):
        diag = check_weasyprint_diagnostics()
        assert diag["setup_hint"]

    def test_production_recommended(self):
        diag = check_weasyprint_diagnostics()
        assert diag["production_recommended"] is True


class TestPlaywrightDiagnostics:

    def test_does_not_crash(self):
        diag = check_playwright_diagnostics()
        assert "backend" in diag
        assert "available" in diag

    def test_has_setup_hint(self):
        diag = check_playwright_diagnostics()
        assert diag["setup_hint"]


class TestGetPdfBackendDiagnostics:

    def test_returns_for_mock(self):
        diag = get_pdf_backend_diagnostics(PDFBackend.MOCK)
        assert diag["available"] is True

    def test_returns_for_weasyprint(self):
        diag = get_pdf_backend_diagnostics(PDFBackend.WEASYPRINT)
        assert "backend" in diag

    def test_returns_for_playwright(self):
        diag = get_pdf_backend_diagnostics(PDFBackend.PLAYWRIGHT)
        assert "backend" in diag


class TestGetAllPdfBackendDiagnostics:

    def test_returns_all_three(self):
        all_diag = get_all_pdf_backend_diagnostics()
        assert "mock" in all_diag
        assert "weasyprint" in all_diag
        assert "playwright" in all_diag


class TestSummarizePdfBackendStatus:

    def test_returns_non_empty_text(self):
        summary = summarize_pdf_backend_status()
        assert len(summary) > 0
        assert "mock" in summary.lower()
