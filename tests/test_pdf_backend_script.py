"""Tests for M17 PDF backend verification script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT = _REPO_ROOT / "scripts" / "verify_pdf_backend.py"


class TestVerifyPdfBackendScript:

    def test_script_exists(self):
        assert _SCRIPT.is_file()

    def test_script_mock_backend(self):
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), "--backend", "mock"],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=30,
        )
        assert result.returncode == 0

    def test_script_all_backends(self):
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), "--backend", "all"],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=30,
        )
        assert result.returncode == 0

    def test_script_weasyprint_no_strict(self):
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), "--backend", "weasyprint", "--no-strict"],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=30,
        )
        assert result.returncode == 0

    def test_script_with_output_dir(self, tmp_path):
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), "--backend", "mock",
             "--output-dir", str(tmp_path / "pdf_check")],
            capture_output=True, text=True,
            cwd=str(_REPO_ROOT), timeout=30,
        )
        assert result.returncode == 0
