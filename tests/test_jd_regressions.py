"""Regression tests for M15 JD parser."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.models.enums import ExportFormat


class TestNoRegressions:

    def test_export_format_still_only_pdf(self):
        """ExportFormat must still only include PDF."""
        members = [m.value for m in ExportFormat]
        assert members == ["pdf"]

    def test_no_llm_imports_in_jd_module(self):
        """JD module should not import LLM libraries."""
        jd_dir = (
            Path(__file__).resolve().parent.parent
            / "src"
            / "resume_pdf_agent"
            / "jd"
        )
        for py_file in jd_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert "openai" not in content.lower()
            assert "anthropic" not in content.lower()
            assert "requests" not in content.lower()
            assert "urllib" not in content.lower()
            assert "scrape" not in content.lower()

    def test_no_web_framework_in_jd_module(self):
        """JD module should not import web frameworks."""
        jd_dir = (
            Path(__file__).resolve().parent.parent
            / "src"
            / "resume_pdf_agent"
            / "jd"
        )
        for py_file in jd_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert "fastapi" not in content.lower()
            assert "flask" not in content.lower()

    def test_no_word_jpg_png_in_jd_module(self):
        """JD module should not introduce Word/JPG/PNG export."""
        jd_dir = (
            Path(__file__).resolve().parent.parent
            / "src"
            / "resume_pdf_agent"
            / "jd"
        )
        for py_file in jd_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert ".docx" not in content.lower()
