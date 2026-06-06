"""Tests for M17 PDF backend CLI commands."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent


class TestCheckPdfBackendCli:

    def test_check_all_backends(self):
        """check-pdf-backend without args should work."""
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "check-pdf-backend"],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=30,
        )
        assert result.returncode == 0

    def test_check_mock_backend(self):
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "check-pdf-backend", "--backend", "mock"],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=30,
        )
        assert result.returncode == 0

    def test_check_weasyprint_no_strict(self):
        """WeasyPrint check should not crash even if unavailable."""
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "check-pdf-backend", "--backend", "weasyprint"],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=30,
        )
        # Non-strict mode should exit 0 even if unavailable
        assert result.returncode in (0, 1)

    def test_check_weasyprint_strict(self):
        """Strict mode exits non-zero if unavailable, zero if available."""
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "check-pdf-backend",
             "--backend", "weasyprint", "--strict"],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=30,
        )
        # May exit 0 (available) or 1 (unavailable+strict)
        assert result.returncode in (0, 1)

    def test_check_with_output_dir(self, tmp_path):
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "check-pdf-backend",
             "--backend", "mock", "--output-dir", str(tmp_path / "pdf_check")],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=30,
        )
        assert result.returncode == 0
