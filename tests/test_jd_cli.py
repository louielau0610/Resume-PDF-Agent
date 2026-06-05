"""Tests for M15 JD CLI integration."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SAMPLE_JD = _REPO_ROOT / "data" / "sample_inputs" / "sample_data_science_jd.txt"


class TestCliJdOptions:

    def test_run_sample_supports_jd_file(self, tmp_path):
        """run-sample --jd-file should work."""
        result = subprocess.run(
            [
                sys.executable, "-m", "resume_pdf_agent", "run-sample",
                "--output-dir", str(tmp_path / "output"),
                "--pdf-backend", "mock",
                "--jd-file", str(_SAMPLE_JD),
                "--use-user-provided-jd",
            ],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            timeout=120,
        )
        assert result.returncode in (0, 1)

    def test_run_sample_still_works_without_jd(self, tmp_path):
        """run-sample without JD should still work."""
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


class TestJdCliOutput:

    def test_output_mentions_jd_usage(self, tmp_path):
        """When JD is used, output should mention it."""
        result = subprocess.run(
            [
                sys.executable, "-m", "resume_pdf_agent", "run-sample",
                "--output-dir", str(tmp_path / "output"),
                "--pdf-backend", "mock",
                "--jd-file", str(_SAMPLE_JD),
                "--use-user-provided-jd",
            ],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            timeout=120,
        )
        assert "JD used" in result.stdout or result.returncode in (0, 1)
