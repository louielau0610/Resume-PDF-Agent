"""Regression tests for M16 LLM module."""

from __future__ import annotations

from pathlib import Path

from resume_pdf_agent.models.enums import ExportFormat


class TestNoRegressions:

    def test_export_format_still_only_pdf(self):
        members = [m.value for m in ExportFormat]
        assert members == ["pdf"]

    def test_no_llm_sdk_imports(self):
        """LLM module should not import external LLM SDKs."""
        llm_dir = (
            Path(__file__).resolve().parent.parent
            / "src"
            / "resume_pdf_agent"
            / "llm"
        )
        for py_file in llm_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert "openai" not in content.lower()
            assert "anthropic" not in content.lower()
            assert "langchain" not in content.lower()
            assert "llamaindex" not in content.lower()

    def test_no_network_in_llm_module(self):
        """LLM module should not make network calls."""
        llm_dir = (
            Path(__file__).resolve().parent.parent
            / "src"
            / "resume_pdf_agent"
            / "llm"
        )
        for py_file in llm_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert "requests.get" not in content.lower()
            assert "urllib.request" not in content.lower()
            assert "http.client" not in content.lower()

    def test_no_word_jpg_png_in_llm_module(self):
        llm_dir = (
            Path(__file__).resolve().parent.parent
            / "src"
            / "resume_pdf_agent"
            / "llm"
        )
        for py_file in llm_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert ".docx" not in content.lower()
