"""Regression tests for M19 API layer."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.models.enums import ExportFormat


class TestNoRegressions:

    def test_export_format_still_only_pdf(self):
        members = [m.value for m in ExportFormat]
        assert members == ["pdf"]

    def test_no_word_jpg_png_in_api(self):
        api_dir = (
            Path(__file__).resolve().parent.parent
            / "src" / "resume_pdf_agent" / "api"
        )
        for py_file in api_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert ".docx" not in content.lower()

    def test_no_network_calls_in_api(self):
        api_dir = (
            Path(__file__).resolve().parent.parent
            / "src" / "resume_pdf_agent" / "api"
        )
        for py_file in api_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert "requests" not in content.lower()
            assert "urllib.request" not in content.lower()

    def test_no_hiring_claim_in_api(self):
        api_dir = (
            Path(__file__).resolve().parent.parent
            / "src" / "resume_pdf_agent" / "api"
        )
        for py_file in api_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert "hiring probability" not in content.lower()
            assert "internal screening" not in content.lower()
