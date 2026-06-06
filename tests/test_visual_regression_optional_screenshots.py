"""Tests for M18 optional screenshot diagnostics."""

from __future__ import annotations

from resume_pdf_agent.visual_regression.optional_screenshots import (
    capture_html_screenshot_if_available,
    is_playwright_available,
)


class TestIsPlaywrightAvailable:

    def test_returns_bool(self):
        result = is_playwright_available()
        assert isinstance(result, bool)

    def test_does_not_crash(self):
        # Calling multiple times should be safe
        for _ in range(3):
            is_playwright_available()


class TestCaptureHtmlScreenshotIfAvailable:

    def test_returns_gracefully_when_unavailable(self):
        ok, warnings = capture_html_screenshot_if_available(
            "nonexistent.html", "output.png"
        )
        # Should not crash
        assert isinstance(ok, bool)
        assert isinstance(warnings, list)
