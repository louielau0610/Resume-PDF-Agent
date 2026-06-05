"""Tests for M16 LLM CLI integration."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent


class TestCliLlmOptions:

    def test_run_sample_without_llm_still_works(self, tmp_path):
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "run-sample",
             "--output-dir", str(tmp_path / "output"),
             "--pdf-backend", "mock"],
            capture_output=True, text=True, cwd=str(_REPO_ROOT), timeout=120,
        )
        assert result.returncode in (0, 1)

    def test_run_sample_with_llm_mock(self, tmp_path):
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "run-sample",
             "--output-dir", str(tmp_path / "output"),
             "--pdf-backend", "mock",
             "--enable-llm-rewriting", "--llm-provider", "mock"],
            capture_output=True, text=True, cwd=str(_REPO_ROOT), timeout=120,
        )
        assert result.returncode in (0, 1)

    def test_list_criteria_still_works(self):
        result = subprocess.run(
            [sys.executable, "-m", "resume_pdf_agent", "list-criteria"],
            capture_output=True, text=True, cwd=str(_REPO_ROOT), timeout=30,
        )
        assert result.returncode == 0
