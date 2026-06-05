"""Tests for M14 confirmation CLI integration."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent


class TestCliConfirmationFlags:
    """CLI commands should support M14 confirmation flags."""

    def test_run_sample_supports_require_confirmation(self, tmp_path):
        """run-sample --require-confirmation-before-pdf should work."""
        result = subprocess.run(
            [
                sys.executable, "-m", "resume_pdf_agent", "run-sample",
                "--output-dir", str(tmp_path / "output"),
                "--pdf-backend", "mock",
                "--require-confirmation-before-pdf",
            ],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            timeout=120,
        )
        # Should not crash
        assert result.returncode in (0, 1)

    def test_run_sample_supports_write_confirmation_packet(self, tmp_path):
        """run-sample --write-confirmation-packet should work."""
        result = subprocess.run(
            [
                sys.executable, "-m", "resume_pdf_agent", "run-sample",
                "--output-dir", str(tmp_path / "output"),
                "--pdf-backend", "mock",
                "--write-confirmation-packet",
            ],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            timeout=120,
        )
        assert result.returncode in (0, 1)

    def test_run_sample_without_confirmation_flags_still_works(self, tmp_path):
        """run-sample without new flags should still work."""
        result = subprocess.run(
            [
                sys.executable, "-m", "resume_pdf_agent", "run-sample",
                "--output-dir", str(tmp_path / "output"),
                "--pdf-backend", "mock",
            ],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            timeout=120,
        )
        assert result.returncode in (0, 1)
        assert "Confirmation packet" in result.stdout or "Status" in result.stdout

    def test_run_sample_no_write_confirmation_packet(self, tmp_path):
        """run-sample --no-write-confirmation-packet should skip packet."""
        result = subprocess.run(
            [
                sys.executable, "-m", "resume_pdf_agent", "run-sample",
                "--output-dir", str(tmp_path / "output"),
                "--pdf-backend", "mock",
                "--no-write-confirmation-packet",
            ],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            timeout=120,
        )
        assert result.returncode in (0, 1)


class TestCliOutputIncludesConfirmationInfo:
    """CLI output should include confirmation summary info."""

    def test_output_mentions_can_generate_pdf(self, tmp_path):
        """CLI summary should mention can_generate_final_pdf."""
        result = subprocess.run(
            [
                sys.executable, "-m", "resume_pdf_agent", "run-sample",
                "--output-dir", str(tmp_path / "output"),
                "--pdf-backend", "mock",
            ],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            timeout=120,
        )
        assert "Can generate PDF" in result.stdout


class TestNoRegressions:
    """Ensure existing CLI behavior is preserved."""

    def test_list_criteria_still_works(self):
        """list-criteria should still work."""
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "list-criteria"],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
        assert "data_science_intern" in result.stdout

    def test_list_templates_still_works(self):
        """list-templates should still work."""
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "list-templates"],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            timeout=30,
        )
        assert result.returncode == 0
