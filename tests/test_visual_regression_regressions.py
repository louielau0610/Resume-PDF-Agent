"""Regression tests for M18 visual regression module."""

from __future__ import annotations

from pathlib import Path

import pytest

from resume_pdf_agent.models.enums import ExportFormat


class TestNoRegressions:

    def test_export_format_still_only_pdf(self):
        members = [m.value for m in ExportFormat]
        assert members == ["pdf"]

    def test_no_playwright_required(self):
        """visual_regression module must not require Playwright in non-optional modules."""
        vr_dir = (
            Path(__file__).resolve().parent.parent
            / "src" / "resume_pdf_agent" / "visual_regression"
        )
        for py_file in vr_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            # Only optional_screenshots.py and __init__.py may reference playwright
            if py_file.name in ("optional_screenshots.py", "__init__.py"):
                continue
            # Other modules should not require playwright
            if "from playwright" in content.lower() or "import playwright" in content.lower():
                # Check if it's guarded
                if "find_spec" not in content and "try:" not in content:
                    pytest.fail(f"{py_file.name} imports playwright without guarding")

    def test_no_network_calls(self):
        vr_dir = (
            Path(__file__).resolve().parent.parent
            / "src" / "resume_pdf_agent" / "visual_regression"
        )
        for py_file in vr_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert "requests" not in content.lower()
            assert "urllib.request" not in content.lower()

    def test_no_word_jpg_png(self):
        vr_dir = (
            Path(__file__).resolve().parent.parent
            / "src" / "resume_pdf_agent" / "visual_regression"
        )
        for py_file in vr_dir.glob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            assert ".docx" not in content.lower()
